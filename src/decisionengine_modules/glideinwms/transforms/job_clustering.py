import pandas

from decisionengine.framework.modules import Transform
from decisionengine.framework.modules.Transform import Parameter

# TODO
# - what debugging logs are needed?
# - what and how is metadata for a dataframe?
# - do we need to validate case or type for attr content?  again onboarding?

@Transform.supports_config(Parameter('match_expressions',
                                     default={"VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)":
                                              ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"]}))
@Transform.consumes(job_manifests=pandas.DataFrame)
@Transform.produces(job_clusters=pandas.DataFrame)
class JobClustering(Transform.Transform):

    def __init__(self, config):
        super().__init__(config)

        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.match_exprs = config.get('match_expressions')
        self.job_q_expr = config.get('job_q_expr')

        # Creating dataframe with config info but all totals are zero
        totals = [[job_expr.get('job_bucket_criteria_expr'), job_expr.get('site_bucket_criteria_expr'),
                   0, job_expr.get('frontend_group')] for job_expr in self.match_exprs]
        self.EMPTY_JOB_CLUSTER = pandas.DataFrame(totals,
                                                  columns=['Job_Bucket_Criteria_Expr', 'Site_Bucket_Criteria_Expr',
                                                           'Totals', 'Frontend_Group'])

        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    def transform(self, datablock):

        self.logger.info("*** Starting job clustering ***")
        # TODO not sure if metadata is propagated or if this is the right attrs to id a datablock

        # Get job queue datablock
        try:
            df_full_q = datablock.get('job_manifests')
        except KeyError:
            self.logger.exception("Unable to retrieve job manifests data block")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}
        except ValueError:
            self.logger.exception("Unable to retrieve job manifests data block")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}
        except pandas.core.computation.ops.UndefinedVariableError:
            self.logger.exception("Unable to retrieve job manifests data block")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}

        # Return empty block if no job data
        if df_full_q.empty:
            self.logger.debug("Empty job manifests data block found")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}

        totals = []
        # VERSION WITHOUT FRONTEND
        """
        try:
            df_q = df_full_q.fillna('').query(self.job_q_expr)
            # Query job q and populate bucket totals
            totals = [[job_expr, self.match_exprs.get(job_expr), df_q.query(job_expr).shape[0]]
                      for job_expr in self.match_exprs.keys()]
            df_job_clusters = pandas.DataFrame(totals,
                                               columns=['Job_Bucket_Criteria_Expr',
                                                        'Site_Bucket_Criteria_Expr', 'Totals'])
            self.logger.debug("Job category totals: %s" % df_job_clusters)
        """
        # VERSION WITH FRONTEND, DELETE AND USE ABOVE WHEN FRONTEND IS GONE
        try:
            df_q = df_full_q.query(self.job_q_expr)
            # Query job q and populate bucket totals
            totals = [[job_expr.get('job_bucket_criteria_expr'), job_expr.get('site_bucket_criteria_expr'),
                       df_q.query(job_expr.get('job_bucket_criteria_expr')).shape[0],
                       job_expr.get('frontend_group')] for job_expr in self.match_exprs]
            df_job_clusters = pandas.DataFrame(totals,
                                               columns=['Job_Bucket_Criteria_Expr', 'Site_Bucket_Criteria_Expr',
                                                        'Totals', 'Frontend_Group'])
            self.logger.debug("Job category totals: %s" % df_job_clusters)

        except KeyError:
            self.logger.exception(
                "Unable to calculate totals from job manifests, may have missing classads or incorrect classad names")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}
        except ValueError:
            self.logger.exception(
                "Unable to calculate totals from job manifests, may have missing classads or incorrect classad names")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}
        except pandas.core.computation.ops.UndefinedVariableError:
            self.logger.exception(
                "Unable to calculate totals from job manifests, may have missing classads or incorrect classad names")
            return {'job_clusters': self.EMPTY_JOB_CLUSTER}

        self.logger.info("*** Ending job clustering ***")

        return {'job_clusters': df_job_clusters}


Transform.describe(JobClustering)
