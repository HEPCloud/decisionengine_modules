#!/usr/bin/env python
"""
Generic AWS publisher

"""
import abc
import os
import copy
import pandas as pd

from decisionengine.framework.modules import Publisher
import decisionengine.framework.configmanager.ConfigManager as configmanager
import decisionengine.framework.dataspace.datablock as datablock
import decisionengine.framework.dataspace.dataspace as dataspace
import decisionengine.modules.graphite_client as graphite

DEFAULT_GRAPHITE_HOST='fermicloud399.fnal.gov'
DEFAULT_GRAPHITE_PORT=2004

class AWSGenericPublisher(Publisher.Publisher):

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self.graphite_host = args[0].get('graphite_host', DEFAULT_GRAPHITE_HOST)
        self.graphite_port = args[0].get('graphite_port', DEFAULT_GRAPHITE_PORT)
        self.graphite_context = args[0].get('graphite_context', self.graphite_context())
        self.publush_to_graphite = args[0].get('publish_to_graphite')
        self.output_file = args[0].get('output_file')

    @abc.abstractmethod
    def consumes(self): # this must be implemented by the inherited class
        return None

    @abc.abstractmethod
    def graphite_context(self): # this must be implemented by the inherited class
        return None

    def publish(self, data_block):
        """
        Publish data

        :type data_block: :obj:`~datablock.DataBlock`
        :arg data_block: data block

        """
        if not self.consumes:
            return
        if self.graphite_host and self.publush_to_graphite:
            end_point = graphite.Graphite(host=self.graphite_host)
            end_point.send_dict(self.graphite_context, data_block[self.consumes()[0]], debug_print=False, send_data=False)
        csv_data = data_block[self.consumes()[0]].to_csv(self.output_file, index=False)
        if not self.output_file:
            print csv_data

