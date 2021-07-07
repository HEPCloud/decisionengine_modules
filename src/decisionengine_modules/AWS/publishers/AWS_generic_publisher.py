"""
Generic AWS publisher

"""
import abc
import pandas

from decisionengine.framework.modules import Publisher
import decisionengine_modules.graphite_client as graphite

DEFAULT_GRAPHITE_HOST = 'fermicloud399.fnal.gov'
DEFAULT_GRAPHITE_PORT = 2004
DEFAULT_GRAPHITE_CONTEXT = ""


class AWSGenericPublisher(Publisher.Publisher, metaclass=abc.ABCMeta):

    def __init__(self, config):
        self.graphite_host = config.get(
            'graphite_host', DEFAULT_GRAPHITE_HOST)
        self.graphite_port = config.get(
            'graphite_port', DEFAULT_GRAPHITE_PORT)
        self.graphite_context_header = config.get(
            'graphite_context', DEFAULT_GRAPHITE_CONTEXT)
        self.publish_to_graphite = config.get('publish_to_graphite')
        self.output_file = config.get('output_file')

    @classmethod
    def consumes_dataframe(cls, product_name):
        def decorator(cls):
            cls._consumes = {product_name: pandas.DataFrame}
            return cls
        return decorator

    @abc.abstractmethod
    # this must be implemented by the inherited class
    def graphite_context(self, data_block):
        return None

    def publish(self, data_block):
        """
        Publish data

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        """
        if not self._consumes:
            return
        data = data_block[list(self._consumes.keys())[0]]
        if self.graphite_host and self.publish_to_graphite:
            end_point = graphite.Graphite(host=self.graphite_host,
                                          pickle_port=self.graphite_port)
            end_point.send_dict(self.graphite_context(data)[0],
                                self.graphite_context(data)[1],
                                debug_print=False,
                                send_data=True)
        csv_data = data.to_csv(self.output_file, index=False)
        if not self.output_file:
            print(csv_data)
