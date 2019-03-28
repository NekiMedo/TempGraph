#!/usr/bin/env python
# All rights reserved;  see LICENSE file
import argparse
import os
import sys

#
# NOTE
#  - required nonstandard libraries:
#       - python-gnuplot (Gnuplot)  see m.graph.py
#       - python-requests           see m.fetch.py
#
# ALSO Generating graphs requires gnuplot (gnuplot5) to be installed
#      On Debian: sudo apt install gnuplot5
#

# support (homebrewed) modules
from m.locations_cfg import LocationsConfig
from m.graph         import create_graph
from m.fetch         import fetch_latest_temp_data
from m.publish       import publish_graph_files


Namespace = argparse.Namespace  # alias


def append_new_data( new_data, fname ):
    '''Append new data points (retrieved from the BOM web page) to the given file.
    new_data - a list of tuples (DATETIME, TEPMERATURE, APPARENT_TEMPERATURE)
    Note: apparent_temperature may not be available for all data sources
    '''
    if len( new_data ) < 1:
        return
    first_new_timestamp = new_data[ 0 ][ 0 ]
    last_new_timestamp = new_data[ len( new_data ) - 1 ][ 0 ]
    last_old_timestamp = 0
    old_timestamp = 0
    with open( fname, 'a+' ) as data_file:
        for line in data_file:
            token = line.split()
            if len( token ) > 2:
                old_timestamp = int( token[ 0 ].strip() )
        for timestamp, air_temp, apparent_temp in new_data:
            if timestamp <= old_timestamp:
                continue
            if apparent_temp is None:  # sometimes BOM don't supply 'apparent temperature'
                apparent_temp = air_temp
            line = "%d %4.1f %4.1f\n" % (timestamp, air_temp, apparent_temp)
            data_file.write( line )


def process_cmd_line_args():
    '''Process command line arguments.
    Intended for iteractive use.
    '''
    parser = argparse.ArgumentParser( description='Fetch temperature data from the web, generate graphs' )
    parser.add_argument( '-v', '--verbose', help='verbose output', action='store_true' )
    parser.add_argument( '-l', '--loop',    help='run in a loop instead of a single shot', action='store_true' )
    parser.add_argument( '-c', '--config',  help='use the specified config (JSON) file',
                         default='locations.json', action='store' )
    args = parser.parse_args()

    if args.config  and  not os.path.exists( args.config ):
        print 'ERROR: cannot find', args.config, 'configuration file'
        sys.exit( 0 )
    return args


def graph_file_path( dir_name, datafile_name ):
    '''Compose the full graph file path, given the directory name and the
    temperature data file name'''
    return os.path.join( dir_name,
                         os.path.basename( os.path.splitext( datafile_name )[ 0 ] )
                         + '.png' )

# Need (username, pwd) to publish graphs on the web server etc.
# Whether the graphs are published is controlled by 'publish_graphs'
# configuration file flag (defaults to 'false').
# FIXME replace with gnome-keyring-daemon to store credentials 
credentials = ('usename', 'secret_password' )

def main():
    args = process_cmd_line_args()
    print 'INFO using config:', args.config, ', loop', args.loop
    cfg = LocationsConfig( args.config ).get()

    graphs_to_upload = []
    for location in cfg.locations:
        loc = Namespace( **location ) 
        graph_path = graph_file_path( cfg.graph_dir, loc.data )
        print '\n', loc.url, '\n  graph_path: ', graph_path
        if hasattr( loc, 'skip_fetch' ) and loc.skip_fetch:
            print 'INFO: SKIPPING data fetch step'  # need adapter for the other API
        else:
            append_new_data( fetch_latest_temp_data( loc.url ), loc.data )

        if create_graph( loc.title, loc.data, graph_path ) and  loc.web_dir is not None:
            graphs_to_upload.append( graph_path )

    if cfg.publish_graphs:
        # NOTE the 'credentials'' above will need to be correct
        publish_graph_files( graphs_to_upload, credentials )


if __name__ == '__main__':
    main()
