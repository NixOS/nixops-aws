from nixops.resources import ResourceOptions
from typing import Optional


class CloudwatchLogGroupOptions(ResourceOptions):
    accessKeyId: str
    arn: str
    name: str
    region: str
    retentionInDays: Optional[int]
