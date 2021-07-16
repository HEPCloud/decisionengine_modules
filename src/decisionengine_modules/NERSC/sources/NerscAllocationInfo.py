"""
Get allocation info from Nersc
"""
import pandas as pd
import structlog

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter
from decisionengine_modules.NERSC.util import newt

_MAX_RETRIES = 10
_RETRY_BACKOFF_FACTOR = 1


@Source.supports_config(Parameter('constraints',
                                  type=dict,
                                  comment="""Supports the layout:

  {
     'usernames': ['user1', 'user2'],
     'newt_keys': {
        'rname': ['m2612', 'm2696'],
        'repo_type': ["STR", ],
  }
"""),
                        Parameter('max_retries', default=_MAX_RETRIES),
                        Parameter('retry_backoff_factor', default=_RETRY_BACKOFF_FACTOR),
                        Parameter('passwd_file', type=str, comment="Path to password file"))
@Source.produces(Nersc_Allocation_Info=pd.DataFrame)
class NerscAllocationInfo(Source.Source):

    """
    Information of allocations on NERSC machines
    """

    def __init__(self, config):
        super().__init__(config)

        self.constraints = config.get('constraints')
        if not isinstance(self.constraints, dict):
            raise RuntimeError('constraints should be a dict')

        self.max_retries = config.get("max_retries", _MAX_RETRIES)
        self.retry_backoff_factor = config.get("retry_backoff_factor",
                                               _RETRY_BACKOFF_FACTOR)
        self.newt = newt.Newt(
            config.get('passwd_file'),
            num_retries=self.max_retries,
            retry_backoff_factor=self.retry_backoff_factor)
        self.logger = structlog.getLogger()

    def send_query(self):
        """
        Send queries and then filter the results based on user constraints
        """
        results = []
        for username in self.constraints.get("usernames", []):
            values = self.newt.get_usage(username)
            if values:
                try:
                    results.extend(values['items'])
                except KeyError:
                    # Empty return from get_usage, so just move on
                    pass
        # filter results based on constraints specified in newt_keys dictionary
        newt_keys = self.constraints.get("newt_keys", {})
        for key, values in newt_keys.items():
            k = key
            # The below remapping is needed for backward compatibility with
            # existing config files
            if key == 'rname':
                k = 'repoName'
            if key == 'repo_type':
                k = 'repoType'
            if values:
                results = [x for x in results if x[k] in values]
        return results

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py.
        Acquire NERSC allocation info and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """
        return {'Nersc_Allocation_Info': pd.DataFrame(self.send_query())}


Source.describe(NerscAllocationInfo)
