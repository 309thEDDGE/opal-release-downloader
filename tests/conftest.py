import pytest
from unittest.mock import patch


@pytest.fixture
def mock_os_getcwd():
    with patch("os.getcwd") as m:
        yield m


@pytest.fixture
def mock_os_chdir():
    with patch("os.chdir") as m:
        yield m


@pytest.fixture
def mock_os_path():
    with patch("os.path") as m:
        yield m


@pytest.fixture
def mock_os_unlink():
    with patch("os.unlink") as m:
        yield m


@pytest.fixture
def mock_os_makedirs():
    with patch("os.makedirs") as m:
        yield m


@pytest.fixture
def mock_os_walk():
    with patch("os.walk") as m:
        yield m
