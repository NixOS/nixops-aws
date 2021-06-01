from typing import Union
from nixops.resources import ResourceOptions
from typing_extensions import Literal
from typing import Sequence


class DimensionsOptions(ResourceOptions):
    Name: str
    Value: str


class CloudwatchMetricAlarmOptions(ResourceOptions):
    accessKeyId: str
    alarmActions: Sequence[str]
    comparisonOperator: Union[
        Literal["GreaterThanOrEqualToThreshold"],
        Literal["GreaterThanThreshold"],
        Literal["LessThanThreshold"],
        Literal["LessThanOrEqualToThreshold"],
    ]
    datapointsToAlarm: int
    dimensions: Sequence[DimensionsOptions]
    evaluationPeriods: int
    insufficientDataActions: Sequence[str]
    metricName: str
    name: str
    namespace: str
    okActions: Sequence[str]
    period: int
    region: str
    statistic: Union[
        Literal["SampleCount"],
        Literal["Average"],
        Literal["Sum"],
        Literal["Minimum"],
        Literal["Maximum"],
    ]
    threshold: int
    treatMissingData: Union[
        Literal["breaching"],
        Literal["notBreaching"],
        Literal["ignore"],
        Literal["missing"],
    ]
    unit: Union[
        Literal["Seconds"],
        Literal["Microseconds"],
        Literal["Milliseconds"],
        Literal["Bytes"],
        Literal["Kilobytes"],
        Literal["Megabytes"],
        Literal["Gigabytes"],
        Literal["Terabytes"],
        Literal["Bits"],
        Literal["Kilobits"],
        Literal["Megabits"],
        Literal["Gigabits"],
        Literal["Terabits"],
        Literal["Percent"],
        Literal["Count"],
        Literal["Bytes/Second"],
        Literal["Kilobytes/Second"],
        Literal["Megabytes/Second"],
        Literal["Gigabytes/Second"],
        Literal["Terabytes/Second"],
        Literal["Bits/Second"],
        Literal["Kilobits/Second"],
        Literal["Megabits/Second"],
        Literal["Gigabits/Second"],
        Literal["Terabits/Second"],
        Literal["Count/Second"],
        Literal["None"],
    ]
