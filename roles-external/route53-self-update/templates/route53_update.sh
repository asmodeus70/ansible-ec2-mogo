#!/usr/bin/bash

function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi

    return $stat
}

METADATA_URL="http://{{route53_update_config.metadata_service.host}}{{route53_update_config.metadata_service.path}}"
export METADATA_URL
IP=$(curl -sS ${METADATA_URL})
R53_VALUE="${IP}"
R53_TYPE="{{ route53_update.record_set.type }}"
R53_NAME="{{ route53_update.record_set.name }}"
R53_TTL="{{ route53_update.record_set.ttl_seconds }}"
LOGFILE="{{ route53_update.logfile_path }}"

export http_proxy=http://squid.{{aws_region}}:3128
export https_proxy=http://squid.{{aws_region}}:3128ccc
export no_proxy=169.254.169.254,localhost,127.0.0.1

[ -f /etc/profile.d/dvla_environment.sh ] && . /etc/profile.d/dvla_environment.sh

### Main


# Check for valid IP
if ! valid_ip $IP; then
        echo "Invalid IP address: $IP" >> "$LOGFILE"
        exit 1
fi

echo "$(date +"%d-%b-%Y %H:%M:%S") - Updating Route53:" >> "$LOGFILE"
echo "/bin/route53 change_record ${R53_ZONE_ID} ${R53_NAME}.${R53_ZONE} ${R53_TYPE} ${IP} ${R53_TTL}" >> "$LOGFILE"
rc=1
until [ $rc -eq "0" ]; do
	[ -f /etc/profile.d/dvla_environment.sh ] && . /etc/profile.d/dvla_environment.sh
	echo "$(date +"%d-%b-%Y %H:%M:%S") - Attempting Route53 update:" >> "$LOGFILE"
	timeout 30 /bin/route53 change_record ${R53_ZONE_ID} ${R53_NAME}.${R53_ZONE} ${R53_TYPE} ${IP} ${R53_TTL} >> "$LOGFILE" 2>&1
	rc=$?
	sleep 30
done
