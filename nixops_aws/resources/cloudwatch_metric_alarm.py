# -*- coding: utf-8 -*-

# Automatic provisioning of AWS Cloudwatch Metric Alarms.

import os
import botocore
import boto3
import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
from .sns_topic import SNSTopicState
from nixops_aws.backends.ec2 import EC2State

from .types.cloudwatch_metric_alarm import CloudwatchMetricAlarmOptions


class CloudwatchMetricAlarmDefinition(nixops.resources.ResourceDefinition):
    """Definition of an Cloudwatch Metric Alarm."""

    config: CloudwatchMetricAlarmOptions

    @classmethod
    def get_type(cls):
        return "cloudwatch-metric-alarm"

    @classmethod
    def get_resource_type(cls):
        return "cloudwatchMetricAlarms"

    def __init__(self, name: str, config: nixops.resources.ResourceEval):
        nixops.resources.ResourceDefinition.__init__(self, name, config)
        self.access_key_id = self.config.accessKeyId
        self.region = self.config.region
        self.alarm_name = self.config.name
        self.metric_name = self.config.metricName
        self.namespace = self.config.namespace
        self.statistic = self.config.statistic
        self.dimensions = self.config.dimensions
        self.unit = self.config.unit
        self.period = self.config.period
        self.evaluation_periods = self.config.evaluationPeriods
        self.threshold = self.config.threshold
        self.comparison_operator = self.config.comparisonOperator
        self.alarm_actions = self.config.alarmActions
        self.ok_actions = self.config.okActions
        self.insufficient_data_actions = self.config.insufficientDataActions
        self.treat_missing_data = self.config.treatMissingData
        self.datapoints_to_alarm = self.config.datapointsToAlarm


class CloudwatchMetricAlarmState(
    nixops.resources.ResourceState[CloudwatchMetricAlarmDefinition]
):
    """State of a Cloudwatch Metric Alarm."""

    definition_type = CloudwatchMetricAlarmDefinition

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("cloudwatch.accessKeyId", None)
    region = nixops.util.attr_property("cloudwatch.region", None)
    alarm_name = nixops.util.attr_property("cloudwatch.name", None)
    put_config = nixops.util.attr_property("cloudwatch.config", {}, "json")

    @classmethod
    def get_type(cls):
        return "cloudwatch-metric-alarm"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._boto_session = None

    @property
    def resource_id(self):
        return self.alarm_name

    def prefix_definition(self, attr):
        return {("resources", "cloudwatchMetricAlarms"): attr}

    def get_physical_spec(self):
        return {}

    def boto_session(self, region):
        if self._boto_session is None:
            (
                access_key_id,
                secret_access_key,
            ) = nixops_aws.ec2_utils.fetch_aws_secret_key(self.access_key_id)
            self._boto_session = boto3.session.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=self.region,
            )
        return self._boto_session

    def create(self, defn, check, allow_reboot, allow_recreate):
        self.access_key_id = (
            defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
        )

        if not (self.access_key_id or os.environ["AWS_ACCESS_KEY_ID"]):
            raise Exception("please set ‘accessKeyId’ or $AWS_ACCESS_KEY_ID")
        client = self.boto_session(self.region or defn.region).client("cloudwatch")

        if self.alarm_name and self.alarm_name != defn.alarm_name:
            raise Exception("Cannot change name of a CloudWatch Metric Alarm")
        if self.region and self.region != defn.region:
            raise Exception("Cannot change region of a CloudWatch Metric Alarm")

        cfg = {}
        cfg["AlarmName"] = defn.alarm_name
        cfg["Statistic"] = defn.statistic
        cfg["Namespace"] = defn.namespace
        cfg["MetricName"] = defn.metric_name
        cfg["Unit"] = defn.unit
        cfg["Period"] = defn.period
        cfg["EvaluationPeriods"] = defn.evaluation_periods
        cfg["Threshold"] = defn.threshold
        cfg["ComparisonOperator"] = defn.comparison_operator
        cfg["TreatMissingData"] = defn.treat_missing_data
        cfg["DatapointsToAlarm"] = defn.datapoints_to_alarm

        # resolve resources
        def resolve_values(kv):
            if kv["Name"] == "InstanceId":
                v = kv["Value"]
                if v.startswith("machine-"):
                    m = self.depl.get_machine(v[8:], EC2State)
                    if not m.vm_id:
                        raise Exception(
                            "cannot create action that refers to a machine that does not exist yet"
                        )
                    kv["Value"] = m.vm_id
                return kv

            return kv

        cfg["Dimensions"] = [resolve_values(v) for v in defn.dimensions]

        def resolve_action(a):
            if a.startswith("res-"):
                topic = self.depl.get_typed_resource(a[4:], "sns-topic", SNSTopicState)
                if not topic.arn:
                    raise Exception(
                        "cannot create action, as SNS topic {} has not yet been created".format(
                            a[4:]
                        )
                    )
                return topic.arn
            return a

        # resolve sns topics
        cfg["AlarmActions"] = [resolve_action(a) for a in defn.alarm_actions]
        cfg["OKActions"] = [resolve_action(a) for a in defn.ok_actions]
        cfg["InsufficientDataActions"] = [
            resolve_action(a) for a in defn.insufficient_data_actions
        ]

        if self.put_config != cfg or check:
            client.put_metric_alarm(**cfg)
            with self.depl._db:
                self.state = self.UP
                self.region = defn.region
                self.alarm_name = defn.alarm_name
                self.put_config = cfg

        return True

    def destroy(self, wipe=False):
        if not self.alarm_name:
            return True
        client = self.boto_session(self.region).client("cloudwatch")

        self.log("destroying cloudwatch metric alarm {}".format(self.alarm_name))
        try:
            client.delete_alarms(AlarmNames=[self.alarm_name])
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFound":
                pass
            raise

        with self.depl._db:
            self.state = self.MISSING
        return True

    def create_after(self, resources, defn):
        return {
            r
            for r in resources
            if isinstance(r, nixops_aws.resources.sns_topic.SNSTopicState)
            or isinstance(r, nixops.backends.MachineState)
        }
