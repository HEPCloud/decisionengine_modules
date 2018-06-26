#!/usr/bin/python
import abc
import argparse
import pprint
import pandas
import numpy

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor import htcondor_query


class ResourceManifests(Source.Source):

    __metaclass__ = abc.ABCMeta


    def __init__(self, *args, **kwargs):
        super(ResourceManifests, self).__init__(*args, **kwargs)
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')
        self.collector_host = config.get('collector_host')
        self.condor_config = config.get('condor_config')
        self.constraint = config.get('constraint', True)
        self.classad_attrs = config.get('classad_attrs')
        self.group_attr = kwargs.get('group_attr', ['Name'])
        self.subsystem_name = kwargs.get('subsystem_name')


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

        condor_status = htcondor_query.CondorStatus(
            subsystem_name=self.subsystem_name,
            pool_name=self.collector_host,
            group_attr=self.group_attr)

        condor_status.load(self.constraint, self.classad_attrs,
                           self.condor_config)

        dataframe = pandas.DataFrame(condor_status.stored_data)
        if not dataframe.empty:
            dataframe['CollectorHost'] = [self.collector_host] * len(dataframe)
        return dataframe
