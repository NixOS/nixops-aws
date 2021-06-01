from typing import Mapping
from nixops.resources import ResourceOptions


class VpcOptions(ResourceOptions):
    accessKeyId: str
    amazonProvidedIpv6CidrBlock: bool
    cidrBlock: str
    enableClassicLink: bool
    enableDnsHostnames: bool
    enableDnsSupport: bool
    instanceTenancy: str
    name: str
    region: str
    tags: Mapping[str, str]
    vpcId: str
