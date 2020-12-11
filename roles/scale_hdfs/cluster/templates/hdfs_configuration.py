#!/usr/bin/env python3
# =================================================================
# Licensed Materials - Property of IBM
#
# "Restricted Materials of IBM"
#
# (C) COPYRIGHT IBM Corp. 2020   All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

def hdfs_configurations():
    """
      This function will modify/add configuration required to start/enable ces
      core-site.xml
      hdfs-site.xml
      gpfs-site.xml
    """
    t_cluster_name = {{ scale_hdfs_hdfs_cluster }}
    nn = get_namenodes_serviceID(t_cluster_name)
    nameserviceID = t_cluster_name
    namenodes = {{ scale_hdfs_namenodes_list }}
    datanodes = {{ scale_hdfs_datanodes_list }}
    fs = {{ scale_hdfs_filesystem }}
    mount_point = {{ mountpoint }}
    datadir = {{ scale_hdfs_datadir }}

    if check_ha_enabled(t_cluster_name):
        hdfs_site_conf_dict = {
            'dfs.nameservices':nameserviceID,
            'dfs.ha.namenodes.' + nameserviceID:nn,
            'dfs.namenode.shared.edits.dir':'file:///' + mount_point + '/HA-' + nameserviceID,
            'dfs.namenode.rpc-bind-host':'0.0.0.0',
            'dfs.namenode.servicerpc-bind-host':'0.0.0.0',
            'dfs.namenode.lifeline.rpc-bind-host':'0.0.0.0',
            'dfs.namenode.http-bind-host':'0.0.0.0',
            'dfs.client.failover.proxy.provider.' + nameserviceID:'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'
        }
    else:
        hdfs_site_conf_dict = {
            'dfs.nameservices':nameserviceID,
            'dfs.ha.namenodes.' + nameserviceID:nn,
            'dfs.namenode.rpc-bind-host':'0.0.0.0',
            'dfs.namenode.servicerpc-bind-host':'0.0.0.0',
            'dfs.namenode.lifeline.rpc-bind-host':'0.0.0.0',
            'dfs.namenode.http-bind-host':'0.0.0.0',
            'dfs.client.failover.proxy.provider.' + nameserviceID:'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider'
        }
    core_site_conf_dict = {
       "fs.defaultFS":"hdfs://" + nameserviceID,
       "hadoop.proxyuser.livy.hosts":"*",
       "hadoop.proxyuser.livy.groups":"*",
       "hadoop.proxyuser.hive.hosts":"*",
       "hadoop.proxyuser.hive.groups":"*",
       "hadoop.proxyuser.oozie.hosts":"*",
       "hadoop.proxyuser.oozie.groups":"*"
    }

    gpfs_site_conf_dict = {
       "gpfs.mnt.dir":mount_point,
       "gpfs.data.dir":datadir
    }

    hdfs_nodes = namenodes + datanodes
    for node in hdfs_nodes:
       key = "JAVA_HOME"
       value = get_openjdk_devel_path(node)
       edit_hdfs_configurations(t_cluster_name, "hadoop-env.sh", key, value, node)

       for nnname, namenode in zip(nn.split(","), namenodes):
           namenode = str(namenode.fqdn).strip()
           key = 'dfs.namenode.rpc-address.' + nameserviceID + '.' + nnname
           value = namenode + ":8020"
           trace("key:{0},value:{1}".format(key, value))
           edit_hdfs_configurations(t_cluster_name, "hdfs-site.xml", key, value, node)
           key = 'dfs.namenode.http-address.' + nameserviceID + '.' + nnname
           value = namenode + ":50070"
           trace("key:{0},value:{1}".format(key, value))
           edit_hdfs_configurations(t_cluster_name, "hdfs-site.xml", key, value, node)

       for key, value in list(hdfs_site_conf_dict.items()):
           trace("key:{0},value:{1}".format(key, value))
           edit_hdfs_configurations(t_cluster_name, "hdfs-site.xml", key, value, node)

       for key, value in list(core_site_conf_dict.items()):
           trace("key:{0},value:{1}".format(key, value))
           edit_hdfs_configurations(t_cluster_name, "core-site.xml", key, value, node)

       for key, value in list(gpfs_site_conf_dict.items()):
           trace("key:{0},value:{1}".format(key, value))
           edit_hdfs_configurations(t_cluster_name, "gpfs-site.xml", key, value, node)

def add_datanodes():
    """
      This function will be responsible for adding datanodes
      mmhdfs worker add/remove [dn1,dn2,...dnN]
      should be run on namenode
    """
    t_cluster_name = {{ scale_hdfs_hdfs_cluster }}
    WORKER_FILE = HADOOP_DIR + "workers"
    namenodes = {{ scale_hdfs_namenodes_list }}
    datanodes = {{ scale_hdfs_datanodes_list }}
    for nn in namenodes:
        # To make sure worker file is empty
        cmd = "rm -rf " + WORKER_FILE + "; touch " + WORKER_FILE
        # Removing localhost from worker file(if any)
        trace("cmd:{0} on {1} node".format(cmd, nn.fqdn))
        retcode1 = get_return_code_from_node(nn, [cmd])
        trace("return code:{0}".format(retcode1))
        if retcode1 != 0:
            raise FriendlyError("Failed to cleanup workers configuration file", nn.fqdn)
        for dn in get_datanodes:
            add_command = HDFS_SBIN + "mmhdfs worker add " + dn.fqdn
            trace("add_command:{0}", add_command)
            retcode2 = get_return_code_from_node(nn, [add_command])
            if retcode2 != 0:
               raise FriendlyError("Failed to assigned {0} node as worker nodes", dn.fqdn)
            else:
               trace("{0} node has been assigned as worker nodes", dn.fqdn)
            # run_command_on_node(nn,[remove_command])


if __name__ == '__main__':
    hdfs_configurations()