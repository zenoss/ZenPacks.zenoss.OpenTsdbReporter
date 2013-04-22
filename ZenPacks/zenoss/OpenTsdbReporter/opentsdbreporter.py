##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013 all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter
import time

import socket

LOG = logging.getLogger('metrology.reporter.opentsdb')

class OpenTsdbReporter(Reporter):
    """
    A reporter that writes metrics to an OpenTSDB tcollector instance ::

      reporter = OpenTsdbReporter(host='localhost', port=4242, interval=10)
      reporter.start()

    :param host: tsd host
    :param port: tsd port
    :param tags: tags to use for this metric (default: host=socket.getfqdn())
    :param interval: time between each reporting
    :param prefix: metrics name prefix

    #TODO: 
       use persistent connection 
       swallow exceptions when tsdb/network fails, log errors
    """
    def __init__(self, host='localhost', port=4242, tags=None, **options):
        self.host = host
        self.port = port
        self.prefix = options.get('prefix', '')
        self.socket = None

        _tags = tags or dict()
        _tags.setdefault('host', socket.getfqdn())
        self.tags = " ".join(["%s=%s" % (key, value) for key, value in _tags.iteritems()])

        super(self.__class__, self).__init__(**options)

    def write(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self._write()
        except Exception as ex:
            LOG.warn("Could not log stats: %s", ex)
        finally:
            if self.socket:
               try:
                   self.socket.close()
               except Exception:
                   pass
               self.socket = None

    def _write(self):
        LOG.debug("logging stats.")

        for name, metric in self.registry:
            if isinstance(metric, Meter):
                self.log_metric(name, 'meter', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate'
                ])
            if isinstance(metric, Gauge):
                self.log_metric(name, 'gauge', metric, [
                    'value'
                ])
            if isinstance(metric, UtilizationTimer):
                self.log_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev',
                    'one_minute_utilization', 'five_minute_utilization',
                    'fifteen_minute_utilization', 'mean_utilization'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Timer):
                self.log_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Counter):
                self.log_metric(name, 'counter', metric, [
                    'count'
                ])
            if isinstance(metric, Histogram):
                self.log_metric(name, 'histogram', metric, [
                    'count', 'min', 'max', 'mean', 'stddev',
                ], [
                    'median', 'percentile_95th'
                ])

    def log_metric(self, name, type, metric, keys, snapshot_keys=None):
        if snapshot_keys is None:
            snapshot_keys = []
        if self.prefix:
            metric_name = "%(prefix)s.%(name)s" % locals()
        else:
            metric_name = "%(name)s" % locals()

        timestamp = int(time.time())
        line = 'put %s.%%s %d %%s %s\n' % (metric_name, timestamp, self.tags)
        messages = [line % (name, getattr(metric, name)) for name in keys]

        #if hasattr(metric, 'snapshot'):
        #    snapshot = metric.snapshot
        #    for name in snapshot_keys:
        #        messages.append("{0}={1}".format(name, getattr(snapshot, name)))

        self.socket.send(''.join(messages));

