Ansible Role: ntp
=================

Installs and configures ntp for RHEL

Role Variables
--------------

### ntp_servers

An array of NTP server hosts to be included in ntp.conf on target 
instance, .e.g.

```yaml

ntp_servers:
  - 0.rhel.pool.ntp.org
  - 1.rhel.pool.ntp.org
  - 2.rhel.pool.ntp.org
  - 3.rhel.pool.ntp.org

```


Output
------

None.

Dependencies
------------

None.

