# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor.sources import source


@Source.produces(startd_manifests=pandas.DataFrame)
class StartdManifests(source.ResourceManifests):
    def __init__(self, config):
        super().__init__(config)

    def acquire(self):
        self.logger.debug("in StartdManifests acquire")
        return {"startd_manifests": self.load()}


Source.describe(StartdManifests)
