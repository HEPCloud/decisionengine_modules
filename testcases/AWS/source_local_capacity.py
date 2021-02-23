from decisionengine.framework.modules import Source

class LocalCapacity(Source):
    PRODUCES = ["local_slots"]

    def __init__(self, params_dict):
        pass

    def produces(self):
        return self.PRODUCES

    # The DataBlock given to the source is t=0
    def acquire(self, DataBlock):
        return {"local_slots": 1}
