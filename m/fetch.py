'''Fetch the latest temperature readings from the BOM web site.
TODO add support for other APIs (OpenWeater etc)
'''

# All rights reserved;  see LICENSE file

import json
# NOTE non-standard library:
import requests

def fetch_latest_temp_data( bom_url ):
    '''Retrieve JSON data from the specified URL (BOM web site).
    Return a list of tuples (DATETIME, TEPMERATURE, APPARENT_TEMPERATURE)
    '''
    temperature_readings = []
    try:
        r = requests.get( bom_url )
        data = r.json()
        obs = data[ 'observations' ]
        for i in obs[ 'data' ]:
            temperature_readings.append( ( int( i[ "local_date_time_full" ] ), i[ 'air_temp' ], i[ 'apparent_t' ] ) )
        # the received data is: 'the latest temperature reading first'
        # we want it in reverse order:
        temperature_readings.reverse()
        #for r in temperature_readings: # just debugging
        #    print r
    except Exception, e:
        print '\nERROR: fetch_latest_temp_data;', e
    return temperature_readings
