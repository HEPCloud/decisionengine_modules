"""
Get AWS capacity (running instances) information.
"""
import boto3
import pandas as pd

from decisionengine.framework.modules import Source, SourceProxy


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

    def __eq__(self, other=None):
        """
        replaces comparison method
        """
        if not other:
            return False

        return (self.data['AvailabilityZone'], self.data['InstanceType']) == (other.data['AvailabilityZone'], other.data['InstanceType'])

    def __ne__(self, other):
        return not self == other


class OccupancyForRegion:
    """
    AWS capacity data and metods
    """

    def __init__(self, region='us-west-2', profile_name=None, instance_types=[]):
        """

        :type region: :obj:`str`
        :arg region: AWS region name
        :type profile_name: :obj:`str`
        :arg profile_name: legal AWS profile name
        :type instance_types: :obj:`list`
        :arg instance_types: list of AWS instance types to query occupancy.
        """

        if profile_name:
            session = boto3.session.Session(profile_name=profile_name,
                                            region_name=region)
            self.ec2_resource = session.resource('ec2', region_name=region)
        else:
            self.ec2_resource = boto3.resource('ec2', region)
        self.instance_types = instance_types
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
            if instance.state['Name'] == 'running':
                running_vms = 1
            d[instance.id] = {'AccountName': self.account_name,
                              'InstanceType': instance.instance_type,
                              'AvailabilityZone': instance.placement['AvailabilityZone'],
                              'RunningVms': running_vms,
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
        for instance, data in instances.items():
            if not self.instance_types or (self.instance_types and
                                           data['InstanceType'] in self.instance_types):
                occ_data = OccupancyData(data)
                if occ_data not in ll:
                    ll.append(occ_data)
                else:
                    i = ll.index(occ_data)
                    ll[i].data['RunningVms'] += occ_data.data['RunningVms']

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


@Source.produces(AWS_Occupancy=pd.DataFrame)
class AWSOccupancy(SourceProxy.SourceProxy):
    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    def acquire(self):
        """
        Fills ``self.data`` with spot price data.

        :type spot_price_history: :obj:`list`
        :arg spot_price_history: list of spotprice data (:class:`SpotPriceData`)
        """

        # Load kown accounts configuration
        account_conf = super().acquire()
        if len(account_conf.keys()) != 1:
            raise RuntimeError(
                'Wrong configuration %s. Only one key is expected' % (account_conf,))
        account_dict = {}
        for k in account_conf:
            # FIXME: We overwrite the 'account_dict' member for each iteration of this loop?
            account_dict = account_conf[k].to_dict()
        self.logger.debug('account_dict %s' % (account_dict,))
        occupancy_data = []
        for account in account_dict:
            for region in account_dict[account]:
                occcupancy = OccupancyForRegion(region, profile_name=account)
                instances = occcupancy.get_ec2_instances()
                if instances:
                    data = occcupancy.capacity(instances)
                    if data:
                        occupancy_data += data

        oc_list = [i.data for i in occupancy_data]
        # to fix the test failure
        return {'AWS_Occupancy': pd.DataFrame(oc_list)}


Source.describe(AWSOccupancy,
                sample_config={"channel_name": "test",
                               "source_channel": "channel_aws_config_data",
                               "Dataproducts": ["spot_occupancy_config"],
                               "retries": 3,
                               "retry_timeout": 20})
