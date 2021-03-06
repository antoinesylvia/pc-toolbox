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



print('API - Getting current account groups...', end='')
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
accounts_groups_list = response_package['data']
print('Done.')


# Save JSON to CSV with date/time and cloud type 
print('Saving JSON contents as a CSV...', end='')

#Get the current date/time
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

# Put json inside a dataframe
pu = pandas.json_normalize(accounts_groups_list)

# Query a specific column (description in this case) and match on a specific string in the rows, customize to your liking.
mvp = pu.query('description == "GCP Project Mapped to Account Group"')

# Onced matched, filter out the remaining columns and docus on just ID and Name.
#alternate method to filter the columns returned ---> mvp1 = mvp.drop(columns=['accounts','alertRules', 'autoCreated', 'accountIds', 'lastModifiedTs', 'lastModifiedBy', 'description'])
mvp1 = mvp.filter(['id', 'name'])

# For the filtered columns that remain, go through each row and filter out items based on the strings you customize below. 
mvp2 = mvp1[~mvp1['id'].str.contains('sbx|sandbox|test|6627851|retrieveseatmap01|playground')]

# Sort the "id" column and save to a CSV without filtered items. 
mvp2.sort_values(by=['id'], ascending = True).to_csv('prisma_accounts_groups_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False)
#index= false removes index on far left
print('Done.')



