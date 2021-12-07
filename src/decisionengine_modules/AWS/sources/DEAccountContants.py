# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
This data is taken from billing and arranged as dictionary of
AccountConstants instead of separate class for each billing class.
This way is more covenient to use in programms.
"""

EXPECTED_NAMES = [
    "accountName",
    "accountNumber",
    "credentialsProfileName",
    "bucketBillingName",
    "lastKnownBillDate",
    "balanceAtDate",
    "costRatePerHourInLastSixHoursAlarmThreshold",
    "costRatePerHourInLastDayAlarmThreshold",
    "applyDiscount",
    "emailReceipientForAlarms",
    "projectId",
]


class AccountConstants:
    def __init__(self, constants=None):

        # Initialize variables
        for k in EXPECTED_NAMES:
            setattr(self, k, None)
        # Set variables
        if constants:
            for k, val in constants.items():
                if k in EXPECTED_NAMES:
                    setattr(self, k, val)

    def __repr__(self):
        return f"{self.accountName} {self.accountNumber} {self.credentialsProfileName} {self.lastKnownBillDate} {self.balanceAtDate} {self.applyDiscount} {self.costRatePerHourInLastSixHoursAlarmThreshold} {self.costRatePerHourInLastDayAlarmThreshold} {self.emailReceipientForAlarms}"

    def info(self):
        for name in EXPECTED_NAMES:
            attr = getattr(self, name)
            print(name, attr, type(attr))


def load_constants(constants_file):
    """
    Load constants from file.

    :type constants_file: :obj:`file`
    :arg constants_file: configuration file as python dict

    :rtype: :obj:`AccountConstants`

    """

    config_dict = None
    with open(constants_file) as f:
        config_dict = eval(f.read())
    return config_dict
