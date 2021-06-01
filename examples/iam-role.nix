{ account
, description ? "IAM Role example"
, ...
}:
{
  network.description = description;

  resources.iamRoles.role = {
    accessKeyId = account;
    tags = {
      Name = "SuperRole";
      Category = "Example";
    };
    policy =
      builtins.toJSON
        {
          Statement =
            [
            {
              Effect = "Allow";
              Action = [ "ses:SendEmail" "ses:SendRawEmail"];
              Resource = "*";
            }
            {
              Effect = "Allow";
              Action = [ "sns:Publish" "sns:ListTopics"];
              Resource = "*";
            }
            {
              Effect = "Allow";
              Action = [ "cloudwatch:PutMetricData" ];
              Resource = "*" ;
            }
            {
              Effect = "Allow";
              Action = [ "ec2:DescribeTags" ];
              Resource = "*" ;
            }
          ];
        };
  };
}
