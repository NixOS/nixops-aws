from typing_extensions import Literal
from typing import Optional
from nixops.resources import ResourceOptions
from typing import Union
from typing import Sequence


class AlarmidentifierOptions(ResourceOptions):
    name: str
    region: str


class Route53HealthCheckOptions(ResourceOptions):
    accessKeyId: str
    alarmIdentifier: AlarmidentifierOptions
    childHealthChecks: Sequence[str]
    enableSNI: bool
    failureThreshold: int
    fullyQualifiedDomainName: str
    healthThreshold: int
    insufficientDataHealthStatus: Optional[
        Union[Literal["Healthy"], Literal["Unhealthy"], Literal["LastKnownStatus"]]
    ]
    inverted: bool
    ipAddress: Optional[str]
    measureLatency: bool
    name: str
    port: Optional[int]
    regions: Sequence[str]
    requestInterval: Union[Literal["10"], Literal["30"]]
    resourcePath: str
    searchString: str
    type: Union[
        Literal["HTTP"],
        Literal["HTTPS"],
        Literal["HTTP_STR_MATCH"],
        Literal["HTTPS_STR_MATCH"],
        Literal["TCP"],
        Literal["CALCULATED"],
        Literal["CLOUDWATCH_METRIC"],
    ]
