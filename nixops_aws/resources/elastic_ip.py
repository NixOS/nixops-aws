# -*- coding: utf-8 -*-

# Automatic provisioning of EC2 elastic IP addresses.

import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
import botocore.exceptions

from .types.elastic_ip import ElasticIpOptions


class ElasticIPDefinition(nixops.resources.ResourceDefinition):
    """Definition of an EC2 elastic IP address."""

    config: ElasticIpOptions

    @classmethod
    def get_type(cls):
        return "elastic-ip"

    @classmethod
    def get_resource_type(cls):
        return "elasticIPs"

    def show_type(self):
        return "{0}".format(self.get_type())


class ElasticIPState(nixops.resources.ResourceState[ElasticIPDefinition]):
    """State of an EC2 elastic IP address."""

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("ec2.accessKeyId", None)
    region = nixops.util.attr_property("ec2.region", None)
    public_ipv4 = nixops.util.attr_property("ec2.ipv4", None)
    allocation_id = nixops.util.attr_property("allocationId", None)
    vpc = nixops.util.attr_property("vpc", False, bool)

    @classmethod
    def get_type(cls):
        return "elastic-ip"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn_boto3 = None

    def show_type(self):
        s = super(ElasticIPState, self).show_type()
        if self.state == self.UP:
            s = "{0} [{1}]".format(s, self.region)
        return s

    @property
    def resource_id(self):
        return self.allocation_id

    def get_physical_spec(self):
        physical = {}
        if self.public_ipv4:
            physical["address"] = self.public_ipv4
        return physical

    def prefix_definition(self, attr):
        return {("resources", "elasticIPs"): attr}

    def _connect_boto3(self, region):
        if self._conn_boto3:
            return self._conn_boto3
        self._conn_boto3 = nixops_aws.ec2_utils.connect_ec2_boto3(
            region, self.access_key_id
        )
        return self._conn_boto3

    def create(self, defn: ElasticIPDefinition, check, allow_reboot, allow_recreate):

        self.access_key_id = (
            defn.config.accessKeyId or nixops_aws.ec2_utils.get_access_key_id()
        )
        if not self.access_key_id:
            raise Exception(
                "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )

        if self.state == self.UP and (self.region != defn.config.region):
            raise Exception(
                "changing the region of an elastic IP address is not supported"
            )

        if self.state != self.UP:

            is_vpc = defn.config.vpc
            domain = "vpc" if is_vpc else "standard"

            self.log(
                "creating elastic IP address (region ‘{0}’ - domain ‘{1}’)...".format(
                    defn.config.region, domain
                )
            )
            address = self._connect_boto3(defn.config.region).allocate_address(
                Domain=domain
            )

            # FIXME: if we crash before the next step, we forget the
            # address we just created.  Doesn't seem to be anything we
            # can do about this.

            with self.depl._db:
                self.state = self.UP
                self.region = defn.config.region
                self.public_ipv4 = address["PublicIp"]
                if is_vpc:
                    self.allocation_id = address["AllocationId"]
                self.vpc = is_vpc

            self.log("IP address is {0}".format(self.public_ipv4))

    def describe_eip(self):
        try:
            response = self._connect_boto3(self.region).describe_addresses(
                PublicIps=[self.public_ipv4]
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "InvalidAddress.NotFound":
                self.warn("public IP {} was deleted".format(self.public_ipv4))
                return None
            else:
                raise error
        if len(response["Addresses"]) == 0:
            self.warn("public IP {} was deleted".format(self.public_ipv4))
            return None
        return response["Addresses"][0]

    def check(self):
        eip = self.describe_eip()
        if eip is None:
            self.state = self.MISSING

    def destroy(self, wipe=False):
        if self.state == self.UP:
            eip = self.describe_eip()
            if eip is not None:
                vpc = eip.get("Domain", None) == "vpc"
                if "AssociationId" in eip.keys():
                    self.log(
                        "disassociating elastic ip {0} with assocation ID {1}".format(
                            eip["PublicIp"], eip["AssociationId"]
                        )
                    )
                    if vpc:
                        self._connect_boto3(self.region).disassociate_address(
                            AssociationId=eip["AssociationId"]
                        )
                self.log("releasing elastic IP {}".format(eip["PublicIp"]))
                if vpc is True:
                    self._connect_boto3(self.region).release_address(
                        AllocationId=eip["AllocationId"]
                    )
                else:
                    self._connect_boto3(self.region).release_address(
                        PublicIp=eip["PublicIp"]
                    )

            with self.depl._db:
                self.state = self.MISSING
                self.public_ipv4 = None
                self.allocation_id = None
                self.vpc = None

        return True
