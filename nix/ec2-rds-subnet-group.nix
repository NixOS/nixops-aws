{ config, lib, uuid, name, ... }:

with lib;
with import ./lib.nix lib;

{
  options = {
    name = mkOption {
      default = "nixops-${uuid}-${name}";
      type = types.str;
      description = ''
        Name of the RDS DB subnet group.
      '';
    };

    description = mkOption {
      type = types.str;
      description = ''
        Description of the RDS DB subnet group.
      ''; 
    };

    region = mkOption {
      type = types.str;
      description = "Amazon RDS DB subnet group region.";
    };

    accessKeyId = mkOption {
      default = "";
      type = types.str;
      description = "The AWS Access Key ID.";
    };

    subnetIds = mkOption {
      default = [];
      type = types.listOf (types.either types.str (resource "vpc-subnet"));
      apply = map (x: if builtins.isString x then x else "res-" + x._name + "." + x._type + ".subnetId");
      description = "List of VPC subnets to use for this DB subnet group (must contain at least a subnet for each AZ), it can be a VPC Subnet resource or a string representing the ID of the VPC Subnet.";
    };
    
  };

  config._type = "ec2-rds-db-subnet-group";
}
