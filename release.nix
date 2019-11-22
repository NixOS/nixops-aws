{ nixopsSrc ? { outPath = ./.; revCount = 0; shortRev = "abcdef"; rev = "HEAD"; }
, officialRelease ? false
, nixpkgs ? <nixpkgs>
}:

let
  pkgs = import nixpkgs { system = "x86_64-linux"; };
  version = "1.7" +
            (if officialRelease then ""
             else if nixopsSrc ? lastModified then "pre${builtins.substring 0 8 nixopsSrc.lastModified}.${nixopsSrc.shortRev}"
             else "pre${toString nixopsSrc.revCount}_${nixopsSrc.shortRev}");
in

rec {
  build = pkgs.lib.genAttrs [ "x86_64-linux" "i686-linux" "x86_64-darwin" ] (system:
    with import nixpkgs { inherit system; };

    python2Packages.buildPythonApplication rec {
      pname = "nixops-aws";
      inherit version;
      namePrefix = "";

      src = ./.;

      prePatch = ''
        substituteAllInPlace setup.py
      '';

      buildInputs = with python2Packages; [ nose coverage ];
      propagatedBuildInputs = with python2Packages; [ boto boto3 ];

      # For "nix-build --run-env".
      shellHook = ''
        export PYTHONPATH=$(pwd):$PYTHONPATH
        export PATH=$(pwd)/scripts:${openssh}/bin:$PATH
      '';

      doCheck = false;

      # Needed by libcloud during tests
      SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";

      # Add openssh to nixops' PATH. On some platforms, e.g. CentOS and RHEL
      # the version of openssh is causing errors when have big networks (40+)
      makeWrapperArgs = ["--prefix" "PATH" ":" "${openssh}/bin" "--set" "PYTHONPATH" ":"];

      postInstall = ''
        mkdir -p $out/share/nix/nixops-aws
        cp -av nix/* $out/share/nix/nixops-aws
      '';

      meta.description = "NixOps AWS package for ${stdenv.system}";
    }
  );
}
