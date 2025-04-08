# Virtualized Network Automation – Lab 9

This project automates the creation and configuration of virtual networks, virtual machines, security groups, and BGP routing using OpenStack and Docker.

## Objectives

**1. Create Virtual Networks**  
- Module: `create_network.py`  
  - Automates the creation of multiple virtual networks (VNs) within the hypervisor and connects them to the public network.

**2. Create Virtual Machines**  
- Module: `create_vm.py`  
  - Automates the creation of multiple VMs on single-tenant (same VN) and multi-tenant (different VN) topologies.  
  - Ensures all VMs are accessible from the host server and can access the Internet.

**3. Configure Security Groups**  
- Module: `setup_security_group.py`  
  - Automates the creation of security groups to allow ICMP and TCP traffic.  
  - Applies security groups to VMs to enable intra-VN and inter-VN communication.

**4. Deploy FRR BGP Router**  
- Module: `frr_router.py`  
  - Automates spinning up and configuring a Quagga/FRR BGP router as a Docker container.  
  - Configures BGP to peer with the SDN controller.

**5. Deploy SDN Controller**  
- Module: `sdn_controller.py`  
  - Automates spinning up and configuring an SDN controller as a Docker container.  
  - Configures its BGP speaker to peer with the FRR router.

**6. Test Connectivity**  
- Module: `test_connectivity.py`  
  - Verifies connectivity between VMs by SSH’ing to one VM and pinging another.

**7. Full Automation Orchestration**  
- Module: `main.py`  
  - Executes all the above modules in order:  
    - Creates virtual networks and subnets  
    - Launches VMs with floating IPs  
    - Sets up and applies security groups  
    - Deploys Docker containers for FRR and SDN controller  
    - Configures BGP peering between the containers  
    - Prints BGP session summaries

## Prerequisites

- **Linux Machine** with Python installed.
- **OpenStack** installed and accessible.
- **Docker** installed and running.
- Python packages:
  - `openstacksdk`
  - `docker`
  - `paramiko`
  
Install required packages with:
```bash
pip install openstacksdk docker paramiko
