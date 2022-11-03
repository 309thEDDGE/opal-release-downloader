import pytest
from unittest.mock import patch, Mock, call

from opal_release_downloader.download import *

import sys
import builtins
import colorama

class TestDownload():

    @patch('sys.stdout')
    def test_bright(self, mock_stdout):
        color = 'red'
        s = 'halloween'
        write_expects = ( colorama.Style.BRIGHT + color + s
            + colorama.Style.RESET_ALL + '\n')
        
        bright(s, color=color)

        mock_stdout.write.assert_called_with(write_expects)
        mock_stdout.write.assert_called_once()
        mock_stdout.flush.assert_called_once()

    @patch('builtins.print')
    @patch('opal_release_downloader.download.verify_directory')
    @patch('opal_release_downloader.download.get_files')
    def test_get_images(self, mock_get_files, mock_verify_dir, 
        mock_print):
        bucket_name = 'my bucket'
        release_tag = '2022.10.31'

        get_images(bucket_name, release_tag)

        mock_get_files.assert_called_with(bucket_name, release_tag,
            dest='images')
        mock_get_files.assert_called_once()
        mock_print.assert_called_once()
        assert mock_print.mock_calls == [call()]
        mock_verify_dir.assert_called_with('images', 
            checksum=f"md5sums_{release_tag}",
            manifest=f"file_manifest_{release_tag}.yml")
        mock_verify_dir.assert_called_once()
    
    @patch('opal_release_downloader.download.get_files')
    def test_get_scripts(self, mock_get_files):
        bucket_name = 'my bucket'
        release_tag = '2022.10.31'

        get_scripts(bucket_name, release_tag)

        mock_get_files.assert_called_with(bucket_name, 'unpacker',
            dest='.')
        mock_get_files.assert_called_once()

    @patch('builtins.print')
    @patch('opal_release_downloader.download.verify_directory')
    @patch('opal_release_downloader.download.get_files')
    def test_get_docker(self, mock_get_files, mock_verify_dir, 
        mock_print):
        bucket_name = 'my bucket'

        get_docker(bucket_name)

        mock_get_files.assert_called_with(bucket_name, 'docker')
        mock_get_files.assert_called_once()
        mock_print.assert_called_once()
        assert mock_print.mock_calls == [call()]
        mock_verify_dir.assert_called_with('docker', 
            checksum=f"md5checksum",
            require_manifest=False,
            strict_checksum=False)
        mock_verify_dir.assert_called_once()

    @patch('builtins.print')
    @patch('opal_release_downloader.download.verify_directory')
    @patch('opal_release_downloader.download.get_files')
    def test_get_rhel(self, mock_get_files, mock_verify_dir, 
        mock_print):
        bucket_name = 'my bucket'

        get_rhel(bucket_name)

        mock_get_files.assert_called_with(bucket_name, 'redhat-iso',
            dest='rhel')
        mock_get_files.assert_called_once()
        mock_print.assert_called_once()
        assert mock_print.mock_calls == [call()]
        mock_verify_dir.assert_called_with('rhel', 
            checksum=f"md5checksum",
            require_manifest=False,
            strict_checksum=False)
        mock_verify_dir.assert_called_once()

    @patch('builtins.print')
    @patch('opal_release_downloader.download.get_scripts')
    @patch('opal_release_downloader.download.get_images')
    @patch('opal_release_downloader.download.bright')
    def test_bootstrap(self, mock_bright, mock_get_images, 
        mock_get_scripts, mock_print, mock_os_makedirs, 
        mock_os_getcwd, mock_os_chdir):
        bucket_name = 'my bucket'
        release_tag = '2022.10.31'
        download_docker = False
        download_rhel = False
        cur_dir = '/some/fake/dir'

        mock_os_getcwd.return_value = cur_dir

        bootstrap(bucket_name, release_tag=release_tag, 
            download_docker=download_docker, download_rhel=download_rhel)

        mock_os_getcwd.assert_called_once_with()
        mock_os_makedirs.assert_called_with('opal_artifacts', exist_ok=True)
        mock_os_makedirs.assert_called_once()
        mock_os_chdir.assert_has_calls(
            [call('opal_artifacts'), call(cur_dir)])
        assert mock_os_chdir.call_count == 2

        mock_bright.assert_has_calls(
            [call('Downloading and Verifying OPAL artifacts'),
            call('Downloading and Verifying installation scripts'),
            call('SUCCESS', colorama.Fore.GREEN)])

        mock_get_images.assert_called_once_with(bucket_name, release_tag)
        mock_print.assert_has_calls(
            [call()]
        )

        mock_get_scripts.assert_called_once_with(bucket_name, release_tag)

    @patch('builtins.print')
    @patch('opal_release_downloader.download.get_latest')
    @patch('opal_release_downloader.download.get_scripts')
    @patch('opal_release_downloader.download.get_images')
    @patch('opal_release_downloader.download.bright')
    def test_bootstrap_no_release_tag(self, mock_bright, mock_get_images, 
        mock_get_scripts, mock_get_latest, mock_print, mock_os_makedirs, 
        mock_os_getcwd, mock_os_chdir):
        bucket_name = 'my bucket'
        release_tag = '2022.10.31'
        download_docker = False
        download_rhel = False
        cur_dir = '/some/fake/dir'

        mock_get_latest.return_value = release_tag
        mock_os_getcwd.return_value = cur_dir

        bootstrap(bucket_name, release_tag=None, 
            download_docker=download_docker, download_rhel=download_rhel)

        mock_get_latest.assert_called_once_with(bucket_name)
        mock_os_getcwd.assert_called_once_with()
        mock_os_makedirs.assert_called_with('opal_artifacts', exist_ok=True)
        mock_os_makedirs.assert_called_once()
        mock_os_chdir.assert_has_calls(
            [call('opal_artifacts'), call(cur_dir)])
        assert mock_os_chdir.call_count == 2

        mock_bright.assert_has_calls(
            [call('Downloading and Verifying OPAL artifacts'),
            call('Downloading and Verifying installation scripts'),
            call('SUCCESS', colorama.Fore.GREEN)])

        mock_get_images.assert_called_once_with(bucket_name, release_tag)
        mock_print.assert_has_calls(
            [call()]
        )

        mock_get_scripts.assert_called_once_with(bucket_name, release_tag)


    @patch('builtins.print')
    @patch('opal_release_downloader.download.get_rhel')
    @patch('opal_release_downloader.download.get_docker')
    @patch('opal_release_downloader.download.get_scripts')
    @patch('opal_release_downloader.download.get_images')
    @patch('opal_release_downloader.download.bright')
    def test_bootstrap_with_docker_and_rhel(self, mock_bright, mock_get_images, 
        mock_get_scripts, mock_get_docker, mock_get_rhel, 
        mock_print, mock_os_makedirs, 
        mock_os_getcwd, mock_os_chdir):
        bucket_name = 'my bucket'
        release_tag = '2022.10.31'
        download_docker = True
        download_rhel = True
        cur_dir = '/some/fake/dir'

        mock_os_getcwd.return_value = cur_dir

        bootstrap(bucket_name, release_tag=release_tag, 
            download_docker=download_docker, download_rhel=download_rhel)

        mock_os_getcwd.assert_called_once_with()
        mock_os_makedirs.assert_called_with('opal_artifacts', exist_ok=True)
        mock_os_makedirs.assert_called_once()
        mock_os_chdir.assert_has_calls(
            [call('opal_artifacts'), call(cur_dir)])
        assert mock_os_chdir.call_count == 2

        mock_bright.assert_has_calls(
            [call('Downloading and Verifying OPAL artifacts'),
            call('Downloading and Verifying installation scripts'),
            call('Downloading and Verifying docker'),
            call('Downloading and Verifying RHEL-8'),
            call('SUCCESS', colorama.Fore.GREEN)])

        mock_get_images.assert_called_once_with(bucket_name, release_tag)
        mock_print.assert_has_calls(
            [call(), call(), call()]
        )

        mock_get_docker.assert_called_once_with(bucket_name)
        mock_get_rhel.asseret_called_once_with(bucket_name)
        mock_get_scripts.assert_called_once_with(bucket_name, release_tag)
