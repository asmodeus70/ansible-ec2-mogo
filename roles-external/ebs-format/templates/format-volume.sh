#!/usr/bin/env bash
device_filesystem_status=$(file -s {{ebs_format_device}})
if [ "${device_filesystem_status}" = "{{ebs_format_device}}: data" ]; then
  echo "Volume {{ebs_format_device}} needs to be formatted. Formatting with {{ebs_format_filesystem}} filesystem..."
  mkfs -t {{ebs_format_filesystem}} {{ebs_format_device}}
else
  echo "Volume {{ebs_format_device}} is already formatted: $device_filesystem_status"
fi