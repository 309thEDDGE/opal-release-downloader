import argparse
import boto3
import datetime
import sys
import json

import botocore as bc

from ._constants import DEFAULT_REGION
from ._date import date, date_fmt, date_tag
from ._display import display, error

def list_bucket_objects(bucket_name: str, *, prefix: str='', 
    region_name: str=DEFAULT_REGION) -> dict:
    s3 = boto3.client('s3', region_name=region_name,
            config=bc.config.Config(signature_version=bc.UNSIGNED))
    obj_list = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if obj_list['KeyCount'] == 0:
        raise RuntimeError('No objects found')
    return obj_list['Contents']

def get_list(bucket_name, *, region_name=DEFAULT_REGION):
    obj_list = list_bucket_objects(bucket_name, region_name=region_name)
    s = set()
    for o in obj_list:
        try:
            key = o['Key'].split('/')[0]
            s.add(date(key))
        except:
            continue

    return ( date_fmt(dt) for dt in sorted(s, reverse=True) )

def print_list(bucket_name, *, region_name=DEFAULT_REGION):
    for dt in get_list(bucket_name, region_name=region_name):
        print(dt)

def get_all(bucket_name, *, prefix='', region_name=DEFAULT_REGION):
    obj_list = list_bucket_objects(bucket_name, prefix=prefix,
       region_name=region_name)
    return obj_list

def print_all(bucket_name, *, prefix='', region_name=DEFAULT_REGION):
    obj_list = get_all(bucket_name, prefix=prefix, region_name=region_name)
    json.dump(obj_list, sys.stdout, indent=2, default=str)

def print_files(bucket_name, *, prefix='', region_name=DEFAULT_REGION):
    obj_list = get_all(bucket_name, prefix=prefix, region_name=region_name)
    for o in obj_list:
        print(o['Key'])


def get_latest(bucket_name, *, region_name=DEFAULT_REGION):
    return next(get_list(bucket_name, region_name=region_name))

def main():
    parser = argparse.ArgumentParser('list_opal_artifacts')
    parser.add_argument('bucket_name', help="name of s3 bucket")
    parser.add_argument('path_spec', nargs='?', default=None, help="path_spec")
    parser.add_argument('--all', '-a', help='show all', action='store_true',
            default=False)
    args = parser.parse_args()


    with display():
        try:
            if args.all:
                print_all(args.bucket_name)
                return
            elif args.path_spec:
                print_files(args.bucket_name, prefix=date_tag(args.path_spec))
                return

            print_list(args.bucket_name)
        except Exception as e:
            error(f'FAILURE: {str(e)}')
            sys.exit(1)

if __name__ == '__main__':
    main()

