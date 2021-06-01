from typing import Mapping
from nixops.resources import ResourceOptions
from typing import Sequence
from typing import Optional


class VpcDhcpOptionsOptions(ResourceOptions):
    accessKeyId: str
    domainName: Optional[str]
    domainNameServers: Optional[Sequence[str]]
    name: str
    netbiosNameServers: Optional[Sequence[str]]
    netbiosNodeType: Optional[int]
    ntpServers: Optional[Sequence[str]]
    region: str
    tags: Mapping[str, str]
    vpcId: str
