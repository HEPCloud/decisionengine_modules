import copy
import logging
import math
import sys

import pandas
from glideinwms.frontend import glideinFrontendConfig
from glideinwms.frontend import glideinFrontendInterface
from glideinwms.frontend import glideinFrontendPlugins
from glideinwms.lib import pubCrypto

from decisionengine_modules.glideinwms import classads
from decisionengine_modules.glideinwms.security import Credential
from decisionengine_modules.glideinwms.security import CredentialCache

pandas.options.mode.chained_assignment = None  # default='warn'

# TODO: Need a better way of setting global logger
logger = logging.getLogger()


class NoCredentialException(Exception):
    pass


def get_gfe_obj(fe_group, acct_group, fe_cfg, gfe_type='glideinwms_fom'):
    """
    Return glide frontend object of right type based on request
    """
    gfe_obj = None
    if gfe_type == 'glideinwms_fom':
        gfe_obj = GlideFrontendElementFOM(fe_group, acct_group, fe_cfg)
    elif gfe_type == 'glideinwms':
        gfe_obj = GlideFrontendElement(fe_group, acct_group, fe_cfg)
    else:
        raise RuntimeError(
            'GlideFrontendElement of type %s not supported' % gfe_type)
    return gfe_obj


class GlideFrontendElement(object):
    """
    Class that implements the functionality of a GlideinWMS Frontend Element
    """

    def __init__(self, fe_group, acct_group, fe_cfg):
        self.logger = logging.getLogger()
        self.fe_group = fe_group
        self.acct_group = acct_group
        self.fe_cfg = fe_cfg

    def generate_glidein_requests(self, jobs_df, slots_df,
                                  entries, factory_globals,
                                  job_filter='ClusterId > 0'):
        ########################################################################
        # STEP 1: Get info from frontend configuration
        # STEP 2: Get credentials to be used for the submission
        ########################################################################

        self.file_id_cache = CredentialCache()
        # Used to map key_obj. Key = (factory_collector)
        self.global_key = {}

        self.read_fe_config()

        # TODO: Figure out how to deal with this info in new scheme
        # Create the params descript object. It stores info about the
        # frontend params/const info
        self.params_descript = glideinFrontendConfig.ParamsDescript(
            self.frontend_workdir, self.fe_group)

        ########################################################################
        # STEP 3: Get glidefactoryglobal and glideentry classads
        ########################################################################

        factory_globals['PubKeyObj'] = self.create_factory_pubkeyobj(
            factory_globals)
        self.glideid_list = self.create_glideid_list(entries)

        ########################################################################
        # STEP 4: Get job and slot classads
        #         Categorize jobs and slots based on their respective status
        ########################################################################

        if not jobs_df.empty:
            # Apply filter to jobs df only if it is not empty
            jobs_df = jobs_df.query(job_filter)
        # Categorize jobs with different status criteria
        job_types = self.categorize_jobs(jobs_df)

        # Categorize HTCondor slots for this group based on status criteria
        slot_types = self.categorize_slots(slots_df)

        self.logger.info('Jobs found total %i idle %i (good %i, old(10min %s, 60min %i), grid %i, voms %i) running %i'
                         % (len(jobs_df), job_types['IdleAll']['abs'],
                            job_types['Idle']['abs'], job_types['OldIdle']['abs'],
                            job_types['Idle_3600']['abs'], job_types['ProxyIdle']['abs'],
                            job_types['VomsIdle']['abs'], job_types['Running']['abs'])
                         )

        # TODO: appendRealRunning -> For every job in schedd
        #       add classad attr RunningOn based on job status
        #       Run = GLIDEIN_Entry_Name@GLIDEIN_Name@GLIDEIN_Factory@fact_pool
        #       Idle = UNKNOWN
        # Find out best way to do this in pandas
        # This is useful to figure out which jobs are running on which glideins
        # It should also be possible to achieve this through config
        # SYSTEM_JOB_MACHINE_ATTRS. Only problem with
        # that approach is, we may not be able to enforce it

        total_slots = slot_types['Total']['abs']
        total_running_slots = slot_types['Running']['abs']
        total_idle_slots = slot_types['Idle']['abs']

        self.logger.info('Group slots found total %i (limit %i curb %i) idle %i (limit %i curb %i) running %i'
                         % (total_slots,
                            self.total_max_slots,
                            self.total_curb_slots,
                            total_idle_slots,
                            self.total_max_slots_idle,
                            self.total_curb_slots_idle,
                            total_running_slots)
                         )
        # TODO: Need to compute following
        #       fe_[total_slots | total_idle_slots | total_running_slots]
        #       global_[total_slots | total_idle_slots | total_running_slots]
        self.logger.info('Frontend slots found total %i?? (limit %i curb %i) idle?? %i (limit %i curb %i) running %i??'
                         % (total_slots,
                            self.fe_total_max_slots,
                            self.fe_total_curb_slots,
                            total_idle_slots,
                            self.fe_total_max_slots_idle,
                            self.fe_total_curb_slots_idle,
                            total_running_slots)
                         )

        self.logger.info('Overall slots found total %i?? (limit %i curb %i) idle?? %i (limit %i curb %i) running %i??'
                         % (total_slots,
                            self.global_total_max_slots,
                            self.global_total_curb_slots,
                            total_idle_slots,
                            self.global_total_max_slots_idle,
                            self.global_total_curb_slots_idle,
                            total_running_slots)
                         )

        # Add entry info to each running slot's classad
        append_running_on(job_types['Running']['dataframe'],
                          slot_types['Running']['dataframe'])

        ########################################################################
        # STEP 5: Match the jobs to the entries
        #         This may be the place to plugin custom algorithms
        ########################################################################
        self.match(job_types, slot_types, entries)

        ########################################################################
        # STEP 6: Create glideclientglobal classads
        ########################################################################

        key_builder = glideinFrontendInterface.Key4AdvertizeBuilder()
        # List of classad objects
        self.gc_classads = []
        self.gcg_classads = []

        # Create the glideclientglobal classads first to load credentials.
        # This loads the credentials. If loading the credential fails, that
        # credential is ignored while creating a glideclient classad
        for index, row in factory_globals.iterrows():
            self.gcg_classads.append(
                self.create_glideclientglobal_classads(row, key_builder))

        ########################################################################
        # STEP 7: Apply any limits and thresholds to come up with final number
        ########################################################################

        # List of glideids that have idle jobs
        glideids_with_idle_jobs = job_types['Idle']['count'].keys()

        # For faster lookup
        self.processed_glideid_strs = []

        log_factory_header()
        total_up_stats_arr = init_factory_stats_arr()
        total_down_stats_arr = init_factory_stats_arr()

        # Get the FOM info and generate requests based on the FOM

        for glideid in glideids_with_idle_jobs:
            if glideid == (None, None):
                # Ignore the unmatched entries
                continue

            # Find my identity at factory from the config for this glideid
            factory_pool_node = glideid[0]
            request_name = glideid[1]
            my_identity = None
            fact_cols = self.fe_cfg['group'][self.fe_group]['factory_collectors']
            for fact_col in fact_cols:
                if fact_col[0] == factory_pool_node:
                    my_identity = fact_col[2]

            glideid_str = "%s@%s" % (request_name, factory_pool_node)
            self.processed_glideid_strs.append(glideid_str)
            entry_info = entries.query(
                'Name == "%s" and CollectorHost == "%s"' % (request_name, factory_pool_node))

            # Some short hand variables for easy reference
            entry_in_downtime = entry_info.get(
                'GLIDEIN_In_Downtime').tolist()[0] == 'True'
            count_jobs = {}    # Count of jobs with straight matches
            prop_jobs = {}     # proportional subset for this entry
            # proportional subset of jobs for this entry scaled also for
            # multicore (requested cores/available cores)
            prop_mc_jobs = {}
            hereonly_jobs = {}  # can only run on this site
            for status in job_types:
                count_jobs[status] = job_types[status]['count'].get(glideid, 0)
                prop_jobs[status] = job_types[status]['prop'].get(glideid, 0)
                prop_mc_jobs[status] = job_types[status]['prop_match_cpu'].get(
                    glideid, 0)
                hereonly_jobs[status] = job_types[status]['hereonly'].get(
                    glideid, 0)

            count_slots = self.count_entry_slots[request_name]
            count_slots_per_cred = self.count_entry_slots_cred[request_name]

            # TODO: Figure out a way to introduce glexec
            #       Assume false for now
            use_glexec = 'NEVER'
            if use_glexec != 'NEVER':
                if entry_info.get('GLIDEIN_REQUIRE_VOMS') == 'True':
                    prop_jobs['Idle'] = prop_jobs['VomsIdle']
                    self.logger.info(
                        'Voms proxy required, limiting idle glideins based on jobs: %i' % prop_jobs['Idle'])
                elif entry_info.get('GLIDEIN_REQUIRE_GLEXEC_USE') == 'True':
                    prop_jobs['Idle'] = prop_jobs['ProxyIdle']
                    self.logger.info(
                        'Proxy required (GLEXEC), limiting idle glideins based on jobs: %i' % prop_jobs['Idle'])

            # MMDB should be debug
            self.logger.info("Request %s: prop jobs %s(mc %s, min %s), available slots %s "
                             % (request_name,
                                prop_jobs['Idle'],
                                prop_mc_jobs['Idle'],
                                self.entry_min_glideins_running,
                                count_slots['Idle'], )
                             )

            # effective idle is how much more we need
            # if there are idle slots, subtract them, they should match soon
            effective_idle = max(prop_jobs['Idle'] - count_slots['Idle'], 0)

            # Adjust the number of idle jobs in case
            # the minimum running parameter is set
            if prop_mc_jobs['Idle'] < self.entry_min_glideins_running:
                self.logger.info("Entry %s: "
                                 "Adjusting idle cores to %s since the 'min' attribute of "
                                 "'running_glideins_per_entry' is set"
                                 % (request_name, self.entry_min_glideins_running)
                                 )
                prop_mc_jobs['Idle'] = self.entry_min_glideins_running

            # Compute min glideins required based on multicore jobs
            effective_idle_mc = max(
                prop_mc_jobs['Idle'] - count_slots['Idle'], 0)
            effective_oldidle_mc = max(
                prop_mc_jobs['OldIdle'] - count_slots['Idle'], 0)

            limits_triggered = {}
            # Compute minimum idle glideins required for this request_name
            # TODO: Understand what to put for fe_total_slots,
            #       fe_total_idle_slots, lobal_total_slots,
            #       global_total_idle_slots,
            glidein_min_idle = self.compute_glidein_min_idle(
                count_slots, total_slots, total_idle_slots,
                # fe_total_slots, fe_total_idle_slots,
                total_slots, total_idle_slots,
                # global_total_slots, global_total_idle_slots,
                total_slots, total_idle_slots,
                effective_idle_mc, effective_oldidle_mc,
                limits_triggered)
            # Compute maximum running glideins required for this request_name
            glidein_max_run = self.compute_glidein_max_running(
                prop_mc_jobs,
                self.count_real_glideins[glideid],
                count_slots['Idle'])

            # TODO: Figure out what to do with monitoring
            # Frontend groups logs stats here creating web monitoring xml files
            # adding data to rrds etc.

            this_stats_arr = (prop_jobs['Idle'], count_jobs['Idle'],
                              effective_idle, prop_jobs['OldIdle'],
                              hereonly_jobs['Idle'], count_jobs['Running'],
                              self.count_real_jobs[glideid],
                              self.entry_max_glideins,
                              count_slots['Total'],
                              count_slots['Idle'],
                              count_slots['Running'],
                              count_slots['Failed'],
                              count_slots['TotalCores'],
                              count_slots['IdleCores'],
                              count_slots['RunningCores'],
                              glidein_min_idle, glidein_max_run)

            if entry_in_downtime:
                total_down_stats_arr = log_and_sum_factory_line(
                    glideid_str, entry_in_downtime,
                    this_stats_arr, total_down_stats_arr)
            else:
                total_up_stats_arr = log_and_sum_factory_line(
                    glideid_str, entry_in_downtime,
                    this_stats_arr, total_up_stats_arr)

            # Get the parameters from the frontend config
            glidein_params = copy.deepcopy(self.params_descript.const_data)
            for k in self.params_descript.expr_data:
                kexpr = self.params_descript.expr_objs[k]
                glidein_params[k] = eval(kexpr)
            # Add GLIDECLIENT_ReqNode to monitor orphaned glideins
            glidein_params['GLIDECLIENT_ReqNode'] = factory_pool_node

            glidein_monitors = {k: count_jobs[k] for k in count_jobs}
            glidein_monitors['RunningHere'] = self.count_real_jobs[glideid]
            for t in count_slots:
                glidein_monitors['Glideins%s' % t] = count_slots[t]

            # Number of credentials that have running and glideins.
            # This will be used to scale down the glidein_monitors[Running]
            # when there are multiple credentials per group.
            # This is efficient way of achieving the end result. Note that
            # Credential specific stats are not presented anywhere except the
            # classad. Monitoring info in frontend and factory shows
            # aggregated info considering all the credentials
            glidein_monitors_per_cred = {}
            creds_with_running = 0
            for cred in self.credential_plugin.cred_list:
                glidein_monitors_per_cred[cred.get_id()] = {
                    'Glideins%s' % t: count_slots_per_cred[cred.get_id()][t] for t in count_slots}
                glidein_monitors_per_cred[cred.get_id()]['ScaledRunning'] = 0
                if glidein_monitors_per_cred[cred.get_id()]['GlideinsRunning']:
                    creds_with_running += 1

            if creds_with_running:
                # Counter to handle rounding errors
                scaled = 0
                tr = glidein_monitors['Running']
                for cred in self.credential_plugin.cred_list:
                    cred_monitor = glidein_monitors_per_cred[cred.get_id()]
                    if cred_monitor['GlideinsRunning']:
                        # This cred has running, scale them down
                        if (creds_with_running - scaled) == 1:
                            cred_monitor['ScaledRunning'] = tr - \
                                (tr // creds_with_running) * scaled
                            scaled += 1
                            break
                        else:
                            cred_monitor['ScaledRunning'] = tr // creds_with_running
                            scaled += 1

            key_obj = None
            for index, row in factory_globals.iterrows():
                pubkeyid = row.get('PubKeyID', None)
                pubkeyobj = row.get('PubKeyObj', None)
                if glideid[1].endswith(row['Name']) and pubkeyid and pubkeyobj:
                    key_obj = key_builder.get_key_obj(
                        my_identity, pubkeyid, pubkeyobj)
                    break

            # TODO: These two come from glidefactory classad rows how to get it?
            trust_domain = entry_info.get('GLIDEIN_TrustDomain',
                                          ['Grid']).tolist()[0]
            auth_method = entry_info.get(
                'GLIDEIN_SupportedAuthenticationMethod',
                ['grid_proxy']).tolist()[0]

            # Only advertize if there is a valid key for encryption
            if key_obj is not None:
                gc_classad = self.create_glideclient_classads(
                    factory_pool_node, request_name, request_name,
                    glidein_min_idle, glidein_max_run, self.idle_lifetime,
                    glidein_params=glidein_params,
                    glidein_monitors=glidein_monitors,
                    glidein_monitors_per_cred=glidein_monitors_per_cred,
                    key_obj=key_obj, glidein_params_to_encrypt=None,
                    security_name=self.security_name, remove_excess_str=None,
                    trust_domain=trust_domain, auth_method=auth_method)
                self.gc_classads.extend(gc_classad)
            else:
                self.logger.warning("Cannot advertise requests for %s because no factory %s key was found" % (
                    request_name, factory_pool_node))

        # TODO: Enable following logging in future
        """
        total_down_stats_arr = self.count_factory_entries_without_classads(total_down_stats_arr)

        self.log_and_print_total_stats(total_up_stats_arr, total_down_stats_arr)
        self.log_and_print_unmatched(total_down_stats_arr)
        """

        # TODO: Enable following renewing and loading credentials
        """
        pids=[]
        # Advertise glideclient and glideclient global classads
        ad_file_id_cache=glideinFrontendInterface.CredentialCache()
        advertizer.renew_and_load_credentials()
        """

        gcg_df = pandas.DataFrame([ad.adParams for ad in self.gcg_classads])
        gc_df = pandas.DataFrame([ad.adParams for ad in self.gc_classads])
        return {
            'glideclientglobal_manifests': gcg_df,
            'glideclient_manifests': gc_df
        }

    def get_factory_key_ad_params(self, key_obj):
        # ReqEncIdentity will be checked against the AuthenticatedIdentity
        # This will prevent replay attacks, as only who knows the symkey
        # can change this field no other changes needed, as Condor provides
        # integrity of the whole classAd
        glidein_symKey_str = key_obj.glidein_symKey.get_code()
        ad_params = {
            'ReqPubKeyID': key_obj.factory_pub_key_id,
            'ReqEncKeyCode': key_obj.factory_pub_key.encrypt_hex(glidein_symKey_str),
            'ReqEncIdentity': key_obj.encrypt_hex(str(key_obj.classad_identity))
        }
        return ad_params

    def create_glideclient_classads(self, factory_pool, request_name,
                                    glidein_name, min_nr_glideins,
                                    max_run_glideins, idle_lifetime,
                                    glidein_params={}, glidein_monitors={},
                                    glidein_monitors_per_cred={}, key_obj=None,
                                    glidein_params_to_encrypt=None,
                                    security_name=None, remove_excess_str=None,
                                    trust_domain='Any', auth_method='Any'):

        # params_obj is only required for fair_assign in the plugins
        # Else it is not really useful as the info is available in other vars
        params_obj = glideinFrontendInterface.AdvertizeParams(
            request_name, glidein_name, min_nr_glideins, max_run_glideins,
            glidein_params=glidein_params,
            glidein_monitors=glidein_monitors,
            glidein_monitors_per_cred=glidein_monitors_per_cred,
            glidein_params_to_encrypt=glidein_params_to_encrypt,
            security_name=security_name, remove_excess_str=remove_excess_str)

        credentials_with_request = self.credential_plugin.get_credentials(
            params_obj=params_obj, credential_type=auth_method,
            trust_domain=trust_domain)

        if not credentials_with_request:
            raise NoCredentialException

        # There will one glideclient classad per glidefactory classad for
        # every credential in this group
        # List of glideclient classad objects to return
        gc_classads = []

        for cred in credentials_with_request:
            if not cred.advertize:
                self.logger.info('Ignoring credential with id: %s, '
                                 'pilot_proxy: %s, type: %s, trust_domain: %s, security_name: %s, advertise: %s'
                                 % (cred.get_id(),
                                    cred.pilot_fname,
                                    cred.type,
                                    cred.trust_domain,
                                    cred.security_class,
                                    cred.advertize)
                                 )
                # We have already determined that this cred cannot be used
                continue

            if not cred.supports_auth_method(auth_method):
                self.logger.warning('Credential %s does not match auth method %s (for %s), skipping...' % (
                    cred.type, auth_method, params_obj.request_name))
                continue

            if cred.trust_domain != trust_domain:
                self.logger.warning('Credential %s does not match %s (for %s) domain, skipping...' % (
                    cred.trust_domain, trust_domain, params_obj.request_name))
                continue

            glidein_monitors_this_cred = {}
            if glidein_params_to_encrypt is None:
                glidein_params_to_encrypt = {}
            else:
                glidein_params_to_encrypt = copy.deepcopy(
                    glidein_params_to_encrypt)
            req_idle, req_max_run = cred.get_usage_details()
            # TODO: Need to print this somewhere but currently logging this is interleaved with stats
            # self.logger.info('Advertizing credential %s with (%d idle, %d max run) for request %s' %
            # (cred.filename, req_idle, req_max_run, params_obj.request_name))

            glidein_monitors_this_cred = params_obj.glidein_monitors_per_cred.get(
                cred.get_id(), {})

            # Create GlideClientClassad object
            my_name = '%s.%s' % (self.frontend_name, self.fe_group)
            gc_classad = classads.GlideClientClassad(glidein_name, my_name)
            # Make the classad name unique by adding credential id to it
            gc_classad.adParams['Name'] = '%s_%s' % \
                (self.file_id_cache.file_id(cred, cred.filename),
                 gc_classad.adParams['Name'])
            gc_classad.adParams['CollectorHost'] = factory_pool
            gc_classad.adParams['FrontendName'] = self.frontend_name
            gc_classad.adParams['GroupName'] = self.fe_group
            gc_classad.adParams['FrontendHAMode'] = 'master'
            gc_classad.adParams['ReqName'] = request_name
            gc_classad.adParams['ReqGlidein'] = glidein_name

            gc_classad.adParams['ReqIdleGlideins'] = req_idle
            gc_classad.adParams['ReqMaxGlideins'] = req_max_run
            gc_classad.adParams['ReqRemoveExcess'] = params_obj.remove_excess_str
            gc_classad.adParams.update(self.get_factory_key_ad_params(key_obj))
            gc_classad.adParams['WebMonitoringURL'] = self.monitoring_web_url
            gc_classad.adParams['WebSignType'] = self.signature_type
            gc_classad.adParams['WebURL'] = self.web_url
            gc_classad.adParams['WebDescriptFile'] = self.descript_fname
            gc_classad.adParams['WebDescriptSign'] = self.descript_signature
            gc_classad.adParams['WebGroupURL'] = self.group_web_url
            gc_classad.adParams['WebGroupDescriptFile'] = self.group_descript_fname
            gc_classad.adParams['WebGroupDescriptSign'] = self.group_descript_signature

            params_attr = {'GlideinParam%s' % k: v for (
                k, v) in params_obj.glidein_params.items()}
            config_attr = {'GlideinConfig%s' % k: v for (
                k, v) in self.glidein_config_limits.items()}
            monitor_attr = {}
            for attr_name in params_obj.glidein_monitors:
                prefix = 'GlideinMonitor'
                if (attr_name == 'RunningHere') and glidein_monitors_this_cred:
                    attr_value = glidein_monitors_this_cred.get(
                        'GlideinsRunning', 0)
                elif (attr_name == 'Running') and glidein_monitors_this_cred:
                    attr_value = glidein_monitors_this_cred.get(
                        'ScaledRunning', 0)
                else:
                    attr_value = glidein_monitors_this_cred.get(
                        attr_name, params_obj.glidein_monitors[attr_name])
                monitor_attr['%s%s' % (prefix, attr_name)] = attr_value

            gc_classad.adParams.update(params_attr)
            gc_classad.adParams.update(config_attr)
            gc_classad.adParams.update(monitor_attr)

            # Add security class and security name to encrypted params
            glidein_params_to_encrypt['SecurityClass'] = str(
                cred.security_class)
            glidein_params_to_encrypt['SecurityName'] = str(self.security_name)

            # Add id for all the credential files
            if 'username_password' in cred.type:
                glidein_params_to_encrypt['Username'] = self.file_id_cache.file_id(
                    cred, cred.filename)
                glidein_params_to_encrypt['Password'] = self.file_id_cache.file_id(
                    cred, cred.key_fname)
            if 'grid_proxy' in cred.type:
                glidein_params_to_encrypt['SubmitProxy'] = self.file_id_cache.file_id(
                    cred, cred.filename)
            if 'cert_pair' in cred.type:
                glidein_params_to_encrypt['PublicCert'] = self.file_id_cache.file_id(
                    cred, cred.filename)
                glidein_params_to_encrypt['PrivateCert'] = self.file_id_cache.file_id(
                    cred, cred.key_fname)
            if 'key_pair' in cred.type:
                glidein_params_to_encrypt['PublicKey'] = self.file_id_cache.file_id(
                    cred, cred.filename)
                glidein_params_to_encrypt['PrivateKey'] = self.file_id_cache.file_id(
                    cred, cred.key_fname)
            if 'vm_id' in cred.type:
                glidein_params_to_encrypt['VMId'] = str(cred.vm_id)
            if 'vm_type' in cred.type:
                glidein_params_to_encrypt['VMType'] = str(cred.vm_type)
            if 'remote_username' in cred.type:
                glidein_params_to_encrypt['RemoteUsername'] = self.file_id_cache.file_id(
                    cred, cred.remote_username)
            if 'auth_file' in cred.type:
                glidein_params_to_encrypt['AuthFile'] = self.file_id_cache.file_id(
                    cred, cred.filename)
            if cred.project_id:
                glidein_params_to_encrypt['ProjectId'] = str(cred.project_id)

            # Add id for the pilot proxy
            if cred.pilot_fname:
                glidein_params_to_encrypt['GlideinProxy'] = self.file_id_cache.file_id(
                    cred, cred.pilot_fname)

            # Add classad attributes that need to be encrypted
            for attr in glidein_params_to_encrypt:
                value = str(key_obj.encrypt_hex(
                    glidein_params_to_encrypt[attr]))
                escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
                ad_attr = '%s%s' % ('GlideinEncParam', attr)
                gc_classad.adParams[ad_attr] = escaped_value

            gc_classads.append(gc_classad)

        return gc_classads

    def create_glideclientglobal_classads(self, glidefactory_classad,
                                          key_builder):
        """
        Create glideclientglobal classads. Use the factory key in the
        glidefactory classad to encrypt sensitive information
        """

        if not glidefactory_classad.get('PubKeyObj'):
            # Do not create glideclientglobal classads for factories
            # that do not have valid factory key objects
            return

        classad_identity = self.my_identity_at_factory[(
            glidefactory_classad['CollectorHost'], glidefactory_classad['AuthenticatedIdentity'])]
        key_obj = key_builder.get_key_obj(classad_identity,
                                          glidefactory_classad['PubKeyID'],
                                          glidefactory_classad['PubKeyObj'])

        self.global_key[glidefactory_classad['CollectorHost']] = key_obj

        # Figure out the credentials to advertise and load them
        credentials = self.credential_plugin.get_credentials()
        nr_credentials = len(credentials)
        self.logger.info('Number of credentials found: %i' % nr_credentials)
        for cred in credentials:
            cred.advertize = True
            cred.renew()
            cred.create_if_not_exist()
            cred.loaded_data = []
            for cred_file in (cred.filename, cred.key_fname, cred.pilot_fname):
                self.logger.debug('Loading credential file %s' %
                                  str(cred_file))
                if cred_file:
                    cred_data = cred.get_string(cred_file)
                    if cred_data:
                        cred.loaded_data.append((cred_file, cred_data))
                    else:
                        # We encountered error with this credential
                        # Move onto next credential
                        self.logger.info(
                            'ERROR loading credential file %s, setting advertize to False' % cred_file)
                        cred.advertize = False
                        break

        # Create GlideClientGlobalClassad object
        my_name = '%s.%s' % (self.frontend_name, self.fe_group)
        gcg_classad = classads.GlideClientGlobalClassad(
            glidefactory_classad['Name'], my_name)
        gcg_classad.adParams['CollectorHost'] = glidefactory_classad['CollectorHost']
        gcg_classad.adParams['FrontendName'] = self.frontend_name
        gcg_classad.adParams['GroupName'] = self.fe_group
        gcg_classad.adParams['FrontendHAMode'] = "False"
        gcg_classad.adParams.update(self.get_factory_key_ad_params(key_obj))

        # Classad attributes that need to be encrypted
        classad_attrs_to_encrypt = {
            'NumberOfCredentials': '%s' % nr_credentials,
            'SecurityName': '%s' % self.security_name
        }
        for cred in credentials:
            if cred.advertize:
                for (fname, data) in cred.loaded_data:
                    classad_attrs_to_encrypt[cred.file_id(fname)] = data
                    if hasattr(cred, 'security_class'):
                        # Convert security_class to string for factory
                        # to interpret it correctly
                        classad_attrs_to_encrypt['SecurityClass%s' % cred.file_id(
                            fname)] = str(cred.security_class)

        # Add classad attributes that need to be encrypted
        for attr in classad_attrs_to_encrypt:
            value = str(key_obj.encrypt_hex(classad_attrs_to_encrypt[attr]))
            escaped_value = value.replace('"', '\\"').replace('\n', '\\n')
            ad_attr = '%s%s' % ('GlideinEncParam', attr)
            gcg_classad.adParams[ad_attr] = escaped_value

        return gcg_classad

    def read_fe_config(self):
        """
        Read the frontend configuration information
        """

        # TODO: This check can go away once we completely decouple ourselves
        #       from the glideinwms frontend configuration
        try:
            group_config = self.fe_cfg['group'][self.fe_group]
        except KeyError:
            self.logger.error(
                'Frontend Group %s not configured in frontend.xml' % self.fe_group)
            raise

        # Frontend information
        self.frontend_workdir = self.fe_cfg['frontend']['workdir']
        self.frontend_name = self.fe_cfg['frontend']['frontend_name']
        self.monitoring_web_url = self.fe_cfg['frontend']['monitoring_web_url']
        self.web_url = self.fe_cfg['frontend']['web_url']

        # Group information
        self.workdir = group_config['workdir']
        # This group's curbs and limits
        self.total_max_slots = int(group_config['total_max_glideins'])
        self.total_curb_slots = int(group_config['total_curb_glideins'])
        self.total_max_slots_idle = int(group_config['total_max_vms_idle'])
        self.total_curb_slots_idle = int(group_config['total_curb_vms_idle'])
        # This frontend's curbs and limits
        self.fe_total_max_slots = int(group_config['fe_total_max_glideins'])
        self.fe_total_curb_slots = int(group_config['fe_total_curb_glideins'])
        self.fe_total_max_slots_idle = int(
            group_config['fe_total_max_vms_idle'])
        self.fe_total_curb_slots_idle = int(
            group_config['fe_total_curb_vms_idle'])
        # This frontend's curbs and limits
        self.global_total_max_slots = int(
            group_config['global_total_max_glideins'])
        self.global_total_curb_slots = int(
            group_config['global_total_curb_glideins'])
        self.global_total_max_slots_idle = int(
            group_config['global_total_max_vms_idle'])
        self.global_total_curb_slots_idle = int(
            group_config['global_total_curb_vms_idle'])

        # Consider if we need to always keep some running glideins at entry
        # entry_min_running
        self.entry_min_glideins_running = int(group_config['min_running'])
        # entry_max_running
        self.entry_max_glideins = int(group_config['max_running'])
        # max_idle
        self.entry_max_glideins_idle = int(group_config['max_idle'])
        # max_vms_idle
        self.entry_max_slots_idle = int(group_config['max_vms_idle'])
        # curb_vms_idle
        self.entry_curb_slots_idle = int(group_config['curb_vms_idle'])
        # entry_fraction_running
        self.entry_fraction_glidein_running = float(
            group_config['fraction_running'])

        self.idle_lifetime = int(group_config.get('idle_lifetime', 0))
        self.reserve_idle = int(group_config['reserve_idle'])
        self.security_name = group_config['security_name']

        # TODO: Support different credential selection plugins in future
        # credential selection plugin to use
        # cred_plugin => self.x509_proxy_plugin in gwms frontend
        cred_plugin_name = 'ProxyAll'
        cred_plugin_class = glideinFrontendPlugins.proxy_plugins[cred_plugin_name]
        cred_list = create_credential_list(group_config['proxies'],
                                           group_config)
        self.logger.info(
            'Number of credentials found from the configuration %s' % len(cred_list))
        self.credential_plugin = cred_plugin_class(self.workdir, cred_list)
        self.glidein_config_limits = {}

        # Lookup my identity: key = (factory_collector, factory_auth_id)
        self.my_identity_at_factory = {}
        for col in group_config['factory_collectors']:
            self.my_identity_at_factory[(col[0], col[1])] = col[2]

        self.signature_type = group_config['sign_descript']['signature_type']

        self.descript_fname = group_config['sign_descript']['frontend_descript_fname']
        self.descript_signature = group_config['sign_descript']['frontend_descript_signature']

        self.group_web_url = group_config['web_url']
        self.group_descript_fname = group_config['sign_descript']['group_descript_fname']
        self.group_descript_signature = group_config['sign_descript']['group_descript_signature']

    def match(self, job_types, slot_types, entries):
        """
        Do the counting and perform the match
        """

        # Step 1: count_glidein_slots
        #         Count the slots in various status keyed by the request name

        self.count_entry_slots, self.count_entry_slots_cred = \
            self.count_glidein_slots(slot_types)

        # Step 2: count_running_on
        #         Count the jobs that are running on a given entry
        #         keyed on request name

        self.count_real_jobs, self.count_real_glideins = \
            self.count_real_running(job_types['Running']['dataframe'])

        # Step 3: Count matches based on each job types
        for job_type in job_types:
            (job_types[job_type]['count'],
             job_types[job_type]['prop'],
             job_types[job_type]['hereonly'],
             job_types[job_type]['prop_match_cpu'],
             job_types[job_type]['total']) = self.count_match(job_types, job_type, entries)

    def count_real_running(self, jobs):
        """
        Counts all the running jobs & glideins on an entry

        :return: Tuple with the job counts (used for stats)
                 and glidein counts (used for glidein_max_run)
        Both are dictionaries keyed by glidename (entry)
        """

        out_job_counts = {}
        out_glidein_counts = {}

        # Get the frequency of each running on
        job_running_on_counts = dict(jobs['RunningOn'].value_counts())
        for glideid in self.glideid_list:
            glide_str = '%s@%s' % (glideid[1], glideid[0].split(':')[0])
            out_job_counts[glideid] = job_running_on_counts.get(glide_str, 0)

            # Now figure out count of running glideins based on RemoteHost
            glidein_ids = set()
            df = jobs.query('RunningOn == "%s"' % glide_str)
            unknown_glideins = 0
            for index, row in df.iterrows():
                try:
                    # glidein ID is just glidein_XXXXX_XXXXX@fqdn
                    # RemoteHost has following valid formats
                    #
                    # Static slots
                    # ------------
                    # 1 core: glidein_XXXXX_XXXXX@fqdn
                    # N core: slotN@glidein_XXXXX_XXXXX@fqdn
                    #
                    # Dynamic slots
                    # -------------
                    # N core: slotN_M@glidein_XXXXX_XXXXX@fqdn
                    remote_host = row.get('RemoteHost')
                    token = remote_host.split('@')
                    glidein_id = '%s@%s' % (token[-2], token[-1])
                    glidein_ids.add(glidein_id)
                except Exception:
                    # If RemoteHost is missing or has a different
                    # format just increment unknown glideins
                    # for accounting purposes. Here we assume that
                    # the job is running in a glidein with 1 slot
                    unknown_glideins += 1
            out_glidein_counts[glideid] = len(glidein_ids) + unknown_glideins

        return out_job_counts, out_glidein_counts

    def count_glidein_slots(self, slot_types):
        """
        Given the slots dataframe, count the number of slots in various
        states per entry
        """

        count_entry_slots = {}
        count_entry_slots_cred = {}

        for glideid in self.glideid_list:
            request_name = glideid[1]
            count_entry_slots[request_name] = {}
            count_entry_slots_cred[request_name] = {}
            for cred in self.credential_plugin.cred_list:
                count_entry_slots_cred[request_name][cred.get_id()] = {}

            req_entry, req_name, req_fact = request_name.split('@')

            total_entry_slots = pandas.DataFrame()
            if not slot_types['Total']['dataframe'].empty:
                #self.logger.info('------- CHECK ---------------------------------------')
                # self.logger.info(slot_types['Total']['dataframe'].columns.values)
                # self.logger.info('----------------------------------------------')
                total_entry_slots = slot_types['Total']['dataframe'].query(
                    '(GLIDEIN_Entry_Name == "%s") and (GLIDEIN_Name == "%s") and (GLIDEIN_FACTORY == "%s")'
                    % (req_entry, req_name, req_fact))

            entry_slot_types = {
                'Total': total_entry_slots,
                'Idle': get_idle_slots(total_entry_slots),
                'Running': get_running_slots(total_entry_slots),
                'Failed': get_failed_slots(total_entry_slots),
                'TotalCores': get_nondynamic_slots(total_entry_slots),
                'IdleCores': get_idle_slots(total_entry_slots),
                'RunningCores': get_running_slots(total_entry_slots),
            }

            count_entry_slots[request_name]['Total'] = len(
                entry_slot_types['Total'])
            count_entry_slots[request_name]['Idle'] = len(
                entry_slot_types['Idle'])
            count_entry_slots[request_name]['Running'] = len(
                entry_slot_types['Running'])

            for st in entry_slot_types:
                if st == 'TotalCores':
                    count_entry_slots[request_name][st] = count_total_cores(
                        entry_slot_types[st])
                elif st == 'IdleCores':
                    count_entry_slots[request_name][st] = count_idle_cores(
                        entry_slot_types[st])
                elif st == 'RunningCores':
                    count_entry_slots[request_name][st] = count_running_cores(
                        entry_slot_types[st])
                elif st == 'Running':
                    count_entry_slots[request_name][st] = len(
                        entry_slot_types[st]) - len(get_running_pslots(total_entry_slots))
                else:
                    count_entry_slots[request_name][st] = len(
                        entry_slot_types[st])
                # Further get counts per credentials
                for cred in self.credential_plugin.cred_list:
                    # Initialize all counts to 0 for potential empty frames
                    count_entry_slots_cred[request_name][cred.get_id()][st] = 0
                    entry_slots_cred = pandas.DataFrame()
                    if not entry_slot_types[st].empty:
                        entry_slots_cred = entry_slot_types[st].query(
                            'GLIDEIN_CredentialIdentifier == "%s"' % cred.get_id())

                    if st == 'TotalCores':
                        count_entry_slots_cred[request_name][cred.get_id(
                        )][st] = count_total_cores(entry_slots_cred)
                    elif st == 'IdleCores':
                        count_entry_slots_cred[request_name][cred.get_id(
                        )][st] = count_idle_cores(entry_slots_cred)
                    elif st == 'RunningCores':
                        count_entry_slots_cred[request_name][cred.get_id(
                        )][st] = count_running_cores(entry_slots_cred)
                    elif st == 'Running':
                        count_entry_slots_cred[request_name][cred.get_id()][st] = len(
                            entry_slots_cred) - len(get_running_pslots(entry_slots_cred))
                    else:
                        count_entry_slots_cred[request_name][cred.get_id()][st] = len(
                            entry_slots_cred)

        return (count_entry_slots, count_entry_slots_cred)

    # IDEA: pass the site buckets and use it as match expr. should work

    def count_match(self, job_types, job_type, entries):
        """
        Count the match for which job is running on which entry
        """

        # TODO: This needs to be expanded to use more attrs and not just
        #       RequestCpus. Similar to glideFrontendLib.countMatch()
        # TODO: Need to understand how to incorporate match_expr functionality
        #       using data frames in DE

        direct_match = {}    # Number of direct job matches
        prop_match = {}      #
        hereonly_match = {}  # Jobs that can only run here
        prop_match_cpu = {}  # Total Cpus: prop_match * GLIDEIN_CPUS

        jobs = job_types[job_type]['dataframe']
        if not jobs.empty:
            # Get group of jobs based on request cpus
            job_groups = jobs.groupby('RequestCpus')

            for (req_cpus, group) in job_groups:
                # Group jobs by matching criteria: RequestCpus for now
                # We care about job counts for each group
                job_count = len(group)

                matches = set()
                # TODO: how is this handling AUTO and GLIDEIN_ESTIMATED_CPUS?
                for index, row in entries.query('GLIDEIN_CPUS >= %i' % req_cpus).iterrows():
                    matches.add((row.get('CollectorHost'), row.get('Name')))

                if len(matches) == 0:
                    # These jobs do not match anywhere. Special entry (None, None)
                    direct_match[(None, None)] = direct_match.get(
                        (None, None), 0) + job_count
                    prop_match[(None, None)] = prop_match.get(
                        (None, None), 0) + job_count
                    hereonly_match[(None, None)] = hereonly_match.get(
                        (None, None), 0) + job_count
                    prop_match_cpu[(None, None)] = prop_match_cpu.get(
                        (None, None), 0) + (job_count * req_cpus)
                else:
                    for key in matches:
                        direct_match[key] = direct_match.get(
                            key, 0) + job_count
                        if len(matches) == 1:
                            # These jobs can only run here
                            hereonly_match[key] = hereonly_match.get(
                                key, 0) + job_count
                        else:
                            hereonly_match[key] = hereonly_match.get(key, 0)
                        fraction = math.ceil(float(job_count) / len(matches))
                        prop_match[key] = prop_match.get(key, 0) + fraction
                        this_entry = entries.query('Name =="%s"' % key[1])
                        # glidein_cpus = 1 # default to 1 if not defined
                        for index, row in this_entry.iterrows():
                            glidein_cpus = row.get('GLIDEIN_CPUS', 1)

                        prop_match_cpu[key] = math.ceil(
                            (prop_match_cpu.get(key, 0) + (fraction * req_cpus)) / glidein_cpus)
        total = job_types[job_type]['abs']
        return (direct_match, prop_match, hereonly_match, prop_match_cpu, total)

    def categorize_jobs(self, jobs_df):
        """
        Categorize jobs based on different job status and voms/proxy requirement
        """
        # TODO: Identify the list of schedds that should not be considered when
        #       requesting glideins for idle jobs. Schedds with one of the
        #       criteria
        #       1. Running jobs (TotalRunningJobs + TotalSchedulerJobsRunning)
        #          is greater than 95% of max number of jobs (MaxJobsRunning)
        #       2. Transfer queue (TransferQueueNumUploading) is >  95%
        #          of max allowed transfers (TransferQueueMaxUploading)
        #       3. CurbMatchmaking in schedd classad is true
        # Need to adjust the jobs_df below once we do that

        if jobs_df.empty:
            idle_all = jobs_df
            idle = jobs_df
            old_idle = jobs_df
            idle_3600 = jobs_df
            voms_idle = jobs_df
            proxy_idle = jobs_df
            running = jobs_df
        else:
            idle_all = jobs_df.query('JobStatus == 1')
            idle = jobs_df.query('JobStatus == 1')
            old_idle = jobs_df.query(
                'JobStatus == 1 and (ServerTime - EnteredCurrentStatus) > 600')
            idle_3600 = jobs_df.query(
                'JobStatus == 1 and (ServerTime - EnteredCurrentStatus) > 3600')
            voms_idle = jobs_df.query(
                'JobStatus == 1 and (x509UserProxyFirstFQAN !="")')
            proxy_idle = jobs_df.query(
                'JobStatus == 1 and (x509userproxy !="")')
            running = jobs_df.query('JobStatus == 2')

        job_types = {
            # 'All': jobs.df,
            'IdleAll': {'dataframe': idle_all, 'abs': len(idle_all)},
            'Idle': {'dataframe': idle, 'abs': len(idle)},
            'OldIdle': {'dataframe': old_idle, 'abs': len(old_idle)},
            'Idle_3600': {'dataframe': idle_3600, 'abs': len(idle_3600)},
            'VomsIdle': {'dataframe': voms_idle, 'abs': len(voms_idle)},
            'ProxyIdle': {'dataframe': proxy_idle, 'abs': len(proxy_idle)},
            'Running': {'dataframe': running, 'abs': len(running)},
        }
        return job_types

    def categorize_slots(self, slots_df):
        """
        Categorize slots and cores based on their status
        """
        # static slots: PartitionableSlot != True
        # pslots not partitioned: TotalSlots == 1
        # pslots with enough resources: Cpus > 0 and Memory > 2500
        # static running slots + dynamic slots + pslots with dynamic slots
        idle_slots = get_idle_slots(slots_df)
        running_slots = get_running_slots(slots_df)
        running_pslots = get_running_pslots(slots_df)
        failed_slots = get_failed_slots(slots_df)
        nondynamic_slots = get_nondynamic_slots(slots_df)

        slot_types = {
            'Total': {'dataframe': slots_df, 'abs': len(slots_df)},
            'Idle': {'dataframe': idle_slots, 'abs': len(idle_slots)},
            'Running': {'dataframe': running_slots, 'abs': (len(running_slots) - len(running_pslots))},
            'Failed': {'dataframe': failed_slots, 'abs': len(failed_slots)},
            'TotalCores': {'dataframe': nondynamic_slots, 'abs': count_total_cores(nondynamic_slots)},
            'IdleCores': {'dataframe': idle_slots, 'abs': count_idle_cores(idle_slots)},
            'RunningCores': {'dataframe': running_slots, 'abs': count_running_cores(running_slots)}
        }

        return slot_types

    def create_glideid_list(self, entries):
        """
        Create list of glideids
        """
        glideid_list = set()
        # TODO: Can we use dataframes apis to do this efficiently?
        for index, row in entries.iterrows():
            glideid_list.add((row['CollectorHost'], row['Name']))
        return glideid_list

    def identify_limits_triggered(self, count_status,
                                  total_glideins, total_idle_glideins,
                                  fe_total_glideins, fe_total_idle_glideins,
                                  global_total_glideins,
                                  global_total_idle_glideins,
                                  limits_triggered):

        # Identify the limits triggered for advertising in glideresource
        if count_status['Total'] >= self.entry_max_glideins:  # max_running
            limits_triggered['TotalGlideinsPerEntry'] = 'count=%i, limit=%i' % (count_status['Total'],
                                                                                self.entry_max_glideins)
        if count_status['Idle'] >= self.entry_max_slots_idle:  # max_vms_idle
            limits_triggered['IdleGlideinsPerEntry'] = 'count=%i, limit=%i' % (count_status['Idle'],
                                                                               self.entry_max_slots_idle)
        if total_glideins >= self.total_max_slots:   # was total_max_glideins
            limits_triggered['TotalGlideinsPerGroup'] = 'count=%i, limit=%i' % (total_glideins,
                                                                                self.total_max_slots)
        if total_idle_glideins >= self.total_max_slots_idle:  # was total_max_vms_idle
            limits_triggered['IdleGlideinsPerGroup'] = 'count=%i, limit=%i' % (total_idle_glideins,
                                                                               self.total_max_slots_idle)
        if fe_total_glideins >= self.fe_total_max_slots:  # fe_total_max_glideins
            limits_triggered['TotalGlideinsPerFrontend'] = 'count=%i, limit=%i' % (fe_total_glideins,
                                                                                   self.fe_total_max_slots)
        if fe_total_idle_glideins >= self.fe_total_max_slots_idle:  # fe_total_max_vms_idle
            limits_triggered['IdleGlideinsPerFrontend'] = 'count=%i, limit=%i' % (fe_total_idle_glideins,
                                                                                  self.fe_total_max_slots_idle)
        if global_total_glideins >= self.global_total_max_slots:  # global_total_max_glideins
            limits_triggered['TotalGlideinsGlobal'] = 'count=%i, limit=%i' % (global_total_glideins,
                                                                              self.global_total_max_slots)
        if global_total_idle_glideins >= self.global_total_max_slots_idle:  # global_total_max_vms_idle
            limits_triggered['IdleGlideinsGlobal'] = 'count=%i, limit=%i' % (global_total_idle_glideins,
                                                                             self.global_total_max_slots_idle)

    def compute_glidein_min_idle(self, count_status, total_glideins,
                                 total_idle_glideins, fe_total_glideins,
                                 fe_total_idle_glideins,
                                 global_total_glideins,
                                 global_total_idle_glideins,
                                 effective_idle, effective_oldidle,
                                 limits_triggered):
        """
        Compute min idle glideins to request for this entry after considering
        all the relevant limits and curbs.
        Identify the limits and curbs triggered for advertizing the info
        glideresource classad
        """
        if ((count_status['Total'] >= self.entry_max_glideins)
                or (count_status['Idle'] >= self.entry_max_slots_idle)
                or (total_glideins >= self.total_max_slots)
                or (total_idle_glideins >= self.total_max_slots_idle)
                or (fe_total_glideins >= self.fe_total_max_slots)
                or (fe_total_idle_glideins >= self.fe_total_max_slots_idle)
                or (global_total_glideins >= self.global_total_max_slots)
                or (global_total_idle_glideins >= self.global_total_max_slots_idle)):

            # Do not request more glideins under following conditions:
            # 1. Have all the running jobs I wanted
            # 2. Have enough idle vms/slots
            # 3. Reached the system-wide limit
            glidein_min_idle = 0

            limits_triggered['ZeroLimitHit'] = 'glidein_min_idle set to 0'

            # Modifies limits_triggered dict
            self.identify_limits_triggered(
                count_status, total_glideins, total_idle_glideins,
                fe_total_glideins, fe_total_idle_glideins,
                global_total_glideins, global_total_idle_glideins,
                limits_triggered)

        elif (effective_idle > 0):
            # don't go over the system-wide max
            # not perfect, given the number of entries, but better than nothing
            glidein_min_idle = min(
                effective_idle,
                # TODO: check if this is correct glidein v/s slot subtraction
                self.entry_max_glideins - count_status['Total'],
                self.total_max_slots - total_glideins,
                self.total_max_slots_idle - total_idle_glideins,
                self.fe_total_max_slots - fe_total_glideins,
                self.fe_total_max_slots_idle - fe_total_idle_glideins,
                self.global_total_max_slots - global_total_glideins,
                self.global_total_max_slots_idle - global_total_idle_glideins)

            if glidein_min_idle < effective_idle:
                limits_triggered['MaxLimitHit'] = 'was=%i, min=%i' % (
                    effective_idle, glidein_min_idle)

            # since it takes a few cycles to stabilize, ask for only one third
            glidein_min_idle = glidein_min_idle / 3
            # do not reserve any more than the number of old idles
            # for reserve (/3)
            glidein_idle_reserve = min(
                effective_oldidle / 3, self.reserve_idle)

            glidein_min_idle += glidein_idle_reserve
            glidein_min_idle = min(
                glidein_min_idle, self.entry_max_glideins_idle)

            if count_status['Idle'] >= self.entry_curb_slots_idle:
                glidein_min_idle /= 2  # above first treshold, reduce
                limits_triggered['CurbIdleGlideinsPerEntry'] = 'count=%i, curb=%i' % (
                    count_status['Idle'], self.entry_curb_slots_idle)
            if total_glideins >= self.total_curb_slots:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbTotalGlideinsPerGroup'] = 'count=%i, curb=%i' % (
                    total_glideins, self.total_curb_slots)
            if total_idle_glideins >= self.total_curb_slots_idle:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbIdleGlideinsPerGroup'] = 'count=%i, curb=%i' % (
                    total_idle_glideins, self.total_curb_slots_idle)
            if fe_total_glideins >= self.fe_total_curb_slots:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbTotalGlideinsPerFrontend'] = 'count=%i, curb=%i' % (
                    fe_total_glideins, self.fe_total_curb_slots)
            if fe_total_idle_glideins >= self.fe_total_curb_slots_idle:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbIdleGlideinsPerFrontend'] = 'count=%i, curb=%i' % (
                    fe_total_idle_glideins, self.fe_total_curb_slots_idle)
            if global_total_glideins >= self.global_total_curb_slots:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbTotalGlideinsGlobal'] = 'count=%i, curb=%i' % (
                    global_total_glideins, self.global_total_curb_slots)
            if global_total_idle_glideins >= self.global_total_curb_slots_idle:
                glidein_min_idle /= 2  # above global treshold, reduce further
                limits_triggered['CurbIdleGlideinsGlobal'] = 'count=%i, curb=%i' % (
                    global_total_idle_glideins, self.global_total_curb_slots_idle)

            if glidein_min_idle < 1:
                glidein_min_idle = 1
        else:
            # no idle, make sure the glideins know it
            limits_triggered['NoEffectiveIdle'] = 'no glidein is needed'
            glidein_min_idle = 0

        return int(glidein_min_idle)

    def compute_glidein_max_running(self, prop_jobs, real_slots, idle_slots):
        """
        Compute max number of running glideins for this entry

        @param prop_jobs: Proportional idle multicore jobs for this entry
        @type prop_jobs: dict

        @param real: Number of jobs running at given glideid
        @type real: int

        @param idle_glideins: Number of idle startds at this entry
        @type idle_glideins: int
        """

        max_running = 0
        if (prop_jobs['Idle'] + real_slots) > 0:
            if prop_jobs['Idle'] > 0:
                # We have idle jobs in the queue. Consider idle startds
                # at this entry when computing max_run. This makes the
                # requests conservative when short running jobs come in
                # frequently but in smaller bursts.
                # NOTE: We do not consider idle cores as fragmentation can
                #       impact us negatively
                max_running = int(
                    (max(prop_jobs['Idle'] - idle_slots, 0) + real_slots) * self.entry_fraction_glidein_running + 1)
            else:
                # No reason for a delta when we don't need more than we have
                max_running = int(real_slots)

        return max_running

    def create_factory_pubkeyobj(self, factory_globals):
        key_objs = []
        for index, row in factory_globals.iterrows():
            try:
                # NOTE: Newline is escaped before storing into the dataframe
                #       Un-escape it to make the pub key string usable
                pub_key = row.get('PubKeyValue').replace('\\n', '\n')
                key_obj = pubCrypto.PubRSAKey(key_str=pub_key)
            except Exception:
                # if no valid key
                # if key needed, will handle the error later on
                raise
            key_objs.append(key_obj)
        return key_objs


