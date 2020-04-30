
import pprint
import argparse

from decisionengine.framework.modules import SourceProxy


PRODUCES = ['GCE_Figure_Of_Merit']


class GceFigureOfMeritSourceProxy(SourceProxy.SourceProxy):


    def __init__(self, config):
        super(GceFigureOfMeritSourceProxy, self).__init__(config)


    def acquire(self):
        """
        Acquire factory entries from the factory collector
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        fom = super(GceFigureOfMeritSourceProxy, self).acquire()
        if not set(PRODUCES).issubset(set(fom.keys())):
            raise RuntimeError('SourceProxy %s not configured with all dataproducts %s' % (type(self).__name__, PRODUCES))
        return {'GCE_Figure_Of_Merit': fom.get('GCE_Figure_Of_Merit')}


    def produces(self, name_schema_id_list=None):
        return PRODUCES


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        'GceFigureOfMeritSourceProxy': {
            'module': 'decisionengine_modules.GCE.sources.GceFigureOfMeritSourceProxy',
            'name': 'GceFigureOfMeritSourceProxy',
            'parameters': {
                'channel_name': 'source_channel_name',
                'Dataproducts': PRODUCES,
                'retries': '<number of retries to acquire data>',
                'retry_timeout': '<retry timeout>'
            }
        }
    }

    print('Entry in channel cofiguration')
    pprint.pprint(template)


def module_config_info():
    """
    print this module configuration information
    """
    print('produces %s' % PRODUCES)
    module_config_template()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--configtemplate",
                        action="store_true",
                        help="prints the expected module configuration")

    parser.add_argument("--configinfo",
                        action="store_true",
                        help="prints config template along with produces and consumes info")

    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == "__main__":
    main()
