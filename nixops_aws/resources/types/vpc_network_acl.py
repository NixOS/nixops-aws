from nixops.resources import ResourceOptions
from typing import Sequence
from typing import Mapping
from typing import Optional


class EntriesOptions(ResourceOptions):
    cidrBlock: Optional[str]
    egress: bool
    fromPort: Optional[int]
    icmpCode: Optional[int]
    icmpType: Optional[int]
    ipv6CidrBlock: Optional[str]
    protocol: str
    ruleAction: str
    ruleNumber: int
    toPort: Optional[int]


class VpcNetworkAclOptions(ResourceOptions):
    accessKeyId: str
    entries: Sequence[EntriesOptions]
    name: str
    networkAclId: str
    region: str
    subnetIds: Sequence[str]
    tags: Mapping[str, str]
    vpcId: str
