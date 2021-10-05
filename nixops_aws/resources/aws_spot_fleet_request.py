# -*- coding: utf-8 -*-
import dataclasses
from typing import TYPE_CHECKING, Union, Optional, List
import boto3
import nixops.util
from nixops.resources import ResourceDefinition
from nixops.resources import ResourceState
from nixops.util import ImmutableValidatedObject
import nixops_aws.ec2_utils
import botocore.exceptions
from . import ec2_common
from .iam_role import IAMRoleState

from .types.aws_spot_fleet import SpotFleetRequestOptions

from mypy_boto3_ec2 import type_defs as ec2types
from mypy_boto3_ec2 import literals as ec2literals

if TYPE_CHECKING:
    from mypy_boto3_ec2.type_defs import (
        LaunchTemplateConfigTypeDef,
        FleetLaunchTemplateSpecificationTypeDef,
    )
else:
    LaunchTemplateConfigTypeDef = dict
    FleetLaunchTemplateSpecificationTypeDef = dict


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
    # launchTemplateConfigs: Optional[List[LaunchTemplateConfigOptions]]
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
    # spotMaxTotalPrice: Optional[str] # todo: price
    # spotPrice: Optional[str] # todo: price
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
            immutable_keys = [
                "region",
                "type",
                "iamFleetRole",
            ]
            immutable_diff = [
                k for k in immutable_keys if getattr(self, k) != getattr(defn.config, k)
            ]
            if immutable_diff:
                raise Exception(
                    "changing keys `{}` of an existing spot fleet request is not supported".format(
                        immutable_diff
                    )
                )

            mutable_keys = [
                # "excessCapacityTerminationPolicy",
                # "launchTemplateConfigs",
                "targetCapacity",
                # "onDemandTargetCapacity",
            ]
            mutable_diff = [
                k for k in mutable_keys if getattr(self, k) != getattr(defn.config, k)
            ]
            if mutable_diff:
                request = ec2types.ModifySpotFleetRequestRequestRequestTypeDef(
                    # ExcessCapacityTerminationPolicy=
                    # LaunchTemplateConfigs=
                    SpotFleetRequestId=self.spotFleetRequestId,
                    # TargetCapacity=
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

            tags = dict(defn.config.tags)
            tags.update(self.get_common_tags())

            # # TODO instance tags
            # instance_tags = dict(defn.config.tags)
            # instance_tags.update(self.get_common_tags())

            # The region may only be set once, when a new spot fleet is being requested
            with self.depl._db:
                self.region = defn.config.region

            launch_template_configs = [
                LaunchTemplateConfigTypeDef(
                    LaunchTemplateSpecification=FleetLaunchTemplateSpecificationTypeDef(
                        # LaunchTemplateId: str
                        LaunchTemplateName=config.launchTemplateSpecification.launchTemplateName,
                        Version=config.launchTemplateSpecification.version,
                    ),
                    # Overrides=
                )
                for config in defn.config.launchTemplateConfigs
            ]

            self._request_spot_fleet(
                ec2types.RequestSpotFleetRequestRequestTypeDef(
                    SpotFleetRequestConfig=ec2types.SpotFleetRequestConfigDataTypeDef(
                        # AllocationStrategy=
                        # OnDemandAllocationStrategy=
                        # SpotMaintenanceStrategies=
                        # ClientToken=
                        # ExcessCapacityTerminationPolicy=
                        # FulfilledCapacity=
                        # OnDemandFulfilledCapacity=
                        IamFleetRole=self._arn_from_role_name(defn.config.iamFleetRole),
                        # LaunchSpecifications=
                        LaunchTemplateConfigs=launch_template_configs,
                        # SpotPrice=
                        TargetCapacity=0,
                        # OnDemandTargetCapacity=
                        # OnDemandMaxTotalPrice=
                        # SpotMaxTotalPrice=
                        # TerminateInstancesWithExpiration=
                        Type=defn.config.type,
                        # ValidFrom=
                        # ValidUntil=
                        # ReplaceUnhealthyInstances=
                        # InstanceInterruptionBehavior=
                        # LoadBalancersConfig=
                        # InstancePoolsToUseCount=
                        TagSpecifications=[
                            ec2types.TagSpecificationTypeDef(
                                ResourceType="spot-fleet-request",
                                Tags=[
                                    ec2types.TagTypeDef(Key=k, Value=tags[k])
                                    for k in tags
                                ],
                            )
                        ],
                    )
                )
            )

    def check(self):
        if self.spotFleetRequestId is None:
            self.state = self.MISSING
            return

        self._describe_spot_fleet_requests(
            ec2types.DescribeSpotFleetRequestsRequestRequestTypeDef(
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
            "canceling spot fleet request with id ‘{0}’...", self.spotFleetRequestId
        )
        try:
            self._cancel_spot_fleet_requests(
                ec2types.CancelSpotFleetRequestsRequestRequestTypeDef(
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

    def _to_resource_state(self, state: ec2literals.BatchStateType) -> int:
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

    def _arn_from_role_name(self, role_name):
        if role_name.startswith("arn:aws:iam"):
            return role_name

        role_arn = self.get_client("iam").get_role(RoleName=role_name)
        return role_arn["Role"]["Arn"]

    def _save_config_data(self, config: ec2types.SpotFleetRequestConfigDataTypeDef):
        if config.get("AllocationStrategy") is not None:
            self.allocationStrategy = config["AllocationStrategy"]
        # if config['OnDemandAllocationStrategy'] is not None:
        #     self.onDemandAllocationStrategy = config['OnDemandAllocationStrategy']
        # if config['SpotMaintenanceStrategies'] is not None:
        #     self.spotMaintenanceStrategies = config['SpotMaintenanceStrategies']
        # if config['ClientToken'] is not None:
        #     self.clientToken = config['ClientToken']
        # if config['ExcessCapacityTerminationPolicy'] is not None:
        #     self.excessCapacityTerminationPolicy = (
        #         config['ExcessCapacityTerminationPolicy']
        #     )
        # if config['FulfilledCapacity'] is not None:
        #     self.fulfilledCapacity = config['FulfilledCapacity']
        # if config['OnDemandFulfilledCapacity'] is not None:
        #     self.onDemandFulfilledCapacity = config['OnDemandFulfilledCapacity']
        self.iamFleetRole = config["IamFleetRole"]
        # if config['LaunchSpecifications'] is not None:
        #     self.launchSpecifications = config['LaunchSpecifications']
        # if config['LaunchTemplateConfigs'] is not None:
        #     self.launchTemplateConfigs = config['LaunchTemplateConfigs']
        # if config['SpotPrice'] is not None:
        #     self.spotPrice = config['SpotPrice']
        self.targetCapacity = config["TargetCapacity"]
        # if config['OnDemandTargetCapacity'] is not None:
        #     self.onDemandTargetCapacity = config['OnDemandTargetCapacity']
        # if config['OnDemandMaxTotalPrice'] is not None:
        #     self.onDemandMaxTotalPrice = config['OnDemandMaxTotalPrice']
        # if config['SpotMaxTotalPrice'] is not None:
        #     self.spotMaxTotalPrice = config['SpotMaxTotalPrice']
        # if config['TerminateInstancesWithExpiration'] is not None:
        #     self.terminateInstancesWithExpiration = (
        #         config['TerminateInstancesWithExpiration']
        #     )
        if config["Type"] is not None:
            self.type = config["Type"]
        # if config['ValidFrom'] is not None:
        #     self.validFrom = config['ValidFrom']
        # if config['ValidUntil'] is not None:
        #     self.validUntil = config['ValidUntil']
        # if config['ReplaceUnhealthyInstances'] is not None:
        #     self.replaceUnhealthyInstances = config['ReplaceUnhealthyInstances']
        # if config['InstanceInterruptionBehavior'] is not None:
        #     self.instanceInterruptionBehavior = (
        #         config['InstanceInterruptionBehavior']
        #     )
        # if config['LoadBalancersConfig'] is not None:
        #     self.loadBalancersConfig = config['LoadBalancersConfig']
        # if config['InstancePoolsToUseCount'] is not None:
        #     self.instancePoolsToUseCount = config['InstancePoolsToUseCount']
        # if config['TagSpecifications'] is not None:
        #     self.tagSpecifications = config['TagSpecifications']

    def _save_tags(self, tags: List[ec2types.TagTypeDef]):
        pass

    # Boto3 wrappers

    def _describe_spot_fleet_requests(
        self, request: ec2types.DescribeSpotFleetRequestsRequestRequestTypeDef
    ) -> Optional[ec2types.DescribeSpotFleetRequestsResponseTypeDef]:
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
        self, request: ec2types.RequestSpotFleetRequestRequestTypeDef
    ) -> ec2types.RequestSpotFleetResponseTypeDef:
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
        self, request: ec2types.ModifySpotFleetRequestRequestRequestTypeDef
    ) -> Optional[ec2types.ModifySpotFleetRequestResponseTypeDef]:
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
        self, request: ec2types.CancelSpotFleetRequestsRequestRequestTypeDef
    ) -> ec2types.CancelSpotFleetRequestsResponseTypeDef:
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
