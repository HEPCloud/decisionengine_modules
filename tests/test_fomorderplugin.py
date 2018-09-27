import os
import pytest
import mock
import pprint
import pandas

from decisionengine_modules.glideinwms import resource_dist_plugins



nersc_entries = ['n1', 'n2', 'n3', 'n4', 'n5']
nersc_foms = [0.1, 0.3, 1, 2.1, .05]
nersc_df = pandas.DataFrame({'entry_name': nersc_entries, 'Nersc_Figure_Of_Merit': nersc_foms})

aws_entries = ['a1', 'a2', 'a3', 'a4', 'a5']
aws_foms = [0.01, 0.1, 1, 0.1, .15]
aws_df = pandas.DataFrame({'entry_name': aws_entries, 'AWS_Figure_Of_Merit': aws_foms})

grid_entries = ['g1', 'g2', 'g3', 'g4', 'g5']
grid_foms = [0, 0, 0, 0, 0]
grid_df = pandas.DataFrame({'entry_name': grid_entries, 'Grid_Figure_Of_Merit': grid_foms})

resources = {
    'Grid_Figure_Of_Merit': grid_df,
    'AWS_Figure_Of_Merit': aws_df,
    'Nersc_Figure_Of_Merit': nersc_df
}

class TestFOMOrderPlugin():

    def test_order_resources(self):
        test_df = pandas.DataFrame({
            'entry_name': ['g1', 'g2', 'g3', 'g4', 'g5', 'a1', 'n5', 'n1',
                           'a2', 'a4', 'a5', 'n2', 'n3', 'a3', 'n4'],
            'fom': [0, 0, 0, 0, 0, 0.01, 0.05, 0.1,
                    0.1, 0.1, 0.15, 0.3, 1, 1, 2.1]
            })

        fom_plugin = resource_dist_plugins.FOMOrderPlugin(resources)
        assert(test_df.equals(fom_plugin._ordered_resources))


    def test_eligible_resources(self):
        test_df = pandas.DataFrame({
            'entry_name': ['g1', 'g2', 'g3', 'g4', 'g5', 'a1', 'n5', 'n1',
                           'a2', 'a4', 'a5', 'n2', 'n3', 'a3', 'n4'],
            'fom': [0, 0, 0, 0, 0, 0.01, 0.05, 0.1,
                    0.1, 0.1, 0.15, 0.3, 1, 1, 2.1]
            })
        fom_plugin = resource_dist_plugins.FOMOrderPlugin(resources)

        # all resources are returned correctly
        assert(test_df.equals(fom_plugin.eligible_resources()))

    def test_eligible_resources_with_constraints(self):
        test_df = pandas.DataFrame({
            'entry_name': ['g1', 'g2', 'g3', 'g4', 'g5', 'a1', 'n5', 'n1',
                           'a2', 'a4', 'a5', 'n2'],
            'fom': [0, 0, 0, 0, 0, 0.01, 0.05, 0.1,
                    0.1, 0.1, 0.15, 0.3]
            })
        fom_plugin = resource_dist_plugins.FOMOrderPlugin(resources)
        # constraint works correctly
        fom_df = fom_plugin.eligible_resources(constraint='fom < 1').reset_index(drop=True)
        assert(test_df.equals(fom_df))

    def test_eligible_resources_with_constraints_limit(self):
        test_df = pandas.DataFrame({
            'entry_name': ['g1', 'g2', 'g3', 'g4', 'g5', 'a1', 'n5', 'n1'],
            'fom': [0, 0, 0, 0, 0, 0.01, 0.05, 0.1]
            })
        fom_plugin = resource_dist_plugins.FOMOrderPlugin(resources)
        # constraint works correctly
        fom_df = fom_plugin.eligible_resources(constraint='fom < 1', limit=8).reset_index(drop=True)
        assert(test_df.equals(fom_df))
