IBM Spectrum Scale Bridge for Grafana Ansible Role
=================================================

Highly-customizable Ansible role for installing & configuring IBM Spectrum Scale Bridge for Grafana, enabling performance metrics visualization through Grafana dashboards. 


Features
--------

- **Install Grafana Bridge**
- **Support for Python 3.8 or above environments**
- **Install via YUM repo or local RPMs**
- **Systemd service management for Grafana Bridge**
- **Customizable log file paths**
- **Modular role design for install, configure, and verify steps**

The following installation methods are available:
- **Install from existing YUM repository**
- **Install from local RPM package**


Future plans:
- **Automated certificate handling for HTTPS endpoints.**
- **Enhanced metrics filtering**


Installation
------
Installation

```
$ ansible-playbook -i hosts playbook_grafana_bridge.yml
```


Requirements
-------------

Public repository available, you'll need to download it from here https://github.com/IBM/ibm-spectrum-scale-bridge-for-grafana 
