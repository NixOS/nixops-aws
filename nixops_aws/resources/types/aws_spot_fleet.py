from typing import Mapping, Sequence, Any, List, Optional, Union
from typing_extensions import Literal
from nixops.resources import ResourceOptions
from dataclasses import dataclass
from dataclasses import field

from .aws_ids import SpotFleetRequestId



# Nix Options
class LaunchTemplateSpecificationOptions(ResourceOptions):
    # launchTemplateId: str # Optional
    launchTemplateName: str  # Optional
    version: str  # Optional


class FleetLaunchTemplateSpecificationOptions(ResourceOptions):
    # launchTemplateId: str # Optional
    launchTemplateName: str  # Optional #  {"max":128,"min":3,"pattern":"[a-zA-Z0-9\\(\\)\\.\\-/_]+"}
    version: str  # Optional


class LaunchTemplateConfigOptions(ResourceOptions):
    launchTemplateSpecification: FleetLaunchTemplateSpecificationOptions  # Optional
    # overrides: Optional[Sequence[LaunchTemplateOverrides]]

class SpotFleetRequestOptions(ResourceOptions):
    spotFleetRequestId: str
    iamFleetRole: str
    type: Union[
        Literal["request"],
        Literal["maintain"]
        # Literal["instant"] # instant is listed but is not used by Spot Fleet.
    ]
    launchTemplateConfigs: Sequence[LaunchTemplateConfigOptions]

    # Common EC2 auth options
    accessKeyId: str
    region: str

    # Common EC2 options
    tags: Mapping[str, str]


















