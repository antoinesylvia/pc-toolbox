from __future__ import print_function

try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import os
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
    '-y',
    '--yes',
    action='store_true',
    help='(Optional) - Override user input for verification (auto answer for yes).')

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)

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

# Grab the policies
print('API - Getting current policy list...', end='')
query_params = "policy.severity=high&policy.severity=medium&policy.severity=low&cloud.type=gcp&cloud.type=all&policy" \
               ".subtype=run" \
               "&policy.subtype=build&policy.subtype=run_and_build"
pc_settings, response_package = pc_lib_api.api_policy_v2_list_filtered_get(pc_settings, query_params=query_params)
policy_v2_list = response_package['data']
# Removing complianceMetadata from Json
for policy_item in policy_v2_list:
    if "complianceMetadata" in policy_item:
        del policy_item['complianceMetadata']
print('Done.')

# Preparing the destination file
export_file_name = "policy_list_full_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".json"
export_file_path = os.path.join(Path.home(), "prisma-cloud-exports")
if not os.path.exists(export_file_path):
    os.makedirs(export_file_path)
pc_lib_general.pc_file_write_json(export_file_name, policy_v2_list, export_file_path)
