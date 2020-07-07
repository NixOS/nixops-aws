from nixops.resources import ResourceOptions


class VpcNatGatewayOptions(ResourceOptions):
    accessKeyId: str
    allocationId: str
    name: str
    region: str
    subnetId: str
