"""
Generic publisher for graphana

"""
import abc
import pandas

from decisionengine.framework.modules import Publisher
from decisionengine.framework.modules.Publisher import Parameter
import decisionengine_modules.graphite_client as graphite

DEFAULT_GRAPHITE_HOST = 'fermicloud399.fnal.gov'
DEFAULT_GRAPHITE_PORT = 2004
DEFAULT_GRAPHITE_CONTEXT = ""


@Publisher.supports_config(
    Parameter("graphite_host", default=DEFAULT_GRAPHITE_HOST),
    Parameter("graphite_port", default=DEFAULT_GRAPHITE_PORT),
    Parameter("max_retries", default=2, comment="Number of retries allowed to send data to Graphite."),
    Parameter("retry_interval", default=60, comment="Number of seconds to wait between retries."),
    Parameter("graphite_context", default=DEFAULT_GRAPHITE_CONTEXT),
    Parameter("publish_to_graphite", type=bool),
    Parameter("output_file", type=str),
)
class GenericPublisher(Publisher.Publisher, metaclass=abc.ABCMeta):

    def __init__(self, config):
        super().__init__(config)
        self.graphite_host = config.get("graphite_host", DEFAULT_GRAPHITE_HOST)
        self.graphite_port = config.get("graphite_port", DEFAULT_GRAPHITE_PORT)
        self.graphite_context_header = config.get("graphite_context", DEFAULT_GRAPHITE_CONTEXT)
        self.max_retries = config.get("max_retries", 2)
        self.retry_interval = config.get("retry_interval", 60)
        self.publish_to_graphite = config.get("publish_to_graphite")
        self.output_file = config.get("output_file")
        self.logger = self.logger.bind(class_module=__name__.split(".")[-1], )

    @classmethod
    def consumes_dataframe(cls, product_name):
        def decorator(cls):
            cls._consumes = {product_name: pandas.DataFrame}
            return cls
        return decorator

    @abc.abstractmethod
    # this must be implemented by the inherited class
    def graphite_context(self, data_frame):
        return None

    def publish(self, data_block):
        """
        Publish data

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        """
        self.logger.debug("in Graphite GenericPublisher publish")
        if not self._consumes:
            return
        product = list(self._consumes.keys())[0]
        try:
            data = data_block[product]
        except KeyError:
            self.logger.exception(f"Failed to extract {product} from data block.")
            return
        if self.graphite_host and self.publish_to_graphite:
            end_point = graphite.Graphite(host=self.graphite_host, pickle_port=self.graphite_port)
            end_point.send_dict(
                self.graphite_context(data)[0],
                self.graphite_context(data)[1],
                debug_print=False,
                send_data=True,
                max_retries=self.max_retries,
                retry_interval=self.retry_interval,
            )
        if not self.output_file:
            self.logger.debug(data.to_csv(self.output_file, index=False))
