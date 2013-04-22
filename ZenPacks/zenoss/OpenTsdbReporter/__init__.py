##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from sys import argv
from os.path import split, splitext
from opentsdbreporter import OpenTsdbReporter
from Products.ZenUtils.config import ConfigLoader, Config
from Products.ZenUtils.GlobalConfig import CONFIG_FILE


def _get_config_data():
    """
    Get OpenTsdbReporter configuration data from global.conf file.
    """
    try:
        config = ConfigLoader(CONFIG_FILE)()
    except IOError:
        config = Config()

    host = config.get('opentsdbreporter-host', 'localhost')
    port = config.getint('opentsdbreporter-port', 4242)
    interval = config.getint('opentsdbreporter-interval', 60)

    return host, port, interval


def _init_reporter():
    """
    Initialize and start the global OpenTsdbReporter instance
    """
    daemon_name = splitext(split(argv[0])[1])[0]
    host, port, interval = _get_config_data()
    global _opentsdb_reporter
    _opentsdb_reporter = OpenTsdbReporter( host=host, port=port,
                                interval=interval, tags=dict(demon=daemon_name))
    _opentsdb_reporter.start()


_init_reporter()