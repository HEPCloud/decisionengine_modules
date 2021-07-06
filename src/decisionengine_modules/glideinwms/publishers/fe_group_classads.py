import pandas

import logging
from decisionengine.framework.modules import Publisher
from decisionengine_modules.htcondor.publishers import publisher

# FIXME: Awkward entanglements between subclass and base class.

# TODO: Enable publishing of glideresource_manifests
#'glideclient_manifests', 'glideresource_manifests',
_CONSUMES = [
    'glideclient_manifests', 'Factory_Entries_Grid', 'Factory_Entries_AWS', 'Factory_Entries_GCE', 'Factory_Entries_LCF'
]
_CONSUMES_DICT = dict.fromkeys(_CONSUMES, pandas.DataFrame)

@Publisher.consumes(**_CONSUMES_DICT)
class GlideinWMSManifests(publisher.HTCondorManifests):

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger()
        self._fact_entrytype_map = {
            'allow_grid_requests': 'Factory_Entries_Grid',
            'allow_aws_requests': 'Factory_Entries_AWS',
            'allow_gce_requests': 'Factory_Entries_GCE',
            'allow_lcf_requests': 'Factory_Entries_LCF'
        }
        self.classad_type = 'glideclient'

    def publish(self, datablock):
        requests_df = datablock.get('glideclient_manifests')
        facts_df = datablock.get('de_logicengine_facts')

        # Create a map of allow facts & entries
        allow_type_entries = {i: datablock.get(self._fact_entrytype_map[i]) for i in self._fact_entrytype_map}

        # Initialize to empty dataframes and add row at a time
        allow_type_req_dfs = {i: pandas.DataFrame() for i in self._fact_entrytype_map}
        for index, row in requests_df.iterrows():
            # Iterate through all requests one at a time
            # Check if the ReqName coincides with the allowed request types
            req_name = row['ReqName']

            # Identify the type of request ie (grid|gce|aws|lcf))
            for allow_type in allow_type_entries:
                these_entries = allow_type_entries[allow_type]
                if len(these_entries.query('Name=="%s"' % req_name)) > 0:
                    # This request belongs to allowed_type
                    allow_type_req_dfs[allow_type] = allow_type_req_dfs[allow_type].append(row)
                    break

        self.logger.info('Facts available in publisher %s: %s' % (self.__class__.__name__,
                                                                  facts_df.to_dict(orient='records')))
        for index, row in facts_df.iterrows():
            fact_name = row['fact_name']
            fact_value = ('%s' % row['fact_value']).lower() == 'true'
            if not fact_value:
                # Convert request idle to 0
                # TODO: Check what to do with max running
                #       For now keep it same so existing glideins can finish
                self.logger.info('Setting ReqIdleGlideins=0 for fact: %s' % fact_name)
                allow_type_req_dfs[fact_name]['ReqIdleGlideins'] = [0] * len(allow_type_req_dfs[fact_name])

        publish_requests_df = pandas.DataFrame(pandas.concat(allow_type_req_dfs.values(), ignore_index=True, sort=True))
        self.publish_to_htcondor(self.classad_type, publish_requests_df)
        self.create_invalidate_constraint(publish_requests_df)

    def create_invalidate_constraint(self, requests_df):
        if not requests_df.empty:
            for collector_host, request_group in requests_df.groupby(['CollectorHost']):
                client_names = list(set(request_group['ClientName']))
                client_names.sort()
                if client_names:
                    constraint = '(glideinmytype == "%s") && (stringlistmember(ClientName, "%s"))' % \
                                 (self.classad_type, ','.join(client_names))
                    self.invalidate_ads_constraint[collector_host] = constraint


Publisher.describe(GlideinWMSManifests)
