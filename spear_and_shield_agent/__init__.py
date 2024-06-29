from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import platform
import subprocess
import logging
import socket
import time

transport = AIOHTTPTransport(url="https://spearandshield.ubnetdef.org/graphql")

client = Client(transport=transport, fetch_schema_from_transport=True)

def get_new_ip_address(currentIPAddress: str) -> str:
    '''
    Contacts Spear and Shield API to get the new IP Address for a machine DHCPed with the currentIPAddress
    '''

    query = gql(
    """
    query MyQuery($fromIPAddress: String!) {
        getSASAgentConfig(fromIPAddress: $fromIPAddress) {
            fromIPAddress
            toIPAddress
        }
    }
    """
    )

    variables = {"fromIPAddress": currentIPAddress}
    result = client.execute(query, variables)
    newIPAddress = result['getSASAgentConfig']['toIPAddress']
    return newIPAddress

def get_windows_first_default_adpater_ip_address() -> str:
    import netifaces
    gws=netifaces.gateways()
    defaultAdapterDict = gws['default']
    firstKey = list(gws['default'].keys())[0]
    adapterInfo = defaultAdapterDict[firstKey]
    currentIPAddress = netifaces.ifaddresses(adapterInfo[1])
    return currentIPAddress

# Solution from: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_windows_ip_address() -> str:
    '''
    Works by using a socket and sending a request to 8.8.8.8, which will determine which is the default interface. Then it will pull the loacl ip of that interface.

    From: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

    Can likely work on other systems, but only tested on windows
    '''
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IPAddress = s.getsockname()[0]
    return IPAddress

def get_linux_first_default_adpater_ip_address() -> str:
    import netifaces
    gws=netifaces.gateways()
    defaultAdapterDict = gws['default']
    firstKey = list(gws['default'].keys())[0]
    adapterInfo = defaultAdapterDict[firstKey]
    currentIPAddress = adapterInfo[0]
    return currentIPAddress

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

class NewIPTimeoutException(Exception):
    pass

def windows_get_new_ip_address() -> str:
    TIMEOUT_TIME = 120
    timeoutUNIXTime = time.time() + TIMEOUT_TIME
    while(True):
        try:
            if(time.time() >= timeoutUNIXTime):
                raise NewIPTimeoutException("Timeout trying to retrieve current ip address or new ip address from backend")

            currentIPAddress = get_windows_ip_address()
            ipAddress = get_new_ip_address(currentIPAddress)
            return ipAddress
        except NewIPTimeoutException as e:
            raise e
        except:
            continue

def configure_ip() -> bytes:
    '''
    Returns the stdout of the system command response
    '''

    platformString = platform.system()
    if platformString == "Linux":
        from pyroute2 import IPRoute
        try:
            ip = IPRoute()
            adapterName = get_linux_first_default_adpater()
            adapterIndex = get_linux_adapter_index(adapterName)
            adapterInfo = ip.get_addr(label=adapterName)
            ipAddress = get_new_ip_address(get_linux_first_default_adpater_ip_address())
            ip.addr('add', adapterIndex, address=ipAddress, mask=24)
            ip.close()
        except IndexError:
            logging.error("Couldn't assign IP on Linux system, agent assumes ens160 is name of adapter to be configured")
            raise Exception("Error when assigning IP to Linux system, system assumes ens160 is name of adapter")
        except Exception as e:
            logging.error("Couldn't assign IP on Linux system")
            raise e
    elif platformString == "Windows":
        ipAddress = windows_get_new_ip_address()
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