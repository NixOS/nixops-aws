from nixops.resources import ResourceOptions


class Ec2KeypairOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
