.. SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
.. SPDX-License-Identifier: Apache-2.0

Release 1.7.5
-------------

Added support for NERSC SuperFacility API.

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~

- `234 <https://github.com/HEPCloud/decisionengine_modules/issues/234>`_ : Prepare code for new NERSC "superfacility" api

Full list of commits since version 1.7.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`a85098a <https://github.com/HEPCloud/decisionengine_modules/commit/a85098abced97945f364ec729695d7ae319e9a90>`_:   Last update to add KeyError

`defb011 <https://github.com/HEPCloud/decisionengine_modules/commit/defb0116eb968fc4875bcf2991f4af154e0e0d6c>`_:   New Nersc SuperFacility code in the branch 1.7

`83e6b88 <https://github.com/HEPCloud/decisionengine_modules/commit/83e6b88db6012e9fd60f3115f8db2b4db5fc79ea>`_:   Updated release notes for 1.7.4


Release 1.7.4
-------------

This release fixes token+proxy hybrid configuration.

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `428 <https://github.com/HEPCloud/decisionengine_modules/issues/428>`_ : Decision engine 1.7.3 bug too many open file descriptors in glide_frontend_element.py
- `434 <https://github.com/HEPCloud/decisionengine_modules/pull/434>`_ : Set CONTINUE_IF_NO_PROXY to False to allow hybrid configuration

Full list of commits since version 1.7.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`80d9041 <https://github.com/HEPCloud/decisionengine_modules/commit/80d904125764a49d602a34094a1f93805d7896fc>`_:   Update refresh_entry_token to use context managers

`62a51f3 <https://github.com/HEPCloud/decisionengine_modules/commit/62a51f3c317ebc3aa64ffef0238defff3fe60fcf>`_:   Merge pull request #434 from BrunoCoimbra/1.7

`2833e82 <https://github.com/HEPCloud/decisionengine_modules/commit/2833e82794572e9ab57b79b5d88349a08befa247>`_:   Set default glidein params on GlideFrontendElement

`ac427d9 <https://github.com/HEPCloud/decisionengine_modules/commit/ac427d9fe4e52fc879866e897ca352d8884975e9>`_:   Set CONTINUE_IF_NO_PROXY to False

`245f316 <https://github.com/HEPCloud/decisionengine_modules/commit/245f31689661ad674fb8133708af4737c2bc279f>`_:   Updated release notes for 1.7.3


Release 1.7.3
-------------

Enable token+proxy hybrid configuration, to send a proxy in a ddition to tokens to support OSG Gratia probes.

Full list of commits since version 1.7.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`da693a7 <https://github.com/HEPCloud/decisionengine_modules/commit/da693a7fc75558ae3af6521dabbd7075fd7b5960>`_:   Enable token proxy hybrid GWMS configuration

`3c75da5 <https://github.com/HEPCloud/decisionengine_modules/commit/3c75da55328c5c25f88efd9713d369a7f4850635>`_:   Updated release notes, ready for 1.7.2


Release 1.7.2
-------------

This release features:

- Add token authentication to the glideinwms module.

Full list of commits since version 1.7.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`82119a2 <https://github.com/HEPCloud/decisionengine_modules/commit/82119a2396667e05465b335ba5c323d493774464>`_:   Add token authentication to the glideinwms module


Release 1.7.1
-------------

Patch level (bug fix) release.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `369 <https://github.com/HEPCloud/decisionengine_modules/issues/369>`_ : Add retries to all publishers that contact Graphite (`e1c28e7 <https://github.com/HEPCloud/decisionengine_modules/commit/e1c28e70e7cf397c03feccfb47effff018006663>`_)


Full list of commits since version 1.7.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`dd4fb50 <https://github.com/HEPCloud/decisionengine_modules/commit/dd4fb50356a542e5d8b4028edb0a7d8673c1d1de>`_:   Homogenize parameter-naming.

`e1c28e7 <https://github.com/HEPCloud/decisionengine_modules/commit/e1c28e70e7cf397c03feccfb47effff018006663>`_:   commit da19f6fd3c81d5a8518dc6e6028fd5853df91279 Author: Kyle Knoepfel <knoepfel@fnal.gov> Date:   Thu Sep 30 21:45:50 2021 +0000

`e56c4d2 <https://github.com/HEPCloud/decisionengine_modules/commit/e56c4d2e9e0495e8b37a5ee84792b7c54b7fab4a>`_:   Fixing issues reported by flake8 and by unit tests for 1.7 branch


Release 1.7.0
-------------

This release features:

- Adopt new produces-consumes decorators introduced in the Framework
- Added structured logging. Improved python logging and adoption of structured logs format that will increase the semantinc content of the messages and ease the export of information for dashboards and Elastic Search.
- Migrated to setuptools package development library. This build system is the standard vanilla python build system provided with the python distribution. Build configurations have been updated and rpm packaging remains the primary distribution method.
- The billing_calculator is now hosted in HEPCloud's GitHub organization

.. note::
    The RPM package was renamed from decisionengine-standard-library to decisionengine_modules. rpm/yum updates from the old RPM will work correctly.

