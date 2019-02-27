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
                "target_aws_vm_burn_rate":      1.0,
                "target_aws_bill_burn_rate":    2.0,
                "target_aws_balance":        1000.0,
                "target_gce_vm_burn_rate":      1.0,
                "target_gce_balance":        1000.0,
            }
        }
