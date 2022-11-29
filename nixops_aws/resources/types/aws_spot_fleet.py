from typing import Mapping, Sequence, Optional, Union
from typing_extensions import Literal
from nixops.resources import ResourceOptions


class LaunchTemplateSpecificationOptions(ResourceOptions):
    # launchTemplateId: str # Optional
    launchTemplateName: str  # Optional
    version: str  # Optional


class FleetLaunchTemplateSpecificationOptions(ResourceOptions):
    # launchTemplateId: str # Optional
    launchTemplateName: str  # Optional #  {"max":128,"min":3,"pattern":"[a-zA-Z0-9\\(\\)\\.\\-/_]+"}
    version: str  # Optional


class LaunchTemplateOverridesOptions(ResourceOptions):
    instanceType: Optional[str]
    spotPrice: Optional[str]
    subnetId: Optional[str]
    availabilityZone: Optional[str]
    weightedCapacity: Optional[float]
    priority: Optional[float]


class LaunchTemplateConfigOptions(ResourceOptions):
    launchTemplateSpecification: FleetLaunchTemplateSpecificationOptions  # Optional
    overrides: Sequence[LaunchTemplateOverridesOptions]


class SpotFleetRequestOptions(ResourceOptions):
    spotFleetRequestId: str
    iamFleetRole: str
    type: Union[
        Literal["request"],
        Literal["maintain"]
        # Literal["instant"] # instant is listed but is not used by Spot Fleet.
    ]
    launchTemplateConfigs: Sequence[LaunchTemplateConfigOptions]
    spotPrice: Optional[str]
    spotMaxTotalPrice: Optional[str]

    # Common EC2 auth options
    accessKeyId: str
    region: str

    # Common EC2 options
    tags: Mapping[str, str]
