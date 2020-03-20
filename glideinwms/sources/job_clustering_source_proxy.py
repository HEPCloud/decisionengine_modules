
import argparse
import pprint

from decisionengine.framework.modules import SourceProxy


PRODUCES = ['job_clusters']


class JobClusteringSourceProxy(SourceProxy.SourceProxy):


    def __init__(self, config):
        super(JobClusteringSourceProxy, self).__init__(config)


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        job_clusters = super(JobClusteringSourceProxy, self).acquire()
        if not set(PRODUCES).issubset(set(job_clusters.keys())):
            raise RuntimeError('SourceProxy %s not configured with all dataproducts %s' % (type(self).__name__, PRODUCES))
        return job_clusters


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'job_categorization': {
            'module': 'decisionengine_modules.glideinwms.sources.job_clustering_source_proxy',
            'name': 'JobClusteringSourceProxy',
            'parameters': {
                'channel_name': 'source_channel_name',
                'Dataproducts': PRODUCES,
                'retries': '<number of retries to acquire data>',
                'retry_timeout': '<retry timeout>'
            },
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)
    module_config_template()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
