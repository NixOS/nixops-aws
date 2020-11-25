{
  region ? "us-east-1"
, accessKeyId ? "AKIA..."
, vpcId ? "vpc-.."
, subnetId1 ? "subnet-.."
, subnetId2 ? "subnet-.."
, ...
}:
{
  network.description = "NixOps RDS Testing";

  resources.ec2SecurityGroups.test-rds-sg =
    {
      inherit region accessKeyId;
      vpcId = vpcId;
      name = "nixops-sg";
      description = "testing vpc sg for rds";
      rules = [
        {
          fromPort = 3306;
          toPort = 3306;
          sourceIp = "0.0.0.0/0";
        }
      ];
    };

  resources.rdsSubnetGroups.test-rds-subnet-group =
    {
      inherit region accessKeyId;
      subnetIds = [ subnetId1 subnetId2 ];
    };

  resources.rdsDbInstances.test-rds-vpc-instance =
    { resources, ... }:
    {
      inherit region accessKeyId;
      id = "test-rds-vpc";
      instanceClass = "db.m3.large";
      snapshot = "test-rds-vpc-final-snapshot-372cd7f1ecbe4bb7a59e3026a15d7535";
      allocatedStorage = 30;
      masterUsername = "administrator";
      masterPassword = "testing123";
      port = 3306;
      engine = "mysql";
      dbName = "testNixOps";
      multiAZ = true;
      subnetGroup = resources.rdsSubnetGroups.test-rds-subnet-group;
      vpcSecurityGroups = [ resources.ec2SecurityGroups.test-rds-sg ];
    };
}
