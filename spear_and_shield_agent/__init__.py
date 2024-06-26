from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import platform
import subprocess
from pyroute2 import IPRoute

transport = AIOHTTPTransport(url="https://spearandshield.ubnetdef.org/graphql")

client = Client(transport=transport, fetch_schema_from_transport=True)

def get_ip_address():
    query = gql(
    """
    query MyQuery {
      hello
    }
    """
    )

    # result = client.execute(query)
    result = "192.168.0.1" # HACK: Figure this out later
    return result

def configure_ip() -> bytes:
    '''
    Returns the stdout of the system command response
    '''

    ipAddress = get_ip_address()

    platformString = platform.system()
    if platformString == "Linux": # TODO: Needs testing
        INTERFACE = "ens160"
        ip = IPRoute()
        index = ip.link_lookup(ifname=INTERFACE)[0]  # FIXME: Add error handling here if assumption about interface name is wrong
        ip.addr('add', index, address=ipAddress, mask=24)
        ip.close()
    elif platformString == "Windows": # TODO: Needs testing
        cmd = f"netsh interface ip set address lan static {ipAddress} 255.255.255.0"
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        return completed.stdout
    else:
        raise Exception(f"Unsupported operating system {platformString}")

def configure_vm():
    configure_ip()