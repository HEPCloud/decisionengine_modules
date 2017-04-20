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
                "p_overflow":               True,
                "p_overflow_threshold":     1,
                "p_overflow_cloud":         True,
                "p_overflow_hpc":           False,
                "p_overflow_osg":           False,
                "p_target_burn_rate":       2.5,
            }
        }
