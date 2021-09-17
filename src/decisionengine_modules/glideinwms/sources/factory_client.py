import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor.sources import source


@Source.produces(factoryclient_manifests=pd.DataFrame)
class FactoryClientManifests(source.ResourceManifests):
    def __init__(self, config):
        super().__init__(config)
        self.constraint = f'({self.constraint})&&(glideinmytype=="glidefactoryclient")'
        self.subsystem_name = "any"
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def acquire(self):
        self.logger.debug("in FactoryClientManifests acquire")
        return {"factoryclient_manifests": self.load()}


Source.describe(FactoryClientManifests)
