.. SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
.. SPDX-License-Identifier: Apache-2.0

Release 1.5.0
-------------

In this release:

* New AWS bill calculator
* Bug fixes

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `271 <https://github.com/HEPCloud/decisionengine_modules/issues/271>`_ : Change configuration so the bill-calculator-hep-mapsacosta library doesn't write stuff to stdout (`5410c46 <https://github.com/HEPCloud/decisionengine_modules/commit/5410c46330ad6ce48654c360f1b1cfc7cb05895c>`_)

- `283 <https://github.com/HEPCloud/decisionengine_modules/issues/283>`_ : Change DEAccountConstants.py to allow more variables through (`7a65032 <https://github.com/HEPCloud/decisionengine_modules/commit/7a650322a3aa7480be4cbb5419e4a07d71dd495d>`_)

- `293 <https://github.com/HEPCloud/decisionengine_modules/issues/293>`_ : Unit test tests/test_job_q.py is failing (`f5006fb <https://github.com/HEPCloud/decisionengine_modules/commit/f5006fb30ad3ae74b2192cbedf0d0245bff038d4>`_)

- `263 <https://github.com/HEPCloud/decisionengine_modules/issues/263>`_ : Python3 encodes hex strings differently, resulting in malformed htcondor classads (`c16f0 <https://github.com/HEPCloud/decisionengine_modules/commit/c16f0acc5e4607c0c8424ae6112572845f96e89c>`_)

- `289 <https://github.com/HEPCloud/decisionengine_modules/issues/289>`_ : Travis CI fails after decisionenigine transitioned to pybind11 (`2bec1da <https://github.com/HEPCloud/decisionengine_modules/commit/2bec1da203da5ec3d2cbecc33925a924bdd8e724>`_)
- `281 <https://github.com/HEPCloud/decisionengine_modules/issues/281>`_ : New exception in NERSC newt get_usage (`398dc42 <https://github.com/HEPCloud/decisionengine_modules/commit/398dc421ded5b7789340d5fbe71f4af5b352a8e3>`_)



Full list of commits since version 1.4.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


`5410c46 <https://github.com/HEPCloud/decisionengine_modules/commit/5410c46330ad6ce48654c360f1b1cfc7cb05895c>`_ : new bill calculator package (#303)

`7a65032 <https://github.com/HEPCloud/decisionengine_modules/commit/7a650322a3aa7480be4cbb5419e4a07d71dd495d>`_ : Resolving issue 283 (#301)


`1a2c3e4 <https://github.com/HEPCloud/decisionengine_modules/commit/1a2c3e4f57e60925dc374f386d8bca3ba9fa3e7e>`_
:   Fix syntax errors and pylint bits (#300)

`976c4a4 <https://github.com/HEPCloud/decisionengine_modules/commit/976c4a43ffd3a8e1d13df42a1a3d6f71d3be0fd7>`_
:   Minor linting of actions (#297)

`c43f311 <https://github.com/HEPCloud/decisionengine_modules/commit/c43f31163691e2c0e6e4782940499ed8fce8ae89>`_
:   Drop redundant action, pep8speaks is already doing this (#296)

`10691e4 <https://github.com/HEPCloud/decisionengine_modules/commit/10691e4a96141f9e412bbf26120f86fae9d3a8c6>`_
:   Add support to use custom docker layer as base of the docker image (#295)

`f5006fb <https://github.com/HEPCloud/decisionengine_modules/commit/f5006fb30ad3ae74b2192cbedf0d0245bff038d4>`_
:   fix for unit test test_job_q issue 293 (#294)

`0b588ef <https://github.com/HEPCloud/decisionengine_modules/commit/0b588efbd5f3034a827f9a72bed6ad8518d5c061>`_
:   Update workflow per changes at github (#292)

`7841d19 <https://github.com/HEPCloud/decisionengine_modules/commit/7841d198b7f5ad9068f10bf2842f203dc7e95188>`_
:   Updated Jenkins configuration documentation (#291)

`c08ffce <https://github.com/HEPCloud/decisionengine_modules/commit/c08ffce3b3499acb785f7c8f2ce4ff353c559f60>`_
:   edited release notes

`c16f0ac <https://github.com/HEPCloud/decisionengine_modules/commit/c16f0acc5e4607c0c8424ae6112572845f96e89c>`_
:   Another fix to malformed strings (#288)

`2bec1da <https://github.com/HEPCloud/decisionengine_modules/commit/2bec1da203da5ec3d2cbecc33925a924bdd8e724>`_
:   Fix #289 where TravisCI is missing changes from https://github.com/HEPCloud/decisionengine/commit/ea7ade57ca825afb0afbfa5ebd49820b16786d8b (#290)

`8647bb2 <https://github.com/HEPCloud/decisionengine_modules/commit/8647bb2bfaf89bf99589b7820ed422a9ad378e92>`_
:   Update to current python test matrix (#287)

`234a78e <https://github.com/HEPCloud/decisionengine_modules/commit/234a78eb57f0f67ade6d112a20a27649448b55c6>`_
:   update release notes

`398dc42 <https://github.com/HEPCloud/decisionengine_modules/commit/398dc421ded5b7789340d5fbe71f4af5b352a8e3>`_
:   decisionengine_modules/NERSC/util:  Added more 5xx codes to retry (#285)

`d2df861 <https://github.com/HEPCloud/decisionengine_modules/commit/d2df8610f9c12edf6b142c164a10ba2372bb4848>`_
:   force docker pull when building the docker container to make sure to use an updated base layer (#280)

`9a78d22 <https://github.com/HEPCloud/decisionengine_modules/commit/9a78d22817ae7d757b8448a874d90a38aa9e13b1>`_
:   added 1.4.0 release notes

`5d3b7ec <https://github.com/HEPCloud/decisionengine_modules/commit/5d3b7ec3da7361139b6662f081341502cdbab371>`_
:   Updating Dockerfile for unittest (#279)

`e16531e <https://github.com/HEPCloud/decisionengine_modules/commit/e16531e23e871ca91baf364d3eb600144d99c281>`_
:   Provide default for util function. (#278)

`02f1738 <https://github.com/HEPCloud/decisionengine_modules/commit/02f17389c8bdd58e8b41821d8c0137e8147aa1c7>`_
:   set RPM version number to 1.5.0rc and drop py3 suffix (#277)

`664b9fe <https://github.com/HEPCloud/decisionengine_modules/commit/664b9fe0d5eaeb3c3409dc38962b5c84c0d9d0b5>`_
:   Add timeout support for unit test on Jenkins for DE modules repo (#274)

`e392a3c <https://github.com/HEPCloud/decisionengine_modules/commit/e392a3c5a39a79ebac6ff8d64cb202085e5ecf16>`_
:   Added initial unit test for glide_frontend_element.py (#269)

`2f0069f <https://github.com/HEPCloud/decisionengine_modules/commit/2f0069f3855b2568f0c390ada5ad93d8fcdabfe7>`_
:   Updated DE modules Jenkins documentation
