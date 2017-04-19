#!/usr/bin/env python
import pandas as pd
import pandasql as pdsql

job_manifests = [
    {"JobId": "1.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
    {"JobId": "2.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
    {"JobId": "3.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
    {"JobId": "3.1", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
    {"JobId": "3.2", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12},
    {"JobId": "6.0", "RequestCpus": 2, "RequestMemory": 4, "RequestTime": 12}
]

resource_list = [
    {"ResourceName": "AWS1", "ResourceCpus": 2, "ResourceMemory": 8,   "EC2Type": "m4.large"},
    {"ResourceName": "AWS2", "ResourceCpus": 4, "ResourceMemory": 16,  "EC2Type": "m4.xlarge"},
    {"ResourceName": "AWS3", "ResourceCpus": 2, "ResourceMemory": 7.5, "EC2Type": "m3.large"},
    {"ResourceName": "AWS4", "ResourceCpus": 4, "ResourceMemory": 15,  "EC2Type": "m3.xlarge"},
    {"ResourceName": "AWS5", "ResourceCpus": 4, "ResourceMemory": 7.5, "EC2Type": "c4.xlarge"}
]

resource_spot_price = [
    {"ResourceName": "AWS1", "SpotPrice": .1},
    {"ResourceName": "AWS2", "SpotPrice": .15},
    {"ResourceName": "AWS3", "SpotPrice": .2},
    {"ResourceName": "AWS4", "SpotPrice": .12},
    {"ResourceName": "AWS5", "SpotPrice": .14}
]

def load_data_frame(list_of_dicts):
    list_of_keys = list_of_dicts[0].keys()
    pandas_data = {}
    for key in list_of_keys:
        pandas_data[key] = pd.Series([d[key] for d in list_of_dicts])
    return pd.DataFrame(pandas_data)

if __name__ == "__main__":
    # Set the display to a more reasonable value
    pd.set_option('display.width', 1000)

    # create jobs pandas data frame
    jobs_pd = load_data_frame(job_manifests)

    # create resources pandas data frame
    resources_pd = load_data_frame(resource_list)

    # create spot price pandas data frame
    spot_pd = load_data_frame(resource_spot_price)

    # merge the spot prices into the resources_pd
    resource_spot_pd = pd.merge(resources_pd, spot_pd, on=["ResourceName"])

    # Because pandas has difficulties in doing unordered outer joins, we will perform a sql query to do our join
    # This query only returns joined rows where the job requirements match the entry offerings
    pysql = lambda q: pdsql.sqldf(q, globals())
    join_sql = """
    select * from jobs_pd, resource_spot_pd
    where jobs_pd.RequestCpus <= resource_spot_pd.ResourceCpus and
          jobs_pd.RequestMemory <= resource_spot_pd.ResourceMemory
"""
    merged_pd = pysql(join_sql)

    # calculate and store the estimated cost per job
    merged_pd = merged_pd.assign(estimatedCost=merged_pd.RequestTime * merged_pd.SpotPrice)

    number_of_jobs = len(jobs_pd.index)

    group = merged_pd.groupby(['SpotPrice'])
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
