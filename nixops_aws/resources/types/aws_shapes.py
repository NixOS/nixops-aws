from typing import Union
from typing import Optional
from typing import List
from typing import Any
from typing_extensions import Literal
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from .aws_ids import SubnetId  # noqa: F401
from .aws_ids import SpotFleetRequestId  # noqa: F401

# AWS unused shapes


LaunchTemplateConfig = Any
LoadBalancersConfig = Any
TagSpecification = Any
GroupIdentifier = Any
BlockDeviceMapping = Any
IamInstanceProfileSpecification = Any
ImageId = Any
InstanceType = Any
KeyPairName = Any
SpotFleetMonitoring = Any
InstanceNetworkInterfaceSpecification = Any
SpotPlacement = Any
SpotFleetTagSpecification = Any
Tag = Any

# Shapes


@dataclass
class SpotFleetLaunchSpecification:
    SecurityGroups: Optional[List[GroupIdentifier]] = field(default=None)
    AddressingType: Optional[str] = field(default=None)
    BlockDeviceMappings: Optional[List[BlockDeviceMapping]] = field(default=None)
    EbsOptimized: Optional[bool] = field(default=None)
    IamInstanceProfile: Optional[IamInstanceProfileSpecification] = field(default=None)
    ImageId: Optional[ImageId] = field(default=None)
    InstanceType: Optional[InstanceType] = field(default=None)
    KernelId: Optional[str] = field(default=None)
    KeyName: Optional[KeyPairName] = field(default=None)
    Monitoring: Optional[SpotFleetMonitoring] = field(default=None)
    NetworkInterfaces: Optional[List[InstanceNetworkInterfaceSpecification]] = field(
        default=None
    )
    Placement: Optional[SpotPlacement] = field(default=None)
    RamdiskId: Optional[str] = field(default=None)
    SpotPrice: Optional[str] = field(default=None)
    SubnetId: Optional[SubnetId] = field(default=None)  # noqa: F811
    UserData: Optional[str] = field(default=None)
    WeightedCapacity: Optional[float] = field(default=None)
    TagSpecifications: Optional[SpotFleetTagSpecification] = field(default=None)


@dataclass
class SpotFleetRequestConfigData:
    IamFleetRole: str
    TargetCapacity: int
    AllocationStrategy: Optional[
        Union[
            Literal["lowestPrice"],
            Literal["diversified"],
            Literal["capacityOptimized"],
            Literal["capacityOptimizedPrioritized"],
        ]
    ] = field(default=None)
    OnDemandAllocationStrategy: Optional[
        Union[Literal["lowestPrice"], Literal["prioritized"]]
    ] = field(default=None)
    SpotMaintenanceStrategies: Optional[SpotMaintenanceStrategies] = field(default=None)
    ClientToken: Optional[str] = field(default=None)
    ExcessCapacityTerminationPolicy: Optional[
        Union[Literal["noTermination"], Literal["default"]]
    ] = field(default=None)
    FulfilledCapacity: Optional[float] = field(default=None)
    OnDemandFulfilledCapacity: Optional[float] = field(default=None)
    LaunchSpecifications: Optional[List[SpotFleetLaunchSpecification]] = field(
        default=None
    )
    LaunchTemplateConfigs: Optional[List[LaunchTemplateConfig]] = field(default=None)
    SpotPrice: Optional[str] = field(default=None)
    OnDemandTargetCapacity: Optional[int] = field(default=None)
    OnDemandMaxTotalPrice: Optional[str] = field(default=None)
    SpotMaxTotalPrice: Optional[str] = field(default=None)
    TerminateInstancesWithExpiration: Optional[bool] = field(default=None)
    Type: Optional[
        Union[Literal["request"], Literal["maintain"], Literal["instant"]]
    ] = field(default=None)
    ValidFrom: Optional[datetime] = field(default=None)
    ValidUntil: Optional[datetime] = field(default=None)
    ReplaceUnhealthyInstances: Optional[bool] = field(default=None)
    InstanceInterruptionBehavior: Optional[
        Union[Literal["hibernate"], Literal["stop"], Literal["terminate"]]
    ] = field(default=None)
    LoadBalancersConfig: Optional[LoadBalancersConfig] = field(default=None)
    InstancePoolsToUseCount: Optional[int] = field(default=None)
    Context: Optional[str] = field(default=None)  # Reserved
    TagSpecifications: Optional[List[TagSpecification]] = field(default=None)


@dataclass
class SpotFleetRequestConfig:
    ActivityStatus: Optional[
        Union[
            Literal["error"],
            Literal["pending_fulfillment"],
            Literal["pending_termination"],
            Literal["fulfilled"],
        ]
    ] = field(default=None)
    # CreateTime: Optional[Timestamp], = field(default=None)
    SpotFleetRequestConfig: Optional[SpotFleetRequestConfigData] = field(default=None)
    SpotFleetRequestId: Optional[SpotFleetRequestId] = field(default=None)  # noqa: F811
    SpotFleetRequestState: Optional[
        Union[
            Literal["submitted"],
            Literal["active"],
            Literal["cancelled"],
            Literal["failed"],
            Literal["cancelled_running"],
            Literal["cancelled_terminating"],
            Literal["modifying"],
        ]
    ] = field(default=None)
    Tags: Optional[List[Tag]] = field(default=None)
    # TagList = {"type":"list","member":{"shape":"Tag","locationName":"item"}}


