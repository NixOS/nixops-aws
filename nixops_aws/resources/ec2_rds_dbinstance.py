# -*- coding: utf-8 -*-

# Automatic provisioning of AWS RDS Database Instances.

import nixops.resources
import nixops.util
import nixops_aws.ec2_utils
import time
from uuid import uuid4
from . import ec2_rds_dbsecurity_group
from .ec2_rds_dbsecurity_group import EC2RDSDbSecurityGroupState
from .ec2_security_group import EC2SecurityGroupState
from .rds_db_subnet_group import RDSDbSubnetGroupState
from .types.ec2_rds_dbinstance import Ec2RdsDbinstanceOptions
from typing import Optional, Sequence, TYPE_CHECKING
from typing_extensions import TypedDict

if TYPE_CHECKING:
    import mypy_boto3_rds


class VpcOptions(TypedDict):
    db_subnet_group_name: Optional[str]
    security_groups: Optional[Sequence[str]]
    vpc_security_groups: Optional[Sequence[str]]


class EC2RDSDbInstanceDefinition(nixops.resources.ResourceDefinition):
    """Definition of an EC2 RDS Database Instance."""

    config: Ec2RdsDbinstanceOptions
    subnet_group: Optional[str]
    vpc_security_groups: Optional[Sequence[str]] = []
    rds_dbinstance_security_groups: Optional[Sequence[str]] = []

    @classmethod
    def get_type(cls):
        return "ec2-rds-dbinstance"

    @classmethod
    def get_resource_type(cls):
        return "rdsDbInstances"

    def __init__(self, name: str, config: nixops.resources.ResourceEval):
        super(EC2RDSDbInstanceDefinition, self).__init__(name, config)
        # rds specific params

        self.rds_dbinstance_id: str = self.config.id
        self.rds_dbinstance_allocated_storage: int = self.config.allocatedStorage
        self.rds_dbinstance_instance_class: str = self.config.instanceClass
        self.rds_dbinstance_master_username: str = self.config.masterUsername
        self.rds_dbinstance_master_password: str = self.config.masterPassword
        self.rds_dbinstance_port: int = self.config.port
        self.rds_dbinstance_engine: str = self.config.engine
        self.rds_dbinstance_db_name: str = self.config.dbName
        self.rds_dbinstance_multi_az: bool = self.config.multiAZ
        self.subnet_group: Optional[str] = self.config.subnetGroup

        if self.subnet_group is not None:
            if self.config.vpcSecurityGroups is None:
                raise Exception(
                    f"rdsDbInstances.{name}.vpcSecurityGroups is required when subnetGroup is specified"
                )
            elif tuple(self.config.securityGroups) != ("default",):
                raise Exception(
                    f"rdsDbInstances.{name}.securityGroups is invalid when subnetGroup is specified"
                )
            else:
                self.vpc_security_groups = self.config.vpcSecurityGroups
        else:
            if self.config.vpcSecurityGroups is not None:
                raise Exception(
                    f"rdsDbInstances.{name}.vpcSecurityGroups is invalid when subnetGroup is not specified"
                )
            else:
                self.rds_dbinstance_security_groups = self.config.securityGroups

        # TODO: implement remainder of boto.rds.RDSConnection.create_dbinstance parameters

        # common params
        self.region = self.config.region
        self.access_key_id = self.config.accessKeyId

    def show_type(self):
        return "{0} [{1}]".format(self.get_type(), self.region)


