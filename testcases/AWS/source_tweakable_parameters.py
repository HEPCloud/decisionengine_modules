import os

from decisionengine.framework.modules import Source

PRODUCES = ["params"]
class TweakableParameters(Source.Source):
    def __init__ (self, params_dict):
        pass

    def produces(self,schema_id_list): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        return {
            "params": {
                "overflow_permitted":               True,
                "overflow_threshold":               1,
                "overflow_cloud_permitted":         True,
                "overflow_hpc_permitted":           False,
                "overflow_osg_permitted":           False,
                "target_burn_rate":                 2.5,
            }
        }
