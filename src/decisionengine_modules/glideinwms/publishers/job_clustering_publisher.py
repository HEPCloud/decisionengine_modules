"""
Publishes price / performance data

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher
import decisionengine_modules.graphite_client as graphite


@publisher.consumes_dataframe('job_clusters')
class JobClusteringPublisher(publisher):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(module=__name__.split(".")[-1])

    def graphite_context(self, dataframe):
        self.get_logger().debug("in JobClusteringPublisher::graphite_context()")
        d = {}
        for i, row in dataframe.iterrows():
            key = ('%s.job_cluster' %
                   (graphite.sanitize_key(row['Frontend_Group'])))
            d[key] = row['Totals']
        return self.graphite_context_header, d


Publisher.describe(JobClusteringPublisher)
