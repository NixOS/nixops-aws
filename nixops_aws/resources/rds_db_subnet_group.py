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


class RDSDbSubnetGroupState(nixops.resources.ResourceState[RDSDbSubnetGroupDefinition]):
    """State of an EC2 security group."""

    definition_type = RDSDbSubnetGroupDefinition
    group_name = nixops.util.attr_property("group_name", None)
    region = nixops.util.attr_property("region", None)
    description = nixops.util.attr_property("description", None)
    subnet_ids = nixops.util.attr_property("subnet_ids", [], "json")

    access_key_id: Optional[str] = None
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
        if self._rds_conn:
            return self._rds_conn
        self._conn = nixops_aws.ec2_utils.connect_rds_boto3(
            self.region, self.access_key_id
        )
        return self._conn

    def create(
        self,
        defn: RDSDbSubnetGroupDefinition,
        check: bool,
        allow_reboot: bool,
        allow_recreate: bool,
    ):
        self.region = defn.config.region
        self.access_key_id = (
            defn.config.accessKeyId or nixops_aws.ec2_utils.get_access_key_id()
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

        if self.state != self.UP:
            self.logger.log(f"Creating RDS Subnet Group {self.group_name}")
            self._connect_rds().create_db_subnet_group(
                DBSubnetGroupName=self.group_name,
                DBSubnetGroupDescription=self.description,
                SubnetIds=subnets,
            )
            self.state = self.UP
        else:
            self._connect_rds().modify_db_subnet_group(
                DBSubnetGroupName=self.group_name,
                DBSubnetGroupDescription=self.description,
                SubnetIds=subnets,
            )

    def destroy(self, wipe=False):

        self.access_key_id = nixops_aws.ec2_utils.get_access_key_id()
        client = self._connect_rds()
        try:
            nixops_aws.ec2_utils.retry(
                lambda: client.delete_db_subnet_group(
                    DBSubnetGroupName=self.group_name
                ),
                error_codes=["DependencyViolation"],
                logger=self.logger,
            )
        except client.exceptions.DBSubnetGroupNotFoundFault:
            pass
        self.state = self.MISSING
        return True
