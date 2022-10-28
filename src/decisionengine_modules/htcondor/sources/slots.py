# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor.sources import source


@Source.produces(startd_manifests=pandas.DataFrame)
class StartdManifests(source.ResourceManifests):
    def __init__(self, config, logger):
        super().__init__(config, logger)

    def acquire(self):
        self.logger.debug("in StartdManifests acquire")
        return {"startd_manifests": self.load()}


Source.describe(StartdManifests)
