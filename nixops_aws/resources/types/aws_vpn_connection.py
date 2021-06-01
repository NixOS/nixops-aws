from nixops.resources import ResourceOptions
from typing import Mapping


class AwsVpnConnectionOptions(ResourceOptions):
    accessKeyId: str
    customerGatewayId: str
    name: str
    region: str
    staticRoutesOnly: bool
    tags: Mapping[str, str]
    vpnGatewayId: str
