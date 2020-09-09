from typing import Sequence
from nixops.resources import ResourceOptions
from typing import Optional


class SubscriptionsOptions(ResourceOptions):
    endpoint: str
    protocol: str


class SnsTopicOptions(ResourceOptions):
    accessKeyId: Optional[str]
    arn: str
    displayName: Optional[str]
    name: str
    policy: str
    region: str
    subscriptions: Sequence[SubscriptionsOptions]
