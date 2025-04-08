import openstack
import docker
import time

# Import functions from your modules.
# Note: Adjust these imports if your functions are under different names.
from create_network import create_network as create_os_network
from create_vm import create_vm as create_os_vm
from setup_security_group import setup_security_group, apply_security_group_to_vm
from frr_router import create_router, configure_bgp as configure_bgp_router
from sdn_controller import create_controller, configure_bgp as configure_bgp_controller

def main():
    # ----- OpenStack Part -----
    # Connect using OpenStack environment (source admin-openrc.sh before running)
    os_conn = openstack.connect()
    
    # Create two networks
    print("Creating networks on OpenStack...")
    net10, sub10, router, intf10 = create_os_network(
        os_conn,
        network_name="network_10",
        subnet_name="subnet_10",
        cidr="10.0.0.0/24",
        gateway_ip="10.0.0.1",
        router_name="shared_router",
        external_network_name="public"
    )
    net20, sub20, router, intf20 = create_os_network(
        os_conn,
        network_name="network_20",
        subnet_name="subnet_20",
        cidr="20.0.0.0/24",
        gateway_ip="20.0.0.1",
        router_name="shared_router",
        external_network_name="public"
    )
    
    # Create two VMs
    print("Creating VMs on OpenStack...")
    create_os_vm(
        os_conn,
        server_name="vm11",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.tiny",
        network_name="network_10"
    )
    create_os_vm(
        os_conn,
        server_name="vm22",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.tiny",
        network_name="network_20"
    )
    
    # Set up and apply security group to the VMs
    sg_name = "custom_sg"
    print("Setting up security group...")
    setup_security_group(os_conn, sg_name)
    for vm in ["vm11", "vm22"]:
        apply_security_group_to_vm(os_conn, vm, sg_name)
    
    # ----- BGP (Docker) Part -----
    # Create a Docker client.
    docker_client = docker.from_env()
    
    # Create a Docker network for BGP containers with subnet 10.0.0.0/24.
    bgp_net_name = "bgp_net"
    try:
        bgp_net = docker_client.networks.get(bgp_net_name)
        print(f"Network '{bgp_net_name}' already exists.")
    except docker.errors.NotFound:
        ipam_pool = docker.types.IPAMPool(subnet="10.0.0.0/24", gateway="10.0.0.1")
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        bgp_net = docker_client.networks.create(bgp_net_name, driver="bridge", ipam=ipam_config)
        print(f"Created Docker network '{bgp_net_name}'.")
    
    # Create the FRR router container (AS 1, router-id 1.1.1.1)
    print("Creating FRR router container...")
    router_container = create_router(docker_client, network_name=bgp_net_name)
    
    # Create the SDN controller container (AS 2, router-id 2.2.2.2)
    print("Creating SDN controller container...")
    controller_container = create_controller(docker_client, network_name=bgp_net_name)
    
    # Reload containers to get updated network info.
    router_container.reload()
    controller_container.reload()
    ip_router = router_container.attrs["NetworkSettings"]["Networks"][bgp_net_name]["IPAddress"]
    ip_controller = controller_container.attrs["NetworkSettings"]["Networks"][bgp_net_name]["IPAddress"]
    
    print("------------")
    print(f"FRR Router container IP: {ip_router}")
    print(f"SDN Controller container IP: {ip_controller}")
    print("------------")
    
    # Configure BGP peering.
    print("Configuring BGP peering...")
    configure_bgp_router(router_container, local_as=1, router_id="1.1.1.1", neighbor_ip=ip_controller, remote_as=2)
    configure_bgp_controller(controller_container, local_as=2, router_id="2.2.2.2", neighbor_ip=ip_router, remote_as=1)
    
    # Allow time for the BGP session to establish.
    print("Waiting for BGP sessions to establish...")
    time.sleep(10)
    
    # Display BGP summaries from both containers.
    summary_router = router_container.exec_run('vtysh -c "show ip bgp summary"', user="root").output.decode()
    summary_controller = controller_container.exec_run('vtysh -c "show ip bgp summary"', user="root").output.decode()
    print("------------")
    print("BGP summary for FRR Router container:")
    print(summary_router)
    print("------------")
    print("BGP summary for SDN Controller container:")
    print(summary_controller)
    print("------------")
    print("Deployment complete. OpenStack networks, VMs, security groups, and BGP containers are all set up.")

if __name__ == "__main__":
    main()

