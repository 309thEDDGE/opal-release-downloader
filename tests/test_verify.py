import pytest
from unittest.mock import patch, Mock, call

from opal_release_downloader.verify import *

import sys
import builtins
import colorama

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
        mock_open.__enter__ = mock_f
        mock_tqdm.__enter__ = Mock()
        mock_tqdm.__exit__ = Mock()
        mock_open.__enter__ = Mock()
        mock_open.__exit__ = Mock()
        hash.hexdigest.return_value = hash_value

        test_hash_value = md5sum(filename)

        mock_hashlib.assert_called_once()
        mock_os_path.getsize.assert_called_once_with(filename)
        mock_tqdm.assert_called_once_with(total=file_size, unit='B',
            unit_scale=True, desc=filename)
        assert mock_f.read.mock_calls == [call(4096), 
            call(4096), call(4096)]
        assert hash.update.mock_calls == [call(read_bytes[0]), 
            call(read_bytes[1]), call(read_bytes[2])] 
        assert mock_tqdm.__enter__.update.mock_calls == [call(4096), 
            call(4096), call(421)]
        assert test_hash_value == hash_value

