#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_group_facts
short_description: Gather facts about security groups in AWS
description:
    - Gather facts about security groups in AWS
version_added: "2.2"
author: "Chris Cundill (@ChrisCundill)"
options:
  vpc_id:
    description:
      - VPC in which to search for the security groups
      required: true
    default: null
  group_names:
    description:
      - Array of security group names for which facts will be gathered
    required: true
    default: null

extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Gather facts about security groups
- ec2_group_facts:
      vpc_id: vpc-12345678
      group_names: [abc, def]

'''

RETURN = '''
group_id:
    description: Security Group ID
    type: string
    sample: sg-12345678
group_name:
    description: Security group name
    type: string
    sample: My AWS Security Group
'''

try:
    import boto.ec2
    from boto.ec2.securitygroup import SecurityGroup
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


def get_group_info(group):

    group_info = {'group_id': group.id,
                  'group_name': group.name}
    return group_info


def list_ec2_groups(connection, module):

    vpc_id = module.params.get("vpc_id")
    group_names = module.params.get("group_names")

    try:
        vpc_security_groups = connection.get_all_security_groups(filters={'vpc-id': vpc_id})
    except Exception as e:
        module.fail_json(msg=str(e))

    filtered_sec_groups = []
    for group in vpc_security_groups:
        if group.name in group_names:
            filtered_sec_groups.append(get_group_info(group))

    module.exit_json(sgs=filtered_sec_groups)


def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            vpc_id=dict(type='str', required=True),
            group_names=dict(type='list', required=True)
        )
    )

    module = AnsibleModule(
        argument_spec = argument_spec
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    connection = ec2_connect(module)

    list_ec2_groups(connection, module)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()
