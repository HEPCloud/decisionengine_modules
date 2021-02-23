
from decisionengine.framework.modules import Publisher

CONSUMES = ["resource_requests"]

class ProvisionerRequests(Publisher.Publisher):

    def __init__(self, params_dict):
        pass

    def consumes(self):
        return CONSUMES

    # The DataBlock given to the source is t=0
    def publish(self, data_block):
        print(data_block["resource_requests"])
