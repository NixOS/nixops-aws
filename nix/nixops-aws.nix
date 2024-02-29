{ lib
, buildPythonPackage
, fetchFromGitHub
, unstableGitUpdater
, poetry-core
, boto
, boto3
, nixops
, nixos-modules-contrib
, typing-extensions
}:

buildPythonPackage {
  pname = "nixops-aws";
  version = "unstable-2023-08-09";
  pyproject = true;

  src =
    with lib.fileset;
    toSource {
      root = ../.;
      fileset = unions [
        ../nixops_aws
        ../pyproject.toml
        ../setup.cfg
        ../tests
        ../tests.py
      ];
    };

  postPatch = ''
    substituteInPlace pyproject.toml \
    --replace poetry.masonry.api poetry.core.masonry.api \
    --replace "poetry>=" "poetry-core>="
  '';

  nativeBuildInputs = [
    poetry-core
  ];

  buildInputs = [
    nixops
  ];

  propagatedBuildInputs = [
    boto
    boto3
    nixos-modules-contrib
    typing-extensions
  ];

  pythonImportsCheck = [ "nixops_aws" ];

  passthru.updateScript = unstableGitUpdater {};

  meta = with lib; {
    description = "AWS plugin for NixOps";
    homepage = "https://github.com/NixOS/nixops-aws";
    license = licenses.lgpl3Only;
    maintainers = nixops.meta.maintainers;
  };
}
