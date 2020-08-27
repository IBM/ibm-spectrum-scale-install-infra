NTP
-------------------
- The Network Time Protocol (NTP) is a networking protocol for clock synchronization between computer systems over packet-switched, variable-latency data networks.
- NTP is intended to synchronize all participating computers to within a few milliseconds of Coordinated Universal Time (UTC). NTP can usually maintain time to within tens of milliseconds over the public Internet, and can achieve better than one millisecond accuracy in local area networks under ideal conditions.

Role Variables
--------------
- ntp_server variable should be defined in defaults/main.yml . If a ntp server is not specified, ant node from the existing cluster will be set as ntp server.

Implementation
------------

The role is divided into 4 separate roles:
- precheck: Checks if a ntp server is defined or not. If not defined, then the toolkit automatically selects the first node in the cluster as ntp server.
- node: Install ntp or chrony depending on the os version.
- cluster: Configure ntp or chrony on every node to sync with given server.
- postcheck: Checks if ntp/chrony is running and also checks if all the nodes are synchronizing with the ntp server.  

Example Playbook
----------------

To use this role, add following lines of code to your playbook:

    - hosts: servers
      roles:
         - ntp/precheck
         - ntp/node
         - ntp/cluster
         - ntp/postcheck

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
