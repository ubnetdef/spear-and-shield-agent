from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import platform
import subprocess
import logging

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

def get_linux_first_default_adpater() -> str:
    import netifaces
    gws=netifaces.gateways()
    defaultAdapterDict = gws['default']
    firstKey = list(gws['default'].keys())[0]
    adapterInfo = defaultAdapterDict[firstKey]
    adapterName = adapterInfo[1]
    return adapterName

def get_linux_adapter_index(adapterName: str) -> int:
    from pyroute2 import IPRoute
    ip = IPRoute()
    adapterInfo = ip.get_addr(label=adapterName)
    adapterIndex = adapterInfo[0]['index']

def configure_ip() -> bytes:
    '''
    Returns the stdout of the system command response
    '''

    ipAddress = get_ip_address()

    platformString = platform.system()
    if platformString == "Linux":
        from pyroute2 import IPRoute
        try:
            ip = IPRoute()
            adapterName = get_linux_first_default_adpater()
            adapterIndex = get_linux_adapter_index(adapterName)
            adapterInfo = ip.get_addr(label=adapterName)
            ip.addr('add', adapterIndex, address=ipAddress, mask=24)
            ip.close()
        except IndexError:
            logging.error("Couldn't assign IP on Linux system, agent assumes ens160 is name of adapter to be configured")
            raise Exception("Error when assigning IP to Linux system, system assumes ens160 is name of adapter")
        except Exception as e:
            logging.error("Couldn't assign IP on Linux system")
            raise e
    elif platformString == "Windows":
        cmd = f"netsh interface ip set address name=\"Ethernet\" static {ipAddress} 255.255.255.0"
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)

        commandResponse = completed.stdout.decode()

        if("The filename, directory name, or volume label syntax is incorrect" in commandResponse):
            logging.error("The assumed ethernet adapter name 'Ethernet' wasn't found for setting IP on windows")
            raise Exception("Couldn't find adapter to set IP address on for Windows")

        if("requires elevation" in commandResponse):
            logging.error("This program ran without administrator access and cannot set ip address")
            raise Exception("Invalid permissions to set ip address")
        return completed.stdout
    else:
        raise Exception(f"Unsupported operating system {platformString}")

def configure_vm():
    configure_ip()