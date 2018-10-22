import os
import pprint
import pandas
from decisionengine_modules.glideinwms.transforms import job_clustering

config_test_match_exprs = { 
  'match_expressions': { 
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
    "VO_Name=='nova'" : ["GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1","GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1"]
  },
  'job_q_expr': "JobStatus==1"
}

# input with valid job_q data
valid_q_datablock = {
  'job_manifests': pandas.DataFrame({
    "VO_Name": ['cms', 'cms', 'cms', 'cms', 'cms', 'cms', 'nova', 'nova', 'des'],
    "RequestCpus": [1, 1, 1, 1, 2, 2, 1, 2, 1],
    "MaxWallTimeMins": [240, 240, 1080, 720, 240, 1080, 720, 240, 240],
    "JobStatus": [1, 5, 1, 1, 1, 1, 1, 1, 1]
    })
}
# expected output
jme_valid_output_dataframe = pandas.DataFrame({
  'Job_Match_Expr': [
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
    "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
    "VO_Name=='nova'"
  ],
  'Factory_Match_Epxr': [
  ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
  ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
  ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
  ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
  ["GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1","GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1"]
  ],
  'Totals': [2, 1, 2, 1, 1]
  },
  columns=['Bucket_Criteria_Expr', 'Totals'])

# input with invalid job_q data 
invalid_q_datablock = {
  'job_manifests': pandas.DataFrame({})
}
# expected output
jme_invalid_output_dataframe = pandas.DataFrame({
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
        job_clusters = job_clustering.JobClustering(config_test_match_exprs)
        assert job_clusters.produces() == produces

    def test_consumes(self):
        consumes = ['job_manifests']
        job_clusters = job_clustering.JobClustering(config_test_match_exprs)
        assert job_clusters.consumes() == consumes

    def test_transform_valid(self):
        job_clusters = job_clustering.JobClustering(config_test_match_exprs)
        output = job_clusters.transform(valid_q_datablock)
        pprint.pprint(output)
        db = output.get('job_clusters')
        assert db['Totals'].sum() == 7 
        assert db.shape[0] == 5

# Leaving in as a ref, unsure what will be an invalid input to module
#    def test_transform_invalid(self):
#        job_clusters = job_clustering.JobClustering(config_test_match_exprs)
#        output = job_clusters.transform(invalid_q_datablock)
#        pprint.pprint(output)
#        db = output.get('job_clusters')
#        assert output['Totals'].sum() == 0
#        assert output.shape[0] == 1
