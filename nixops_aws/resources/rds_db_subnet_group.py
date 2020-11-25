# -*- coding: utf-8 -*-

# Automatic provisioning of EC2 security groups.

import nixops.resources
import nixops.util
import nixops_aws.ec2_utils
from typing import Optional, List, TYPE_CHECKING
from .types.rds_db_subnet_group import RDSDbSubnetGroupOptions
from .vpc_subnet import VPCSubnetState

if TYPE_CHECKING:
    import mypy_boto3_rds


class RDSDbSubnetGroupDefinition(nixops.resources.ResourceDefinition):
    """Definition of an RDS DB Subnet Group."""

    config: RDSDbSubnetGroupOptions

    @classmethod
    def get_type(cls):
        return "rds-subnet-group"

    @classmethod
    def get_resource_type(cls):
        return "rdsSubnetGroups"

    def __init__(self, name: str, config: nixops.resources.ResourceEval):
        super(RDSDbSubnetGroupDefinition, self).__init__(name, config)

        self.group_name: str = self.config.name
        self.description: Optional[str] = self.config.description
        self.subnet_ids: List[str] = self.config.subnetIds

        # common params
        self.region: str = self.config.region
        self.access_key_id: str = self.config.accessKeyId

    def show_type(self):
        return "{0} [{1}]".format(self.get_type(), self.region)


class RDSDbSubnetGroupState(nixops.resources.ResourceState[RDSDbSubnetGroupDefinition]):
    """State of an EC2 security group."""

    definition_type = RDSDbSubnetGroupDefinition
    group_name = nixops.util.attr_property("group_name", None)
    region = nixops.util.attr_property("region", None)
    description = nixops.util.attr_property("description", None)
    subnet_ids = nixops.util.attr_property("subnet_ids", [], "json")
    access_key_id = nixops.util.attr_property("accessKeyId", None)

    _rds_conn: Optional["mypy_boto3_rds.RDSClient"] = None

    @classmethod
    def get_type(cls):
        return "rds-subnet-group"

    @property
    def resource_id(self):
        return self.group_name

    def create_after(self, resources, defn):
        return {r for r in resources if isinstance(r, VPCSubnetState)}

    def _connect_rds(self) -> "mypy_boto3_rds.RDSClient":
        if not self._rds_conn:
            self._rds_conn = nixops_aws.ec2_utils.connect_rds_boto3(
                self.region, self.access_key_id
            )
        return self._rds_conn

    def create(
        self,
        defn: RDSDbSubnetGroupDefinition,
        check: bool,
        allow_reboot: bool,
        allow_recreate: bool,
    ):
        self.region = defn.config.region
        self.access_key_id = (
            defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
        )

        if not self.access_key_id:
            raise Exception(
                "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )

        if self.state == self.UP and (self.region != defn.config.region):
            raise Exception(
                "changing the region of an RDS Subnet Group is not supported"
            )
        if self.state == self.UP and (self.group_name != defn.config.name):
            raise Exception("changing the name of an RDS Subnet Group is not supported")

        self.group_name = defn.config.name
        self.description = defn.config.description

        subnets: List[str] = []
        for s in defn.config.subnetIds:
            if s.startswith("res-"):
                res = self.depl.get_typed_resource(
                    s[4:].split(".")[0], "vpc-subnet", VPCSubnetState
                )
                subnets.append(res._state["subnetId"])
            else:
                subnets.append(s)

        rds_client = self._connect_rds()
        if self.state != self.UP:
            self.logger.log("creating RDS Subnet Group ‘{0}’..".format(self.group_name))
            try:

                rds_client.create_db_subnet_group(
                    DBSubnetGroupName=self.group_name,
                    DBSubnetGroupDescription=self.description,
                    SubnetIds=subnets,
                )
            except rds_client.exceptions.DBSubnetGroupAlreadyExistsFault:
                self.logger.error(
                    "The DB subnet group ‘{0}’ already exists.".format(self.group_name)
                )
                raise
            self.state = self.UP
        else:
            rds_client.modify_db_subnet_group(
                DBSubnetGroupName=self.group_name,
                DBSubnetGroupDescription=self.description,
                SubnetIds=subnets,
            )

    def destroy(self, wipe=False):

        if self.state == self.UP:
            if not self.depl.logger.confirm(
                "are you sure you want to destroy the RDS subnet group ‘{0}’?".format(
                    self.group_name
                )
            ):
                return False

            rds_client = self._connect_rds()
            try:
                self.logger.log(
                    "deleting RDS subnet group ‘{0}’..".format(self.group_name)
                )
                nixops_aws.ec2_utils.retry(
                    lambda: rds_client.delete_db_subnet_group(
                        DBSubnetGroupName=self.group_name
                    ),
                    error_codes=["DependencyViolation"],
                    logger=self.logger,
                )
            except rds_client.exceptions.DBSubnetGroupNotFoundFault:
                self.logger.log(
                    "RDS subnet group ‘{0}’ does not exist, skipping.".format(
                        self.group_name
                    )
                )
            except rds_client.exceptions.InvalidDBSubnetGroupStateFault:
                self.logger.error(
                    "RDS Subnet group ‘{0}’ is being used by a database instance".format(
                        self.group_name
                    )
                )
                return False
            self.state = self.MISSING
        return True
