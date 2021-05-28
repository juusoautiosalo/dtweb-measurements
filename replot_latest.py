"""
Replots the latest measurement according to the parameter files.
"""

# import pandas as pd
import os
import plotting_module as plot
import yaml
import pprint

# Read foldername from current params.yaml 
try:
    with open('params.yaml', 'r') as yamlfile:
        params = yaml.load(yamlfile, Loader=yaml.FullLoader)
except:
    print('Could not open params.yaml, using params-example.yaml instead.')
    with open('params-example.yaml', 'r') as yamlfile:
        params = yaml.load(yamlfile, Loader=yaml.FullLoader)    
foldername_measurements = os.path.join('measurements', params['foldername'])


cwd = os.getcwd()
folderpath_latest = os.path.join(cwd, foldername_measurements, 'latest')
print(folderpath_latest)


# Read parameters file of latest measurement
latest_params_filepath = os.path.join(folderpath_latest, 'params.yaml')
try:
    with open(latest_params_filepath, 'r') as yamlfile:
        params = yaml.load(yamlfile, Loader=yaml.FullLoader)
except:
    print('Some error while trying to open parameter file from latest, try do fix something. Maybe the latest folder does not yet exist?') 
pprint.pprint(params)

#####  Plot measurements #####

## Plot registry measurement ##
if params['registry_measurement']['run']:
    print('\n---- Plotting registry measurement ----\n')
    ######## Plot ########
    registry_folderpath = os.path.join(folderpath_latest, 'registry_measurement')
    registry_log_filepath = os.path.join(registry_folderpath, 'main_log.csv')
    dtids = params['registry_measurement']['params']['dtids']
    plot.plot_registry_fetch_times(registry_log_filepath, registry_folderpath, dtids)
else: 
    print('\n---- Skipped registry measurement due to parameter file configuration ----\n')



## Plot network measurements ##
folderpath_network = os.path.join(folderpath_latest, 'network_measurements')

print('\n---- Plot network measurements ----')
for key in params['network_measurements']:
    if params['network_measurements'][key]['run']:
        print('\n-- Plotting network measurement: ' + key)
        # Read foldername
        foldername_key = key
        folderpath_key = os.path.join(folderpath_network, foldername_key)
        run_params = params['network_measurements'][key]['params']
        network_log_filepath = os.path.join(folderpath_key, 'main_log.csv')
        dtids = run_params['dtids']
        registry_domain = dtids[0].split('/')[2]
        ###### Plot ######
        plot.plot_network_fetch_times(network_log_filepath, folderpath_key, registry_domain)
    else:
        print('\n--Parameter file has a measurement run called ' + key + ' but it is set to False')


print('\nFinished')