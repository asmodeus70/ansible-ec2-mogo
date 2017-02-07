Ansible Role: nginx-https-front-upstream
========================================

Configures nginx as a HTTPS termination proxy to front an application running on a configurable port.

Role Variables
--------------

### nginx_https_front_upstream

A dictionary containing the HTTPS proxy configuration, e.g.

```yaml

nginx_https_front_upstream:
  nginx_conf_name: jenkins
  port_to_secure: 8080
  private_key: |
    -----BEGIN PRIVATE KEY-----
    SOMEPRIVATESTUFF
    -----END PRIVATE KEY-----

  public_crt: |
    -----BEGIN CERTIFICATE-----
    SOMEPRIVATESTUFF
    -----END CERTIFICATE-----
```


Output
------

None.


Dependencies
------------

None.