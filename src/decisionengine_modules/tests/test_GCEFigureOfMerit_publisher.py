# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas

from decisionengine_modules.GCE.publishers import GCEFigureOfMerit_publisher

config_fom_pub = {
    "channel_name": "test",
    "publish_to_graphite": True,
    "graphite_host": "lsdataitb.fnal.gov",
    "graphite_port": 2004,
    "graphite_context": "hepcloud.de.gce",
    "output_file": "/etc/decisionengine/modules.data/test_GCE_fom.csv",
}

valid_datablock = pandas.DataFrame(
    {
        "EntryName": [
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768",
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
        ],
        "FigureOfMerit": [0, 0, 0, 0, 0, 0],
    }
)

# expected output
valid_output_dict = {
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768.fig_of_merit": 0,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit": 0,
}


def test_consumes():
    fom_pub = GCEFigureOfMerit_publisher.GCEFigureOfMeritPublisher(config_fom_pub)
    assert fom_pub._consumes == {"GCE_Figure_Of_Merit": pandas.DataFrame}


def test_graphite_context():
    fom_pub = GCEFigureOfMerit_publisher.GCEFigureOfMeritPublisher(config_fom_pub)
    output = fom_pub.graphite_context(valid_datablock)
    assert output[0] == "hepcloud.de.gce"
    assert output[1].get("FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.fig_of_merit") == 0
