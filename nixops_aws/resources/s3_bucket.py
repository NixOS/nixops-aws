# -*- coding: utf-8 -*-

# Automatic provisioning of AWS S3 buckets.

import botocore
import boto3
import json
import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
from typing import Union
from typing_extensions import Literal

from .types.s3_bucket import S3BucketOptions


class S3BucketDefinition(nixops.resources.ResourceDefinition):
    """Definition of an S3 bucket."""

    config: S3BucketOptions

    @classmethod
    def get_type(cls):
        return "s3-bucket"

    @classmethod
    def get_resource_type(cls):
        return "s3Buckets"

    def __init__(self, name, config):
        nixops.resources.ResourceDefinition.__init__(self, name, config)
        self.bucket_name = self.config.name
        self.region = self.config.region
        self.access_key_id = self.config.accessKeyId
        self.policy = self.config.policy
        self.lifecycle = self.config.lifeCycle
        self.versioning = self.config.versioning
        self.website_enabled = self.config.website.enabled
        self.website_suffix = self.config.website.suffix
        self.website_error_document = self.config.website.errorDocument
        self.persist_on_destroy = self.config.persistOnDestroy

    def show_type(self):
        return "{0} [{1}]".format(self.get_type(), self.region)


class S3BucketState(nixops.resources.ResourceState[S3BucketDefinition]):
    """State of an S3 bucket."""

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    bucket_name = nixops.util.attr_property("ec2.bucketName", None)
    access_key_id = nixops.util.attr_property("ec2.accessKeyId", None)
    region = nixops.util.attr_property("ec2.region", None)
    versioning = nixops.util.attr_property("versioning", None)
    persist_on_destroy = nixops.util.attr_property("persistOnDestroy", False)

    @classmethod
    def get_type(cls):
        return "s3-bucket"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn = None

    def show_type(self):
        s = super(S3BucketState, self).show_type()
        if self.region:
            s = "{0} [{1}]".format(s, self.region)
        return s

    @property
    def resource_id(self):
        return self.bucket_name

    def get_definition_prefix(self):
        return "resources.s3Buckets."

    def _connect(self):
        if self._conn:
            return self._conn
        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            self.access_key_id
        )
        self._conn = boto3.session.Session(
            region_name=self.region if self.region != "US" else "us-east-1",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        return self._conn

    def create(self, defn, check, allow_reboot, allow_recreate):

        self.access_key_id = (
            defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
        )
        if not self.access_key_id:
            raise Exception(
                "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )

        if len(defn.bucket_name) > 63:
            raise Exception(
                "bucket name ‘{0}’ is longer than 63 characters.".format(
                    defn.bucket_name
                )
            )

        s3client = self._connect().client("s3")
        if check or self.state != self.UP:

            self.log("creating S3 bucket ‘{0}’...".format(defn.bucket_name))
            try:
                ACL = "private"  # ..or: public-read, public-read-write, authenticated-read
                s3loc = region_to_s3_location(defn.region)
                if s3loc == "US":
                    s3client.create_bucket(ACL=ACL, Bucket=defn.bucket_name)
                else:
                    s3client.create_bucket(
                        ACL=ACL,
                        Bucket=defn.bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": s3loc},
                    )
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                    raise

            with self.depl._db:
                self.state = self.UP
                self.bucket_name = defn.bucket_name
                self.region = defn.region
                self.persist_on_destroy = defn.persist_on_destroy

        try:

            if self.versioning != defn.versioning:
                self.log(
                    "Updating versioning configuration on ‘{0}’...".format(
                        defn.bucket_name
                    )
                )
                s3client.put_bucket_versioning(
                    Bucket=defn.bucket_name,
                    VersioningConfiguration={"Status": defn.versioning},
                )
                with self.depl._db:
                    self.versioning = defn.versioning

            if self.persist_on_destroy != defn.persist_on_destroy:
                with self.depl._db:
                    self.persist_on_destroy = defn.persist_on_destroy

        except botocore.exceptions.ClientError as e:
            self.log(
                "An Error occured while Updating versioning configuration on ‘{0}’...".format(
                    defn.bucket_name
                )
            )
            raise e

        if defn.policy:
            self.log("setting S3 bucket policy on ‘{0}’...".format(defn.bucket_name))
            s3client.put_bucket_policy(
                Bucket=defn.bucket_name, Policy=defn.policy.strip()
            )
        else:
            try:
                s3client.delete_bucket_policy(Bucket=defn.bucket_name)
            except botocore.exceptions.ClientError as e:
                # This seems not to happen - despite docs indicating it should:
                # [http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketDELETEpolicy.html]
                if e.response["ResponseMetadata"]["HTTPStatusCode"] != 204:
                    raise  # (204 : Bucket didn't have any policy to delete)

        if defn.lifecycle:
            self.log(
                "setting S3 bucket lifecycle configuration on ‘{0}’...".format(
                    defn.bucket_name
                )
            )
            s3client.put_bucket_lifecycle_configuration(
                Bucket=defn.bucket_name,
                LifecycleConfiguration=json.loads(defn.lifecycle),
            )
        else:
            try:
                s3client.delete_bucket_lifecycle(Bucket=defn.bucket_name)
            except botocore.exceptions.ClientError as e:
                self.log(
                    "An Error occured while deleting lifecycle configuration on ‘{0}’...".format(
                        defn.bucket_name
                    )
                )
                raise e

        if not defn.website_enabled:
            try:
                s3client.delete_bucket_website(Bucket=defn.bucket_name)
            except botocore.exceptions.ClientError as e:
                if e.response["ResponseMetadata"]["HTTPStatusCode"] != 204:
                    raise
        else:
            website_config = {"IndexDocument": {"Suffix": defn.website_suffix}}
            if defn.website_error_document != "":
                website_config["ErrorDocument"] = {"Key": defn.website_error_document}
            s3client.put_bucket_website(
                Bucket=defn.bucket_name, WebsiteConfiguration=website_config
            )

    def destroy(self, wipe=False):
        if self.state == self.UP:
            if self.persist_on_destroy:
                self.warn(
                    "S3 bucket '{}' will be left due to the usage of"
                    " persistOnDestroy = true".format(self.bucket_name)
                )
                return True

            try:
                self.log("destroying S3 bucket ‘{0}’...".format(self.bucket_name))
                bucket = self._connect().resource("s3").Bucket(self.bucket_name)
                try:
                    bucket.delete()
                except botocore.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] != "BucketNotEmpty":
                        raise
                    if not self.depl.logger.confirm(
                        "are you sure you want to destroy S3 bucket ‘{0}’?".format(
                            self.bucket_name
                        )
                    ):
                        return False
                    bucket.objects.all().delete()
                    bucket.delete()
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "NoSuchBucket":
                    raise
        return True


def region_to_s3_location(region):
    # S3 location names are identical to EC2 regions, except for
    # us-east-1 and eu-west-1.
    if region == "eu-west-1":
        return "EU"
    elif region == "us-east-1":
        return "US"
    else:
        return region
