"""
Query Resource Limits from another channel with the factory source
"""
import typing

from decisionengine.framework.modules import Source, SourceProxy
from decisionengine.framework.modules.Source import Parameter


@Source.supports_config(Parameter('entry_limit_attrs', type=list))
@Source.produces(GCE_Resource_Limits=typing.Any)
class GCEResourceLimits(SourceProxy.SourceProxy):
    """
    Consumes factory data to find GCE entry limits
    """

    def __init__(self, config):
        super().__init__(config)
        self.entry_limit_attrs = config.get('entry_limit_attrs')

    def acquire(self):
        """
        Acquire google factory entry limits from source proxy
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        factory_data = super().acquire()
        if len(factory_data) != 1:
            raise RuntimeError("Incorrect number of elements in data block.")
        df_factory_data = factory_data.popitem()[1]
        df_entry_limits = df_factory_data[self.entry_limit_attrs]
        return {'GCE_Resource_Limits': df_entry_limits}


Source.describe(GCEResourceLimits)
