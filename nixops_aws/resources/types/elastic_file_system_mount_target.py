from typing import Mapping
from nixops.resources import ResourceOptions
from typing import Sequence
from typing import Optional


class ElasticFileSystemMountTargetOptions(ResourceOptions):
    accessKeyId: str
    fileSystem: str
    ipAddress: Optional[str]
    region: str
    securityGroups: Sequence[str]
    subnet: str
    tags: Mapping[str, str]
