# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas

from decisionengine.framework.modules import Publisher
from decisionengine_modules.htcondor.publishers import publisher

# FIXME: Awkward entanglements between subclass and base class.


class GlideinWMSManifests(publisher.HTCondorManifests):
    def __init__(self, config):
        super().__init__(config)
        self.allow_types = ["Grid", "AWS", "GCE", "LCF"]
        self._consumes = {f"Factory_Entries_{key}": pandas.DataFrame for key in self.allow_types}
        self._consumes.update(glideclient_manifests=pandas.DataFrame)
        self.classad_type = "glideclient"

    def publish(self, datablock):
        self.logger.debug("in GlideinWMSManifests publish")

        facts_df = datablock.get("de_logicengine_facts")
        self.logger.info(
            f"Facts available in publisher {self.__class__.__name__}: {facts_df.to_dict(orient='records')}"
        )

        publish_requests_df = pandas.DataFrame()
        for allow_type in self.allow_types:
            df = self.dataframe_for_entrytype(allow_type, datablock)
            publish_requests_df = pandas.concat([publish_requests_df, df], ignore_index=True, sort=True)

        self.publish_to_htcondor(self.classad_type, publish_requests_df)
        self.create_invalidate_constraint(publish_requests_df)

    def create_invalidate_constraint(self, requests_df):
        if requests_df.empty:
            return

        for collector_host, request_group in requests_df.groupby(["CollectorHost"]):
            client_names = list(set(request_group["ClientName"]))
            client_names.sort()
            if client_names:
                constraint = f"""(glideinmytype == "{self.classad_type}") && (stringlistmember(ClientName, "{','.join(client_names)}"))"""
                self.invalidate_ads_constraint[collector_host] = constraint

    def dataframe_for_entrytype(self, allow_type, datablock):
        requests_df = datablock.get("glideclient_manifests")
        facts_df = datablock.get("de_logicengine_facts")

        data_product_name = f"Factory_Entries_{allow_type}"
        fact_name = f"allow_{allow_type.lower()}_requests"
        entries = datablock.get(data_product_name)
        # Find the overlap between requests_df and the entries df, using a join-type method.
        df = requests_df.merge(entries.Name, left_on="ReqName", right_on="Name").drop(columns=["Name"])
        not_allowed = facts_df.query(f"fact_name == '{fact_name}' and fact_value == True").empty
        if not_allowed:
            # Convert request idle to 0
            # TODO: Check what to do with max running
            #       For now keep it same so existing glideins can finish
            self.logger.info(f"Setting ReqIdleGlideins=0 for fact: {allow_type}")
            df["ReqIdleGlideins"] = 0
        return df


Publisher.describe(GlideinWMSManifests)
