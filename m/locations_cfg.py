'''Load the JSON configuration file (default: locations.json)
'''
import argparse
import json
import os

Namespace = argparse.Namespace  # alias

class LocationsConfig( object ):
    'Return configuration from the specified JSON file'

    def __init__( self, fname='locations.json' ):
        with open( fname, 'r' ) as f:
            self.data = json.loads( f.read() )
            if 'graph_dir' not in self.data:
                self.data[ 'graph_dir' ] = 'Graphs'
            if not os.path.exists( self.data[ 'graph_dir' ] ):
                print 'ERROR: directory does not exist:', self.data[ 'graph_dir' ], '; using /tmp'
                graph_dir = '/tmp'  # NOTE create directory instead?

    def get( self ):
        return Namespace( **(self.data) )
