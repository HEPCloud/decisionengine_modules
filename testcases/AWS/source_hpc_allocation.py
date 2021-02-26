from decisionengine.framework.modules import Source

class HPCAllocation(Source):
    PRODUCES = ["available_hpc_allocation"]

    def __init__(self, params_dict):
        pass

    def produces(self):
        return self.PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        return {"available_hpc_allocation": 0}
