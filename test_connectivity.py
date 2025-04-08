import openstack
import paramiko

def get_server_floating_ip(conn, server_name):
    """
    Retrieve the floating IP address for the server with the given name.
    """
    server = conn.compute.find_server(server_name)
    if not server:
        print(f"Server '{server_name}' not found.")
        return None
    
    # The addresses are stored in a dictionary by network name.
    # Look for an address that is marked as floating.
    for net, addresses in server.addresses.items():
        for addr in addresses:
            # OpenStack SDK typically sets 'OS-EXT-IPS:type' to 'floating' for floating IPs.
            if addr.get("OS-EXT-IPS:type", "").lower() == "floating":
                return addr.get("addr")
    return None

def get_server_private_ip(conn, server_name):
    """
    Retrieve the fixed (private) IP address for the server with the given name.
    """
    server = conn.compute.find_server(server_name)
    if not server:
        print(f"Server '{server_name}' not found.")
        return None
    
    for net, addresses in server.addresses.items():
        for addr in addresses:
            if addr.get("OS-EXT-IPS:type", "").lower() == "fixed":
                return addr.get("addr")
    return None

def ssh_and_ping(ssh_hostname, ssh_username, ssh_password, target_ip):
    """
    SSH into a host and run a ping command to the target IP.
    Returns the command output.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ssh_hostname, username=ssh_username, password=ssh_password)
    except Exception as e:
        return f"SSH connection failed: {e}"
    
    command = f"ping -c 3 {target_ip}"
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode() + stderr.read().decode()
    ssh.close()
    return output

def main():
    # Connect using environment variables (ensure you've sourced your admin-openrc.sh)
    conn = openstack.connect()

    # Retrieve IPs for the two VMs.
    # We assume vm11 has a floating IP and vm22 has a private (fixed) IP.
    vm11_floating = get_server_floating_ip(conn, "vm11")
    vm22_private = get_server_private_ip(conn, "vm22")
    
    if not vm11_floating:
        print("Could not retrieve floating IP for vm11.")
        return
    if not vm22_private:
        print("Could not retrieve private IP for vm22.")
        return

    print("------------")
    print(f"VM11 (source) Floating IP: {vm11_floating}")
    print(f"VM22 (destination) Private IP: {vm22_private}")
    print("------------")

    # SSH credentials for the source VM. Adjust these if your image uses different credentials.
    ssh_username = "cirros"
    ssh_password = "gocubsgo"

    print("Pinging from vm11 to vm22...")
    ping_result = ssh_and_ping(vm11_floating, ssh_username, ssh_password, vm22_private)
    print("------------")
    print("Ping output:")
    print(ping_result)
    print("------------")

if __name__ == "__main__":
    main()

