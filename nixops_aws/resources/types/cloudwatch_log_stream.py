from nixops.resources import ResourceOptions


class CloudwatchLogStreamOptions(ResourceOptions):
    accessKeyId: str
    arn: str
    logGroupName: str
    name: str
    region: str
