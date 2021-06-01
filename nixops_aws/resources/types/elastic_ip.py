from nixops.resources import ResourceOptions


class ElasticIpOptions(ResourceOptions):
    accessKeyId: str
    address: str
    region: str
    vpc: bool
