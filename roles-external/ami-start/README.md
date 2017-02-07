Ansible Role: ami-start
====================================

Launches an ec2 instance according the provided build configuration ready for image baking.

Role Variables
--------------

### build

A hash containing the image build configuration, e.g.

```yaml
build:
  launch:
    key_pair: ansible
    region: eu-west-1
    subnet_id: subnet-a1bbcde1
    security_group_id: sg-a1bbcde1
    instance_type: t2.medium
    assign_public_ip: no
    tags:
        type: buildbox
        Environment: mgmt
        Name: some-buildbox
        Service: 1
```

Output
------

### ec2_build

The result of the ec2 instance launch.

### build_instance_id

The identifier of the ec2 instance launched for image building.

### memory_hosts

This role creates an in-memory host group called memory_hosts along with 
such variables as deploy_env, aws_region, blue_green and ec2_prefix. 

Dependencies
------------

None.

