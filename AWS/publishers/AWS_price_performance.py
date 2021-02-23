"""
Publishes price / performance data

"""
import pprint

from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher
import decisionengine_modules.graphite_client as graphite

DEFAULT_GRAPHITE_CONTEXT = "hepcloud.aws"
CONSUMES = ['AWS_Price_Performance']


class AWSPricePerformancePublisher(publisher):
    def __init__(self, *args, **kwargs):
        super(AWSPricePerformancePublisher, self).__init__(*args, **kwargs)

    def consumes(self):
        return CONSUMES

    def graphite_context(self, datablock):
        d = {}
        for i, row in datablock.iterrows():
            key = ('%s.%s.%s.price_perf' % (
                row['AccountName'], row['AvailabilityZone'], graphite.sanitize_key(row['InstanceType'])))
            d[key] = row['AWS_Price_Performance']
        return self.graphite_context_header, d


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSPricePerformancePublisher": {
         "module": "modules.AWS.publishers.AWS_price_performance",
         "name": "AWSPricePerformancePublisher",
         }, }
    print("Entry in channel cofiguration")
    pprint.pprint(d)
    print("where")
    print("\t name - name of the class to be instantiated by task manager")
    print("\t publish_to_graphite - publish to graphite if True")
    print("\t graphite_host - graphite host name")


def module_config_info():
    """
    print this module configuration information
    """

    print("consumes", CONSUMES)
    module_config_template()


def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--configtemplate',
                        action='store_true',
                        help='prints the expected module configuration')

    parser.add_argument('--configinfo',
                        action='store_true',
                        help='prints config template along with produces and consumes info')
    args = parser.parse_args()
    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()


if __name__ == '__main__':
    main()
