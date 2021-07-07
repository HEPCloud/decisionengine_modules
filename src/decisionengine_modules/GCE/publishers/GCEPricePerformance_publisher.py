"""
Publishes price / performance data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher
import decisionengine_modules.graphite_client as graphite


@publisher.consumes_dataframe('GCE_Price_Performance')
class GCEPricePerformancePublisher(publisher):
    def __init__(self, config):
        super().__init__(config)

    def graphite_context(self, dataframe):
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.price_perf' % (graphite.sanitize_key(row['EntryName'])))
            d[key] = row['PricePerformance']
        return self.graphite_context_header, d


Publisher.describe(GCEPricePerformancePublisher)
