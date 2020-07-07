from nixops.resources import ResourceOptions
from typing import Mapping


class VpcInternetGatewayOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
    tags: Mapping[str, str]
    vpcId: str
