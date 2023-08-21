**What is MROT??**

IBM Storage Scale 5.1.5 introduces the Multi-Rail over TCP (MROT) feature. This feature enables the concurrent use of multiple subnets to communicate with a specified destination, and now allows the concurrent use of multiple physical network interfaces without requiring bonding to be configured.

As per this MROT configuration code MROT can be configured when both storage and compute cluster VSI has two vNICs up and running. 
For Compute cluster primary interface should be in compute cluster subnet and secondary interface should be in storage cluster subnet.
For Storage cluster both interfaces should be in storage cluster subnet.

**Note:** Using this mrot configuration code only M*N connection model can be configured. In this case for compute cluster scale got installed on secondary interface and for storage cluster scale got installed on primary interface.

For more information, see https://www.ibm.com/docs/en/storage-scale/5.1.7?topic=configuring-multi-rail-over-tcp-mrot

**How to check MROT and Logical subnet got configure??**

To check if MROT and logical subnet got configured we can use mmdiag --network  and mmlsconfig command. 
For more information, see below
https://www.ibm.com/docs/en/storage-scale/5.0.5?topic=reference-mmdiag-command
https://www.ibm.com/docs/en/storage-scale/5.0.4?topic=reference-mmlsconfig-command

**Example - mmdiag --network for the Compute Cluster**

Logical subnet can be seen under my addr list. In below result under hostname and idx destination hostnames of nodes and destination IPs can be found.

For compute cluster: scale is getting configured only on secondary IPs hence only secondary IPs can be seen in result.Individually for each nodes, Details can be found under Connection details and IpPair Table will show source ip and destination ip.
```
[root@scale-cluster-compute-1 ~]# mmdiag --network

=== mmdiag: network ===

Pending messages:
  (none)
Inter-node communication configuration:
  tscConnMode     mrot
  tscTcpPort      1191
  my address      10.241.1.22/24 (eth1) <c0n0>
  my addr list    10.241.1.22/24 (eth1)/scale-cluster.compscale.com;scale-cluster.strgscale.com
  my subnet list  10.241.1.0/24
  my node number  1
TCP Connections between nodes:
    hostname                            node     idx destination     status     err  sock  sent(MB)  recvd(MB)  ostype
    scale-cluster-compute-3-sec         <c0n1>     0 10.241.1.21     connected  0    124   0         0          Linux/L
    scale-cluster-compute-3-sec         <c0n1>     1 10.241.1.21     connected  0    127   0         0          Linux/L
    scale-cluster-compute-2-sec         <c0n2>     0 10.241.1.19     connected  0    125   0         0          Linux/L
    scale-cluster-compute-2-sec         <c0n2>     1 10.241.1.19     connected  0    128   0         0          Linux/L
    scale-cluster-compute-4-sec         <c0n3>     0 10.241.1.20     connected  0    126   0         0          Linux/L
    scale-cluster-compute-4-sec         <c0n3>     1 10.241.1.20     connected  0    108   0         0          Linux/L
    scale-cluster-storage-1             <c1n0>     0 10.241.1.26     connected  0    134   0         0          Linux/L
    scale-cluster-storage-1             <c1n0>     1 10.241.1.23     connected  0    135   0         0          Linux/L
    scale-cluster-storage-3             <c1n1>     0 10.241.1.24     connected  0    137   0         0          Linux/L
    scale-cluster-storage-3             <c1n1>     1 10.241.1.25     connected  0    138   0         0          Linux/L
    scale-cluster-storage-2             <c1n2>     0 10.241.1.30     connected  0    136   0         0          Linux/L
    scale-cluster-storage-2             <c1n2>     1 10.241.1.27     connected  0    140   0         0          Linux/L
    scale-cluster-storage-4             <c1n3>     0 10.241.1.29     connected  0    133   0         0          Linux/L
    scale-cluster-storage-4             <c1n3>     1 10.241.1.28     connected  0    117   0         0          Linux/L
Connection details:
  <c0n1> 10.241.1.21/0 (scale-cluster-compute-3-sec)
    status connected was_broken 0 err 0 reconnEnabled 1 delayedAckEnabled 1
    connMode mrot shutting 0 handlerCount 0 need_notify 0 leaseSentOn 1
    nMaxTcpConns 2 (2) nActiveCount 2 nActiveState 0x3 (1100000000000000)
    nInuseTcpConns 0 currTcpConnIndex 0 availableTcpConns (1111111111111111)
    nReservedSmallMsgTcpConns 0 currSmallMsgTcpConnIndex 0 currLargeMsgTcpConnIndex 0
    reconnectTcpConns (0000000000000000) disconnectTcpConns (0000000000000000)
    Inuse owner:
      [ 0]:0          [ 1]:0          [ 2]:0          [ 3]:0        
      [ 4]:0          [ 5]:0          [ 6]:0          [ 7]:0        
      [ 8]:0          [ 9]:0          [10]:0          [11]:0        
      [12]:0          [13]:0          [14]:0          [15]:0        

    IpPair Table (offset 0 [555/0/1]):
      idx iface           status ping_cnt source          destination     subnet
        0 eth1                up        0 10.241.1.22     10.241.1.21     10.241.1.0/24
```
**Example of mmlsconfig for Compute cluster**

