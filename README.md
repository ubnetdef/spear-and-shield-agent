# Spear and Shield Agent

## How to setup for VM
1. Load these files onto the virtual machine
2. Make sure VM has python3 and poetry installed
3. Run `poetry install` inside this project's directory
4. Make it so the system runs `poetry run python3 runner.py` on boot (crontab @reboot should work) (this must run as admin!)
5. Should be good to go!

## For Development
This library uses poetry for managing it's dependencies. So, when using vscode make sure to switch your python interpreter to use the poetry virutal environment

For development and testing features for linux, this also includes a config for a developer container. This is mainly just to test basic features and allow for quick testing.