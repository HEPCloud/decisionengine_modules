import pprint

import pandas

from decisionengine_modules.NERSC.publishers import NerscFigureOfMerit_publisher

config_fom_pub = {"publish_to_graphite": True,
                  "graphite_host": "lsdataitb.fnal.gov",
                  "graphite_port": 2004,
                  "graphite_context": "hepcloud.de.nersc",
                  "output_file": "/etc/decisionengine/modules.data/test_Nersc_fom.csv"}

valid_datablock = pandas.DataFrame({
    'EntryName': ["CMSHTPC_T3_US_NERSC_Cori",
                  "CMSHTPC_T3_US_NERSC_Cori2"],
    'FigureOfMerit': [1.0, 0.3]
})

# expected output
valid_output_dict = {"CMSHTPC_T3_US_NERSC_Cori.fig_of_merit": 1.0,
                     "CMSHTPC_T3_US_NERSC_Cori2.fig_of_merit": 0.3}


class TestNerscFigureOfMeritPublisher:

    def test_consumes(self):
        consumes = ['Nersc_Figure_Of_Merit']
        fom_pub = NerscFigureOfMerit_publisher.NerscFigureOfMeritPublisher(
            config_fom_pub)
        assert fom_pub.consumes() == consumes

    def test_graphite_context(self):
        fom_pub = NerscFigureOfMerit_publisher.NerscFigureOfMeritPublisher(
            config_fom_pub)
        output = fom_pub.graphite_context(valid_datablock)
        pprint.pprint(output)
        assert output[0] == "hepcloud.de.nersc"
        assert output[1].get("CMSHTPC_T3_US_NERSC_Cori.fig_of_merit") == 1.0
