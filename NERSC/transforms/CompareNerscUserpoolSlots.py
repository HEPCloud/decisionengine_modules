#!/usr/bin/python
"""
Compare slots on Nersc and startd
"""
import argparse
import pprint
import logging

import logging
from decisionengine.framework.modules import Transform

CONSUMES = ['startd_manifests', 'Factory_Entries_LCF', 'Nersc_Job_Info']
PRODUCES = ['nersc_userpool_slots_comparison']

class CompareNerscUserpoolSlots(Transform.Transform):
    """
    Transform that consumes nersc slots and userpool slots as input,
    and produces the comparison between them
    """

    def __init__(self, param_dict):
        self.param_dict = param_dict
        self.entry_nersc_map = param_dict['entry_nersc_map']
        self.logger = logging.getLogger()

    def consumes(self):
        """
        Method to be called from Task Manager. Show the list of keys to consume.
        """
        return CONSUMES

    def produces(self):
        """
        Method to be called from Task Manager. Show the list of keys to produce.
        """
        return PRODUCES

    def transform(self, data_block):
        """
        Count the number of slots on startd, calculate the running slots on Nersc, and
        compare the two metrics. Also calculate the relative difference between them.
        """

        nersc_df = data_block['Nersc_Job_Info']
        userpool_slots_df = data_block['startd_manifests']
        factory_entry_df = data_block['Factory_Entries_LCF']

        # constrain userpool slots with only batch slurm
        userpool_slots_df = userpool_slots_df[userpool_slots_df['GLIDEIN_GridType'] == "batch slurm"]
        userpool_slots_df = userpool_slots_df[userpool_slots_df['SlotType'] == 'Partitionable']

        results = {}

        # construct mapping of entry_name: #cores per node
        cores_dict = {}

        for index, row in factory_entry_df.iterrows():
            cores_dict[row['EntryName']] = int(row['GLIDEIN_CPUS'])

        total_slots_nersc = 0

        for index, row in nersc_df.iterrows():
            if row['status'] == 'R':
                key = row['hostname']+row['queue']+row['user']
                entry_name = self.entry_nersc_map[key]
                if entry_name not in cores_dict:
                    logging.info("error: entry %s does NOT exist!" %(entry_name))
                else:
                    result_key = 'nersc'+'.'+row['hostname']+'.'\
                                 +row['queue']+'.'+row['user']+'.count'
                    if result_key in results:
                        results[result_key] += (cores_dict[entry_name]*int(row['nodes']))
                    else:
                        results[result_key] = (cores_dict[entry_name]*int(row['nodes']))
                    total_slots_nersc += (cores_dict[entry_name]*int(row['nodes']))

        logging.info("total number of slots on Nersc = " + str(total_slots_nersc))

        # pull slot info from User pool ########

        total_slots_userpool = 0
        for index, row in userpool_slots_df.iterrows():
            total_slots_userpool += int(row['TotalCpus'])

        logging.info("total number of slots on userpool = " + str(total_slots_userpool))

        # compute the relative difference between the two metrics ###
        rel_diff = 0.0
        diff = abs(total_slots_userpool - total_slots_nersc)
        if diff != 0:
            more = max(total_slots_nersc, total_slots_userpool)
            rel_diff = diff / more

        logging.info("diff = %f, rel diff = %f" %(diff, rel_diff))

        # construct the result namespace ############################
        results['nersc.count'] = total_slots_nersc
        results['userpool.count'] = total_slots_userpool
        results['relative_diff'] = rel_diff

        return {PRODUCES[0]: results}

def module_config_template():
    """
    Print template for this module configuration
    """
    template = {
        'nersc_userpool_slots_comparison': {
            'module': 'modules.NERSC.transforms.compare_nersc_userpool_slots',
            'name': 'CompareNerscUserpoolSlots',
            'parameters': {
                'entry_nersc_map': 'map <jobs on nersc, entry name>'
            }
        }
    }
    print 'Entry in channel configuration'
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print 'produces %s' % PRODUCES
    module_config_template()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--configtemplate',
        action='store_true',
        help='prints the expected module configuration')

    parser.add_argument(
        '--configinfo',
        action='store_true',
        help='prints config template along with produces and consumes info')
    args = parser.parse_args()

    if args.configtemplate:
        module_config_template()
    elif args.configinfo:
        module_config_info()
    else:
        pass


if __name__ == '__main__':
    main()
