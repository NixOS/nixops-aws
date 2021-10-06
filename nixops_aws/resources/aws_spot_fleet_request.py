# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Optional, List
import boto3
import nixops.util
from nixops.resources import ResourceDefinition
from nixops.resources import ResourceState
import nixops_aws.ec2_utils
import botocore.exceptions
from . import ec2_common
from .iam_role import IAMRoleState

from .types.aws_spot_fleet import SpotFleetRequestOptions


if TYPE_CHECKING:
    from mypy_boto3_ec2.literals import BatchStateType
    from mypy_boto3_ec2.type_defs import (
        LaunchTemplateConfigTypeDef,
        FleetLaunchTemplateSpecificationTypeDef,
        LaunchTemplateOverridesTypeDef,
        TagSpecificationTypeDef,
        SpotFleetRequestConfigDataTypeDef,
        TagTypeDef,
        DescribeSpotFleetRequestsRequestRequestTypeDef,
        DescribeSpotFleetRequestsResponseTypeDef,
        RequestSpotFleetRequestRequestTypeDef,
        RequestSpotFleetResponseTypeDef,
        ModifySpotFleetRequestRequestRequestTypeDef,
        ModifySpotFleetRequestResponseTypeDef,
        CancelSpotFleetRequestsRequestRequestTypeDef,
        CancelSpotFleetRequestsResponseTypeDef,
    )
else:
    BatchStateType = object
    LaunchTemplateConfigTypeDef = dict
    FleetLaunchTemplateSpecificationTypeDef = dict
    LaunchTemplateOverridesTypeDef = dict
    TagSpecificationTypeDef = dict
    SpotFleetRequestConfigDataTypeDef = dict
    TagTypeDef = dict
    DescribeSpotFleetRequestsRequestRequestTypeDef = dict
    DescribeSpotFleetRequestsResponseTypeDef = dict
    RequestSpotFleetRequestRequestTypeDef = dict
    RequestSpotFleetResponseTypeDef = dict
    ModifySpotFleetRequestRequestRequestTypeDef = dict
    ModifySpotFleetRequestResponseTypeDef = dict
    CancelSpotFleetRequestsRequestRequestTypeDef = dict
    CancelSpotFleetRequestsResponseTypeDef = dict


class awsSpotFleetRequestDefinition(ResourceDefinition):
    """Definition of a spot fleet request"""

    config: SpotFleetRequestOptions

    @classmethod
    def get_type(cls):
        return "aws-spot-fleet-request"

    @classmethod
    def get_resource_type(cls):
        return "awsSpotFleetRequest"

    def show_type(self):
        return "{0}".format(self.get_type())


