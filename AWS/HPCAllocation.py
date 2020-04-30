from decisionengine.framework.modules import Source

PRODUCES = ["available_hpc_allocation"]


class HPCAllocation(Source.Source):

    def __init__(self, params_dict):
        pass

    def produces(self, schema_id_list):
        return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        return {"available_hpc_allocation": 0}
