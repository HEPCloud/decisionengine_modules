#!/usr/bin/env python

import pandas
import pprint

from decisionengine.framework.modules import Transform
import decisionengine.framework.modules.de_logger as de_logger

CONSUMES = ['Factory_Entries_Grid']

PRODUCES = ['Grid_Figure_Of_Merit']


class GridFigureOfMerit(Transform.Transform):


    def __init__(self, config):
        super(GridFigureOfMerit, self).__init__(config)
        self.config = config
        self.logger = de_logger.get_logger()


    def transform(self, datablock):
        """
        Grid sites FOM are straight up assumed as 0 for now
        """

        entries = datablock.get('Factory_Entries_Grid', pandas.Series())
        fom_df = pandas.DataFrame({'EntryName': entries['GLIDEIN_Entry_Name']})
        # FOM for grid entries is 0
        fom_df['Grid_Figure_Of_Merit'] = 0
        return {PRODUCES[0]: fom_df}


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
           "module":  "modules.glideinwms.transforms.grid_figure_of_merit",
           "name":  "GridFigureOfMerit",
           "parameters": { },
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
