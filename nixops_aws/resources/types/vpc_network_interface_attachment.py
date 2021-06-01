from nixops.resources import ResourceOptions


class VpcNetworkInterfaceAttachmentOptions(ResourceOptions):
    accessKeyId: str
    deviceIndex: int
    instanceId: str
    name: str
    networkInterfaceId: str
    region: str
