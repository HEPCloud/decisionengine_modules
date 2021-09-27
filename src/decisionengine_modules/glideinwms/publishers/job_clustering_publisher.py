"""
Publishes price / performance data

"""
import decisionengine_modules.graphite_client as graphite

from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher


@publisher.consumes_dataframe("job_clusters")
class JobClusteringPublisher(publisher):
    def __init__(self, config):
        super().__init__(config)

    def graphite_context(self, dataframe):
        self.logger.debug("in JobClusteringPublisher graphite_context")
        d = {}
        for _i, row in dataframe.iterrows():
            key = f"{graphite.sanitize_key(row['Frontend_Group'])}.job_cluster"
            d[key] = row["Totals"]
        return self.graphite_context_header, d


Publisher.describe(JobClusteringPublisher)
