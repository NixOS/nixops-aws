# -*- coding: utf-8 -*-

# Automatic provisioning of AWS IAM roles.

import boto
import boto.iam
import nixops.util
import nixops.resources
import nixops_aws.ec2_utils
from boto.exception import BotoServerError

from .types.iam_role import IamRoleOptions


class IamPermissionException(BotoServerError):
    pass


class IamNotFound(BotoServerError):
    pass


class IAMRoleDefinition(nixops.resources.ResourceDefinition):
    """Definition of an IAM Role."""

    config: IamRoleOptions

    @classmethod
    def get_type(cls):
        return "iam-role"

    @classmethod
    def get_resource_type(cls):
        return "iamRoles"

    def __init__(self, name, config):
        nixops.resources.ResourceDefinition.__init__(self, name, config)
        self.role_name = config.name
        self.access_key_id = config.accessKeyId
        self.policy = config.policy
        self.assume_role_policy = config.assumeRolePolicy

    def show_type(self):
        return "{0}".format(self.get_type())


class IAMRoleState(nixops.resources.ResourceState):
    """State of an IAM Role."""

    state = nixops.util.attr_property(
        "state", nixops.resources.ResourceState.MISSING, int
    )
    role_name = nixops.util.attr_property("ec2.roleName", None)
    access_key_id = nixops.util.attr_property("ec2.accessKeyId", None)
    policy = nixops.util.attr_property("ec2.policy", None)
    assume_role_policy = nixops.util.attr_property("ec2.assumeRolePolicy", None)

    @classmethod
    def get_type(cls):
        return "iam-role"

    def __init__(self, depl, name, id):
        nixops.resources.ResourceState.__init__(self, depl, name, id)
        self._conn = None

    def show_type(self):
        s = super(IAMRoleState, self).show_type()
        return s

    @property
    def resource_id(self):
        return self.role_name

    def get_definition_prefix(self):
        return "resources.iamRoles."

    def _connect(self):
        if self._conn:
            return self._conn
        (access_key_id, secret_access_key) = nixops_aws.ec2_utils.fetch_aws_secret_key(
            self.access_key_id
        )
        self._conn = boto.connect_iam(
            aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key
        )
        return self._conn

    def _destroy(self):
        if self.state != self.UP:
            return

        try:
            try:
                # check for the existance
                self._get_instance_profile(self.role_name)
                self._get_role(self.role_name)
                # sever the link
                self._connect().remove_role_from_instance_profile(
                    self.role_name, self.role_name
                )
            except IamPermissionException as e:
                self.log(str(e))
                raise
            except IamNotFound:
                self.warn("instance profile already destroyed")
            except BotoServerError as e:
                if e.status == 404:
                    self.warn("instance profile probably already removed from role")
            except Exception as e:
                self.log("error removing instance profile: " + str(e))
                raise

            try:
                self._connect().get_role_policy(self.role_name, self.role_name)
                self.log("removing role policy")
                self._connect().delete_role_policy(self.role_name, self.role_name)
            except IamPermissionException as e:
                self.warn(str(e))
                raise
            except IamNotFound:
                self.warn("role policy already destroyed")
            except BotoServerError as e:
                if e.status == 404:
                    self.warn("role policy already removed")
            except Exception as e:
                self.log("error removing role policy: " + str(e))
                raise

            try:
                self._get_role(self.role_name)
                self.log("removing role")
                self._connect().delete_role(self.role_name)
            except IamPermissionException:
                raise
            except IamNotFound:
                self.warn("could not find role")
            except BotoServerError as e:
                if e.status == 404:
                    self.warn("role already removed")

            except Exception as e:
                self.log("error removing role: " + str(e))
                raise

            self.log("removing instance profile")
            self._connect().delete_instance_profile(self.role_name)

        except IamPermissionException:
            raise
        except IamNotFound:
            self.warn("instance profile already destroyed")
        except BotoServerError as e:
            if e.status == 404:
                self.warn("instance profile already removed")

        except Exception as e:
            self.log(str(e))
            raise

        with self.depl._db:
            self.state = self.MISSING
            self.role_name = None
            self.access_key_id = None
            self.policy = None
            self.assume_role_policy = None

    def create_after(self, resources, defn):
        # IAM roles can refer to S3 buckets.
        return {
            r
            for r in resources
            if isinstance(r, nixops_aws.resources.s3_bucket.S3BucketState)
        }

    def _get_instance_profile(self, name, allow404=True):
        try:
            return self._connect().get_instance_profile(name)
        except BotoServerError as e:
            if e.status == 403:
                raise IamPermissionException(e.status, e.reason, body=e.body)
            if e.status == 404:
                if allow404:
                    return False
                else:
                    raise IamNotFound(e.status, e.reason, body=e.body)
        except:
            raise

    def _get_role_policy(self, name, allow404=True):
        try:
            return self._connect().get_role_policy(name, name)
        except BotoServerError as e:
            if e.status == 403:
                raise IamPermissionException(e.status, e.reason, body=e.body)
            if e.status == 404:
                if allow404:
                    return False
                else:
                    raise IamNotFound(e.status, e.reason, body=e.body)
        except:
            raise

    def _get_role(self, name, allow404=True):
        try:
            return self._connect().get_role(name)
        except BotoServerError as e:
            if e.status == 403:
                raise IamPermissionException(e.status, e.reason, body=e.body)
            if e.status == 404:
                if allow404:
                    return False
                else:
                    raise IamNotFound(e.status, e.reason, body=e.body)
        except:
            raise

    def create(self, defn, check, allow_reboot, allow_recreate):

        self.access_key_id = (
            defn.access_key_id or nixops_aws.ec2_utils.get_access_key_id()
        )
        if not self.access_key_id:
            raise Exception(
                "please set ‘accessKeyId’, $EC2_ACCESS_KEY or $AWS_ACCESS_KEY_ID"
            )


        ip = self._get_instance_profile(defn.role_name, True)
        rp = self._get_role_policy(defn.role_name, True)
        r = self._get_role(defn.role_name, True)

        if not r:
            self.log("creating IAM role ‘{0}’...".format(defn.role_name))
            role = self._connect().create_role(defn.role_name)

        if not ip:
            self.log("creating IAM instance profile ‘{0}’...".format(defn.role_name))
            self._connect().create_instance_profile(defn.role_name, "/")
            self._connect().add_role_to_instance_profile(defn.role_name, defn.role_name)

        if not check:
            self._connect().put_role_policy(defn.role_name, defn.role_name, defn.policy)

        if defn.assume_role_policy != "":
            self._connect().update_assume_role_policy(
                defn.role_name, defn.assume_role_policy
            )

        with self.depl._db:
            self.state = self.UP
            self.role_name = defn.role_name
            self.policy = defn.policy

    def destroy(self, wipe=False):
        self._destroy()
        return True
