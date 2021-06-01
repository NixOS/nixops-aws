from nixops.resources import ResourceOptions
from typing import Mapping


class VpcCustomerGatewayOptions(ResourceOptions):
    accessKeyId: str
    bgpAsn: int
    name: str
    publicIp: str
    region: str
    tags: Mapping[str, str]
    type: str
