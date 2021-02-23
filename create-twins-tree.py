""" Creates a tree of digital twins.

The twin documents will be saved as index.yaml files to 

Arguments:
    1: The depth of the tree.
        Must be even number.
    2: The width of the tree, i.e. one twin will have this many children
        Must be even number

"""

import sys, uuid, os, yaml, lorem
# import pprint
from datetime import datetime, timezone
from coolname import generate_slug

# Receive user input argument for dimensions of the twin tree
depth = int(sys.argv[1])
width = int(sys.argv[2])

# Constants
REGISTRY = 'https://dtid.org/'                      # Base URL of DTID registry
DTID_BASE = REGISTRY \
    + datetime.now().strftime('%Y-%m-%d_%H:%M:%S_') # Base URL of DTIDs   

# Create a tree of DTs in advance so that adding parents and children is a bit easier
tree = {}
totalcount = 0
print('Creating tree with depth ' + str(depth) + ' and width ' + str(width))

def create_tree(current, depth: int, width: int, totalcount: int):
    dtid = DTID_BASE + str(uuid.uuid4()).split('-')[0]
    totalcount += 1
    current[dtid] = []
    if depth != 0:
        depth = depth-1
        for i in range(width):
            current[dtid].append({})
            _, totalcount = create_tree(current[dtid][i], depth, width, totalcount)
    return current, totalcount

twintree, totalcount = create_tree(tree, depth, width, totalcount)

# Create folder for the twins
foldername = 'twintree-' + datetime.now(timezone.utc).isoformat()
print('Twins are added to folder: ' + foldername + '/')
os.mkdir(foldername)

# Create the twin documents 
print('---- Creating ' + str(totalcount) + ' twin docs ----:')
creator_dtid = 'http://d-t.fi/juuso' # Parent for the first twin

def create_twins(current, parent):
    for dtid in current:
        print('Creating DT doc for: ' + dtid)
        doc = {}
        doc['dt-id'] = dtid
        doc['hosting-iri'] = 'autoassign'
        doc['name'] = generate_slug().replace('-', ' ').title()
        if parent == 'http://d-t.fi/juuso':
            doc['name'] = 'The Origin at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('The name of the first DT: ' + doc['name'])
        doc['description'] = lorem.sentence()

        # Add parent
        doc['relations'] = []
        doc['relations'].append({})
        doc['relations'][0]['dt-id'] = parent
        doc['relations'][0]['relationType'] = 'parent'

        # Add children
        if len(current[dtid]) > 0:
            for i in range(len(current[dtid])):
                for child in current[dtid][i]:
                    doc['relations'].append({})
                    doc['relations'][i+1]['dt-id'] = child
                    doc['relations'][i+1]['relationType'] = 'child'

        # Create folder for the new twin
        dtfolder = foldername + '/' + dtid.split('/')[3]
        os.mkdir(dtfolder)

        # Write the twin doc to a YAML file
        filename = dtfolder + '/index.yaml'
        with open (filename, 'w') as yamlfile:
            yaml.dump(doc, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # Create more twins in recursive loop
        for i in range(len(current[dtid])):
            create_twins(current[dtid][i], dtid)
    return dtid

origin_dtid = create_twins(twintree, creator_dtid)

print('Created ' + str(totalcount) + ' twins.')
print('Origin DT: ' + origin_dtid)

# Print the DT tree:
# pprint.pprint(twintree)
