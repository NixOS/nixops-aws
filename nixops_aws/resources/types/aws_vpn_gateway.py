from nixops.resources import ResourceOptions
from typing import Mapping


class AwsVpnGatewayOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
    tags: Mapping[str, str]
    vpcId: str
    zone: str
