"""
This dummy source takes the name of an FOM source datablock from config file
as parameter "datablock_type" and produces an empty FOM datablock with that name
"""
import pandas as pd

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(
    Parameter("datablock_type", default=""),
)
class DummyFOMSource(Source.Source):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )
        self.datablock_type = config.get("datablock_type")
        if not self.datablock_type:
            raise RuntimeError("No datablock_type found in configuration")

        self._produces = {self.datablock_type: pd.DataFrame}

    def acquire(self):
        self.logger.debug(f"in DummyFOMSource: {self.datablock_type} acquire")
        return {self.datablock_type: pd.DataFrame()}


Source.describe(DummyFOMSource)
