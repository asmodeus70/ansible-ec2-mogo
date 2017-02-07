#!/usr/bin/python

'''
Script to attach a volume and mount it to the given location
'''
# ---------------------------- Module imports ---------------------------------------------------
import boto.ec2
from boto.exception import EC2ResponseError
import time
import subprocess
import os
import sys
import signal
# ---------------------------- Global variables -------------------------------------------------
global blockdevice
global partition
global mountpoint
# ---------------------------- Script variables -------------------------------------------------
blockdevice="{{ ebs_persistent[aws_region]['blockdevice'] }}"
partition="{{ ebs_persistent[aws_region]['partition'] }}"
mountpoint="{{ ebs_persistent[aws_region]['mountpoint'] }}"
vol_id="{{ ebs_persistent[aws_region]['vol_id'] }}"
region="{{ aws_region }}"
log_file="{{ebs_log_path}}"
# ---------------------------- Constants --------------------------------------------------------
# Minutes to retry on an unsuccessful mount attempt
FAIL_RETRY_FREQ_IN_MINUTES = 1
# Minutes to check mount point after successful mount
PASS_CHECK_FREQ_IN_MINUTES = {{disk_check_in_minutes}}
# An executable (script or binary) to run before a mount
# If the var not defined, it will be ignored
{% if pre_mount_script is defined %}
PRE_MOUNT_SCRIPT = "{{pre_mount_script}}"
{% else %}
PRE_MOUNT_SCRIPT = ''
{% endif %}
# An executable (script or binary) to run after a successful mount
# If the var not defined, it will be ignored
{% if post_mount_script is defined %}
POST_MOUNT_SCRIPT = "{{post_mount_script}}"
{% else %}
POST_MOUNT_SCRIPT = ''
{% endif %}

# Redirect the stdout and stderr
sys.stdout = open(log_file,'a',0)
sys.stderr = open(log_file,'a',0)
# ---------------------------- Internal Functions -----------------------------------------------
def cleanup_before_exit(signal, frame):
  print "Exit requested."
  # Flush the buffers
  sys.stdout.flush()
  sys.stderr.flush()
  sys.exit(0)
# -----------------------------------------------------------------------------------------------
def ec2_connect():
  """
  Connects to EC2, returns a connection object.
  """

  global ec2conn
  
  try: 
    ec2conn = boto.ec2.connect_to_region(region)
  except Exception, e:
    sys.stderr.write ('ERROR: Could not connect to region: %s. Exception: %s\n' % (region, e))
    return False

  return True
# -----------------------------------------------------------------------------------------------
def volume_status():
  """
  Print volume object information.
  """
  print '============ Volume status ==========='
  print 'Time:', (time.strftime("%c"))
  print 'My instance ID:', instance_id
  print 'Current Volume Status: ', curr_vol.status
  print 'Current Volume Availability Zone: ', curr_vol.zone
  print 'Current Volume Device: ', curr_vol.attach_data.device
  print 'Volume attached to instance: ', curr_vol.attach_data.instance_id
  print 'Volume attachment time: ', curr_vol.attach_data.attach_time
  print 'Volume id: ', curr_vol.attach_data.id
  print '/usr/sbin/lsblk: '
  print subprocess.check_output("/usr/bin/lsblk", shell=True)
  print '/usr/bin/df -hT: '
  print subprocess.check_output("/usr/bin/df -hT", shell=True)
  print '--------------------------------------'
# -----------------------------------------------------------------------------------------------
def volume_attach():
  """
  Attach volume to instance and expose to OS as blockdevice.
  """
  if instance_id != curr_vol.attach_data.instance_id:
    ec2conn.attach_volume(vol_id,instance_id, blockdevice)
  else:
    print "[volume-attach]: Volume %s already attached to current instance %s." % (vol_id, instance_id)
# -----------------------------------------------------------------------------------------------
def volume_detach():
  """
  Detach volume. Note FORCE detach is set to true to allow forced detach.
  """
  if instance_id == curr_vol.attach_data.instance_id:
    print "[volume-detach]: Volume %s already attached to this instance %s. Skipping detach." % (vol_id, instance_id)
    return
  else: 
    print "[volume-detach]: Volume %s attached to instance %s. Detaching." % (vol_id,curr_vol.attach_data.instance_id)
    ec2conn.detach_volume(vol_id,instance_id=None,device=None,force=True)
    waitfor_available()
# -----------------------------------------------------------------------------------------------
def waitfor_available():
  """
  Check whether volume status is 'in-use'.
  """
  while curr_vol.status == 'in-use':
    print "Waiting for volume to become available. Volume state: %s" % curr_vol.status
    time.sleep(5)
    curr_vol.update()
