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
from m.temp_data     import TempDataFile
from m.fetch         import fetch_latest_temp_data
from m.publish       import publish_graph_files


Namespace = argparse.Namespace  # alias


def process_cmd_line_args():
    '''Process command line arguments.
    Intended for iteractive use.
    '''
    parser = argparse.ArgumentParser( description='Fetch temperature data from the web, generate graphs' )
    parser.add_argument( '-v', '--verbose', help='verbose output', action='store_true' )
    parser.add_argument( '-l', '--loop',    help='run in a loop instead of a single shot', action='store_true' )
    parser.add_argument( '-c', '--config',  help='use the specified config (JSON) file',
                         default='locations.json', action='store' )
    # FIXME add -n option to skip uploading graphs
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
#credentials = ('username', 'secret_password' )

def main():
    args = process_cmd_line_args()
    print 'INFO using config:', args.config, ', loop', args.loop
    cfg = LocationsConfig( args.config ).get()
    if cfg.upload_method == "S3":
        print cfg.method_S3
    elif cfg.upload_method == "FTP":
        print cfg.method_FTP
    elif cfg.upload_method == "SCP":
        print cfg.method_SCP
    else:
        print "oops"
        sys.exit( 1 )
    #sys.exit( 0 )

    graphs_to_upload = []
    for location in cfg.locations:
        loc = Namespace( **location )
        if hasattr( loc, 'skip') and loc.skip:
            print '  ** SKIPPING over', os.path.basename( loc.data )
            continue
        graph_path = graph_file_path( cfg.graph_dir, loc.data )
        print '\n', loc.url, '\n  graph_path: ', graph_path
        temp_data = TempDataFile( loc.data )
        temp_data.append_new_data( fetch_latest_temp_data( loc.url ) )
        if create_graph( loc.title, temp_data, graph_path ) and  loc.web_dir is not None:
            graphs_to_upload.append( graph_path )

    if cfg.publish_graphs:
        print '\nUsing: ', cfg.upload_method, '\n'
        # NOTE the 'credentials'' above will need to be correct
        publish_graph_files( cfg.upload_method, graphs_to_upload, credentials )


if __name__ == '__main__':
    main()
