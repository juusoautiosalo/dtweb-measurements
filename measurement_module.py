"""
Functions for executing measurements on Digital Twin Web.
"""
import time, os
import psutil
from datetime import datetime, timezone

import asyncio, asks
from contextlib import closing

import plotting_module as plot
import yaml

async def fetch_host_url_async(dtid: str, timeout=None) -> str:
    """
    Fetches hosting URL based on a DTID

    Returns:
        Hosting URL as a string

    """
    r = await asks.get(dtid, timeout=timeout)
    return r.url


async def fetch_dt_doc_async(dtid: str, timeout_registry=3.0, timeout_base=2.0) -> dict:
    """
    Fetches a DT doc based on a DTID.

    Args:
      dtid: The DT identifier of the target DT. Must be URL.

    Returns:
      DT doc in python dict form.

    """
    dt_url = await fetch_host_url_async(dtid, timeout=timeout_registry)
    r = await asks.get(dt_url + '/index.json',timeout=timeout_base)

    return r.json()


async def fetch_and_log_dt_doc_async(dtid: str,log,number,timeout_registry=None,timeout_base=None) -> dict:
    """
    Fetches DT doc in dict form based on a DTID.

    Args:
      dtid: The DT identifier of the target DT. Must be URL.

    Returns:
      DT doc in python dict form.
    """

    starttime = time.perf_counter()
    # Fetch host url from DTID
    try:
        dt_url = await fetch_host_url_async(dtid, timeout=timeout_registry)
    except:
        print('Could not resolve DTID: ' + dtid + ' in ' + str(timeout_registry) + ' seconds')
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},{},Could not resolve DTID,-,-,-,{},{}\n'
        log.write(msg.format(time.perf_counter()-starttime, dtid, dtid, number))
        return None
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},{},DTID > hosturl fetch time,-,-,-,{},{}\n'
    log.write(msg.format(time.perf_counter()-starttime, dtid, dtid, number))

    # Fetch DT doc from host URL
    starttime_doc = time.perf_counter()
    try:
        r = await asks.get(dt_url + '/index.json', timeout=timeout_base)
    except:
        print('Could not fetch DT doc from: ' + dt_url + ' in ' + str(timeout_base) + ' seconds')
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},{},Could not fetch DT doc,-,-,-,{},{}\n'
        log.write(msg.format(time.perf_counter()-starttime, dtid, dtid, number))
        return None
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},{},Hosturl > DT doc fetch time,-,-,-,{},{}\n'
    log.write(msg.format(time.perf_counter()-starttime_doc, dtid, dtid, number))
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},{},DT doc received,-,-,-,{},{}\n'
    log.write(msg.format(time.perf_counter()-starttime, dtid, dtid, number))

    return r.json()


def get_multiple_dt_docs(params, log, number, show_time=True):
    """
    Fetch multiple DT docs simultaneously

    Returns:
      ?
    """
    start = time.perf_counter()
    pages = []
    tasks = []
    timeout_registry = params['timeout_registry']
    timeout_base = params['timeout_base']
    asyncio.set_event_loop(asyncio.new_event_loop())
    with closing(asyncio.get_event_loop()) as loop:
        for dtid in params['dtids']:
            tasks.append(fetch_and_log_dt_doc_async(dtid,log,number,timeout_registry=timeout_registry,timeout_base=timeout_base))
        pages = loop.run_until_complete(asyncio.gather(*tasks))
    duration = time.perf_counter() - start
    if show_time:
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = 'It took {:4.3f} seconds to get {} DT docs.\n'
        log.write(msg.format(duration, len(params['dtids'])))

    return pages


