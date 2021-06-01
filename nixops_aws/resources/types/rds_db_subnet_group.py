from typing import Sequence
from nixops.resources import ResourceOptions


class RDSDbSubnetGroupOptions(ResourceOptions):
    accessKeyId: str
    description: str
    name: str
    region: str
    subnetIds: Sequence[str]