In the mmlsconfig output, the subnets parameter is found in list of configuration parameters.
```
subnets 10.241.1.0/scale-cluster.compscale.com;scale-cluster.strgscale.com
```

**Example - mmdiag --network for Storage cluster**

Logical subnet can be seen under my addr list.In below result under hostname and idx destination, hostnames of nodes and destination IPs can be found.

For Storage cluster: scale is getting configured only on both IPs hence primary and secondary IPs can be seen in the result.Individually for each nodes, Details can be found under Connection details and IpPair Table will show source ip and destination ip.

```
[root@scale-cluster-storage-1 ~]# mmdiag --network

=== mmdiag: network ===

Pending messages:
  (none)
Inter-node communication configuration:
  tscConnMode     mrot
  tscTcpPort      1191
  my address      10.241.1.23/24 (eth0) <c0n0>
  my addr list    10.241.1.23/24 (eth0)/scale-cluster.strgscale.com;scale-cluster.compscale.com  10.241.1.26/24 (eth1)/scale-cluster.strgscale.com;scale-cluster.compscale.com
  my subnet list  10.241.1.0/24
  my node number  1
TCP Connections between nodes:
    hostname                            node     idx destination     status     err  sock  sent(MB)  recvd(MB)  ostype
    scale-cluster-storage-3             <c0n1>     0 10.241.1.25     connected  0    126   0         0          Linux/L
    scale-cluster-storage-3             <c0n1>     1 10.241.1.24     connected  0    130   0         0          Linux/L
    scale-cluster-storage-2             <c0n2>     0 10.241.1.27     connected  0    127   0         0          Linux/L
    scale-cluster-storage-2             <c0n2>     1 10.241.1.30     connected  0    131   0         0          Linux/L
    scale-cluster-storage-4             <c0n3>     0 10.241.1.28     connected  0    124   0         0          Linux/L
    scale-cluster-storage-4             <c0n3>     1 10.241.1.29     connected  0    133   0         0          Linux/L
    scale-cluster-compute-1-sec         <c0n4>     0 10.241.1.22     connected  0    128   0         0          Linux/L
    scale-cluster-compute-1-sec         <c0n4>     1 10.241.1.22     connected  0    137   0         0          Linux/L
    scale-cluster-compute-4-sec         <c0n5>     0 10.241.1.20     connected  0    138   0         0          Linux/L
    scale-cluster-compute-4-sec         <c0n5>     1 10.241.1.20     connected  0    141   0         0          Linux/L
    scale-cluster-compute-3-sec         <c0n6>     0 10.241.1.21     connected  0    139   0         0          Linux/L
    scale-cluster-compute-3-sec         <c0n6>     1 10.241.1.21     connected  0    143   0         0          Linux/L
    scale-cluster-compute-2-sec         <c0n7>     0 10.241.1.19     connected  0    140   0         0          Linux/L
    scale-cluster-compute-2-sec         <c0n7>     1 10.241.1.19     connected  0    142   0         0          Linux/L
Connection details:
  <c0n1> 10.241.1.24/0 (scale-cluster-storage-3)
    status connected was_broken 0 err 0 reconnEnabled 1 delayedAckEnabled 1
    connMode mrot shutting 0 handlerCount 0 need_notify 0 leaseSentOn 1
    nMaxTcpConns 2 (2) nActiveCount 2 nActiveState 0x3 (1100000000000000)
    nInuseTcpConns 0 currTcpConnIndex 1 availableTcpConns (1111111111111111)
    nReservedSmallMsgTcpConns 0 currSmallMsgTcpConnIndex 0 currLargeMsgTcpConnIndex 0
    reconnectTcpConns (0000000000000000) disconnectTcpConns (0000000000000000)
    Inuse owner:
      [ 0]:0          [ 1]:0          [ 2]:0          [ 3]:0        
      [ 4]:0          [ 5]:0          [ 6]:0          [ 7]:0        
      [ 8]:0          [ 9]:0          [10]:0          [11]:0        
      [12]:0          [13]:0          [14]:0          [15]:0        

    IpPair Table (offset 1 [559/0/2]):
      idx iface           status ping_cnt source          destination     subnet
        0 eth0                up        0 10.241.1.23     10.241.1.24     10.241.1.0/24
        1 eth1                up        0 10.241.1.26     10.241.1.25     10.241.1.0/24

```
**Example - mmlsconfig Storage cluster**

In the mmlsconfig output, the subnets parameter is found in list of configuration parameters.

```subnets 10.241.1.0/scale-cluster.strgscale.com;scale-cluster.compscale.com
```

