import numpy as np
import pandas as pd

class CloudRequests(Transform):
    CONSUMES = ["job_manifests", "provisioner_resources", "provisioner_resource_spot_prices" ]
    PRODUCES = ["jobs", ]

    def __init__(self, para_dict):
      pass

    # name_list:  A list of the data product names that the Transform will consume
    def consumes(): return CONSUMES

    def produces(): return PRODUCES

    def transform(DataBlock):
        job_manifests_pd = DataBlock["job_manifests"]
        resources_pd = DataBlock["provisioner_resources"]
        spot_pd = DataBlock["provisioner_resource_spot_prices"]

        # merge the spot prices into the resources_pd
        resource_spot_pd = pd.merge(resources_pd, spot_pd, on=["ResourceName"])

        # merge the job_manifests_pd and resource_spot_pd - sort of like:
        #   select *
        #   from job_manifests_pd, resource_spot_pd
        #   where job_manifests_pd.RequestCpus <= resource_spot_pd.ResourceCpus
        merged_pd = pd.merge(job_manifests_pd, resource_spot_pd, how='outer', left_on='RequestCpus', right_on='ResourceCpus')

        # create a new column that gives a boolean determining whether or not the row matches memory requirments
        merged_pd = merged_pd.assign(Match=((merged_pd.RequestMemory <= merged_pd.ResourceMemory) &&
                                            (merged_pd.RequestCpus <= merged_pd.ResourceCpus)))

        # filter for matched entries in the data frame
        matched_pd = merged_pd[(merged_pd.Match == True)]
        number_of_jobs = len(matched_pd.index)

        group = matched_pd.groupby(['SpotPrice','ResourceName'])
        res_group = group['ResourceName']

        req = {}
        limit = 5
        for i in res_group:
            entry_name = i[0][1]
            spot_price = i[0][0]

            print "considering jobs for %s" % entry_name
            print "number of jobs remaining: %i" % number_of_jobs
            print "limit: %i" % limit
            if number_of_jobs - limit > 0:
                req[entry_name] = (spot_price, limit)
                number_of_jobs -= limit
            elif number_of_jobs > 0:
                req[entry_name] = (spot_price, number_of_jobs)
                number_of_jobs = 0
            else:
                break
        print "number of unconsidered jobs: %i" % number_of_jobs

        for k in req.keys():
            print req[k]






        resource_list = [
            {"ResourceName": "AWS1", "RequestCpus": 2, "RequestMemory": 8,   "EC2Type": "m4.large"},
            {"ResourceName": "AWS2", "RequestCpus": 4, "RequestMemory": 16,  "EC2Type": "m4.xlarge"},
            {"ResourceName": "AWS3", "RequestCpus": 2, "RequestMemory": 7.5, "EC2Type": "m3.large"},
            {"ResourceName": "AWS4", "RequestCpus": 4, "RequestMemory": 15,  "EC2Type": "m3.xlarge"},
            {"ResourceName": "AWS5", "RequestCpus": 4, "RequestMemory": 7.5, "EC2Type": "c4.xlarge"}
        ]

        resource_list = [
            {"ResourceName": "AWS1", "SpotPrice": 1},
            {"ResourceName": "AWS2", "SpotPrice": 2},
            {"ResourceName": "AWS3", "SpotPrice": 2},
            {"ResourceName": "AWS4", "SpotPrice": 1},
            {"ResourceName": "AWS5", "SpotPrice": 2}
        ]

        job_manifests = [
            {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
            {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12}
        ]
