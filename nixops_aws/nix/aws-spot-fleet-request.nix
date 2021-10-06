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
      spotPrice = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr str;
        description = "The maximum price per unit hour that you are willing to pay for a Spot Instance.";
      };

      subnetId = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr str;
        # description = "The ID of the subnet in which to launch the instances.";
      };

      availabilityZone = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr str;
        description = "The Availability Zone in which to launch the instances.";
      };

      weightedCapacity = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr float;
        description = "The number of units provided by the specified instance type.";
      };

      priority = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr float;
        description = ''
          The priority for the launch template override. The highest priority is launched first.
          If <code>OnDemandAllocationStrategy</code> is set to <literal>"prioritized"</literal>, Spot Fleet uses priority to determine which launch template override to use first in fulfilling On-Demand capacity.
          If the Spot <code>AllocationStrategy</code> is set to <literal>"capacityOptimizedPrioritized"</literal>, Spot Fleet uses priority on a best-effort basis to determine which launch template override to use in fulfilling Spot capacity, but optimizes for capacity first.
          Valid values are whole numbers starting at <literal>0</literal>. The lower the number, the higher the priority. If no number is set, the launch template override has the lowest priority. You can set the same priority for different launch template overrides.
        '';
      };

      # Common EC2 instance options
      instanceType = mkOption {
        default = null;
        # example = ;
        type = with types; nullOr str;
        description = "The instance type.";
      };
    };
  };

  launchTemplateConfigOptions = {
    options = {
      launchTemplateSpecification = mkOption {
        type = types.submodule fleetLaunchTemplateSpecificationOptions;
        description = "The launch template.";
      };

      overrides = mkOption {
        default = [ ]; # Optional
        example = [
          {
            instanceType = "m1.small";
            weightedCapacity = 1.;
          }
          {
            instanceType = "m3.medium";
            weightedCapacity = 1.;
          }
          {
            instanceType = "m1.medium";
            weightedCapacity = 1.;
          }
        ];
        type = with types; listOf (types.submodule launchTemplateOverridesOptions);
        description = "Any parameters that you specify override the same parameters in the launch template.";
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

    iamFleetRole = mkOption {
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

    spotPrice = mkOption {
      type = with types; nullOr str;
      description = ''
        The maximum price per unit hour that you are willing to pay for a Spot Instance. The default is the On-Demand price.
      '';
    };

    spotMaxTotalPrice = mkOption {
      type = with types; nullOr str;
      description = "The maximum amount per hour for Spot Instances that you're willing to pay. You can use the <code>spotdMaxTotalPrice</code> parameter, the <code>onDemandMaxTotalPrice</code> parameter, or both parameters to ensure that your fleet cost does not exceed your budget. If you set a maximum price per hour for the On-Demand Instances and Spot Instances in your request, Spot Fleet will launch instances until it reaches the maximum amount you're willing to pay. When the maximum amount you're willing to pay is reached, the fleet stops launching instances even if it hasn’t met the target capacity.";
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


