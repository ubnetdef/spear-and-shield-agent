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

    platformString = platform.system()
    
    if platformString == "Linux":
        ipAddress = get_ip_address()
        INTERFACE = "ens160"
        cmd = f"ip addr add {ipAddress}/24 dev {INTERFACE}" # TODO: Figure out how to set IPs in Linux
        completed = subprocess.run(["bash", "-c", cmd], capture_output=True)
        return completed.stdout
    elif platformString == "Windows":
        cmd = "whoami" # TODO: Figure out how to set IPs in Windows
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        return completed.stdout
    else:
        raise Exception(f"Unsupported operating system {platformString}")

def configure_vm():
    configure_ip()