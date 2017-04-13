class CloudBudget(Source):
    PRODUCES = ["available_hpc_allocation"]

    def __init__ (self, params_dict): pass

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        DataBlock["available_hpc_allocation"] = 0
