#!/usr/bin/env nix-shell
#!nix-shell -p awscli
#!nix-shell -p nixpkgs-fmt
#!nix-shell -I nixpkgs=channel:nixos-unstable
#!nix-shell -i bash
set -euo pipefail

if test -z "${NO_FETCH:-}"; then
  aws ec2 describe-instance-types --region us-east-1 >instance-types.json
fi

nix-instantiate ec2-properties.nix --eval --strict | sed -e 's/; "/;\n  "/' | nixpkgs-fmt >ec2-properties-orig-sorted.nix

nix-instantiate --strict --eval ./generate-ec2-properties.nix \
  | sed -e 's/; "/;\n  "/' \
  | nixpkgs-fmt \
  > ec2-properties-generated.nix

diff --color=always ec2-properties-orig-sorted.nix ec2-properties-generated.nix
