"""Test module"""
from unittest import mock
from fmonitor.utils import (
    parse_settings,
    validate_settings
)
from fmonitor.app import process_url


def test_parse_settings(tmpdir):
    settings_file = tmpdir.mkdir("sub").join("settings.conf")
    settings_file.write("""
            {
                "interval": 10,
                "workers": 4
            }
    """)

    result = parse_settings(file_path=settings_file)
    assert result['interval'] == 10 and result['workers'] == 4


def test_parse_settings_invalid(tmpdir):
    settings_file = tmpdir.mkdir("sub").join("settings.conf")
    settings_file.write("""
            {
                "interval": '10',
            }
    """)
    assert parse_settings(file_path=settings_file) is None



def test_validate_settings_valid():
    settings = {
        'interval': 5,
        'workers': 4,
        'urls': []
    }
    assert validate_settings(settings) is True


def test_validate_settings_invalid_interval():
    settings = {
        'interval': "d",
        'workers': 4
    }
    assert validate_settings(settings) is False

def test_validate_settings_invalid_urls():
    settings = {
        'urls': 'not_a_list'
    }
    assert validate_settings(settings) is False


def test_validate_settings_schema_invalid(tmpdir):
    schema_file = tmpdir.mkdir("sub").join("settings.conf")
    schema_file.write("""
            {
               wrong schema
            }
    """)

    settings = {
        'interval': 5,
        'workers': 4,
        'urls': []
    }
    assert validate_settings(settings, schema_file=schema_file) is False


@mock.patch('fmonitor.app.log_result')
@mock.patch('requests.get')
def test_process_url_success(mock_get, mock_log_result):
    mock_get.return_value = mock.Mock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "KEYWORD"
    mock_get.return_value.elapsed.total_seconds = lambda: 0.12

    task = {
        "url": "https://www.url.com",
        "condition": "KEYWORD"
    }

    process_url(task)

    mock_log_result.assert_called_with('https://www.url.com', elapsed=0.12)


@mock.patch('fmonitor.app.log_result')
@mock.patch('requests.get')
def test_process_url_condition_invalid(mock_get, mock_log_result):
    mock_get.return_value = mock.Mock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "can't find it"
    mock_get.return_value.elapsed.total_seconds = lambda: 0.12

    task = {
        "url": "https://www.url.com",
        "condition": "KEYWORD"
    }

    process_url(task)

    mock_log_result.assert_called_with(
        'https://www.url.com',
        elapsed=0.12,
        failure_reason='Condition not met',
        success=False
    )


@mock.patch('fmonitor.app.log_result')
@mock.patch('requests.get')
def test_process_url_status_400(mock_get, mock_log_result):
    mock_get.return_value = mock.Mock()
    mock_get.return_value.status_code = 400
    mock_get.return_value.elapsed.total_seconds = lambda: 0.12

    task = {
        "url": "https://www.url.com",
        "condition": "KEYWORD"
    }

    process_url(task)

    mock_log_result.assert_called_with(
        'https://www.url.com',
        failure_reason='RequestException',
        success=False
    )

