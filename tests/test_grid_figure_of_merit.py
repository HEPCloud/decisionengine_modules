import os
import pytest
import mock
import pprint
import pandas
from decisionengine_modules.glideinwms.transforms.grid_figure_of_merit import GridFigureOfMerit

grid_entries = ['g1', 'g2', 'g3', 'g4', 'g5']
grid_df = pandas.DataFrame({'GLIDEIN_Entry_Name': grid_entries})

datablock = {
    'Factory_Entries_Grid': grid_df
}

class TestGridFigureOfMerit():

    def test_eligible_resources_with_constraints(self):
        test_df = pandas.DataFrame({
            'EntryName': ['g1', 'g2', 'g3', 'g4', 'g5'],
            'Grid_Figure_Of_Merit': [0, 0, 0, 0, 0]
            })
        fom = GridFigureOfMerit({})
        assert(test_df.equals(fom.transform(datablock).get('Grid_Figure_Of_Merit')))
