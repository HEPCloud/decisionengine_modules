# SPDX-FileCopyrightText: 2022 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Get allocation info from Rigetti
"""
from pathlib import Path

import httpx  # just for the typing information
import pandas as pd
import qcs_api_client.models as qcs_models
import qcs_api_client.operations.sync as qcs_sync_operations

from qcs_api_client.client import build_sync_client, QCSClientConfiguration

from decisionengine.framework.modules import Source
from decisionengine.framework.modules.Source import Parameter

QCS_BASE_PATH = Path("~/.qcs").expanduser()

DEFAULT_SECRETS_FILE_PATH = QCS_BASE_PATH / "secrets.toml"
DEFAULT_SETTINGS_FILE_PATH = QCS_BASE_PATH / "settings.toml"

__all__ = [
    "RigettiBalance",
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
)
@Source.produces(Rigetti_Balance=pd.DataFrame)
class RigettiBalance(Source.Source):
    """
    Billing status for the Rigetti systems
    """

    def __init__(self, config):
        """
        Read in our toml files and build a client we can use
        """
        super().__init__(config)

        self.constraints = config.get("constraints")
        if not isinstance(self.constraints, dict):
            raise RuntimeError("constraints should be a dict")

        self.qcs_config: QCSClientConfiguration = QCSClientConfiguration.load(
            profile_name=config.get("qcs_profile_name"),
            secrets_file_path=config.get("qcs_secrets_file_path"),
            settings_file_path=config.get("qcs_settings_file_path"),
        )

    def acquire(self):
        """
        Method to be called from Task Manager.
        redefines acquire from Source.py.
        Acquire Regetti balance info and return as pandas frame

        Returns:
          dict: A dictionary with a obj:`~pd.DataFrame` containing Rigetti credits remaining
        """
        self.logger.debug("in RigettiBalance acquire")
        result = {}
        with build_sync_client(configuration=self.qcs_config) as qcs_client:
            qcs_client: httpx.Client
            user: qcs_models.user.User = qcs_sync_operations.auth_get_user(client=qcs_client).parsed
            balance: qcs_models.account_balance.AccountBalance = qcs_sync_operations.get_user_balance(
                user_id=user.idp_id, client=qcs_client
            ).parsed
            result[user.profile.email] = {}
            result[user.profile.email]["account_info"] = user.to_dict()
            result[user.profile.email]["account"] = balance.to_dict()

            # result looks something like:
            # {'riehecky@fnal.gov': {'account_info': {'createdTime': '2022-04-02T14:58:09+00:00', 'id': 8888, 'idpId': '00uh3y44je4e2voe0357', 'profile': {'email': 'riehecky@fnal.gov', 'firstName': 'Pat', 'lastName': 'Riehecky', 'organization': 'Fermilab'}}, 'account': {'balance': -1200000}}}
        return {"Regetti_Balance": pd.DataFrame(result)}


Source.describe(RigettiBalance)
