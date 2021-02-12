import dtweb
import time

# Run measurement
dtid = 'http://d-t.fi/konecranes-K16052'
start = time.time()
host_url = dtweb.client.fetch_host_url(dtid)
end = time.time()

# Print measurement result
print()
print('Time elapsed for fetching the hosting URL of "' + dtid + '":')
print(end-start)
print()
