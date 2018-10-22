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

# TODO 
# - what debugging logs are needed?
# - what and how is metadata for a dataframe?
# - do we need to validate case or type for attr content?  again onboarding?

class JobClustering(Transform.Transform):
    
    def __init__(self, config):
        super(JobClustering, self).__init__(config)

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.match_exprs = config.get('match_expressions')
        self.job_q_expr = config.get('job_q_expr')

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
            df_full_q = datablock.get('job_manifests')
            df_q = df_full_q.query(self.job_q_expr)
        except KeyError, ValueError:
            self.logger.error("Unable to retrieve job manifests data block")
            return pandas.DataFrame({
                'Job_Bucket_Criteria_Expr': [""],
                'Site_Bucket_Criteria_Expr': [""],
                'Totals': [0]
                },
                columns=['Job_Bucket_Criteria_Expr', 'Site_Bucket_Criteria_Expr', 'Totals'])

        totals = []
        try:
            # Query job q and populate bucket totals
            totals = [[job_expr, self.match_exprs.get(job_expr), df_q.query(job_expr).shape[0]] for job_expr in self.match_exprs.keys()]
            df_job_clusters = pandas.DataFrame(totals, columns=['Job_Bucket_Criteria_Expr', 'Site_Bucket_Criteria_Expr', 'Totals'])
            self.logger.debug("Job category totals: %s" % df_job_clusters)
        except KeyError, ValueError:
            self.logger.error("Unable to calculate totals from job manifests, may have missing classads or incorrect classad names")
            return pandas.DataFrame({
                'Job_Bucket_Criteria_Expr': [""],
                'Site_Bucket_Criteria_Expr': [""],
                'Totals': [0]
                },
                columns=['Job_Bucket_Criteria_Expr', 'Site_Bucket_Criteria_Expr', 'Totals'])

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
                'match_expressions': {
                      "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"]
                 }
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
