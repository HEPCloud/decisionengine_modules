import os

import mock
import pandas

import utils
from decisionengine.framework.modules import SourceProxy
from decisionengine_modules.GCE.sources import GCEResourceLimits

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXTURE_FILE = os.path.join(DATA_DIR, "gce_limits_factory_entries.test")

CONFIG = {
   "channel_name": "factory_data_channel",
   "Dataproducts": ["Factory_Entries_GCE"],
   "retries": 3,
   "retry_timeout": 20,
   "entry_limit_attrs": ["EntryName",
                         "GlideinConfigDefaultPerFrontendMaxGlideins",
                         "GlideinConfigDefaultPerFrontendMaxHeld",
                         "GlideinConfigDefaultPerFrontendMaxIdle",
                         "GlideinConfigPerEntryMaxGlideins",
                         "GlideinConfigPerEntryMaxHeld",
                         "GlideinConfigPerEntryMaxIdle",
                         "GlideinConfigPerFrontendMaxGlideins",
                         "GlideinConfigPerFrontendMaxHeld",
                         "GlideinConfigPerFrontendMaxIdle"]
}

PRODUCES = ["GCE_Resource_Limits"]

class TestGCEResourceLimits:

    def test_produces(self):
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(CONFIG)
        assert gce_resource_limits.produces() == PRODUCES

    def test_acquire(self):
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(CONFIG)
        with mock.patch.object(SourceProxy.SourceProxy, "acquire") as factory_data:
            factory_entries = utils.input_from_file(FIXTURE_FILE)
            factory_data.return_value = {"Factory_Entries_GCE": pandas.DataFrame(factory_entries)}
            gce_limits = gce_resource_limits.acquire()
            assert PRODUCES == gce_limits.keys()
            assert CONFIG.get("entry_limit_attrs").sort() == list(gce_limits.get(PRODUCES[0])).sort()
