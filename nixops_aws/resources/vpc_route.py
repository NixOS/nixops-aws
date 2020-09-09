# -*- coding: utf-8 -*-

# Automatic provisioning of AWS VPC route.

import botocore

import nixops.util
import nixops.resources
from nixops_aws.resources.ec2_common import EC2CommonState
from nixops.diff import Handler
from nixops.state import StateDict
from . import vpc_route_table, vpc_internet_gateway, vpc_nat_gateway
from .vpc_route_table import VPCRouteTableState
from typing import Any

from .types.vpc_route import VpcRouteOptions


class VPCRouteDefinition(nixops.resources.ResourceDefinition):
    """Definition of a VPC route"""

    config: VpcRouteOptions

    @classmethod
    def get_type(cls):
        return "vpc-route"

    @classmethod
    def get_resource_type(cls):
        return "vpcRoutes"

    def show_type(self):
        return "{0}".format(self.get_type())


class VPCRouteState(nixops.resources.DiffEngineResourceState, EC2CommonState):
    """State of a VPC route"""

    definition_type = VPCRouteDefinition

    state = nixops.util.attr_property(
        "state", nixops.resources.DiffEngineResourceState.MISSING, int
    )
    access_key_id = nixops.util.attr_property("accessKeyId", None)
    _reserved_keys = EC2CommonState.COMMON_EC2_RESERVED
    TARGETS = [
        "egressOnlyInternetGatewayId",
        "gatewayId",
        "instanceId",
        "natGatewayId",
        "networkInterfaceId",
    ]

    @classmethod
    def get_type(cls):
        return "vpc-route"

    def __init__(self, depl, name, id):
        nixops.resources.DiffEngineResourceState.__init__(self, depl, name, id)
        self._state = StateDict(depl, id)
        self.region = self._state.get("region", None)
        keys = [
            "region",
            "routeTableId",
            "destinationCidrBlock",
            "destinationIpv6CidrBlock",
            "egressOnlyInternetGatewayId",
            "gatewayId",
            "instanceId",
            "natGatewayId",
            "networkInterfaceId",
        ]
        self.handle_create_route = Handler(keys, handle=self.realize_create_route)

    def show_type(self):
        s = super(VPCRouteState, self).show_type()
        if self.region:
            s = "{0} [{1}]".format(s, self.region)
        return s

    @property
    def resource_id(self):
        return self._state.get("destinationCidrBlock", None) or self._state.get(
            "destinationIpv6CidrBlock", None
        )

    def prefix_definition(self, attr):
        return {("resources", "vpcRoutes"): attr}

    def get_definition_prefix(self):
        return "resources.vpcRoutes."

    def create_after(self, resources, defn):
        return {
            r
            for r in resources
            if isinstance(r, vpc_route_table.VPCRouteTableState)
            or isinstance(r, vpc_internet_gateway.VPCInternetGatewayState)
            or isinstance(r, vpc_nat_gateway.VPCNatGatewayState)
        }

    def realize_create_route(self, allow_recreate):
        config: VPCRouteDefinition = self.get_defn()

        if self.state == self.UP:
            if not allow_recreate:
                raise Exception(
                    "route {} definition changed and it needs to be recreated"
                    " use --allow-recreate if you want to create a new one".format(
                        self.name
                    )
                )
            self.warn("route definition changed, recreating ...")
            self._destroy()

        self._state["region"] = config.config.region

        rtb_id = config.config.routeTableId
        if rtb_id.startswith("res-"):
            res = self.depl.get_typed_resource(
                rtb_id[4:].split(".")[0], "vpc-route-table", VPCRouteTableState
            )
            rtb_id = res._state["routeTableId"]

        route = dict()

        num_targets = 0
        for item in self.TARGETS:
            if getattr(config.config, item, None):
                num_targets += 1
                target = item

        if num_targets > 1:
            raise Exception(
                "you should specify only 1 target from {}".format(str(self.TARGETS))
            )

        if (config.config.destinationCidrBlock is not None) and (
            config.config.destinationIpv6CidrBlock is not None
        ):
            raise Exception(
                "you can't set both destinationCidrBlock and destinationIpv6CidrBlock in one route"
            )

        if config.config.destinationCidrBlock is not None:
            destination = "destinationCidrBlock"
        if config.config.destinationIpv6CidrBlock is not None:
            destination = "destinationIpv6CidrBlock"

        def retrieve_defn(option):
            cfg = getattr(config.config, option)
            if cfg.startswith("res-"):
                name = cfg[4:].split(".")[0]
                res_type = cfg.split(".")[1]
                attr = cfg.split(".")[2] if len(cfg.split(".")) > 2 else option
                # TODO: Type this how?
                res: Any = self.depl.get_generic_resource(name, res_type)  # type: ignore
                return res._state[attr]
            else:
                return cfg

        route["RouteTableId"] = rtb_id
        route[self.upper(target)] = retrieve_defn(target)
        route[self.upper(destination)] = getattr(config.config, destination)

        self.log(
            "creating route {0} => {1} in route table {2}".format(
                retrieve_defn(target), getattr(config.config, destination), rtb_id
            )
        )
        self.get_client().create_route(**route)

        with self.depl._db:
            self.state = self.UP
            self._state[target] = route[self.upper(target)]
            self._state[destination] = getattr(config.config, destination)
            self._state["routeTableId"] = rtb_id

    def upper(self, option):
        return "%s%s" % (option[0].upper(), option[1:])

    def _destroy(self):
        if self.state != self.UP:
            return
        destination = (
            "destinationCidrBlock"
            if ("destinationCidrBlock" in self._state.keys())
            else "destinationIpv6CidrBlock"
        )
        self.log(
            "deleting route to {0} from route table {1}".format(
                self._state[destination], self._state["routeTableId"]
            )
        )
        try:
            args = dict()
            args[self.upper(destination)] = self._state[destination]
            args["RouteTableId"] = self._state["routeTableId"]
            self.get_client().delete_route(**args)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "InvalidRoute.NotFound":
                self.warn("route was already deleted")
            else:
                raise error

        with self.depl._db:
            self.state = self.MISSING
            self._state["routeTableId"] = None
            self._state[destination] = None
            for target in self.TARGETS:
                self._state[target] = None

    def destroy(self, wipe=False):
        self._destroy()
        return True
