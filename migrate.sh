#!/bin/bash

# Replaces old role names with new role names in any text file

usage () {
  echo "Usage: $0 filename"
  exit 1
}

[ "$#" -eq 1 ] || usage
[ -r "$1" ] || usage

cp ${1} ${1}.bak

sed -i '
s,callhome/cluster,callhome_configure,g
s,callhome/node,callhome_install,g
s,callhome/postcheck,callhome_verify,g
s,callhome/precheck,callhome_prepare,g
s,core/cluster,core_configure,g
s,core/common,core_common,g
s,core/node,core_install,g
s,core/postcheck,core_verify,g
s,core/precheck,core_prepare,g
s,core/upgrade,core_upgrade,g
s,gui/cluster,gui_configure,g
s,gui/node,gui_install,g
s,gui/postcheck,gui_verify,g
s,gui/precheck,gui_prepare,g
s,gui/upgrade,gui_upgrade,g
s,nfs/cluster,nfs_configure,g
s,nfs/common,ces_common,g
s,nfs/node,nfs_install,g
s,nfs/postcheck,nfs_verify,g
s,nfs/precheck,nfs_prepare,g
s,nfs/upgrade,nfs_upgrade,g
s,remote_mount/,remotemount_configure,g
s,scale_auth/upgrade,auth_upgrade,g
s,scale_ece/cluster,ece_configure,g
s,scale_ece/node,ece_install,g
s,scale_ece/precheck,ece_prepare,g
s,scale_ece/upgrade,ece_upgrade,g
s,scale_fileauditlogging/cluster,fal_configure,g
s,scale_fileauditlogging/node,fal_install,g
s,scale_fileauditlogging/postcheck,fal_verify,g
s,scale_fileauditlogging/precheck,fal_prepare,g
s,scale_fileauditlogging/upgrade,fal_upgrade,g
s,scale_hdfs/cluster,hdfs_configure,g
s,scale_hdfs/node,hdfs_install,g
s,scale_hdfs/postcheck,hdfs_verify,g
s,scale_hdfs/precheck,hdfs_prepare,g
s,scale_hdfs/upgrade,hdfs_upgrade,g
s,scale_hpt/node,afm_cos_install,g
s,scale_hpt/postcheck,afm_cos_verify,g
s,scale_hpt/precheck,afm_cos_prepare,g
s,scale_hpt/upgrade,afm_cos_upgrade,g
s,scale_object/cluster,obj_configure,g
s,scale_object/node,obj_install,g
s,scale_object/postcheck,obj_verify,g
s,scale_object/precheck,obj_prepare,g
s,scale_object/upgrade,obj_upgrade,g
s,smb/cluster,smb_configure,g
s,smb/node,smb_install,g
s,smb/postcheck,smb_verify,g
s,smb/precheck,smb_prepare,g
s,smb/upgrade,smb_upgrade,g
s,zimon/cluster,perfmon_configure,g
s,zimon/node,perfmon_install,g
s,zimon/postcheck,perfmon_verify,g
s,zimon/precheck,perfmon_prepare,g
s,zimon/upgrade,perfmon_upgrade,g
' $1

exit 0
