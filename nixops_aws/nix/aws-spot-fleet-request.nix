{ config, lib, uuid, name, ... }:

with lib;


let
  cfg = config.awsSpotFleetRequest;

  launchSpecificationOptions = {
    options = {
    };
  };

  fleetLaunchTemplateSpecificationOptions = {
    options = {
      launchTemplateName = mkOption {
        type = types.str;
        description = "The name of the launch template. If you specify the template name, you can't specify the template ID.";
      };

      version = mkOption {
        type = types.str;
        description = ''
          The launch template version number, <literal>"$Latest"</literal>, or <literal>"$Default"</literal>.
          If the value is <literal>"$Latest"</literal>, Amazon EC2 uses the latest version of the launch template.
          If the value is <literal>"$Default"</literal>, Amazon EC2 uses the default version of the launch template.
        '';
      };
    };
  };

  launchTemplateOverridesOptions = {
    options = {
    };
  };


  launchTemplateConfigOptions = {
    options = {
      launchTemplateSpecification = mkOption {
        type = types.submodule fleetLaunchTemplateSpecificationOptions;
        description = "The launch template.";
      };
    };
  };
in
{
  imports = [ ./common-ec2-auth-options.nix ];

  options = {

    spotFleetRequestId = mkOption {
      default = "";
      type = types.str;
      description = "Spot fleet request ID (set by NixOps)";
    };

    type = mkOption {
      default = "maintain";
      example = "request";
      type =
        types.enum [
          "request"
          "maintain"
          # "instant" # instant is listed but is not used by Spot Fleet.
        ];
      description = ''
        The type of request. Indicates whether the Spot Fleet only requests
        the target capacity or also attempts to maintain it. When this
        value is <code>request</code>, the Spot Fleet only places the
        required requests. It does not attempt to replenish Spot Instances if
        capacity is diminished, nor does it submit requests in alternative Spot
        pools if capacity is not available. When this value is
        <code>maintain</code>, the Spot Fleet maintains the target capacity.
        The Spot Fleet places the required requests to meet capacity and
        automatically replenishes any interrupted instances.
      '';
    };

    iamFleetRole = mkOption {
      # example = "rolename"; # TODO
      type = types.str;
      description = ''
        The Amazon Resource Name (ARN) of an Identity and Access Management
        (IAM) role that grants the Spot Fleet the permission to request,
        launch, terminate, and tag instances on your behalf.

        Spot Fleet can terminate Spot Instances on your behalf when you cancel
        its Spot Fleet request or when the Spot Fleet request expires, if you
        set <code>TerminateInstancesWithExpiration</code>.
      '';
    };

    launchTemplateConfigs = mkOption
      {
        type = with types; listOf (submodule launchTemplateConfigOptions);
        description = ''
          The launch template and overrides. If you specify <code>LaunchTemplateConfigs</code>, you can't specify <code>LaunchSpecifications</code>. If you include On-Demand capacity in your request, you must use <code>LaunchTemplateConfigs</code>.
        '';
      };

  }
  // (import ./common-ec2-options.nix { inherit lib; });

  config._type = "aws-spot-fleet-request";

}


