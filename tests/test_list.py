import pytest 
import boto3
import botocore
from unittest.mock import patch, Mock

from opal_release_downloader.list import *
import opal_release_downloader._date as _date

class TestList:

    @patch('botocore.config')
    @patch('boto3.client')
    def test_list_bucket_objects(self, mock_boto3, mock_botocore):
        bucket_name = 'my bucket'
        config_retval = 'config'
        region_name = 'here and there'
        prefix = 'a preefix'
        list_objects_dict = {'Contents': [
            {'Key': '2022.10.01/file1.txt'},
            {'Key': '2022.10.01/my.yaml'},
            {'Key': '2022.04.05/other.data'}]}

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

        assert test_obj_dict == list_objects_dict


    @patch('botocore.config')
    @patch('boto3.client')
    def test_list_bucket_objects_no_objects_found(self, mock_boto3, mock_botocore):
        bucket_name = 'my bucket'
        config_retval = 'config'
        region_name = 'here and there'
        prefix = 'a preefix'
        list_objects_dict = {'KeyCount': 0, 'Contents': [
            {'Key': '2022.10.01/file1.txt'},
            {'Key': '2022.10.01/my.yaml'},
            {'Key': '2022.04.05/other.data'}]}

        mock_botocore.Config.return_value = config_retval

        mock_s3_client = Mock()
        mock_s3_client.list_objects_v2.return_value = list_objects_dict

        mock_boto3.return_value = mock_s3_client

        with self.assertRaises(RuntimeError):
            test_obj_dict = list_bucket_objects(bucket_name, prefix=prefix, 
                region_name=region_name)

        # mock_botocore.Config.assert_called_with(
        #     signature_version=botocore.UNSIGNED)
        # mock_botocore.Config.assert_called_once()

        # mock_s3_client.list_objects_v2.assert_called_with(
        #     Bucket=bucket_name, Prefix=prefix)
        # mock_s3_client.list_objects_v2.assert_called_once()

        # mock_boto3.assert_called_once()
        # mock_boto3.assert_called_with('s3', region_name=region_name,
        #     config=config_retval)

        # assert test_obj_dict == list_objects_dict


    @patch('opal_release_downloader.list.list_bucket_objects')
    def test_get_list(self, mock_list_bucket_objects):
        bucket_name = 'my bucket'
        config_retval = 'config'
        region_name = 'here and there'
        list_objects_dict = {'Contents': [
            {'Key': '2022.10.01/file1.txt'},
            {'Key': '2022.10.01/my.yaml'},
            {'Key': '2022.04.05/other.data'}]}

        mock_list_bucket_objects.return_value = list_objects_dict

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
