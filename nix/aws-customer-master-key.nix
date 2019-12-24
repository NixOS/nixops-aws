{ config, lib, uuid, name, ... }:

with lib;

{
  imports = [ ./common-ec2-auth-options.nix ];

  options = {

    alias = mkOption {
      default = "nixops-${uuid}-${name}";
      type = types.str;
      description = "Alias of the CMK.";
    };

    keyId = mkOption {
      default = "";
      type = types.str;
      description = "The globally unique identifier for the CMK. This is set by NixOps";
    };

    policy = mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        The key policy to attach to the CMK.
      '';
    };

    description = mkOption {
      default = "CMK created by nixops";
      type = types.str;
      description = "A description of the CMK.";
    };

    origin = mkOption {
      default = "AWS_KMS";
      type = types.enum [ "AWS_KMS" "AWS_CLOUDHSM" ];
      description = ''
        The source of the key material for the CMK.
        You cannot change the origin after you create the CMK.
        There is also an EXTERNAL option but it is not supported
        in nixops yet.
      '';
    };

    customKeyStoreId = mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        Creates the CMK in the specified custom key store and the key
        material in its associated AWS CloudHSM cluster. To create a CMK
        in a custom key store, you must also specify the Origin parameter
        with a value of "AWS_CLOUDHSM" .
      '';
    };

    deletionWaitPeriod = mkOption {
      default = 30;
      type = types.int;
      description = ''
        The waiting period, specified in number of days. After
        the waiting period ends, AWS KMS deletes the customer master key (CMK).
        Valid values are between 7 and 30.
      '';
    };

  } // import ./common-ec2-options.nix { inherit lib; };

  config._type = "aws-customer-master-key";
}
