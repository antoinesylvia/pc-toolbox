from __future__ import print_function

import os
from pprint import pprint

try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import json
import pandas
from datetime import datetime, date, time
from pathlib import Path

# --Execution Block-- #
# --Parse command line arguments-- #
parser = argparse.ArgumentParser(prog='rltoolbox')

parser.add_argument(
    '-u',
    '--username',
    type=str,
    help='*Required* - Prisma Cloud API Access Key ID that you want to set to access your Prisma Cloud account.')

parser.add_argument(
    '-p',
    '--password',
    type=str,
    help='*Required* - Prisma Cloud API Secret Key that you want to set to access your Prisma Cloud account.')

parser.add_argument(
    '-url',
    '--uiurl',
    type=str,
    help='*Required* - Base URL used in the UI for connecting to Prisma Cloud.  '
         'Formatted as app.prismacloud.io or app2.prismacloud.io or app.eu.prismacloud.io, etc.  '
         'You can also input the api version of the URL if you know it and it will be passed through.')

parser.add_argument(
    '-url_compute',
    '--uiurl_compute',
    type=str,
    help='*Required* - Base URL used in the UI for connecting to Prisma Cloud Compute.  '
         'Formatted as region.cloud.twistlock.com/identifier.'
         'Retrieved from Compute->Manage->System->Downloads->Path to Console')

parser.add_argument(
    '-y',
    '--yes',
    action='store_true',
    help='(Optional) - Override user input for verification (auto answer for yes).')

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl, args.uiurl_compute)

# Verification (override with -y)
if not args.yes:
    print()
    print('Ready to excute commands aginst your Prisma Cloud tenant.')
    verification_response = str(input('Would you like to continue (y or yes to continue)?'))
    continue_response = {'yes', 'y'}
    print()
    if verification_response not in continue_response:
        pc_lib_general.pc_exit_error(400, 'Verification failed due to user response.  Exiting...')

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

# Get containers list
print('API - Getting containers list...', end='')
pc_settings, response_package = pc_lib_api.api_containers_get(pc_settings)
file_name = "containers_list_filtered_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".csv"
file_path = os.path.join(Path.home(), "prisma-compute-exports")
containers = response_package['data']
data_header = "Application,Hostname,Cluster,Image Name,Namespace"
print("Exporting data to: " + os.path.join(file_path, file_name))
pc_lib_general.pc_file_write_csv(file_name, data_header, file_path)
for container in containers:
    data_info_hostname = container['hostname']
    data_info_namespace = container['info']['namespace']
    data_info_cluster = container['info']['cluster']
    data_info_imageName = container['info']['imageName']
    data_info_app = container['info']['app']
    data_line = data_info_app + "," + data_info_hostname + "," + data_info_cluster + "," + data_info_imageName + "," + data_info_namespace
    pc_lib_general.pc_file_write_csv(file_name, data_line, file_path)
print('Done.')
