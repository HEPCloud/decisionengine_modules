# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Publishes GCE VM Burn Rates

"""

from decisionengine.framework.modules import Publisher
from decisionengine_modules.graphite.publishers.generic_publisher import GenericPublisher as publisher


@publisher.consumes_dataframe("GCE_Burn_Rate")
class GCEBurnRatePublisher(publisher):
    def __init__(self, config):
        super().__init__(config)

    def graphite_context(self, dataframe):
        self.logger.debug("in GCEBurnRatePublisher graphite_context")
        d = {}
        # Only one row in this data frame
        d["hepcloud-fnal.BurnRate"] = dataframe.loc[0, "BurnRate"].item()
        return self.graphite_context_header, d


Publisher.describe(GCEBurnRatePublisher)
