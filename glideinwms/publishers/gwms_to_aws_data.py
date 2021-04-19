import pandas
import pprint
import tempfile
import shutil

from decisionengine.framework.modules import Publisher
from decisionengine.framework.modules.Publisher import Parameter


@Publisher.supports_config(Parameter('aws_instance_limits', type=str),
                           Parameter('spot_occupancy_config', type=str))
@Publisher.consumes(aws_instance_limits=pandas.DataFrame,
                    spot_occupancy_config=pandas.DataFrame)
class AWSFactoryEntryDataPublisher(Publisher.Publisher):

    def __init__(self, config):
        super().__init__(config)
        self.aws_instance_limits_file = config.get('aws_instance_limits')
        self.spot_occupancy_config_file = config.get('spot_occupancy_config')

        if None in (self.aws_instance_limits_file, self.spot_occupancy_config_file):
            raise RuntimeError('parameters for module config is missing spot_occupancy_config or aws_instance_limits')

    def publish(self, datablock):
        limits_df = self.aws_instance_limits(datablock)
        so_config = self.spot_occupancy_config(datablock).to_dict()

        fname = None
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fd:
            fname = fd.name
            pprint.pprint(so_config, fd)
        shutil.move(fname, self.spot_occupancy_config_file)

        fname = None
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as fd:
            fname = fd.name
            fd.write('%s' % limits_df.to_csv(index=False))
        shutil.move(fname, self.aws_instance_limits_file)


Publisher.describe(AWSFactoryEntryDataPublisher)
