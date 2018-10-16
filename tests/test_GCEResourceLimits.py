import pandas
import mock
import utils

from decisionengine_modules.GCE.sources import GCEResourceLimits
from decisionengine.framework.modules import SourceProxy

config = {
   "channel_name": "factory_data_channel",
   "Dataproducts": ["Factory_Entries_GCE"],
   "retries": 3,
   "retry_timeout": 20,
   "entry_limit_attrs": ['EntryName',
                         'GlideinConfigDefaultPerFrontendMaxGlideins',
                         'GlideinConfigDefaultPerFrontendMaxHeld',
                         'GlideinConfigDefaultPerFrontendMaxIdle',
                         'GlideinConfigPerEntryMaxGlideins',
                         'GlideinConfigPerEntryMaxHeld',
                         'GlideinConfigPerEntryMaxIdle',
                         'GlideinConfigPerFrontendMaxGlideins',
                         'GlideinConfigPerFrontendMaxHeld',
                         'GlideinConfigPerFrontendMaxIdle']
}

produces = ['GCE_Resource_Limits']

class TestGCEResourceLimits:

    def test_produces(self):
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(config)
        assert gce_resource_limits.produces() == produces

    def test_acquire(self):
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(config)
        with mock.patch.object(SourceProxy.SourceProxy, 'acquire') as factory_data:
            factory_entries = utils.input_from_file('gce_limits_factory_entries.test')
            factory_data.return_value = {'Factory_Entries_GCE': pandas.DataFrame(factory_entries)}
            gce_limits = gce_resource_limits.acquire()
            assert produces == gce_limits.keys()
            assert config.get("entry_limit_attrs").sort() == list(gce_limits.get(produces[0])).sort()
