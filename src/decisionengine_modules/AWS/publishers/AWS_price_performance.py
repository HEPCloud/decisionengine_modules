# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Publishes price / performance data

"""
import decisionengine_modules.graphite_client as graphite

from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe("AWS_Price_Performance")
class AWSPricePerformancePublisher(publisher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def graphite_context(self, dataframe):
        self.logger.debug("in AWSPricePerformancePublisher graphite_context")
        d = {}
        for _i, row in dataframe.iterrows():
            key = f"{row['AccountName']}.{row['AvailabilityZone']}.{graphite.sanitize_key(row['InstanceType'])}.price_perf"
            d[key] = row["AWS_Price_Performance"]
        return self.graphite_context_header, d


Publisher.describe(AWSPricePerformancePublisher)
