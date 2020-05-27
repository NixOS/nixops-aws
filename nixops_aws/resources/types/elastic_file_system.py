from typing import Mapping
from nixops.resources import ResourceOptions


class ElasticFileSystemOptions(ResourceOptions):
    accessKeyId: str
    region: str
    tags: Mapping[str, str]
