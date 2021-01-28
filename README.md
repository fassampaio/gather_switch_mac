# Gather Switch MACs
Gather Cisco switch MAC addresses information and write the results to JSON and CSV files.
The program uses Netmiko to conected and Genie library to parse the commands output.
## Instalation
### 1. Create a virtual python environment to keep the python modules isolated.
```
virtualenv gather_switch_mac
source gather_switch_mac/bin/activate
```
### 2. Clone the git repository
```
git clone ...
```
### 3. Install the modules requeriments into de virtual environment with `pip`.
```
cd gather_switch_mac
pip install -r requeriments.txt
```
### 4. Configure files
Edit the configurations files to meet your network.
- `gather_switch_mac.ini`
- `host_list.yaml`
- `credentials.yaml`
### 5. Run program
```
python gather_switch_mac.py
```
## Components

### Configuration file
The configuration file is in INI format and store the initial parameters.
This file has the file names definitions

`gather_switch_mac.ini`

Default file content:
```
# gather_switches_mac configuration file
[files]
credentials = credentials.yaml
host_list = host_list.yaml
mac_addresses_json_file = mac_addresses.json
mac_addresses_csv_file = mac_addresses.csv
```

### Host list file
The host list file stores in format YAML all the devices to gather information

`host_list.yaml`

File content:
```
---
# Host list
# Host type depends on connection protocol
# ssh - cisco_ios or cisco_nxos
# telnet - cisco_ios_telnet

hosts:
  10.0.0.1: cisco_ios_telnet
  10.0.0.2: cisco_ios_telnet
  10.0.0.3: cisco_ios
  10.0.0.4: cisco_ios
  
...
```

### Credentials file

`credentials.yaml`

File content:
```
---
credentials:
  cli:
    username: admin
    password: cisco

...
```

## Useful links
- [Genie library](https://developer.cisco.com/docs/genie-docs/)
- [Genie models](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models)
