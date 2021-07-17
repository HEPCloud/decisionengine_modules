Release 1.7.0
-------------

This release features:

- Adopt new produces-consumes decorators introduced in the Framework
- Added structured logging. Improved python logging and adoption of structured logs format that will increase the semantinc content of the messages and ease the export of information for dashboards and Elastic Search.
- Migrated to setuptools package development library. This build system is the standard vanilla python build system provided with the python distribution. Build configurations have been updated and rpm packaging remains the primary distribution method.
- The billing_calculator is now hosted in HEPCloud's GitHub organization

.. note::
    The RPM package was renamed from decisionengine-standard-library to decisionengine_modules. rpm/yum updates from the old RPM will work correctly.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`333  <https://github.com/HEPCloud/decisionengine_modules/issues/333>`_ : DE modules entrypoint script always pick DE default branch, this becomes an issue when testing DE modules branches enhancement
`325  <https://github.com/HEPCloud/decisionengine_modules/issues/325>`_ : Follow up for 323 unit test inside correction map logic
`323  <https://github.com/HEPCloud/decisionengine_modules/issues/323>`_ : Need to be able to add the conversion map to the factory_entries source onmachine_patch operations


Full list of commits since version 1.6.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

