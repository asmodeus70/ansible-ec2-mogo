#!/usr/bin/env python

# Hackhackhack, this class is the basis of something decent, but needs work on
# TODO: error handling
# TODO: exception checking
# TODO: Validation

import boto3


class DvlaIam:

    def __init__(self):
        self.boto_client = boto3.client('iam')

    @staticmethod
    def _get_json(json_document):
        with open(json_document, 'r') as policy_file:
            return policy_file.read()

    def get_policy_by_name(self, policy_name):
        response = self.boto_client.list_policies(
            Scope='Local'
        )
        for item in response['Policies']:
            if item['PolicyName'] == policy_name:
                return item

    def create_policy(self, policy_json=None, policy_name=None, policy_description=None):
        policy_json_text = self._get_json(policy_json)

        policy = self.get_policy_by_name(policy_name)

        if policy:
            return self.create_policy_version(policy_arn=policy['Arn'], policy_json_text=policy_json_text, default=True)
        else:
            return self.boto_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=policy_json_text,
                Description=policy_description
            )

    def create_policy_version(self, policy_arn=None, policy_json_text=None, default=None):
        versions = self.boto_client.list_policy_versions(PolicyArn=policy_arn)

        number_of_records = len(versions['Versions'])

        # get the current version document.  compare it with whats coming in.  do nothing if no changes.

        if number_of_records == 5:
            # delete the oldest unused
            deleted = False
            counter = number_of_records
            while not deleted:
                policy_version = versions['Versions'][counter - 1]
                if not policy_version['IsDefaultVersion']:
                    response = self.boto_client.delete_policy_version(
                        PolicyArn=policy_arn, VersionId=policy_version['VersionId'])
                    deleted = True

        response = self.boto_client.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=policy_json_text,
            SetAsDefault=default
        )

        # Arn is not included in policy version response
        response['Arn'] = policy_arn
        return response

    def create_role(self, role_name=None, assume_role_policy_document=None):
        assume_role_policy_document_text = self._get_json(
            assume_role_policy_document)
        return self.boto_client.create_role(RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_document_text)

    def attach_role_policy(self, role_name=None, policy_arn=None):
        self.boto_client.attach_role_policy(
            RoleName=role_name, PolicyArn=policy_arn)

    def create_instance_profile(self, instance_profile_name=None):
        return self.boto_client.create_instance_profile(InstanceProfileName=instance_profile_name)

    def attach_role_to_instance_profile(self, role_name=None, instance_profile_name=None):
        return self.boto_client.add_role_to_instance_profile(RoleName=role_name, InstanceProfileName=instance_profile_name)

    def create_instance_profile_with_role(self, role_name=None, instance_profile_name=None):
        # TODO: We dont have access to query instance profile, so just throwing the exception for now.
        # We need iam:GetInstanceProfile
        # Return something more meaningful
        self.create_instance_profile(
            instance_profile_name=instance_profile_name)
        self.attach_role_to_instance_profile(
            role_name=role_name, instance_profile_name=instance_profile_name)
