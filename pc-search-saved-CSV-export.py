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



print('API - Getting saved searches list...', end='')
pc_settings, response_package = pc_lib_api.api_search_get_all(pc_settings)
saved_searches = response_package['data']
print('Done.')


# Save JSON to CSV with date/time and cloud type 
print('Saving JSON contents as a CSV...', end='')
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
pu = pandas.json_normalize(saved_searches) #put json inside a dataframe

#strip everything except the policy ID in the "policies" column, useful for mapping purposes for other objectives.
#pu.policies = pu.id.str.replace(".+\['|'].+", '')  

# Change timestamp for specific column from UNIX time to any time zone. 
pu['timestamp']=(pandas.to_datetime(pu['timestamp'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
pu['searchModel.timeRange.value.startTime']=(pandas.to_datetime(pu['searchModel.timeRange.value.startTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
pu['searchModel.timeRange.value.endTime']=(pandas.to_datetime(pu['searchModel.timeRange.value.endTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

print('Saving JSON contents as a CSV...', end='')
pu.to_csv('saved_searches_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')



