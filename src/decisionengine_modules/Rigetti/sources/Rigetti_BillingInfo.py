# SPDX-FileCopyrightText: 2022 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Get billing info from Rigetti
"""
from pathlib import Path

import pandas as pd

from qcs_api_client.client import QCSClientConfiguration

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

QCS_BASE_PATH = Path("~/.qcs").expanduser()

DEFAULT_SECRETS_FILE_PATH = QCS_BASE_PATH / "secrets.toml"
DEFAULT_SETTINGS_FILE_PATH = QCS_BASE_PATH / "settings.toml"

__all__ = [
    "RigettiBillingInfo",
]


@Source.supports_config(
    Parameter(
        "constraints",
        type=dict,
        comment="""Supports the layout:
  {
     'qcs_profile_name': 'default',
     'qcs_secrets_file_path': '/home/decisionengine/.qcs/secrets.toml',
     'qcs_settings_file_path': '/home/decisionengine/.qcs/settings.toml',

     'qcs_default_credits_per_second_for_reservation': 1,
     'qcs_default_credits_per_second_for_ondemand': 1,
  }
""",
    ),
    Parameter("qcs_profile_name", type=str, default="default"),
    Parameter(
        "qcs_secrets_file_path",
        type=str,
        default=DEFAULT_SECRETS_FILE_PATH,
        comment="Path to QCS generated secrets file",
    ),
    Parameter(
        "qcs_settings_file_path",
        type=str,
        default=DEFAULT_SETTINGS_FILE_PATH,
        comment="Path to QCS generated settings file",
    ),
    Parameter(
        "qcs_default_credits_per_second_for_reservation",
        type=int,
        default=0,
        comment="How many credits are consumed per second of QPU reservation scheduling (default)",
    ),
    Parameter(
        "qcs_default_credits_per_second_for_ondemand",
        type=int,
        default=0,
        comment="How many credits are consumed per second of QPU on demand scheduling (default)",
    ),
)
@Source.produces(Rigetti_BillingInfo=pd.DataFrame)
class RigettiBillingInfo(Source.Source):
    """
    Billing costs for the Rigetti systems
    """

    def __init__(self, config, logger):
        """
        Read in our toml files and build a client we can use
        """
        super().__init__(config, logger)

        self.constraints = config.get("constraints")
        if not isinstance(self.constraints, dict):
            raise RuntimeError("constraints should be a dict")

        self.qcs_config: QCSClientConfiguration = QCSClientConfiguration.load(
            profile_name=config.get("qcs_profile_name"),
            secrets_file_path=config.get("qcs_secrets_file_path"),
            settings_file_path=config.get("qcs_settings_file_path"),
        )

        self.qcs_credits_per_second_for_reservation = config.get("qcs_default_credits_per_second_for_reservation")
        self.qcs_credits_per_second_for_ondemand = config.get("qcs_default_credits_per_second_for_ondemand")

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py.
        Acquire Regetti costs and return as pandas frame

        Returns:
          dict: A dictionary with a obj:`~pd.DataFrame` containing Rigetti costs
        """
        self.logger.debug("in RigettiBillingInfo acquire")
        result = {}

        # It would be nice if this was something I could check via the API,
        # but today that is not the case.
        result["qcs_credits_per_second_for_reservation"] = self.qcs_credits_per_second_for_reservation
        result["qcs_credits_per_second_for_ondemand"] = self.qcs_credits_per_second_for_ondemand
        return {"Rigetti_BillingInfo": pd.DataFrame(result)}


Source.describe(RigettiBillingInfo)
