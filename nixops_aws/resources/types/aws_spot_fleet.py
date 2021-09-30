from typing import Union
from typing import Optional
from typing import List
from typing import Any
from typing_extensions import Literal
from nixops.resources import ResourceOptions
from dataclasses import dataclass
from dataclasses import field

from .aws_ids import SpotFleetRequestId
from .aws_shapes import SpotFleetRequestConfig
from .aws_shapes import SpotFleetRequestConfigData

import mypy_boto3_ec2


# Nix Options


class SpotFleetRequestOptions(ResourceOptions):
    accessKeyId: Optional[str]
    region: str
    iamFleetRole: str
    type: Union[
        Literal["request"],
        Literal["maintain"]
        # Literal["instant"] # instant is listed but is not used by Spot Fleet.
    ]


# AWS operations


@dataclass
class RequestSpotFleet:
    SpotFleetRequestConfig: SpotFleetRequestConfigData
    DryRun: Optional[bool] = field(default=None)


@dataclass
class RequestSpotFleetResponse:
    SpotFleetRequestId: SpotFleetRequestId


@dataclass
class DescribeSpotFleetRequests:
    DryRun: Optional[bool] = field(default=None)
    MaxResults: Optional[int] = field(default=None)
    NextToken: Optional[str] = field(default=None)
    SpotFleetRequestIds: Optional[List[SpotFleetRequestId]] = field(default=None)


@dataclass
class DescribeSpotFleetRequestsResponse:
    NextToken: str
    SpotFleetRequestConfigs: List[SpotFleetRequestConfig]


@dataclass
class ModifySpotFleetRequest:
    SpotFleetRequestId: SpotFleetRequestId
    ExcessCapacityTerminationPolicy: Optional[
        Union[Literal["noTermination"], Literal["default"]]
    ] = field(default=None)
    # LaunchTemplateConfigs: Optional[List[LaunchTemplateConfig]] = field(default=None)
    TargetCapacity: Optional[int] = field(default=None)
    OnDemandTargetCapacity: Optional[int] = field(default=None)


@dataclass
class ModifySpotFleetRequestResponse:
    Return: bool


@dataclass
class CancelSpotFleetRequests:
    SpotFleetRequestIds: List[SpotFleetRequestId]
    TerminateInstances: bool
    DryRun: Optional[bool] = field(default=None)


@dataclass
class CancelSpotFleetRequestsResponse:
    CancelSpotFleetRequestsSuccessSet = Union[Any]
    CancelSpotFleetRequestsErrorSet = Union[Any]
    SuccessfulFleetRequests: CancelSpotFleetRequestsSuccessSet
    # CancelSpotFleetRequestsSuccessSet = {"type":"list","member":{"shape":"CancelSpotFleetRequestsSuccessItem","locationName":"item"}}
    # {}
    UnsuccessfulFleetRequests: CancelSpotFleetRequestsErrorSet
    # CancelSpotFleetRequestsErrorSet = {"type":"list","member":{"shape":"CancelSpotFleetRequestsErrorItem","locationName":"item"}}
    # {}
