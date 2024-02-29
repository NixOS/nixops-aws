{
  description = "Description for the project";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs.url = "github:hercules-ci/nixpkgs/update-nixops_unstable";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
      ];
      debug = true;
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" "x86_64-darwin" ];
      perSystem = { config, self', inputs', pkgs, system, ... }: {
        packages.nixops_with_aws =
          (pkgs.nixops_unstable_minimal.addAvailablePlugins (self: super: {
            nixops-aws = super.callPackage ./nix/nixops-aws.nix { };
          })).withPlugins (plugins: [ plugins.nixops-aws ]);
        packages.plugin = config.packages.nixops_with_aws.availablePlugins.nixops-aws;
        # `plugin` would have been a valid choice, but a nixops is more useful. It builds fast.
        packages.default = config.packages.nixops_with_aws;
        devShells.default =
          pkgs.mkShell {
            inputsFrom = [ config.packages.plugin ];
          };
      };
      flake = {
      };
    };
}