# -----------------------------------------------------------------------------------------------
def mount():
  """
  Check whether filesystem is already mounted. 
  Wait for block device to become visible and mount filesystem once available.
  """
  if not os.path.exists(mountpoint):
    sys.stderr.write("[mount] ERROR: Path %s does not exist" % mountpoint)
    return False

  if os.path.ismount(mountpoint):
    print "[mount]: Filesystem", mountpoint, " is already mounted. Skipping mount."
    return True

  while not os.path.exists(blockdevice):
    print "[mount]: Waiting for block device %s to become visible. Sleeping before retry. " % blockdevice
    time.sleep(5) # Wait 5 seconds before retry

  print "[mount]: Block device %s is visible. Mounting filesystem %s." % (blockdevice, mountpoint)
  mount_result = subprocess.Popen(['/bin/mount', partition, mountpoint], stderr=sys.stderr, stdout=sys.stdout)
  retVal = False
  if mount_result != None:
    mount_result.communicate()
    print "[mount: mount returned %d." % mount_result.returncode
    retVal = (mount_result.returncode == 0)
  else:
    sys.stderr.write("[mount] ERROR: mount subprocess failed for unknown reason")
  return retVal
# -----------------------------------------------------------------------------------------------
def run_script(script_to_run):
  script_error = ''
  script_result = None
  if len(script_to_run) > 0:
    try:
      script_result = subprocess.Popen([script_to_run],stderr = subprocess.PIPE, stdout=sys.stdout)
      if script_result != None:
        script_error = script_result.stderr.read()
      if len(script_error) > 0:
        sys.stderr.write("ERROR: Script %s failed with error %s." % (script_to_run, script_error))
        return False
    except Exception, e:
      sys.stderr.write ('ERROR: Script %s crashed with exception %s.' % (script_to_run, str(e)))
      return False
  return True
# -----------------------------------------------------------------------------------------------
def get_vol_status():
  ret_val = None
  rc = -1
  while rc == -1:
    try:
      ret_val = ec2conn.get_all_volumes([vol_id])[0]
      rc=0
    except Exception, e:
      sys.stderr.write ('ERROR: Could not get info of volume %s for region: %s. Check network, squid availability, boto credentials and volume id. Sleeping 60s until retry...\n' % (vol_id, region))
      time.sleep(60)
  return ret_val
# -----------------------------------------------------------------------------------------------
def volume_mounted():
  return os.path.ismount(mountpoint)
# --------------------------------- Main Flow ---------------------------------------------------
# Trap the interrupts to cleanup before exit
signal.signal(signal.SIGINT, cleanup_before_exit)
signal.signal(signal.SIGTERM, cleanup_before_exit)
# Get the instance Id 
while True:
  id_retry_sec = 20
  try:
    instance_id = subprocess.check_output("curl -s http://169.254.169.254/latest/meta-data/instance-id", shell=True)
    if (len(instance_id) > 0):
      print('Current instance id is %s' % (instance_id))
      break
  except Exception, e:
    pass
  sys.stderr.write ('ERROR: Failed to get the instance id. Trying in %d seconds.' % (id_retry_sec))
  time.sleep(id_retry_sec)

while True:
  # Set the default frequency as fail
  next_iter_in_minutes = FAIL_RETRY_FREQ_IN_MINUTES
  # Check if volume is mounted
  if not volume_mounted():
    # Set the default frequency as pass
    next_iter_in_minutes = PASS_CHECK_FREQ_IN_MINUTES
    if run_script(PRE_MOUNT_SCRIPT):
      if ec2_connect():
        curr_vol = get_vol_status()
        
        volume_status()
        if curr_vol.status != "available" and curr_vol.status != "in-use":
          print "Volume status undetermined. Will try again ..."
          next_iter_in_minutes = FAIL_RETRY_FREQ_IN_MINUTES
        else:
          if curr_vol.status == "in-use" and instance_id != curr_vol.attach_data.instance_id:
            print 'Volume %s is used in %s. Detaching...' % (vol_id, curr_vol.attach_data.instance_id)
            volume_detach()
          print 'Attaching %s to this instance.' % vol_id
          volume_attach()
          print 'Mounting volume."'
          if mount():
            volume_status()
            run_script(POST_MOUNT_SCRIPT)
            
  print "Waiting ", next_iter_in_minutes, " minutes for the next iteration."
  # Flush the buffers
  sys.stdout.flush()
  sys.stderr.flush()
  # Wait for next turn
  time.sleep( next_iter_in_minutes * 60)
