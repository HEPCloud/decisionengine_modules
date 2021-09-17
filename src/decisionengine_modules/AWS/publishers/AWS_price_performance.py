"""
Publishes price / performance data

"""
import decisionengine_modules.graphite_client as graphite

from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe("AWS_Price_Performance")
class AWSPricePerformancePublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def graphite_context(self, dataframe):
        self.logger.debug("in AWSPricePerformancePublisher graphite_context")
        d = {}
        for _i, row in dataframe.iterrows():
            key = f"{row['AccountName']}.{row['AvailabilityZone']}.{graphite.sanitize_key(row['InstanceType'])}.price_perf"
            d[key] = row["AWS_Price_Performance"]
        return self.graphite_context_header, d


Publisher.describe(AWSPricePerformancePublisher)
