import pytest
from unittest.mock import patch, Mock, call

from opal_release_downloader.fetch import *

import sys
import builtins
import colorama

@pytest.fixture
def mock_os_getcwd():
    with patch('os.getcwd') as m:
        yield m

@pytest.fixture 
def mock_os_makedirs():
    with patch('os.makedirs') as m:
        yield m

@pytest.fixture
def mock_os_chdir():
    with patch('os.chdir') as m:
        yield m

@pytest.fixture
def mock_os_path_dirname():
    with patch('os.path.dirname') as m:
        yield m

@pytest.fixture
def mock_os_path_realpath():
    with patch('os.path.realpath') as m:
        yield m

@pytest.fixture
def mock_os_path_relpath():
    with patch('os.path.relpath') as m:
        yield m

@pytest.fixture
def mock_os_path():
    with patch('os.path') as m:
        yield m

@pytest.fixture
def mock_os_unlink():
    with patch('os.unlink') as m:
        yield m

@pytest.fixture
def mock_os_makedirs():
    with patch('os.makedirs') as m:
        yield m


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


class TestFetch():

    def test_prepare_local_path(self, mock_os_path, mock_os_makedirs):
        s3_item = {'Key': '2022.09.07/blind', 'Size': 200}
        dest = '/home/user/artifacts'
        
        join_retval1 = 'blind'
        join_retval2 = 'home/user/artifacts/blind'
        realpath_retval = join_retval2
        dirname_retval = '/home/user/artifacts'
        mock_os_path.join.side_effect = [join_retval1, join_retval2]
        mock_os_path.realpath.return_value = realpath_retval
        mock_os_path.dirname.return_value = dirname_retval
        mock_os_path.isdir.return_value = True
        mock_os_path.exists.return_value = False

        prepare_local_path(dest, s3_item)

        mock_os_path.join.assert_has_calls([call(join_retval1), call(dest, join_retval1)])
        mock_os_path.realpath.assert_called_once_with(join_retval2)
        mock_os_path.dirname.assert_called_once_with(realpath_retval)
        mock_os_makedirs.assert_called_once_with(dirname_retval, exist_ok=True)
        mock_os_path.exists.assert_called_once_with(realpath_retval)

    def test_prepare_local_path_makedirs_failure(self, mock_os_path, mock_os_makedirs):
        s3_item = {'Key': '2022.09.07/blind', 'Size': 200}
        dest = '/home/user/artifacts'
        
        join_retval1 = 'blind'
        join_retval2 = 'home/user/artifacts/blind'
        realpath_retval = join_retval2
        dirname_retval = '/home/user/artifacts'
        mock_os_path.join.side_effect = [join_retval1, join_retval2]
        mock_os_path.realpath.return_value = realpath_retval
        mock_os_path.dirname.return_value = dirname_retval
        mock_os_path.isdir.return_value = False

        with pytest.raises(RuntimeError):
            prepare_local_path(dest, s3_item)

        mock_os_path.join.assert_has_calls([call(join_retval1), call(dest, join_retval1)])
        mock_os_path.realpath.assert_called_once_with(join_retval2)
        mock_os_path.dirname.assert_called_once_with(realpath_retval)
        mock_os_makedirs.assert_called_once_with(dirname_retval, exist_ok=True)

    def test_prepare_local_path_unlink(self, mock_os_path, mock_os_makedirs,
        mock_os_unlink):
        s3_item = {'Key': '2022.09.07/blind', 'Size': 200}
        dest = '/home/user/artifacts'
        
        join_retval1 = 'blind'
        join_retval2 = 'home/user/artifacts/blind'
        realpath_retval = join_retval2
        dirname_retval = '/home/user/artifacts'
        mock_os_path.join.side_effect = [join_retval1, join_retval2]
        mock_os_path.realpath.return_value = realpath_retval
        mock_os_path.dirname.return_value = dirname_retval
        mock_os_path.isdir.return_value = True
        mock_os_path.exists.return_value = True

        prepare_local_path(dest, s3_item)

        mock_os_path.join.assert_has_calls([call(join_retval1), call(dest, join_retval1)])
        mock_os_path.realpath.assert_called_once_with(join_retval2)
        mock_os_path.dirname.assert_called_once_with(realpath_retval)
        mock_os_makedirs.assert_called_once_with(dirname_retval, exist_ok=True)
        mock_os_path.exists.assert_called_once_with(realpath_retval)
        mock_os_unlink.assert_called_once_with(realpath_retval)


    # @patch('opal_release_downloader.fetch.list_bucket_objects_get_s3_client')
    # @patch('opal_release_downloader.fetch.get_latest')
    # def test_get_files_path_spec_and_dest_is_none(self, mock_get_latest, 
    #     mock_list_objects, mock_os_path):
    #     bucket_name = 'howdy-doody'
    #     path_spec = None
    #     region_name = 'us-west-and-east'
    #     dest = None
    #     prefix = '2022.09.07'

    #     item_list = [{'Key': '2022.09.07/three', 'Size': 100}, 
    #         {'Key': '2022.09.07/blind', 'Size': 200}, 
    #         {'Key': '2022.09.07/mice', 'Size': 300}]
    #     s3 = 's3 client'
    
    #     get_latest_retval = '2022.09.07/'
    #     dirname_retval = get_latest_retval[:-1]
    #     realpath_retval = '/home/user/' + dirname_retval
    #     relpath_retval = '../' + dirname_retval
    #     mock_get_latest.return_value = get_latest_retval
    #     mock_os_path.dirname.return_value = dirname_retval
    #     mock_os_path.realpath.return_value = realpath_retval
    #     mock_list_objects.return_value = item_list, s3
    #     mock_os_path.relpath.return_value = relpath_retval
    #     mock_os_path.join.side_effect = []

    #     get_files(bucket_name, path_spec, region_name=region_name, 
    #         dest=None)
        
    #     mock_get_latest.assert_called_once_with(bucket_name,
    #         region_name=region_name)
    #     mock_os_path.dirname.assert_called_once_with(get_latest_retval)
    #     mock_os_path.realpath.assert_called_once_with(dirname_retval)
    #     mock_list_objects.assert_called_once_with(bucket_name, 
    #         prefix=get_latest_retval, region_name=region_name)
    #     mock_os_path.relpath.assert_called_once_with(realpath_retval)

