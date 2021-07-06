import abc
import classad
import htcondor
import logging
import os
import pandas
from functools import partial
from decisionengine.framework.modules import Publisher
from decisionengine.framework.modules.Publisher import Parameter
from decisionengine_modules.util.retry_function import retry_wrapper

DEFAULT_UPDATE_AD_COMMAND = 'UPDATE_AD_GENERIC'
DEFAULT_INVALIDATE_AD_COMMAND = 'INVALIDATE_AD_GENERIC'


@Publisher.supports_config(Parameter('condor_config', type=str),
                           Parameter('x509_user_proxy', type=str),
                           Parameter('nretries', type=int),
                           Parameter('retry_interval', type=int, comment="Number of seconds to wait between retries."))
class HTCondorManifests(Publisher.Publisher, metaclass=abc.ABCMeta):

    def __init__(self, config):
        self.condor_config = config.get('condor_config')
        self.x509_user_proxy = config.get('x509_user_proxy')
        self.nretries = config.get('nretries')
        self.retry_interval = config.get('retry_interval')
        self.logger = logging.getLogger()
        self.update_ad_command = DEFAULT_UPDATE_AD_COMMAND
        self.invalidate_ad_command = DEFAULT_INVALIDATE_AD_COMMAND
        self.classad_type = 'generic'
        self.invalidate_ads_constraint = {}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s' % vars(self)

    def __del__(self):
        for collector_host in self.invalidate_ads_constraint:
            constraint = self.invalidate_ads_constraint[collector_host]
            if constraint:
                ads = [{
                    'MyType': 'Query',
                    'TargetType': self.classad_type,
                    'Requirements': constraint
                }]
                try:
                    self.logger.info('Invalidating %s classads from collector_host %s with constraint %s' % (
                        self.classad_type, collector_host, constraint))
                    self.condor_advertise(ads, collector_host=collector_host,
                                          update_ad_command=DEFAULT_INVALIDATE_AD_COMMAND)
                except Exception:
                    self.logger.error('Error running invalidating %s classads from collector_host %s' % (
                        self.classad_type, collector_host))

    @classmethod
    def consumes_dataframes(cls, *product_names):
        def decorator(cls):
            cls._consumes = dict.fromkeys(product_names, pandas.DataFrame)
            return cls
        return decorator

    def _condor_advertise(self, classads, collector_host=None,
                          update_ad_command=DEFAULT_UPDATE_AD_COMMAND):
        """
        Advertise list of classads to the HTCondor Collector

        :type ads: :obj:`list`
        :type collector_host: :obj:`string`
        """

        ads = classads

        old_condor_config_env = os.environ.get('CONDOR_CONFIG')
        try:
            if self.condor_config and os.path.exists(self.condor_config):
                os.environ['CONDOR_CONFIG'] = self.condor_config
            htcondor.reload_config()
            if self.x509_user_proxy and os.path.exists(self.x509_user_proxy):
                os.environ['X509_USER_PROXY'] = self.x509_user_proxy

            collector = None
            if collector_host:
                collector = htcondor.Collector(collector_host)
            else:
                collector_host = 'default'
                collector = htcondor.Collector()
            self.logger.info('Advertising %s classads to collector_host %s' % (
                self.classad_type, collector_host))
            collector.advertise(ads, update_ad_command, True)
        except Exception:
            # TODO: We need to be more specific about the errors/exception
            #       For now just raise to get more info logged
            col = 'default'
            if collector_host:
                col = collector_host
            self.logger.error('Error running %s for %s classads to collector_host %s' % (
                update_ad_command, self.classad_type, col))
            #err_str = 'Error advertising with command %s to pool %s: %s' % (self.update_ad_command, col, ex)
            #raise QueryError(err_str), None, sys.exc_info()[2]
            raise
        finally:
            if old_condor_config_env:
                os.environ['CONDOR_CONFIG'] = old_condor_config_env

    def condor_advertise(self, classads, collector_host=None,
                         update_ad_command=DEFAULT_UPDATE_AD_COMMAND):
        return retry_wrapper(partial(self._condor_advertise, classads,
                                     **{"collector_host": collector_host,
                                        "update_ad_command": update_ad_command}),
                             self.nretries, self.retry_interval)

    def publish(self, datablock):
        """
        Publish classads to the HTCondor Collector
        NOTE: Assumes dataframes is a dict of values as dataframe and
              keys as datablock keys

        :type datablock: :obj:`DataBlock`
        """
        for key in self._consumes:
            dataframe = datablock.get(key)
            self.publish_to_htcondor(key, dataframe)
            self.create_invalidate_constraint(dataframe)

    def create_invalidate_constraint(self, dataframe):
        """
        Derived classes should override the constraint creation else no
        classads will be deleted
        """
        pass

    def publish_to_htcondor(self, key, dataframe):
        try:
            # TODO: How can we do this pandas way rather than interative?
            if not dataframe.empty:
                # Iterate over sub dataframes with same CollectorHost value
                for collector in pandas.unique(dataframe.CollectorHost.ravel()):
                    # Convert dataframe -> dict -> classads
                    ads = dataframe_to_classads(
                        dataframe[(dataframe['CollectorHost'] == collector)])
                    # Advertise the classad to given collector
                    self.condor_advertise(ads, collector_host=collector)
            else:
                self.logger.info('No %s classads found to advertise' % key)
        except Exception:
            self.logger.exception("Failed to publish")


def dataframe_to_classads(dataframe):
    """
    Convert pandas dataframe to list of HTCondor classads

    :type dataframe: :obj:`DataFrame`
    """
    ads = []
    records = dataframe.to_dict(orient='records')
    for record in records:
        # NOTE: Pandas will add NaN for some of the values. This causes
        #       extremely undesired/unexpected issues. Better to remove
        #       NaN values before converting a dataframe row to classad.
        ad_dict = {}
        for key, value in record.items():
            if pandas.isnull(value):
                continue
            # The massage below is needed to handle Issue #263
            # https://github.com/HEPCloud/decisionengine_modules/issues/263
            # after switch to python3
            if isinstance(value, bytes):
                ad_dict[key] = value.decode("latin-1")
            elif isinstance(value, str):
                if value.startswith("b'"):
                    ad_dict[key] = value[2:].rstrip("'")
                else:
                    ad_dict[key] = value
            else:
                ad_dict[key] = value
        ad = classad.ClassAd()
        ad.update(ad_dict)
        ads.append(ad)
    return ads
