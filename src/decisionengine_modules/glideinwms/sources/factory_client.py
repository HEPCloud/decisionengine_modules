import pandas

from decisionengine_modules.htcondor.sources import source
from decisionengine.framework.modules import Source


@Source.produces(factoryclient_manifests=pandas.DataFrame)
class FactoryClientManifests(source.ResourceManifests):

    def __init__(self, config):
        super().__init__(config)
        self.constraint = '(%s)&&(glideinmytype=="glidefactoryclient")' % self.constraint
        self.subsystem_name = 'any'


    def acquire(self):
        return {'factoryclient_manifests': self.load()}


Source.describe(FactoryClientManifests)
