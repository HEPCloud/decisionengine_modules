from decisionengine.framework.modules import Source

PRODUCES = ["params"]
class TweakableParameters(Source.Source):
    def __init__(self, params_dict):
        pass

    def produces(self, schema_id_list):
        return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        return {
            "params": {
                "overflow_permitted":               True,   # noqa: 241
                "overflow_threshold":               1,      # noqa: 241
                "overflow_cloud_permitted":         True,   # noqa: 241
                "overflow_hpc_permitted":           False,  # noqa: 241
                "overflow_osg_permitted":           False,  # noqa: 241
                "target_burn_rate":                 2.5,    # noqa: 241
            }
        }
