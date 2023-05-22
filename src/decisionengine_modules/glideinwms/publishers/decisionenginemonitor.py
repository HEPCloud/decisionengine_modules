# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from decisionengine.framework.modules import Publisher
from decisionengine_modules.htcondor.publishers import publisher


@publisher.HTCondorManifests.consumes_dataframes("decisionenginemonitor_manifests")
class DecisionEngineMonitorManifests(publisher.HTCondorManifests):
    def __init__(self, config):
        super().__init__(config)
        self.classad_type = "glideclientmonitor"

    def create_invalidate_constraint(self, requests_df):
        self.logger.debug("in DecisionEngineMonitorManifests create_invalidate_constraint")
        if not requests_df.empty:
            # Starting pandas 1.5.0, groupby instruction, when iterating, returns a single element only when the grouper is a string (not a list)
            for collector_host, request_group in requests_df.groupby("CollectorHost"):
                client_names = list(set(request_group["GlideClientName"]))
                client_names.sort()
                if client_names:
                    constraint = f"""(glideinmytype == "{self.classad_type}") && (stringlistmember(GlideClientName, "{','.join(client_names)}"))"""
                    self.invalidate_ads_constraint[collector_host] = constraint


Publisher.describe(DecisionEngineMonitorManifests)