async def fetch_children_async(dtid, log, starttime, depth, origin, params, number):
    """
    Fetches the children of a twin.
    
    Returns:
        children: A list of children's DTIDs
    """
    try:
        dtdoc = await fetch_dt_doc_async(dtid,timeout_registry=params['timeout_registry'],timeout_base=params['timeout_base'])
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},{},DT doc received,-,{},{},-,{}\n'
        log.write(msg.format(time.perf_counter()-starttime, dtid, depth, origin, number))
    except:
        print('Could not fetch DT doc for: ' + dtid + ' due to registry or base timeout.')#' in ' + str(params['timeout_registry']) + ' seconds (may also be because of base)')
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},{},Could not fetch DT doc,-,{},{},-,{}\n'
        log.write(msg.format(time.perf_counter()-starttime, dtid, depth, origin, number))
        return None

    children = []
    try:
        for relation in dtdoc['relations']:
            # print(relation)
            if relation['relationType'] == 'child':
                # print('child found!')
                children.append(relation['dt-id'])
            # else:
            #     print('No children for ' + dtdoc['name'])
    except:
        print('No relations for ' + dtdoc['name'])
    return children


async def loop_through_children(dtid, log, starttime, depth, origin, params, number, show_time=True):
    """
    Recursive loop through the children of a twin.
    """
    start = time.perf_counter()
    twintree = {}
    twintree[dtid] = []
    child_dtids = await fetch_children_async(dtid, log, starttime, depth, origin, params, number)

    depth +=1
    if isinstance(child_dtids, list):
        children =  await asyncio.gather(*[loop_through_children(dtid, log, starttime, depth, origin, params, number) for dtid in child_dtids])
        twintree[dtid].append(children)

    duration = time.perf_counter() - start
    if show_time:
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},{},Duration to fetch all children,{:4.6f},{},{},-,{}\n'
        log.write(msg.format(time.perf_counter()-starttime, dtid, duration, depth-1, origin, number))
    
    return twintree


def start_loop_through_children(params: dict, log, starttime, number, show_time=True):
    """
    Starts a loop through children of a list of twins.
    """
    start = time.perf_counter()
    twintree_list = []
    tasks = []
    depth = 0
    # https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    asyncio.set_event_loop(asyncio.new_event_loop())
    with closing(asyncio.get_event_loop()) as loop:
        for dtid in params['dtids']:
            origin = dtid
            tasks.append(loop_through_children(dtid, log, starttime, depth, origin, params, number))
        twintree_list = loop.run_until_complete(asyncio.gather(*tasks))
    duration = time.perf_counter() - start
    if show_time:
        # Time,DTID,Event,Duration,Depth,Origin,Base,Number
        msg = '{:4.6f},"{}",Whole loop to fetch children of {} DTs,{:4.6f},-,-,-,{}\n'
        log.write(msg.format(time.perf_counter()-starttime, params['dtids'], len(params['dtids']),duration,number))
    return twintree_list


def init_network_measurement(params: dict, filepath: str, number: int, show_time=True):
    """
    Initializes a network measurement that fetches children of multiple origin DTIDs.

    Args:
      params: Dict of measurement parameters
      filepath: Path to file where the measurement log will be written.
      number: Sample number of measurement

    Returns:
      children: A list of twin trees. Can be printed with pprint.
    """

    ### Setup
    
    # Open file
    try:
        main_logfile = open(filepath, "a")
    except:
        print("Couldn't open file \"" + filepath + "\", exiting...")
        exit()
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    main_logfile.write("Time,DTID,Event,Duration,Depth,Origin,Base,Number\n")

    starttime = time.perf_counter()
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},"{}",Start measurement loop for a list of twins,-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, params['dtids'],number))
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},metadata,Start at {},-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, datetime.now(timezone.utc).isoformat(), number))
    

    ### Go to measurement loop
    children = start_loop_through_children(params, main_logfile, starttime, number)
    

    ### Wrap up 

    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},"{}",Ended measurement loop,-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, params['dtids'], number))

    main_logfile.close()
    
    return children


