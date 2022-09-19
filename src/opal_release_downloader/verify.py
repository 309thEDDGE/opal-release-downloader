import argparse
import glob
import hashlib
import os
import sys
import yaml

import tqdm
import colorama

from ._display import display, error, warn


def md5sum(filename):
    hash_ = hashlib.md5()

    file_size = os.path.getsize(filename)
    with tqdm.tqdm(total=file_size, unit='B', unit_scale=True,
            desc=filename) as tq:
        with open(filename, 'rb') as f:
            block = f.read(4096)
            bytes_read = len(block)

            while block:
                hash_.update(block)
                tq.update(bytes_read)

                block = f.read(4096)
                bytes_read = len(block)

    return hash_.hexdigest()


def check_checksums(checksum, *, excluded_files=[], strict=True):
    """
    notes:
    This should run from within the directory where the checksum file and
    rest of the files are
    """
    sums = {}
    with open(checksum, "r") as f:
        line = f.readline()

        while line:
            parts = line.strip().split()
            if len(parts) != 2:
                raise Exception(f'malformed line in {checksum}')

            filename = os.path.basename(parts[1])
            hash_ = parts[0]
            sums[filename] = hash_

            line = f.readline()

    print('verifying checksums')
    for root, dirs, files, in os.walk('.'):
        if dirs:
            cur_dir = os.path.join(os.getcwd(), root)
            raise Exception(f'unexpected directory layout in {cur_dir}')

        for f in files:
            if f in excluded_files:
                continue

            if not f in sums:
                if strict:
                    raise Exception(f'file "{f}" no checksum found.')
                else:
                    warn(f'WARNING: no checksum found for "{f}"')
                    continue

            sum_ = md5sum(f)
            if sum_ != sums[f]:
                raise Exception(f'file "{f}" checksum {sum_}')


def check_manifest(manifest, *, excluded_files=[]):
    """
    notes:
    This should run from within the directory where the manifest and files are

    This should fail for 2 reasons
    - a file is in the folder that shouldn't be there
    - a file is missing from the folder
    """

    with open(manifest, "r") as f:
        expected_files = yaml.load(f, Loader=yaml.SafeLoader)

    with tqdm.tqdm(desc='checking_manfiest', total=len(expected_files)) as tq:
        files_found = {}
        for f in expected_files:
            files_found[f] = False

        for root, dirs, files, in os.walk('.'):
            if dirs:
                cur_dir = os.path.join(os.getcwd(), root)
                raise Exception(f'unexpected directory layout in {cur_dir}')

            for f in files:
                if f in excluded_files:
                    continue

                if not  f in expected_files:
                    raise Exception(f'unexpected file "{f}" found')

                files_found[f] = True
                tq.update()

        for k, v in files_found.items():
            if not v:
                raise Exception(f'file "{k}" not found')


def verify_directory(
        directory, *,
        checksum=None,
        manifest=None,
        search=False,
        require_manifest=True,
        strict_checksum=True
        ):

    cur_dir = os.getcwd()

    if not os.path.exists(directory):
        raise Exception('Unable to find directory')

    if not os.path.isdir(directory):
        raise Exception (f'directory {directory} is not a valid directory')

    try:
        os.chdir(directory)

        if search and (checksum is None):
            files = glob.glob('md5sums_*')
            if len(files) != 1:
                raise Exception('Unable to find checksum file')
            checksum = files[0]

        if (not checksum) or (not os.path.exists(checksum)):
            raise Exception(f'checksum file {checksum} does not exist')

        if require_manifest:
            if search and (manifest is None):
                files = glob.glob("file_manifest_*.yml")
                if len(files) != 1:
                    raise Exception('Unable to find manifest file')
                manifest = files[0]

            if (not manifest) or (not os.path.exists(manifest)):
                raise Exception(f'manifest file {manifest} does not exist')

            check_manifest(manifest, excluded_files=[checksum])
            print()

        check_checksums(checksum, excluded_files=[checksum],
                strict=strict_checksum)

    finally:
        os.chdir(cur_dir)



def main():
    parser = argparse.ArgumentParser('verify_opal_artifacts')
    parser.add_argument('directory', help="names of local directory to verify")
    parser.add_argument("-s", "--search", default=False, action="store_true",
            help="search for checksum and manifest file")
    parser.add_argument("-c", "--checksum", help="name of checksum file",
            default=None)
    parser.add_argument("-m", "--manifest", help="name of manifest file",
            default=None)
    parser.add_argument("--no-manifest", help="do not require a manifest file",
            default=False, action='store_true')
    parser.add_argument("--relaxed-checksum", default=False,
            action="store_true",
            help="don't fail if a file is not in the checksum list")

    args = parser.parse_args()

    with display():
        try:
            verify_directory(args.directory,
                    checksum=args.checksum,
                    manifest=args.manifest,
                    search=bool(args.search),
                    require_manifest = not bool(args.no_manifest),
                    strict_checksum= not bool(args.relaxed_checksum))
        except Exception as e:
            error(f'FAILURE: {str(e)}')
            sys.exit(1)


if __name__ == '__main__':
    main()
