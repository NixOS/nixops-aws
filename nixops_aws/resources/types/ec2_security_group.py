from nixops.resources import ResourceOptions
from typing import Optional
from typing import Sequence


class SourcegroupOptions(ResourceOptions):
    groupName: Optional[str]
    ownerId: Optional[str]


class RulesOptions(ResourceOptions):
    codeNumber: Optional[int]
    fromPort: Optional[int]
    protocol: str
    sourceGroup: SourcegroupOptions
    sourceIp: Optional[str]
    toPort: Optional[int]
    typeNumber: Optional[int]


class Ec2SecurityGroupOptions(ResourceOptions):
    accessKeyId: str
    description: str
    groupId: Optional[str]
    name: str
    region: str
    rules: Sequence[RulesOptions]
    vpcId: Optional[str]
