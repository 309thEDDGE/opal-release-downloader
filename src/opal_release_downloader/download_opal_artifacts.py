#!/usr/bin/env python3

import pathlib
import os
import argparse
import boto3
from botocore.exceptions import ClientError
from botocore import UNSIGNED
from botocore.config import Config
import yaml
import shutil
import re
import hashlib

# This class provides utility functions to correctly download the proper s3 bucket 
class artifact_downloader():
    def __init__(self, bucket_name, release_tag):
        self.release_tag=release_tag
        self.bucket_name=bucket_name
        self.working_dir = pathlib.Path('.').resolve()
        self.downloaded_artifact_path = self.working_dir / "opal_artifacts"
        self.image_path = self.downloaded_artifact_path / "images"
        self.docker_binary_path = self.downloaded_artifact_path / "docker"
        self.rhel_iso_path = self.downloaded_artifact_path / "rhel"
        self.s3=boto3.client('s3',region_name='us-gov-west-1',config=Config(signature_version=UNSIGNED))
        self.check_directories_exist(self.downloaded_artifact_path)
        

    # This function checks to make sure the proper director exists
    def check_directories_exist(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        
    # downloads contents of images directory (images + opal-ops repo)
    def download_images(self):
        self.check_directories_exist(self.image_path)
        os.chdir(self.image_path)
        print("\n ------ Downloading Images ------")
        self.download_files(self.release_tag)
        print("  ---Images downloaded. Proceeding to validate checksums")
        image_hashfile = self.image_path / f"md5sums_{self.release_tag}"
        image_manifest = self.image_path / f"file_manifest_{self.release_tag}.yml"
        self.check_directory_has_expected_contents(image_manifest, image_hashfile, self.image_path)
        if not self.validate_checksums(image_hashfile, self.image_path):
            print(f"   --- Something went wrong while retrieving docker images")
        else:
            print(" === Docker images successfully validated ===")

    def download_scripts(self):
        os.chdir(self.downloaded_artifact_path)
        print("\n ------ Downloading Scripts ------")
        self.download_files("unpacker")
        print(" === Scripts successfully downloaded ===")

    # downloads docker and docker-compose binaries
    def download_docker_binaries(self):
        self.check_directories_exist(self.docker_binary_path)
        os.chdir(self.docker_binary_path)
        print("\n ------ Downloading Docker Binaries ------")
        self.download_files("docker")
        print("  --- All docker binaries downloaded. Proceeding to validate checksums")
        binary_hashfile = self.docker_binary_path / "md5checksum"
        if not self.validate_checksums(binary_hashfile, self.docker_binary_path):
            print(f"   --- Something went wrong while retrieving docker binaries")

    # This function wil download the basic rhel8 ISO image to work with our product
    def download_rhel_iso(self):
        self.check_directories_exist(self.rhel_iso_path)
        os.chdir(self.rhel_iso_path)
        #use download_files function
        print("\n ------ Downloading Rhel ISO ------")
        s3_dir = 'redhat-iso'
        self.download_files(s3_dir)
        rhel_hashfile =  self.rhel_iso_path / "md5checksum"
        if not self.validate_checksums(rhel_hashfile, self.rhel_iso_path):
            print(f"   --- Something went wrong while retrieving rhel image")
        

    #just a generic download function. Downloads from whatever directory in s3 it's told to 
    # download from
    def download_files(self, s3_dir):
        for item in self.s3.list_objects_v2(Bucket=self.bucket_name,Prefix=s3_dir)['Contents']:
            file_name = item['Key'].split('/')[-1]
            print(f"  - {file_name}")
            if pathlib.Path(file_name).is_file():
                print(f"  - {file_name} already exists. skipping.")
                continue
            try:
                self.s3.download_file(self.bucket_name,item['Key'],item['Key'].split('/')[-1])
            except Exception as e:
                print(e)

    # This function will check the MD5sum hash against a proper working and known checksum list
    def validate_checksums(self, hashfile, working_path):
        os.chdir(working_path)
        print(f"\n ------ Beginning Checksum Validation for {working_path} ------")
        # assume success, so any single failure will result in a negative result
        validation_passed = True
        with open(hashfile, "r") as f:
            for line in f:
                cols = line.split()
                old_hash = cols[0]
                raw_filename = cols[-1].split('/')[-1]
                in_file = self.downloaded_artifact_path / raw_filename
                print(f" ----- Validating {raw_filename} -----")
                print(f"  --- Original filehash: {old_hash}")
                new_hash = self.generate_checksum(in_file.name) 
                print(f"  --- New filehash: {new_hash}")
                if str(old_hash) != str(new_hash):
                    print(f"  === File {raw_filename} failed validation\n")
                    validation_passed = False
                else:
                    print(f"  === File {raw_filename} successfully validated\n")
        return validation_passed

    def check_directory_has_expected_contents(self, manifest_file, hashfile, working_path):
        os.chdir(working_path)
        # we need this filename to add as an exclusion, since it is not part of the manifest
        hash_name = hashfile.name
        print("\n ------ Checking directory has only the expected files ------")
        try:
            with open(manifest_file , 'r') as m:
                manifest = yaml.safe_load(m)
                for file in working_path.glob('*'):
                    if not (file.name == hash_name or file.name in manifest):
                        raise Exception(f"ERROR: Found unexpected file: {file.name}.\nHalting execution. Delete all downloaded files and try again")
                print(" === No unexpected files found")
        except Exception as e:
            print(str(e))
            exit(1)
            

    # This function will generate a checksum for a specific file to be later validated against a known list of working checksums
    def generate_checksum(self, filename):
        print("  --- Generating checksum")
        #create a variable and make it the path of the file you need to create a checksum for
        #create hash object and use hashlib.md5() function to generate the hashsum
        hasher = hashlib.md5()
        #need to open the file and read the contents while passing them to the hash object 
        read_size_byte = int(100e6)
        with open(filename, 'rb') as open_file:
            observed_read_size = read_size_byte
            while observed_read_size == read_size_byte:
                #store contents of open file
                content = open_file.read(read_size_byte)
                hasher.update(content)
                observed_read_size = len(content)
        return hasher.hexdigest()


# Simple function to run a yes/no input when user is tasked with a choice
def yes_no():
    valid_input = False
    in_bool=False
    while not valid_input:
        try:
            reply = str(input()).lower()
            if reply == 'y' or reply == '': 
                in_bool=True
                valid_input = True
            elif reply == 'n':
                in_bool = False
                valid_input = True
            else: raise Exception("Unrecognized input, please try again")
        except Exception as e:
            print(str(e))
            continue
    return in_bool
    
def validate_release_format(tag: str) -> bool:
    date_match = re.match(r'^[0-9]{4}\.(0[1-9]|1[0-2])\.(0[1-9]|[1-2][0-9]|3[0-1])$', tag)
    if not date_match:
        print("Please enter the tag in the correct format: yyyy.mm.dd")
        return False
    return True

def cli_get_args():
    parser = argparse.ArgumentParser(description='Download OPAL artifacts')
    parser.add_argument('bucket_name', help='Name of S3 bucket in which OPAL artifacts reside')
    parser.add_argument('release_tag', help='OPAL release tag to be downloaded, in YYYY.MM.DD form')
    parser.add_argument('--no-docker', help='Do not download binaries for docker', 
        action='store_true', default=False)
    parser.add_argument('--no-rhel', help='Do not download a vetted RHEL8 ISO image',
        action='store_true', default=False)

    args = parser.parse_args()
    return args

def run_downloader():
    args = cli_get_args()
    bucket = args.bucket_name
    tag = args.release_tag
    if validate_release_format(tag):
    
        dl = artifact_downloader(bucket, tag)
        dl.download_images()
        dl.download_scripts()
        if not args.no_docker:
            dl.download_docker_binaries()
        if not args.no_rhel:
            dl.download_rhel_iso()

