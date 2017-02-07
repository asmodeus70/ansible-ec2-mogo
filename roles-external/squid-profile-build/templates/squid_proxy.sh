http_proxy="squid.build.cis.dvla.gov.uk:3128"
https_proxy="squid.build.cis.dvla.gov.uk:3128"
all_proxy="squid.build.cis.dvla.gov.uk:3128"
{# 
169.254.169.254 - Amazon EC2 metadata url
This should match the one in the ebs_volume python
script
#}
no_proxy="169.254.169.254,localhost"

{# Export and declaration done separately to reuse this 
   file in the systemd script(s)
#}
export http_proxy
export https_proxy
export all_proxy
export no_proxy