class awsSpotFleetRequestState(ResourceState, ec2_common.EC2CommonState):
    """State of a spot fleet request"""

    definition_type = awsSpotFleetRequestDefinition

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("accessKeyId", None)
    region = nixops.util.attr_property("region", None)

    spotFleetRequestId = nixops.util.attr_property("spotFleetRequestId", None)
    allocationStrategy = nixops.util.attr_property("allocationStrategy", None)
    # allocationStrategy: Optional[Union[
    #    Literal["lowestPrice"],
    #    Literal["diversified"],
    #    Literal["capacityOptimized"],
    #    Literal["capacityOptimizedPrioritized"]
    # ]],
    # clientToken: Optional[str]
    # excessCapacityTerminationPolicy: Optional[Union[
    #    Literal["noTermination"],
    #    Literal["default"]
    # ]],
    # fulfilledCapacity: Optional[float]

    iamFleetRole = nixops.util.attr_property("iamFleetRole", None)

    # instanceInterruptionBehavior: Optional[Union[
    #     Literal["hibernate"],
    #     Literal["top"],
    #     Literal["terminate"]
    # ]],
    # instancePoolsToUseCount: Optional[int]
    # launchSpecifications = nixops.util.attr_property("launchSpecifications", [], "json")
    launchTemplateConfigs = nixops.util.attr_property(
        "launchTemplateConfigs", [], "json"
    )
    # loadBalancersConfig: Optional[List[LoadBalancersConfigOptions]]
    # onDemandAllocationStrategy: Optional[Union[
    #    Literal["lowestPrice"],
    #    Literal["prioritized"]
    # ]]
    # onDemandFulfilledCapacity: Optional[float]
    # onDemandMaxTotalPrice: Optional[str] # todo: price
    # onDemandTargetCapacity: Optional[int]
    # replaceUnhealthyInstances: Optional[bool]
    # spotMaintenaneStrategies: Optional[SpotMaintenanceStrategiesOptions]
    spotMaxTotalPrice = nixops.util.attr_property("spotMaxTotalPrice", None)
    spotPrice = nixops.util.attr_property("spotPrice", None)
    # # tagSpecifications / tags = Mapping[str, str]
    targetCapacity = nixops.util.attr_property("targetCapacity", 0, int)
    # terminateInstancesWithExpiration: Optional[bool]
    type = nixops.util.attr_property("type", None)
    # validFrom: Optional[Timestamp]
    # validUntil: Optional[Timestamp]

    @classmethod
    def get_type(cls):
        return "aws-spot-fleet-request"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)

    def _exists(self):
        return self.state != self.MISSING

    def show_type(self):
        s = super(awsSpotFleetRequestState, self).show_type()
        return s

    @property
    def resource_id(self):
        return self.spotFleetRequestId

    def create_after(self, resources, defn):
        return {r for r in resources if isinstance(r, IAMRoleState)}

    def get_client(self, service):
        if hasattr(self, "_client"):
            if self._client:
                return self._client

        assert self.region
        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            self.access_key_id
        )
        client = boto3.session.Session().client(
            service_name=service,
            region_name=self.region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        return client

    def create(
        self,
        defn: awsSpotFleetRequestDefinition,
        check: bool,
        allow_reboot: bool,
        allow_recreate: bool,
    ):
        self.access_key_id = (
            defn.config.accessKeyId or nixops_aws.ec2_utils.get_access_key_id()
        )
        if not self.access_key_id:
            raise Exception(
                "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )

        if self._exists():
            immutable_values = {
                "region": defn.config.region,
                "type": defn.config.type,
                "iamFleetRole": self._arn_from_role_name(defn.config.iamFleetRole),
            }
            immutable_diff = {
                k for k in immutable_values if getattr(self, k) != immutable_values[k]
            }  # TODO dict diff
            if immutable_diff:
                raise Exception(
                    "changing keys ‘{0}’ (from ‘{1}’ to ‘{2}’) of an existing spot fleet request is not supported".format(
                        immutable_diff,
                        [getattr(self, k) for k in immutable_diff],
                        [getattr(defn.config, k) for k in immutable_diff],
                    )
                )

            mutable_values = {
                # "excessCapacityTerminationPolicy",
                # "launchTemplateConfigs",
                "targetCapacity": 0,  # defn.config.targetCapacity
                # "onDemandTargetCapacity",
            }
            mutable_diff = [
                k for k in mutable_values if getattr(self, k) != mutable_values[k]
            ]  # TODO dict diff
            if True or mutable_diff:
                request = ModifySpotFleetRequestRequestRequestTypeDef(
                    # ExcessCapacityTerminationPolicy=
                    # LaunchTemplateConfigs=
                    SpotFleetRequestId=self.spotFleetRequestId,
                    TargetCapacity=mutable_values["targetCapacity"]
                    # OnDemandTargetCapacity=
                )

                self.log(
                    "modifying spot fleet request `{}`... ".format(
                        self.spotFleetRequestId
                    )
                )
                self._modify_spot_fleet_request(request)

                # TODO update tags?

        if self.state == self.MISSING:
            self.log(
                "creating spot fleet request with target capacity of ‘{0}’...".format(
                    # self.targetCapacity
                    0
                )
            )
            # The region may only be set once, when a new spot fleet is being requested
            with self.depl._db:
                self.region = defn.config.region

            self._request_spot_fleet(self._to_spot_fleet_request(defn.config))

    def check(self):
        if self.spotFleetRequestId is None:
            self.state = self.MISSING
            return

        self._describe_spot_fleet_requests(
            DescribeSpotFleetRequestsRequestRequestTypeDef(
                # DryRun=None,
                # MaxResults=None,
                # NextToken=None,
                SpotFleetRequestIds=[self.spotFleetRequestId]
            )
        )

        # TODO handle state
        # self.warn()

        return

    def destroy(self, wipe=False):
        if not self._exists():
            return True

        self.log(
            "canceling spot fleet request with id ‘{0}’...".format(
                self.spotFleetRequestId
            )
        )
        try:
            self._cancel_spot_fleet_requests(
                CancelSpotFleetRequestsRequestRequestTypeDef(
                    SpotFleetRequestIds=[self.spotFleetRequestId],
                    TerminateInstances=True,
                )
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.warn(
                    "spot fleet request with id {0} was already deleted".format(
                        self.spotFleetRequestId
                    )
                )
            else:
                raise e

        return True

    # Boto3 helpers

    def _to_resource_state(self, state: BatchStateType) -> int:
        if state == "active":
            return self.UP
        elif state == "cancelled":
            return self.MISSING
        elif state == "cancelled_running":
            return self.MISSING
        elif state == "cancelled_terminating":
            return self.MISSING
        elif state == "failed":
            return self.MISSING
        elif state == "modifying":
            return self.UP
        elif state == "submitted":
            return self.UP
        else:
            return self.UNKNOWN

    def _to_launch_template_overrides(
        self, overrides
    ) -> LaunchTemplateOverridesTypeDef:
        result = LaunchTemplateOverridesTypeDef()
        if overrides.instanceType:
            result["InstanceType"] = overrides.instanceType
        if overrides.spotPrice:
            result["SpotPrice"] = overrides.spotPrice
        if overrides.subnetId:
            result["SubnetId"] = overrides.subnetId
        if overrides.availabilityZone:
            result["AvailabilityZone"] = overrides.availabilityZone
        if overrides.weightedCapacity:
            result["WeightedCapacity"] = overrides.weightedCapacity
        if overrides.priority:
            result["Priority"] = overrides.priority
        return result

    def _to_spot_fleet_request(self, config):
        tags = dict(config.tags)
        tags.update(self.get_common_tags())

        # # TODO instance tags
        # instance_tags = dict(config.tags)
        # instance_tags.update(self.get_common_tags())

        launch_template_configs = [
            LaunchTemplateConfigTypeDef(
                LaunchTemplateSpecification=FleetLaunchTemplateSpecificationTypeDef(
                    # LaunchTemplateId: str
                    LaunchTemplateName=template_config.launchTemplateSpecification.launchTemplateName,
                    Version=template_config.launchTemplateSpecification.version,
                ),
                Overrides=[
                    self._to_launch_template_overrides(overrides)
                    for overrides in template_config.overrides
                ],
            )
            for template_config in config.launchTemplateConfigs
        ]

        request = RequestSpotFleetRequestRequestTypeDef(
            SpotFleetRequestConfig=SpotFleetRequestConfigDataTypeDef(
                # AllocationStrategy=
                # OnDemandAllocationStrategy=
                # SpotMaintenanceStrategies=
                # ClientToken=
                # ExcessCapacityTerminationPolicy=
                # FulfilledCapacity=
                # OnDemandFulfilledCapacity=
                IamFleetRole=self._arn_from_role_name(config.iamFleetRole),
                # LaunchSpecifications=
                LaunchTemplateConfigs=launch_template_configs,
                TargetCapacity=1,  # TODO
                # OnDemandTargetCapacity=
                # OnDemandMaxTotalPrice=
                # TerminateInstancesWithExpiration=
                Type=config.type,
                # ValidFrom=
                # ValidUntil=
                # ReplaceUnhealthyInstances=
                # InstanceInterruptionBehavior=
                # LoadBalancersConfig=
                # InstancePoolsToUseCount=
                TagSpecifications=[
                    TagSpecificationTypeDef(
                        ResourceType="spot-fleet-request",
                        Tags=[TagTypeDef(Key=k, Value=tags[k]) for k in tags],
                    )
                ],
            )
        )
        if config.spotPrice:
            request["SpotFleetRequestConfig"]["SpotPrice"] = config.spotPrice
        if config.spotMaxTotalPrice:
            request["SpotFleetRequestConfig"][
                "SpotMaxTotalPrice"
            ] = config.spotMaxTotalPrice
        return request

    def _arn_from_role_name(self, role_name):
        if role_name.startswith("arn:aws:iam"):
            return role_name

        role_arn = self.get_client("iam").get_role(RoleName=role_name)
        return role_arn["Role"]["Arn"]

    def _save_config_data(self, config: SpotFleetRequestConfigDataTypeDef):
        if config.get("AllocationStrategy") is not None:
            self.allocationStrategy = config["AllocationStrategy"]
        # if config["OnDemandAllocationStrategy"] is not None:
        #     self.onDemandAllocationStrategy = config["OnDemandAllocationStrategy"]
        # if config["SpotMaintenanceStrategies"] is not None:
        #     self.spotMaintenanceStrategies = config["SpotMaintenanceStrategies"]
        # if config["ClientToken"] is not None:
        #     self.clientToken = config["ClientToken"]
        # if config["ExcessCapacityTerminationPolicy"] is not None:
        #     self.excessCapacityTerminationPolicy = (
        #         config["ExcessCapacityTerminationPolicy"]
        #     )
        # if config["FulfilledCapacity"] is not None:
        #     self.fulfilledCapacity = config["FulfilledCapacity"]
        # if config["OnDemandFulfilledCapacity"] is not None:
        #     self.onDemandFulfilledCapacity = config["OnDemandFulfilledCapacity"]
        self.iamFleetRole = config["IamFleetRole"]
        # if config["LaunchSpecifications"] is not None:
        #     self.launchSpecifications = config["LaunchSpecifications"]
        if config["LaunchTemplateConfigs"] is not None:
            self.launchTemplateConfigs = config["LaunchTemplateConfigs"]
        if config["SpotPrice"] is not None:
            self.spotPrice = config["SpotPrice"]
        self.targetCapacity = config["TargetCapacity"]
        # if config["OnDemandTargetCapacity"] is not None:
        #     self.onDemandTargetCapacity = config["OnDemandTargetCapacity"]
        # if config["OnDemandMaxTotalPrice"] is not None:
        #     self.onDemandMaxTotalPrice = config["OnDemandMaxTotalPrice"]
        if config["SpotMaxTotalPrice"] is not None:
            self.spotMaxTotalPrice = config["SpotMaxTotalPrice"]
        # if config["TerminateInstancesWithExpiration"] is not None:
        #     self.terminateInstancesWithExpiration = (
        #         config["TerminateInstancesWithExpiration"]
        #     )
        if config["Type"] is not None:
            self.type = config["Type"]
        # if config["ValidFrom"] is not None:
        #     self.validFrom = config["ValidFrom"]
        # if config["ValidUntil"] is not None:
        #     self.validUntil = config["ValidUntil"]
        # if config["ReplaceUnhealthyInstances"] is not None:
        #     self.replaceUnhealthyInstances = config["ReplaceUnhealthyInstances"]
        # if config["InstanceInterruptionBehavior"] is not None:
        #     self.instanceInterruptionBehavior = (
        #         config["InstanceInterruptionBehavior"]
        #     )
        # if config["LoadBalancersConfig"] is not None:
        #     self.loadBalancersConfig = config["LoadBalancersConfig"]
        # if config["InstancePoolsToUseCount"] is not None:
        #     self.instancePoolsToUseCount = config["InstancePoolsToUseCount"]
        # if config["TagSpecifications"] is not None:
        #     self.tagSpecifications = config["TagSpecifications"]

    def _save_tags(self, tags: List[TagTypeDef]):
        pass

    # Boto3 wrappers

    def _describe_spot_fleet_requests(
        self, request: DescribeSpotFleetRequestsRequestRequestTypeDef
    ) -> Optional[DescribeSpotFleetRequestsResponseTypeDef]:
        def check_response_field(name, value, expected_value):
            if value != expected_value:
                raise Exception(
                    "Unexpected value ‘{0} = {1}’ in response, expected ‘{0} = {2}’".format(
                        name, value, expected_value
                    )
                )

        try:
            response = self.get_client("ec2").describe_spot_fleet_requests(
                # **dataclasses.asdict(request)
                **request
            )
            for config in response["SpotFleetRequestConfigs"]:
                check_response_field(
                    "SpotFleetRequestId",
                    config["SpotFleetRequestId"],
                    self.spotFleetRequestId,
                )

                # TODO:
                # Why is activity status not always present?
                # Is it due to spot fleet being canceled without any instances?
                if response.get("ActivityStatus") == "error":
                    self.warn(
                        "spot fleet activity status is {}, please investigate...".format(
                            response["ActivityStatus"]
                        )
                    )

                if not request.get("DryRun"):
                    with self.depl._db:
                        # Update deployment state from response
                        self.state = self._to_resource_state(
                            config["SpotFleetRequestState"]
                        )
                        self._save_config_data(config["SpotFleetRequestConfig"])
                        self._save_tags(config["Tags"])

            return response
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.state = self.MISSING
                return None
            else:
                raise e

    def _request_spot_fleet(
        self, request: RequestSpotFleetRequestRequestTypeDef
    ) -> RequestSpotFleetResponseTypeDef:
        response = self.get_client("ec2").request_spot_fleet(
            # **dataclasses.asdict(request)
            **request
        )

        if not request.get("DryRun"):
            with self.depl._db:
                self.state = self.UP

                # Save response to deployment state
                self.spotFleetRequestId = response["SpotFleetRequestId"]

                # Save request to deployment state
                self._save_config_data(request["SpotFleetRequestConfig"])

        return response

    def _modify_spot_fleet_request(
        self, request: ModifySpotFleetRequestRequestRequestTypeDef
    ) -> Optional[ModifySpotFleetRequestResponseTypeDef]:
        try:
            response = self.get_client("ec2").modify_spot_fleet_request(
                # **dataclasses.asdict(request)
                **request
            )

            if response.Return:
                with self.depl._db:
                    # Save request to deployment state
                    # if request.ExcessCapacityTerminationPolicy is not None:
                    #     self.excessCapacityTerminationPolicy = (
                    #         request.ExcessCapacityTerminationPolicy
                    #     )
                    # if request.LaunchTemplateConfigs is not None:
                    #     self.launchTemplateConfigs = request.LaunchTemplateConfigs
                    if request["TargetCapacity"] is not None:
                        self.targetCapacity = request["TargetCapacity"]
                    if request["OnDemandTargetCapacity"] is not None:
                        self.onDemandTargetCapacity = request["OnDemandTargetCapacity"]

            return response

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                with self.depl._db:
                    self.state = self.MISSING
                return None
            else:
                raise e

    def _cancel_spot_fleet_requests(
        self, request: CancelSpotFleetRequestsRequestRequestTypeDef
    ) -> CancelSpotFleetRequestsResponseTypeDef:
        response = self.get_client("ec2").cancel_spot_fleet_requests(
            # **dataclasses.asdict(request)
            **request
        )

        def check_response_field(name, value, expected_value):
            if value != expected_value:
                raise Exception(
                    "Unexpected value ‘{0} = {1}’ in response, expected ‘{0} = {2}’".format(
                        name, value, expected_value
                    )
                )

        for item in response["SuccessfulFleetRequests"]:
            check_response_field(
                "SpotFleetRequestId",
                item["SpotFleetRequestId"],
                self.spotFleetRequestId,
            )
            self.state = self._to_resource_state(item["CurrentSpotFleetRequestState"])

        for item in response["UnsuccessfulFleetRequests"]:
            check_response_field(
                "SpotFleetRequestId",
                item["SpotFleetRequestId"],
                self.spotFleetRequestId,
            )
            self.warn(
                "spot fleet request with id ‘{0}’ cancelation failed with error ‘{1}: {2}’".format(
                    self.spotFleetRequestId,
                    response["Error"]["Code"],
                    response["Error"]["Message"],
                )
            )
            self.state = self.UNKNOWN

        return response
