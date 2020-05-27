from nixops.resources import ResourceOptions
from typing import Optional
from typing import Sequence


class VpcEndpointOptions(ResourceOptions):
    accessKeyId: str
    name: str
    policy: Optional[str]
    region: str
    routeTableIds: Sequence[str]
    serviceName: str
    vpcId: str
