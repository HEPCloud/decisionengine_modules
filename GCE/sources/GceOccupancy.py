"""
Get GCE occupancies 
"""
import argparse
import os 
import pprint
import pandas as pd

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

from decisionengine.framework.modules import Source

PRODUCES = ["GCE_Occupancy"]


class GceOccupancy(Source.Source):

    def __init__(self, config):
        super(GceOccupancy, self).__init__(config)
        self.project = config.get("project")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.get("credential")
        credentials = GoogleCredentials.get_application_default()
        self.client = discovery.build("compute", "v1", credentials=credentials)

    def produces(self, name_schema_id_list=None):
        return PRODUCES

    def get_zones(self):
        zones = []
        pageToken = None
        while True:
            result =  self.client.zones().list(project=self.project, 
                                               pageToken=pageToken).execute()
            pageToken = result.pop("nextPageToken", None)
            if "items" not in result:
                break
            zones +=  [x.get("name") for x in result.get("items",{})]
            if pageToken == None:
                break
        return zones
        
    def acquire(self):
        d = [] 
        zones = self.get_zones()
        for zone in zones:
            pageToken = None
            while True:
                result = self.client.instances().list(project=self.project,
                                                      zone=zone, 
                                                      pageToken=pageToken).execute()
                pageToken = result.pop("nextPageToken", None)
                if "items" not in result:
                    break
                for instance in result.get("items",[]):
                    InstanceType = instance.get("machineType").split('/').pop()
                    if instance.get("status") == "RUNNING":
                        d.append({"InstanceType" : InstanceType,
                                  "AvailabilityZone" : zone, 
                                  "Running" : 1})
                    else:
                        d.append({"InstanceType" : InstanceType,
                                  "AvailabilityZone" : zone, 
                                  "Running" : 0})
                        
                if pageToken == None:
                    break
                    
        df =  pd.DataFrame(d)
        df['Occupancy'] = df.groupby(['InstanceType', 
                                      'AvailabilityZone'])['Running'].transform('sum')

        df = df.drop_duplicates(subset=['InstanceType', 
                                        'AvailabilityZone'])

        return { PRODUCES[0] : df.filter(['InstanceType',
                                          'AvailabilityZone',
                                          'Occupancy']) }

def module_config_template():
    """
    Print template for this module configuration
    """
    template = {
        'gce_occupancy': {
            'module': 'decisionengine_modules.GCE.sources.GceOccupancy',
            'name': 'GceOccupancy',
            'parameters': {
                'project': 'hepcloud-fnal',
                'credengtial' : '/etc/gwms-frontend/credentials/monitoring.json',
            }
        }
    }
    print 'Entry in channel configuration'
    pprint.pprint(template)

def module_config_info():
    """
    Print module information
    """
    print 'produces %s' % PRODUCES
    module_config_template()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
