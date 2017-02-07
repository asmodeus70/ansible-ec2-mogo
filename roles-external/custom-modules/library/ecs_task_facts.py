#!/usr/bin/python

DOCUMENTATION = '''
---
module: ecs_task_facts
short_description: Gather facts about tasks belonging to a particular ECS Service
description:
    - Gather facts about tasks belonging to a particular ECS Service
'''

try:
    import boto
    import botocore
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

class EcsServiceManager:
    """Handles ECS Services"""

    def __init__(self, module):
        self.module = module

        try:
            region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
            if not region:
                module.fail_json(msg="Region must be specified as a parameter, in EC2_REGION or AWS_REGION environment variables or in boto configuration file")
            self.ecs = boto3_conn(module, conn_type='client', resource='ecs', region=region, endpoint=ec2_url, **aws_connect_kwargs)
        except boto.exception.NoAuthHandlerFound, e:
            self.module.fail_json(msg="Can't authorize connection - "+str(e))


    def describe_tasks(self, cluster, service):
        tasksArns = self.ecs.list_tasks(cluster = cluster)['taskArns']
        response = self.ecs.describe_tasks(cluster = cluster, tasks = tasksArns)

        # relevant_response = dict(services = map(self.extract_service_from, response['services']))
        # if 'failures' in response and len(response['failures'])>0:
        #     relevant_response['services_not_running'] = response['failures']
        return response

    def extract_service_from(self, service):
        # some fields are datetime which is not JSON serializable
        # make them strings
        if 'deployments' in service:
            for d in service['deployments']:
                if 'createdAt' in d:
                    d['createdAt'] = str(d['createdAt'])
                if 'updatedAt' in d:
                    d['updatedAt'] = str(d['updatedAt'])
        if 'events' in service:
            for e in service['events']:
                if 'createdAt' in e:
                    e['createdAt'] = str(e['createdAt'])
        return service

def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        cluster=dict(required=True, type='str'),
        service=dict(required=True, type='str')
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_BOTO:
      module.fail_json(msg='boto is required.')

    if not HAS_BOTO3:
      module.fail_json(msg='boto3 is required.')

    task_mgr = EcsServiceManager(module)
    ecs_facts = task_mgr.describe_tasks(module.params['cluster'], module.params['service'])

    ecs_facts_result = dict(changed=False, ansible_facts=ecs_facts)
    module.exit_json(**ecs_facts_result)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()