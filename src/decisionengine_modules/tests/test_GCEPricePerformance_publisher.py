
import pandas

from decisionengine_modules.GCE.publishers import GCEPricePerformance_publisher

config_pp_pub = {"publish_to_graphite": True,
                 "graphite_host": "lsdataitb.fnal.gov",
                 "graphite_port": 2004,
                 "graphite_context": "hepcloud.de.gce",
                 "output_file": "/etc/decisionengine/modules.data/test_GCE_pr_perf.csv"}

valid_datablock = pandas.DataFrame({
    'EntryName': [
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-2",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-4",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-8",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-16",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-32",
        "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768"],
    'PricePerformance': [1.49842271293,
                         2.35148514851,
                         2.40811153359,
                         2.29191797346,
                         2.43980738363,
                         2.60944206009,
                         2.16019261637]})

# expected output
valid_output_dict = {
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1": 1.49842271293,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-2": 2.35148514851,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-4": 2.40811153359,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-8": 2.29191797346,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-16": 2.43980738363,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-32": 2.60944206009,
    "FNAL_HEPCLOUD_GOOGLE_us-central1-a_custom-16-32768": 2.16019261637
}


class TestGCEPricePerformancePublisher:

    def test_consumes(self):
        pp_pub = GCEPricePerformance_publisher.GCEPricePerformancePublisher(
            config_pp_pub)
        assert pp_pub._consumes == {'GCE_Price_Performance': pandas.DataFrame}

    def test_graphite_context(self):
        pp_pub = GCEPricePerformance_publisher.GCEPricePerformancePublisher(
            config_pp_pub)
        output = pp_pub.graphite_context(valid_datablock)
        assert output[0] == "hepcloud.de.gce"
        assert output[1].get(
            "FNAL_HEPCLOUD_GOOGLE_us-central1-a_n1-standard-1.price_perf") == 1.49842271293
