import boto3
import mypy_boto3_efs
from typing import Optional
import nixops_aws.ec2_utils


class EFSCommonState:
    access_key_id: Optional[str]
    region: Optional[str]
    _client: Optional[mypy_boto3_efs.EFSClient] = None

    def _get_client(self, access_key_id: Optional[str] =None, region: Optional[str]=None):
        if self._client:
            return self._client

        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            access_key_id or self.access_key_id
        )

        if region is not None:
            region_name = region
        elif self.region is not None:
            region_name = self.region
        else:
            raise Exception("region and self.region are None")

        self._client = boto3.session.Session().client(
            "efs",
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

        return self._client
