from nixops.resources import ResourceOptions
from typing import Optional


class VpcRouteOptions(ResourceOptions):
    accessKeyId: str
    destinationCidrBlock: Optional[str]
    destinationIpv6CidrBlock: Optional[str]
    egressOnlyInternetGatewayId: Optional[str]
    gatewayId: Optional[str]
    instanceId: Optional[str]
    name: str
    natGatewayId: Optional[str]
    networkInterfaceId: Optional[str]
    region: str
    routeTableId: str
