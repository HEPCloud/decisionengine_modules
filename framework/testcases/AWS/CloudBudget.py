import os

from decisionengine.framework.modules import Source

PRODUCES = ["available_cloud_budget"]
class CloudBudget(Source.Source):

    def __init__ (self, params_dict):
        self.budget_file = params_dict["budget_file"]

    def produces(self,schema_id_list): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        with open(self.budget_file,"r") as fd:
            budget = float(fd.read().strip())
            return { "available_cloud_budget": budget }
