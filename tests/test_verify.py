import pytest
from unittest.mock import patch, Mock, call

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