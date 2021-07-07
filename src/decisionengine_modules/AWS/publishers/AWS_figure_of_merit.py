"""
Publishes figure of merit data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe('AWS_Figure_Of_Merit')
class AWSFOMPublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def graphite_context(self, dataframe):
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.%s.FOM' % (row['AccountName'], row['EntryName']))
            d[key] = row['AWS_Figure_Of_Merit']
        return self.graphite_context_header, d


Publisher.describe(AWSFOMPublisher)
