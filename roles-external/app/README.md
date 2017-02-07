Ansible Role: app
==============================

Installs and configures an app from a Nexus Yum repository on RHEL 7.

Configures Yum repo, installs package and enables app as a service.

Role Variables
--------------

### app_name

The name of app package to install. Required. No default.

### app_version: 

Version of the app package to install. Defaults to "latest". 

###  app_repo_base: 

Base URL of the Nexus Yum repo. Defaults to http://nexus.cis.dvla.gov.uk:8081/nexus/content/repositories.

### app_repo_name: 

The name of the Nexus Yum repo. Defaults to "snapshots".

### app_config_file: 

App config template filename. Defaults to "none".

### app_config_destination: 

File path of app config on target host. Defaults to "/etc/opt/{{app_name}}/{{app_name}}.conf"


Output
------

None

Dependencies
------------

None.
