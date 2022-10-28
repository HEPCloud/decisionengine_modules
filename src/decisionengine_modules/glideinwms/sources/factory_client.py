# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine_modules.htcondor.sources import source


@Source.produces(factoryclient_manifests=pd.DataFrame)
class FactoryClientManifests(source.ResourceManifests):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.constraint = f'({self.constraint})&&(glideinmytype=="glidefactoryclient")'
        self.subsystem_name = "any"

    def acquire(self):
        self.logger.debug("in FactoryClientManifests acquire")
        return {"factoryclient_manifests": self.load()}


Source.describe(FactoryClientManifests)
