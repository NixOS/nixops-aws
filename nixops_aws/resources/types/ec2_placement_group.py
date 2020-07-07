from nixops.resources import ResourceOptions


class Ec2PlacementGroupOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
    strategy: str
