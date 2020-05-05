{
  config_exporters = { optionalAttrs, ... }: [
    (config: { ec2 = optionalAttrs (config.deployment.targetEnv == "ec2") config.deployment.ec2; })
    (config: { route53 = config.deployment.route53; })
  ];
  options = [
    ./ec2.nix
    ./route53.nix
  ];
  resources = { evalResources, zipAttrs, resourcesByType, ... }: {
    snsTopics = evalResources ./sns-topic.nix (zipAttrs resourcesByType.snsTopics or []);
    sqsQueues = evalResources ./sqs-queue.nix (zipAttrs resourcesByType.sqsQueues or []);
    ec2KeyPairs = evalResources ./ec2-keypair.nix (zipAttrs resourcesByType.ec2KeyPairs or []);
    s3Buckets = evalResources ./s3-bucket.nix (zipAttrs resourcesByType.s3Buckets or []);
    iamRoles = evalResources ./iam-role.nix (zipAttrs resourcesByType.iamRoles or []);
    ec2SecurityGroups = evalResources ./ec2-security-group.nix (zipAttrs resourcesByType.ec2SecurityGroups or []);
    ec2PlacementGroups = evalResources ./ec2-placement-group.nix (zipAttrs resourcesByType.ec2PlacementGroups or []);
    ebsVolumes = evalResources ./ebs-volume.nix (zipAttrs resourcesByType.ebsVolumes or []);
    elasticIPs = evalResources ./elastic-ip.nix (zipAttrs resourcesByType.elasticIPs or []);
    rdsDbInstances = evalResources ./ec2-rds-dbinstance.nix (zipAttrs resourcesByType.rdsDbInstances or []);
    rdsDbSecurityGroups = evalResources ./ec2-rds-dbsecurity-group.nix (zipAttrs resourcesByType.rdsDbSecurityGroups or []);
    route53RecordSets = evalResources ./route53-recordset.nix (zipAttrs resourcesByType.route53RecordSets or []);
    elasticFileSystems = evalResources ./elastic-file-system.nix (zipAttrs resourcesByType.elasticFileSystems or []);
    elasticFileSystemMountTargets = evalResources ./elastic-file-system-mount-target.nix (zipAttrs resourcesByType.elasticFileSystemMountTargets or []);
    cloudwatchLogGroups = evalResources ./cloudwatch-log-group.nix (zipAttrs resourcesByType.cloudwatchLogGroups or []);
    cloudwatchLogStreams = evalResources ./cloudwatch-log-stream.nix (zipAttrs resourcesByType.cloudwatchLogStreams or []);
    cloudwatchMetricAlarms = evalResources ./cloudwatch-metric-alarm.nix (zipAttrs resourcesByType.cloudwatchMetricAlarms or []);
    route53HostedZones = evalResources ./route53-hosted-zone.nix (zipAttrs resourcesByType.route53HostedZones or []);
    route53HealthChecks = evalResources ./route53-health-check.nix (zipAttrs resourcesByType.route53HealthChecks or []);
    vpc = evalResources ./vpc.nix (zipAttrs resourcesByType.vpc or []);
    vpcSubnets = evalResources ./vpc-subnet.nix (zipAttrs resourcesByType.vpcSubnets or []);
    vpcInternetGateways = evalResources ./vpc-internet-gateway.nix (zipAttrs resourcesByType.vpcInternetGateways or []);
    vpcEgressOnlyInternetGateways = evalResources ./vpc-egress-only-internet-gateway.nix (zipAttrs resourcesByType.vpcEgressOnlyInternetGateways or []);
    vpcDhcpOptions = evalResources ./vpc-dhcp-options.nix (zipAttrs resourcesByType.vpcDhcpOptions or []);
    vpcNetworkAcls = evalResources ./vpc-network-acl.nix (zipAttrs resourcesByType.vpcNetworkAcls or []);
    vpcNatGateways = evalResources ./vpc-nat-gateway.nix (zipAttrs resourcesByType.vpcNatGateways or []);
    vpcNetworkInterfaces = evalResources ./vpc-network-interface.nix (zipAttrs resourcesByType.vpcNetworkInterfaces or []);
    vpcNetworkInterfaceAttachments = evalResources ./vpc-network-interface-attachment.nix (zipAttrs resourcesByType.vpcNetworkInterfaceAttachments or []);
    vpcRouteTables = evalResources ./vpc-route-table.nix (zipAttrs resourcesByType.vpcRouteTables or []);
    vpcRouteTableAssociations = evalResources ./vpc-route-table-association.nix (zipAttrs resourcesByType.vpcRouteTableAssociations or []);
    vpcRoutes = evalResources ./vpc-route.nix (zipAttrs resourcesByType.vpcRoutes or []);
    vpcCustomerGateways = evalResources ./vpc-customer-gateway.nix (zipAttrs resourcesByType.vpcCustomerGateways or []);
    vpcEndpoints = evalResources ./vpc-endpoint.nix (zipAttrs resourcesByType.vpcEndpoints or []);
    awsVPNGateways = evalResources ./aws-vpn-gateway.nix (zipAttrs resourcesByType.awsVPNGateways or []);
    awsVPNConnections = evalResources ./aws-vpn-connection.nix (zipAttrs resourcesByType.awsVPNConnections or []);
    awsVPNConnectionRoutes = evalResources ./aws-vpn-connection-route.nix (zipAttrs resourcesByType.awsVPNConnectionRoutes or []);
  };
}