@dataclass
class SpotCapacityRebalance:
    ReplacementStrategy: Optional[Union[Literal["launch"]]] = field(default=None)


@dataclass
class SpotMaintenanceStrategies:
    CapacityRebalance: Optional[SpotCapacityRebalance] = field(default=None)


# class GroupIdentifier:
#     GroupName: Optional[str] = field(default=None)
#     GroupId: Optional[str] = field(default=None)

# class LaunchTemplateConfig:
#     LaunchTemplateSpecification: Optional[FleetLaunchTemplateSpecification] = field(default=None)
#     Overrides: Optional[List[LaunchTemplateOverrides]] = field(default=None)

# class FleetLaunchTemplateSpecification:
#     LaunchTemplateId: Optional[str] = field(default=None)
#     LaunchTemplateName: Optional[str] = field(default=None)
#     Version: Optional[str] = field(default=None)

# class LaunchTemplateOverrides:
#     InstanceType: Optional[InstanceType] = field(default=None)
#     SpotPrice: Optional[str] = field(default=None)
#     SubnetId: Optional[str] = field(default=None)
#     AvailabilityZone: Optional[str] = field(default=None)
#     WeightedCapacity: Optional[float] = field(default=None)
#     Priority: Optional[float] = field(default=None)

# class LaunchTemplateSpecification:
#     LaunchTemplateId: Optional[LaunchTemplateId] = field(default=None)
#     LaunchTemplateName: Optional[str] = field(default=None)
#     Version: Optional[str] = field(default=None)

# class LoadBalancersConfig:
#     ClassicLoadBalancersConfig: Optional[ClassicLoadBalancersConfig] = field(default=None)
#     TargetGroupsConfig: Optional[TargetGroupsConfig] = field(default=None)

# class ClassicLoadBalancersConfig:
#     ClassicLoadBalancers: Optional[List[ClassicLoadBalancer]] = field(default=None)

# class ClassicLoadBalancer:
#     Name: Optional[str] = field(default=None)

# class TargetGroupsConfig:
#     TargetGroups: Optional[TargetGroups] = field(default=None)

# class TargetGroup:
#     arn: Optional[str] = field(default=None)

# class SpotFleetMonitoring:
#     Enabled: Optional[bool] = field(default=None)

# class SpotPlacement:
#     AvailabilityZone: Optional[str] = field(default=None)
#     GroupName: Optional[PlacementGroupName] = field(default=None)
#     Tenancy: Optional[Union[
#         Literal["default"],
#         Literal["dedicated"],
#         Literal["host"]
#     ]] = field(default=None)

# class SpotFleetTagSpecification:
#     ResourceType: Optional[Union[
#         Literal["capacity-reservation"],
#         Literal["client-vpn-endpoint"],
#         Literal["customer-gateway"],
#         Literal["carrier-gateway"],
#         Literal["dedicated-host"],
#         Literal["dhcp-options"],
#         Literal["egress-only-internet-gateway"],
#         Literal["elastic-ip"],
#         Literal["elastic-gpu"],
#         Literal["export-image-task"],
#         Literal["export-instance-task"],
#         Literal["fleet"],
#         Literal["fpga-image"],
#         Literal["host-reservation"],
#         Literal["image"],
#         Literal["import-image-task"],
#         Literal["import-snapshot-task"],
#         Literal["instance"],
#         Literal["instance-event-window"],
#         Literal["internet-gateway"],
#         Literal["ipv4pool-ec2"],
#         Literal["ipv6pool-ec2"],
#         Literal["key-pair"],
#         Literal["launch-template"],
#         Literal["local-gateway"],
#         Literal["local-gateway-route-table"],
#         Literal["local-gateway-virtual-interface"],
#         Literal["local-gateway-virtual-interface-group"],
#         Literal["local-gateway-route-table-vpc-association"],
#         Literal["local-gateway-route-table-virtual-interface-group-association"],
#         Literal["natgateway"],
#         Literal["network-acl"],
#         Literal["network-interface"],
#         Literal["network-insights-analysis"],
#         Literal["network-insights-path"],
#         Literal["placement-group"],
#         Literal["prefix-list"],
#         Literal["replace-root-volume-task"],
#         Literal["reserved-instances"],
#         Literal["route-table"],
#         Literal["security-group"],
#         Literal["security-group-rule"],
#         Literal["snapshot"],
#         Literal["spot-fleet-request"],
#         Literal["spot-instances-request"],
#         Literal["subnet"],
#         Literal["traffic-mirror-filter"],
#         Literal["traffic-mirror-session"],
#         Literal["traffic-mirror-target"],
#         Literal["transit-gateway"],
#         Literal["transit-gateway-attachment"],
#         Literal["transit-gateway-connect-peer"],
#         Literal["transit-gateway-multicast-domain"],
#         Literal["transit-gateway-route-table"],
#         Literal["volume"],
#         Literal["vpc"],
#         Literal["vpc-endpoint"],
#         Literal["vpc-endpoint-service"],
#         Literal["vpc-peering-connection"],
#         Literal["vpn-connection"],
#         Literal["vpn-gateway"],
#         Literal["vpc-flow-log"]
#     ] = field(default=None)
#     Tags: Optional[List[Tag]] = field(default=None)

# class Tag:
#     Key: Optional[str] = field(default=None)
#     Value: Optional[str] = field(default=None)
