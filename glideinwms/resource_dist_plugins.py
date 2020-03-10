#!/usr/bin/python
import six
import abc
import pandas

import logging

logger = logging.getLogger()

@six.add_metaclass(abc.ABCMeta)
class ResourceOrderPlugin(object):

    """
    Pure virtual class to have a minimum set of methods defined
    """

    def __init__(self, resources):
        # ordered_resources if a list of tuple (EntryName, ordering_criteria)
        # list is ordered in descending order of preferred resources
        self.resources = resources
        self._ordered_resources = []
        self.order_resources(ascending=True)


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return '%s' % vars(self)


    @abc.abstractmethod
    def order_resources(self, ascending=True):
        """
        max_count can be integer or string
        """
        return


    @abc.abstractmethod
    def eligible_resources(self, constraint=None, limit=None):
        """
        max_count can be integer or string
        """
        return


class FOMOrderPlugin(ResourceOrderPlugin):

    def __init__(self, resources):
        self.resource_fom_column_map = {
            'Grid_Figure_Of_Merit': 'Grid_Figure_Of_Merit',
            'GCE_Figure_Of_Merit': 'FigureOfMerit',
            'AWS_Figure_Of_Merit': 'AWS_Figure_Of_Merit',
            'Nersc_Figure_Of_Merit': 'FigureOfMerit'
        }
        ResourceOrderPlugin.__init__(self, resources)


    def order_resources(self, ascending=True):

        rss_foms = pandas.DataFrame()

        for rss in self.resource_fom_column_map:
            fom_df = self.resources.get(rss)
            logger.info('Ordering resources based on %s' % rss)
            if (fom_df is not None) and (fom_df.empty is False):
                # Create a new dataframe with just EntryName and FOM
                df = fom_df[['EntryName', self.resource_fom_column_map[rss]]]
                # Rename the entry type specific FOM columns to just 'fom'
                df = df.rename(columns={self.resource_fom_column_map[rss]: 'FOM'})
                # Append the results
                rss_foms = rss_foms.append(df)
            else:
                logger.info('%s does not have any entries to order' % rss)
        try:
            self._ordered_resources = rss_foms.sort_values(
                by=['FOM'], ascending=ascending).reset_index(drop=True)
        except KeyError as e:
            logger.error('Unable to find Figure of Merrit "FOM" in the dataframe columns %s' % list(self.resources.columns))


    def eligible_resources(self, constraint=None, limit=None):
        """
        max_count can be integer or string
        """

        if constraint is None:
            return self._ordered_resources.head(limit)
        else:
            return self._ordered_resources.query(constraint).head(limit)
