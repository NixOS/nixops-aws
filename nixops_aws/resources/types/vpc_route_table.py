from nixops.resources import ResourceOptions
from typing import Mapping
from typing import Sequence


class VpcRouteTableOptions(ResourceOptions):
    accessKeyId: str
    name: str
    propagatingVgws: Sequence[str]
    region: str
    tags: Mapping[str, str]
    vpcId: str
