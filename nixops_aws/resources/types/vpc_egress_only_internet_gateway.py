from nixops.resources import ResourceOptions


class VpcEgressOnlyInternetGatewayOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
    vpcId: str
