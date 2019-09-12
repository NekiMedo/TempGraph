'''Use gnuplot to generate *.png graphs from temperature readings (ASCII text)
'''
# All rights reserved;  see LICENSE file

import os
from temp_data import TempDataFile
# NOTE nonstandard library (python-gnuplot package under Debian)
import Gnuplot

# NOTE Generating graphs requires gnuplot (gnuplot5) to be installed
#      On Debian: sudo apt install gnuplot5
#      FIXME runtime check: gnuplot is installed?


def create_graph( graph_title, temp_data_file, graph_file ):
    '''Create a PNG graph out of passed data using Gnuplot Python wrapper around
    bare gnuplot utility
    '''
    if not os.path.exists( temp_data_file.fname ):
        print '\nWARNING no data in %s file yet\n' % temp_data_file.fname
        return False
    seven_days_data = temp_data_file.extract_last_n_days( 7 )
    min_temp, max_temp = TempDataFile( seven_days_data ).get_min_max_temperature()
    floor = int( float( min_temp ) / 10 ) * 10
    ceil  = ( 1 + int( max_temp / 10 )) * 10
    if min_temp < 0:
        floor -= 10

    g = Gnuplot.Gnuplot( debug=0 )  # set debug=1 for a verbose run
    g.title( graph_title )
    g( 'set xdata time' )
    g( 'set style data lines' )
    g( 'set term png size 1200, 900' )
    g( 'set timefmt "%Y%m%d%H%M%S"' )   # date format int the FILE
    g( 'set ylabel "temperature" ' )
    g( 'set yrange [ "%d" : "%d" ]' % (floor, ceil) )  # dynamically adjust min/max temperature scale
    g( 'set grid' )
    g( 'set bmargin 6' )
    g( 'set xtics rotate by 90 offset 0, -5.4' )    # 4.8 => 5.4 (label offset)
    g( 'set xtics format "%d-%b %H:%M" time' )      # date/time format on the GRAPH
    g( 'set linetype 1 linecolor rgb "#C00000"' )
    g( 'set linetype 2 linecolor rgb "0x0000C0"' )
    g( 'set output "%s"' % graph_file )
    f = Gnuplot.File( seven_days_data, using='1:2 t "air temp.", "" u 1:3 t "apparent temp."' )
    g.plot( f )
    return True
