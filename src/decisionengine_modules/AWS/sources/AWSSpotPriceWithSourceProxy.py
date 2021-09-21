"""
Get AWS spot price information
"""

import datetime
import time

import boto3
import pandas as pd

from decisionengine.framework.modules import Source, SourceProxy

# default values
REGION = "us-west-2"
INSTANCE_TYPES = ["m3.2xlarge", "c3.2xlarge"]
HISTORY_OBSERVATION_TIME = 3600  # observe spot price for the last hour
# HISTORY_START_TIME = HISTORY_END_TIME.replace(day=(HISTORY_END_TIME.day-1)) # 1 day ago
PRODUCT_DESCRIPTIONS = ["Linux/UNIX"]
DRY_RUN = False
MAX_RESULTS = 1000
AVAILABILITY_ZONE = ""  # any


class SpotPriceData:
    """
    Spot Price data element
    """

    def __init__(self, sp_data):
        """

        :type sp_data: :obj:`dict`
        :arg sp_data: spot price data
        """
        self.data = sp_data
        self.data["Timestamp"] = sp_data["Timestamp"].isoformat()

    def __cmp__(self, other=None):
        """
        overrides comparison method
        """
        try:
            if (self.data["AvailabilityZone"], self.data["InstanceType"]) == (
                other.data["AvailabilityZone"],
                other.data["InstanceType"],
            ):
                return 0
        except Exception:
            pass

        return -1


class AWSSpotPriceForRegion:
    """
    Spot price data and methods
    """

    def __init__(self, region=REGION, profile_name=None):
        """

        :type region: :obj:`str`
        :arg region: AWS region name
        :type profile_name: :obj:`str`
        :arg profile_name: legal AWS profile name
        """
        if profile_name:
            session = boto3.session.Session(profile_name=profile_name, region_name=region)
            self.ec2 = session.client("ec2", region_name=region)

        else:
            self.ec2 = boto3.client("ec2", region_name=region)
        self.account_name = profile_name
        t = time.time()
        self.start_time = datetime.datetime.utcfromtimestamp(t - HISTORY_OBSERVATION_TIME)
        self.end_time = datetime.datetime.utcfromtimestamp(t)
        self.intance_types = INSTANCE_TYPES
        self.dry_run = DRY_RUN
        self.max_results = MAX_RESULTS
        self.product_descriptions = PRODUCT_DESCRIPTIONS
        self.availability_zone = AVAILABILITY_ZONE

    def init_query(
        self,
        spot_price_history_start_time=None,
        spot_price_history_end_time=None,
        instance_types=INSTANCE_TYPES,
        product_descriptions=PRODUCT_DESCRIPTIONS,
        dry_run=DRY_RUN,
        max_resuts=MAX_RESULTS,
        availability_zone=AVAILABILITY_ZONE,
    ):
        """
        Init AWS spot price query

        :type spot_price_history_start_time: :obj:`str`
        :arg spot_price_history_start_time: price since.
        :type spot_price_history_end_time: :obj:`str`
        :arg spot_price_history_end_time: price till.
        :type instance_types: :obj:`list`
        :arg instance_types: list of AWS instance types to query spot price for.
        :type dry_run: :obj:`bool`
        :arg dry_run: as described in boto3 documentation.
        :type max_resuts: :obj:`int`
        :arg max_resuts: maximum number of results to return.

        """
        if spot_price_history_start_time:
            self.start_time = spot_price_history_start_time
        if spot_price_history_end_time:
            self.end_time = spot_price_history_end_time
        self.intance_types = instance_types
        self.dry_run = dry_run
        self.max_results = max_resuts
        self.product_descriptions = product_descriptions
        self.availability_zone = availability_zone

    def get_price(self, logger):
        """
        Get AWS spot prices.
        """
        try:
            rc = self.ec2.describe_spot_price_history(
                DryRun=self.dry_run,
                StartTime=self.start_time,
                EndTime=self.end_time,
                InstanceTypes=self.intance_types,
                ProductDescriptions=self.product_descriptions,
                Filters=[],
                AvailabilityZone=self.availability_zone,
                MaxResults=self.max_results,
                NextToken="",
            )
        except Exception:
            logger.exception("Exception in AWSSpotPriceWithSourceProxy call to get_price")
            return None
        price_history = rc.get("SpotPriceHistory")
        if len(price_history) == 0:
            price_history = None
        return price_history

    def spot_price_summary(self, spot_price_history):
        """
        Returns the current spot prices per
        availability zone and instance type

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of dictonaries
        :rtype: :obj:`list`: list of spot price data (:class:`SpotPriceData`)
        """

        ll = []
        for item in spot_price_history:
            item["AccountName"] = self.account_name
            spd = SpotPriceData(item)
            if spd not in ll:
                # append if there is no element with given
                # availability zone and instance type
                ll.append(spd)
            else:
                # replace spot price by the most recent
                i = ll.index(spd)
                ll[i].data["Timestamp"] = spd.data["Timestamp"]
                ll[i].data["SpotPrice"] = spd.data["SpotPrice"]
        return ll


@Source.produces(provisioner_resource_spot_prices=pd.DataFrame)
class AWSSpotPrice(SourceProxy.SourceProxy):
    def __init__(self, config):
        super().__init__(config)

    def acquire(self):
        """
        Gets data from AWS

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """

        # Load known accounts configuration
        self.logger.debug("in AWSSpotPrice-SP acquire")
        account_conf = super().acquire()
        if len(account_conf.keys()) != 1:
            raise RuntimeError(f"Wrong configuration {account_conf}. Only one key is expected")
        account_dict = {}
        for k in account_conf:
            account_dict = account_conf[k].to_dict()
        sp_data = []
        for account in account_dict:
            for region, instances in account_dict[account].items():
                spot_price_info = AWSSpotPriceForRegion(region, profile_name=account)
                spot_price_info.init_query(instance_types=instances)
                spot_price_history = spot_price_info.get_price(self.logger)
                if spot_price_history:
                    sp_data += spot_price_info.spot_price_summary(spot_price_history)

        sp_list = [i.data for i in sp_data]
        column_names = [
            "AccountName",
            "AvailabilityZone",
            "InstanceType",
            "ProductDescription",
            "SpotPrice",
            "Timestamp",
        ]
        return {"provisioner_resource_spot_prices": pd.DataFrame(sp_list, columns=column_names)}


Source.describe(
    AWSSpotPrice,
    sample_config={
        "channel_name": "test",
        "source_channel": "channel_aws_config_data",
        "Dataproducts": ["spot_occupancy_config"],
        "retries": 3,
        "retry_timeout": 20,
    },
)
