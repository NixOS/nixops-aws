from nixops.resources import ResourceOptions


class SqsQueueOptions(ResourceOptions):
    accessKeyId: str
    arn: str
    name: str
    region: str
    url: str
    visibilityTimeout: int
