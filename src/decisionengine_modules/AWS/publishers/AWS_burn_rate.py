"""
Publishes AWS VM burn rate

"""
from decisionengine.framework.modules import Publisher
from decisionengine_modules.AWS.publishers.AWS_generic_publisher import AWSGenericPublisher as publisher


@publisher.consumes_dataframe('AWS_Burn_Rate')
class AWSBurnRatePublisher(publisher):

    def graphite_context(self, dataframe):
        d = {}
        # There should be only one row [0] in the AWS_Burn_Rate data block
        d['FERMILAB.BurnRate'] = dataframe.loc[0, 'BurnRate'].item()
        return self.graphite_context_header, d


Publisher.describe(AWSBurnRatePublisher)
