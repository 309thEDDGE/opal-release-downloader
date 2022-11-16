import pytest
import yaml
from unittest.mock import patch, Mock, call, ANY

from opal_release_downloader.verify import *

class TestVerify():

    @patch('builtins.open')
    @patch('tqdm.tqdm')
    @patch('hashlib.md5')
    def test_md5sum(self, mock_hashlib, mock_tqdm, 
        mock_open, mock_os_path):
        filename = 'myfile.parquet'
        hash = Mock()
        file_size = 4939199
        hash_value = '48hg38utA4yihjwg'

        mock_hashlib.return_value = hash
        mock_os_path.getsize.return_value = file_size
        read_bytes = [bytes(4096), bytes(4096), 
            bytes(421), bytes(0)]
        mock_f = Mock()
        mock_f.read.side_effect = read_bytes
        mock_open.return_value.__enter__.return_value = mock_f
        mock_tq = Mock()
        mock_tqdm.return_value.__enter__.return_value = mock_tq
        mock_tqdm.__exit__ = Mock(return_value=True)
        mock_open.__exit__ = Mock(return_value=True)
        hash.hexdigest.return_value = hash_value

        test_hash_value = md5sum(filename)

        mock_hashlib.assert_called_once()
        mock_os_path.getsize.assert_called_once_with(filename)
        mock_tqdm.assert_called_once_with(total=file_size, unit='B',
            unit_scale=True, desc=filename)
        assert mock_f.read.mock_calls == [call(4096), 
            call(4096), call(4096), call(4096)]
        assert hash.update.mock_calls == [call(read_bytes[0]), 
            call(read_bytes[1]), call(read_bytes[2])] 
        assert mock_tq.update.mock_calls == [call(4096), 
            call(4096), call(421)]
        assert test_hash_value == hash_value

    @patch('builtins.open')
    def test_read_checksums_from_file(self, mock_open, mock_os_path):
        checksum = '/tmp/hashes/check.md5sum'
        read_lines = [
            'erg8hqw3pt8y /home/user/f1',
            'aegp9834tadbnAD /tmp/data/another_one.pq',
            ''
        ]
        sums = {}
        sums['f1'] = 'erg8hqw3pt8y'
        sums['another_one.pq'] = 'aegp9834tadbnAD'

        mock_f = Mock()
        mock_f.readline.side_effect = read_lines
        mock_open.return_value.__enter__.return_value = mock_f
        mock_os_path.basename.side_effect = ['f1', 'another_one.pq']

        test_sums = read_checksums_from_file(checksum) 

        mock_open.assert_called_once_with(checksum, "r")
        assert mock_os_path.basename.mock_calls == [
            call('/home/user/f1'), call('/tmp/data/another_one.pq')
        ]
        assert test_sums == sums

    @patch('builtins.open')
    def test_read_checksums_from_file_malformed(self, mock_open, 
        mock_os_path):
        checksum = '/tmp/hashes/check.md5sum'
        read_lines = [
            'erg8hqw3pt8y /home/user/f1',
            'aegp9834tadbnAD /tmp/data/another_one.pq whoa! more here',
            ''
        ]
        sums = {}
        sums['f1'] = 'erg8hqw3pt8y'
        sums['another_one.pq'] = 'aegp9834tadbnAD'

        mock_f = Mock()
        mock_f.readline.side_effect = read_lines
        mock_open.return_value.__enter__.return_value = mock_f
        mock_os_path.basename.side_effect = ['f1', 'another_one.pq']

        exception_msg = f"malformed line in {checksum}"
        with pytest.raises(Exception) as e:
            read_checksums_from_file(checksum) 
            assert e.value.message == exception_msg

        mock_open.assert_called_once_with(checksum, "r")
        mock_os_path.basename.assert_called_once_with('/home/user/f1')

    def test_operate_on_files_fail_if_subdirs(self, mock_os_walk,
        mock_os_getcwd, mock_os_path):
        walk_root = '.'
        walk_dirs = ['data', 'test']
        walk_files = ['f1', 'other.txt']
        root_dir = '.'
        join_retval = '/home/Sprocket/./data'
        getcwd_retval = '/home/Sprocket'

        mock_os_walk.return_value = [[walk_root, walk_dirs, walk_files]]
        mock_os_path.join.return_value = join_retval
        mock_os_getcwd.return_value = getcwd_retval
        def dummy_func(f):
            pass

        with pytest.raises(Exception) as e:
            operate_on_files(root_dir, dummy_func, 
                fail_if_subdirs=True)

        mock_os_walk.assert_called_once_with(root_dir)
        mock_os_getcwd.assert_called_once()
        mock_os_path.join.assert_called_once_with(getcwd_retval, walk_root)

    def test_operate_on_files_apply_func(self, mock_os_walk):
        walk_root = '.'
        walk_dirs = ['data', 'test']
        walk_files = ['f1', 'other.txt']
        root_dir = '.'

        mock_os_walk.return_value = [[walk_root, walk_dirs, walk_files]]

        files_operated = []
        def dummy_func(f):
            files_operated.append(f)

        operate_on_files(root_dir, dummy_func, 
                fail_if_subdirs=False)

        mock_os_walk.assert_called_once_with(root_dir)
        assert files_operated == walk_files

    def test_operate_on_files_excluded_files(self, mock_os_walk):
        walk_root = '.'
        walk_dirs = ['data', 'test']
        walk_files = ['f1', 'other.txt']
        root_dir = '.'
        excluded_files = ['other.txt']

        mock_os_walk.return_value = [[walk_root, walk_dirs, walk_files]]

        files_operated = []
        def dummy_func(f):
            files_operated.append(f)

        operate_on_files(root_dir, dummy_func, 
                fail_if_subdirs=False, excluded_files=excluded_files)

        mock_os_walk.assert_called_once_with(root_dir)
        assert files_operated == ['f1']

    def test_operate_on_files_expected_files(self, mock_os_walk):
        walk_root = '.'
        walk_dirs = ['data', 'test']
        walk_files = ['f1', 'other.txt']
        root_dir = '.'
        expected_files = ['other.txt']
        mock_os_walk.return_value = [[walk_root, walk_dirs, walk_files]]

        files_operated = []
        def dummy_func(f):
            files_operated.append(f)

        with pytest.raises(Exception) as e:
            operate_on_files(root_dir, dummy_func, 
                fail_if_subdirs=False, expected_files=expected_files)

        mock_os_walk.assert_called_once_with(root_dir)
        assert files_operated == []
    
    @patch('opal_release_downloader.verify.warn')
    def test_check_checksums_operator_not_in_sums(self, mock_warn):
        f = 'f1'
        sums = {'other': 'akb98434ptiuheg'}
        strict = False

        op_func = check_checksums_operator(sums, strict)
        op_func(f)

        mock_warn.assert_called_once()

    def test_check_checksums_operator_not_in_sums_strict(self):
        f = 'f1'
        sums = {'other': 'akb98434ptiuheg'}
        strict = True

        op_func = check_checksums_operator(sums, strict)
        with pytest.raises(Exception) as e:
            op_func(f)

    @patch('opal_release_downloader.verify.md5sum')
    def test_check_checksums_operator_matching_sum(self, mock_md5sum):
        f = 'other'
        sums = {'other': 'akb98434ptiuheg'}
        strict = True

        mock_md5sum.return_value = sums['other']
        op_func = check_checksums_operator(sums, strict)
        op_func(f)

        mock_md5sum.assert_called_once_with(f)

    @patch('opal_release_downloader.verify.md5sum')
    def test_check_checksums_operator_nonmatching_sum(self, mock_md5sum):
        f = 'other'
        sums = {'other': 'akb98434ptiuheg'}
        strict = True

        mock_md5sum.return_value = 'nonmatching'
        op_func = check_checksums_operator(sums, strict)
        with pytest.raises(Exception) as e:
            op_func(f)

        mock_md5sum.assert_called_once_with(f)

    
    @patch('opal_release_downloader.verify.operate_on_files')
    @patch('opal_release_downloader.verify.check_checksums_operator')
    @patch('opal_release_downloader.verify.read_checksums_from_file')
    def test_check_checksums(self, mock_read_checksums_from_file, 
        mock_check_checksums_operator, mock_operate_on_files):
        checksum = 'checksums_file.txt'
        sums = {'test', 'blahago8934t98'}
        strict = False
        excluded_files = ['another']
        operator = Mock()
        fail_if_subdirs = True

        mock_read_checksums_from_file.return_value = sums
        mock_check_checksums_operator.return_value = operator

        check_checksums(checksum, excluded_files=excluded_files, 
            strict=strict)

        mock_read_checksums_from_file.assert_called_once_with(checksum)
        mock_check_checksums_operator.assert_called_once_with(sums, strict)
        mock_operate_on_files.assert_called_once_with('.', operator, 
            fail_if_subdirs=fail_if_subdirs, excluded_files=excluded_files)

    @patch('opal_release_downloader.verify.tqdm')
    def test_check_manifest_operator(self, mock_tqdm):
        f = 'a_file.data'
        files_found = {}

        op_func = check_manifest_operator(files_found, mock_tqdm.tqdm)
        op_func(f)

        assert files_found == {f: True}
        mock_tqdm.tqdm.update.assert_called_once()

    @patch('opal_release_downloader.verify.operate_on_files')
    @patch('opal_release_downloader.verify.check_manifest_operator')
    @patch('opal_release_downloader.verify.yaml')
    @patch('builtins.open')
    @patch('opal_release_downloader.verify.tqdm')
    def test_check_manifest(self, mock_tqdm, mock_open, mock_yaml,
        mock_check_manifest_operator, mock_operate_on_files):
        manifest = 'manifest.txt'
        excluded_files = ['one.a', 'two.b']
        expected_files = {'exp1.a': None, 'exp2.b': None}
        files_found = {k: False for k,v in expected_files.items()}
        expected_files_list = list(expected_files.keys())
        operator = Mock()

        mock_f = Mock()
        mock_open.return_value.__enter__.return_value = mock_f
        mock_yaml.load.return_value = expected_files
        mock_tq = Mock()
        mock_tqdm.tqdm.return_value.__enter__.return_value = mock_tq

        # The side effect here exists solely as a convenient 
        # way to modify the input argument, files_found.
        def operator_side_effect(input, tq):
            assert input == files_found
            assert tq == mock_tq
            for k in input.keys():
                input[k] = True
            return operator
        mock_check_manifest_operator.side_effect = operator_side_effect

        check_manifest(manifest, excluded_files=excluded_files)
        mock_open.assert_called_once_with(manifest, "r")
        mock_yaml.load.assert_called_once_with(mock_f, 
            Loader=mock_yaml.SafeLoader)
        mock_tqdm.tqdm.assert_called_once_with(desc='checking_manifest',
            total=len(expected_files))
        mock_operate_on_files.assert_called_once_with('.', operator, 
            fail_if_subdirs=True, excluded_files=excluded_files, 
            expected_files=expected_files_list)

    @patch('opal_release_downloader.verify.operate_on_files')
    @patch('opal_release_downloader.verify.check_manifest_operator')
    @patch('opal_release_downloader.verify.yaml')
    @patch('builtins.open')
    @patch('opal_release_downloader.verify.tqdm')
    def test_check_manifest_file_not_found(self, mock_tqdm, mock_open, mock_yaml,
        mock_check_manifest_operator, mock_operate_on_files):
        manifest = 'manifest.txt'
        excluded_files = ['one.a', 'two.b']
        expected_files = {'exp1.a': None, 'exp2.b': None}
        files_found = {k: False for k,v in expected_files.items()}
        expected_files_list = list(expected_files.keys())
        operator = Mock()

        mock_f = Mock()
        mock_open.return_value.__enter__.return_value = mock_f
        mock_yaml.load.return_value = expected_files
        mock_tq = Mock()
        mock_tqdm.tqdm.return_value.__enter__.return_value = mock_tq

        # The side effect here exists solely as a convenient 
        # way to modify the input argument, files_found.
        def operator_side_effect(input, tq):
            assert input == files_found
            assert tq == mock_tq
            for k in input.keys():
                input[k] = True
                # note the break !!
                break
            return operator
        mock_check_manifest_operator.side_effect = operator_side_effect

        with pytest.raises(Exception) as e:
            check_manifest(manifest, excluded_files=excluded_files)
        mock_open.assert_called_once_with(manifest, "r")
        mock_yaml.load.assert_called_once_with(mock_f, 
            Loader=mock_yaml.SafeLoader)
        mock_tqdm.tqdm.assert_called_once_with(desc='checking_manifest',
            total=len(expected_files))
        mock_operate_on_files.assert_called_once_with('.', operator, 
            fail_if_subdirs=True, excluded_files=excluded_files, 
            expected_files=expected_files_list)

    def test_find_file_and_confirm_no_search_or_fname(self):
        glob_str = 'a.*'
        with pytest.raises(Exception) as e:
            find_file_and_confirm(glob_str)

    @patch('opal_release_downloader.verify.glob')
    def test_find_file_and_confirm_glob_search_fail(self, 
        mock_glob):
        glob_str = 'a.*'
        glob_search_result = ['a.txt', 'a.other']
        mock_glob.glob.return_value = glob_search_result
        with pytest.raises(Exception) as e:
            find_file_and_confirm(glob_str, search=True)

    @patch('opal_release_downloader.verify.glob')
    def test_find_file_and_confirm_glob_search_succeed(self, 
        mock_glob, mock_os_path):
        glob_str = 'a.*'
        glob_search_result = ['a.txt']
        mock_glob.glob.return_value = glob_search_result
        mock_os_path.exists.return_value = True
        result = find_file_and_confirm(glob_str, search=True)
        mock_os_path.exists.assert_called_once_with(glob_search_result[0])
        assert result == glob_search_result[0]

    @patch('opal_release_downloader.verify.glob')
    def test_find_file_and_confirm_glob_result_not_exist(self, 
        mock_glob, mock_os_path):
        glob_str = 'a.*'
        glob_search_result = ['a.txt']
        mock_glob.glob.return_value = glob_search_result
        mock_os_path.exists.return_value = False
        with pytest.raises(Exception) as e:
            find_file_and_confirm(glob_str, search=True)
        mock_os_path.exists.assert_called_once_with(glob_search_result[0])

    def test_find_file_and_confirm_no_search_file_not_exist(self, 
        mock_os_path):
        glob_str = 'a.*'
        file_name = 'a.txt'
        mock_os_path.exists.return_value = False
        with pytest.raises(Exception) as e:
            find_file_and_confirm(glob_str, file_name=file_name, 
                search=False)
        mock_os_path.exists.assert_called_once_with(file_name)

    def test_find_file_and_confirm_no_search_file_exist(self, 
        mock_os_path):
        glob_str = 'a.*'
        file_name = 'a.txt'
        mock_os_path.exists.return_value = True
        result = find_file_and_confirm(glob_str, file_name=file_name, 
                search=False)
        mock_os_path.exists.assert_called_once_with(file_name)
        assert result == file_name

    def test_verify_directory():
        pass