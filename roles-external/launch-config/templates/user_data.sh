#!/usr/bin/env bash

# Set environment variables for all profiles
if [ ! -f /etc/profile.d/dvla_environment.sh ]; then
  echo "export AWS_REGION={{aws_region}}" >> /etc/profile.d/dvla_environment.sh
  echo "export AWS_DEFAULT_REGION={{aws_region}}" >> /etc/profile.d/dvla_environment.sh
  echo "export ENVIRONMENT={{deploy_env}}" >> /etc/profile.d/dvla_environment.sh
  echo "export EC2_PREFIX={{ec2_prefix}}" >> /etc/profile.d/dvla_environment.sh
  echo "export DEPLOY_COLOUR={{blue_green}}" >> /etc/profile.d/dvla_environment.sh
  echo "export R53_ZONE={{deploy_env}}.{{domain}}." >> /etc/profile.d/dvla_environment.sh
  echo "export R53_ZONE_ID={{platform_route53.zones[deploy_env].zone_id}}" >> /etc/profile.d/dvla_environment.sh
fi

# Set environment variables for systemd service if present
if [ -f /etc/sysconfig/{{ec2_prefix}} ]; then
  sed -i -e '$a\' /etc/sysconfig/{{ec2_prefix}}
  echo "AWS_REGION={{aws_region}}" >> /etc/sysconfig/{{ec2_prefix}}
  echo "AWS_DEFAULT_REGION={{aws_region}}" >> /etc/sysconfig/{{ec2_prefix}}
  echo "ENVIRONMENT={{deploy_env}}" >> /etc/sysconfig/{{ec2_prefix}}
  echo "EC2_PREFIX={{ec2_prefix}}" >> /etc/sysconfig/{{ec2_prefix}}
  echo "http_proxy=squid.{{aws_region}}:3128" >> /etc/sysconfig/{{ec2_prefix}}
  echo "https_proxy=squid.{{aws_region}}:3128" >> /etc/sysconfig/{{ec2_prefix}}
  echo "all_proxy=squid.{{aws_region}}:3128" >> /etc/sysconfig/{{ec2_prefix}}
  echo "no_proxy=.cis.dvla.gov.uk,169.254.169.254,localhost" >> /etc/sysconfig/{{ec2_prefix}}
fi

# Set environment variables for logstash if present
if [ -f /etc/sysconfig/logstash ]; then
  sed -i -e '$a\' /etc/sysconfig/logstash
  echo "export ENVIRONMENT={{deploy_env}}" >> /etc/sysconfig/logstash
  echo "export DEPLOY_COLOUR={{blue_green}}" >> /etc/sysconfig/logstash
  systemctl restart logstash
fi

# Update bash prompt with deployment colour if present
if [ -f /etc/profile.d/user_prompt.sh ]; then
  echo "export PS1=\"[\u@{{deploy_env}}-{{aws_region}}-{{ec2_prefix}}-{{blue_green}}:\W]$ \"" > /etc/profile.d/user_prompt.sh
fi


echo "$(date --rfc-2822)" >> /tmp/user_data_finish

