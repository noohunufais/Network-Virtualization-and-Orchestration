import openstack

def create_network(conn, network_name, subnet_name, cidr, gateway_ip,
                              router_name="shared_router", external_network_name="public"):
    """
    Create a network and a subnet with a specified CIDR and gateway IP, and attach the subnet
    to a router. If the router doesn't exist, create it and set its external gateway.
    
    Parameters:
      conn (openstack.connection.Connection): Authenticated OpenStack connection.
      network_name (str): Name for the new network.
      subnet_name (str): Name for the new subnet.
      cidr (str): CIDR block for the subnet (e.g., "10.0.0.0/24").
      gateway_ip (str): Gateway IP for the subnet (must be within the CIDR).
      router_name (str): Name of the router to attach this network to.
      external_network_name (str): Name of the external network to set as the router's gateway.
    
    Returns:
      tuple: (network, subnet, router, interface) created or used.
    """
    # Create the network
    network = conn.network.create_network(name=network_name)
    print(f"Created network '{network_name}' with ID: {network.id}")

    # Create the subnet with the given CIDR and gateway IP
    subnet = conn.network.create_subnet(
        network_id=network.id,
        name=subnet_name,
        cidr=cidr,
        ip_version="4",
        gateway_ip=gateway_ip
    )
    print(f"Created subnet '{subnet_name}' with CIDR {cidr} and gateway {gateway_ip} (ID: {subnet.id})")

    # Check if the router exists; if not, create it.
    router = conn.network.find_router(router_name)
    if not router:
        router = conn.network.create_router(name=router_name)
        print(f"Created router '{router_name}' with ID: {router.id}")
    else:
        print(f"Found existing router '{router_name}' with ID: {router.id}")

    # Find the external network named "public"
    public_network = conn.network.find_network(external_network_name)
    if not public_network:
        raise Exception(f"External network '{external_network_name}' not found")
    
    # Update the router's external gateway if needed
    if not router.external_gateway_info or router.external_gateway_info.get("network_id") != public_network.id:
        router = conn.network.update_router(router, external_gateway_info={"network_id": public_network.id})
        print(f"Updated router '{router_name}' with external gateway (network '{external_network_name}' ID: {public_network.id})")
    
    # Attach the subnet to the router
    interface = conn.network.add_interface_to_router(router, subnet_id=subnet.id)
    print(f"Attached subnet '{subnet_name}' to router '{router_name}'.")

    return network, subnet, router, interface

# Example usage:
if __name__ == '__main__':
    # Assumes you've sourced your admin-openrc.sh so that environment variables are set.
    conn = openstack.connect()

    # Create the first network: 10.0.0.0/24
    create_network(
        conn,
        network_name="network_10",
        subnet_name="subnet_10",
        cidr="10.0.0.0/24",
        gateway_ip="10.0.0.1",
        router_name="shared_router",  # Router name; reused across networks
        external_network_name="public"
    )

    # Create the second network: 20.0.0.0/24
    create_network(
        conn,
        network_name="network_20",
        subnet_name="subnet_20",
        cidr="20.0.0.0/24",
        gateway_ip="20.0.0.1",
        router_name="shared_router",  # Using the same router to attach both networks
        external_network_name="public"
    )


