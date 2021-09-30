# -*- coding: utf-8 -*-
import dataclasses
from typing import Union
from typing import Optional
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
from .types.aws_spot_fleet import RequestSpotFleet
from .types.aws_spot_fleet import RequestSpotFleetResponse
from .types.aws_spot_fleet import DescribeSpotFleetRequests
from .types.aws_spot_fleet import DescribeSpotFleetRequestsResponse
from .types.aws_spot_fleet import ModifySpotFleetRequest
from .types.aws_spot_fleet import ModifySpotFleetRequestResponse
from .types.aws_spot_fleet import CancelSpotFleetRequests
from .types.aws_spot_fleet import CancelSpotFleetRequestsResponse
from .types import aws_shapes as aws

from mypy_boto3_ec2 import type_defs as ec2types


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
    # allocationStrategy: Optional[Union[
    #    Literal["lowestPrice"],
    #    Literal["diversified"],
    #    Literal["capacityOptimized"],
    #    Literal["capacityOptimizedPrioritized"]
    # ]],
    # clientToken: Optional[str],
    # excessCapacityTerminationPolicy: Optional[Union[
    #    Literal["noTermination"],
    #    Literal["default"]
    # ]],
    # fulfilledCapacity: Optional[float],
    iamFleetRole = nixops.util.attr_property("iamFleetRole", None)
    # instanceInterruptionBehavior: Optional[Union[
    #     Literal["hibernate"],
    #     Literal["top"],
    #     Literal["terminate"]
    # ]],
    # instancePoolsToUseCount: Optional[int],
    # launchSpecifications = nixops.util.attr_property("launchSpecifications", [], "json")
    # launchTemplateConfigs: Optional[List[LaunchTemplateConfigOptions]],
    # loadBalancersConfig: Optional[List[LoadBalancersConfigOptions]],
    # onDemandAllocationStrategy: Optional[Union[
    #    Literal["lowestPrice"],
    #    Literal["prioritized"]
    # ]],
    # onDemandFulfilledCapacity: Optional[float],
    # onDemandMaxTotalPrice: Optional[str], # todo: price
    # onDemandTargetCapacity: Optional[int],
    # replaceUnhealthyInstances: Optional[bool],
    # spotMaintenaneStrategies: Optional[SpotMaintenanceStrategiesOptions],
    # spotMaxTotalPrice: Optional[str], # todo: price
    # spotPrice: Optional[str], # todo: price
    # # tagSpecifications / tags = Mapping[str, str],
    # targetCapacity = nixops.util.attr_property("targetCapacity", None, int)
    # terminateInstancesWithExpiration: Optional[bool],
    # requestType: Optional[Union[
    #     Literal["request"],
    #     Literal["maintain"],
    #     Literal["instant"]
    # ]],
    # validFrom: Optional[Timestamp],
    # validUntil: Optional[Timestamp]

    @classmethod
    def get_type(cls):
        return "aws-spot-fleet-request"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn_boto3 = None

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

    def save_deploy_state(
        self,
        aws_config: Union[
            ec2types.RequestSpotFleetRequestRequestTypeDef,
            # ec2types.RequestSpotFleetResponse,
            RequestSpotFleetResponse,
            ModifySpotFleetRequest,
            ModifySpotFleetRequestResponse,
        ],
    ):
        with self.depl._db:
            if isinstance(aws_config, RequestSpotFleet):
                data = aws_config.SpotFleetRequestConfig
                # if data.AllocationStrategy != None:
                #     self.allocationStrategy = data.AllocationStrategy
                # if data.OnDemandAllocationStrategy != None:
                #     self.onDemandAllocationStrategy = data.OnDemandAllocationStrategy
                # if data.SpotMaintenanceStrategies != None:
                #     self.spotMaintenanceStrategies = data.SpotMaintenanceStrategies
                # if data.ClientToken != None:
                #     self.clientToken = data.ClientToken
                # if data.ExcessCapacityTerminationPolicy != None:
                #     self.excessCapacityTerminationPolicy = (
                #         data.ExcessCapacityTerminationPolicy
                #     )
                # if data.FulfilledCapacity != None:
                #     self.fulfilledCapacity = data.FulfilledCapacity
                # if data.OnDemandFulfilledCapacity != None:
                #     self.onDemandFulfilledCapacity = data.OnDemandFulfilledCapacity
                self.iamFleetRole = data.IamFleetRole
                # if data.LaunchSpecifications != None:
                #     self.launchSpecifications = data.LaunchSpecifications
                # if data.LaunchTemplateConfigs != None:
                #     self.launchTemplateConfigs = data.LaunchTemplateConfigs
                # if data.SpotPrice != None:
                #     self.spotPrice = data.SpotPrice
                self.targetCapacity = data.TargetCapacity
                # if data.OnDemandTargetCapacity != None:
                #     self.onDemandTargetCapacity = data.OnDemandTargetCapacity
                # if data.OnDemandMaxTotalPrice != None:
                #     self.onDemandMaxTotalPrice = data.OnDemandMaxTotalPrice
                # if data.SpotMaxTotalPrice != None:
                #     self.spotMaxTotalPrice = data.SpotMaxTotalPrice
                # if data.TerminateInstancesWithExpiration != None:
                #     self.terminateInstancesWithExpiration = (
                #         data.TerminateInstancesWithExpiration
                #     )
                if data.Type is not None:
                    self.type = data.Type
                # if data.ValidFrom != None:
                #     self.validFrom = data.ValidFrom
                # if data.ValidUntil != None:
                #     self.validUntil = data.ValidUntil
                # if data.ReplaceUnhealthyInstances != None:
                #     self.replaceUnhealthyInstances = data.ReplaceUnhealthyInstances
                # if data.InstanceInterruptionBehavior != None:
                #     self.instanceInterruptionBehavior = (
                #         data.InstanceInterruptionBehavior
                #     )
                # if data.LoadBalancersConfig != None:
                #     self.loadBalancersConfig = data.LoadBalancersConfig
                # if data.InstancePoolsToUseCount != None:
                #     self.instancePoolsToUseCount = data.InstancePoolsToUseCount
                # if data.TagSpecifications != None:
                #     self.tagSpecifications = data.TagSpecifications

            elif isinstance(aws_config, RequestSpotFleetResponse):
                self.state = self.UP
                self.spotFleetRequestId = aws_config.SpotFleetRequestId

            elif isinstance(aws_config, ModifySpotFleetRequest):
                # if aws_config.ExcessCapacityTerminationPolicy != None:
                #     self.excessCapacityTerminationPolicy = (
                #         aws_config.ExcessCapacityTerminationPolicy
                #     )
                # if aws_config.LaunchTemplateConfigs != None:
                #     self.launchTemplateConfigs = aws_config.LaunchTemplateConfigs
                # if aws_config.TargetCapacity != None:
                #     self.targetCapacity = aws_config.TargetCapacity
                # if aws_config.OnDemandTargetCapacity != None:
                #     self.onDemandTargetCapacity = aws_config.OnDemandTargetCapacity
                pass

            elif isinstance(aws_config, ModifySpotFleetRequestResponse):
                pass

            else:
                assert False, "Unknown type to save deploy state"

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
                modify_spot_fleet_request = ModifySpotFleetRequest(
                    ExcessCapacityTerminationPolicy=None,
                    # LaunchTemplateConfigs=None,
                    SpotFleetRequestId=self.spotFleetRequestId,
                    TargetCapacity=None,
                    OnDemandTargetCapacity=None,
                )

                self.log(
                    "modifying spot fleet request `{}`... ".format(
                        self.spotFleetRequestId
                    )
                )
                try:
                    self.get_client().modify_spot_fleet_request(
                        **dataclasses.asdict(modify_spot_fleet_request)
                    )
                except botocore.exceptions.ClientError as error:
                    raise error

                self.save_deploy_state(modify_spot_fleet_request)

        if self.state == self.MISSING:
            request_spot_fleet = ec2types.RequestSpotFleetRequestRequestTypeDef(
                # SpotFleetRequestConfig=aws.SpotFleetRequestConfigData(
                SpotFleetRequestConfig=ec2types.SpotFleetRequestConfigDataTypeDef(
                    # AllocationStrategy=None,
                    # OnDemandAllocationStrategy=None,
                    # SpotMaintenanceStrategies=None,
                    # ClientToken=None,
                    # ExcessCapacityTerminationPolicy=None,
                    # FulfilledCapacity=None,
                    # OnDemandFulfilledCapacity=None,
                    IamFleetRole=defn.config.iamFleetRole,
                    # LaunchSpecifications=None,
                    # LaunchTemplateConfigs=None,
                    # SpotPrice=None,
                    TargetCapacity=0,
                    # OnDemandTargetCapacity=None,
                    # OnDemandMaxTotalPrice=None,
                    # SpotMaxTotalPrice=None,
                    # TerminateInstancesWithExpiration=None,
                    Type=defn.config.type,
                    # ValidFrom=None,
                    # ValidUntil=None,
                    # ReplaceUnhealthyInstances=None,
                    # InstanceInterruptionBehavior=None,
                    # LoadBalancersConfig=None,
                    # InstancePoolsToUseCount=None,
                    # TagSpecifications=None,
                ),
            )

            self.log(
                "creating spot fleet request with target capacity of ‘{0}’...".format(
                    # self.targetCapacity
                    0
                )
            )
            self._request_spot_fleet(request_spot_fleet)

    def check(self):
        if self.spotFleetRequestId is None:
            self.state = self.MISSING
            return

        self._describe_spot_fleet_requests(
            DescribeSpotFleetRequests(
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
                CancelSpotFleetRequests(
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

    # Boto3 wrappers

    def _describe_spot_fleet_requests(
        self, request: DescribeSpotFleetRequests
    ) -> Optional[DescribeSpotFleetRequestsResponse]:
        try:
            response = DescribeSpotFleetRequestsResponse(
                **self.get_client().describe_spot_fleet_requests(
                    **dataclasses.asdict(request)
                )
            )
            return response
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.state = self.MISSING
                return None
            else:
                raise e

    def _request_spot_fleet(
        self, request: ec2types.RequestSpotFleetRequestRequestTypeDef
    ):
        response = RequestSpotFleetResponse(
            **self.get_client().request_spot_fleet(**dataclasses.asdict(request))
        )
        self.save_deploy_state(request)
        self.save_deploy_state(response)
        return response

    def _modify_spot_fleet_request(
        self, request: ModifySpotFleetRequest
    ) -> Optional[ModifySpotFleetRequestResponse]:
        try:
            response = ModifySpotFleetRequestResponse(
                self.get_client().modify_spot_fleet_request(
                    **dataclasses.asdict(request)
                )
            )
            self.save_deploy_state(request)
            self.save_deploy_state(response)
            return response
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.state = self.MISSING
                return None
            else:
                raise e

    def _cancel_spot_fleet_requests(
        self, request: CancelSpotFleetRequests
    ) -> CancelSpotFleetRequestsResponse:
        return CancelSpotFleetRequestsResponse(
            **self.get_client().cancel_spot_fleet_requests(
                **dataclasses.asdict(request)
            )
        )
        # response['SuccessfulFleetRequests]
        # ['CurrentSpotFleetRequestState']
        # "cancelled_running", "cancelled_terminating",
        # ['PreviousSpotFleetRequestState']
        # ['SpotFleetRequestId']

        # response['UnsuccessfulFleetRequests]
        # ['Error']
        # ['SpotFleetRequestId']
