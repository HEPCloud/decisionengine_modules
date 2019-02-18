import os
import pytest
import mock
import pprint
import classad
import utils
from decisionengine_modules.htcondor import htcondor_query


config_cq = {
    'condor_config': 'condor_config',
    'pool_name': 'dummy_collector.fnal.gov, cmssrv274.fnal.gov',
    'schedd_name': 'hepcjobsub01.fnal.gov',
}

config_cs = {
    'condor_config': 'condor_config',
    'pool_name': 'dummy_collector.fnal.gov, cmssrv274.fnal.gov',
}

config_cq_bad = {
    'condor_config': 'condor_config',
    'pool_name': 'dummy_collector.fnal.gov, bad_collector.fnal.gov',
    'schedd_name': 'hepcjobsub01.fnal.gov',
}

config_cs_bad = {
    'condor_config': 'condor_config',
    'pool_name': 'dummy_collector.fnal.gov, bad_collector.fnal.gov',
}

class TestCondorQ:

    def test_condorq_live(self):
        if not os.environ.get('CONDOR_CONFIG'):
            os.environ['CONDOR_CONFIG'] = config_cq.get('condor_config')

        condor_q = htcondor_query.CondorQ(
            schedd_name=config_cq.get('schedd_name'),
            pool_name=config_cq.get('pool_name'))

        condor_q.load(constraint='procid < 2')
        #pprint.pprint(condor_q.stored_data)
        pprint.pprint('Fetched %s job classads from schedd %s in collector %s' % (len(condor_q.stored_data), config_cq.get('schedd_name'), config_cq.get('pool_name')))


    def test_condorq_queryerror(self):
        if not os.environ.get('CONDOR_CONFIG'):
            os.environ['CONDOR_CONFIG'] = config_cq_bad.get('condor_config')

        condor_q = htcondor_query.CondorQ(
            schedd_name=config_cq_bad.get('schedd_name'),
            pool_name=config_cq_bad.get('pool_name'))
        try:
            condor_q.load(constraint='procid < 2')
            assert False
        except htcondor_query.QueryError:
            assert True
        #pprint.pprint(condor_q.stored_data)


    def test_condorq(self):

        condor_q = htcondor_query.CondorQ(
            schedd_name=config_cq.get('schedd_name'),
            pool_name=config_cq.get('pool_name'))

        with mock.patch.object(htcondor_query.CondorQ, 'fetch') as f:
            f.return_value = utils.input_from_file('cq.fixture')
            condor_q.load()
            pprint.pprint('Fetched %s job classads' % len(condor_q.stored_data))


class TestCondorStatus:

    def test_condorstatus_live(self):
        if not os.environ.get('CONDOR_CONFIG'):
            os.environ['CONDOR_CONFIG'] = config_cs.get('condor_config')

        condor_status = htcondor_query.CondorStatus(
            pool_name=config_cs.get('pool_name'))

        condor_status.load()
        pprint.pprint('Fetched %s resource classads from collector %s' % (len(condor_status.stored_data), config_cs.get('pool_name')))


    def test_condorstatus_queryerror(self):
        if not os.environ.get('CONDOR_CONFIG'):
            os.environ['CONDOR_CONFIG'] = config_cs_bad.get('condor_config')

        condor_status = htcondor_query.CondorStatus(
            pool_name=config_cs_bad.get('pool_name'))

        try:
            condor_status.load()
            assert False
        except htcondor_query.QueryError:
           assert True


    def test_condorstatus(self):
        condor_status = htcondor_query.CondorStatus(
            subsystem_name='any',
            pool_name=config_cs.get('pool_name'))

        with mock.patch.object(htcondor_query.CondorStatus, 'fetch') as f:
            f.return_value = utils.input_from_file('cs.fixture')
            condor_status.load()
            #pprint.pprint(condor_status.stored_data)
            pprint.pprint('Fetched %s resource classads' % len(condor_status.stored_data))
