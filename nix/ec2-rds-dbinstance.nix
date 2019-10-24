{ config, lib, uuid, name, ... }:

with lib;
with import ./lib.nix lib;

{

  options = {

    id = mkOption {
      type = types.str;
      default = "nixops-${uuid}-${name}";
      description = "Identifier for RDS database instance";
    };

    region = mkOption {
      type = types.str;
      description = "Amazon RDS region.";
    };

    multiAZ = mkOption {
      default = false;
      type = types.bool;
      description = ''
        If True, specifies the DB Instance will be deployed in multiple availability zones.
      '';
    };

    accessKeyId = mkOption {
      default = "";
      type = types.str;
      description = "The AWS Access Key ID.";
    };

    allocatedStorage = mkOption {
      type = types.int;
      description = "Allocated storage in GB";
    };

    instanceClass = mkOption {
      type = types.str;
      example = "db.m3.xlarge";
      description = ''
        RDS instance class. See <link
        xlink:href='http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html' />
        for more information.
      '';
    };

    masterUsername = mkOption {
      type = types.str;
      example = "sa";
      description = "Master username for authentication to database instance.";
    };

    masterPassword = mkOption {
      type = types.str;
      description = "Password for master user.";
    };

    port = mkOption {
      type = types.int;
      description = "Port for database instance connections.";
    };

    engine = mkOption {
      type = types.str;
      description = ''Database engine. See <link
      xlink:href='http://boto.readthedocs.org/en/latest/ref/rds.html#boto.rds.RDSConnection.create_dbinstance'
      for valid engines.'';
    };

    dbName = mkOption {
      type = types.str;
      description = "Optional database name to be created when instance is first created.";
    };

    endpoint = mkOption {
      default = ""; # FIXME: Needs a default until read-only options are supported.
      type = types.str;
      description = "The endpoint address of the database instance.  This is set by NixOps.";
    };

    securityGroups = mkOption {
      default = [ "default" ];
      type = types.listOf (types.either types.str (resource "ec2-rds-security-group"));
      apply = map (x: if builtins.isString x then x else "res-" + x._name);
      description = ''
        List of names of DBSecurityGroup to authorize on this DBInstance, use it if you are not a VPC or are using EC2-Classic.
      '';
    };

    vpcSecurityGroups = mkOption {
      default = null; # default to the default security group of the DB subnet.
      type = types.listOf (types.either type.str (resource "ec2-security-group"));
      description = ''
        List of names of VPCSecurityGroupMembership to authorize on this DBInstance, use this if you are in an VPC and not on EC2-Classic. Not applicable for Amazon Aurora.
        '';
    };

    dbSubnetGroupName = mkOption {
      default = null;
      type = types.either type.str (resource "ec2-rds-subnet-group");
      description = ''
        A name for a DBSubnetGroup, they must contain at least one subnet in each availability zone in the AWS region.
        '';
    };

  };

  config._type = "ec2-rds-dbinstance";

}
