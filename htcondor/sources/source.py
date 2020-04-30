import six
import abc
import traceback
import argparse
import pprint
import pandas

from decisionengine.framework.modules import Source
import logging
from decisionengine_modules.htcondor import htcondor_query

@six.add_metaclass(abc.ABCMeta)
class ResourceManifests(Source.Source):

    def __init__(self, config):
        super(ResourceManifests, self).__init__(config)
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.logger = logging.getLogger()
        self.collector_host = config.get('collector_host')
        self.condor_config = config.get('condor_config')
        self.constraint = config.get('constraint', True)
        self.classad_attrs = config.get('classad_attrs')
        self.group_attr = config.get('group_attr', ['Name'])
        self.subsystem_name = config.get('subsystem_name')


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return '%s' % vars(self)


    @abc.abstractmethod
    def produces(self):
        """
        Return list of items produced
        """
        return


    @abc.abstractmethod
    def acquire(self):
        """
        Acquire startd classads from the HTCondor Schedd
        :rtype: :obj:`~pd.DataFrame`
        """
        return


    def load(self):
        """
        Acquire resource classads from the HTCondor Collector
        :rtype: :obj:`~pd.DataFrame`
        """

        dataframe = pandas.DataFrame()
        try:
            condor_status = htcondor_query.CondorStatus(
                subsystem_name=self.subsystem_name,
                pool_name=self.collector_host,
                group_attr=self.group_attr)

            condor_status.load(self.constraint, self.classad_attrs,
                               self.condor_config)

            dataframe = pandas.DataFrame(condor_status.stored_data)
            if not dataframe.empty:
                (collector_host, secondary_collectors) = htcondor_query.split_collector_host(self.collector_host)
                dataframe['CollectorHost'] = [collector_host] * len(dataframe)
                if secondary_collectors != '':
                    dataframe['CollectorHosts'] = ['%s,%s' % (collector_host, secondary_collectors)] * len(dataframe)
                else:
                    dataframe['CollectorHosts'] = [collector_host] * len(dataframe)
        except htcondor_query.QueryError:
            self.logger.warning('Query error fetching classads from collector host(s) "%s"' % self.collector_host)
            self.logger.error('Query error fetching classads from collector host(s) "%s". Traceback: %s' % (self.collector_host, traceback.format_exc()))
        except Exception:
            self.logger.warning('Unexpected error fetching classads from collector host(s) "%s"' % self.collector_host)
            self.logger.error('Unexpected error fetching classads from collector host(s) "%s". Traceback: %s' % (self.collector_host, traceback.format_exc()))

        return dataframe
