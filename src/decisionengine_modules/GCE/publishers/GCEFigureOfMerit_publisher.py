"""
Publishes price / performance data

"""

from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher
import decisionengine_modules.graphite_client as graphite


@publisher.consumes_dataframe('GCE_Figure_Of_Merit')
class GCEFigureOfMeritPublisher(publisher):
    def __init__(self, config):
        super().__init__(config)

    def graphite_context(self, dataframe):
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.fig_of_merit' %
                   (graphite.sanitize_key(row['EntryName'])))
            d[key] = row['FigureOfMerit']
        return self.graphite_context_header, d


Publisher.describe(GCEFigureOfMeritPublisher)
