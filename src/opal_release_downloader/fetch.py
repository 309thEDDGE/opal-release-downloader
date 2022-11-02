import argparse
import boto3
import botocore as bc
import os
import sys

import tqdm

from ._constants import DEFAULT_REGION
from ._display import display, error, warn
from .list import get_latest, list_bucket_objects_get_s3_client

def get_files(bucket_name, path_spec, *,
        region_name=DEFAULT_REGION,
        dest=None):

    #TODO:  i think this shouldn't be so helpfull fetch.get_files(...)
    #       should always have a path_spec
    if path_spec is None:
        path_spec = get_latest(bucket_name, region_name=region_name)

    if dest is None:
        dest = os.path.dirname(path_spec)
        if not dest:
            dest = path_spec

    dest = os.path.realpath(dest)

    item_list, s3 = list_bucket_objects_get_s3_client(bucket_name, 
        prefix=path_spec, region_name=region_name)

    rel_dest = os.path.relpath(dest)
    print(f'Downloading files to {rel_dest}')
    for it in item_list:
        key = it['Key']
        size = it['Size']

        it_path = os.path.join(key.split('/')[-1])
        # local_name = os.path.realpath(os.path.join(dest, it_path))
        # local_dir = os.path.dirname(local_name)

        # os.makedirs(local_dir, exist_ok=True)
        # if not os.path.isdir(local_dir):
        #     raise RuntimeError(f'Unable to write to {local_dir}')

        # if os.path.exists(local_name):
        #     os.unlink(local_name)
        #     warn(f'WARNING: overwriting file {local_name}')

        # with tqdm.tqdm(total=size, unit='B', unit_scale=True, desc=it_path) as tq:
        #     def update(sz):
        #         tq.update(sz)

        #     s3.download_file(bucket_name, key, local_name, Callback=update)
    
def prepare_local_path(dest: str, s3_item: dict):
    key = s3_item['Key']
    item_path = os.path.join(key.split('/')[-1])
    local_name = os.path.realpath(os.path.join(dest, item_path))
    local_dir = os.path.dirname(local_name)

    os.makedirs(local_dir, exist_ok=True)
    if not os.path.isdir(local_dir):
        raise RuntimeError(f'Unable to write to {local_dir}')

    if os.path.exists(local_name):
        os.unlink(local_name)
        warn(f'WARNING: overwriting file {local_name}')

def s3_download_with_progress(s3_client, bucket_name: str, s3_key: str, 
    local_name: str, size: int):
    desc_path = os.path.basename(local_name)
    with tqdm.tqdm(total=size, unit='B', unit_scale=True, desc=desc_path) as tq:
        def update(sz):
            tq.update(sz)

        s3_client.download_file(bucket_name, s3_key, local_name, Callback=update)


def main():
    parser = argparse.ArgumentParser('fetch_opal_artifacts')
    parser.add_argument('bucket_name', help='name of bucket')
    parser.add_argument('path_spec', nargs='?', default=None, help="path_spec")
    parser.add_argument("--dest", "-d", help="destination directory")
    args = parser.parse_args()

    with display():
        try:
            get_files(args.bucket_name, args.path_spec, dest=args.dest)
        except Exception as e:
            error(f'FAILURE: {str(e)}')
            sys.exit(1)

if __name__ == '__main__':
    main()

