# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

from decisionengine.framework.modules import Publisher
from decisionengine_modules.htcondor.publishers import publisher


@publisher.HTCondorManifests.consumes_dataframes("glideclientglobal_manifests")
class GlideClientGlobalManifests(publisher.HTCondorManifests):
    def __init__(self, config):
        super().__init__(config)
        self.classad_type = "glideclientglobal"

    def create_invalidate_constraint(self, dataframe):
        self.logger.debug("in GlideClientGlobalManifests create_invalidate_constraint")
        if not dataframe.empty:
            # Starting pandas 1.5.0, groupby instruction, when iterating, returns a single element only when the grouper is a string (not a list)
            for collector_host, group in dataframe.groupby("CollectorHost"):
                client_names = list(set(group["ClientName"]))
                client_names.sort()
                if client_names:
                    constraint = f"""(glideinmytype == "{self.classad_type}") && (stringlistmember(ClientName, "{','.join(client_names)}"))"""
                    self.invalidate_ads_constraint[collector_host] = constraint


Publisher.describe(GlideClientGlobalManifests)
