# -*- coding: utf-8 -*-
import base64
import datetime
import nixops.util
import nixops_aws.ec2_utils
import nixops_aws.resources
from nixops_aws.resources.ec2_common import EC2CommonState
import botocore.exceptions
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_ec2.type_defs import CreateLaunchTemplateRequestRequestTypeDef
    from mypy_boto3_ec2.type_defs import RequestLaunchTemplateDataTypeDef
    from mypy_boto3_ec2.type_defs import CreateLaunchTemplateResultTypeDef
    from mypy_boto3_ec2.type_defs import TagSpecificationTypeDef
    from mypy_boto3_ec2.type_defs import LaunchTemplateTagSpecificationRequestTypeDef
    from mypy_boto3_ec2.type_defs import TagTypeDef
else:
    CreateLaunchTemplateRequestRequestTypeDef = dict
    RequestLaunchTemplateDataTypeDef = dict
    CreateLaunchTemplateResultTypeDef = dict
    TagSpecificationTypeDef = dict
    LaunchTemplateTagSpecificationRequestTypeDef = dict
    TagTypeDef = dict


class awsEc2LaunchTemplateDefinition(nixops.resources.ResourceDefinition):
    """Definition of an ec2 launch template"""

    @classmethod
    def get_type(cls):
        return "aws-ec2-launch-template"

    @classmethod
    def get_resource_type(cls):
        return "awsEc2LaunchTemplate"

    def show_type(self):
        return "{0}".format(self.get_type())


