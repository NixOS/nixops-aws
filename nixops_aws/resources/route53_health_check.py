# -*- coding: utf-8 -*-

# Automatic provisioning of AWS Route53 Health Check.

import os
import botocore
import boto3
import uuid
import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
import copy
from nixops_aws.backends.ec2 import EC2State

# boto3.set_stream_logger(name='botocore')

from .types.route53_health_check import Route53HealthCheckOptions


class Route53HealthCheckDefinition(nixops.resources.ResourceDefinition):
    """Definition of an Route53 Health Check."""

    config: Route53HealthCheckOptions

    @classmethod
    def get_type(cls):
        return "aws-route53-health-check"

    @classmethod
    def get_resource_type(cls):
        return "route53HealthChecks"

    def __init__(self, name: str, config: nixops.resources.ResourceEval):
        nixops.resources.ResourceDefinition.__init__(self, name, config)
        self.access_key_id = self.config.accessKeyId
        self.ip_address = self.config.ipAddress
        self.port = self.config.port
        self.type = self.config.type
        self.resource_path = self.config.resourcePath
        self.fqdn = self.config.fullyQualifiedDomainName
        self.search_string = self.config.searchString
        self.request_interval = self.config.requestInterval
        self.failure_threshold = self.config.failureThreshold
        self.measure_latency = self.config.measureLatency
        self.inverted = self.config.inverted
        self.enable_sni = self.config.enableSNI
        self.regions = self.config.regions
        self.alarm_indentifier_region = self.config.alarmIdentifier.region
        self.alarm_indentifier_name = self.config.alarmIdentifier.name
        self.insufficient_data_health_status = self.config.insufficientDataHealthStatus
        self.child_health_checks = self.config.childHealthChecks
        self.health_threshold = self.config.healthThreshold


class Route53HealthCheckState(
    nixops.resources.ResourceState[Route53HealthCheckDefinition]
):
    """State of a Route53 Health Check."""

    definition_type = Route53HealthCheckDefinition

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("ec2.accessKeyId", None)
    health_check_id = nixops.util.attr_property("route53.healthCheckId", None)
    health_check_config = nixops.util.attr_property(
        "route53.healthCheckConfig", {}, "json"
    )
    child_health_checks = nixops.util.attr_property(
        "route53.childHealthChecks", [], "json"
    )

    @classmethod
    def get_type(cls):
        return "aws-route53-health-check"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._boto_session = None

    @property
    def resource_id(self):
        return self.health_check_id

    def prefix_definition(self, attr):
        return {("resources", "route53HealthChecks"): attr}

    def boto_session(self):
        if self._boto_session is None:
            (
                access_key_id,
                secret_access_key,
            ) = nixops_aws.ec2_utils.fetch_aws_secret_key(self.access_key_id)
            self._boto_session = boto3.session.Session(
                aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key
            )
        return self._boto_session

    def resolve_health_check(self, id):
        if id.startswith("res-"):
            hc = self.depl.get_typed_resource(
                id[4:], "aws-route53-health-check", Route53HealthCheckState
            )
            if not hc.health_check_id:
                raise Exception(
                    "cannot create calculated health check for not-yet children."
                )
            return hc.health_check_id
        else:
            return id

    def build_config(self, defn):
        def resolve_machine_ip(v):
            if v.startswith("res-"):
                m = self.depl.get_machine(v[4:], EC2State)
                if not m.public_ipv4:
                    raise Exception(
                        "cannot create health check for a machine that has not yet been created"
                    )
                return m.public_ipv4
            else:
                return v

        cfg = {"Type": defn.type}
        if defn.ip_address:
            cfg["IPAddress"] = resolve_machine_ip(defn.ip_address)

        if defn.fqdn:
            cfg["FullyQualifiedDomainName"] = defn.fqdn
        if defn.port:
            cfg["Port"] = defn.port
        if defn.resource_path != "":
            cfg["ResourcePath"] = defn.resource_path
        if defn.search_string != "":
            cfg["SearchString"] = defn.search_string
        if defn.regions != []:
            cfg["Regions"] = defn.regions
        if defn.insufficient_data_health_status:
            cfg["insufficientDataHealthStatus"] = defn.insufficient_data_health_status
        if defn.alarm_indentifier_name:
            cfg["AlarmIdentifier"] = {
                "Name": defn.alarm_indentifier_name,
                "Region": defn.alarm_indentifier_region,
            }

        if defn.type == "CALCULATED":
            cfg["ChildHealthChecks"] = [
                self.resolve_health_check(c) for c in defn.child_health_checks
            ]
            cfg["HealthThreshold"] = defn.health_threshold
        else:
            cfg["RequestInterval"] = defn.request_interval
            cfg["FailureThreshold"] = defn.failure_threshold
            cfg["Inverted"] = defn.inverted
            cfg["EnableSNI"] = defn.enable_sni

        return cfg

    def create(self, defn, check, allow_reboot, allow_recreate):
        self.access_key_id = (
            defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
        )
        if not (self.access_key_id or os.environ["AWS_ACCESS_KEY_ID"]):
            raise Exception("please set ‘accessKeyId’ or $AWS_ACCESS_KEY_ID")

        client = self.boto_session().client("route53")

        def cannot_change(desc, sk, d):
            if (
                self.health_check_config
                and sk in self.health_check_config
                and self.health_check_config[sk] != d
            ):
                raise Exception(
                    "{} of health check cannot be changed from {} to {}. Need to destroy before redeploying.".format(
                        desc, self.health_check_config[sk], d
                    )
                )

        cannot_change("type", "Type", defn.type)
        cannot_change("request interval", "RequestInterval", defn.request_interval)

        cfg = self.build_config(defn)
        orig_cfg = copy.deepcopy(cfg)

        if check or self.health_check_config != cfg:
            if not self.health_check_id:
                ref = str(uuid.uuid1())
                self.log("creating health check")
                health_check = client.create_health_check(
                    CallerReference=ref, HealthCheckConfig=cfg
                )
                with self.depl._db:
                    self.state = self.UP
                    self.health_check_id = health_check["HealthCheck"]["Id"]
            else:
                health_check = client.get_health_check(
                    HealthCheckId=self.health_check_id
                )
                version = health_check["HealthCheck"]["HealthCheckVersion"]
                cfg["HealthCheckId"] = self.health_check_id
                cfg["HealthCheckVersion"] = version
                if "Type" in cfg:
                    cfg.pop("Type")
                if "RequestInterval" in cfg:
                    cfg.pop("RequestInterval")
                self.log("updating health check")
                client.update_health_check(**cfg)

            with self.depl._db:
                self.health_check_config = orig_cfg
                self.child_health_checks = defn.child_health_checks

        return True

    def destroy(self, wipe=False):
        client = self.boto_session().client("route53")

        if not self.health_check_id:
            return True

        self.log("destroying health check {}".format(self.health_check_id))
        try:
            client.delete_health_check(HealthCheckId=self.health_check_id)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchHealthCheck":
                pass
            raise

        with self.depl._db:
            self.state = self.MISSING
        return True

    def create_after(self, resources, defn):
        hcs = defn.child_health_checks if defn else self.child_health_checks
        return {
            r
            for r in resources
            if isinstance(r, nixops.backends.MachineState)
            or (
                isinstance(r, Route53HealthCheckState)
                and "res-{}".format(r.name) in hcs
            )
        }
