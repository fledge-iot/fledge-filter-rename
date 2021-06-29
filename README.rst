======================
fledge-filter-rename
======================

It is a filter plugin for Fledge which can be used to modify the name of asset, datapoint and both.

Configuration options
======================

*  'operation': type: enumeration default: 'asset'
    Search and replace operation be performed on asset name, datapoint name and both
*  'find': type: string default: 'assetName'
    A regular expression to match for the given operation
*  'replaceWith': type: string default: 'newAssetName'
    A substitution string to replace the matched text with
*  'enable': type: boolean default: 'false'
    Enable/Disable filter plugin

Examples
========

* A reading object

.. code-block:: console

    {"readings": {"sinusoid": -0.978147601, "a": {"sinusoid": "Blah"}}, "asset": "sinusoid", "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b", "ts": "2021-06-28 14:03:22.106562+00:00", "user_ts": "2021-06-28 14:03:22.106435+00:00"}

Set the configuration:

a) Case1

* 'operation'   : 'asset'
* 'find'        : 'sinusoid'
* 'replaceWith' : 'newsinusoid'
* 'enable'      : 'True'

Output
~~~~~~
.. code-block:: console

    {"readings": {"sinusoid": -0.978147601, "a": {"sinusoid": 2.0}}, "asset": "newsinusoid", "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b", "ts": "2021-06-28 14:03:22.106562+00:00", "user_ts": "2021-06-28 14:03:22.106435+00:00"}

    See the asset 'sinusoid' is replaced with 'newsinusoid'


b) Case2

* 'operation'   : 'datapoint'
* 'find'        : 'sinusoid'
* 'replaceWith' : 'newsinusoid'
* 'enable'      : 'True'

Output
~~~~~~
.. code-block:: console

    {"readings": {"newsinusoid": -0.978147601, "a": {"newsinusoid": 2.0}}, "asset": "sinusoid", "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b", "ts": "2021-06-28 14:03:22.106562+00:00", "user_ts": "2021-06-28 14:03:22.106435+00:00"}

    See the readings datapoint 'sinusoid' is replaced with 'newsinusoid' even for the nested elements as well

c) Case3

* 'operation'   : 'both'
* 'find'        : 'sinusoid'
* 'replaceWith' : 'newsinusoid'
* 'enable'      : 'True'

Output
~~~~~~
.. code-block:: console

    {"readings": {"newsinusoid": -0.978147601, "a": {"newsinusoid": 2.0}}, "asset": "newsinusoid", "id": "a1bedea3-8d80-47e8-b256-63370ccfce5b", "ts": "2021-06-28 14:03:22.106562+00:00", "user_ts": "2021-06-28 14:03:22.106435+00:00"}

    See the asset & readings datapoint 'sinusoid' is replaced with 'newsinusoid'
