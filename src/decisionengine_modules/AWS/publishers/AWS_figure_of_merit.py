"""
Publishes figure of merit data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe("AWS_Figure_Of_Merit")
class AWSFOMPublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def graphite_context(self, dataframe):
        self.logger.debug("in AWSFOMPublisher graphite_context")
        d = {}
        for _i, row in dataframe.iterrows():
            key = f"{row['AccountName']}.{row['EntryName']}.FOM"
            d[key] = row["AWS_Figure_Of_Merit"]
        return self.graphite_context_header, d


Publisher.describe(AWSFOMPublisher)
