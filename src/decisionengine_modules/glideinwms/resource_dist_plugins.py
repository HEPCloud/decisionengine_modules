import pandas as pd

_RESOURCE_FROM_COLUMN_MAP = {
    "Grid_Figure_Of_Merit": "Grid_Figure_Of_Merit",
    "GCE_Figure_Of_Merit": "FigureOfMerit",
    "AWS_Figure_Of_Merit": "AWS_Figure_Of_Merit",
    "Nersc_Figure_Of_Merit": "FigureOfMerit",
}


def order_resources(resources, logger=None):
    ordered_resources = []
    rss_foms = pd.DataFrame()

    for rss, column_name in _RESOURCE_FROM_COLUMN_MAP.items():
        fom_df = resources.get(rss)
        if logger is not None:
            logger.info(f"Ordering resources based on {rss}")
        if (fom_df is not None) and (fom_df.empty is False):
            # Create a new dataframe with just EntryName and FOM
            df = fom_df[["EntryName", column_name]]
            # Rename the entry type specific FOM columns to just 'fom'
            df = df.rename(columns={column_name: "FOM"})
            # Append the results
            rss_foms = rss_foms.append(df)
        elif logger is not None:
            logger.info(f"{rss} does not have any entries to order")
    try:
        ordered_resources = rss_foms.sort_values(by=["FOM", "EntryName"], ascending=True).reset_index(drop=True)
    except KeyError:
        if logger is not None:
            logger.exception(
                f'Unable to find Figure of Merrit "FOM" in the dataframe columns {list(resources.columns)}'
            )
    return ordered_resources


def fom_eligible_resources(resources, constraint=None, limit=None, logger=None):
    ordered_resources = order_resources(resources, logger)
    if constraint is None:
        return ordered_resources.head(limit)
    return ordered_resources.query(constraint).head(limit)
