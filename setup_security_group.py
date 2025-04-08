import openstack

def setup_security_group(conn, sg_name):
    """
    Create a security group with rules to allow:
      - ICMP (ping)
      - All TCP traffic

    Both rules allow traffic from any source.
    """
    sg = conn.network.find_security_group(sg_name)
    if not sg:
        sg = conn.network.create_security_group(
            name=sg_name,
            description="Security group for ICMP and TCP"
        )
        print(f"Created security group '{sg_name}' with ID: {sg.id}")
    else:
        print(f"Security group '{sg_name}' already exists with ID: {sg.id}")

    # Add ICMP (ping) rule.
    conn.network.create_security_group_rule(
        security_group_id=sg.id,
        direction="ingress",
        protocol="icmp",
        remote_ip_prefix="0.0.0.0/0"
    )
    print("Added ICMP (ping) rule.")

    # Add TCP rule for all ports.
    conn.network.create_security_group_rule(
        security_group_id=sg.id,
        direction="ingress",
        protocol="tcp",
        port_range_min=1,
        port_range_max=65535,
        remote_ip_prefix="0.0.0.0/0"
    )
    print("Added TCP rule for all ports.")

def apply_security_group_to_vm(conn, vm_name, sg_name):
    """
    Apply an existing security group to an existing VM using the security group object.
    
    Parameters:
      conn (openstack.connection.Connection): Authenticated OpenStack connection.
      vm_name (str): The name of the existing VM.
      sg_name (str): The name of the security group to apply.
    """
    server = conn.compute.find_server(vm_name)
    if not server:
        print(f"Server '{vm_name}' not found.")
        return

    security_group = conn.network.find_security_group(sg_name)
    if not security_group:
        print(f"Security group '{sg_name}' not found.")
        return

    try:
        conn.compute.add_security_group_to_server(server, security_group)
        print(f"Added security group '{sg_name}' to VM '{vm_name}'.")
    except Exception as e:
        print(f"Failed to add security group '{sg_name}' to VM '{vm_name}': {e}")

if __name__ == '__main__':
    # Connect using environment variables (ensure you've sourced your admin-openrc.sh)
    conn = openstack.connect()

    sg_name = "custom_sg"
    setup_security_group(conn, sg_name)

    # List of existing VMs (by name) to which the security group should be applied.
    existing_vm_names = ["vm11", "vm22"]

    for vm in existing_vm_names:
        apply_security_group_to_vm(conn, vm, sg_name)

