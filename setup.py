#!/usr/bin/env python

# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

# Eventually this should move to pyproject.toml
#  but setuptools must first gain support for parsing that

import importlib
import pathlib
import site
import sys

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Add this module to the import path to help centralize metadata
sys.path.append(str(here) + "/src")
about = importlib.import_module("decisionengine_modules.about")

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# pull in runtime requirements
runtime_require = [
    "boto3 >= 1.17.10",
    "google_auth >= 1.16.0",
    "google-api-python-client >= 1.12.8",
    "gcs-oauth2-boto-plugin >= 2.7",
    "htcondor >= 9.0.0",
    "structlog >= 21.1.0",
    "requests >= 2.14.2",
    "urllib3 >= 1.26.2",
    "bill-calculator-hep >= 0.1.4",
    "numpy >= 1.19.5, < 2.0.0; python_version >= '3.7'",
    "pandas >= 1.5.3, < 2.0.0; python_version >= '3.7'",
    "qcs-api-client >= 0.21.1; python_version >= '3.7'",
    "authlib",
    "cryptography",
    "pem",
    "PyJWT",
]

# pull in development requirements
devel_req = [
    "pytest >= 7.0.0, < 8.0",
    "pytest-cov >= 2.11.1",
    "pytest-xdist[psutil] >= 2.3.0",
    "flake8 >= 6.0.0, < 7.0.0",
    "coverage >= 6.1.2",
    "tabulate >= 0.8.8",
    "toml >= 0.10.2",
    "pyyaml >= 5.4.1",
    "sphinx >= 3.5.3",
    "sphinx_rtd_theme >= 0.5.1",
    "packaging >= 20.9",
    "wheel >= 0.36.2",
    "pylint >= 2.7.4",
    "reuse >= 1.1.2",
    "importlib_resources >= 5.1.2; python_version <= '3.8'",
]

# workaround bug in editable install when PEP517 is detected
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

rpm_require = ["decisionengine", "glideinwms-vofrontend-libs", "glideinwms-vofrontend-glidein"]

__base_pip_requires = [
    f"python3.{sys.version_info.minor}dist(wheel)",
]
rpm_require.extend(__base_pip_requires)

# This metadata can be read out with:
#    import importlib.metadata
#    dir(importlib.metadata.metadata('decisionengine_modules'))
#  or
#    importlib_resources on python < 3.9
#
# Much of it comes out of decisionengine_modules.about.py
setup(
    setup_requires=["setuptools >= 51.2", "wheel >= 0.36.2", "setuptools_scm >= 6.3.1"],
    python_requires=">3.7.0",
    name=about.__title__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about.__url__,
    author=about.__author__,
    license=about.__license__,
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests", "*.tests", "*.tests.*", "build.*", "doc.*")),
    install_requires=runtime_require,
    extras_require={
        "develop": devel_req,
    },
    options={
        "bdist_rpm": {
            "build_requires": __base_pip_requires,
            "provides": ["python3-" + about.__title__, "decisionengine-standard-library"],
            "install_script": "package/rpm/install_section",
            "requires": rpm_require,
            "release": "1%{?dist}",
        },
    },
    zip_safe=True,
)
