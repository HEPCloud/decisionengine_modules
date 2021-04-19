"""
Compare jobs on factory and Nersc
"""

import pandas as pd

import logging
from decisionengine.framework.modules import Transform

@Transform.consumes(job_manifests=pd.DataFrame,
                    Nersc_Job_Info=pd.DataFrame)
@Transform.produces(nersc_factory_jobs_comparison=dict)
class CompareNerscFactoryJobs(Transform.Transform):
    """
    Transform that consumes nersc jobs and factory jobs data,
    and produces the comparison between them
    """

    def __init__(self, param_dict):
        self.logger = logging.getLogger()

    def transform(self, data_block):
        """
        Compare the job IDs between the jobs acquired from both sides. Output the
        comparison results, as # jobs in both, # jobs in factory/Nersc only, # jobs
        running on Nersc, and # jobs in factory without an ID.
        """
        nersc_df = data_block['Nersc_Job_Info']
        factory_df = data_block['job_manifests']

        # constrain factory jobs to only the batch slurm jobs
        factory_df = factory_df[factory_df.GridResource.str.startswith(
            'batch slurm')]

        results = {
            'both.count': 0,
            'nersc_only.count': 0,
            'factory_only.count': 0,
            'factory_no_ID.count': 0,
            'nersc.running.count': 0,
        }

        if factory_df.empty:
            if nersc_df.empty:
                # all four metrics stay '0'
                pass
            else:
                # both, factory_only, factory_no_ID stay '0'
                results['nersc_only.count'] = len(nersc_df)
                for index, row in nersc_df.iterrows():
                    result_key = 'nersc' + '.' + row['hostname'] + '.' + row['queue'] + \
                                 '.' + row['user'] + '.count'
                    if result_key in results:
                        results[result_key] += 1
                    else:
                        results[result_key] = 1
        else:
            # factory has jobs, process it
            num_no_id = 0
            num_with_id = 0
            factory_id_list = []

            for index, row in factory_df.iterrows():
                # four possibilities:
                #   the row does NOT have GridJobID
                #   the row has GridJobID set to be null/nan
                #   the row has GridJobID, but no real ID on Nersc
                #   the row has GridJObID, and a real ID on Nersc

                if 'GridJobID' not in row.axes[0].tolist():
                    num_no_id += 1
                elif pd.isnull(row.GridJobID):
                    num_no_id += 1
                else:
                    line = row['GridJobID'].split(' ')
                    if len(line) == 3:
                        num_no_id += 1
                        factory_df.loc[index, 'GridJobID'] = None
                    elif len(line) == 4:
                        num_with_id += 1
                        factory_df.loc[index,
                                       'GridJobID'] = line[-1].split('/')[-1]
                        factory_id_list.append(line[-1].split('/')[-1])

            #assert(num_no_id+num_with_id == len(factory_df))

            results['factory_no_ID.count'] = num_no_id

            if nersc_df.empty:
                if num_with_id == 0:
                    # both, nersc_only, and factory_only all stay '0'
                    pass
                else:
                    # both and nersc_only stay '0'
                    results['factory_only.count'] = num_with_id
            else:
                # nersc side has jobs
                # first send all nersc job details
                for index, row in nersc_df.iterrows():
                    result_key = 'nersc' + '.' + row['hostname'] + '.' + row['queue'] + '.'\
                                 + row['user'] + '.count'
                    if result_key in results:
                        results[result_key] += 1
                    else:
                        results[result_key] = 1
                if num_with_id == 0:
                    # both and factory_only stay '0'
                    results['factory_only.count'] = len(nersc_df)
                else:
                    # compare the exact job IDs
                    nersc_id_list = nersc_df.jobid.tolist()

                    factory_id_set = set(factory_id_list)
                    nersc_id_set = set(nersc_id_list)

                    in_both_set = factory_id_set & nersc_id_set
                    factory_only_set = factory_id_set - nersc_id_set
                    nersc_only_set = nersc_id_set - factory_id_set

                    num_in_both = len(in_both_set)
                    num_in_factory = len(factory_only_set)
                    num_in_nersc = len(nersc_only_set)

                    results['both.count'] = num_in_both
                    results['nersc_only.count'] = num_in_nersc
                    results['factory_only.count'] = num_in_factory

        for index, row in nersc_df.iterrows():
            if row['status'] == 'R':
                results['nersc.running.count'] += 1

        return {'nersc_factory_jobs_comparison': results}


Transform.describe(CompareNerscFactoryJobs)
