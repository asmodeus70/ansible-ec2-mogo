#!/usr/bin/python

DOCUMENTATION = '''
---
module: asg_scheduled_action
short_description: Create a scheduled action on an AWS EC2 Auto Scaling Group
description:
    - Create a scheduled action on an AWS EC2 Auto Scaling Group
'''
try:
    import boto.ec2
    import boto.ec2.autoscale
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def create_scheduled_action(connection, module):
    try:
        if module.params.get('start_time'):
            start_time = datetime.strptime(module.params.get('start_time'), '%Y-%m-%d %H:%M:%S %Z')
        else:
            start_time = None

        response = connection.create_scheduled_group_action(
            as_group = module.params.get('asg_name'),
            name = module.params.get('name'),
            start_time = start_time,
            recurrence = module.params.get('cron'),
            min_size = module.params.get('min_size'),
            max_size = module.params.get('max_size'),
            desired_capacity = module.params.get('desired_capacity')
        )
    except Exception as e:
        module.fail_json(msg=e.message)

    module.exit_json(changed=True, meta=module.params, response=response)


def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            asg_name=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            cron=dict(required=True, type='str'),
            min_size=dict(required=True, type='int'),
            max_size=dict(required=True, type='int'),
            desired_capacity=dict(required=True, type='int'),
            start_time=dict(required=False, type='str')
        )
    )

    module = AnsibleModule(
        argument_spec = argument_spec
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)
    connection = connect_to_aws(boto.ec2.autoscale, region, **aws_connect_params)

    create_scheduled_action(connection, module)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *
from datetime import datetime

main()
