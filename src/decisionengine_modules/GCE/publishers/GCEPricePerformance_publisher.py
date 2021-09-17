"""
Publishes price / performance data

"""
import decisionengine_modules.graphite_client as graphite

from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher


@publisher.consumes_dataframe("GCE_Price_Performance")
class GCEPricePerformancePublisher(publisher):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def graphite_context(self, dataframe):
        self.logger.debug("in GCEPricePerformancePublisher graphite_context")
        d = {}
        for _i, row in dataframe.iterrows():
            key = f"{graphite.sanitize_key(row['EntryName'])}.price_perf"
            d[key] = row["PricePerformance"]
        return self.graphite_context_header, d


Publisher.describe(GCEPricePerformancePublisher)
