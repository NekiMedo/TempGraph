'''Fetch the latest temperature readings from BOM web site.
TODO add support for other APIs (OpenWeater etc)

All rights reserved;  see LICENSE file
'''
import json

# NOTE non-standard library:
import requests

def fetch_latest_temp_data( bom_url ):
    '''Retrieve JSON data from the specified URL (BOM web site).
    Return a list of tuples (DATETIME, TEPMERATURE, APPARENT_TEMPERATURE)
    '''
    r = requests.get( bom_url )
    data = r.json()
    obs = data[ 'observations' ]
    temp_readings = []
    for i in obs[ 'data' ]:
        temp_readings.append( ( int( i[ "local_date_time_full" ] ), i[ 'air_temp' ], i[ 'apparent_t' ] ) )
        # the received data is: 'the latest temp. reading first'
        # we want the reverse order
    temp_readings.reverse()
    return temp_readings
