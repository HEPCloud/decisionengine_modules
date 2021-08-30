import os.path
import pandas
import numpy

from decisionengine.framework.modules import Transform
from decisionengine.framework.modules.Transform import Parameter
from decisionengine_modules.glideinwms import glide_frontend_element
from decisionengine_modules.glideinwms.resource_dist_plugins import fom_eligible_resources


_CONSUMES = [
    'factoryglobal_manifests', 'job_manifests', 'job_clusters',
    'Factory_Entries_LCF', 'startd_manifests', 'Factory_Entries_AWS',
    'Grid_Figure_Of_Merit', 'GCE_Figure_Of_Merit', 'AWS_Figure_Of_Merit',
    'Nersc_Figure_Of_Merit',
]

_SUPPORTED_ENTRY_TYPES = [
    'Factory_Entries_LCF', 'Factory_Entries_AWS', 'Factory_Entries_Grid', 'Factory_Entries_GCE'
]

# TODO: Extend to use following in future
# 'Nersc_Job_Info', 'Nersc_Allocation_Info'

@Transform.supports_config(Parameter('accounting_group', type=str, default='CMS'),
                           Parameter('job_filter', type=str, default='ClusterId > 0'),
                           Parameter('fe_config_group', type=str, default='CMS'),
                           Parameter('fom_resource_constraint'),
                           Parameter('fom_resource_limit'),
                           Parameter('de_frontend_config', type=str, default='/var/lib/gwms-frontend/vofrontend/de_frontend_config'))
@Transform.consumes(**dict.fromkeys(_CONSUMES, pandas.DataFrame))
@Transform.produces(glideclientglobal_manifests=pandas.DataFrame,
                    glideclient_manifests=pandas.DataFrame)
