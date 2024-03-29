# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pandas
import pytest

from decisionengine_modules.glideinwms.publishers import job_clustering_publisher

valid_datablock = pandas.DataFrame(
    {
        "Job_Bucket_Criteria_Expr": [
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='nova'",
        ],
        "Site_Bucket_Criteria_Expr": [
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            [
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1",
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1",
            ],
        ],
        "Totals": [2, 1, 2, 1, 1],
        "Frontend_Group": ["group_1", "group_2", "group_3", "group_4", "group_5"],
    },
    columns=["Job_Bucket_Criteria_Expr", "Site_Bucket_Criteria_Epxr", "Totals", "Frontend_Group"],
)

# expected output
valid_output_dict = {
    "VO_Name=='cms'_and_RequestCpus==1_and_(MaxWallTimeMins>0_and_MaxWallTimeMins<=_60*12).job_cluster": 2,
    "VO_Name=='cms'_and_RequestCpus==2_and_(MaxWallTimeMins>0_and_MaxWallTimeMins<=_60*12).job_cluster": 1,
    "VO_Name=='cms'_and_RequestCpus==1_and_(MaxWallTimeMins>60*12_and_MaxWallTimeMins<=_60*24).job_cluster": 2,
    "VO_Name=='cms'_and_RequestCpus==2_and_(MaxWallTimeMins>60*12_and_MaxWallTimeMins<=_60*24).job_cluster": 1,
    "VO_Name=='nova'.job_cluster": 1,
}


@pytest.fixture
def job_clustering_pub():
    config = {
        "channel_name": "test",
        "publish_to_graphite": True,
        "graphite_host": "lsdataitb.fnal.gov",
        "graphite_port": 2004,
        "graphite_context": "hepcloud.de.glideinwms",
        "output_file": "/etc/decisionengine/modules.data/test_job_clusters.csv",
    }
    return job_clustering_publisher.JobClusteringPublisher(config)


def test_consumes(job_clustering_pub):
    assert job_clustering_pub._consumes == {"job_clusters": pandas.DataFrame}


def test_graphite_context(job_clustering_pub):
    output = job_clustering_pub.graphite_context(valid_datablock)
    assert output[0] == "hepcloud.de.glideinwms"
    assert output[1].get("group_1.job_cluster") == 2
    assert output[1].get("group_2.job_cluster") == 1
    assert output[1].get("group_3.job_cluster") == 2
    assert output[1].get("group_4.job_cluster") == 1
    assert output[1].get("group_5.job_cluster") == 1
