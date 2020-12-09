'''Publish graphs to a web server directory (or equivalent) somewhere across the network.
'''

# All rights reserved;  see LICENSE file

import ftplib
import os
import subprocess
import boto3


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

            
class PublishGraphsAwsS3( PublishGraphs ):
    "Copy files to the specified Amazon S3 bucket"
    def __init__( self, bucket, remote_dir, credentials ):
        super( PublishGraphsAwsS3, self ).__init__(  bucket, remote_dir, credentials )

    def copy_files( self, file_list ):
        '''
        file_list - a list of files to upload; the full path is specified
        '''
        s3 = boto3.resource( 's3' )
        bucket = s3.Bucket( self.remote_host )
        for f in file_list:
            dest_fname = os.path.basename( f )
            dest_path  = os.path.join( self.remote_dir, dest_fname )
            try:
                with open( f, 'rb') as fdata:
                    print ' ', f, '=>', dest_path
                    bucket.put_object( Key=dest_path, Body=fdata )
            except Exception, e:
                print '\nOOPS [S3]:', e


class PublishGraphsFtp( PublishGraphs ):
    'Copy files using FTP'
    def __init__( self, remote_host, remote_dir, credentials ):
        super( PublishGraphsFtp, self ).__init__(  remote_host, remote_dir, credentials )

    def copy_files( self, file_list ):
        # FIXME - switch to keyring-daemon for credentials
        try:
            session = ftplib.FTP( self.remote_host, self.username, self.password )
            for graph_file in file_list:
                #  9-DEC-2020: Exetel misconfigured the FTP server so now needs 'public_html' prefix:
                # 10-DEC-2020 - they reverted the configuration after i've notified them
                #dest_fname = 'public_html/' + os.path.basename( graph_file )
                dest_fname = os.path.basename( graph_file ) 
                with open( graph_file, 'rb' ) as fileobj:
                    print '  ** About to FTP upload %s file -> %s' % (graph_file, dest_fname)
                    #print 'cwd', session.pwd()                          # debug
                    session.storbinary( 'STOR ' + dest_fname, fileobj ) # send the file
                    fileobj.close()                                     # close the file

            session.quit()  # close the FTP session
        except Exception, e:
            print '\nERROR: PublishGraphsFtp; %s\n' % e


def publish_graph_files( upload_method, graph_names, credentials ):
    '''Use SSH/FTP/AwsS3 to upload the specified files (a list) to the remote host'''
    if len( graph_names ) > 0:
        if upload_method == 'S3':
            publisher = PublishGraphsAwsS3( 'mala-sova-pub', 'TemperatureGraphs', credentials )
        elif upload_method == 'FTP':
            publisher = PublishGraphsFtp( 'home.exetel.com.au', '.', credentials )
        elif upload_method == 'SCP':
            publisher = PublishGraphsSsh( 'deb-xeon', '/var/www/html/TempGraph/', credentials ) 
        else:
            print 'ERROR; publish_graph_files(): wrong upload method', upload_method
            return
        publisher.copy_files( graph_names )

