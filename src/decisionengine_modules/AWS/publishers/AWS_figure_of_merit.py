"""
Publishes figure of merit data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe('AWS_Figure_Of_Merit')
class AWSFOMPublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def graphite_context(self, dataframe):
        self.get_logger().debug("Calling graphite_context() in AWSFOMPublisher")
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.%s.FOM' % (row['AccountName'], row['EntryName']))
            d[key] = row['AWS_Figure_Of_Merit']
        return self.graphite_context_header, d


Publisher.describe(AWSFOMPublisher)
