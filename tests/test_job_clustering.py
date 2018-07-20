import os
import pprint
import pandas
from decisionengine_modules.glideinwms.transforms import job_clustering

config_test_job_categories = { 
  'job_categories': [
      ["VO_Name=='cms'", "VO_Name=='des'", "VO_Name=='nova'"],
      ["RequestCpus==1", "RequestCpus==2"],
      ["(MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)", "(MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)"]
  ]
}

# input with valid job_q data
valid_q_datablock = {
  'job_manifests': pandas.DataFrame({
      "VO_Name": ['cms', 'cms', 'cms', 'des', 'des'],
      "RequestCpus": [1, 2, 2, 2, 2],
      "MaxWallTimeMins": [500, 500, 1000, 500, 1000]
    })
}
# expected output
jc_valid_output_dataframe = pandas.DataFrame({
  'Bucket_Criteria_Expr': [
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='des' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='des' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='des' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='des' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='nova' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='nova' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='nova' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='nova' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)"
  ],
  'Totals': [1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0]
  },
  columns=['Bucket_Criteria_Expr', 'Totals'])

# input with invalid job_q data 
invalid_q_datablock = {
  'job_manifests': pandas.DataFrame({})
}
# expected output
jc_invalid_output_dataframe = pandas.DataFrame({
  'Bucket_Criteria_Expr': [''],
  'Totals': [0]
  },
  columns=['Bucket_Criteria_Expr', 'Totals'])


class TestJobClustering:

    # Test can create expected totals table based on known and valid input
    # Test can handle missing job q data: missing column or missing attr, for all jobs or single job 
    # Test uses defaults if no dataframe retrieved 
    # Validate log messages

    def test_produces(self):
        produces = ['job_clusters']
        job_clusters = job_clustering.JobClustering(config_test_job_categories)
        assert job_clusters.produces() == produces

    def test_consumes(self):
        consumes = ['job_manifests']
        job_clusters = job_clustering.JobClustering(config_test_job_categories)
        assert job_clusters.consumes() == consumes

    def test_transform_valid(self):
        job_clusters = job_clustering.JobClustering(config_test_job_categories)
        output = job_clusters.transform(valid_q_datablock)
        pprint.pprint(output)
        db = output.get('job_clusters')
        assert db['Totals'].sum() == 5
        assert db.shape[0] == 12

# Leaving in as a ref, unsure what will be an invalid input to module
#    def test_transform_invalid(self):
#        job_clusters = job_clustering.JobClustering(config_test_job_categories)
#        output = job_clusters.transform(invalid_q_datablock)
#        pprint.pprint(output)
#        db = output.get('job_clusters')
#        assert output['Totals'].sum() == 0
#        assert output.shape[0] == 1
