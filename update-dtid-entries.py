"""Updates DTID registry entries at Rebrandly

Reads DTID the dt-id and hosting-id fields from local DT documents and 
pushes them to a DTID registry hosted at Rebrandly via the Rebrandly API.

Only updates the entries of the specified DTID registry domain.

This script should be run in the "docs" folder of Twinbase.

Requires setting up the environment variable "REBRANDLY_API_KEY"
which can be read or created at https://app.rebrandly.com/account/api-keys

    To set environment variable, run in terminal: 
    export REBRANDLY_API_KEY=<api-key-from-rebrandly>

Falls back to dtid.org as the default DTID registry domain.
If you don't have the API key for dtid.org, set the environment
variable "DTID_REGISTRY_DOMAIN" to match your domain.

    To set environment variable, run in terminal:
    export DTID_REGISTRY_DOMAIN=<domain>
"""

import requests, uuid, os, time, yaml

# Read environment variables
try:
    API_KEY = os.environ["REBRANDLY_API_KEY"]
    print('Successfully read the REBRANDLY_API_KEY environment variable')
except:
    print('Environment variable "REBRANDLY_API_KEY" was not found.')
    print('Please fetch or create your API key at https://app.rebrandly.com/account/api-keys')
    print('and set it using the following command.\n')
    print('    export REBRANDLY_API_KEY=<api-key-from-rebrandly>\n')    
    exit()
try:
    REGISTRY_DOMAIN = os.environ["DTID_REGISTRY_DOMAIN"] # e.g. dtid.org
    print('Using DTID registry domain: ' + REGISTRY_DOMAIN)
except:
    print('No environment variable "DTID_REGISTRY_DOMAIN" was found, using "dtid.org"')
    REGISTRY_DOMAIN = "dtid.org"

print(' ')

# Set fixed variables
REBRANDLY_URL = "https://api.rebrandly.com/v1/links"

# Read base YAML file to set owner for the registry entry
with open('index.yaml', 'r') as yamlfile:
    doc = yaml.load(yamlfile, Loader=yaml.FullLoader)
title = 'Owner: ' + doc['owner']['dt-id']

print('Using entry title: ' + title + '\n')

# Go through the twin folders
curdir = os.getcwd()
for folder in os.listdir(curdir):
    if os.path.isdir(folder) and folder != 'static' and folder != 'new-twin':
        
        # Load YAML file
        with open(folder + '/index.yaml', 'r') as yamlfile:
            doc = yaml.load(yamlfile, Loader=yaml.FullLoader)

        if doc['dt-id'].split('/')[2] == REGISTRY_DOMAIN:

            print('Creating redirection for ' + doc['name'])
            # Create redirect entry to Rebrandly
            payload = {
                "domain": {"fullName": REGISTRY_DOMAIN},
                "destination": doc['hosting-iri'],
                "slashtag": doc['dt-id'].split('/')[3],
                "title": title
            }
            headers = {
                "Content-Type": "application/json",
                "apikey": API_KEY
            }
            response = requests.request("POST", REBRANDLY_URL, json=payload, headers=headers)
            r = response.json()

            # Handle any errors
            try:
                if r['errors'][0]['code'] == 'AlreadyExists':
                    print('DT-ID already exists, updating it to match current hosting-iri.')
                    time.sleep(0.1)

                    # Get link id from rebrandly
                    querystring = {
                        "domain.fullName":REGISTRY_DOMAIN,
                        "slashtag":doc['dt-id'].split('/')[3]
                    }
                    headers = {"apikey": API_KEY}
                    response = requests.request("GET", REBRANDLY_URL, headers=headers, params=querystring)
                    link_id = response.json()[0]['id']

                    time.sleep(0.1)

                    # Update
                    url = "https://api.rebrandly.com/v1/links/" + link_id
                    payload = {
                        "title": title,
                        "destination": doc['hosting-iri']
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "apikey": API_KEY
                    }
                    response = requests.request("POST", url, json=payload, headers=headers)
            except:
                pass
            
            # Sleep a while to comply with Rebrandly API limitations
            # https://developers.rebrandly.com/docs/api-limits
            time.sleep(0.1)

        else:
            print('Skipping ' + doc['dt-id'] + ' (' + doc['name'] + ')')

print('\nFinished!')
