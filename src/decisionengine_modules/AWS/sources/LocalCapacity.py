from decisionengine.framework.modules import Source

@Source.produces(local_slots=int)
class LocalCapacity(Source.Source):

    def __init__(self, params_dict):
        super().__init__(config)
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    # The DataBlock given to the source is t=0
    def acquire(self):
        self.logger.debug("in LocalCapacity acquire")
        return {"local_slots": 1}
