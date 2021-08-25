import pandas

from decisionengine.framework.modules import Transform
from decisionengine.framework.modules.Transform import Parameter
from decisionengine_modules.util.figure_of_merit import figure_of_merit

ATTR_ENTRYNAME = 'EntryName'
ATTR_FOM = 'Grid_Figure_Of_Merit'


@Transform.supports_config(Parameter('price_performance', default=1))
@Transform.consumes(Factory_Entries_Grid=pandas.DataFrame)
@Transform.produces(Grid_Figure_Of_Merit=pandas.DataFrame)
class GridFigureOfMerit(Transform.Transform):

    def __init__(self, config):
        super().__init__(config)
        self.logger = self.logger.bind(module=__name__.split(".")[-1])
        self.price_performance = config.get('price_performance', 1)

    def transform(self, datablock):
        """
        Grid sites FOM are straight up assumed as 0 for now
        """
        self.getlogger().debug("in GridFigureOfMerit::transform")
        entries = self.Factory_Entries_Grid(datablock)
        if entries is None:
            entries = pandas.DataFrame({ATTR_ENTRYNAME: []})
        foms = []
        if not entries.empty:
            for index, entry in entries.iterrows():
                running = float(entry['GlideinMonitorTotalStatusRunning'])
                max_allowed = float(entry['GlideinConfigPerEntryMaxGlideins'])
                max_idle = float(entry['GlideinConfigPerEntryMaxIdle'])
                idle = float(entry['GlideinMonitorTotalStatusIdle'])
                f = {
                    ATTR_ENTRYNAME: entry[ATTR_ENTRYNAME],
                    ATTR_FOM: figure_of_merit(self.price_performance,
                                              running, max_allowed,
                                              self.getlogger(),
                                              idle, max_idle)
                }
                foms.append(f)

        return {'Grid_Figure_Of_Merit': pandas.DataFrame(foms)}


Transform.describe(GridFigureOfMerit)
