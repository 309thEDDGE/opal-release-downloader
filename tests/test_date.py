from unittest.mock import patch

import opal_release_downloader._date as _date 

import datetime

class TestDate():

    @patch('opal_release_downloader._date.datetime')
    def test_date(self, mock_datetime):
        tag = '2022.10.11'
        expected_value = 'x'
        mock_datetime.strptime.return_value = expected_value
        test_value = _date.date(tag)

        mock_datetime.strptime.assert_called_with(tag, '%Y.%m.%d')
        mock_datetime.strptime.assert_called_once()

        assert test_value == expected_value        

    def test_date_fmt(self):
        dt = datetime.datetime.now()
        expected = f"{dt.year:04}.{dt.month:02}.{dt.day:02}"
        test_value = _date.date_fmt(dt)

        assert expected == test_value

    @patch('opal_release_downloader._date.date_fmt')
    @patch('opal_release_downloader._date.date')
    def test_date_tag(self, mock_date, mock_date_fmt):
        tag = '2022.10.6'
        expected = '2022.10.06'
        dt = datetime.datetime.now()
        mock_date.return_value = dt
        mock_date_fmt.return_value = expected

        test_value = _date.date_tag(tag)

        mock_date.assert_called_with(tag)
        mock_date.assert_called_once()
        mock_date_fmt.assert_called_with(dt)
        mock_date_fmt.assert_called_once()

        assert expected == test_value