class GlideinRequestManifests(Transform.Transform):

    def __init__(self, config):
        super().__init__(config)

        # VO to which this transform should be applied
        self.acct_group = config.get('accounting_group', 'CMS')
        # Filter to further select jobs matching the criteria
        self.job_filter = config.get('job_filter', 'ClusterId > 0')
        # FE config group to get settings from
        self.fe_group = config.get('fe_config_group', 'CMS')
        # FOM Plugin
        self.fom_resource_constraint = config.get('fom_resource_constraint')
        self.fom_resource_limit = config.get('fom_resource_limit')
        # Get the place where translated frontend config is located
        self.de_frontend_configfile = config.get(
            'de_frontend_config',
            '/var/lib/gwms-frontend/vofrontend/de_frontend_config')
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )


    def transform(self, datablock):
        """
        Make all necessary calculations

        :type datablock: :obj:`~datablock.DataBlock`
        :arg datablock: data block

        :rtype: pandas frame (:class:`pd.DataFramelist`)
        """

        # Dict to be returned
        self.logger.debug("in GlideinRequestManifests transform")
        manifests = {}

        try:
            # Get the frontend config dict
            fe_cfg = self.read_fe_config()
            # Get factory global classad dataframe
            factory_globals = datablock.get('factoryglobal_manifests')
            entries = pandas.DataFrame(pandas.concat(
                [datablock.get(et) for et in _SUPPORTED_ENTRY_TYPES], ignore_index=True, sort=True))
            if entries.empty:
                self.logger.info('There are no entries to request resources from')
                return dict.fromkeys(
                    ['glideclientglobal_manifests', 'glideclient_manifests'], pandas.DataFrame())

            # Sanitize 'auto' in GLIDEIN_CPUS and convert it to a valid int
            entries = self.sanitize_entries(entries)
            # Shortlisted entries using Figure of Merit
            # TODO: This will be influenced once we can configure different
            #       resource selection plugins. Currently supports FOM only.
            foms = {
                'Grid_Figure_Of_Merit': self.Grid_Figure_Of_Merit(datablock),
                'GCE_Figure_Of_Merit': self.GCE_Figure_Of_Merit(datablock),
                'AWS_Figure_Of_Merit': self.AWS_Figure_Of_Merit(datablock),
                'Nersc_Figure_Of_Merit': self.Nersc_Figure_Of_Merit(datablock)
            }
            fom_entries = fom_eligible_resources(foms,
                                                 constraint=self.fom_resource_constraint,
                                                 limit=self.fom_resource_limit)
            self.logger.debug('Figure of Merits')
            self.logger.debug(fom_entries)

            # Get the jobs dataframe
            jobs_df = self.job_manifests(datablock)
            # Get the job clusters dataframe
            job_clusters_df = self.job_clusters(datablock)
            # Get HTCondor slots dataframe
            slots_df = self.startd_manifests(datablock)

            # self.logger.info(job_clusters_df)
            for index, row in job_clusters_df.iterrows():
                # Each job bucket represents a frontend group equivalent
                # For every job bucket figure out how many glideins to request
                # at which entry (i.e entries matching entry query expressions)

                self.logger.info(
                    '--------------------------------------------')
                fe_group = row.get('Frontend_Group')

                self.logger.info(
                    'Processing glidein requests for the FE Group: %s' % fe_group)
                job_query = row.get('Job_Bucket_Criteria_Expr')
                self.logger.info('Frontend Group %s job query: %s' %
                                 (fe_group, job_query))
                match_exp = ' or '.join(row.get('Site_Bucket_Criteria_Expr'))
                self.logger.info(
                    'Frontend Group %s site matching expression : %s' % (fe_group, match_exp))
                self.logger.info(
                    '--------------------------------------------')

                matched_entries = entries.query(match_exp)

                # Get the Frontend element object. Currently FOM.
                gfe = glide_frontend_element.get_gfe_obj(
                    fe_group, self.acct_group, fe_cfg)

                # Generate glideclient and glideclientglobal manifests
                # for this bucket/frontend group
                group_manifests = \
                    gfe.generate_glidein_requests(
                        # jobs_df, job_clusters_df, slots_df, matched_entries,
                        jobs_df, slots_df, matched_entries, factory_globals,
                        job_filter=job_query, fom_entries=fom_entries)
                manifests = self.merge_requests(manifests, group_manifests)
        except Exception:
            self.logger.exception('Error generating glidein requests')
            raise

        return manifests

    def sanitize_entries(self, entries):
        """
        Sanitize values of columns like GLIDEIN_CPUS and return sanitized
        dataframe with original columns copied to COL_DE_ORIGINAL
        """
        tag = 'DE_ORIGINAL'

        entries['GLIDEIN_CPUS_%s' % tag] = entries['GLIDEIN_CPUS']
        if 'GLIDEIN_ESTIMATED_CPUS' in entries.columns:
            entries['GLIDEIN_ESTIMATED_CPUS_%s' %
                    tag] = entries['GLIDEIN_ESTIMATED_CPUS']
            entries = entries.fillna(value={'GLIDEIN_ESTIMATED_CPUS': 1})
        else:
            entries['GLIDEIN_ESTIMATED_CPUS_%s' %
                    tag] = pandas.Series([numpy.nan] * len(entries))
            entries['GLIDEIN_ESTIMATED_CPUS'] = pandas.Series([1] * len(entries))
        return entries.apply(sanitize_glidein_cpus, axis=1)

    def merge_requests(self, manifests, group_manifests):
        merged_manifests = {}
        if manifests and group_manifests:
            m_keys = set(manifests.keys())
            g_keys = set(group_manifests.keys())
            if m_keys != g_keys:
                self.logger.exception(f"Mismatch in manifest keys: {m_keys}, {g_keys}")
                raise RuntimeError()
            for key in m_keys:
                merged_manifests[key] = manifests[key].append(
                    group_manifests[key], ignore_index=True)
        else:
            merged_manifests = group_manifests
        return merged_manifests

    def read_fe_config(self):
        if not os.path.isfile(self.de_frontend_configfile):
            self.logger.exception(
                'Error reading Frontend config for DE %s. '
                'Run configure_gwms_frontend.py to generate one and after every change to the frontend configuration.' %
                self.de_frontend_configfile)
            raise RuntimeError()

        fe_cfg = eval(open(self.de_frontend_configfile, 'r').read())

        if not isinstance(fe_cfg, dict):
            self.logger.exception(f"Frontend config for DE in {self.de_frontend_configfile} is invalid")
            raise ValueError()
        return fe_cfg


def sanitize_glidein_cpus(row):
    if str(row['GLIDEIN_CPUS']).lower() == 'auto':
        row['GLIDEIN_CPUS'] = row['GLIDEIN_ESTIMATED_CPUS']
    row['GLIDEIN_CPUS'] = int(row['GLIDEIN_CPUS'])
    return row


Transform.describe(GlideinRequestManifests)
