from distutils.core import setup


setup(
    name="nixops-aws",
    version="@version@",
    description="NixOS cloud deployment tool, but for aws",
    url="https://github.com/NixOS/nixops-aws",
    # TODO: add author
    author="",
    author_email="",
    packages=[
        "nixopsaws",
        "nixopsaws.data",
        "nixopsaws.resources",
        "nixopsaws.backends",
    ],
    entry_points={"nixops": ["aws = nixopsaws.plugin"]},
    py_modules=["plugin"],
)
