# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge-iot.readthedocs.io
# FLEDGE_END

""" Plugin module that can be used to modify the name of an asset, datapoint or both """

import re
import copy
import logging

from fledge.common import logger
import filter_ingest

__author__ = "Ashish Jabble"
__copyright__ = "Copyright (c) 2021 Dianomic Systems Inc."
__license__ = "Apache 2.0"

_LOGGER = logger.setup(__name__, level=logging.INFO)

PLUGIN_NAME = "rename"
# Filter specific objects
the_callback = None
the_ingest_ref = None

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Filter that modify the name of an asset, datapoint or both',
        'type': 'string',
        'default': PLUGIN_NAME,
        'readonly': 'true'
    },
    'operation': {
        'description': 'Search and replace operation be performed on asset name, datapoint name or both',
        'type': 'enumeration',
        'default': 'asset',
        'options': ['asset', 'datapoint', 'both'],
        'order': '2',
        'displayName': 'Operation'
    },
    'find': {
        'description': 'A regular expression to match for the given operation',
        'type': 'string',
        'default': 'assetName',
        'order': '3',
        'mandatory': 'true',
        'displayName': 'Find'
    },
    'replaceWith': {
        'description': 'A substitution string to replace the matched text with',
        'type': 'string',
        'default': 'newAssetName',
        'order': '4',
        'mandatory': 'true',
        'displayName': 'Replace With'
    },
    'enable': {
        'description': 'Enable/Disable filter plugin',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Enabled',
        'order': "5"
    }
}


def plugin_info():
    """ Returns information about the plugin
    Args:
    Returns:
        dict: plugin information
    Raises:
    """
    return {
        'name': PLUGIN_NAME,
        'version': '1.9.1',
        'mode': "none",
        'type': 'filter',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config, ingest_ref, callback):
    """ Initialise the plugin
    Args:
        config:     JSON configuration document for the Filter plugin configuration category
        ingest_ref: filter ingest reference
        callback:   filter callback
    Returns:
        data:       JSON object to be used in future calls to the plugin
    Raises:
    """
    data = copy.deepcopy(config)
    global the_callback, the_ingest_ref
    the_callback = callback
    the_ingest_ref = ingest_ref
    return data


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    Args:
        handle:     handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    """
    _LOGGER.info("Old config {} \n new config {} for {} plugin ".format(handle, new_config, PLUGIN_NAME))
    new_handle = copy.deepcopy(new_config)
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    """
    global the_callback, the_ingest_ref
    the_callback = None
    the_ingest_ref = None
    _LOGGER.info('{} filter plugin shutdown.'.format(PLUGIN_NAME))


def plugin_ingest(handle, data):
    """ Modify readings data and pass it onward

    Args:
        handle: handle returned by the plugin initialisation call
        data:   readings data
    """
    global the_callback, the_ingest_ref
    if handle['enable']['value'] == 'false':
        # Filter not enabled, just pass data onwards
        filter_ingest.filter_ingest_callback(the_callback, the_ingest_ref, data)
        return

    # Filter is enabled: compute for each reading
    processed_data = []
    for element in data:
        processed_data.append(find_and_replace(handle['operation']['value'], handle['find']['value'],
                                               handle['replaceWith']['value'], element))
    _LOGGER.debug("processed data {}".format(processed_data))
    # Pass data onwards
    filter_ingest.filter_ingest_callback(the_callback, the_ingest_ref, processed_data)

    _LOGGER.debug("{} filter ingest done".format(PLUGIN_NAME))


def find_and_replace(operation, find, replace_with, reading):
    """ Find and replace asset, datapoint or both with case sensitive
    Args:
        operation:     Possible values are asset, datapoint or both
        find:          A regular expression to match for the given operation
        replace_with:  A substitution string to replace the matched text with
        reading:       A reading object
    Returns:
        dict:          A processed dictionary
    """
    revised_reading_dict = {}

    def get_all_values(nested_dictionary):
        for key, value in nested_dictionary.items():
            if type(value) is dict:
                get_all_values(value)
            _datapoint = re.sub(search_pattern, replace_with, str(key), flags=re.IGNORECASE)
            revised_reading_dict[_datapoint] = value

    _LOGGER.debug("reading {}".format(reading))
    new_dict = reading.copy()
    search_pattern = r'{}'.format(find)
    replace_with = r'{}'.format(replace_with)
    _LOGGER.debug("search_pattern: {}".format(search_pattern))
    # TODO: Regex IGNORECASE should be configurable
    if operation == 'asset':
        new_dict['asset'] = re.sub(search_pattern, replace_with, new_dict['asset'], flags=re.IGNORECASE)
    elif operation == 'datapoint':
        get_all_values(new_dict['readings'])
        new_dict['readings'] = revised_reading_dict
    elif operation == 'both':
        # Both asset and datapoint case
        new_dict['asset'] = re.sub(search_pattern, replace_with, new_dict['asset'], flags=re.IGNORECASE)
        get_all_values(new_dict['readings'])
        new_dict['readings'] = revised_reading_dict
    else:
        _LOGGER.warning("Unknown {} operation found, forwarding the readings as is".format(operation))
    _LOGGER.debug("New dictionary {} in case of {}: ".format(new_dict, operation))
    return new_dict
