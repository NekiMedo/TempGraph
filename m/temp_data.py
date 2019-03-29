'''Manipulate temperature data file.
'''
# All rights reserved;  see LICENSE file

import datetime
import os

# NOTE Generating graphs requires gnuplot (gnuplot5) to be installed
#      On Debian: sudo apt install gnuplot5
#      FIXME runtime check: gnuplot is installed?

class TempDataFile( object ):
    '''Facilitate manipulation of temperature data file;
    e.g. append new data, extract the last N days of data points from the file etc
    '''
    def __init__( self, fname ):
        'fname -- the name of the file containing temperature data'
        self.fname = fname
        self.last_time = self.__find_last_timestamp()

    def extract_last_n_days( self, n_days ):
        '''If the file contains more data than we are interested in
        extract only the specified period into a separate file.
        Returns the extracted data file name.
        '''
        out_fname = str( self.fname + '.' + str( n_days ) )
        out_file = open( out_fname, 'w' )
        with open( self.fname, 'r' ) as f:
            for line in f:
                token = line.split()
                if len( token ) < 3:
                    continue
                timestamp =  token[ 0 ].strip()
                dt = datetime.datetime( int( timestamp [ 0 : 4] ),  # yyyy
                                        int( timestamp [ 4 : 6] ),  # mm
                                        int( timestamp [ 6 : 8] ),  # dd
                                        int( timestamp [ 8 : 10]) ) # hh
                days = (self.last_time - dt).days
                #print timestamp, 'days', (last_timestamp - dt).days
                if days < n_days:
                    out_file.write( line )
        out_file.flush()
        out_file.close()
        return out_fname

    def __find_last_timestamp( self ):
        '''Scan the whole file and find the last timestamp (1st column).
        Assumes the file is sorted by time/date i.e. the last line is
        the most recent time => FIXME optimise: skip all lines until the last
        Ignore minutes and secods, return datetime with hours
        '''
        if not os.path.exists( self.fname ):
            return 0
        last_timestamp = 0
        with open( self.fname, 'r' ) as f:
            for line in f:
                token = line.split()
                if len( token ) < 3:
                    continue
                timestamp =  token[ 0 ].strip()
                dt = datetime.datetime( int( timestamp [ 0 : 4] ),  # yyyy
                                        int( timestamp [ 4 : 6] ),  # mm
                                        int( timestamp [ 6 : 8] ),  # dd
                                        int( timestamp [ 8 : 10]) ) # hh
                last_timestamp = dt
        return last_timestamp

    def get_min_max_temperature( self ):
        '''Return the minimum and maximum temperatures logged.
        The 2nd column is air temperature.
        The 3rd column is apparent temperature (adjusted for wind factor)
        '''
        min_temp = 100
        max_temp = -100
        with open( self.fname, 'r' ) as data_file:
            for line in data_file:
                token = line.split()
                if len( token ) > 2:
                    air_temp = int( float( token[ 1 ].strip() ) + 0.5 )
                    apparent_temp = int( float( token[ 2 ].strip() ) + 0.5 )
                    for t in (air_temp, apparent_temp):
                        if min_temp > t:
                            min_temp = t
                        if max_temp < t:
                            max_temp = t
        return (min_temp, max_temp)

    def append_new_data( self, new_data ):
        '''Append new data points (retrieved from the BOM web page) to data file.
        new_data - a list of tuples (DATETIME, TEPMERATURE, APPARENT_TEMPERATURE)
        Note: apparent_temperature may not be available for all data sources, so
              we'll just duplicate the TEMPERATURE entry
        '''
        if len( new_data ) < 1:
            return
        first_new_timestamp = new_data[ 0 ][ 0 ]
        last_new_timestamp = new_data[ len( new_data ) - 1 ][ 0 ]
        last_old_timestamp = 0
        old_timestamp = 0
        with open( self.fname, 'a+' ) as data_file:
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
