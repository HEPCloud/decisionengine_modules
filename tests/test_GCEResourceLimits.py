import os

import mock
import pandas
import typing

import decisionengine.framework.config.ChannelConfigHandler as configmanager
import decisionengine.framework.dataspace.dataspace as dataspace
from decisionengine.framework.modules import SourceProxy
from decisionengine_modules.GCE.sources import GCEResourceLimits
from decisionengine_modules.util import testutils as utils

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

_PRODUCES = {"GCE_Resource_Limits": typing.Any}


def test_produces():
    with mock.patch.object(configmanager, "ChannelConfigHandler"), \
         mock.patch.object(dataspace, "DataSpace"):
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(CONFIG)
        assert gce_resource_limits._produces == _PRODUCES

def test_acquire():
    with mock.patch.object(configmanager, "ChannelConfigHandler"), \
         mock.patch.object(dataspace, "DataSpace"), \
         mock.patch.object(SourceProxy.SourceProxy, "acquire") as factory_data:
        gce_resource_limits = GCEResourceLimits.GCEResourceLimits(CONFIG)
        factory_entries = utils.input_from_file(FIXTURE_FILE)
        factory_data.return_value = {"Factory_Entries_GCE": pandas.DataFrame(factory_entries)}
        gce_limits = gce_resource_limits.acquire()
        assert _PRODUCES.keys() == gce_limits.keys()
        assert CONFIG.get("entry_limit_attrs").sort() == list(gce_limits.get('GCE_Resource_Limits')).sort()
