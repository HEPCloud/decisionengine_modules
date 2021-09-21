from decisionengine.framework.modules import Source


@Source.produces(local_slots=int)
class LocalCapacity(Source.Source):
    def __init__(self, params_dict):
        super().__init__(params_dict)

    # The DataBlock given to the source is t=0
    def acquire(self):
        self.logger.debug("in LocalCapacity acquire")
        return {"local_slots": 1}
