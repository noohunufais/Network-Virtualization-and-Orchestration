import openstack

def create_vm(conn, server_name, image_name, flavor_name, network_name, external_network_name="public"):
    """
    Create a virtual machine (server) in OpenStack, assign a floating IP using the specified
    method, and print the server details.

    Parameters:
      conn (openstack.connection.Connection): Authenticated OpenStack connection.
      server_name (str): The name to assign to the new VM.
      image_name (str): Name of the image to use (e.g., "cirros-0.6.3-x86_64-disk").
      flavor_name (str): Name of the flavor to use (e.g., "m1.tiny").
      network_name (str): Name of the network the VM will connect to.
      external_network_name (str): Name of the external network to get a floating IP from.
    """
    # Locate the image, flavor, and network by their names.
    image = conn.compute.find_image(image_name)
    if not image:
        raise Exception(f"Image '{image_name}' not found.")

    flavor = conn.compute.find_flavor(flavor_name)
    if not flavor:
        raise Exception(f"Flavor '{flavor_name}' not found.")

    network = conn.network.find_network(network_name)
    if not network:
        raise Exception(f"Network '{network_name}' not found.")

    # Create the server instance.
    server = conn.compute.create_server(
        name=server_name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
    )
    
    # Wait for the server to become active.
    server = conn.compute.wait_for_server(server)
    
    # Associate a floating IP using the provided snippet.
    external_net = conn.network.find_network(external_network_name)
    if not external_net:
        raise Exception(f"External network '{external_network_name}' not found")
    
    # Create a floating IP on the external network.
    floating_ip = conn.network.create_ip(floating_network_id=external_net.id)
    
    # Retrieve the server port(s).
    ports = list(conn.network.ports(device_id=server.id))
    if not ports:
        raise Exception(f"No port found for server '{server.id}'")
    
    # Associate the floating IP with the first port.
    conn.network.update_ip(floating_ip, port_id=ports[0].id)
    
    # Print server details.
    print("Server created successfully:")
    print(f"Name: {server.name}")
    print(f"ID: {server.id}")
    print(f"Status: {server.status}")
    print(f"Networks: {server.addresses}")
    print(f"Floating IP: {floating_ip.floating_ip_address}")
    print("-" * 60)

if __name__ == '__main__':
    # Connect using environment variables (ensure you've sourced your admin-openrc.sh)
    conn = openstack.connect()

    # Create the first VM on network_10 (single tenant, same VN).
    create_vm(
        conn,
        server_name="vm11",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.tiny",      # Update with a valid flavor in your environment.
        network_name="network_10"    # VM attached to network_10.
    )

    # Create the second VM on network_20 (multi-tenant, different VN).
    create_vm(
        conn,
        server_name="vm22",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.tiny",      # Update with a valid flavor in your environment.
        network_name="network_20"    # VM attached to network_20.
    )