###############################################################################
# GlideFrontendElement class using Figure of Merit
###############################################################################


class GlideFrontendElementFOM(GlideFrontendElement):
    """
    Class that implements the functionality of a GlideinWMS Frontend Element
    to make glidein requests based on Figure of Merit
    """

    def __init__(self, fe_group, acct_group, fe_cfg):
        super(GlideFrontendElementFOM, self).__init__(fe_group,
                                                      acct_group, fe_cfg)
        # Sum of all the glidein requests from different job filters
        self.total_glidein_requests = {}

    def generate_glidein_requests(self, jobs_df, slots_df,
                                  entries, factory_globals,
                                  job_filter='ClusterId > 0',
                                  fom_entries=None):
        """
        Given the dataframes for jobs, job_clusters, factory entries,cw
        slots in pool and factory global classads, generate glidein requests.
        Returns a dict of dataframes for glideclientglobal and glideclient
        classads

        jobs_df: Jobs dataframe
                 columns = classad attributes
        slots_df: Slots/startd classad dataframe
                 columns = classad attributes
        entries: entry/glidefactory classad dataframe
                 columns = classad attributes
        factory_globals: dataframe of glidefactory_global classads
        job_filter: job query expression (not required since this is in buckets)
        fom_entries: entries ordered by figure of merit
        """

        self.fom_entries = fom_entries

        return self.generate_glidein_requests_one(
            jobs_df, slots_df, entries,
            factory_globals, job_filter=job_filter)

    # def generate_glidein_requests_one(self, jobs_df, job_clusters_df,

    def generate_glidein_requests_one(self, jobs_df, slots_df,
                                      entries, factory_globals,
                                      job_filter='ClusterId > 0'):
        """
        Generate glidein request using fom for a single job_filter

        jobs_df: Jobs dataframe
                 columns = classad attributes
        job_clusters_df: Job clusters dataframe
                 columns = job cluster criteria, job cluster total,
                           list of site bucket matches
        slots_df: Slots/startd classad dataframe
                 columns = classad attributes
        entries: entry/glidefactory classad dataframe
                 columns = classad attributes
        factory_globals: dataframe of glidefactory_global classads
                 columns = classad attributes
        job_filter: job query expression (query expression being processed now)
        fom_entries: entries ordered by figure of merit
        """
        ########################################################################
        # STEP 1: Get info from frontend configuration
        # STEP 2: Get credentials to be used for the submission
        ########################################################################

        self.file_id_cache = CredentialCache()
        # Used to map key_obj. Key = (factory_collector)
        self.global_key = {}

        self.read_fe_config()

        # TODO: Figure out how to deal with this info in new scheme
        # Create the params descript object. It stores info about the
        # frontend params/const info
        self.params_descript = glideinFrontendConfig.ParamsDescript(
            self.frontend_workdir, self.fe_group)

        ########################################################################
        # STEP 3: Get glidefactoryglobal and glideentry classads
        ########################################################################

        factory_globals['PubKeyObj'] = self.create_factory_pubkeyobj(
            factory_globals)
        self.glideid_list = self.create_glideid_list(entries)

        ########################################################################
        # STEP 4: Get job and slot classads
        #         Categorize jobs and slots based on their respective status
        ########################################################################

        if not jobs_df.empty:
            # Apply filter to jobs df only if it is not empty
            # This will give jobs equivalent to job_query_expr
            jobs_df = jobs_df.query(job_filter)
        # Categorize jobs with different status criteria
        job_types = self.categorize_jobs(jobs_df)

        # Categorize HTCondor slots for this group based on status criteria
        group_slots_df = fe_slots_df = pandas.DataFrame()
        if 'GLIDECLIENT_NAME' in slots_df:
            non_na_slots_df = slots_df.dropna(subset=['GLIDECLIENT_NAME'])
            group_slots_query_str = 'GLIDECLIENT_NAME=="%s.%s"' % (
                self.frontend_name, self.fe_group)
            fe_slots_query_str = 'GLIDECLIENT_NAME.str.startswith("%s.")' % self.frontend_name
            self.logger.debug(
                'Finding group slots matching condition: %s' % group_slots_query_str)
            self.logger.debug(
                'Finding fe slots matching condition: %s' % fe_slots_query_str)
            group_slots_df = non_na_slots_df.query(group_slots_query_str)
            fe_slots_df = non_na_slots_df.query(fe_slots_query_str)
        else:
            self.logger.info('No slots found with attribute GLIDECLIENT_NAME')
        slot_types = self.categorize_slots(group_slots_df)

        # Find idle and total slot counts for frontend and global
        fe_slots_count = count_slots_by_state(fe_slots_df)
        global_slots_count = count_slots_by_state(slots_df)

        self.logger.info('Jobs found total %i idle %i (good %i, old(10min %s, 60min %i), grid %i, voms %i) running %i'
                         % (len(jobs_df),
                            job_types['IdleAll']['abs'],
                            job_types['Idle']['abs'],
                            job_types['OldIdle']['abs'],
                            job_types['Idle_3600']['abs'],
                            job_types['ProxyIdle']['abs'],
                            job_types['VomsIdle']['abs'],
                            job_types['Running']['abs'])
                         )

        # TODO: appendRealRunning -> For every job in schedd
        #       add classad attr RunningOn based on job status
        #       Run = GLIDEIN_Entry_Name@GLIDEIN_Name@GLIDEIN_Factory@fact_pool
        #       Idle = UNKNOWN
        # Find out best way to do this in pandas
        # This is useful to figure out which jobs are running on which glideins
        # It should also be possible to achieve this through config
        # SYSTEM_JOB_MACHINE_ATTRS. Only problem with
        # that approach is, we may not be able to enforce it

        total_slots = slot_types['Total']['abs']
        total_running_slots = slot_types['Running']['abs']
        total_idle_slots = slot_types['Idle']['abs']
        fe_total_slots = fe_slots_count['Total']
        fe_total_idle_slots = fe_slots_count['Idle']
        fe_total_running_slots = fe_slots_count['Running']
        global_total_slots = global_slots_count['Total']
        global_total_idle_slots = global_slots_count['Idle']
        global_total_running_slots = global_slots_count['Running']

        self.logger.info('Group slots found total %i (limit %i curb %i) idle %i (limit %i curb %i) running %i'
                         % (total_slots,
                            self.total_max_slots,
                            self.total_curb_slots,
                            total_idle_slots,
                            self.total_max_slots_idle,
                            self.total_curb_slots_idle,
                            total_running_slots)
                         )
        self.logger.info('Frontend slots found total %i (limit %i curb %i) idle %i (limit %i curb %i) running %i'
                         % (fe_total_slots,
                            self.fe_total_max_slots,
                            self.fe_total_curb_slots,
                            fe_total_idle_slots,
                            self.fe_total_max_slots_idle,
                            self.fe_total_curb_slots_idle,
                            fe_total_running_slots)
                         )
        self.logger.info('Overall slots found total %i (limit %i curb %i) idle %i (limit %i curb %i) running %i'
                         % (global_total_slots,
                            self.global_total_max_slots,
                            self.global_total_curb_slots,
                            global_total_idle_slots,
                            self.global_total_max_slots_idle,
                            self.global_total_curb_slots_idle,
                            global_total_running_slots)
                         )

        # Add entry info to each running slot's classad
        append_running_on(job_types['Running']['dataframe'],
                          slot_types['Running']['dataframe'])

        ########################################################################
        # STEP 5: Match the jobs to the entries
        #         This only counts matches but does not request
        ########################################################################
        self.match(job_types, slot_types, entries)

        ########################################################################
        # STEP 6: Create glideclientglobal classads
        ########################################################################

        key_builder = glideinFrontendInterface.Key4AdvertizeBuilder()
        # List of classad objects
        self.gc_classads = []
        self.gcg_classads = []

        # Create the glideclientglobal classads first to load credentials.
        # This loads the credentials. If loading the credential fails, that
        # credential is ignored while creating a glideclient classad
        for index, row in factory_globals.iterrows():
            self.gcg_classads.append(
                self.create_glideclientglobal_classads(row, key_builder))

        ########################################################################
        # STEP 7: Apply any limits and thresholds to come up with final number
        ########################################################################

        # List of glideids that have idle jobs
        glideids_with_idle_jobs = job_types['Idle']['count'].keys()

        # For faster lookup
        self.processed_glideid_strs = []

        log_factory_header()
        total_up_stats_arr = init_factory_stats_arr()
        total_down_stats_arr = init_factory_stats_arr()

        for glideid in glideids_with_idle_jobs:
            if glideid == (None, None):
                # Ignore the unmatched entries
                continue

            # Find my identity at factory from the config for this glideid
            factory_pool_node = glideid[0]
            request_name = glideid[1]
            my_identity = None
            fact_cols = self.fe_cfg['group'][self.fe_group]['factory_collectors']
            for fact_col in fact_cols:
                if fact_col[0] == factory_pool_node:
                    my_identity = fact_col[2]

            glideid_str = "%s@%s" % (request_name, factory_pool_node)
            self.processed_glideid_strs.append(glideid_str)
            entry_info = entries.query(
                'Name == "%s" and CollectorHost == "%s"' % (request_name, factory_pool_node))

            # Some short hand variables for easy reference
            glidein_in_downtime = entry_info.get(
                'GLIDEIN_In_Downtime').tolist()[0]
            # numpy bool is not python bool. Convert to string and compare
            entry_in_downtime = ('%s' % glidein_in_downtime).upper() == 'TRUE'
            count_jobs = {}    # Count of jobs with straight matches
            prop_jobs = {}     # proportional subset for this entry
            # proportional subset of jobs for this entry scaled also for
            # multicore (requested cores/available cores)
            prop_mc_jobs = {}
            hereonly_jobs = {}  # can only run on this site
            for status in job_types:
                count_jobs[status] = job_types[status]['count'].get(glideid, 0)
                prop_jobs[status] = job_types[status]['prop'].get(glideid, 0)
                prop_mc_jobs[status] = job_types[status]['prop_match_cpu'].get(
                    glideid, 0)
                hereonly_jobs[status] = job_types[status]['hereonly'].get(
                    glideid, 0)

            count_slots = self.count_entry_slots[request_name]
            count_slots_per_cred = self.count_entry_slots_cred[request_name]

            # TODO: Figure out a way to introduce glexec
            #       Assume false for now
            use_glexec = 'NEVER'
            if use_glexec != 'NEVER':
                if entry_info.get('GLIDEIN_REQUIRE_VOMS') == 'True':
                    prop_jobs['Idle'] = prop_jobs['VomsIdle']
                    self.logger.info(
                        'Voms proxy required, limiting idle glideins based on jobs: %i' % prop_jobs['Idle'])
                elif entry_info.get('GLIDEIN_REQUIRE_GLEXEC_USE') == 'True':
                    prop_jobs['Idle'] = prop_jobs['ProxyIdle']
                    self.logger.info(
                        'Proxy required (GLEXEC), limiting idle glideins based on jobs: %i' % prop_jobs['Idle'])

            # MMDB should be debug
            self.logger.info("Request %s: prop jobs %s(mc %s, min %s), available slots %s " % (
                request_name, prop_jobs['Idle'], prop_mc_jobs['Idle'], self.entry_min_glideins_running,
                count_slots['Idle'],))

            # effective idle is how much more we need
            # if there are idle slots, subtract them, they should match soon
            effective_idle = max(prop_jobs['Idle'] - count_slots['Idle'], 0)

            # Adjust the number of idle jobs in case
            # the minimum running parameter is set
            if prop_mc_jobs['Idle'] < self.entry_min_glideins_running:
                self.logger.info("Entry %s: Adjusting idle cores to %s since the 'min' attribute "
                                 "of 'running_glideins_per_entry' is set"
                                 % (request_name, self.entry_min_glideins_running))
                prop_mc_jobs['Idle'] = self.entry_min_glideins_running

            # Compute min glideins required based on multicore jobs
            effective_idle_mc = max(
                prop_mc_jobs['Idle'] - count_slots['Idle'], 0)
            effective_oldidle_mc = max(
                prop_mc_jobs['OldIdle'] - count_slots['Idle'], 0)

            limits_triggered = {}
            # Compute minimum idle glideins required for this request_name
            # TODO: Understand what to put for fe_total_slots,
            #       fe_total_idle_slots, lobal_total_slots,
            #       global_total_idle_slots,
            glidein_min_idle = self.compute_glidein_min_idle(
                count_slots, total_slots, total_idle_slots,
                fe_total_slots, fe_total_idle_slots,
                global_total_slots, global_total_idle_slots,
                effective_idle_mc, effective_oldidle_mc,
                limits_triggered)
            # Compute maximum running glideins required for this request_name
            glidein_max_run = self.compute_glidein_max_running(
                prop_mc_jobs,
                self.count_real_glideins[glideid],
                count_slots['Idle'])

            # MMDB should be debug
            self.logger.info("Limits triggered: %s " % (
                ', '.join(["%s: %s" % (k, v) for k, v in limits_triggered.items()])))

            # TODO: Figure out what to do with monitoring
            # Frontend groups logs stats here creating web monitoring xml files
            # adding data to rrds etc.

            this_stats_arr = (prop_jobs['Idle'], count_jobs['Idle'],
                              effective_idle, prop_jobs['OldIdle'],
                              hereonly_jobs['Idle'], count_jobs['Running'],
                              self.count_real_jobs[glideid],
                              self.entry_max_glideins,
                              count_slots['Total'],
                              count_slots['Idle'],
                              count_slots['Running'],
                              count_slots['Failed'],
                              count_slots['TotalCores'],
                              count_slots['IdleCores'],
                              count_slots['RunningCores'],
                              glidein_min_idle, glidein_max_run)

            # Extract FOM for this entry
            ent_list = entry_info.get('EntryName', []).tolist()
            ent_name = ent_list[0] if ent_list else "-"
            fom_info = self.fom_entries.query('EntryName=="%s"' % ent_name)
            try:
                fom = fom_info.get('FOM').tolist()[0]
            except IndexError:
                fom = '-'
                self.logger.error(
                    'FOM info not found for following entry possibly because of '
                    'inaccurate/missing info in the instance performance file')
                self.logger.error(entry_info)
                self.logger.error(fom_info)

            if entry_in_downtime:
                total_down_stats_arr = log_and_sum_factory_line(
                    glideid_str, entry_in_downtime,
                    this_stats_arr, total_down_stats_arr,
                    fom=fom)
            else:
                total_up_stats_arr = log_and_sum_factory_line(
                    glideid_str, entry_in_downtime,
                    this_stats_arr, total_up_stats_arr,
                    fom=fom)

            # Get the parameters from the frontend config
            glidein_params = copy.deepcopy(self.params_descript.const_data)
            for k in self.params_descript.expr_data:
                kexpr = self.params_descript.expr_objs[k]
                glidein_params[k] = eval(kexpr)
            # Add GLIDECLIENT_ReqNode to monitor orphaned glideins
            glidein_params['GLIDECLIENT_ReqNode'] = factory_pool_node

            glidein_monitors = {k: count_jobs[k] for k in count_jobs}
            glidein_monitors['RunningHere'] = self.count_real_jobs[glideid]
            for t in count_slots:
                glidein_monitors['Glideins%s' % t] = count_slots[t]

            # Number of credentials that have running and glideins.
            # This will be used to scale down the glidein_monitors[Running]
            # when there are multiple credentials per group.
            # This is efficient way of achieving the end result. Note that
            # Credential specific stats are not presented anywhere except the
            # classad. Monitoring info in frontend and factory shows
            # aggregated info considering all the credentials
            glidein_monitors_per_cred = {}
            creds_with_running = 0
            for cred in self.credential_plugin.cred_list:
                glidein_monitors_per_cred[cred.get_id()] = {
                    'Glideins%s' % t: count_slots_per_cred[cred.get_id()][t] for t in count_slots}
                glidein_monitors_per_cred[cred.get_id()]['ScaledRunning'] = 0
                if glidein_monitors_per_cred[cred.get_id()]['GlideinsRunning']:
                    creds_with_running += 1

            if creds_with_running:
                # Counter to handle rounding errors
                scaled = 0
                tr = glidein_monitors['Running']
                for cred in self.credential_plugin.cred_list:
                    cred_monitor = glidein_monitors_per_cred[cred.get_id()]
                    if cred_monitor['GlideinsRunning']:
                        # This cred has running, scale them down
                        if (creds_with_running - scaled) == 1:
                            cred_monitor['ScaledRunning'] = tr - \
                                (tr // creds_with_running) * scaled
                            scaled += 1
                            break
                        else:
                            cred_monitor['ScaledRunning'] = tr // creds_with_running
                            scaled += 1

            key_obj = None
            for index, row in factory_globals.iterrows():
                pubkeyid = row.get('PubKeyID', None)
                pubkeyobj = row.get('PubKeyObj', None)
                if glideid[1].endswith(row['Name']) and pubkeyid and pubkeyobj:
                    key_obj = key_builder.get_key_obj(
                        my_identity, pubkeyid, pubkeyobj)
                    break

            # TODO: These two come from glidefactory classad rows how to get it?
            trust_domain = entry_info.get('GLIDEIN_TrustDomain',
                                          ['Grid']).tolist()[0]
            auth_method = entry_info.get(
                'GLIDEIN_SupportedAuthenticationMethod',
                ['grid_proxy']).tolist()[0]

            # Only advertize if there is a valid key for encryption
            if key_obj is not None:
                gc_classad = self.create_glideclient_classads(
                    factory_pool_node, request_name, request_name,
                    glidein_min_idle, glidein_max_run, self.idle_lifetime,
                    glidein_params=glidein_params,
                    glidein_monitors=glidein_monitors,
                    glidein_monitors_per_cred=glidein_monitors_per_cred,
                    key_obj=key_obj, glidein_params_to_encrypt=None,
                    security_name=self.security_name, remove_excess_str=None,
                    trust_domain=trust_domain, auth_method=auth_method)
                self.gc_classads.extend(gc_classad)
            else:
                self.logger.warning("Cannot advertise requests for %s because no factory %s key was found" % (
                    request_name, factory_pool_node))

        # TODO: Enable following logging in future
        """
        total_down_stats_arr = self.count_factory_entries_without_classads(total_down_stats_arr)

        self.log_and_print_total_stats(total_up_stats_arr, total_down_stats_arr)
        self.log_and_print_unmatched(total_down_stats_arr)
        """

        # TODO: Enable following renewing and loading credentials
        """

        pids=[]
        # Advertise glideclient and glideclient global classads
        ad_file_id_cache=glideinFrontendInterface.CredentialCache()
        advertizer.renew_and_load_credentials()
        """

        gcg_df = pandas.DataFrame([ad.adParams for ad in self.gcg_classads])
        gc_df = pandas.DataFrame([ad.adParams for ad in self.gc_classads])
        return {
            'glideclientglobal_manifests': gcg_df,
            'glideclient_manifests': gc_df
        }

    def count_match(self, job_types, job_type, entries):
        return self.count_match_fom_bff(job_types, job_type, entries)

    def count_match_fom_bff(self, job_types, job_type, entries):
        """
        Count the matches. This will use FOM for calculations to
        count direct matches and proportionate matches and do breadth first fill
        Requests are made in proportion to the fom values

        Algorithm:
        1. Lower FOM is better, so inverse the FOM values ie calculate 1/FOM
        2. Find out what percentage each 1/FOM value is wrt others
        3. Request resources based on the percentage of the site's 1/FOM
        NOTE: This expects that FOM values are linear for good results
        """

        # TODO: This needs to be expanded to use more attrs and not just
        #       RequestCpus. Similar to glideFrontendLib.countMatch()

        direct_match = {}    # Number of direct job matches
        prop_match = {}      #
        hereonly_match = {}  # Jobs that can only run here
        prop_match_cpu = {}  # Total Cpus: prop_match * GLIDEIN_CPUS

        dbg_info = ['count_match_fom_bff']

        jobs = job_types[job_type]['dataframe']
        if not jobs.empty:
            # Get group of jobs based on request cpus
            job_groups = jobs.groupby('RequestCpus')

            dbg_info.append('%i job groups' % len(job_groups))

            for (req_cpus, job_group) in job_groups:
                # Group jobs by matching criteria: RequestCpus for now
                # We only care about job counts for each group
                job_count = len(job_group)

                matches = set()
                # TODO: only entries w/ explicit numeric fixed GLIDEIN_CPUS are considered. Handle auto here
                entries_with_cpus = entries.query(
                    'GLIDEIN_CPUS>=%i' % req_cpus)

                for index, row in entries_with_cpus.iterrows():
                    matches.add((row.get('CollectorHost'), row.get('Name')))

                if len(matches) == 0:
                    # These jobs do not match anywhere
                    # Represented by a special entry (None, None)
                    direct_match[(None, None)] = direct_match.get(
                        (None, None), 0) + job_count
                    prop_match[(None, None)] = prop_match.get(
                        (None, None), 0) + job_count
                    hereonly_match[(None, None)] = hereonly_match.get(
                        (None, None), 0) + job_count
                    prop_match_cpu[(None, None)] = prop_match_cpu.get(
                        (None, None), 0) + (job_count * req_cpus)
                    dbg_info.append(
                        '%i jobs requesting %i cpus not matching entries' % (job_count, req_cpus))
                else:
                    if len(matches) == 1:
                        # These jobs can only run here
                        key = next(iter(matches))
                        direct_match[key] = direct_match.get(
                            key, 0) + job_count
                        prop_match[key] = prop_match.get(key, 0) + job_count
                        this_entry = entries.query('Name=="%s"' % key[1])
                        # Default glidein_cpus to 1 if not defined
                        glidein_cpus = this_entry.get('GLIDEIN_CPUS', 1)
                        prop_match_cpu[key] = math.ceil(
                            (prop_match_cpu.get(key, 0) + float(req_cpus * job_count)) / glidein_cpus)
                        # Append FOM for all matches that are not in downtime
                        fom_matches = self.matches_with_fom(
                            matches, entries_with_cpus)
                        dbg_info.append('%i jobs requesting %i cpus matching 1 entry '
                                        '(fom %i) w/ %i cpus: (<%s>, <%s>, <%s, %s>) %s, %s'
                                        % (job_count,
                                           req_cpus,
                                           len(fom_matches),
                                           glidein_cpus,
                                           prop_match_cpu.get(key, 0),
                                           float(req_cpus) / glidein_cpus,
                                           type(req_cpus),
                                           type(glidein_cpus),
                                           prop_match_cpu[key], key)
                                        )
                    else:
                        # Append FOM for all matches that are not in downtime
                        fom_matches = self.matches_with_fom(
                            matches, entries_with_cpus)
                        # Get entries not in downtime and FOM not INFINITY
                        fom_matches_up = fom_matches.query(
                            '(GLIDEIN_In_Downtime!=True) and (FOM != %f)' % sys.float_info.max)
                        # Compute 1/FOM for each match
                        inv_fom_series = fom_matches_up['FOM'].apply(
                            compute_nth)
                        inv_fom_total = inv_fom_series.sum()
                        # Calculate requests based on % value of 1/FOM
                        fom_reqs = inv_fom_series.apply(
                            compute_weighted_share, args=(inv_fom_total, job_count))
                        fom_matches_up['ResourceRequests'] = fom_reqs
                        dbg_info.append('%i jobs requesting %i cpus matching %i entries (fom_up: %i):  ' %
                                        (job_count, req_cpus, len(matches), len(fom_matches_up)))

                        for index, row in fom_matches_up.iterrows():
                            key = (row.get('CollectorHost'), row.get('Name'))
                            direct_match[key] = direct_match.get(
                                key, 0) + job_count
                            fraction = row.get('ResourceRequests', 0)
                            prop_match[key] = prop_match.get(key, 0) + fraction
                            glidein_cpus = row.get('GLIDEIN_CPUS', 1)
                            prop_match_cpu[key] = math.ceil(
                                (prop_match_cpu.get(key, 0) + (fraction * req_cpus)) / glidein_cpus)
                            hereonly_match[key] = hereonly_match.get(key, 0)
                            dbg_info.append('  entry i %i: (%s, %s, fr: %s) %s, %s ' %
                                            (len(matches), prop_match_cpu.get(key, 0),
                                             (fraction * req_cpus) / glidein_cpus, fraction, prop_match_cpu[key], key))

                    # Add stats for all entries in downtime or FOM == INFINITY
                    fom_matches_down = entries_with_cpus.query(
                        'GLIDEIN_In_Downtime==True')
                    fom_matches_inf = fom_matches.query(
                        'FOM==%f' % sys.float_info.max)
                    for rejected_matches in (fom_matches_down, fom_matches_inf):
                        for index, row in rejected_matches.iterrows():
                            key = (row['CollectorHost'], row['Name'])
                            direct_match[key] = direct_match.get(key, 0)
                            hereonly_match[key] = hereonly_match.get(key, 0)
                            prop_match[key] = prop_match.get(key, 0)

        total = job_types[job_type]['abs']
        # TODO: MMDB should be debug
        # logger.info('\n'.join(dbg_info))

        return (direct_match, prop_match, hereonly_match, prop_match_cpu, total)

    def count_match_fom_dff(self, job_types, job_type, entries):
        """
        Count the matches. This will use FOM for calculations to
        count direct matches and proportionate matches and do depth first fill
        """

        # TODO: This needs to be expanded to use more attrs and not just
        #       RequestCpus. Similar to glideFrontendLib.countMatch()

        direct_match = {}    # Number of direct job matches
        prop_match = {}      #
        hereonly_match = {}  # Jobs that can only run here
        prop_match_cpu = {}  # Total Cpus: prop_match * GLIDEIN_CPUS

        jobs = job_types[job_type]['dataframe']
        if not jobs.empty:
            # Get group of jobs based on request cpus
            job_groups = jobs.groupby('RequestCpus')

            for (req_cpus, job_group) in job_groups:
                # Group jobs by matching criteria: RequestCpus for now
                # We care about job counts for each group
                job_count = len(job_group)

                # Figure out which entries match this job group
                # Figure out how may glideins to request based on the FOM
                # Algorithm:
                # 1. Fill the sites with lowest FOM first
                # 2. If there are multiple sites with FOM split the request
                #    equally amongst them
                matches = set()
                for index, row in entries.query('GLIDEIN_CPUS >= %i' % req_cpus).iterrows():
                    matches.add((row.get('CollectorHost'), row.get('Name')))

                if len(matches) == 0:
                    # These jobs do not match anywhere. Special entry (None, None)
                    direct_match[(None, None)] = direct_match.get(
                        (None, None), 0) + job_count
                    prop_match[(None, None)] = prop_match.get(
                        (None, None), 0) + job_count
                    hereonly_match[(None, None)] = hereonly_match.get(
                        (None, None), 0) + job_count
                    prop_match_cpu[(None, None)] = prop_match_cpu.get(
                        (None, None), 0) + (job_count * req_cpus)
                elif len(matches) == 1:
                    # These jobs can only run here
                    key = next(iter(matches))
                    direct_match[key] = direct_match.get(key, 0) + job_count
                    prop_match[key] = prop_match.get(key, 0) + job_count
                    this_entry = entries.query('Name=="%s"' % key[1])
                    # glidein_cpus = 1 # default to 1 if not defined
                    glidein_cpus = this_entry.get('GLIDEIN_CPUS', 1)
                    prop_match_cpu[key] = math.ceil(
                        (prop_match_cpu.get(key, 0) + float(req_cpus)) / glidein_cpus)
                else:
                    fom_matches = self.group_matches_by_fom(matches, entries)

                    # How many jobs have been considered so far
                    # Start with entries with lowest FOM and fill them first
                    job_count_matched = 0

                    for (fom, fom_group_entries) in fom_matches:
                        job_count_unmatched = job_count - job_count_matched
                        if job_count_unmatched > 0:
                            # Distribute the jobs equally among this entry group
                            # TODO: Currently this will only consider first
                            #       FOM group. Need to spill over to other groups
                            #       by looking at the entries max capacity
                            # TODO: Check if we need to really go depth first
                            #       or fill all FOM groups but in ratio of their
                            #       FOMs
                            for key in matches:
                                this_entry_df = fom_group_entries.query(
                                    '(Name=="%s") and (GLIDEIN_In_Downtime != True)' % key[1])
                                if len(this_entry_df):
                                    if (job_count - job_count_matched) > 0:
                                        direct_match[key] = direct_match.get(
                                            key, 0) + job_count
                                    else:
                                        # We already matched everything
                                        # Just populate the stats
                                        direct_match[key] = direct_match.get(
                                            key, 0)
                                        prop_match[key] = prop_match.get(
                                            key, 0)
                                    # hereonly_match remains same
                                    hereonly_match[key] = hereonly_match.get(
                                        key, 0)
                            # Populate info for entries that are in downtime
                            #down_entries_df = fom_group_entries.query('(GLIDEIN_In_Downtime == True)')
                        else:
                            # Consider other FOM groups that also matched
                            # We already matched everything to other FOM groups
                            # Populate the stats as downtime doesnt mattter
                            for key in matches:
                                this_entry_df = fom_group_entries.query(
                                    '(Name=="%s")' % key[1])
                                direct_match[key] = direct_match.get(key, 0)
                                hereonly_match[key] = hereonly_match.get(
                                    key, 0)
                                prop_match[key] = prop_match.get(key, 0)
                        # Add stats for all entries in downtime
                        # in case they are not considered above
                        fom_group_entries_down = fom_group_entries.query(
                            '(GLIDEIN_In_Downtime == True)')
                        for index, row in fom_group_entries_down.iterrows():
                            key = (row['CollectorHost'], row['Name'])
                            direct_match[key] = direct_match.get(key, 0)
                            hereonly_match[key] = hereonly_match.get(key, 0)
                            prop_match[key] = prop_match.get(key, 0)
        #self.logger.info('---------- count_match return keys ----------')
        #self.logger.info('---------- count_match return keys ----------')
        total = job_types[job_type]['abs']
        return (direct_match, prop_match, hereonly_match, prop_match_cpu, total)

    def matches_with_fom(self, matches, entries):
        """
        Given the entries and matches, return matches with entire entry
        classad and FOM series added to the df
        """

        #self.logger.info('---------- %s ----------' % 'group_matches_by_fom')
        # ASSUMTION: Entry names are unique
        # Get all the classad names for the entries from the matches
        entry_classad_names = [x[1] for x in matches]
        df1 = pandas.DataFrame({'Name': entry_classad_names})
        # Get the intersection of rows with column 'Name'
        matches_df = pandas.merge(entries, df1, on=['Name'], how='inner')
        # Get the intersection of matches_df and fom_entries
        # Following will give all the matches with entire entry classad and FOM
        matches_fom_entries_df = pandas.merge(
            self.fom_entries, matches_df, on=['EntryName'], how='inner')
        #self.logger.info('----------> %s' % matches_fom_entries_df.columns.values)
        return matches_fom_entries_df

    def group_matches_by_fom(self, matches, entries):
        """
        Given the entries and matches, group entries by their respective FOM
        Return a dataframe groupby object with FOM and entries dataframe with
        that FOM sorted by the FOM
        """
        return self.matches_matches_with_fom(matches, entries).groupby(['FOM'])


###############################################################################
# Common functions
# TODO: Move them to a common library outside this module
###############################################################################

def count_total_cores(slots):
    """
    Counts total cores in the nondynamic slots dataframe
    """
    count = 0
    if not slots.empty:
        # TotalSlotCpus should always be the correct number but
        # is not defined pre partitionable slots
        count = slots.loc[slots['SlotType'] == 'Partitionable', 'TotalSlotCpus'].sum()
        count += slots.loc[slots['SlotType'] != 'Partitionable', 'Cpus'].sum()
    return count


def count_idle_cores(slots):
    """
    Counts cores in the idle slots dataframe
    """
    count = 0
    if not slots.empty:
        count = slots['Cpus'].sum()
    return count


def count_running_cores(slots):
    """
    Counts cores in the running slots dataframe
    """
    count = 0
    if not slots.empty:
        count = slots.loc[slots['SlotType'] != 'Partitionable', 'Cpus'].sum()
    return count


def get_vo_entries(vo, all_entries):
    """
    Get the list of entries where the given VO is allowed
    """
    entries = pandas.DataFrame()
    for index, row in all_entries.iterrows():
        allowed_vos = row.get('GLIDEIN_Supported_VOs')
        if pandas.notnull(allowed_vos):
            allowed_vo_list = [i.strip() for i in allowed_vos.split(',')]
            if vo in allowed_vo_list:
                entries = entries.append(row)
    return entries


def create_credential_list(credentials, group_descript):
    """
    Create a list of Credential objects from the credentials
    configured in the frontend
    """
    credential_list = []
    num = 0
    for cred in credentials:
        credential_list.append(Credential(num, cred, group_descript))
        num += 1
    return credential_list


def append_running_on(jobs, slots):
    """
    For every running job add the RunningOn info to the jobs dataframe
    """
    # TODO: Is there a better way to do this in pandas?
    ro_list = []
    for index, job in jobs.iterrows():
        ro = 'UNKNOWN'
        remote_host = job.get('RemoteHost')
        if pandas.notnull(remote_host):
            matching_slots = slots.query('Name == "%s"' % remote_host)
            if len(matching_slots) > 1:
                logger.info('ERROR: Multiple slots %s running same job found' %
                            matching_slots['Name'].tolist())
            elif len(matching_slots) == 1:
                # TODO: Find a better way to do this through pandas
                schedd = matching_slots.get('GLIDEIN_Schedd').tolist()[
                    0].split('@')
                factory_pool = schedd[-1].split(':')[0]

                entry_name = matching_slots.get(
                    'GLIDEIN_ENTRY_NAME').tolist()[0]
                glidein_name = matching_slots.get('GLIDEIN_Name').tolist()[0]
                factory_name = matching_slots.get(
                    'GLIDEIN_Factory').tolist()[0]
                #factory_pool = matching_slots.get('CollectorHost').tolist()[0]
                ro = '%s@%s@%s@%s' % (entry_name, glidein_name, factory_name,
                                      factory_pool)
            else:
                # len(matching_slots) == 0
                # NOTE: A job may be in final stages or maybe its not updated
                #       while the slot goes away. In that case
                #       len(matching_slots) will be 0. Just ignore it.
                pass

        ro_list.append(ro)
    # TODO: Getting warning:  SettingWithCopyWarning:
    #       A value is trying to be set on a copy of a slice from a DataFrame.
    #       Try using .loc[row_indexer,col_indexer] = value instead
    # From https://stackoverflow.com/questions/20625582/how-to-deal-with-settingwithcopywarning-in-pandas
    # For this use case you want to add RunningOn to the original dataframe
    # pd.options.mode.chained_assignment = None  # default='warn'

    jobs['RunningOn'] = ro_list


def log_and_sum_factory_line(factory, is_down, factory_stat_arr,
                             old_factory_stat_arr, fom='-'):
    """
    Will log the factory_stat_arr (tuple composed of 17 numbers)
    and return a sum of factory_stat_arr+old_factory_stat_arr
    """
    # if numbers are too big, reduce them to either k or M for presentation
    form_arr = []
    for i in factory_stat_arr:
        if i < 100000:
            form_arr.append("%5i" % i)
        elif i < 10000000:
            form_arr.append("%4ik" % (i / 1000))
        else:
            form_arr.append("%4iM" % (i / 1000000))

    if is_down:
        down_str = "Down"
    else:
        down_str = "Up  "

    if fom == sys.float_info.max:
        fom = 'INFINITY'

    if isinstance(fom, (float, int)):
        logger.info(('%s(%s %s %s %s) %s(%s %s) | %s %s %s %s | %s %s %s | %s %s | ' % tuple(
            form_arr)) + ('%s %14.4f %s' % (down_str, fom, factory)))
    else:
        logger.info(('%s(%s %s %s %s) %s(%s %s) | %s %s %s %s | %s %s %s | %s %s | ' % tuple(
            form_arr)) + ('%s %14s %s' % (down_str, fom, factory)))

    new_arr = []
    for i in range(len(factory_stat_arr)):
        new_arr.append(factory_stat_arr[i] + old_factory_stat_arr[i])
    return new_arr


def init_factory_stats_arr():
    return [0] * 17


def log_factory_header():
    logger.info('            Jobs in schedd queues                 |           Slots         |       Cores       | '
                'Glidein Req | Factory Entry Information')
    logger.info('Idle (match  eff   old  uniq )  Run ( here  max ) | Total  Idle   Run  Fail | Total  Idle   Run | '
                'Idle MaxRun | State FigureOfMerit EntryName')


def get_idle_slots(slots_df):
    if slots_df.empty:
        return slots_df
    return slots_df.query('(State == "Unclaimed") and (Activity == "Idle") and ((SlotType != "Partitionable") '
                          'or (TotalSlots == 1) or ((Cpus > 0) and (Memory > 2500)))')


def get_running_slots(slots_df):
    if slots_df.empty:
        return slots_df
    return slots_df.query('((State == "Claimed") and (Activity == "Busy" or Activity == "Retiring")) '
                          'or ((SlotType == "Partitionable") and (TotalSlots > 1))')


def get_running_pslots(slots_df):
    if slots_df.empty:
        return slots_df
    return slots_df.query('(SlotType == "Partitionable") and (TotalSlots > 1)')


def get_nondynamic_slots(slots_df):
    if slots_df.empty:
        return slots_df
    return slots_df.query('SlotType != "Dynamic"')


def get_failed_slots(slots_df):
    if slots_df.empty:
        return slots_df
    return slots_df.query('(State == "Drained") and (Activity == "Retiring")')


def count_slots_by_state(slots_df):
    return {
        'Idle': len(get_idle_slots(slots_df)),
        'Running': len(get_running_slots(slots_df)),
        'Total': len(slots_df)
    }


def compute_weighted_share(n, n_total, req_total):
    return int(math.ceil(float(n) * req_total / n_total))


def compute_nth(n):
    return float(1) / n
