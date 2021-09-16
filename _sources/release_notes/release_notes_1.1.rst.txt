Release 1.1.0
-------------

In this release:

* Fixed. https://github.com/HEPCloud/decisionengine_modules/issues/62. "Update Nersc Allocation Info source for new NERSC API "
* significant code cleanup and pep8 compliance
* unit test work
* CI (GitHub actions and Travis) is introduced


Patches:
~~~~~~~~

`6455c93 <https://github.com/HEPCloud/decisionengine_modules/commit/6455c937089b8e48977df49974e26842f05ef64f>`_
:   1.1 (#203)

`375bec5 <https://github.com/HEPCloud/decisionengine_modules/commit/375bec5088196249df5bc7e2cee9eeeef2a9ee5c>`_
:   clone specific branch of decisionengine (#202)

`36c66a8 <https://github.com/HEPCloud/decisionengine_modules/commit/36c66a8c6a7e6d7bca3f9963b86e0b370dd0eb63>`_
:   set version to 1.1.0

`40f31bb <https://github.com/HEPCloud/decisionengine_modules/commit/40f31bbd0cd7490f1fa5f538b56df0da8e1f3711>`_
:   Use sparse checkout for first checkout to get ./github/actions (#23)

`b2933d7 <https://github.com/HEPCloud/decisionengine_modules/commit/b2933d732ec31885cf93c8b211a4bcf8ec1792ee>`_
:   Remove unpackaged files (#22)

`fee64ea <https://github.com/HEPCloud/decisionengine_modules/commit/fee64ea0b5502550c991e7b6b00b8e00abd7fd70>`_
:   remove python shebang, fix logging-too-many-args, fix unsubscriptable-object (#21)

`fbf4eb6 <https://github.com/HEPCloud/decisionengine_modules/commit/fbf4eb65228b198caf0572a755fb8d4c3c3cd19d>`_
:   Fixes pep8 warnings. (#20)

`9f26659 <https://github.com/HEPCloud/decisionengine_modules/commit/9f266593c852631d5be53bc06d036a34f4d05d9d>`_
:   Hyunwoo2to3 (#19)

`6870b0b <https://github.com/HEPCloud/decisionengine_modules/commit/6870b0bc8e517f1cd2a85919f808565df6772367>`_
:   travis-ci: install boto3, htcondor and execute test in one directory above decisionengine_modules (#18)

`22ed8b9 <https://github.com/HEPCloud/decisionengine_modules/commit/22ed8b9cc58384c49289cef6db3b279288828728>`_
:   Fixup condor-classad (#17)

`c9edb09 <https://github.com/HEPCloud/decisionengine_modules/commit/c9edb09be896a88e0b6a4d0c770d865c497a25e2>`_
:   Add unit test github action. Run as non-root uid. Install python packages in virtualenv. (#14)

`b41257d <https://github.com/HEPCloud/decisionengine_modules/commit/b41257dd378ed7b897f311817a257cee2d601e36>`_
:   Setup pep8speaks (#16)

`b3bbe28 <https://github.com/HEPCloud/decisionengine_modules/commit/b3bbe28dc9b86c38e501254940f3311ea1a1c8f1>`_
:   Transitioned NERSC API to new IRIS API for accounting data. (#15)

`267ec14 <https://github.com/HEPCloud/decisionengine_modules/commit/267ec149de62ad1a895a8a9275fdd46782b18ec1>`_
:   Setup travis (#13)

`4151a9a <https://github.com/HEPCloud/decisionengine_modules/commit/4151a9aa084ceeb1212c11bafdce0930fac6ab83>`_
:   unittest: Fix GCEResourceLimits so that it does not depend on configuration (#12)

`5a44018 <https://github.com/HEPCloud/decisionengine_modules/commit/5a44018603994b64253356186c27d358961a0d2c>`_
:   Update decisionengine_modules rpmbuild and pylint actions. (#9)

`c562696 <https://github.com/HEPCloud/decisionengine_modules/commit/c562696be17d972296d1c4f11fb2bab7584b7bef>`_
:   Update entrypoint.sh (#8)

`6d953f2 <https://github.com/HEPCloud/decisionengine_modules/commit/6d953f2ce1670e1975ecd2f65e2b074f26499d43>`_
:   rpm spec: remove unwated directory (#7)

`474c39c <https://github.com/HEPCloud/decisionengine_modules/commit/474c39c923378bc93c231f1feec0af5195fe13b0>`_
:   unittest: make htcondor_query test pass (#6)

`f0ff5a9 <https://github.com/HEPCloud/decisionengine_modules/commit/f0ff5a99d7eefc8258f7be7d48846a9b64158900>`_
:   unittest improvements (#5)

`e928059 <https://github.com/HEPCloud/decisionengine_modules/commit/e92805958e7a5ebcad636f40e718dbf061ead8c7>`_
:   AWS: fix all but one unit tests

`182b582 <https://github.com/HEPCloud/decisionengine_modules/commit/182b5822545f5549ed80b8ee1a2fe95c15fe3eef>`_
:   fix unit tests, light formatting

`bb4a9e4 <https://github.com/HEPCloud/decisionengine_modules/commit/bb4a9e489e8cc0c408734114c56b464f81e95489>`_
:   Cache venv directory instead.

`d805129 <https://github.com/HEPCloud/decisionengine_modules/commit/d8051298009a920561edc67605067e828502e4b4>`_
:   Test pip cache

`b64e85d <https://github.com/HEPCloud/decisionengine_modules/commit/b64e85db0000f64c7f7446cf948c9f89fc56286b>`_
:   Add Github Actions
