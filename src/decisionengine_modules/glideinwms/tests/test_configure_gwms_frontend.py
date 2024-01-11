# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

import warnings

from argparse import ArgumentParser

# If using HTCondor without a configuration becomes important, we can
# put this warning filter in the pyproject.toml file.
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, module="htcondor")
    from decisionengine_modules.glideinwms import configure_gwms_frontend


def test_get_arg_parser():
    parser = configure_gwms_frontend.get_arg_parser()
    assert isinstance(parser, ArgumentParser)


# TODO: This test requires the new GlideinWMS RPMs to be installed.

# import os
# from types import SimpleNamespace
# from decisionengine.framework.config.policies import GLOBAL_CONFIG_FILENAME

# MOCK_CONFIG = """{
#     "glideinwms": {
#         "frontend_name": "mock_frontend",
#         "collectors": [
#             {
#                 "DN": "/DC=org/OU=HEPCloud/CN=mock_collector.hepcloud.org",
#                 "group": "default",
#                 "node": "localhost:9618",
#                 "secondary": "False"
#             }
#         ],
#         "groups": {
#             "main": {}
#         },
#         work: {
#             base_dir: '/var/lib/gwms-frontend/vofrontend',
#             base_log_dir: '/var/log/gwms-frontend',
#         },
#         stage: {
#             base_dir: '/var/lib/gwms-frontend/web-area/stage',
#             use_symlink: 'True',
#             web_base_url: 'http://localhost/vofrontend/stage',
#         },
#         monitor: {
#             base_dir: '/var/lib/gwms-frontend/web-area/monitor',
#             flot_dir: '/usr/share/javascriptrrd/flot',
#             javascriptRRD_dir: '/usr/share/javascriptrrd/js',
#             jquery_dir: '/usr/share/javascriptrrd/flot',
#         }
#     }
# }"""

# def test_main(tmp_path):
#     de_frontend_config = tmp_path / "de_frontend_config"
#     config_file = tmp_path / GLOBAL_CONFIG_FILENAME
#     config_file.write_text(MOCK_CONFIG)

#     os.environ["CONFIG_PATH"] = str(tmp_path)

#     args = SimpleNamespace()
#     args.web_base_dir = "/var/lib/gwms-frontend/web-base"
#     args.update_scripts = False
#     args.de_frontend_config = de_frontend_config
#     configure_gwms_frontend.main(args)

#     assert de_frontend_config.exists()
#     config = eval(de_frontend_config.read_text())
#     assert type(config) == dict
