#!/usr/bin/python

import argparse
import pprint
import pandas
import itertools

from decisionengine.framework.modules import de_logger
from decisionengine.framework.modules import Transform
from decisionengine.framework.dataspace.datablock import DataBlock

PRODUCES = ['job_clusters']

CONSUMES = ['job_manifests']

# Expects a named list of expressions
# Expects a list of expressions to apply for each category type, 
# each category corresponds to a job classad attr and expressions to apply to it for buckets 
DEFAULT_JOB_CATEGORIES = [
  #[ "VO_Name=='cms'", "VO_Name=='des'", "VO_Name=='nova'" ],
  ["RequestCPUs==1", "RequestCPUs==2", "RequestCPUs=4"],
  #[ "MaxWallTimeMins>0 && MaxWallTimeMins<= 60*12", "MaxWallTimeMins>60*12 && MaxWallTimeMins<= 60*24", "MaxWallTimeMins>60*24 && MaxWallTimeMins<= 60*12*2", "MaxWallTimeMins>60*24*2 && MaxWallTimeMins<= 60*12*4" ],
  #[ "RequestMemory==??" ],
  #[ "Require_CVMFS==True", "Require_CVMFS==False" ],
  #[ "Input_IO_Rate ==??" ], 
  #[ "Data_Location=='fnal'", "Data_Location=='aaa'", "Data_Location=='cloud'", "Data_Location=='local'" ]
]

# TODO 
# - what debugging logs are needed?
# - what and how is metadata for a dataframe?
# - do we need to validate case or type for attr content?  again onboarding?

class JobClustering(Transform.Transform):
    
    def __init__(self, config):
        super(JobClustering, self).__init__(config)

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.job_categories = config.get('job_categories')

        self.logger = de_logger.get_logger()

    def consumes(self):
        """
        Return list of items consumed
        """
        return CONSUMES


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def transform(self, datablock):

        self.logger.info("*** Starting job clustering ***")
        # TODO not sure if metadata is propagated or if this is the right attrs to id a datablock
#        self.logger.info("Using job manifests data block taskmanager=%s, generation=%s" % datablock.taskmanager_id, datablock.generation_id)

        # Get job queue datablock
        try:
            df_q = datablock.get('job_manifests')
        except KeyError, ValueError:
            self.logger.error("Unable to retrieve job manifests data block")
            return pandas.DataFrame({
                'Bucket_Criteria_Expr': [""],
                'Totals': [0]
                },
                columns=['Bucket_Criteria_Expr', 'Totals'])
            

        # Read in category configs
        if self.job_categories:
            job_category_config = self.job_categories
            self.logger.info("Using config job categories")
        else:
            job_category_config = DEFAULT_JOB_CATEGORIES
            self.logger.info("Using DEFAULT job categories")

        # Create clusters
        buckets = list(itertools.product(*job_category_config))

        # Append tuple into single query string
        bucket_list = [" and ".join(x) for x in buckets]
        self.logger.debug("Buckets created: %s" % bucket_list)

        # Create bucket dataframe and extend with totals
        df_job_clusters = pandas.DataFrame(bucket_list, columns=["Bucket_Criteria_Expr"])
        df_job_clusters['Totals'] = pandas.Series([0]*len(bucket_list))

        try:
            # Query job q and populate bucket totals
            for b_l in bucket_list:
                # Get index
                buckets_idx = df_job_clusters.index[df_job_clusters["Bucket_Criteria_Expr"] == b_l].tolist()[0]
                df_job_clusters.iloc[buckets_idx,1] = df_q.query(b_l).shape[0]
            self.logger.debug("Job category totals:\n" % df_job_clusters)
        except KeyError, ValueError:
            self.logger.error("Unable to calculate totals from job manifests, may have missing classads or incorrect classad names")
            return pandas.DataFrame({
                'Bucket_Criteria_Expr': [""],
                'Totals': [0]
                },
                columns=['Bucket_Criteria_Expr', 'Totals'])

        self.logger.info("*** Ending job clustering ***")

        return {'job_clusters': df_job_clusters}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        't_job_categorization': {
            'module': 'decisionengine.modules.glideinwms.t_job_clustering',
            'name': 'JobClustering',
            'parameters': {
                'job_categories': [
                   ["VO_Name=='cms'", "VO_Name=='des'", "VO_Name=='nova'"],
                   ["RequestCpus==1", "RequestCpus==2", "RequestCpus==4"],
                   ["(MaxWallTimeMins>0 && MaxWallTimeMins<= 60*12)", "(MaxWallTimeMins>60*12 && MaxWallTimeMins<= 60*24)", "(MaxWallTimeMins>60*24 && MaxWallTimeMins<= 60*12*2)"]
                 ]
            },
        }
    }
    print('Job categorization')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)
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
