import pytest 
from unittest.mock import patch, Mock, call

from opal_release_downloader.list import *

import opal_release_downloader._date as _date
import sys
import boto3
import botocore
import json

@pytest.fixture
def list_bucket_objects_config():
    bucket_name = 'my bucket'
    config_retval = 'config'
    region_name = 'here and there'
    prefix = 'a preefix'
    list_objects_dict = {'KeyCount': 3, 'Contents': [
        {'Key': '2022.10.01/file1.txt'},
        {'Key': '2022.10.01/my.yaml'},
        {'Key': '2022.04.05/other.data'}]}
    return [bucket_name, config_retval, region_name, prefix, 
        list_objects_dict]

class TestList():

    @patch('botocore.config')
    @patch('boto3.client')
    def test_list_bucket_objects(self, mock_boto3, mock_botocore, 
        list_bucket_objects_config):
        (bucket_name, config_retval, region_name, prefix, 
            list_objects_dict) = list_bucket_objects_config

        mock_botocore.Config.return_value = config_retval

        mock_s3_client = Mock()
        mock_s3_client.list_objects_v2.return_value = list_objects_dict

        mock_boto3.return_value = mock_s3_client

        test_obj_dict = list_bucket_objects(bucket_name, prefix=prefix, 
            region_name=region_name)

        mock_botocore.Config.assert_called_with(
            signature_version=botocore.UNSIGNED)
        mock_botocore.Config.assert_called_once()

        mock_s3_client.list_objects_v2.assert_called_with(
            Bucket=bucket_name, Prefix=prefix)
        mock_s3_client.list_objects_v2.assert_called_once()

        mock_boto3.assert_called_once()
        mock_boto3.assert_called_with('s3', region_name=region_name,
            config=config_retval)

        assert test_obj_dict == list_objects_dict['Contents']


    @patch('botocore.config')
    @patch('boto3.client')
    def test_list_bucket_objects_no_objects_found(self, mock_boto3, 
        mock_botocore, list_bucket_objects_config):

        (bucket_name, config_retval, region_name, prefix, 
            list_objects_dict) = list_bucket_objects_config
        
        # Modify keycount so exception is raised
        list_objects_dict['KeyCount'] = 0

        mock_botocore.Config.return_value = config_retval

        mock_s3_client = Mock()
        mock_s3_client.list_objects_v2.return_value = list_objects_dict

        mock_boto3.return_value = mock_s3_client

        with pytest.raises(RuntimeError):
            test_obj_dict = list_bucket_objects(bucket_name, prefix=prefix, 
                region_name=region_name)

        mock_botocore.Config.assert_called_with(
            signature_version=botocore.UNSIGNED)
        mock_botocore.Config.assert_called_once()

        mock_s3_client.list_objects_v2.assert_called_with(
            Bucket=bucket_name, Prefix=prefix)
        mock_s3_client.list_objects_v2.assert_called_once()

        mock_boto3.assert_called_once()
        mock_boto3.assert_called_with('s3', region_name=region_name,
            config=config_retval)


    @patch('opal_release_downloader.list.list_bucket_objects')
    def test_get_list(self, mock_list_bucket_objects, 
        list_bucket_objects_config):
        (bucket_name, _, region_name, _, 
            list_objects_dict) = list_bucket_objects_config

        mock_list_bucket_objects.return_value = list_objects_dict['Contents']

        s = set()
        for o in list_objects_dict['Contents']:
            key = o['Key'].split('/')[0]
            s.add(_date.date(key))
        expected = [ _date.date_fmt(dt) for dt in sorted(s, reverse=True) ]

        test_tuple = get_list(bucket_name, region_name=region_name)

        mock_list_bucket_objects.assert_called_with(
            bucket_name, region_name=region_name)
        mock_list_bucket_objects.assert_called_once()

        index = 0
        for test_val in test_tuple:
            assert index < len(expected)
            assert expected[index] == test_val
            index += 1
        assert index == len(expected)

    @patch('builtins.print')
    @patch('opal_release_downloader.list.get_list')
    def test_print_list(self, mock_get_list, mock_print, 
        list_bucket_objects_config):
        (bucket_name, _, region_name, _, _) = list_bucket_objects_config

        ret_list = [1, 2, 3]
        mock_get_list.return_value = ret_list
        expected_calls = [call(x) for x in ret_list]

        print_list(bucket_name, region_name=region_name)

        mock_get_list.assert_called_with(bucket_name, region_name=region_name)
        mock_get_list.assert_called_once()
        assert mock_print.mock_calls == expected_calls

    @patch('opal_release_downloader.list.list_bucket_objects')
    def test_get_all(self, mock_list_bucket_objects, 
        list_bucket_objects_config):
        (bucket_name, _, region_name, prefix, 
            list_objects_dict) = list_bucket_objects_config

        mock_list_bucket_objects.return_value = list_objects_dict['Contents']

        obj_list = get_all(bucket_name, prefix=prefix, 
            region_name=region_name)

        mock_list_bucket_objects.assert_called_with(bucket_name, 
            prefix=prefix, region_name=region_name)
        mock_list_bucket_objects.assert_called_once()

        assert obj_list == list_objects_dict['Contents']

    @patch('json.dump')
    @patch('opal_release_downloader.list.get_all')
    def test_print_all(self, mock_get_all, mock_json,
        list_bucket_objects_config):
        (bucket_name, _, region_name, prefix, 
            list_objects_dict) = list_bucket_objects_config

        mock_get_all.return_value = list_objects_dict['Contents']

        obj_list = print_all(bucket_name, prefix=prefix, 
            region_name=region_name)

        mock_get_all.assert_called_with(bucket_name, 
            prefix=prefix, region_name=region_name)
        mock_get_all.assert_called_once()

        mock_json.assert_called_with(list_objects_dict['Contents'],
            sys.stdout, indent=2, default=str)
        mock_json.assert_called_once()

    @patch('builtins.print')
    @patch('opal_release_downloader.list.get_all')
    def test_print_files(self, mock_get_all, mock_print,
        list_bucket_objects_config):
        (bucket_name, _, region_name, prefix, 
            list_objects_dict) = list_bucket_objects_config

        mock_get_all.return_value = list_objects_dict['Contents']

        expected_calls = [call(x['Key']) for x in 
            list_objects_dict['Contents']]

        print_files(bucket_name, prefix=prefix, 
            region_name=region_name)

        mock_get_all.assert_called_with(bucket_name, 
            prefix=prefix, region_name=region_name)
        mock_get_all.assert_called_once()
        assert mock_print.mock_calls == expected_calls

    @patch('opal_release_downloader.list.get_list')
    def test_get_latest(self, mock_get_list,
        list_bucket_objects_config):
        (bucket_name, _, region_name, _, _) = list_bucket_objects_config

        ret_vals = ['a', 'b', 'c']
        mock_get_list.return_value = ( x for x in ret_vals )

        result = get_latest(bucket_name, region_name=region_name)
        mock_get_list.assert_called_with(bucket_name, 
            region_name=region_name)
        mock_get_list.assert_called_once()
        assert result == ret_vals[0] 

        result = get_latest(bucket_name, region_name=region_name)
        assert result == ret_vals[1] 