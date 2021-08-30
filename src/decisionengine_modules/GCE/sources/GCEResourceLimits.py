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
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )
        self.entry_limit_attrs = config.get('entry_limit_attrs')
        if len(self.data_keys) != 1:
            raise RuntimeError("Only one element may be specified in the 'Dataproducts' parameter.")

    def acquire(self):
        """
        Acquire google factory entry limits from source proxy
        and return as pandas frame
        :rtype: :obj:`~pd.DataFrame`
        """

        self.logger.debug("in GCEResourceLimits acquire")
        factory_data = super().acquire()
        assert len(factory_data) == 1
        df_factory_data = factory_data.popitem()[1]
        df_entry_limits = df_factory_data[self.entry_limit_attrs]
        return {'GCE_Resource_Limits': df_entry_limits}


Source.describe(GCEResourceLimits)
