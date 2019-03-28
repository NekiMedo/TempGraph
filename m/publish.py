'''Publish graphs to a web server directory (or equivalent) somewhere across the network.
'''

# All rights reserved;  see LICENSE file

import ftplib
import os
import subprocess


class PublishGraphs( object ):
    'The base class defining an interface for varous implementations (FTP, SSH, etc)'
    def __init__( self, remote_host, remote_dir, credentials ):
        self.remote_host = remote_host
        self.remote_dir  = remote_dir
        self.username    = credentials[ 0 ]
        self.password    = credentials[ 1 ]

    def copy_files( self, file_list ):
        raise NotImplementedError()


class PublishGraphsSsh( PublishGraphs ):
    "Copy files using 'scp'"
    def __init__( self, remote_host, remote_dir, credentials ):
        super( PublishGraphsSsh, self ).__init__(  remote_host, remote_dir, credentials )

    def copy_files( self, file_list ):
        print 'PublishGraphsSsh copying files', file_list, 'to host', self.remote_host, 'dir', self.remote_dir
        for f in file_list:
            # FIXME use credentials instead of public key
            subprocess.Popen( ['scp', f, self.remote_host + ':' + self.remote_dir ] ).wait()


class PublishGraphsFtp( PublishGraphs ):
    'Copy files using FTP'
    def __init__( self, remote_host, remote_dir, credentials ):
        super( PublishGraphsFtp, self ).__init__(  remote_host, remote_dir, credentials )

    def copy_files( self, file_list ):
        # FIXME - switch to keyring-daemon for credentials
        #       - catch the connection exceptions
        session = ftplib.FTP( self.remote_host, self.username, self.password )
        for graph_file in file_list:
            dest_fname = os.path.basename( graph_file )
            with open( graph_file, 'rb' ) as fileobj:
                print '  ** About to FTP upload %s file -> %s' % (graph_file, dest_fname)
                #print 'cwd', session.pwd()                          # debug
                session.storbinary( 'STOR ' + dest_fname, fileobj ) # send the file
                fileobj.close()                                     # close the file
                
        session.quit()  # close the FTP session


def publish_graph_files( graph_names, credentials ):
    '''Use SSH/FTP to upload the specified files (a list) to the remote host'''
    if len( graph_names ) > 0:
        # check if we are behind the firewall (FTP can't get around it)
        behind_firewall = False # if 'someuser' == os.getenv( 'USER' ) or os.path.exists( '/home/someuser/' ) else True
        # FIXME move PATH/URL into the configuration file
        publisher = PublishGraphsSsh( 'deb-xeon', '/var/www/html/TempGraph/', credentials ) \
                       if behind_firewall else PublishGraphsFtp( 'home.exetel.com.au', '.', credentials )
        publisher.copy_files( graph_names )

