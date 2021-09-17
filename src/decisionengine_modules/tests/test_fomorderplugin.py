import pandas

from decisionengine_modules.glideinwms import resource_dist_plugins

nersc_entries = ["n1", "n2", "n3", "n4", "n5"]
nersc_foms = [0.1, 0.3, 1, 2.1, 0.05]
nersc_df = pandas.DataFrame({"EntryName": nersc_entries, "FigureOfMerit": nersc_foms})

aws_entries = ["a1", "a2", "a3", "a4", "a5"]
aws_foms = [0.01, 0.1, 1, 0.1, 0.15]
aws_df = pandas.DataFrame({"EntryName": aws_entries, "AWS_Figure_Of_Merit": aws_foms})

grid_entries = ["g1", "g2", "g3", "g4", "g5"]
grid_foms = [0, 0, 0, 0, 0]
grid_df = pandas.DataFrame({"EntryName": grid_entries, "Grid_Figure_Of_Merit": grid_foms})

resources = {"Grid_Figure_Of_Merit": grid_df, "AWS_Figure_Of_Merit": aws_df, "Nersc_Figure_Of_Merit": nersc_df}


class TestFOMOrderPlugin:
    def test_order_resources(self):
        test_df = pandas.DataFrame(
            {
                "EntryName": ["g1", "g2", "g3", "g4", "g5", "a1", "n5", "a2", "a4", "n1", "a5", "n2", "a3", "n3", "n4"],
                "FOM": [0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.05, 0.10, 0.10, 0.10, 0.15, 0.30, 1.00, 1.00, 2.10],
            }
        )

        ordered_resources = resource_dist_plugins.order_resources(resources)
        assert test_df.equals(ordered_resources)

    def test_eligible_resources(self):
        test_df = pandas.DataFrame(
            {
                "EntryName": ["g1", "g2", "g3", "g4", "g5", "a1", "n5", "a2", "a4", "n1", "a5", "n2", "a3", "n3", "n4"],
                "FOM": [0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.05, 0.10, 0.10, 0.10, 0.15, 0.30, 1.00, 1.00, 2.10],
            }
        )

        eligible_resources = resource_dist_plugins.fom_eligible_resources(resources)
        assert test_df.equals(eligible_resources)

    def test_eligible_resources_with_constraints(self):
        test_df = pandas.DataFrame(
            {
                "EntryName": ["g1", "g2", "g3", "g4", "g5", "a1", "n5", "a2", "a4", "n1", "a5", "n2"],
                "FOM": [0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.05, 0.10, 0.10, 0.10, 0.15, 0.30],
            }
        )
        fom_df = resource_dist_plugins.fom_eligible_resources(resources, constraint="FOM < 1").reset_index(drop=True)
        assert test_df.equals(fom_df)

    def test_eligible_resources_with_constraints_limit(self):
        test_df = pandas.DataFrame(
            {
                "EntryName": ["g1", "g2", "g3", "g4", "g5", "a1", "n5", "a2"],
                "FOM": [0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.05, 0.10],
            }
        )
        fom_df = resource_dist_plugins.fom_eligible_resources(resources, constraint="FOM < 1", limit=8).reset_index(
            drop=True
        )
        assert test_df.equals(fom_df)
