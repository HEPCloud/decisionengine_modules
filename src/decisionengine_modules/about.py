# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

"""
    PEP-0396 provides instructions for providing module versions
    While we are at it, add a few other useful bits
"""
try:
    # This is built by setuptools_scm
    from .version import version as __version__  # noqa: F401
except ImportError:
    __version__ = "1.7.0rc"

__title__ = "decisionengine_modules"
__description__ = "The HEPCloud Decision Engine Framework"
__author__ = "Fermi Research Alliance LLC"
__license__ = "Fermitools Software Legal Information (Modified BSD License)"
__url__ = "http://hepcloud.fnal.gov"
