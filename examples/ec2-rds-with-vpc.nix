let
  region = "us-east-1";
  accessKeyId = "AKIA...";
in
{
  network.description = "NixOps RDS in a VPC Testing";
  # A VPC.
  resources.vpc.private = {
    inherit region accessKeyId;
    enableDnsSupport = true;
    enableDnsHostnames = true;
    cidrBlock = "10.0.0.0/16";
  };

  # 2 VPC at least.
  resources.vpcSubnets = {
    db-a = { resources, ... }: {
      inherit region accessKeyId;
      vpcId=resources.vpc.private;
      cidrBlock="10.0.0.0/19";
      zone="us-east-1a";
    };
    db-b = { resources, ... }: {
      inherit region accessKeyId;
      vpcId=resources.vpc.private;
      zone="us-east-1c";
      cidrBlock="10.0.32.0/19";
    };
  };


  resources.ec2SecurityGroups = {
    database = { resources, lib, ... }:
    {
      inherit region accessKeyId;
      vpcId = resources.vpc.private;
      rules = [
        {
          sourceIp = "10.0.0.0/16";
          fromPort = 5432;
          toPort = 5432;
        }
      ];
    };
  };

  resources.rdsDbSubnetGroups.db-subnet = {resources, ...}: {
    inherit region accessKeyId;
    description = "RDS test subnet";
    subnetIds = (map (key: resources.vpcSubnets.${"db-" + key}) ["a" "b"]);
  };

  resources.rdsDbInstances.test-rds-instance = { resources, ... }: {
    inherit region accessKeyId;
    id = "test-multi-az";
    instanceClass = "db.r3.large";
    allocatedStorage = 30;
    masterUsername = "administrator";
    masterPassword = "testing123";
    port = 5432;
    engine = "postgres";
    dbName = "testNixOps";
    multiAZ = true;
    vpcSecurityGroupIds = [ resources.ec2SecurityGroups.database ];
    dbSubnetGroup = resources.rdsDbSubnetGroups.db-subnet.name;
  };
}
