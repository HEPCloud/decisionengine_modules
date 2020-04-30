
import argparse
import pprint
import tempfile
import shutil

from decisionengine.framework.modules import Publisher


CONSUMES = ['aws_instance_limits', 'spot_occupancy_config']


class AWSFactoryEntryDataPublisher(Publisher.Publisher):

    def __init__(self, config):
        super(AWSFactoryEntryDataPublisher, self).__init__(config)
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.aws_instance_limits = config.get('aws_instance_limits')
        self.spot_occupancy_config = config.get('spot_occupancy_config')

        if None in (self.aws_instance_limits, self.spot_occupancy_config):
            raise RuntimeError('parameters for module config is missing spot_occupancy_config or aws_instance_limits')

    def consumes(self):
        """
        Return list of items consumed
        """
        return CONSUMES

    def publish(self, datablock):
        limits_df = datablock.get('aws_instance_limits')
        so_config = datablock.get('spot_occupancy_config').to_dict()

        fname = None
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fd:
            fname = fd.name
            pprint.pprint(so_config, fd)
        shutil.move(fname, self.spot_occupancy_config)

        fname = None
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fd:
            fname = fd.name
            fd.write('%s' % limits_df.to_csv(index=False))
        shutil.move(fname, self.aws_instance_limits)


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'gwms_to_aws_data': {
            'module': 'modules.glideinwms.t_gwms_to_aws_config',
            'name': 'AWSFactoryEntryDataPublisher',
            'parameters': {
                'data_file': '/path/to/aws_instance_limits.csv',
                'spot_occupancy_config': '/path/to/spot_occupancy_config.py'
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('consumes %s' % CONSUMES)
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