.. note::
    The "channel_name" key in the Source Proxy config dictionaries needs to be changed to "source_channel". "channel_name" is now being used to describe the name of the channel itself, not the name of the channel the Source Proxy is gettting information from.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `354 <https://github.com/HEPCloud/decisionengine_modules/issues/354>`_ : Interior log messages from decision engine modules subroutines are missing;
- `348 <https://github.com/HEPCloud/decisionengine_modules/issues/348>`_ : Name convention on bill_calculator_hep vs. billing_calculator_hep
- `333  <https://github.com/HEPCloud/decisionengine_modules/issues/333>`_ : DE modules entrypoint script always pick DE default branch, this becomes an issue when testing DE modules branches enhancement
- `325  <https://github.com/HEPCloud/decisionengine_modules/issues/325>`_ : Follow up for 323 unit test inside correction map logic
- `323  <https://github.com/HEPCloud/decisionengine_modules/issues/323>`_ : Need to be able to add the conversion map to the factory_entries source onmachine_patch operations


Full list of commits since version 1.6.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`4d2c9fe <https://github.com/HEPCloud/decisionengine_modules/commit/4d2c9febb28fba4395efebe1e63ab65ce1a19f25>`_:   Updated documentation for 1.7.0 release

`7451799 <https://github.com/HEPCloud/decisionengine_modules/commit/7451799a6855f1dd5229ad19e976774f5a98b706>`_:   Updated release notes for 1.7.0 RC4 (1.6.99.post8)

`34d2d74 <https://github.com/HEPCloud/decisionengine_modules/commit/34d2d7474da1ccddb8df5c2df156676722abadb6>`_:   Added module logger for functions in glide_frontend_element.py outside the class

`41e1060 <https://github.com/HEPCloud/decisionengine_modules/commit/41e1060791df9c0234c59248bc1a6161e896dc05>`_:   fixes to tests

`ab0c739 <https://github.com/HEPCloud/decisionengine_modules/commit/ab0c739688011efd742173c7ce470289f696a8a2>`_:   Update release_notes_1.7.rst

`cc94791 <https://github.com/HEPCloud/decisionengine_modules/commit/cc947913c879f626e3d1086eb2ea1e1c3e26ef9f>`_:   Updated release notes for 1.7.0 RC3 (1.6.99.post7)

`076371a <https://github.com/HEPCloud/decisionengine_modules/commit/076371a8aecca02909fc810852c72650623ddea7>`_:   changes needed for structured logging

`77a79ad <https://github.com/HEPCloud/decisionengine_modules/commit/77a79adb0c6b6a81441f77cb0d1b62fe1a614a75>`_:   Use latest version of bill calc

`385266c <https://github.com/HEPCloud/decisionengine_modules/commit/385266c417c18eba3c8aedecc6f6a4e6aca6b92f>`_:   Fix requiements to match our usage

`56e2d9e <https://github.com/HEPCloud/decisionengine_modules/commit/56e2d9e288295a5d6d0987b9250acc644a54b809>`_:   Add config for lgtm

`31d9d77 <https://github.com/HEPCloud/decisionengine_modules/commit/31d9d77db46b1c8b2318157cf868acaf3b96492e>`_:   Rename bill_calculator_hep imports

`2cd29c4 <https://github.com/HEPCloud/decisionengine_modules/commit/2cd29c454a570580030e46818b3db1e88b6a5972>`_:   Updated release notes for 1.7.0 RC2 (1.6.99.post6)

`f8c4c73 <https://github.com/HEPCloud/decisionengine_modules/commit/f8c4c7326a8400ad28bcdab5ef0fcfb3675335eb>`_:   standardizing logging

`160e3b8 <https://github.com/HEPCloud/decisionengine_modules/commit/160e3b8a3a2476cdd5b5c9e323085ac77b648d17>`_:   Added a note to the release notes about the RPM name change

`456003b <https://github.com/HEPCloud/decisionengine_modules/commit/456003b0d6d5dc7fdde3d006e954bc6496c3f1a0>`_:   Release notes ready for v1.7.0

`f8eef94 <https://github.com/HEPCloud/decisionengine_modules/commit/f8eef945932b3097ab066d29ad8cab3391c30370>`_:   changes for structured logging

`8a8c3dc <https://github.com/HEPCloud/decisionengine_modules/commit/8a8c3dc469042df4d13f2719ae94a5958870226f>`_:   Set more firm version requirements for setup.py

`3b44f36 <https://github.com/HEPCloud/decisionengine_modules/commit/3b44f3669e41467b8a3d5e55597e29598d744c67>`_:   Allow use of custom DEframework branch to test DE modules pick DEframework branch from DE modules branch

`d454093 <https://github.com/HEPCloud/decisionengine_modules/commit/d45409304989b5b44f8dd46c7d09b0aeffba7dd6>`_:   Legacy boto isn't used internally any longer

`e87e1fb <https://github.com/HEPCloud/decisionengine_modules/commit/e87e1fb32369373b29fdb6d9d3638c1089a7c323>`_:   Don't package tests at top level

