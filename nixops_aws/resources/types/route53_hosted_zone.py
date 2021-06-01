from nixops.resources import ResourceOptions
from typing import Sequence


class AssociatedvpcsOptions(ResourceOptions):
    region: str
    vpcId: str


class Route53HostedZoneOptions(ResourceOptions):
    accessKeyId: str
    associatedVPCs: Sequence[AssociatedvpcsOptions]
    comment: str
    name: str
    privateZone: bool
