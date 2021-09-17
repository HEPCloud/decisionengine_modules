"""
Get AWS capacity (running instances) information.
"""
import boto3
import pandas as pd

import decisionengine_modules.load_config as load_config

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

# default values
REGION = "us-west-2"


class OccupancyData:
    """
    Occupancy data element
    """

    def __init__(self, occupancy_data):
        """

        :type occupancy_data: :obj:`dict`
        :arg occupancy_data: occupancy data
        """
        self.data = occupancy_data

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


class OccupancyForRegion:
    """
    AWS capacity data and metods
    """

    def __init__(self, region="us-west-2", profile_name=None, instance_types=None):
        """

        :type region: :obj:`str`
        :arg region: AWS region name
        :type profile_name: :obj:`str`
        :arg profile_name: legal AWS profile name
        :type instance_types: :obj:`list`
        :arg instance_types: list of AWS instance types to query occupancy.
        """

        if profile_name:
            session = boto3.session.Session(profile_name=profile_name, region_name=region)
            self.ec2_resource = session.resource("ec2", region_name=region)
        else:
            self.ec2_resource = boto3.resource("ec2", region)
        if instance_types:
            self.instance_types = instance_types
        else:
            self.instance_types = []
        self.account_name = profile_name

    def get_ec2_instances(self):
        """
        Get all known EC2 instances.

        :rtype: :obj:`dict`: return all instances
        """

        instances = self.ec2_resource.instances.all()
        d = {}
        for instance in instances:
            running_vms = 0
            if instance.state["Name"] == "running":
                running_vms = 1
            d[instance.id] = {
                "AccountName": self.account_name,
                "InstanceType": instance.instance_type,
                "AvailabilityZone": instance.placement["AvailabilityZone"],
                "RunningVms": running_vms,
            }
        return d

    def capacity(self, instances):
        """
        Returns the current running instances data

        :type instances: :obj:`dict`
        :arg instances: instances returned by :meth:`get_ec2_instances`
        :rtype: :obj:`list`: list of spot price data (:class:`aws_data.AWSDataElement`)
        """
        ll = []
        for _instance, data in instances.items():
            if (not self.instance_types) or (self.instance_types and (data["InstanceType"] in self.instance_types)):
                occ_data = OccupancyData(data)
                if occ_data not in ll:
                    ll.append(occ_data)
                else:
                    i = ll.index(occ_data)
                    ll[i].data["RunningVms"] += occ_data.data["RunningVms"]
        return ll

    '''
    def fill_capacity_data(self, instances):
        """
        Fills ``self.data`` with current instances information.

        :type instances: :obj:`dict`
        :arg instances: instances returned by :meth:`get_ec2_instances`
        """

        internal_data = self.capacity(instances)

        for row in internal_data:
            self.data.put(AvailabilityZone=row.AvailabilityZone,
                          InstanceType=row.InstanceType,
                          RunningVms=row.RunningVms)
  '''


@Source.supports_config(
    Parameter(
        "occupancy_configuration",
        type=str,
        comment="""Python file containing (dynamic) account configuration.  The format of the file is

  {
    "ProfileName1": ["RegionName1"],
    "ProfileName2": ["RegionName2", RegionName3"]
    ...
  }

where the keys ("ProfileName*") are the name of an account profile (e.g. "hepcloud-rnd"
and the entries in the lists (e.g. "RegionName1") are the name of a region (eg. "us-west-2").
""",
    )
)
@Source.produces(AWS_Occupancy=pd.DataFrame)
class AWSOccupancy(Source.Source):
    def __init__(self, configdict):
        super().__init__(configdict)
        self.config_file = configdict["occupancy_configuration"]
        self.logger = self.logger.bind(
            class_module=__name__.split(".")[-1],
        )

    def acquire(self):
        """
        Fills ``self.data`` with spot price data.

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of spotprice data (:class:`SpotPriceData`)
        """

        # Load known accounts configuration
        # account configuration is dynamic
        account_dict = load_config.load(self.config_file, 5, 20)
        occupancy_data = []
        self.logger.debug(f"account_dict {self.account_dict}")
        for account in account_dict:  # pylint: disable=not-an-iterable
            for region in account_dict[account]:  # pylint: disable=unsubscriptable-object
                occcupancy = OccupancyForRegion(region, profile_name=account)
                instances = occcupancy.get_ec2_instances()
                if instances:
                    data = occcupancy.capacity(instances)
                    if data:
                        occupancy_data += data

        oc_list = [i.data for i in occupancy_data]
        return {"AWS_Occupancy": pd.DataFrame(oc_list)}


Source.describe(AWSOccupancy, sample_config={"occupancy_configuration": "occupancy_config_sample.py"})
