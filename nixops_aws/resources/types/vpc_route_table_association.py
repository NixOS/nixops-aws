from nixops.resources import ResourceOptions


class VpcRouteTableAssociationOptions(ResourceOptions):
    accessKeyId: str
    name: str
    region: str
    routeTableId: str
    subnetId: str
