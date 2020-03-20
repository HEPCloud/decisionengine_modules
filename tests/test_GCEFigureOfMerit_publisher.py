import pprint

import pandas

from decisionengine_modules.GCE.publishers import GCEFigureOfMerit_publisher

config_fom_pub = {"publish_to_graphite": True,
                  "graphite_host": "lsdataitb.fnal.gov",
                  "graphite_port": 2004,
                  "graphite_context": "hepcloud.de.gce",
                  "output_file": "/etc/decisionengine/modules.data/test_GCE_fom.csv"}

valid_datablock = pandas.DataFrame({
    'EntryName': ["FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
                  "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
                  "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
                  "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
                  "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
                  "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1"],
    'FigureOfMerit': [0, 0, 0, 0, 0, 0]})

# expected output
valid_output_dict = {"FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768.fig_of_merit": 0,
                     "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768.fig_of_merit": 0,
                     "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768.fig_of_merit": 0,
                     "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit": 0,
                     "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit": 0,
                     "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit": 0}


class TestGCEFigureOfMeritPublisher:

    def test_consumes(self):
        consumes = ['GCE_Figure_Of_Merit']
        fom_pub = GCEFigureOfMerit_publisher.GCEFigureOfMeritPublisher(
            config_fom_pub)
        assert fom_pub.consumes() == consumes

    def test_graphite_context(self):
        fom_pub = GCEFigureOfMerit_publisher.GCEFigureOfMeritPublisher(
            config_fom_pub)
        output = fom_pub.graphite_context(valid_datablock)
        pprint.pprint(output)
        assert output[0] == "hepcloud.de.gce"
        assert output[1].get(
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit") == 0
