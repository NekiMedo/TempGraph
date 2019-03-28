'''Use gnuplot to generate *.png graphs from temperature readings (ASCII text)
'''
# All rights reserved;  see LICENSE file

import datetime
import os
# NOTE nonstandard library (python-gnuplot package under Debian)
import Gnuplot

# NOTE Generating graphs requires gnuplot (gnuplot5) to be installed
#      On Debian: sudo apt install gnuplot5
#      FIXME runtime check: gnuplot is installed?

class TempDataFile( object ):
    '''Facilitate manipulation of temperature data file;
    e.g. extract only the last N days of data points from the data file.
    '''
    def __init__( self, fname ):
        '''
        fname -- the name of the file containing data
        '''
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

        #if type( out_fname ) is not types.StringType:  # FIXME rm: name needs to be a string
        #    print out_fname, 'is not a string'
        return out_fname

    def __find_last_timestamp( self ):
        '''Scan the whole file and find the last timestamp (1st column).
        Assumes the file is sorted by time/date i.e. the last line is
        the most recent time => FIXME optimise: skip all lines until the last
        Ignore minutes and secods, return datetime with hours
        '''
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


# FIXME make this a TempDataFile member    
def get_min_max_temperature( fname ):
    '''Return the minimum and maximum temperatures logged in fname file.
    The 2nd column is air temperature.
    The 3rd column is apparent temperature (adjusted for wind factor)
    '''
    # FIXME check the file exists
    min_temp = 100
    max_temp = -100
    with open( fname, 'r' ) as data_file:
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



def create_graph( graph_title, data_file, graph_file ):
    '''Create PNG graph out of passed data using Gnuplot Python wrapper around
    bare gnuplot
    '''
    if not os.path.exists( data_file ):
        print '\nWARNING: cannot find %s data file; skipping it\n' % data_file
        return False 
    
    data = TempDataFile( data_file )
    seven_days_data = data.extract_last_n_days( 7 )

    min_temp, max_temp = get_min_max_temperature( seven_days_data )
    floor = int( float( min_temp ) / 10 ) * 10
    ceil  = ( 1 + int( max_temp / 10 )) * 10
    if min_temp < 0:
        floor -= 10

    g = Gnuplot.Gnuplot( debug=0 )  # set debug=1 for verbose run
    g.title( graph_title )
    g( 'set xdata time' )
    g( 'set style data lines' )
    g( 'set term png size 1200, 900' )
    g( 'set timefmt "%Y%m%d%H%M%S"' )   # date format int the FILE
    g( 'set ylabel "temperature" ' )
    g( 'set yrange [ "%d" : "%d" ]' % (floor, ceil) )  # dynamically adjust min/max temperature scale
    g( 'set grid' )
    g( 'set bmargin 6' )
    g( 'set xtics rotate by 90 offset 0, -4.8' )
    g( 'set xtics format "%d-%b %H:%M" time' )      # date/time format on the GRAPH
    g( 'set linetype 1 linecolor rgb "#C00000"' )
    g( 'set linetype 2 linecolor rgb "0x0000C0"' )
    g( 'set output "%s"' % graph_file )
    #f = Gnuplot.File( data_file, using='1:2 t "air temp.", "" u 1:3 t "apparent temp."' )
    f = Gnuplot.File( seven_days_data, using='1:2 t "air temp.", "" u 1:3 t "apparent temp."' )
    g.plot( f )
    return True
