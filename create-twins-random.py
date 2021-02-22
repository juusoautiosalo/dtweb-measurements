import sys, uuid, os, random, yaml, lorem
from datetime import datetime, timezone
from coolname import generate_slug


def generate_dtids(registry: str, number: int) -> list:
    """
    Generate a list of DTIDs.

    Args:
      number: The number of generated DTIDs.
      registry: Base URL of the DTID registry.

    Returns:
      List of DTIDs

    """
    dtids = []

    for _ in range(number):
        dtids.append(registry + str(uuid.uuid4()))

    return dtids

# Receive user input argument for number of twins
number = int(sys.argv[1])


# Constants
REGISTRY = 'https://dtid.org/'          # Base URL of DTID registry
RELATION_TYPES = ['child', 'parent']    # Acceptable relations to other twins
RELATION_COUNTS = [0, 1, 2]             # Distribution for number of relations of one twin

# Make sure user has requested enough twins to be able to make meaningful relations
try:
    assert number > max(RELATION_COUNTS)
except AssertionError:
    print('ERROR: Try with more than ' + str(max(RELATION_COUNTS)) + ' twins!')
    raise
print('Generating ' + str(number) + ' randomly generated twin docs.')

# Create folder for the twins
foldername = datetime.now(timezone.utc).isoformat()[:-3]
print('Twins are added to folder: ' + foldername + '/')
os.mkdir(foldername)

# Generate list of DTIDs
dtids = generate_dtids(REGISTRY, number)

# Create twin docs
for dtid in dtids:
    doc = {}
    doc['dtid'] = dtid
    doc['hosting-iri'] = 'autoassign'
    doc['name'] = generate_slug().replace('-', ' ').title()
    doc['description'] = lorem.sentence()
    relationCount = random.choice(RELATION_COUNTS)
    if relationCount > 0:
        doc['relations'] = []
        for i in range(relationCount):
            doc['relations'].append({})
            doc['relations'][i]['dtid'] = random.choice(dtids)
            # Make sure not to create relation to itself 
            # (Multiple relations to same twin are ok for now)
            while doc['relations'][i]['dtid'] == dtid:
                doc['relations'][i]['dtid'] = random.choice(dtids)
            doc['relations'][i]['relationType'] = random.choice(RELATION_TYPES)

    # Create folder for the new twin
    dtfolder = foldername + '/' + dtid.split('/')[3]
    os.mkdir(dtfolder)

    # Write the twin doc to a YAML file
    filename = dtfolder + '/index.yaml'
    with open (filename, 'w') as yamlfile:
        yaml.dump(doc, yamlfile, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print('Saved DT doc with ' + str(relationCount) + ' relations')
