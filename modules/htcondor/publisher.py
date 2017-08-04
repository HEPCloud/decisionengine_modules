#!/usr/bin/python
import abc
import pandas
import htcondor
import classad

from decisionengine.framework.modules import de_logger
from decisionengine.framework.modules import Publisher
#from decisionengine.framework.dataspace import datablock

class HTCondorManifests(Publisher.Publisher):


    __metaclass__ = abc.ABCMeta


    def __init__(self, *args, **kwargs):
        if args:
            config = args[0]
        else:
            config = {}

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.collector_host = config.get('collector_host')
        self.condor_config = config.get('condor_config')
        self.logger = de_logger.get_logger()
        self.update_ad_command = 'UPDATE_AD_GENERIC'
        self.invalidate_ad_command = 'INVALIDATE_AD_GENERIC'


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return '%s' % vars(self)


    @abc.abstractmethod
    def consumes(self):
        """
        Return list of items consumed
        """
        return None


    def condor_advertise(self, ads, collector_host=None):
        """
        Advertise list of classads to the HTCondor Collector

        :type ads: :obj:`list`
        :type collector_host: :obj:`string`
        """
        collector = None
        if collector_host:
            collector = htcondor.Collector(collector_host)
        else:
            collector = htcondor.Collector()
        collector.advertise(ads, self.update_ad_command, True)


    def publish(self, datablock):
        """
        Publish classads to the HTCondor Collector
        NOTE: Assumes dataframes is a dict of values as dataframe and
              keys as datablock keys

        :type datablock: :obj:`DataBlock`
        """
        for key in self.consumes():
            dataframe = datablock.get(key)
            # TODO: How can we do this pandas way rather than interative?
            if not dataframe.empty:
                # Iterate over sub dataframes with same CollectorHost value
                for collector in pandas.unique(dataframe.CollectorHost.ravel()):
                    # Convert dataframe -> dict -> classads
                    ads = dataframe_to_classads(
                        dataframe[(dataframe['CollectorHost'] == collector)])
                    # Advertise the classad to given collector
            else:
                self.logger.info('No %s classads found to advertise' % key)


def dataframe_to_classads(dataframe):
    """
    Convert pandas dataframe to list of HTCondor classads

    :type dataframe: :obj:`DataFrame`
    """
    ads = []
    records = dataframe.to_dict(orient='records')
    for record in records:
        ad = classad.ClassAd()
        ad.update(record)
        ads.append(ad)
    return ads
