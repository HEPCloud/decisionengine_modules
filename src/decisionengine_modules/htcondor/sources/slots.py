import pandas

from decisionengine_modules.htcondor.sources import source
from decisionengine.framework.modules import Source


@Source.produces(startd_manifests=pandas.DataFrame)
class StartdManifests(source.ResourceManifests):

    def acquire(self):
        return {'startd_manifests': self.load()}


Source.describe(StartdManifests)
