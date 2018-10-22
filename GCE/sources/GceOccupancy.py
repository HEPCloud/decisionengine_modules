"""
Get GCE occupancies 
"""
from decisionengine.framework.modules import Source


class GceOccupancy(Source.Source):

    def __init__(self, config):
        self.config = config
        
