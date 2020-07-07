import botocore.exceptions
import botocore.errorfactory
import boto3
import mypy_boto3_rds
import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
from nixops_aws.resources.ec2_common import EC2CommonState
from nixops.diff import Handler
from typing import Optional

from .types.ec2_rds_dbsecurity_group import Ec2RdsDbsecurityGroupOptions


class EC2RDSDbSecurityGroupDefinition(nixops.resources.ResourceDefinition):

    config: Ec2RdsDbsecurityGroupOptions

    @classmethod
    def get_type(cls):
        return "ec2-rds-dbsecurity-group"

    @classmethod
    def get_resource_type(cls):
        return "rdsDbSecurityGroups"

    def show_type(self):
        return "{0}".format(self.get_type())


class EC2RDSDbSecurityGroupState(
    nixops.resources.DiffEngineResourceState, EC2CommonState
):

    _rds_client: Optional[mypy_boto3_rds.RDSClient]

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("accessKeyId", None)
    _reserved_keys = EC2CommonState.COMMON_EC2_RESERVED

    @classmethod
    def get_type(cls):
        return "ec2-rds-dbsecurity-group"

    def __init__(self, depl, name, id):
        nixops.resources.DiffEngineResourceState.__init__(self, depl, name, id)
        self.handle_create_rds_db_sg = Handler(
            ["groupName", "region", "description"], handle=self.realize_create_sg
        )
        self.handle_rules = Handler(
            ["rules"],
            after=[self.handle_create_rds_db_sg],
            handle=self.realize_rules_change,
        )

    def show_type(self):
        s = super(EC2RDSDbSecurityGroupState, self).show_type()
        return "{0} [{1}]".format(s, self._state.get("region", None))

    @property
    def resource_id(self):
        return self._state.get("groupName", None)

    def _check(self):
        if self._state.get("groupName", None) is None:
            return
        if self.state == self.UP:
            try:
                response = self.get_rds_client().describe_db_security_groups(
                    DBSecurityGroupName=self._state["groupName"]
                )
            except botocore.exceptions.ClientError as error:
                if error.response["Error"]["Code"] == "DBSecurityGroupNotFound":
                    self.warn(
                        "RDS db security group {} not found, performing destroy to sync the state ...".format(
                            self._state["groupName"]
                        )
                    )
                    self._destroy()
                    return
                else:
                    raise error

            rules = []

            def generate_rule(rule):
                # FIXME note that we're forcing sg name to None here
                # as it causes InvalidParameterCombination errors
                # during revoke diff handling since sg name and id
                # can't be used together and the api returns both
                # anyway. This might also cause some unnecessary diff
                # handling when the config has securityGroupName set
                # and we run nixops check as it will persist the id
                # instead.
                return {
                    "securityGroupId": rule.get("EC2SecurityGroupId", None),
                    "securityGroupName": None,
                    "securityGroupOwnerId": rule.get("EC2SecurityGroupOwnerId", None),
                    "cidrIp": rule.get("CIDRIP", None),
                }

            for rule in response["DBSecurityGroups"][0].get("EC2SecurityGroups", []):
                rules.append(generate_rule(rule))
            for rule in response["DBSecurityGroups"][0].get("IPRanges", []):
                rules.append(generate_rule(rule))

            with self.depl._db:
                self._state["rules"] = rules

    def realize_create_sg(self, allow_recreate):
        config = self.get_defn()
        if self.state == self.UP:
            if not allow_recreate:
                raise Exception(
                    "RDS security group {} definition changed and it needs to be recreated"
                    " use --allow-recreate if you want to create a new one".format(
                        self._state["groupName"]
                    )
                )

            self.warn("RDS security group definition changed, recreating ...")
            self._destroy()
            self.reset_client()  # FIXME ideally this should be detected automatically

        self.log("creating RDS security group {}".format(config["groupName"]))
        self._state["region"] = config["region"]
        self.get_rds_client().create_db_security_group(
            DBSecurityGroupName=config["groupName"],
            DBSecurityGroupDescription=config["description"],
        )
        with self.depl._db:
            self.state = self.UP
            self._state["groupName"] = config["groupName"]
            self._state["description"] = config["description"]

    def realize_rules_change(self, allow_recreate):
        config = self.get_defn()

        rules_to_remove = [
            r for r in self._state.get("rules", []) if r not in config["rules"]
        ]
        rules_to_add = [
            r for r in config["rules"] if r not in self._state.get("rules", [])
        ]

        for rule in rules_to_remove:
            self.log(
                "removing old rules from RDS security group {} ...".format(
                    self._state["groupName"]
                )
            )
            kwargs = self.process_rule(rule)
            self.get_rds_client().revoke_db_security_group_ingress(**kwargs)

        for rule in rules_to_add:
            self.log(
                "adding new rules to RDS security group {} ...".format(
                    self._state["groupName"]
                )
            )
            kwargs = self.process_rule(rule)
            self.get_rds_client().authorize_db_security_group_ingress(**kwargs)

        with self.depl._db:
            self._state["rules"] = config["rules"]

    def process_rule(self, config):
        # FIXME do more checks before passing the args to the boto api call
        args = dict()
        args["DBSecurityGroupName"] = self._state["groupName"]
        args["CIDRIP"] = config.get("cidrIp", None)
        args["EC2SecurityGroupName"] = config.get("securityGroupName", None)
        args["EC2SecurityGroupId"] = config.get("securityGroupId", None)
        args["EC2SecurityGroupOwnerId"] = config.get("securityGroupOwnerId", None)
        return {attr: args[attr] for attr in args if args[attr] is not None}

    def _destroy(self):
        if self.state != self.UP:
            return
        self.log("destroying rds db security group {}".format(self._state["groupName"]))
        try:
            self.get_rds_client().delete_db_security_group(
                DBSecurityGroupName=self._state["groupName"]
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "DBSecurityGroupNotFound":
                self.warn(
                    "rds security group {} already deleted".format(
                        self._state["groupName"]
                    )
                )
            else:
                raise error

        with self.depl._db:
            self.state = self.MISSING
            self._state["groupName"] = None
            self._state["region"] = None
            self._state["description"] = None
            self._state["rules"] = None

    def destroy(self, wipe=True):
        self._destroy()
        return True

    def get_rds_client(self):
        """
        Generic method to get a cached RDS AWS client or create it.
        """
        new_access_key_id = (
            self.get_defn()["accessKeyId"] if self.depl.definitions else None
        ) or nixops_aws.ec2_utils.get_access_key_id()
        if new_access_key_id is not None:
            self.access_key_id = new_access_key_id
        if self.access_key_id is None:
            raise Exception(
                "please set 'accessKeyId', $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )
        if self._rds_client:
            return self._rds_client
        assert self._state["region"]
        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            self.access_key_id
        )
        self._rds_client = boto3.session.Session().client(
            service_name="rds",
            region_name=self._state["region"],
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        return self._rds_client
