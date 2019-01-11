import os
import sys
import pytest
import mock
import pprint
import pandas
from decisionengine_modules.glideinwms.transforms.grid_figure_of_merit import GridFigureOfMerit

grid_entries = ['g1', 'g2', 'g3', 'g4', 'g5']
running = [5, 10, 15, 20, 200]
max_allowed = [10, 10, 10, 2000, 500]
idle = [20, 3, 4, 5, 6]
max_idle = [10, 10, 10, 10, 10]

entries = {
    'EntryName': grid_entries,
    'GlideinMonitorTotalStatusRunning': running,
    'GlideinConfigPerEntryMaxGlideins': max_allowed,
    'GlideinMonitorTotalStatusIdle': idle,
    'GlideinConfigPerEntryMaxIdle': max_idle,
}

grid_df = pandas.DataFrame(entries)

datablock = {
    'Factory_Entries_Grid': grid_df
}

class TestGridFigureOfMerit():

    def test_eligible_resources_with_constraints(self):
        test_df = pandas.DataFrame({
            'EntryName': ['g1', 'g2', 'g3', 'g4', 'g5'],
            'Grid_Figure_Of_Merit': [sys.float_info.max, sys.float_info.max, sys.float_info.max, 1.050000e-02, 4.020000e-01]
            })
        fom = GridFigureOfMerit({})
        assert(test_df.equals(fom.transform(datablock).get('Grid_Figure_Of_Merit')))
