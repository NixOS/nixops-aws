import os.path
import nixops.plugins
from nixops.plugins import Plugin


class NixopsAWSPlugin(Plugin):
    @staticmethod
    def nixexprs():
        return [os.path.dirname(os.path.abspath(__file__)) + "/nix"]

    @staticmethod
    def load():
        return [
            "nixops_aws.resources",
            "nixops_aws.backends.ec2",
            "nixops_aws.resources.ec2_keypair",
        ]


@nixops.plugins.hookimpl
def plugin():
    return NixopsAWSPlugin()
