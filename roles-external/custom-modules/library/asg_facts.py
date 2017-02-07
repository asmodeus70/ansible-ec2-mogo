#!/usr/bin/python

DOCUMENTATION = '''
---
module: asg_facts
short_description: Gather facts about an AWS EC2 Auto Scaling Group
description:
    - Gather facts about an AWS EC2 Auto Scaling Group
'''

try:
    import boto.ec2
    import boto.ec2.autoscale
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def get_tags(asg_tags):

    return list(map(lambda tag: { 'key': tag.key, 'value': tag.value }, asg_tags))

def get_group_info(asg):

    asg_info = {'name': asg.name,
                'availability_zones': asg.availability_zones,
                'load_balancers': asg.load_balancers,
                'min_size': asg.min_size,
                'max_size': asg.max_size,
                'tags': get_tags(asg.tags)}
    return asg_info

def get_group(connection, module):
    try:
        asgs = connection.get_all_groups(max_records = 100)

        name_prog = re.compile(r'^' + module.params['name'])
        matched_asgs = []

        for asg in asgs:
            matched_name = name_prog.search(asg.name)

            if matched_name:
                matched_asgs.append(get_group_info(asg))

    except Exception as e:
        module.fail_json(msg=e.message)

    module.exit_json(meta=module.params, response=matched_asgs)


def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            name=dict(required=True, type='str')
        )
    )

    module = AnsibleModule(
        argument_spec = argument_spec
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)
    connection = connect_to_aws(boto.ec2.autoscale, region, **aws_connect_params)

    get_group(connection, module)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *
import re

main()
