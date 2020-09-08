from nixops.resources import ResourceOptions
from typing import Sequence


class Ec2RdsDbinstanceOptions(ResourceOptions):
    accessKeyId: str
    allocatedStorage: int
    dbName: str
    endpoint: str
    engine: str
    id: str
    instanceClass: str
    masterPassword: str
    masterUsername: str
    multiAZ: bool
    port: int
    region: str
    securityGroups: Sequence[str]
    vpcSecurityGroups: Sequence[str]
