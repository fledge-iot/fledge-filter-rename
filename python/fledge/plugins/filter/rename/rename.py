# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge-iot.readthedocs.io
# FLEDGE_END

""" Plugin module that can be used to modify the name of asset, datapoint and both """

import re
import copy
import logging

from fledge.common import logger
import filter_ingest

__author__ = "Ashish Jabble"
__copyright__ = "Copyright (c) 2021 Dianomic Systems Inc."
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)

PLUGIN_NAME = "rename"
# Filter specific objects
the_callback = None
the_ingest_ref = None

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Filter that modify the name of asset, datapoint and both',
        'type': 'string',
        'default': PLUGIN_NAME,
        'readonly': 'true'
    },
    'operation': {
        'description': 'Search and replace operation be performed on asset name, datapoint name and both',
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
    processed_data = {}
    for element in data:
        processed_data = find_and_replace(handle['operation']['value'], handle['find']['value'],
                                          handle['replaceWith']['value'], element)
    _LOGGER.debug("processed data {}".format([processed_data]))
    # Pass data onwards
    filter_ingest.filter_ingest_callback(the_callback, the_ingest_ref, [processed_data])

    _LOGGER.info("{} filter ingest done".format(PLUGIN_NAME))


def find_and_replace(operation, find, replace_with, reading):
    """ Find and replace asset, datapoint and both with case sensitive
    Args:
        operation:     Possible values are asset, datapoint and both
        find:          A regular expression to match for the given operation
        replace_with:  A substitution string to replace the matched text with
        reading:       A reading object
    Returns:
        dict:          A processed dictionary
    """
    new_dict = reading.copy()
    search_pattern = r'\b{}\b'.format(find)
    _LOGGER.debug("search_pattern: {}".format(search_pattern))
    if operation == 'asset':
        new_dict['asset'] = re.sub(search_pattern, replace_with, new_dict['asset'], flags=re.IGNORECASE)
    elif operation == 'datapoint':
        dp = re.sub(search_pattern, replace_with, str(new_dict['readings']), flags=re.IGNORECASE)
        new_dict['readings'] = eval(dp)
    elif operation == 'both':
        # Both asset and datapoint case
        both = re.sub(search_pattern, replace_with, str(reading), flags=re.IGNORECASE)
        new_dict = eval(both)
    else:
        _LOGGER.warning("Unknown {} operation found.")
    _LOGGER.debug("New dictionary {} in case of {}: ".format(new_dict, operation))
    return new_dict
