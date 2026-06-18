# scale_firewall_config

## Role Definition

**Role Name:** `scale_firewall_config`

### Description
The `scale_firewall_config` Ansible role provides automated, validated firewall configuration for cluster and distributed system environments using **firewalld**.

This role ensures that:
- `firewalld` is installed and enabled  
- Firewall state is inspected before changes  
- Required ports are validated  
- Declared ports are opened permanently  
- Firewall configuration is reloaded  
- Post-change validation is performed  
- Execution fails safely if mandatory ports are not present  

It enforces **declarative firewall configuration with validation**, making it suitable for production, cluster, and enterprise infrastructure environments.

---

## Features

- Automatic installation of `firewalld`
- Service enablement and startup
- Pre-configuration inspection
- Dynamic extraction of open ports
- Required-port validation
- Declarative port configuration
- Permanent firewall rules
- Automatic reload handling
- Post-configuration verification
- Fail safe enforcement model
- Debug logging at every stage

---

## Prerequisites

### Access
- Root or sudo access on target nodes

### Ansible Requirements
- `yum` module  
- `firewalld` module  

---

## Configuration

### Firewall Configuration (`group_vars/all.yml`)
**firewall**: ports that Ansible will configure
```yaml
firewall: 
 - { port: 80, protocol: tcp }
 - { port: 22, protocol: tcp }
 - { port: 443, protocol: tcp }
```

**required_ports**: ports that must exist for the system to be considered valid
```yaml
required_ports:
  - { port: 80, protocol: tcp }
  - { port: 443, protocol: tcp }
  - { port: 22, protocol: tcp }
```

This separation enables policy enforcement independent of configuration logic.

### Role Structure

```text
roles/scale_firewall_config/
├── tasks/
│   └── main.yml
├── defaults/
│   └── main.yml
├── handlers/
│   └── main.yml
├── group_vars/
│   └── all.yml
├── tests/
│   ├── inventory.yml
│   └── playbook.yml
└── README.md
```



## Workflow Design

### 1. Installation Phase
- Installs firewalld
- Enables and starts the service

### 2. Precheck Phase
- Reads current firewall configuration
- Extracts open ports dynamically

### 3. Validation Phase
- Compares open ports with `required_ports`
- Identifies missing ports

### 4. Configuration Phase
- Opens all ports defined in `firewall`
- Applies permanent firewall rules

### 5. Reload Phase
- Reloads firewalld configuration

### 6. Postcheck Phase
- Re-reads firewall state
- Verifies open ports

### 7. Safety Enforcement
- Execution fails if required ports are still missing
- Prevents silent misconfiguration


## Testing

This role includes a test setup to validate firewall configuration across multiple cluster nodes.

### Inventory (`tests/inventory.yml`)
The inventory file defines the target cluster hosts and their access details.  
```yaml
[cluster01]
scale01 ansible_host=<ip> ansible_user=root
scale02 ansible_host=<ip> ansible_user=root
```

### Playbook (`tests/playbook.yml`)
The playbook applies the `scale_firewall_config` role on the cluster group and executes the full firewall automation workflow, including installation, validation, configuration, reload, and verification.

```yaml
name: Configure firewall ports on scale cluster nodes
hosts: cluster01
become: yes
roles:
    - scale_firewall_config
```
