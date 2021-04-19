import argparse
import pprint

from decisionengine.framework.modules import SourceProxy


PRODUCES = ['job_manifests']


class JobQSourceProxy(SourceProxy.SourceProxy):

    def __init__(self, config):
        super().__init__(config)


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        """
        Acquire jobs from the HTCondor Schedd
        :rtype: :obj:`~pd.DataFrame`
        """
        job_manifests = super().acquire()
        if not set(PRODUCES).issubset(set(job_manifests.keys())):
            raise RuntimeError('SourceProxy %s not configured with all dataproducts %s' % (type(self).__name__, PRODUCES))
        return job_manifests



def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'job_manifests': {
            'module': 'decisionengine_modules.htcondor.sources.job_q_source_proxy',
            'name': 'JobQSourceProxy',
            'parameters': {
                'channel_name': 'source_channel_name',
                'Dataproducts': PRODUCES,
                'retries': '<number of retries to acquire data>',
                'retry_timeout': '<retry timeout>'
            }
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
