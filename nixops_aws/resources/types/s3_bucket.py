from typing_extensions import Literal
from nixops.resources import ResourceOptions
from typing import Union


class WebsiteOptions(ResourceOptions):
    enabled: bool
    errorDocument: str
    suffix: str


class S3BucketOptions(ResourceOptions):
    accessKeyId: str
    arn: str
    lifeCycle: str
    name: str
    persistOnDestroy: bool
    policy: str
    region: str
    versioning: Union[Literal["Suspended"], Literal["Enabled"]]
    website: WebsiteOptions
