from argparse import ArgumentParser

from decisionengine_modules.glideinwms import configure_gwms_frontend
from decisionengine_modules.glideinwms.tests.fixtures import de_client_config  # noqa: F401


def test_get_arg_parser():
    parser = configure_gwms_frontend.get_arg_parser()
    assert isinstance(parser, ArgumentParser)


# TODO: This test requires the new GlideinWMS RPMs to be installed.
# def test_main():
#     args = Namespace()
#     args.web_base_dir = "/var/lib/gwms-frontend/web-base"
#     args.update_scripts = False
#     args.de_frontend_config = "/var/lib/gwms-frontend/vofrontend/de_frontend_config"
#     configure_gwms_frontend.main(args)
