"""
Publishes price / performance data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher
import decisionengine_modules.graphite_client as graphite


@publisher.consumes_dataframe('AWS_Price_Performance')
class AWSPricePerformancePublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def graphite_context(self, dataframe):
        self.get_logger().debug("in AWSPricePerformancePublisher::graphite_context()")
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.%s.%s.price_perf' % (
                row['AccountName'], row['AvailabilityZone'], graphite.sanitize_key(row['InstanceType'])))
            d[key] = row['AWS_Price_Performance']
        return self.graphite_context_header, d


Publisher.describe(AWSPricePerformancePublisher)
