import numpy as np
import pandas as pd

from decisionengine.framework.modules import Publisher

CONSUMES = ["resource_requests"]

class PublishMonitoring(Publisher.Publisher):

    def __init__ (self, params_dict):
        pass

    def consumes(self): return CONSUMES

    # The DataBlock given to the source is t=0
    def publish(self, data_block):
        monitoring_message = "This would be a monitoring push.  Printing the request instead.  Request: %s" % data_block["resource_requests"]
        print(monitoring_message)
