from typing import Mapping, Optional
from nixops.resources import ResourceOptions


class ElasticFileSystemOptions(ResourceOptions):
    accessKeyId: Optional[str]
    region: str
    tags: Mapping[str, str]
