import contextlib
import os

import pytest

# Test for the presence of modules used in glide_frontend_element
# Not testing all imports of glide_frontend_element which are
# from glideinwms.frontend import glideinFrontendConfig
# from glideinwms.frontend import glideinFrontendInterface
# from glideinwms.frontend import glideinFrontendPlugins
# from glideinwms.lib import pubCrypto
# Using a simple one, assuming that is glideinwms is in the PYTHONPATH,
# all modules are

gwms_modules_available = True
try:
    from glideinwms.lib import glideinWMSVersion
except ImportError:
    glideinWMSVersion = None
    gwms_modules_available = False

gwms_modules_python3 = False
if gwms_modules_available and glideinWMSVersion is not None:
    with contextlib.suppress(Exception):
        # Assuming no Python 3 glideinwms if something goes wrong
        with open(glideinWMSVersion.__file__) as fd:
            line = fd.readline()
            gwms_modules_python3 = "python3" in line


def test_glideinwms_import():
    assert gwms_modules_available, "glideinwms package is required"


@pytest.mark.skipif(not gwms_modules_available, reason="Python version of glideinwms cannot be tested w/o glideinwms")
def test_glideinwms_python3():
    assert gwms_modules_python3, "a Python3 version of glideinwms is required"


FRONTEND_CFG = {
    "frontend": {
        "frontend_name": "hepcsvc00-fnal-gov_hepcloud_decisionengine",
        "monitoring_web_url": "http://hepcsvc00.fnal.gov:8319/vofrontend/monitor",
        "web_url": "http://hepcsvc00.fnal.gov:8319/vofrontend/stage",
        "workdir": "/var/lib/gwms-frontend/vofrontend",
    },
    "group": {
        "cms": {
            "ProxyCreationScripts": {},
            "ProxyKeyFiles": {
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "/etc/gwms-frontend/credentials/hepcloud_fermilab_secretkey"
            },
            "ProxyPilotFiles": {
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "/etc/gwms-frontend/proxies/cloud_proxy"
            },
            "ProxyProjectIds": {"/etc/gwms-frontend/proxies/cms_proxy": "unb000"},
            "ProxyRemoteUsernames": {},
            "ProxySecurityClasses": {
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "frontend",
                "/etc/gwms-frontend/proxies/cms_proxy": "frontend",
            },
            "ProxyTrustDomains": {
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "HEPCloud_AWS_us-east-1",
                "/etc/gwms-frontend/proxies/cms_proxy": "grid",
            },
            "ProxyTypes": {
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "key_pair+vm_id",
                "/etc/gwms-frontend/proxies/cms_proxy": "grid_proxy+project_id",
            },
            "ProxyUpdateFrequency": {},
            "ProxyVMIdFname": {},
            "ProxyVMIds": {"/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey": "ami-00000000000"},
            "ProxyVMTypeFname": {},
            "ProxyVMTypes": {},
            "classad_proxy": "/etc/gwms-frontend/proxies/fe_proxy",
            "condor_config": "/var/lib/gwms-frontend/vofrontend/frontend.condor_config",
            "condor_mapfile": "/var/lib/gwms-frontend/vofrontend/group_cms_all/group.mapfile",
            "curb_vms_idle": 4500,
            "factory_collectors": [
                ("cmssrv200.fnal.gov", "gfactory@cmssrv200.fnal.gov", "hepcloudsvc00@cmssrv200.fnal.gov")
            ],
            "fe_total_curb_glideins": 167000,
            "fe_total_curb_vms_idle": 25000,
            "fe_total_max_glideins": 170000,
            "fe_total_max_vms_idle": 35000,
            "fraction_running": 3.0,
            "global_total_curb_glideins": 167000,
            "global_total_curb_vms_idle": 25000,
            "global_total_max_glideins": 170000,
            "global_total_max_vms_idle": 35000,
            "max_idle": 12800,
            "max_matchmakers": 3,
            "max_running": "40000",
            "max_vms_idle": 5000,
            "min_running": "0",
            "proxies": [
                "/etc/gwms-frontend/proxies/cms_proxy",
                "/etc/gwms-frontend/credentials/hepcloud_fermilab_accesskey",
            ],
            "proxy_selection_plugin": "ProxyAll",
            "reserve_idle": 100,
            "schedds": ["cmssrv270.fnal.gov", "cmssrv277.fnal.gov"],
            "security_name": "hepcloudsvc00",
            "sign_descript": {
                "frontend_descript_fname": "description.000000.cfg",
                "frontend_descript_signature": "123000000000a000000000a000000000",
                "group_descript_fname": "description.000000.cfg",
                "group_descript_signature": "321000000000a000000000a000000000",
                "signature_type": "sha1",
            },
            "total_curb_glideins": 39000,
            "total_curb_vms_idle": 39000,
            "total_max_glideins": 40000,
            "total_max_vms_idle": 40000,
            "web_url": "http://hepcsvc00.fnal.gov:8319/vofrontend/stage/group_cms",
            "workdir": "/var/lib/gwms-frontend/vofrontend/group_cms",
        }
    },
}


@pytest.mark.skipif(
    not gwms_modules_available or not gwms_modules_python3,
    reason="glide_frontend_element cannot be tested w/o Python 3 glideinwms",
)
class TestGlideFrontendElement:
    if gwms_modules_available and gwms_modules_python3:
        from decisionengine_modules.glideinwms import glide_frontend_element

    @staticmethod
    def read_fe_config(fpath):
        # to read the configuration in form a fixture file
        if not os.path.isfile(fpath):
            raise RuntimeError(
                f"Error reading Frontend config for DE {fpath}. "
                "Run configure_gwms_frontend.py to generate one and after every change to the frontend configuration."
            )
        with open(fpath) as _fd:
            fe_cfg = eval(_fd.read())
        if not isinstance(fe_cfg, dict):
            raise ValueError(f"Frontend config for DE in {fpath} is invalid")
        return fe_cfg

    def test_compute_glidein_max_running(self):
        # fe_cfg = self.read_fe_config("de_frontend_config")
        fe_cfg = FRONTEND_CFG
        gfe = self.glide_frontend_element.get_gfe_obj("CMS", "CMS", fe_cfg, "glideinwms")
        gfe.entry_fraction_glidein_running = 1.15
        assert gfe.compute_glidein_max_running({"Idle": 412}, 971, 0) == 1591
        assert gfe.compute_glidein_max_running({"Idle": 100}, 100, 0) == 230
        assert gfe.compute_glidein_max_running({"Idle": 100}, 0, 0) == 115
        assert gfe.compute_glidein_max_running({"Idle": 0}, 0, 0) == 0
        assert gfe.compute_glidein_max_running({"Idle": 0}, 100, 100) == 100
