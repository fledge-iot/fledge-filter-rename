======================
fledge-filter-rename
======================

It is a filter plugin for Fledge which can be used to modify the name of an asset, datapoint or both.

Configuration options
======================

*  config item: 'operation', type: 'enumeration', default: 'asset'
    Search and replace operation be performed on asset name, datapoint name or both
*  config item: 'find', type: 'string', default: 'assetName'
    A regular expression to match for the given operation
*  config item: 'replaceWith', type: 'string', default: 'newAssetName'
    A substitution string to replace the matched text with
*  config item: 'enable', type: 'boolean', default: 'false'
    Enable/Disable filter plugin

Examples
========

* An input of reading object

.. code-block:: JSON

    {
        "readings": {
            "sinusoid": -0.978147601,
            "a": {
                "sinusoid": "2.0"
            }
        },
        "asset": "sinusoid",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

Apply the configuration:
------------------------

a) Case1

* 'Operation'   : 'asset'
* 'Find'        : 'sinusoid'
* 'Replace With' : 'sin'
* 'Enabled'      : 'True'

Output
~~~~~~

.. code-block:: JSON

    {
        "readings": {
            "sinusoid": -0.978147601,
            "a": {
                "sinusoid": 2.0
            }
        },
        "asset": "sin",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

See the asset 'sinusoid' is replaced with 'sin'


b) Case2

* 'Operation'   : 'datapoint'
* 'Find'        : 'sinusoid'
* 'Replace With' : 'sin'
* 'Enabled'      : 'True'

Output
~~~~~~

.. code-block:: JSON

    {
        "readings": {
            "sin": -0.978147601,
            "a": {
                "sin": 2.0
            }
        },
        "asset": "sinusoid",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }


See the readings datapoint 'sinusoid' is replaced with 'sin' even for the nested elements as well

c) Case3

* 'Operation'   : 'both'
* 'Find'        : 'sinusoid'
* 'Replace With' : 'sin'
* 'Enabled'      : 'True'

Output
~~~~~~

.. code-block:: JSON

    {
        "readings": {
            "sin": -0.978147601,
            "a": {
                "sin": 2.0
            }
        },
        "asset": "sin",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

See the asset & readings datapoint 'sinusoid' is replaced with 'sin'

d) Case4 - With regular expression, note that escaping do it by your own

* 'Operation'    : 'both'
* 'Find'         : '^(.+)$'
* 'Replace With' : 'NEW.\\1'
* 'Enabled'      : 'True'

Output
~~~~~~

.. code-block:: JSON

    {
        "readings": {
            "NEW.sinusoid": -0.978147601,
            "a": {
                "NEW.sinusoid": 2.0
            }
        },
        "asset": "NEW.sinusoid",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

See the asset & readings datapoint 'sinusoid' is replaced with 'New.sinusoid'

e) Case5

* 'Operation'    : 'asset'
* 'Find'         : '^sin.*'
* 'Replace With' : 'sine'
* 'Ignore Case'  : 'False'
* 'Enabled'      : 'True'

.. code-block:: JSON

    {
        "readings": {
            "sinusoid": -0.978147601,
            "a": {
                "sinusoid": "2.0"
            }
        },
        "asset": "sine",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

With case insensitive search, see the asset 'sinusoid' is replaced with 'sine'

f) Case6

* 'Operation'    : 'both'
* 'Find'         : '^Sin.*'
* 'Replace With' : 'sine'
* 'Ignore Case'  : 'True'
* 'Enabled'      : 'True'

.. code-block:: JSON

    {
        "readings": {
            "sinusoid": -0.978147601,
            "a": {
                "sinusoid": "2.0"
            }
        },
        "asset": "sinusoid",
        "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b",
        "ts": "2021-06-28 14:03:22.106562+00:00",
        "user_ts": "2021-06-28 14:03:22.106435+00:00"
    }

With case sensitive search, Nothing to get replaced
