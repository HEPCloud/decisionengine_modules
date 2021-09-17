"""
Calculates real time burn rate for GCE

"""
import pandas as pd

from decisionengine.framework.modules import Transform


@Transform.consumes(GCE_Instance_Performance=pd.DataFrame, GCE_Occupancy=pd.DataFrame)
@Transform.produces(GCE_Burn_Rate=pd.DataFrame)
class GceBurnRate(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def transform(self, data_block):
        self.logger.debug("in GceBurnRate transform")
        performance = self.GCE_Instance_Performance(data_block).fillna(0)
        occupancy = self.GCE_Occupancy(data_block).fillna(0)

        burn_df = pd.DataFrame([{"BurnRate": 0.0}])
        if not occupancy.empty:
            df = pd.merge(occupancy, performance, how="inner", on=["AvailabilityZone", "InstanceType"])
            if not df.empty:
                df["BurnRate"] = pd.to_numeric(df["Occupancy"]) * pd.to_numeric(df["PreemptiblePrice"])
                burn_df = pd.DataFrame([{"BurnRate": df["BurnRate"].sum()}])

        return {"GCE_Burn_Rate": burn_df}


Transform.describe(GceBurnRate)
