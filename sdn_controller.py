import docker
import time

def create_container(client, container_name, network_name):
    """
    Create a Debian container in privileged mode with a persistent process.
    """
    try:
        container = client.containers.get(container_name)
        print(f"Container '{container_name}' already exists. Removing...")
        container.remove(force=True)
    except docker.errors.NotFound:
        pass

    print(f"Creating container '{container_name}'...")
    container = client.containers.run(
        "debian:latest",
        name=container_name,
        detach=True,
        tty=True,
        privileged=True,
        network=network_name,
        command="tail -f /dev/null"
    )
    time.sleep(3)
    return container

def install_and_configure_frr(container):
    """
    Install FRR using apt, enable bgpd in the daemons file, and start bgpd.
    """
    print(f"Installing FRR in container '{container.name}'...")
    container.exec_run("apt update", user="root")
    container.exec_run("apt install -y frr", user="root")
    
    print(f"Configuring FRR daemons in container '{container.name}'...")
    sed_cmd = r"sed -i 's/bgpd=no/bgpd=yes/g' /etc/frr/daemons"
    container.exec_run(sed_cmd, user="root")
    
    print(f"Starting bgpd in container '{container.name}'...")
    container.exec_run("/usr/lib/frr/bgpd -d", user="root")
    time.sleep(3)

def configure_bgp(container, local_as, router_id, neighbor_ip, remote_as):
    """
    Configure BGP via vtysh.
    Sends BGP configuration commands, then issues 'end' and 'write memory'.
    """
    print(f"Configuring BGP in container '{container.name}'...")
    bgp_config = (
        f"configure terminal\n"
        f"router bgp {local_as}\n"
        f"bgp router-id {router_id}\n"
        f"neighbor {neighbor_ip} remote-as {remote_as}\n"
        f"end\n"
        f"write memory\n"
    )
    config_cmd = f"vtysh -c \"{bgp_config}\""
    result = container.exec_run(config_cmd, user="root")
    print(result.output.decode())

def create_controller(client, network_name):
    """
    Create and configure the SDN controller container.
    Uses local AS 2 and router-id 2.2.2.2.
    """
    container = create_container(client, "sdn_controller", network_name)
    install_and_configure_frr(container)
    return container

