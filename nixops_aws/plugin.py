import os.path
import nixops.plugins


@nixops.plugins.hookimpl
def nixexprs():
    return [os.path.dirname(os.path.abspath(__file__)) + "/nix"]


@nixops.plugins.hookimpl
def load():
    return [
        "nixops_aws.resources",
        "nixops_aws.backends.ec2",
        "nixops_aws.resources.ec2_keypair",
    ]
