from typing import Mapping
from typing import Union
from typing import Optional
from typing_extensions import Literal
from nixops.resources import ResourceOptions


class AwsDataLifecycleManagerOptions(ResourceOptions):
    accessKeyId: Optional[str]
    region: str
    dlmName: str
    policyId: Optional[str]
    description: Optional[str]
    executionRole: str
    resourceTypes: Union[
        Literal["instance"], Literal["volume"],
    ]
    targetTags: Mapping[str, str]
    excludeBootVolume: bool
    copyTags: bool
    tagsToAdd: Mapping[str, str]
    ruleInterval: Union[
        Literal[2],
        Literal[3],
        Literal[4],
        Literal[6],
        Literal[8],
        Literal[12],
        Literal[24],
    ]
    ruleIntervalUnit: Union[
        Literal["hours"],
    ]
    ruleTime: str
    retainRule: int
