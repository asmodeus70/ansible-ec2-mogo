Ansible Role: clamav
===========================

Installs and configures clamav as a service.  Manages selinux to allow
system scanning.  Uses freshclam to keep virus database current.

Role Variables
--------------

None.


Output
------

None.

Dependencies
------------

None.


Example Playbook
----------------

```yaml
- hosts: webapp
  roles:
    - clamav
```
