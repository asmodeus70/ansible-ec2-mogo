Ansible Role: ami-finish
========================

Produces an Amazon Machine Image (AMI) for a given ec2 instance that has 
has been used for image baking, according the provided build configuration.
The given ec2 instance is terminated once the AMI has been produced.

Role Variables
--------------

### build

A hash containing the image build configuration, e.g.

```yaml
build:
  ami:
    instance_id: abc123def
    name: webapp-1.0
    region: eu-west-1
    tags:
      app: webapp
      version: 1.0
      Service: 1
  terminate:
    instance_id: abc123def
    region: eu-west-1 
```

Output
------

### ec2_build_ami

The result of the ec2_ami creation.

Dependencies
------------

None.
