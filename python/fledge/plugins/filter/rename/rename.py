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
__copyright__ = "Copyright (c) 2022 Dianomic Systems Inc."
__license__ = "Apache 2.0"

_LOGGER = logger.setup(__name__, level=logging.INFO)

PLUGIN_NAME = "rename"

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
    'ignoreCase': {
        'description': 'Case insensitive search',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Ignore Case',
        'order': "5"
    },
    'enable': {
        'description': 'Enable/Disable filter plugin',
        'type': 'boolean',
        'default': 'false',
        'displayName': 'Enabled',
        'order': "6"
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
        'version': '2.5.0',
        'mode': 'none',
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
    data['callback'] = callback
    data['ingestRef'] = ingest_ref
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
    new_handle['callback'] = handle['callback']
    new_handle['ingestRef'] = handle['ingestRef']
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    """
    handle['callback'] = None
    handle['ingestRef'] = None
    _LOGGER.info('{} filter plugin shutdown.'.format(PLUGIN_NAME))


def plugin_ingest(handle, data):
    """ Modify readings data and pass it onward

    Args:
        handle: handle returned by the plugin initialisation call
        data:   readings data
    """
    if handle['enable']['value'] == 'false':
        # Filter not enabled, just pass data onwards
        filter_ingest.filter_ingest_callback(handle['callback'],  handle['ingestRef'], data)
        return

    # Filter is enabled: compute for each reading
    processed_data = []
    for element in data:
        processed_data.append(find_and_replace(handle['operation']['value'], handle['find']['value'],
                                               handle['replaceWith']['value'], handle['ignoreCase']['value'], element))
    _LOGGER.debug("processed data {}".format(processed_data))
    # Pass data onwards
    filter_ingest.filter_ingest_callback(handle['callback'],  handle['ingestRef'], processed_data)

    _LOGGER.debug("{} filter ingest done".format(PLUGIN_NAME))


def find_and_replace(operation, find, replace_with, ignore_case, reading):
    """ Find and replace asset, datapoint or both with case-sensitive
    Args:
        operation:     Possible values are asset, datapoint or both
        find:          A regular expression to match for the given operation
        replace_with:  A substitution string to replace the matched text with
        ignore_case:   A case-insensitive search
        reading:       A reading object
    Returns:
        dict:          A processed dictionary
    """
    revised_reading_dict = {}
    _ignore_case_flag = re.IGNORECASE if ignore_case == 'false' else False
    
    if "\\" in replace_with:
        replace_with=replace_with.replace("\\","\\\\")

    def rename_reading_attributes(readings):
        res = dict()
        for key in readings.keys():
            is_key_found = False
            # Check if key is found for case insensitive option
            if not _ignore_case_flag and re.fullmatch(search_pattern, key, re.IGNORECASE):
                is_key_found = True

            # Check if key is found for case sensitive option
            if _ignore_case_flag and re.fullmatch(search_pattern, key):
                is_key_found = True

            if isinstance(readings[key], dict):
                if is_key_found:
                    res[replace_with] = rename_reading_attributes(readings[key])
                else:
                    res[key] = rename_reading_attributes(readings[key])
            else:
                if is_key_found:
                    res[replace_with] = readings[key]
                else:
                    res[key] = readings[key]
        return res

    _LOGGER.debug("reading {}".format(reading))
    new_dict = reading.copy()
    search_pattern = r'{}'.format(find)
    replace_with = r'{}'.format(replace_with)
    _LOGGER.debug("search_pattern: {}".format(search_pattern))
    # TODO: Regex IGNORECASE should be configurable
    if operation == 'asset':
        new_dict['asset'] = re.sub(search_pattern, replace_with, new_dict['asset'], flags=_ignore_case_flag)
    elif operation == 'datapoint':
        new_dict['readings'] = rename_reading_attributes(new_dict['readings'])
    elif operation == 'both':
        # Both asset and datapoint case
        new_dict['asset'] = re.sub(search_pattern, replace_with, new_dict['asset'], flags=_ignore_case_flag)
        new_dict['readings'] = rename_reading_attributes(new_dict['readings'])
    else:
        _LOGGER.warning("Unknown {} operation found, forwarding the readings as is".format(operation))
    _LOGGER.debug("New dictionary {} in case of {}: ".format(new_dict, operation))
    return new_dict
