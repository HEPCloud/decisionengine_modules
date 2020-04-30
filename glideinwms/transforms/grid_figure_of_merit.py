
import pandas
import pprint

import logging
from decisionengine.framework.modules import Transform
from decisionengine_modules.util.figure_of_merit import figure_of_merit

CONSUMES = ['Factory_Entries_Grid']

PRODUCES = ['Grid_Figure_Of_Merit']

ATTR_ENTRYNAME = 'EntryName'
ATTR_FOM = 'Grid_Figure_Of_Merit'


class GridFigureOfMerit(Transform.Transform):

    def __init__(self, config):
        super(GridFigureOfMerit, self).__init__(config)
        self.config = config
        self.logger = logging.getLogger()
        self.price_performance = self.config.get('price_performance', 1)

    def transform(self, datablock):
        """
        Grid sites FOM are straight up assumed as 0 for now
        """

        entries = datablock.get('Factory_Entries_Grid',
                                pandas.DataFrame({ATTR_ENTRYNAME: []}))
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
                                              idle, max_idle)
                }
                foms.append(f)

        return {PRODUCES[0]: pandas.DataFrame(foms)}

    def consumes(self, name_list=None):
        return CONSUMES

    def produces(self, name_schema_id_list=None):
        return PRODUCES


def module_config_template():
    """
    print a template for this module configuration data
    """

    template = {
        "GridFigureOfMerit": {
            "module": "decisionengine_modules.glideinwms.transforms.grid_figure_of_merit",
            "name": "GridFigureOfMerit",
            "parameters": {},
        }
    }

    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    print this module configuration information
    """
    print('consumes %s' % CONSUMES)
    print('produces %s' % PRODUCES)
    module_config_template()


def main():
    """
    Call this a a test unit or use as CLI of this module
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--configtemplate",
                        action="store_true",
                        help="prints the expected module configuration")

    parser.add_argument("--configinfo",
                        action="store_true",
                        help="prints config template along with produces and consumes info")

    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()


if __name__ == "__main__":
    main()
