import pytest
from unittest.mock import patch, Mock, call

from opal_release_downloader.fetch import *

import sys
import builtins
import colorama

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

    @patch('tqdm.tqdm')
    def test_s3_download_with_progress(self, mock_tqdm, mock_os_path):
        mock_s3_client = Mock()
        bucket_name = 'b'
        s3_item = {'Key': '2022.09.07/blind', 'Size': 200}
        local_name = '/home/user/a.b'

        s3_key = s3_item['Key']
        size = s3_item['Size']
        mock_os_path.basename.return_value = 'a.b'

        s3_download_with_progress(mock_s3_client, bucket_name, s3_item,
            local_name)

        mock_os_path.basename.assert_called_once_with(local_name)
        mock_tqdm.assert_called_once_with(total=size, unit='B', unit_scale=True, desc='a.b')

        # TODO: Fill in args including local-scope update function ref
        mock_s3_client.download_file.assert_called_once()


    @patch('opal_release_downloader.fetch.s3_download_with_progress')
    @patch('opal_release_downloader.fetch.prepare_local_path')
    @patch('opal_release_downloader.fetch.list_bucket_objects_get_s3_client')
    @patch('opal_release_downloader.fetch.get_latest')
    def test_get_files_path_spec_and_dest_is_none(self, mock_get_latest, 
        mock_list_objects, mock_prepare_local_path, mock_s3_download, mock_os_path):
        bucket_name = 'howdy-doody'
        path_spec = None
        region_name = 'us-west-and-east'

        item_list = [{'Key': '2022.09.07/three', 'Size': 100}, 
            {'Key': '2022.09.07/blind', 'Size': 200}, 
            {'Key': '2022.09.07/mice', 'Size': 300}]
        s3 = 's3 client'
    
        get_latest_retval = '2022.09.07/'
        dirname_retval = get_latest_retval[:-1]
        realpath_retval = '/home/user/' + dirname_retval
        relpath_retval = '../' + dirname_retval
        mock_get_latest.return_value = get_latest_retval
        mock_os_path.dirname.return_value = dirname_retval
        mock_os_path.realpath.return_value = realpath_retval
        mock_list_objects.return_value = item_list, s3
        mock_os_path.relpath.return_value = relpath_retval
        prepare_local_path_retvals = ['two', 'three', 'four']
        mock_prepare_local_path.side_effect = prepare_local_path_retvals

        get_files(bucket_name, path_spec, region_name=region_name, 
            dest=None)
        
        mock_get_latest.assert_called_once_with(bucket_name,
            region_name=region_name)
        mock_os_path.dirname.assert_called_once_with(get_latest_retval)
        mock_os_path.realpath.assert_called_once_with(dirname_retval)
        mock_list_objects.assert_called_once_with(bucket_name, 
            prefix=get_latest_retval, region_name=region_name)
        mock_os_path.relpath.assert_called_once_with(realpath_retval)
        assert mock_prepare_local_path.mock_calls == [
            call(realpath_retval, item_list[0], no_overwrite=False),
            call(realpath_retval, item_list[1], no_overwrite=False), 
            call(realpath_retval, item_list[2], no_overwrite=False)
        ]
        assert mock_s3_download.mock_calls == [
            call(s3, bucket_name, item_list[0], prepare_local_path_retvals[0]),
            call(s3, bucket_name, item_list[1], prepare_local_path_retvals[1]),
            call(s3, bucket_name, item_list[2], prepare_local_path_retvals[2])
        ]


    @patch('opal_release_downloader.fetch.s3_download_with_progress')
    @patch('opal_release_downloader.fetch.prepare_local_path')
    @patch('opal_release_downloader.fetch.list_bucket_objects_get_s3_client')
    def test_get_files(self, mock_list_objects, 
        mock_prepare_local_path, mock_s3_download, mock_os_path):
        bucket_name = 'howdy-doody'
        path_spec = '2022.09.12'
        region_name = 'us-west-and-east'
        dest = '/home/user/opal_download'

        item_list = [{'Key': '2022.09.07/three', 'Size': 100}, 
            {'Key': '2022.09.07/blind', 'Size': 200}, 
            {'Key': '2022.09.07/mice', 'Size': 300}]
        s3 = 's3 client'
    
        relpath_retval = '../opal_download'
        mock_os_path.realpath.return_value = dest
        mock_list_objects.return_value = item_list, s3
        mock_os_path.relpath.return_value = relpath_retval
        prepare_local_path_retvals = ['two', 'three', 'four']
        mock_prepare_local_path.side_effect = prepare_local_path_retvals

        get_files(bucket_name, path_spec, region_name=region_name, 
            dest=dest)
        
        mock_os_path.realpath.assert_called_once_with(dest)
        mock_list_objects.assert_called_once_with(bucket_name, 
            prefix=path_spec, region_name=region_name)
        mock_os_path.relpath.assert_called_once_with(dest)
        assert mock_prepare_local_path.mock_calls == [
            call(dest, item_list[0], no_overwrite=False),
            call(dest, item_list[1], no_overwrite=False), 
            call(dest, item_list[2], no_overwrite=False)
        ]
        assert mock_s3_download.mock_calls == [
            call(s3, bucket_name, item_list[0], prepare_local_path_retvals[0]),
            call(s3, bucket_name, item_list[1], prepare_local_path_retvals[1]),
            call(s3, bucket_name, item_list[2], prepare_local_path_retvals[2])
        ]

    @patch('opal_release_downloader.fetch.s3_download_with_progress')
    @patch('opal_release_downloader.fetch.prepare_local_path')
    @patch('opal_release_downloader.fetch.list_bucket_objects_get_s3_client')
    def test_get_files_no_overwrite(self, mock_list_objects, 
        mock_prepare_local_path, mock_s3_download, mock_os_path):
        bucket_name = 'howdy-doody'
        path_spec = '2022.09.12'
        region_name = 'us-west-and-east'
        dest = '/home/user/opal_download'

        item_list = [{'Key': '2022.09.07/three', 'Size': 100}, 
            {'Key': '2022.09.07/blind', 'Size': 200}, 
            {'Key': '2022.09.07/mice', 'Size': 300}]
        s3 = 's3 client'
    
        relpath_retval = '../opal_download'
        mock_os_path.realpath.return_value = dest
        mock_list_objects.return_value = item_list, s3
        mock_os_path.relpath.return_value = relpath_retval
        prepare_local_path_retvals = ['two', 'three', 'four']
        mock_prepare_local_path.side_effect = prepare_local_path_retvals
        mock_os_path.exists.side_effect = [False, False, True]

        get_files(bucket_name, path_spec, region_name=region_name, 
            dest=dest, no_overwrite=True)
        
        mock_os_path.realpath.assert_called_once_with(dest)
        mock_list_objects.assert_called_once_with(bucket_name, 
            prefix=path_spec, region_name=region_name)
        mock_os_path.relpath.assert_called_once_with(dest)
        assert mock_prepare_local_path.mock_calls == [
            call(dest, item_list[0], no_overwrite=True),
            call(dest, item_list[1], no_overwrite=True),
            call(dest, item_list[2], no_overwrite=True)
        ]
        assert mock_s3_download.mock_calls == [
            call(s3, bucket_name, item_list[0], prepare_local_path_retvals[0]),
            call(s3, bucket_name, item_list[1], prepare_local_path_retvals[1]),
        ]
