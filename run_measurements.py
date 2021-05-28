import os
from datetime import datetime, timezone
import measurement_module as meas
import yaml
import pprint
import time
# import pandas as pd

measurement_starttime = time.perf_counter()


##### Prepare measurement #####


# Open parameters file
try:
    with open('params.yaml', 'r') as yamlfile:
        params = yaml.load(yamlfile, Loader=yaml.FullLoader)
except:
    print('Could not open params.yaml, using params-example.yaml instead.')
    with open('params-example.yaml', 'r') as yamlfile:
        params = yaml.load(yamlfile, Loader=yaml.FullLoader)    

print('Parameters:')

pprint.pprint(params)

# Set foldernames
foldername_measurements = os.path.join('measurements', params['foldername'])
foldername = os.path.join(foldername_measurements, 'measurements-' + datetime.now(timezone.utc).isoformat()[:-13])
try:
    os.mkdir(foldername)
except:
    try:
        os.mkdir(foldername_measurements)
        print('Created ' + foldername_measurements + ' folder')
        os.mkdir(foldername)
    except:
        os.mkdir('measurements')
        print('Created "measurements" folder')
        os.mkdir(foldername_measurements)
        print('Created ' + foldername_measurements + ' folder')
        os.mkdir(foldername)
cwd = os.getcwd()
folderpath = os.path.join(cwd, foldername)
print('\nWriting to folder: ' + foldername + '\n')
print('Press Ctrl + C to cancel\n')

# Create folder for registry measurement
foldername_registry = 'registry_measurement'
folderpath_registry = os.path.join(folderpath, foldername_registry)
os.mkdir(folderpath_registry)

# Create folder for network measurements
foldername_network = 'network_measurements'
folderpath_network = os.path.join(folderpath, foldername_network)
os.mkdir(folderpath_network)

# Save parameter file to measurement folder
with open (os.path.join(folderpath, 'params.yaml'), 'w') as yamlfile:
    yaml.dump(params, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)


#####  Run measurements #####

## Run registry measurement ##
if params['registry_measurement']['run']:
    print('\n---- Starting registry measurement ----\n')
    ######## Run ########
    filepath = meas.run_registry_measurement(params['registry_measurement']['params'], folderpath_registry)
else: 
    print('\n---- Skipped registry measurement due to parameter file configuration ----\n')

## Run network measurements ##
print('\n\n---- Starting network measurement ----')
for key in params['network_measurements']:
    if params['network_measurements'][key]['run']:
        print('\n-- Running measurement: ' + key)
        # Create folder
        foldername_key = key
        folderpath_key = os.path.join(folderpath_network, foldername_key)
        os.mkdir(folderpath_key)
        run_params = params['network_measurements'][key]['params']
        ###### Run ######
        filepath = meas.run_network_measurement(run_params, folderpath_key)
    else:
        print('\n--Parameter file has a measurement run called ' + key + ' but it is set to False')


#####  Postprocess #####

print('\n---- Postprocessing ----\n')

### Copy to latest
from distutils.dir_util import copy_tree
fromDirectory = folderpath
toDirectory = os.path.join(foldername_measurements, 'latest')
copy_tree(fromDirectory, toDirectory)
print('\nCopied all files to ' + toDirectory)


print('\nMeasurement finished, see this folder for results:')
print(folderpath)

print('\nThis measurement took ' + str(int(round(time.perf_counter() - measurement_starttime))) + ' seconds in total.' )
