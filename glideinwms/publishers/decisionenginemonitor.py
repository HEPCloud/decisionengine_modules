from decisionengine.framework.modules import Publisher
from decisionengine_modules.htcondor.publishers import publisher


@publisher.HTCondorManifests.consumes_dataframes('decisionenginemonitor_manifests')
class DecisionEngineMonitorManifests(publisher.HTCondorManifests):

    def __init__(self, config):
        super().__init__(config)
        self.classad_type = 'glideclientmonitor'


    def create_invalidate_constraint(self, requests_df):
        for collector_host, request_group in requests_df.groupby(['CollectorHost']):
            client_names = list(set(request_group['GlideClientName']))
            client_names.sort()
            if client_names:
                constraint = '(glideinmytype == "%s") && (stringlistmember(GlideClientName, "%s"))' % (self.classad_type, ','.join(client_names))
                self.invalidate_ads_constraint[collector_host] = constraint


Publisher.describe(DecisionEngineMonitorManifests)
