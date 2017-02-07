Ansible Role: ebs-persistent-storage
==============================

Attaches an EBS volume to an instance by:

1. Creating a service to run a python script on boot
2. Executes ebs_volume.py script to attach static EBS volume
3. Records

Useful for when a static volume is needed to be attached to a single EC2 instance.
