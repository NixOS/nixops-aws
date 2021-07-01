from typing import Union
from nixops.resources import ResourceOptions
from typing import Mapping
from typing import Optional
from typing_extensions import Literal


class EbsVolumeOptions(ResourceOptions):
    accessKeyId: Optional[str]
    iops: Optional[int]
    region: str
    size: int
    snapshot: str
    tags: Mapping[str, str]
    volumeId: Optional[str]
    volumeType: Union[
        Literal["standard"],
        Literal["io1"],
        Literal["io2"],
        Literal["gp2"],
        Literal["st1"],
        Literal["sc1"],
    ]
    zone: str
