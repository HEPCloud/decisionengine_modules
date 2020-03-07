from random import randint

from decisionengine.framework.modules import Source

PRODUCES = ["local_slots"]


class LocalCapacity(Source.Source):

    def __init__(self, params_dict): pass

    def produces(self, schema_id_list): return PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self):
        return {"local_slots": 1}
