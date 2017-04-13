import os

class CloudBudget(Source):
    PRODUCES = ["available_cloud_budget"]

    def __init__ (self, params_dict):
        self.budget_file = params_dict["budget_file"]

    def produces(self): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        with os.open(self.budget_file, os.O_EXLOCK) as fd:
            budget = float(fd.read().strip())
            DataBlock["local_capacity_slots"] = budget
