from __future__ import annotations
import boto3
from typing import Optional, TYPE_CHECKING
import nixops_aws.ec2_utils

if TYPE_CHECKING:
    import mypy_boto3_efs


class EFSCommonState:
    access_key_id: Optional[str]
    region: Optional[str]
    _efs_client: Optional[mypy_boto3_efs.EFSClient] = None

    def _get_efs_client(
        self, access_key_id: Optional[str] = None, region: Optional[str] = None
    ) -> mypy_boto3_efs.EFSClient:
        if self._efs_client:
            return self._efs_client

        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            access_key_id or self.access_key_id
        )

        if region is not None:
            region_name = region
        elif self.region is not None:
            region_name = self.region
        else:
            raise Exception("region and self.region are None")

        client: mypy_boto3_efs.EFSClient = boto3.session.Session().client(
            "efs",
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        self._efs_client = client

        return self._efs_client
