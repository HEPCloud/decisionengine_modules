#!/usr/bin/env python
"""
Fill in data from Job limits csv file
"""
import pandas as pd

import decisionengine_modules.AWS.sources.AWSJobLimits as AWSJobLimits

config = {'data_file':'job_limits_sample.csv'}

expected_pandas_df = pd.read_csv(config.get("data_file")).drop_duplicates(subset=['AvailabilityZone', 'InstanceType'], keep='last').reset_index(drop=True)
produces = ['Job_Limits']

class TestAWSJobLimits:

    def test_produces(self):
        aws_job_limits = AWSJobLimits.AWSJobLimits(config)
        assert aws_job_limits.produces() == produces

    def test_acquire(self):
        aws_job_limits = AWSJobLimits.AWSJobLimits(config)
        res = aws_job_limits.acquire()
        assert produces == res.keys()
        assert expected_pandas_df.equals(res.get(produces[0]))
