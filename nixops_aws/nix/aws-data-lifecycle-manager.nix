{ config, lib, uuid, name, ... }:

with lib;

{
  imports = [ ./common-ec2-auth-options.nix ];

  options = {

    dlmName = mkOption {
      default = "nixops-${uuid}-${name}";
      type = types.str;
      description = "data lifecycle manager name.";
    };

    policyId = mkOption {
      default = "";
      type = types.str;
      description = "The identifier of the lifecycle policy. This is set by NixOps";
    };

    description = mkOption {
      default = "lifecycle policy created by nixops.";
      type = types.str;
      description = "A description of the lifecycle policy. ";
    };

    executionRole = mkOption {
      default = "AWSDataLifecycleManagerDefaultRole";
      type = types.str;
      description = "IAM role used to run the operations specified by the lifecycle policy.";
    };

    resourceTypes = mkOption {
      default = "instance"  ;
      type = types.enum [ "instance" "volume" ];
      description = "The resource type.";
    };

    targetTags = mkOption {
      default = { };
      example = { foo = "bar"; xyzzy = "bla"; };
      type = types.attrsOf types.str;
      description = ''
        The single tag that identifies targeted resources for this policy.
      '';
    };

    excludeBootVolume = mkOption {
      default = true;
      type = types.bool;
      description = ''
        When executing an EBS Snapshot Management – Instance policy,
        execute all CreateSnapshots calls with the excludeBootVolume
        set to the supplied field. Defaults to false. Only valid for
        EBS Snapshot Management – Instance policies.
      '';
    };

    copyTags = mkOption {
      default = true;
      type = types.bool;
      description = ''
        Copy all user-defined tags on a source volume to snapshots
        of the volume created by this policy.
      '';
    };

    tagsToAdd = mkOption {
      default = { };
      example = { foo = "bar"; xyzzy = "bla"; };
      type = types.attrsOf types.str;
      description = ''
        The tags to apply to policy-created resources.
        These user-defined tags are in addition to the
        AWS-added lifecycle tags.
      '';
    };

    ruleInterval = mkOption {
      default = 12;
      type = types.enum [ 2 3 4 6 8 12 24 ];
      description = ''
        The interval between snapshots. The supported
        values are 2, 3, 4, 6, 8, 12, and 24.
      '';
    };

    ruleIntervalUnit = mkOption {
      default = "hours";
      type = types.enum [ "hours" ];
      description = "The interval unit.";
    };

    ruleTime = mkOption {
      default = "09:00";
      type = types.str;
      description = ''
        The time, in UTC, to start the operation.
        The supported format is hh:mm. The operation occurs
        within a one-hour window following the specified time.
      '';
    };

    retainRule = mkOption {
      default = 1000;
      type = types.int;
      description = ''
        The number of snapshots to keep for each volume, up to a maximum of 1000.
      '';
    };
  };

  config._type = "aws-data-lifecycle-manager";
}