def init_registry_measurement(params: dict, filepath, number, show_time=True):
    """
    Initializes a registry measurement for a list of DTIDs.

    Args:
      params: Dict of measurement parameters
      filepath: Path to file where the measurement log will be written.
      number: Sample number of measurement

    Returns:
      ?
    """

    ### Setup

    # Open file
    try:
        main_logfile = open(filepath, "a")
    except:
        print("Couldn't open file \"" + filepath + "\", exiting...")
        exit()
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    main_logfile.write("Time,DTID,Event,Duration,Depth,Origin,Base,Number\n")

    starttime = time.perf_counter()
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},"{}",Start measurement loop for a list of twins,-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, params['dtids'], number))
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},metadata,Start at {},-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, datetime.now(timezone.utc).isoformat(), number))

    ### Go to measurement loop
    docs = get_multiple_dt_docs(params, main_logfile,number)

    ### Wrap up 
    # Time,DTID,Event,Duration,Depth,Origin,Base,Number
    msg = '{:4.6f},"{}",Ended measurement loop,-,-,-,-,{}\n'
    main_logfile.write(msg.format(time.perf_counter()-starttime, params['dtids'], number))

    main_logfile.close()

    return docs


def run_registry_measurement(params, folderpath):
    """
    Prepares and starts a comparison measurement for multiple origin DTIDs.

    Args:
      params: Dict with measurement parameters.
              Must follow the structure of params defined under
              registry_measurement in params-example.yaml
      folderpath: Path to folder where all measurement result files will be written.

    Returns:
      String of measurement log filepath
    """


    ### Prepare measurement ###

    try:
        samples = params['samples']
        dtids = params['dtids']
    except:
        print('\nCould not use parameters, please check them. Exiting.')
        exit()

    print('Measuring DTIDs:\n' + str(dtids) +'\n')
    print('Writing to folder: ' + folderpath + '\n')

    filename = 'main_log.csv'
    filepath = os.path.join(folderpath, filename)

    # Save parameters as a YAML file
    with open (os.path.join(folderpath, 'params.yaml'), 'w') as yamlfile:
        yaml.dump(params, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)


    ### Run measurements ###

    for sample in range(samples):
        # Print statistics to terminal
        memory = psutil.virtual_memory()
        print('Sample ' + str(sample+1) + ' / ' + str(samples) + ' Memory usage: ' + str(memory.percent) + '% (' + str((memory.total - memory.available)/1000000000) + '/' + str(memory.total/1000000000) + ')')
        
        time.sleep(0.2)
        init_registry_measurement(params, filepath, sample+1)

    print('\nRegistry measurement done\n')

        
    ### Plot measurement results ###

    print('Plotting ' + filepath)
    print(dtids)
    plot.plot_registry_fetch_times(filepath, folderpath, dtids)

    return filepath



def run_network_measurement(params, folderpath):
    """
    Prepares and starts a network measurement for multiple origin DTIDs.

    Args:
      params: Dict with measurement parameters.
              Must follow the structure of params defined under
              network_measurements in params-example.yaml
      folderpath: Path to folder where all measurement result files will be written.

    Returns:
      String of measurement log filepath
    """


    ### Prepare measurement ###

    # Parameters
    dtids = params['dtids']
    samples = params['samples']

    print('Number of samples: ' + str(samples))
    print('Measuring DTIDs:\n' + str(dtids) +'\n')

    # Save parameters to a YAML file
    with open (os.path.join(folderpath, 'params.yaml'), 'w') as yamlfile:
        yaml.dump(params, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Set filename
    filename = 'main_log.csv'
    filepath = os.path.join(folderpath, filename)
    print('Writing to file: ' + filepath)


    ### Run measurements ###

    for sample in range(samples):
        # Print statistics to terminal
        memory = psutil.virtual_memory()
        print('Sample ' + str(sample+1) + ' / ' + str(samples) + ' Memory usage: ' + str(memory.percent) + '% (' + str((memory.total - memory.available)/1000000000) + '/' + str(memory.total/1000000000) + ')')
 
        time.sleep(0.2)
        init_network_measurement(params, filepath, sample+1)


    ### Plot measurement results ###

    print('Plotting ' + filepath)
    registry_domain = dtids[0].split('/')[2]
    plot.plot_network_fetch_times(filepath, folderpath, registry_domain)

    return filepath


if __name__ == '__main__':

    print('Use the "run_measurements.py file to run measurements')
