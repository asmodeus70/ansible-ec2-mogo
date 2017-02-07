Ansible Role: iptables
=======================

Sets iptables rules according to input parameters.

Role Variables
--------------

### iptables (optional)

Rules can be provided explicitly or via templates within your roles.

The former is achieved by making use of the iptables.pre_routes and iptables.rules parameters while
the latter requires setting the role_base_dirs parameter and
including template files within the template directories of roles, e.g. 
roles/<role>/templates/iptable_prerouting.j2 and roles/<role>/templates/iptable_rules.j2

Example of providing rules explicitly using pre_route and rule entries, e.g.

```yaml

iptables:
  pre_routes:
    - "-A PREROUTING -i eth1 -p udp --dport 53 -j DNAT --to-destination some_dns_server"
  rules:
    - "-A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT"
    
```

Output
------

None.

Dependencies
------------

None.
