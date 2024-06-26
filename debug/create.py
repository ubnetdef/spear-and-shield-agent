from os import path
import sys
sys.path.insert(0, path.abspath('./'))

import spear_and_shield_agent

print(spear_and_shield_agent.configure_ip().decode())