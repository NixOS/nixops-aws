from typing import Optional
from typing import Sequence
from typing import Mapping
from nixops.resources import ResourceOptions


class VpcNetworkInterfaceOptions(ResourceOptions):
    accessKeyId: str
    description: str
    name: str
    primaryPrivateIpAddress: Optional[str]
    privateIpAddresses: Sequence[str]
    region: str
    secondaryPrivateIpAddressCount: Optional[int]
    securityGroups: Sequence[str]
    sourceDestCheck: bool
    subnetId: str
    tags: Mapping[str, str]
