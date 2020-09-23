{ config, lib, uuid, name, ... }:

with import ./lib.nix lib;
with lib;
with import ./lib.nix lib;

{

  options = {

    name = mkOption {
      default = "nixops-${uuid}-${name}";
      type = types.str;
      description = "Name of the RDS subnet group.";
    };

    description = mkOption {
      default = "NixOps-provisioned subnet group ${name}";
      type = types.str;
      description = "Informational description of the subnet group.";
    };

    accessKeyId = mkOption {
      default = "";
      type = types.str;
      description = "The AWS Access Key ID.";
    };

    region = mkOption {
      example = "us-east-1";
      type = types.str;
      description = ''
        AWS region in which the instance is to be deployed.
      '';
    };

    subnetIds = mkOption {
      default = [];
      example = [ "subnet-00000000" ];
      type = types.listOf (types.either types.str (resource "vpc-subnet"));
      apply = map (x: if builtins.isString x then x else "res-" + x._name + "." + x._type);
      description = ''
        The subnets inside a VPC to launch the databases in.
      '';
    };
  };

  config._type = "rds-subnet-group";
}
