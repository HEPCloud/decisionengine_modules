"""
Calculates real time burn rate for AWS

"""
import pandas as pd

from decisionengine.framework.modules import Transform


@Transform.consumes(provisioner_resource_spot_prices=pd.DataFrame, AWS_Occupancy=pd.DataFrame)
@Transform.produces(AWS_Burn_Rate=pd.DataFrame)
class AwsBurnRate(Transform.Transform):
    def __init__(self, config):
        super().__init__(config)

    def transform(self, data_block):

        spot_prices = self.provisioner_resource_spot_prices(data_block).fillna(0)
        occupancy = self.AWS_Occupancy(data_block).fillna(0)

        burn_df = pd.DataFrame([{"BurnRate": 0.0}])
        if not occupancy.empty:
            df = pd.merge(occupancy, spot_prices, how="inner", on=["AccountName", "AvailabilityZone", "InstanceType"])
            if not df.empty:
                df["BurnRate"] = pd.to_numeric(df["RunningVms"]) * pd.to_numeric(df["SpotPrice"])
                burn_df = pd.DataFrame([{"BurnRate": df["BurnRate"].sum()}])

        return {"AWS_Burn_Rate": burn_df}


Transform.describe(AwsBurnRate)
