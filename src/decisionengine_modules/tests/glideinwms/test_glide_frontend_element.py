# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import contextlib
import os
import tempfile

from unittest import mock

import pytest
import structlog

from glideinwms.lib import token_util

from decisionengine_modules.glideinwms import glide_frontend_element

# Test for the presence of modules used in glide_frontend_element
# Not testing all imports of glide_frontend_element which are
# from glideinwms.frontend import glideinFrontendConfig
# from glideinwms.frontend import glideinFrontendInterface
# from glideinwms.frontend import glideinFrontendPlugins
# from glideinwms.lib import pubCrypto
# Using a simple one, assuming that is glideinwms is in the PYTHONPATH,
# all modules are

glideinWMSVersion = pytest.importorskip("glideinwms.lib.glideinWMSVersion")

gwms_modules_python3 = False
with contextlib.suppress(Exception):
    # Assuming no Python 3 glideinwms if something goes wrong
    with open(glideinWMSVersion.__file__) as fd:
        line = fd.readline()
        gwms_modules_python3 = "python3" in line

if not gwms_modules_python3:
    pytest.skip("A Python3 version of glideinwms is required", allow_module_level=True)


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


def test_compute_glidein_max_running():
    fe_cfg = FRONTEND_CFG
    gfe = glide_frontend_element.get_gfe_obj("CMS", "CMS", fe_cfg, "glideinwms")
    gfe.entry_fraction_glidein_running = 1.15
    assert gfe.compute_glidein_max_running({"Idle": 412}, 971, 0) == 1591
    assert gfe.compute_glidein_max_running({"Idle": 100}, 100, 0) == 230
    assert gfe.compute_glidein_max_running({"Idle": 100}, 0, 0) == 115
    assert gfe.compute_glidein_max_running({"Idle": 0}, 0, 0) == 0
    assert gfe.compute_glidein_max_running({"Idle": 0}, 100, 100) == 100


def test_refresh_entry_token():
    with tempfile.TemporaryDirectory() as work_dir:
        os.mkdir(os.path.join(work_dir, "passwords.d"))
        with open(os.path.join(work_dir, "passwords.d", "FRONTEND"), "wb") as fd:
            fd.write(token_util.derive_master_key(b"TEST"))

        create_and_sign_token = token_util.create_and_sign_token
        with mock.patch.object(token_util, "create_and_sign_token") as create_token:
            create_token.side_effect = lambda *args, **kwargs: create_and_sign_token(
                *args, **kwargs, issuer="fermicloud000.fnal.gov:0000"
            )

            gfe = glide_frontend_element.get_gfe_obj("CMS", "CMS", FRONTEND_CFG, structlog.getLogger("test"))
            token = gfe.refresh_entry_token("test_entry", work_dir)

            assert token
            assert not token_util.token_str_expired(token)
