from typing import Optional
from typing import Mapping
from nixops.resources import ResourceOptions


class VpcSubnetOptions(ResourceOptions):
    accessKeyId: str
    cidrBlock: str
    ipv6CidrBlock: Optional[str]
    mapPublicIpOnLaunch: bool
    name: str
    region: str
    subnetId: str
    tags: Mapping[str, str]
    vpcId: str
    zone: str