class EC2RDSDbInstanceState(nixops.resources.ResourceState[EC2RDSDbInstanceDefinition]):
    """State of an RDS Database Instance."""

    definition_type = EC2RDSDbInstanceDefinition

    _conn: Optional["mypy_boto3_rds.RDSClient"]
    region = nixops.util.attr_property("ec2.region", None)
    access_key_id = nixops.util.attr_property("ec2.accessKeyId", None)
    rds_dbinstance_id = nixops.util.attr_property("ec2.rdsDbInstanceID", None)
    rds_dbinstance_allocated_storage = nixops.util.attr_property(
        "ec2.rdsAllocatedStorage", None, int
    )
    rds_dbinstance_instance_class = nixops.util.attr_property(
        "ec2.rdsInstanceClass", None
    )
    rds_dbinstance_master_username = nixops.util.attr_property(
        "ec2.rdsMasterUsername", None
    )
    rds_dbinstance_master_password = nixops.util.attr_property(
        "ec2.rdsMasterPassword", None
    )
    rds_dbinstance_port = nixops.util.attr_property("ec2.rdsPort", None, int)
    rds_dbinstance_engine = nixops.util.attr_property("ec2.rdsEngine", None)
    rds_dbinstance_db_name = nixops.util.attr_property("ec2.rdsDbName", None)
    rds_dbinstance_endpoint = nixops.util.attr_property("ec2.rdsEndpoint", None)
    rds_dbinstance_multi_az = nixops.util.attr_property("ec2.multiAZ", False)
    subnet_group = nixops.util.attr_property("subnetGroup", None)
    rds_dbinstance_security_groups = nixops.util.attr_property(
        "ec2.securityGroups", [], "json"
    )
    vpc_security_groups = nixops.util.attr_property("ec2.vpcSecurityGroups", [], "json")

    requires_reboot_attrs = (
        "rds_dbinstance_id",
        "rds_dbinstance_allocated_storage",
        "rds_dbinstance_instance_class",
        "rds_dbinstance_master_password",
    )

    @classmethod
    def get_type(cls):
        return "ec2-rds-dbinstance"

    def __init__(self, depl, name, id):
        super(EC2RDSDbInstanceState, self).__init__(depl, name, id)
        self._conn = None

    def show_type(self):
        s = super(EC2RDSDbInstanceState, self).show_type()
        if self.region:
            s = "{0} [{1}]".format(s, self.region)
        return s

    def prefix_definition(self, attr):
        return {("resources", "rdsDbInstances"): attr}

    def get_physical_spec(self):
        return {"endpoint": self.rds_dbinstance_endpoint}

    @property
    def resource_id(self):
        return self.rds_dbinstance_id

    def create_after(self, resources, defn: EC2RDSDbInstanceDefinition):
        return {
            r
            for r in resources
            if isinstance(r, ec2_rds_dbsecurity_group.EC2RDSDbSecurityGroupState)
            or isinstance(r, RDSDbSubnetGroupState)
            or isinstance(
                r, nixops_aws.resources.ec2_security_group.EC2SecurityGroupState
            )
        }

    def _connect(self) -> "mypy_boto3_rds.RDSClient":
        if not self._conn:
            self._conn = nixops_aws.ec2_utils.connect_rds_boto3(
                region=self.region, access_key_id=self.access_key_id
            )
        return self._conn

    def _exists(self):
        return self.state != self.MISSING and self.state != self.UNKNOWN

    def _assert_invariants(self, defn: EC2RDSDbInstanceDefinition):
        # NOTE: it is possible to change region, master_username, port, or db_name
        # by creating a snapshot of the database and recreating the instance,
        # then restoring the snapshot.  Not sure if this is in the scope of what
        # nixops intends to manager for the user, or if it violates the principle
        # of least surprise.

        diff = self._diff_defn(defn)
        diff_attrs = set(diff.keys())

        invariant_attrs = set(
            [
                "region",
                "rds_dbinstance_master_username",
                "rds_dbinstance_engine",
                "rds_dbinstance_port",
                "rds_dbinstance_db_name",
            ]
        )

        violated_attrs = diff_attrs & invariant_attrs
        if len(violated_attrs) > 0:
            message = (
                "Invariant violated: (%s) cannot be changed for an RDS instance"
                % ",".join(violated_attrs)
            )
            for attr in violated_attrs:
                message += "\n%s != %s" % (getattr(self, attr), getattr(defn, attr))
            raise Exception(message)

    def _try_fetch_dbinstance(self, instance_id):
        dbinstance = None
        rds_client = self._connect()
        try:
            dbinstance = rds_client.describe_db_instances(
                DBInstanceIdentifier=instance_id
            )["DBInstances"][0]
        except rds_client.exceptions.DBInstanceNotFoundFault:
            dbinstance = None
        except:
            raise

        return dbinstance

    def _diff_defn(self, defn: EC2RDSDbInstanceDefinition):
        attrs = (
            "region",
            "rds_dbinstance_port",
            "rds_dbinstance_engine",
            "rds_dbinstance_multi_az",
            "rds_dbinstance_instance_class",
            "rds_dbinstance_db_name",
            "rds_dbinstance_master_username",
            "rds_dbinstance_master_password",
            "rds_dbinstance_allocated_storage",
            "rds_dbinstance_security_groups",
            "vpc_security_groups",
        )

        def get_state_attr(attr):
            # handle boolean type in the state to avoid triggering false
            # diffs
            if attr == "rds_dbinstance_multi_az":
                return bool(getattr(self, attr))
            else:
                return getattr(self, attr)

        def get_defn_attr(attr):
            if attr == "rds_dbinstance_security_groups":
                return self.fetch_rds_security_group_resources(
                    defn.rds_dbinstance_security_groups
                )
            elif attr == "vpc_security_groups":
                return self.fetch_vpc_security_group_resources(defn.vpc_security_groups)
            else:
                return getattr(defn, attr)

        return {
            attr: get_defn_attr(attr)
            for attr in attrs
            if get_defn_attr(attr) != get_state_attr(attr)
        }

    def _requires_reboot(self, defn: EC2RDSDbInstanceDefinition):
        diff = self._diff_defn(defn)
        return set(self.requires_reboot_attrs) & set(diff.keys())

    def _wait_for_dbinstance(self, dbinstance_id, state="available"):
        self.log_start("waiting for database instance state=`{0}` ".format(state))
        while True:
            dbinstance = self._try_fetch_dbinstance(dbinstance_id)
            self.log_continue("[{0}] ".format(dbinstance["DBInstanceStatus"]))
            if dbinstance["DBInstanceStatus"] not in {
                "creating",
                "backing-up",
                "available",
                "modifying",
                "configuring-enhanced-monitoring",
            }:
                raise Exception(
                    "RDS database instance ‘{0}’ in an error state (state is ‘{1}’)".format(
                        dbinstance["DBInstanceIdentifier"],
                        dbinstance["DBInstanceStatus"],
                    )
                )
            if dbinstance["DBInstanceStatus"] == state:
                return dbinstance
            time.sleep(6)

    def _copy_dbinstance_attrs(
        self, dbinstance, rds_security_groups, vpc_security_groups
    ):
        with self.depl._db:
            self.rds_dbinstance_id = dbinstance["DBInstanceIdentifier"]
            self.rds_dbinstance_allocated_storage = int(dbinstance["AllocatedStorage"])
            self.rds_dbinstance_instance_class = dbinstance["DBInstanceClass"]
            self.rds_dbinstance_master_username = dbinstance["MasterUsername"]
            self.rds_dbinstance_engine = dbinstance["Engine"]
            self.rds_dbinstance_multi_az = dbinstance["MultiAZ"]
            if dbinstance["DBSubnetGroup"]:
                self.subnet_group = dbinstance["DBSubnetGroup"]["DBSubnetGroupName"]

            if dbinstance["Endpoint"]:
                self.rds_dbinstance_port = int(dbinstance["Endpoint"]["Port"])
                self.rds_dbinstance_endpoint = dbinstance["Endpoint"]["Address"]
            self.rds_dbinstance_security_groups = rds_security_groups
            self.vpc_security_groups = vpc_security_groups

    def _to_boto_kwargs(self, attrs):
        attr_to_kwarg = {
            "rds_dbinstance_allocated_storage": "allocated_storage",
            "rds_dbinstance_master_password": "master_password",
            "rds_dbinstance_instance_class": "instance_class",
            "rds_dbinstance_multi_az": "multi_az",
            "rds_dbinstance_security_groups": "security_groups",
            "vpc_security_groups": "vpc_security_groups",
        }
        result = {attr_to_kwarg[attr]: attrs[attr] for attr in attrs.keys()}

        # If the user has specified VPC security groups, and
        # have left security groups as the default list of "default",
        # they probably don't use the default security group --
        # and it is incompatible with VPC security groups anyway.
        if (
            "vpc_security_groups" in result
            and "security_groups" in result
            and len(result["vpc_security_groups"]) > 0
            and tuple(result["security_groups"]) == ("default",)
        ):
            del result["security_groups"]

        return result

    def _compare_instance_id(self, instance_id):
        # take care when comparing instance ids, as aws lowercases and converts to unicode
        return str(self.rds_dbinstance_id).lower() == str(instance_id).lower()

    def fetch_rds_security_group_resources(
        self, config: Optional[Sequence[str]]
    ) -> Optional[Sequence[str]]:
        if config is None:
            return None
        security_groups = []
        for sg in config:
            if sg.startswith("res-"):
                res = self.depl.get_typed_resource(
                    sg[4:].split(".")[0],
                    "ec2-rds-dbsecurity-group",
                    EC2RDSDbSecurityGroupState,
                )
                security_groups.append(res._state["groupName"])
            else:
                security_groups.append(sg)
        return security_groups

    def fetch_vpc_security_group_resources(
        self, config: Optional[Sequence[str]]
    ) -> Optional[Sequence[str]]:
        if config is None:
            return None
        security_groups = []
        for sg in config:
            if sg.startswith("res-"):
                res: EC2SecurityGroupState = self.depl.get_typed_resource(
                    sg[4:].split(".")[0],
                    "ec2-security-group",
                    EC2SecurityGroupState,
                )
                security_groups.append(res.security_group_id)
            else:
                security_groups.append(sg)
        return security_groups

    def create(
        self, defn: EC2RDSDbInstanceDefinition, check, allow_reboot, allow_recreate
    ):
        with self.depl._db:
            self.access_key_id = (
                defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
            )
            if not self.access_key_id:
                raise Exception(
                    "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
                )

            if self._exists():
                self._assert_invariants(defn)

            self.region = defn.region

        # fetch our target instance identifier regardless to fail early if needed
        dbinstance = self._try_fetch_dbinstance(defn.rds_dbinstance_id)

        if self.state == self.UP:
            # if we are changing instance ids and our target instance id already exists
            # there is no reasonable recourse.  bail.
            if dbinstance and not self._compare_instance_id(defn.rds_dbinstance_id):
                raise Exception(
                    "database identifier changed but database with instance_id=%s already exists"
                    % defn.rds_dbinstance_id
                )

            dbinstance = self._try_fetch_dbinstance(self.rds_dbinstance_id)

        with self.depl._db:
            dbinstance = self._try_fetch_dbinstance(defn.rds_dbinstance_id)
            if check or self.state == self.MISSING or self.state == self.UNKNOWN:
                if dbinstance and (
                    self.state == self.MISSING or self.state == self.UNKNOWN
                ):
                    if dbinstance["DBInstanceStatus"] == "deleting":
                        self.logger.log(
                            "RDS instance `{0}` is being deleted, waiting...".format(
                                dbinstance["DBInstanceIdentifier"]
                            )
                        )
                        while True:
                            if dbinstance["DBInstanceStatus"] == "deleting":
                                continue
                            else:
                                break
                            self.log_continue(
                                "[{0}] ".format(dbinstance["DBInstanceStatus"])
                            )
                            time.sleep(6)

                    self.logger.log(
                        "RDS instance `{0}` is MISSING but already exists, synchronizing state".format(
                            dbinstance["DBInstanceIdentifier"]
                        )
                    )
                    self.state = self.UP

                if not dbinstance and self.state == self.UP:
                    self.logger.log(
                        "RDS instance `{0}` state is UP but does not exist!"
                    )
                    if not allow_recreate:
                        raise Exception(
                            "RDS instance is UP but does not exist, set --allow-recreate to recreate"
                        )
                    self.state = self.MISSING

                if not dbinstance and (
                    self.state == self.MISSING or self.state == self.UNKNOWN
                ):
                    self.logger.log(
                        "creating RDS database instance ‘{0}’ (this may take a while)...".format(
                            defn.rds_dbinstance_id
                        )
                    )

                    vpc_opts = self.get_vpc_options(defn)
                    # create a new dbinstance with desired config
                    dbinstance = self._connect().create_db_instance(
                        DBName=defn.rds_dbinstance_db_name,
                        DBInstanceIdentifier=defn.rds_dbinstance_id,
                        AllocatedStorage=defn.rds_dbinstance_allocated_storage,
                        DBInstanceClass=defn.rds_dbinstance_instance_class,
                        Engine=defn.rds_dbinstance_engine,
                        MasterUsername=defn.rds_dbinstance_master_username,
                        MasterUserPassword=defn.rds_dbinstance_master_password,
                        Port=defn.rds_dbinstance_port,
                        MultiAZ=defn.rds_dbinstance_multi_az,
                        DBSubnetGroupName=vpc_opts["db_subnet_group_name"],
                        VpcSecurityGroupIds=vpc_opts["vpc_security_groups"],
                        DBSecurityGroups=vpc_opts["security_groups"],
                    )["DBInstance"]

                    self.state = self.STARTING
                    dbinstance = self._wait_for_dbinstance(defn.rds_dbinstance_id)

                self.region = defn.region
                self.access_key_id = (
                    defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
                )
                self.rds_dbinstance_db_name = defn.rds_dbinstance_db_name
                self.rds_dbinstance_master_password = (
                    defn.rds_dbinstance_master_password
                )
                self._copy_dbinstance_attrs(
                    dbinstance,
                    defn.rds_dbinstance_security_groups,
                    self.fetch_vpc_security_group_resources(defn.vpc_security_groups),
                )
                self.state = self.UP

        with self.depl._db:
            if self.state == self.UP and self._diff_defn(defn):
                if dbinstance is None:
                    raise Exception(
                        "state is UP but database instance does not exist. re-run with --check option to synchronize states"
                    )

                # check invariants again since state possibly changed due to check = true
                self._assert_invariants(defn)

                reboot_keys = self._requires_reboot(defn)
                if self._requires_reboot(defn) and not allow_reboot:
                    raise Exception(
                        "changing keys (%s) requires reboot, but --allow-reboot not set"
                        % ", ".join(reboot_keys)
                    )

                diff = self._diff_defn(defn)
                boto_kwargs = self._to_boto_kwargs(diff)
                if not self._compare_instance_id(defn.rds_dbinstance_id):
                    boto_kwargs["new_instance_id"] = defn.rds_dbinstance_id
                boto_kwargs["apply_immediately"] = True

                # first check is for the unlikely event we attempt to modify the db during its maintenance window
                self._wait_for_dbinstance(defn.rds_dbinstance_id)
                dbinstance = self._connect().modify_db_instance(**boto_kwargs)[
                    "DBInstance"
                ]
                # Ugly hack to prevent from waiting on state
                # 'modifying' on sg change as that looks like it's an
                # immediate change in RDS.
                if not (len(boto_kwargs) == 2 and "security_groups" in boto_kwargs):
                    dbinstance = self._wait_for_dbinstance(
                        dbinstance["DBInstanceIdentifier"], state="modifying"
                    )
                dbinstance = self._wait_for_dbinstance(
                    dbinstance["DBInstanceIdentifier"]
                )
                self._copy_dbinstance_attrs(
                    dbinstance,
                    defn.rds_dbinstance_security_groups,
                    self.fetch_vpc_security_group_resources(defn.vpc_security_groups),
                )

    def get_vpc_options(self, defn: EC2RDSDbInstanceDefinition) -> VpcOptions:
        opts: VpcOptions = {
            "db_subnet_group_name": None,
            "vpc_security_groups": [],
            "security_groups": [],
        }

        if defn.subnet_group:
            if defn.subnet_group.startswith("res-"):
                opts["db_subnet_group_name"] = self.depl.get_typed_resource(
                    defn.subnet_group[4:].split(".")[0],
                    "rds-subnet-group",
                    RDSDbSubnetGroupState,
                ).group_name
            else:
                opts["db_subnet_group_name"] = defn.subnet_group

            opts["vpc_security_groups"] = self.fetch_vpc_security_group_resources(
                defn.vpc_security_groups
            )
        else:
            opts["security_groups"] = self.fetch_rds_security_group_resources(
                defn.rds_dbinstance_security_groups
            )

        return opts

    def after_activation(self, defn: EC2RDSDbInstanceDefinition):
        # TODO: Warn about old instances, but don't clean them up.
        pass

    def destroy(self, wipe=False):
        if self.state == self.UP or self.state == self.STARTING:
            if not self.depl.logger.confirm(
                "are you sure you want to destroy RDS instance ‘{0}’?".format(
                    self.rds_dbinstance_id
                )
            ):
                return False

            dbinstance = None
            if self.rds_dbinstance_id:
                dbinstance = self._try_fetch_dbinstance(self.rds_dbinstance_id)

            if dbinstance and dbinstance["DBInstanceStatus"] != "deleting":
                self.logger.log(
                    "deleting RDS instance `{0}'...".format(self.rds_dbinstance_id)
                )
                final_snapshot_id = "%s-final-snapshot-%s" % (
                    self.rds_dbinstance_id,
                    uuid4().hex,
                )
                self.logger.log("saving final snapshot as %s" % final_snapshot_id)
                self._connect().delete_db_instance(
                    DBInstanceIdentifier=self.rds_dbinstance_id,
                    FinalDBSnapshotIdentifier=final_snapshot_id,
                )

                while True:
                    if dbinstance["DBInstanceStatus"] == "deleting":
                        dbinstance = self._try_fetch_dbinstance(self.rds_dbinstance_id)
                        continue
                    else:
                        break
                    self.log_continue("[{0}] ".format(dbinstance["DBInstanceStatus"]))
                    time.sleep(6)

            else:
                self.logger.log(
                    "RDS instance `{0}` does not exist, skipping.".format(
                        self.rds_dbinstance_id
                    )
                )

            self.state = self.MISSING
        return True
