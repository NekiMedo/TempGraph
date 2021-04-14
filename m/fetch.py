'''Fetch the latest temperature readings from the BOM web site.
TODO add support for other APIs (OpenWeater etc)
'''

# All rights reserved;  see LICENSE file

import json
# NOTE non-standard library:
import requests

#
# BOM started refusing GET requests without usual headers (15-Apr-2021)
#     so here we are, simulating Firefox
browser_headers = \
    {
        'User-Agent':      'Mozilla/5.0 (X11; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
        'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en,en-US;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer':         'http://www.bom.gov.au/nsw/observations/nswall.shtml',
        'DNT':             '1',
        'Connection':      'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control':             'max-age=0'
    }

def fetch_latest_temp_data( bom_url ):
    '''Retrieve JSON data from the specified URL (BOM web site).
    Return a list of tuples (DATETIME, TEPMERATURE, APPARENT_TEMPERATURE)
    '''
    temperature_readings = []
    try:
        r = requests.get( bom_url, headers=browser_headers )
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
