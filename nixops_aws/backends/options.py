from nixops.backends import MachineOptions
from typing import Optional
from nixops.resources import ResourceOptions
from typing import Sequence
from typing import Mapping
from typing_extensions import Literal
from typing import Union


class DiskOptions(ResourceOptions):
    size: int
    iops: Optional[int]
    volumeType: Union[
        Literal["standard"],
        Literal["io1"],
        Literal["gp2"],
        Literal["st1"],
        Literal["sc1"],
    ]
    disk: str
    fsType: str
    deleteOnTermination: bool
    encrypt: bool
    encryptionType: Union[
        Literal["luks"], Literal["ebs"],
    ]
    cipher: str
    keySize: int
    passphrase: str


class FilesystemsOptions(DiskOptions):
    pass


class BlockdevicemappingOptions(DiskOptions):
    pass


class Ec2Options(ResourceOptions):
    accessKeyId: str
    ami: str
    associatePublicIpAddress: bool
    blockDeviceMapping: Mapping[str, BlockdevicemappingOptions]
    ebsBoot: bool
    ebsInitialRootDiskSize: int
    ebsOptimized: bool
    elasticIPv4: str
    instanceId: str
    instanceProfile: str
    instanceType: str
    keyPair: str
    physicalProperties: Mapping[str, Union[int, str, bool]]
    placementGroup: str
    privateKey: str
    region: str
    securityGroupIds: Sequence[str]
    securityGroups: Sequence[str]
    sourceDestCheck: bool
    spotInstanceInterruptionBehavior: Union[
        Literal["terminate"], Literal["stop"], Literal["hibernate"]
    ]
    spotInstancePrice: int
    spotInstanceRequestType: Union[Literal["one-time"], Literal["persistent"]]
    spotInstanceTimeout: int
    subnetId: str
    tags: Mapping[str, str]
    tenancy: Union[Literal["default"], Literal["dedicated"], Literal["host"]]
    usePrivateIpAddress: bool
    zone: str
    fileSystems: Optional[Mapping[str, FilesystemsOptions]]


class EC2MachineOptions(MachineOptions):
    ec2: Ec2Options
