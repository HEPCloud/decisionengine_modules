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

    def graphite_context(self, dataframe):
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.%s.%s.price_perf' % (
                row['AccountName'], row['AvailabilityZone'], graphite.sanitize_key(row['InstanceType'])))
            d[key] = row['AWS_Price_Performance']
        return self.graphite_context_header, d


Publisher.describe(AWSPricePerformancePublisher)
