"""
Publishes figure of merit data

"""
import pprint

from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher

DEFAULT_GRAPHITE_CONTEXT = "hepcloud.aws"
CONSUMES = ['AWS_Figure_Of_Merit']


class AWSFOMPublisher(publisher):
    def __init__(self, *args, **kwargs):
        super(AWSFOMPublisher, self).__init__(*args, **kwargs)

    def consumes(self):
        return CONSUMES

    def graphite_context(self, datablock):
        d = {}
        for i, row in datablock.iterrows():
            key = ('%s.%s.FOM' % (row['AccountName'], row['EntryName']))
            d[key] = row['AWS_Figure_Of_Merit']
        return self.graphite_context_header, d


def module_config_template():
    """
    print a template for this module configuration data
    """

    d = {"AWSFOMPublisher": {
        "module": "modules.AWS.publishers.AWS_figure_of_merit",
        "name": "AWSFOMPublisher",
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
