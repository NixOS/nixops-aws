from nixops.resources import ResourceOptions


class IamRoleOptions(ResourceOptions):
    accessKeyId: str
    assumeRolePolicy: str
    name: str
    policy: str
