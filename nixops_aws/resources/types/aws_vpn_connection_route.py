from nixops.resources import ResourceOptions
from typing import Optional


class AwsVpnConnectionRouteOptions(ResourceOptions):
    accessKeyId: str
    destinationCidrBlock: Optional[str]
    name: str
    region: str
    vpnConnectionId: str
