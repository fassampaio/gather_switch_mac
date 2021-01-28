#!/usr/bin/env python

# Metadata
__author__ = "Fabio Sampaio"
__contact__ = "fabio.sampaio@protonmail.com"
__license__ = "MIT"
__version__ = 0.1


import sys
import csv
import json
import yaml
import os.path
import logging
import netmiko
import argparse
import configparser

from datetime import datetime


log_level = "20"
logger = logging.getLogger(__name__)

CONFIG_FILE = "gather_switches_mac.ini"


def args_parse():
    """
    This functions read the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Program to gather ARP information from network devices.",
        epilog="Enjoy the program! :)"
    )
    parser.add_argument(
        "-l",
        "--log",
        help="define logging level. Options [30 = WARNING, 20 = INFO, 10 = DEBUG]. Default = "+log_level,
        metavar="LOG_LEVEL",
        dest="log_level",
        type=int,
        choices=[30, 20, 10],
        default=log_level
    )
    args = parser.parse_args()
    return(args.log_level)


def load_configuration():
    # Load configuration information
    global credentials_file
    global host_list_file
    global mac_addresses_json_file
    global mac_addresses_csv_file

    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        credentials_file = config['files']['credentials']
        host_list_file = config['files']['host_list']
        mac_addresses_json_file = config['files']['mac_addresses_json_file']
        mac_addresses_csv_file = config['files']['mac_addresses_csv_file']

        logger.info("Load configuration from {}".format(CONFIG_FILE))
        logger.debug("Credentials file - {}".format(credentials_file))
        logger.debug("Host list file - {}".format(host_list_file))
        logger.debug(
            "Mac addresses JSON file - {}".format(mac_addresses_json_file))

    else:
        logger.error(
            'Please create configuration file - {}'.format(CONFIG_FILE))


def load_credentials():
    global username
    global password

    if os.path.exists(credentials_file):
        credentials_dict = yaml.load(
            open(credentials_file, "r"), Loader=yaml.FullLoader)
        username = credentials_dict['credentials']['cli']['username']
        password = credentials_dict['credentials']['cli']['password']
        logger.info("Load credentials from {}".format(credentials_file))
        logger.debug("Username - {}".format(username))
    else:
        logger.error(
            'Please create credentials file - {}'.format(credentials_file))


def load_host_list():
    if os.path.exists(host_list_file):
        hosts_list = yaml.load(open(host_list_file, "r"),
                               Loader=yaml.FullLoader)
        logger.info("Load host list from {}".format(host_list_file))
        logger.debug("Host list:\n{}".format(json.dumps(hosts_list)))
    else:
        logger.error(
            'Please create host list file - {}'.format(host_list_file))

    return(hosts_list)


def config_logging():
    """
    This function configures the environments variables
    """
    logging.getLogger('netmiko').setLevel(logging.CRITICAL)
    logging.getLogger('paramiko').setLevel(logging.CRITICAL)

    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        datefmt='%d-%b-%y %H:%M:%S'
    )
    logger.info("Configuring environment.")
    logger.debug("Logging level - {}".format(log_level))


class GatherMacAddresses():
    """
    Gather mac addresses information from devices.
    """

    def __init__(self, host_list):
        """Init the object and variables.

        Args:
            host_list (dict): Variable to store hosts mac addresses information.
        """
        self.host_list = host_list
        self.hosts = {
            'hosts': {}
        }

    def save_to_file_json(self, output_file):
        """Store the content of self.hosts to a file in JSON format.

        Args:
            output_file (str): Path end file name to write.
        """
        try:
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(self.hosts, f, ensure_ascii=False, indent=4)
                logger.info('Write JSON dictionary to {}'.format(output_file))

        except IOError:
            logger.error("I/O error to write {} file".format(output_file))

    def save_to_file_csv(self, output_file):
        csv_header = {'hostname', 'vlan', 'mac_address', 'interface', 'mode'}
        try:
            with open(output_file, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=csv_header)
                writer.writeheader()
                hosts = self.hosts['hosts']
                for host in hosts:
                    vlans = hosts[host]['mac_table']['vlans']
                    for vlan in vlans:
                        mac_addresses = vlans[vlan]['mac_addresses']
                        for mac_address in mac_addresses:
                            if 'interfaces' in mac_addresses[mac_address]:
                                interfaces = mac_addresses[mac_address]['interfaces']
                                for interface in interfaces:
                                    if vlan != 'all':
                                        hosts_int = self.hosts['hosts'][host]['interfaces']
                                        for host_int in hosts_int:
                                            if host_int == interface:
                                                mode = hosts_int[host_int]['vlan']
                                                writer.writerow({
                                                    'hostname': host,
                                                    'vlan': vlan,
                                                    'mac_address': mac_address,
                                                    'interface': interface,
                                                    'mode': mode
                                                })

                logger.info("Write CSV list to {}".format(output_file))

        except IOError:
            logger.error("I/O error to write {} file".format(output_file))

    def _add_host(self, host):
        host_key = {
            host: {}
        }
        self.hosts['hosts'].update(host_key)
        logger.debug('Add host {} to dict'.format(host))

    def _add_interface_mac(self, host, interface_mac):
        self.hosts['hosts'][host].update(interface_mac)
        logger.debug("Add the following interface mac to dict:\n{}".format(
            json.dumps(interface_mac, indent=4)))

    def _add_interface_status(self, host, interface_status):
        self.hosts['hosts'][host].update(interface_status)
        logger.debug("Add the following interface status to dict:\n{}".format(
            json.dumps(interface_status, indent=4)))

    def run(self):
        """
        Connect to host in list and gather MAC addresses information
        and store in self.hosts
        """
        # Init local variables
        interface_mac = {}
        interface_status = {}

        # Loop to gather hosts information
        hosts = self.host_list['hosts']
        for host in hosts:
            self._add_host(host)
            try:
                # Connecto to host
                device_type = hosts[host]
                host_connect = netmiko.Netmiko(
                    host=host,
                    username=username,
                    password=password,
                    device_type=device_type
                )
                logger.info("Connect to host {}".format(host))

                # Send command
                interface_mac = host_connect.send_command(
                    "show mac address-table", use_genie=True)
                logger.debug(
                    "Output of the show mac address-table \n{}".format(
                        json.dumps(interface_mac,
                                   indent=4,
                                   skipkeys=False,
                                   ensure_ascii=True)))
                interface_status = host_connect.send_command(
                    "show interfaces status", use_genie=True)
                logger.debug("Output of the show interface_status \n{}".format(
                    json.dumps(interface_status, indent=4)))
                logger.info("Gather host {} information".format(host))

            except Exception as e:
                logger.warning(
                    'Failed to connect to host {}: {}'.format(host, str(e)))

            self._add_interface_mac(host, interface_mac)
            self._add_interface_status(host, interface_status)

        return(self.hosts)


def main():
    print("Gather ARP information from swicthes.")

    # Register start time
    start_time = datetime.now()
    logger.info("Start time: {}".format(start_time))

    # Configure environment
    config_logging()
    load_configuration()
    load_credentials()
    host_list = load_host_list()

    # Gather switches information
    gather_info = GatherMacAddresses(host_list)
    gather_info.run()

    # Save information to file
    gather_info.save_to_file_json(mac_addresses_json_file)
    gather_info.save_to_file_csv(mac_addresses_csv_file)

    # Register end time
    elapsed_time = datetime.now() - start_time
    logger.info("Elapsed time: {}".format(elapsed_time))


if __name__ == "__main__":
    # Read command line arguments
    log_level = args_parse()

    main()
