from nixops.resources import ResourceOptions
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Literal


class Route53RecordsetOptions(ResourceOptions):
    accessKeyId: str
    domainName: str
    healthCheckId: str
    name: str
    recordType: Union[
        Literal["A"],
        Literal["AAAA"],
        Literal["TXT"],
        Literal["CNAME"],
        Literal["MX"],
        Literal["NAPT"],
        Literal["PTR"],
        Literal["SRV"],
        Literal["SPF"],
    ]
    recordValues: Sequence[str]
    routingPolicy: Union[Literal["simple"], Literal["weighted"], Literal["multivalue"]]
    setIdentifier: str
    ttl: int
    weight: int
    zoneId: Optional[str]
    zoneName: Optional[str]
