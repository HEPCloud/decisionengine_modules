# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import pprint

import pandas
import pytest

from decisionengine_modules.glideinwms.transforms import job_clustering

config_test_match_exprs = {
    "channel_name": "test",
    "match_expressions": [
        {
            "job_bucket_criteria_expr": "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "frontend_group": "group_1",
            "site_bucket_criteria_expr": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
        },
        {
            "job_bucket_criteria_expr": "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "frontend_group": "group_2",
            "site_bucket_criteria_expr": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
        },
        {
            "job_bucket_criteria_expr": "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "frontend_group": "group_3",
            "site_bucket_criteria_expr": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
        },
        {
            "job_bucket_criteria_expr": "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "frontend_group": "group_4",
            "site_bucket_criteria_expr": ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
        },
        {
            "job_bucket_criteria_expr": "VO_Name=='nova'",
            "frontend_group": "group_5",
            "site_bucket_criteria_expr": [
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1",
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1",
            ],
        },
    ],
    "job_q_expr": "JobStatus==1",
}

# input with valid job_q data
valid_q_datablock = {
    "job_manifests": pandas.DataFrame(
        {
            "VO_Name": ["cms", "cms", "cms", "cms", "cms", "cms", "nova", "nova", "des"],
            "RequestCpus": [1, 1, 1, 1, 2, 2, 1, 2, 1],
            "MaxWallTimeMins": [240, 240, 1080, 720, 240, 1080, 720, 240, 240],
            "JobStatus": [1, 5, 1, 1, 1, 1, 1, 1, 1],
        }
    )
}
# expected output
valid_output_dataframe = pandas.DataFrame(
    {
        "Job_Match_Expr": [
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='nova'",
        ],
        "Factory_Match_Epxr": [
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
    columns=["Job_Match_Expr", "Factory_Match_Epxr", "Totals", "Frontend_Group"],
)

# input with empty job_q data
empty_q_datablock = {"job_manifests": pandas.DataFrame({})}
# expected output from empty job queue
empty_q_output_dataframe = pandas.DataFrame(
    {
        "Job_Match_Expr": [
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='nova'",
        ],
        "Factory_Match_Epxr": [
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            [
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1",
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1",
            ],
        ],
        "Totals": [0, 0, 0, 0, 0],
        "Frontend_Group": ["group_1", "group_2", "group_3", "group_4", "group_5"],
    },
    columns=["Job_Match_Expr", "Factory_Match_Epxr", "Totals", "Frontend_Group"],
)


# input with missing job_q data
missing_q_datablock = {
    "job_manifests": pandas.DataFrame(
        {
            "VO_Name": ["cms", "cms", "cms", "cms", "cms", "cms", "nova", "nova", "des"],
            "MaxWallTimeMins": [240, 240, 1080, 720, 240, 1080, 720, 240, 240],
            "JobStatus": [1, 5, 1, 1, 1, 1, 1, 1, 1],
        }
    )
}
# expected output from missing data job queue
missing_q_output_dataframe = pandas.DataFrame(
    {
        "Job_Match_Expr": [
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)",
            "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='cms' and RequestCpus==2 and (MaxWallTimeMins>60*12 and MaxWallTimeMins<= 60*24)",
            "VO_Name=='nova'",
        ],
        "Factory_Match_Epxr": [
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS == 1"],
            ["GLIDEIN_Supported_VOs.str.contains('CMS') and GLIDEIN_CPUS > 1"],
            [
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS == 1",
                "GLIDEIN_Supported_VOs.str.contains('Nova') and GLIDEIN_CPUS > 1",
            ],
        ],
        "Totals": [0, 0, 0, 0, 0],
        "Frontend_Group": ["group_1", "group_2", "group_3", "group_4", "group_5"],
    },
    columns=["Job_Match_Expr", "Factory_Match_Epxr", "Totals", "Frontend_Group"],
)


# ***NOTE***
# This test must be updated to remove 'Frontend_Group' from test data when the
# frontend is no longer used in the decision engine


# Test can create expected totals table based on known and valid input
# Test can handle missing job q data: missing column or missing attr, for all jobs or single job
# Test uses defaults if no dataframe retrieved
# Validate log messages


@pytest.fixture
def job_clusters():
    return job_clustering.JobClustering(config_test_match_exprs)


def test_produces(job_clusters):
    assert job_clusters._produces == {"job_clusters": pandas.DataFrame}


def test_consumes(job_clusters):
    assert job_clusters._consumes == {"job_manifests": pandas.DataFrame}


def test_transform_valid(job_clusters):
    output = job_clusters.transform(valid_q_datablock)
    pprint.pprint(output)
    db = output.get("job_clusters")
    assert db["Totals"].sum() == 7
    assert db.shape[0] == 5


def test_transform_empty_q(job_clusters):
    output = job_clusters.transform(empty_q_datablock)
    pprint.pprint(output)
    db = output.get("job_clusters")
    assert db["Totals"].sum() == 0
    assert db.shape[0] == 5
    assert db.iloc[0, 0] == "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)"


def test_transform_missing_q(job_clusters):
    output = job_clusters.transform(missing_q_datablock)
    pprint.pprint(output)
    db = output.get("job_clusters")
    assert db["Totals"].sum() == 0
    assert db.shape[0] == 5
    assert db.iloc[0, 0] == "VO_Name=='cms' and RequestCpus==1 and (MaxWallTimeMins>0 and MaxWallTimeMins<= 60*12)"
