import os
import argparse
import pprint
import pandas
import numpy

from decisionengine_modules.htcondor.sources import source
from glideinwms.frontend import glideinFrontendConfig


PRODUCES = ['gwms_fe_config']


class FrontendConfiguration():

    def __init__(self, config):
        if not config:
            config = {}
        if not isinstance(config, dict):
            raise RuntimeError('parameters for module config should be a dict')

        self.frontend_workdir = config.get('frontend_workdir', '/var/lib/gwms-frontend/vofrontend')

        glideinFrontendConfig.frontendConfig.frontend_descript_file = os.path.join(self.frontend_workdir, glideinFrontendConfig.frontendConfig.frontend_descript_file)
        self.frontend_descript = glideinFrontendConfig.FrontendDescript(self.frontend_workdir)
        self.groups = self.frontend_descript.data['Groups'].split(',')
        self.groups.sort()
        self.group_descript = {}
        self.group_params_descript = {}
        self.group_sign_descript = {}
        self.group_attrs_descript = {}

        self.frontend_config = {'frontend': {}, 'group': {}}
        self.frontend_config['frontend'] = {
            'frontend_name': self.frontend_descript.data['FrontendName'],
            'workdir': self.frontend_workdir,
            'web_url': self.frontend_descript.data['WebURL'],
            'monitoring_web_url': self.frontend_descript.data['MonitoringWebURL'],
        }

        for g in self.groups:
            self.group_descript[g] = glideinFrontendConfig.ElementMergedDescript(self.frontend_workdir, g)
            self.group_params_descript[g] = glideinFrontendConfig.ParamsDescript(self.frontend_workdir, g)
            self.group_sign_descript[g] = glideinFrontendConfig.GroupSignatureDescript(self.frontend_workdir, g)
            self.group_attrs_descript[g] = glideinFrontendConfig.AttrsDescript(self.frontend_workdir, g)

            self.frontend_config['group'][g] = {
                'workdir': glideinFrontendConfig.get_group_dir(self.frontend_workdir, g),
                'web_url': os.path.join(self.frontend_descript.data['WebURL'], 'group_%s' % g),
                'security_name': self.group_descript[g].merged_data['SecurityName'],
                'factory_collectors': self.group_descript[g].merged_data['FactoryCollectors'],
                'min_running': self.group_descript[g].element_data['MinRunningPerEntry'],
                'max_running': self.group_descript[g].element_data['MaxRunningPerEntry'],
                'fraction_running': float(self.group_descript[g].element_data['FracRunningPerEntry']),
                'max_idle': int(self.group_descript[g].element_data['MaxIdlePerEntry']),
                'reserve_idle': int(self.group_descript[g].element_data['ReserveIdlePerEntry']),
                #'idle_lifetime': int(self.group_descript[g].element_data['IdleLifetime']),
                'max_vms_idle': int(self.group_descript[g].element_data['MaxIdleVMsPerEntry']),
                'curb_vms_idle': int(self.group_descript[g].element_data['CurbIdleVMsPerEntry']),
                'total_max_glideins': int(self.group_descript[g].element_data['MaxRunningTotal']),
                'total_curb_glideins': int(self.group_descript[g].element_data['CurbRunningTotal']),
                'total_max_vms_idle': int(self.group_descript[g].element_data['MaxIdleVMsTotal']),
                'total_curb_vms_idle': int(self.group_descript[g].element_data['CurbIdleVMsTotal']),
                'fe_total_max_glideins': int(self.group_descript[g].frontend_data['MaxRunningTotal']),
                'fe_total_curb_glideins': int(self.group_descript[g].frontend_data['CurbRunningTotal']),
                'fe_total_max_vms_idle': int(self.group_descript[g].frontend_data['MaxIdleVMsTotal']),
                'fe_total_curb_vms_idle': int(self.group_descript[g].frontend_data['CurbIdleVMsTotal']),
                'global_total_max_glideins': int(self.group_descript[g].frontend_data['MaxRunningTotalGlobal']),
                'global_total_curb_glideins': int(self.group_descript[g].frontend_data['CurbRunningTotalGlobal']),
                'global_total_max_vms_idle': int(self.group_descript[g].frontend_data['MaxIdleVMsTotalGlobal']),
                'global_total_curb_vms_idle': int(self.group_descript[g].frontend_data['CurbIdleVMsTotalGlobal']),
                'max_matchmakers': int(self.group_descript[g].element_data['MaxMatchmakers']),
                'proxies': self.group_descript[g].merged_data['Proxies'],
                'proxy_selection_plugin': self.group_descript[g].merged_data['ProxySelectionPlugin'],
                'condor_config': self.group_descript[g].frontend_data['CondorConfig'],
                'condor_mapfile': self.group_descript[g].element_data['MapFile'],
                'classad_proxy': self.group_descript[g].frontend_data['ClassAdProxy'],
                'schedds': self.group_descript[g].merged_data['JobSchedds'],
                'sign_descript': {
                    'frontend_descript_fname': self.group_sign_descript[g].frontend_descript_fname,
                    'group_descript_fname': self.group_sign_descript[g].group_descript_fname,
                    'signature_type': self.group_sign_descript[g].signature_type,
                    'frontend_descript_signature': self.group_sign_descript[g].frontend_descript_signature,
                    'group_descript_signature': self.group_sign_descript[g].group_descript_signature,
                }
            }
            self.get_proxy_descript_data(g)


    def get_proxy_descript_data(self, group):
        proxy_list = self.group_descript[group].merged_data['Proxies']
        proxy_descript_attrs = [
            'ProxySecurityClasses', 'ProxyTrustDomains', 'ProxyTypes',
            'ProxyKeyFiles', 'ProxyPilotFiles',
            'ProxyVMIds', 'ProxyVMTypes', 'ProxyVMIdFname', 'ProxyVMTypeFname',
            'ProxyCreationScripts', 'ProxyUpdateFrequency',
            'ProxyRemoteUsernames', 'ProxyProjectIds']

        for attr in proxy_descript_attrs:
            proxy_descript_data = {}
            for data in (self.frontend_descript.data, self.group_descript[group].element_data):
                if attr in data:
                    dprs = eval(data[attr])
                    for k in dprs.keys():
                        proxy_descript_data[k] = dprs[k]
            self.frontend_config['group'][group][attr] = proxy_descript_data


    def produces(self):
        """
        Return list of items produced
        """
        return PRODUCES


    def acquire(self):
        return {PRODUCES[0]: self.frontend_config}


def module_config_template():
    """
    Print template for this module configuration
    """

    template = {
        'factoryglobal_manifests': {
            'module': 'modules.htcondor.s_factory_client',
            'name': 'StartdManifests',
            'parameters': {
                'frontend_workdir': 'path to glideinwms frontend workdir (DEFAULT: /var/lib/gwms-frontend/vofrontend)'
            }
        }
    }
    print('Entry in channel configuration')
    pprint.pprint(template)


def module_config_info():
    """
    Print module information
    """
    print('produces %s' % PRODUCES)
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
