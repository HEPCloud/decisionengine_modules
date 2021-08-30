import pandas

from decisionengine_modules.htcondor.sources import source
from decisionengine.framework.modules import Source


@Source.produces(startd_manifests=pandas.DataFrame)
class StartdManifests(source.ResourceManifests):

    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    def acquire(self):
        self.logger.debug("in StartdManifests acquire")
        return {'startd_manifests': self.load()}


Source.describe(StartdManifests)
