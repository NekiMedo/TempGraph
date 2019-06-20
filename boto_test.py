#!/usr/bin/env python

import boto3  # NOTE: also needs AWS credentials 
import os

# Generated bucket policy (read objects) at https://awspolicygen.s3.amazonaws.com/policygen.html
# and pasted it in Bucket / Permisions / Policy
# see also https://stackoverflow.com/questions/19176926/how-to-make-all-objects-in-aws-s3-bucket-public-by-default
# {
#     "Id": "Policy1560986221168",
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "Stmt1560986213413",
#             "Action": [
#                 "s3:GetObject"
#             ],
#             "Effect": "Allow",
#             "Resource": "arn:aws:s3:::mala-sova-pub/*",
#             "Principal": "*"
#         }
#     ]
# }


s3 = boto3.resource( 's3' )
#for bucket in s3.buckets.all():
    #print bucket.name


graphs = [ 'thredbo_temp', 'perisher_temp', 'liawenee', 'butlers_gorge',
              'cape_naturaliste', 'cape_leeuwin',
              'syd_airport', 'homebush', 'coona_temp', ]
for l in graphs:
    fname = l + '.png' 
    path = os.path.join( 'Graphs', fname )
    dest_path = os.path.join( 'TemperatureGraphs', fname )
    try:
        with open( path, 'rb') as fdata:
            print path, '=>', dest_path
            s3.Bucket( 'mala-sova-pub' ).put_object( Key=dest_path, Body=fdata )
    except Exception, e:
        print '\nOOPS [S3]:', e


