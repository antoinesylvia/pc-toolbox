from __future__ import print_function
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

# Sort out and build the filters JSON
print('Local - Building the filter JSON package...', end='')

print('API - Getting anomaly settings list...', end='')
pc_settings, response_package = pc_lib_api.api_anomalies_settings_get_UEBA(pc_settings)
anomalies_settings_UEBA = response_package['data']
print('Done.')

pc_settings, response_package = pc_lib_api.api_anomalies_settings_get_Network(pc_settings)
anomalies_settings_Network = response_package['data']
print('Done.')

# Get the current date/time 
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

# Put JSON(s) inside a data frame
pu1 = pandas.json_normalize(anomalies_settings_UEBA) #put json inside a dataframe
pu2 = pandas.json_normalize(anomalies_settings_Network)

print('Saving JSON contents as a CSV...', end='')
pu1.to_csv('anomalies_settings_UEBA_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')
pu2.to_csv('anomalies_settings_Network_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
# print('Done.')



