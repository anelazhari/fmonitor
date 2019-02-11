"""utils

containes helper functions
"""
import logging
import json
from json.decoder import JSONDecodeError
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Setup logging
FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)
_logger = logging.getLogger('__name__')
_logger.setLevel(logging.INFO)


def parse_settings(file_path='settings.json'):
    """Loads settings from json file

    Reads settings file and returns a dictionary holding
    URL list, running interval and number of worker threads.
    """
    settings = None
    with open(file_path, 'r') as _file:
        try:
            settings = json.loads(_file.read())
        except JSONDecodeError as exp:
            _logger.error("Could not parse the settings file: %s", exp)
    return settings


def validate_settings(settings, schema_file="settings.schema"):
    """Verify config file settings are correct

    Verify that config file has an url list, and if it has
    an interval and workers setting that they are correct.
    """
    with open(schema_file, 'r') as _file:
        try:
            schema = json.loads(_file.read())
        except JSONDecodeError as exp:
            _logger.error("Could not parse the settings.schema file: %s", exp)
            return False
        try:
            validate(settings, schema)
        except ValidationError as exp:
            _logger.error('Setting file is not valid: %s', exp)
            return False

        return True