class awsEc2LaunchTemplateState(nixops.resources.ResourceState, EC2CommonState):
    """State of an ec2 launch template"""

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("accessKeyId", None)
    region = nixops.util.attr_property("region", None)
    templateName = nixops.util.attr_property("templateName", None)
    templateId = nixops.util.attr_property("templateId", None)
    templateVersion = nixops.util.attr_property("templateVersion", None)
    versionDescription = nixops.util.attr_property("versionDescription", None)
    ebsOptimized = nixops.util.attr_property("ebsOptimized", True, type=bool)
    instanceProfile = nixops.util.attr_property("instanceProfile", None)
    ami = nixops.util.attr_property("ami", None)
    instanceType = nixops.util.attr_property("instanceType", None)
    keyPair = nixops.util.attr_property("keyPair", None)
    userData = nixops.util.attr_property("userData", None)
    securityGroupIds = nixops.util.attr_property("securityGroupIds", None, "json")
    disableApiTermination = nixops.util.attr_property(
        "disableApiTermination", False, type=bool
    )
    instanceInitiatedShutdownBehavior = nixops.util.attr_property(
        "instanceInitiatedShutdownBehavior", None
    )
    placementGroup = nixops.util.attr_property("placementGroup", None)
    zone = nixops.util.attr_property("zone", None)
    tenancy = nixops.util.attr_property("tenancy", None)
    associatePublicIpAddress = nixops.util.attr_property(
        "associatePublicIpAddress", True, type=bool
    )
    networkInterfaceId = nixops.util.attr_property("networkInterfaceId", None)
    subnetId = nixops.util.attr_property("subnetId", None)
    privateIpAddresses = nixops.util.attr_property("privateIpAddresses", {}, "json")
    secondaryPrivateIpAddressCount = nixops.util.attr_property(
        "secondaryPrivateIpAddressCount", None
    )
    monitoring = nixops.util.attr_property("LTMonitoring", False, type=bool)
    spotInstancePrice = nixops.util.attr_property("ec2.spotInstancePrice", None)
    spotInstanceRequestType = nixops.util.attr_property("spotInstanceRequestType", None)
    spotInstanceInterruptionBehavior = nixops.util.attr_property(
        "spotInstanceInterruptionBehavior", None
    )
    spotInstanceTimeout = nixops.util.attr_property("spotInstanceTimeout", None)
    clientToken = nixops.util.attr_property("clientToken", None)
    ebsInitialRootDiskSize = nixops.util.attr_property("ebsInitialRootDiskSize", None)

    @classmethod
    def get_type(cls):
        return "aws-ec2-launch-template"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn_boto3 = None
        self._conn_vpc = None

    def _exists(self):
        return self.state != self.MISSING

    def show_type(self):
        s = super(awsEc2LaunchTemplateState, self).show_type()
        return s

    @property
    def resource_id(self):
        return self.templateId

    def connect_boto3(self, region):
        if self._conn_boto3:
            return self._conn_boto3
        self._conn_boto3 = nixops_aws.ec2_utils.connect_ec2_boto3(
            region, self.access_key_id
        )
        return self._conn_boto3

    def connect_vpc(self):
        if self._conn_vpc:
            return self._conn_vpc
        self._conn_vpc = nixops_aws.ec2_utils.connect_vpc(
            self.region, self.access_key_id
        )
        return self._conn_vpc

    # TODO: Work on how to update the template (create a new version and update default version to use or what)
    # i think this is done automatically so i think i need to remove it right ?
    def create_after(self, resources, defn):
        # EC2 launch templates can require key pairs, IAM roles, security
        # groups and placement groups
        return {
            r
            for r in resources
            if isinstance(r, nixops_aws.resources.ec2_keypair.EC2KeyPairState)
            or isinstance(r, nixops_aws.resources.iam_role.IAMRoleState)
            or isinstance(
                r, nixops_aws.resources.ec2_security_group.EC2SecurityGroupState
            )
            or isinstance(
                r, nixops_aws.resources.ec2_placement_group.EC2PlacementGroupState
            )
            or isinstance(r, nixops_aws.resources.vpc_subnet.VPCSubnetState)
        }

    # fix security group stuff later
    def security_groups_to_ids(self, subnetId, groups):
        sg_names = filter(lambda g: not g.startswith("sg-"), groups)
        if sg_names != [] and subnetId != "":
            # Note: we can use ec2_utils.name_to_security_group but it only works with boto2
            group_ids = []
            for i in groups:
                if i.startswith("sg-"):
                    group_ids.append(i)
                else:
                    try:
                        group_ids.append(
                            self.connect_boto3(self.region).describe_security_groups(
                                Filters=[{"Name": "group-name", "Values": [i]}]
                            )["SecurityGroups"][0]["GroupId"]
                        )
                    except botocore.exceptions.ClientError as error:
                        raise error
            return group_ids
        else:
            return groups

    def create(self, defn, check, allow_reboot, allow_recreate):
        if self.region is None:
            self.region = defn.config["region"]
        elif self.region != defn.config["region"]:
            self.warn(
                "cannot change region of a running instance (from ‘{}‘ to ‘{}‘)".format(
                    self.region, defn.config["region"]
                )
            )

        self.access_key_id = defn.config["accessKeyId"]
        if self.state != self.UP:
            # Use a client token to ensure that the template creation is
            # idempotent; i.e., if we get interrupted before recording
            # the fleet ID, we'll get the same fleet ID on the
            # next run.
            if not self.clientToken:
                with self.depl._db:
                    self.clientToken = nixops.util.generate_random_string(
                        length=48
                    )  # = 64 ASCII chars
                    self.state = self.STARTING

            self.log(
                "creating launch template {} ...".format(defn.config["templateName"])
            )

            tags = defn.config["tags"]
            tags.update(self.get_common_tags())

            self._create_launch_template(
                CreateLaunchTemplateRequestRequestTypeDef(
                    LaunchTemplateName=defn.config["templateName"],
                    VersionDescription=defn.config["versionDescription"],
                    LaunchTemplateData=self._launch_template_data_from_config(
                        defn.config
                    ),
                    ClientToken=self.clientToken,
                    TagSpecifications=[
                        TagSpecificationTypeDef(
                            ResourceType="launch-template",
                            Tags=[TagTypeDef(Key=k, Value=tags[k]) for k in tags],
                        )
                    ],
                )
            )

    def check(self):

        conn = self.connect_boto3(self.region)
        launch_template = conn.describe_launch_templates(
            LaunchTemplateIds=[self.templateId]
        )["LaunchTemplates"]
        if launch_template is None:
            self.state = self.MISSING
            return
        if str(launch_template[0]["DefaultVersionNumber"]) != self.templateVersion:
            self.warn(
                "default version on the launch template is different then nixops managed version..."
            )

    def _destroy(self):

        conn = self.connect_boto3(self.region)
        self.log("deleting ec2 launch template `{}`... ".format(self.templateName))
        try:
            conn.delete_launch_template(LaunchTemplateId=self.templateId)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "InvalidLaunchTemplateId.NotFound":
                self.warn("Template `{}` already deleted...".format(self.templateName))
            else:
                raise error

    def destroy(self, wipe=False):
        if not self._exists():
            return True

        self._destroy()
        return True

    # Boto3 helpers
    def _launch_template_data_from_config(
        self, config
    ) -> RequestLaunchTemplateDataTypeDef:
        common_tags = self.get_common_tags()
        instance_tags = config["instanceTags"]
        volume_tags = config["volumeTags"]

        # Common tags don't necessarily make sense for resources launched using the template
        # Instances launched using this template may override common tags
        instance_tags["CharonTemplateNetworkUUID"] = common_tags["CharonNetworkUUID"]
        instance_tags["CharonTemplateName"] = common_tags["CharonMachineName"]
        instance_tags["CharonTemplateStateFile"] = common_tags["CharonStateFile"]
        volume_tags["CharonTemplateNetworkUUID"] = common_tags["CharonNetworkUUID"]
        volume_tags["CharonTemplateName"] = common_tags["CharonMachineName"]
        volume_tags["CharonTemplateStateFile"] = common_tags["CharonStateFile"]
        if common_tags.get("CharonNetworkName"):
            instance_tags["CharonTemplateNetworkName"] = common_tags[
                "CharonNetworkName"
            ]
            volume_tags["CharonTemplateNetworkName"] = common_tags["CharonNetworkName"]

        data = RequestLaunchTemplateDataTypeDef(
            EbsOptimized=config["ebsOptimized"],
            ImageId=config["ami"],
            Placement=dict(Tenancy=config["tenancy"]),
            Monitoring=dict(Enabled=config["monitoring"]),
            DisableApiTermination=config["disableApiTermination"],
            InstanceInitiatedShutdownBehavior=config[
                "instanceInitiatedShutdownBehavior"
            ],
            TagSpecifications=[
                LaunchTemplateTagSpecificationRequestTypeDef(
                    ResourceType="instance",
                    Tags=[
                        TagTypeDef(Key=k, Value=instance_tags[k]) for k in instance_tags
                    ],
                ),
                LaunchTemplateTagSpecificationRequestTypeDef(
                    ResourceType="volume",
                    Tags=[TagTypeDef(Key=k, Value=volume_tags[k]) for k in volume_tags],
                ),
            ],
        )
        if config["instanceProfile"] != "":
            data["IamInstanceProfile"] = dict(Name=config["instanceProfile"])
        if config["userData"]:
            data["UserData"] = str(base64.b64encode(config["userData"]), "utf-8")
        if config["instanceType"]:
            data["InstanceType"] = config["instanceType"]
        if config["placementGroup"] != "":
            data["Placement"]["GroupName"] = config["placementGroup"]
        if config["zone"]:
            data["Placement"]["AvailabilityZone"] = config["zone"]

        if config["spotInstancePrice"] != 0:
            data["InstanceMarketOptions"] = dict(
                MarketType="spot",
                SpotOptions=dict(
                    MaxPrice=str(config["spotInstancePrice"] / 100.0),
                    SpotInstanceType=config["spotInstanceRequestType"],
                    ValidUntil=(
                        datetime.datetime.utcnow()
                        + datetime.timedelta(0, config["spotInstanceTimeout"])
                    ).isoformat(),
                    InstanceInterruptionBehavior=config[
                        "spotInstanceInterruptionBehavior"
                    ],
                ),
            )
        if config["networkInterfaceId"] != "" or config["subnetId"] != "":
            data["NetworkInterfaces"] = [
                dict(
                    DeviceIndex=0,
                    AssociatePublicIpAddress=config["associatePublicIpAddress"],
                )
            ]
            if config["securityGroupIds"] != []:
                data["NetworkInterfaces"][0]["Groups"] = self.security_groups_to_ids(
                    config["subnetId"], config["securityGroupIds"]
                )
            if config["networkInterfaceId"] != "":
                if config["networkInterfaceId"].startswith("res-"):
                    config["networkInterfaceId"] = self.depl.get_typed_resource(
                        config["networkInterfaceId"][4:].split(".")[0],
                        "vpc-network-interface",
                        nixops_aws.resources.vpc_network_interface.VPCNetworkInterfaceState,
                    )._state["networkInterfaceId"]
                data["NetworkInterfaces"][0]["NetworkInterfaceId"] = config[
                    "networkInterfaceId"
                ]
            if config["subnetId"] != "":
                if config["subnetId"].startswith("res-"):
                    config["subnetId"] = self.depl.get_typed_resource(
                        config["subnetId"][4:].split(".")[0],
                        "vpc-subnet",
                        nixops_aws.resources.vpc_subnet.VPCSubnetState,
                    )._state["subnetId"]
                data["NetworkInterfaces"][0]["SubnetId"] = config["subnetId"]
            if config["secondaryPrivateIpAddressCount"]:
                data["NetworkInterfaces"][0]["SecondaryPrivateIpAddressCount"] = config[
                    "secondaryPrivateIpAddressCount"
                ]
            if config["privateIpAddresses"]:
                data["NetworkInterfaces"][0]["PrivateIpAddresses"] = config[
                    "privateIpAddresses"
                ]
        if config["keyPair"] != "":
            data["KeyName"] = config["keyPair"]

        ami = self.connect_boto3(self.region).describe_images(ImageIds=[config["ami"]])[
            "Images"
        ][0]

        # TODO: BlockDeviceMappings for non root volumes
        data["BlockDeviceMappings"] = [
            dict(
                DeviceName="/dev/sda1",
                Ebs=dict(
                    DeleteOnTermination=True,
                    VolumeSize=config["ebsInitialRootDiskSize"],
                    VolumeType=ami["BlockDeviceMappings"][0]["Ebs"]["VolumeType"],
                ),
            )
        ]

        return data

    # Boto3 wrappers
    def _create_launch_template(
        self, request: CreateLaunchTemplateRequestRequestTypeDef
    ) -> CreateLaunchTemplateResultTypeDef:
        try:
            response = self.connect_boto3(self.region).create_launch_template(**request)
        except botocore.exceptions.ClientError as error:
            raise error
            # Not sure whether to use lambda retry or keep it like this
        with self.depl._db:
            self.state = self.UP

            self.templateId = response["LaunchTemplate"]["LaunchTemplateId"]
            self.templateName = request["LaunchTemplateName"]
            self.templateVersion = response["LaunchTemplate"]["LatestVersionNumber"]
            self.versionDescription = request["VersionDescription"]
        return response
