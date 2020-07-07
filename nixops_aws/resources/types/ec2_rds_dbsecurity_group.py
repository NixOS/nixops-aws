from typing import Sequence
from nixops.resources import ResourceOptions
from typing import Optional


class RulesOptions(ResourceOptions):
    cidrIp: Optional[str]
    securityGroupId: Optional[str]
    securityGroupName: Optional[str]
    securityGroupOwnerId: Optional[str]


class Ec2RdsDbsecurityGroupOptions(ResourceOptions):
    accessKeyId: str
    description: str
    groupName: str
    region: str
    rules: Sequence[RulesOptions]
