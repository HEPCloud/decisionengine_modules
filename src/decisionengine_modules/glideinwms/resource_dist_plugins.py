import structlog
import pandas

from decisionengine.framework.modules.logging_configDict import CHANNELLOGGERNAME

logger = structlog.getLogger(CHANNELLOGGERNAME)
logger = logger.bind(module=__name__.split(".")[-1], channel="")

_RESOURCE_FROM_COLUMN_MAP = {
    'Grid_Figure_Of_Merit': 'Grid_Figure_Of_Merit',
    'GCE_Figure_Of_Merit': 'FigureOfMerit',
    'AWS_Figure_Of_Merit': 'AWS_Figure_Of_Merit',
    'Nersc_Figure_Of_Merit': 'FigureOfMerit'
}

def order_resources(resources):
    ordered_resources = []
    rss_foms = pandas.DataFrame()

    for rss, column_name in _RESOURCE_FROM_COLUMN_MAP.items():
        fom_df = resources.get(rss)
        logger.info('Ordering resources based on %s' % rss)
        if (fom_df is not None) and (fom_df.empty is False):
            # Create a new dataframe with just EntryName and FOM
            df = fom_df[['EntryName', column_name]]
            # Rename the entry type specific FOM columns to just 'fom'
            df = df.rename(columns={column_name: 'FOM'})
            # Append the results
            rss_foms = rss_foms.append(df)
        else:
            logger.info('%s does not have any entries to order' % rss)
    try:
        ordered_resources = rss_foms.sort_values(
            by=['FOM', 'EntryName'], ascending=True).reset_index(drop=True)
    except KeyError:
        logger.exception('Unable to find Figure of Merrit "FOM" in the dataframe columns %s' % list(resources.columns))
    return ordered_resources


def fom_eligible_resources(resources, constraint=None, limit=None):
    ordered_resources = order_resources(resources)
    if constraint is None:
        return ordered_resources.head(limit)
    return ordered_resources.query(constraint).head(limit)
