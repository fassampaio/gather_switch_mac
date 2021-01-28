# Gather Switch MACs
Gather Cisco switch MAC addresses information and write the results to JSON and CSV files.
The program uses Netmiko to conected and Genie library to parse the commands output.

## 2. Instalation
### 2.1. Create a virtual python environment to keep the python modules isolated.
```
virtualenv gather_switch_mac
source gather_switch_mac/bin/activate
```

### 2.2. Clone the git repository
```
git clone ...
```

### 2.3. Install the modules requeriments into de virtual environment with `pip`.
```
cd gather_switch_mac
pip install -r requeriments.txt
```

### 2.4. Configure files
Edit the configurations files to meet your network.
- `gather_switch_mac.ini`
- `host_list.yaml`
- `credentials.yaml`

### 2.5. Run program
```
python gather_switch_mac.py
```

## 3. Useful links
- [Genie library](https://developer.cisco.com/docs/genie-docs/)
- [Genie models](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models)