`76f3ae1 <https://github.com/HEPCloud/decisionengine_modules/commit/76f3ae191836e7308730c4d781e8f0916dea519b>`_:   Fix GlideinWMS RPM requirement

`5f9534f <https://github.com/HEPCloud/decisionengine_modules/commit/5f9534f05bab0dd83716e4eda51061611b8339a3>`_:   Move packaging to develop

`267995b <https://github.com/HEPCloud/decisionengine_modules/commit/267995b9b4e6a7ac01938c10a591ae099727b3a5>`_:   Implementing PEP8 issues

`2a4d266 <https://github.com/HEPCloud/decisionengine_modules/commit/2a4d266c9bb83193786c81d3a969fa6dc8415e47>`_:   Adding new test for correction map

`1c60be8 <https://github.com/HEPCloud/decisionengine_modules/commit/1c60be8f7761fdc37b5cdc5011648f2209be8324>`_:   Update Jenkins file to cope with setuptools

`a674626 <https://github.com/HEPCloud/decisionengine_modules/commit/a67462628c2074e768d0825edee4ee5d570030e0>`_:   Migrate to setuptools

`7efbe56 <https://github.com/HEPCloud/decisionengine_modules/commit/7efbe5677dd34168e3b97f3a7df0bc8a1ff739c5>`_:   Preparing 1.7, ready for 1.6.99.post2

`5c3f8b3 <https://github.com/HEPCloud/decisionengine_modules/commit/5c3f8b38ff7f9fa19e216579c3f08facb73efd6f>`_:   Add in Jenkinsfile pipeline configuration a timeout at stage level

`bd83afa <https://github.com/HEPCloud/decisionengine_modules/commit/bd83afa1e4f13be42db0a16cdeef8849a0ece336>`_:   bill-calculator-hep now on official pypi

`518ffdc <https://github.com/HEPCloud/decisionengine_modules/commit/518ffdc5bf69287a776b02b9686f5353463bba36>`_:   Fix coding error.

`68d6441 <https://github.com/HEPCloud/decisionengine_modules/commit/68d64418113727f7347e4a8d07c4c83e117bc754>`_:   Fix typos encountered during integration testing.

`5435707 <https://github.com/HEPCloud/decisionengine_modules/commit/54357079948adf0e3f68618efe6bb76a3a0af651>`_:   Check for configuration error.

`4f7fc04 <https://github.com/HEPCloud/decisionengine_modules/commit/4f7fc044f1761cbf915d405e235a1d7cc9b9812c>`_:   Accomodate breaking changes introduced by the framework.

`a27f92a <https://github.com/HEPCloud/decisionengine_modules/commit/a27f92afc1f5ef2b3d16c03cc311a49593a168cf>`_:   Added 1.6.2 release notes, from branch 1.6

`c7351ca <https://github.com/HEPCloud/decisionengine_modules/commit/c7351ca6a996fb83fc3a2d14625ddd98abdac712>`_:   Merge pull request #329 from jcpunk/billing_calc

`82c7b33 <https://github.com/HEPCloud/decisionengine_modules/commit/82c7b332e2cb77635082e27fb7bd72999e25c8f1>`_:   Add billing-calculator into CI environment

`6658c62 <https://github.com/HEPCloud/decisionengine_modules/commit/6658c623a79fc66b45010f464770b0cb613bf754>`_:   Merge pull request #327 from knoepfel/produces-consumes-configuration

`5a1ab2b <https://github.com/HEPCloud/decisionengine_modules/commit/5a1ab2b6bb707e15f1100037863fe5c071a7dbea>`_:   Address Marco's comments.

`0e2a005 <https://github.com/HEPCloud/decisionengine_modules/commit/0e2a005244af106726d4a0064d581fb31b748f9f>`_:   Upgrade to new produces/consumes/supports_config interface

`e8fd175 <https://github.com/HEPCloud/decisionengine_modules/commit/e8fd175ed79a11a542230909df6c5955dbabf2fc>`_:   Python cleanups

`5edf1f5 <https://github.com/HEPCloud/decisionengine_modules/commit/5edf1f5ccfda2a053545e7c6b7a16f21939fa7a3>`_:   Remove unneeded files

`4a30632 <https://github.com/HEPCloud/decisionengine_modules/commit/4a30632432a3a2e990753c10d743f190c22e1a8a>`_:   Merge pull request #324 from hyunwoo18/t323

`1f80c4a <https://github.com/HEPCloud/decisionengine_modules/commit/1f80c4aaa73e8199c5ea8dd3726e00b8317e7ae7>`_:   Correction map implemented too

`9ce3b1c <https://github.com/HEPCloud/decisionengine_modules/commit/9ce3b1c9946edfe9a0e8cec98c231e6b87fdc974>`_:   Fix import (#321)

`5449e00 <https://github.com/HEPCloud/decisionengine_modules/commit/5449e0034fdcb75d84920de22070c08769a095c7>`_:   fix typo

`7c0752f <https://github.com/HEPCloud/decisionengine_modules/commit/7c0752fabe8f095343c0177ca7e2fb694fb09571>`_:   bump trrunk version
