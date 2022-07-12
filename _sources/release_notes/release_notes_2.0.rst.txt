.. SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
.. SPDX-License-Identifier: Apache-2.0

Release 2.0.1
-------------

Patch level (bug fix) release.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~


Full list of commits since version 2.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`6f2db85 <https://github.com/HEPCloud/decisionengine/commit/6f2db85ffc13470ff2a83b081cd85902ed7c781b>`_:   Fix coverage reporting.

`a764562 <https://github.com/HEPCloud/decisionengine/commit/a76456276c7737a33fe51dba2645ee4f3c7518c9>`_:   Silence warnings that are beyond our control or are irrelevant.

`cc481e9 <https://github.com/HEPCloud/decisionengine/commit/cc481e9affb01d16cba9d87031c2e54ec632f69e>`_:   Test that duplicate column names and empty dataframes are properly handled.

`76e1085 <https://github.com/HEPCloud/decisionengine/commit/76e10851d0084cec5385006a1311bfb6d5af9b85>`_:   Fix NERSC FOM test.

`f67df9d <https://github.com/HEPCloud/decisionengine/commit/f67df9d5070028e4f94602f7d8697ce43e1d7810>`_:   Cleanup tests.

`51c6e75 <https://github.com/HEPCloud/decisionengine/commit/51c6e756e4387c33dede15159379eebab223fb1e>`_:   Work around pylint bug.

`3eb1e92 <https://github.com/HEPCloud/decisionengine/commit/3eb1e92635d1d621e5656a0069294b81dc0f379f>`_:   Ensure setuptools is up-to-date in GitHub actions; also update actions.

`bfe45e5 <https://github.com/HEPCloud/decisionengine/commit/bfe45e5005edfd19b9bbfe1331d9fc6a64656828>`_:   in dataframe_for_entrytype take care of empty datablocks

`5223daf <https://github.com/HEPCloud/decisionengine/commit/5223daf2442ba6992b917d9f63e58bc1351d9049>`_:   Enable token proxy hybrid GWMS configuration

`265dc8e <https://github.com/HEPCloud/decisionengine/commit/265dc8e3224581c43b48704e988e5c8576f566f9>`_:   Fix pre-commit node version to 17.9.0, the last to support SL7.

`7f5922f <https://github.com/HEPCloud/decisionengine/commit/7f5922f22359d72f6a0d6742c67d22e0762f93e2>`_:   Single point of maintenance for entry types.

`0125962 <https://github.com/HEPCloud/decisionengine/commit/0125962b4bb14a9a38254ae57f8f28d1f63ed1cc>`_:   Support additional queries according to the entrytype/logic-engine fact.

`f685f24 <https://github.com/HEPCloud/decisionengine/commit/f685f240abea3616e9a923d71325692778abf061>`_:   Use Pandas concepts.

`331a284 <https://github.com/HEPCloud/decisionengine/commit/331a28418ceb86959450eaac41e30301ad90e397>`_:   Testing cleanups.

`05b605e <https://github.com/HEPCloud/decisionengine/commit/05b605eba937a619573971310a25b3bd10a55175>`_:   Remove unnecessary code.

`0b9e6c7 <https://github.com/HEPCloud/decisionengine/commit/0b9e6c7ca9db99450ad8e8aae402b3d42dcfd088>`_:   Fix pyupgrade version for python 3.6 compatibility

`9f8dddb <https://github.com/HEPCloud/decisionengine/commit/9f8dddb8779805cb97e1caaef47acf45d73c9c28>`_:   Further cleanups for testing glidein frontend element.

`0292842 <https://github.com/HEPCloud/decisionengine/commit/029284239b1fad5fac06baface5e3aa3b67adeb5>`_:   Remove unnecessary testing classes.

`fcd1a40 <https://github.com/HEPCloud/decisionengine/commit/fcd1a405b25bf7105f3f5e12625c69f189a08860>`_:   Added cross-package link in the documentation

`a35c2e8 <https://github.com/HEPCloud/decisionengine/commit/a35c2e88dd1fd7627a3d84726654e0d9d6c9fc0f>`_:   Updated 2.0 release notes and indexes, ready for 2.0.0


Release 2.0.0
-------------

This release series follows 1.7. A lot started to happen in 1.7.0 and has happened since, so we felt it was proper
to change the major version number.
We are proud to introduce Decision Engine 2.0.0 to outside users: it provides a
friendlier installation procedure and configuration samples to test it
on all resources supported by the GlideinWMS Factory, like OSG, some HPC resources and
commercial cloud providers.
The decisionengine_modules is the standard library of modules distributed to support the main
sources, transformations and publishers of the Decision Engine.
See also the Release Notes of decisionengine, the Decision Engine framework.

This release features:

- Adopt new Framework architecture for the sources
- Separation from the GlideinWMS Frontend. Decision Engine still shares some libraries with GlideinWMS but
  you don't need any more to install and configure the Frontend.
- Structured logging. Improved python logging and adoption of structured logs format that will increase the semantinc content of the messages and ease the export of information for dashboards and Elastic Search.
- Monitoring via Prometheus.
- Added support of CentOS8 (RHEL7 is still out main platform)
- Configuration example using HTC resources via GlideinWMS Factory
- Decision Engine is distributed under the Apache 2.0 license
- We increased our CI tests including also code auto-formatting and license compliance.
  We introduced integration tests and we are proud of our over 95% unit test coverage.

.. note::
    decisionengine_modules now requires GlideinWMS 3.9.4. The vofrontend installation and configuration is no more needed,
    decisionengine_modules now depends from the GlideinWMS vofrontend-lib.
    Check the new instructions for the changed configuration of the glideinwms module.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `353 <https://github.com/HEPCloud/decisionengine_modules/issues/353>`_ : yum update decisionengine-standard-library doesn't detect and pull in decisionengine_modules
- `282 <https://github.com/HEPCloud/decisionengine_modules/issues/282>`_ : Decision Engine classad encoding problems make multiple exceptions in the factory
- `349 <https://github.com/HEPCloud/decisionengine_modules/issues/349>`_ : Minor issue setup tools decisionengine_modules
- `363 <https://github.com/HEPCloud/decisionengine_modules/issues/363>`_ : Replace AWSOccupancy and AWSSpotPrice classes with SourceProxy + transforms
- `253 <https://github.com/HEPCloud/decisionengine_modules/issues/253>`_ : Different modules are using different retry parameters in config
- `348 <https://github.com/HEPCloud/decisionengine_modules/issues/348>`_ : Name convention on bill_calculator_hep vs. billing_calculator_hep
- `361 <https://github.com/HEPCloud/decisionengine_modules/issues/361>`_ : glide_frontend_element.py throws logger exception in 1.7.0rc3


Full list of commits since version 1.7.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`d605ab0 <https://github.com/HEPCloud/decisionengine_modules/commit/d605ab0aa3833cec5b31a97bacadda83a520f5a8>`_:   Added changelog file for developers curated list of changes

`cc0b18a <https://github.com/HEPCloud/decisionengine_modules/commit/cc0b18a0eb10dd06ea9c18b2347109a902413951>`_:   Adding 1.7.2 release information

`eb40d1e <https://github.com/HEPCloud/decisionengine_modules/commit/eb40d1ef5e24c409e80ee6c3404b7f540266ef92>`_:   Updated release notes, ready for 2.0.0 RC4

`53b2fe4 <https://github.com/HEPCloud/decisionengine_modules/commit/53b2fe47660af403b6708b23029b71b52c9b98dc>`_:   The rpm-build workflow has been updated to include the workflow_dispatch action me
chanism. This allows to trigger this action through a GitHub API or directly through the action dashboard, This PR also customize the RPM artifact file name.

`cd52b39 <https://github.com/HEPCloud/decisionengine_modules/commit/cd52b394b6fb3b837508934ef2fd6c7301d3037e>`_:   Catch exceptions when no VMs running in GCE

`9044b64 <https://github.com/HEPCloud/decisionengine_modules/commit/9044b64d3dc813e9eabc36d04c125392f2efecb9>`_:   Add token authentication to the glideinwms module

`97ca32a <https://github.com/HEPCloud/decisionengine_modules/commit/97ca32ad84d26b9059f6eda8988c8ddd80a0466a>`_:   Modified pre-commit bot suggestions. Avoid pyupgrade that requires pytohn 3.7

`95a7d7b <https://github.com/HEPCloud/decisionengine_modules/commit/95a7d7b8835776da4ed16a3a6268da96cabe74e6>`_:   Test the arguments used to call publish_to_htcondor.

`27f0f4b <https://github.com/HEPCloud/decisionengine_modules/commit/27f0f4b2be069f2e9d5f2449e123e131f21b0c29>`_:   Adjust code-coverage configuration to display code in browser.

`3addf20 <https://github.com/HEPCloud/decisionengine_modules/commit/3addf20c66d21c6d2868fd49b335dbbe82b36ad3>`_:   Make sure variables are defined before they're used.

`75381df <https://github.com/HEPCloud/decisionengine_modules/commit/75381df5cd121774ce4685566ff9c6a7642daa73>`_:   Improve fe_group_classads test.

`ed2a8b4 <https://github.com/HEPCloud/decisionengine_modules/commit/ed2a8b425817ffe10325929b993c4c264899494f>`_:   Check DecisionEngineMonitorManifests for empty DFs

`e7a247b <https://github.com/HEPCloud/decisionengine_modules/commit/e7a247bde306e69b71ecb05c9ae528a01fc36373>`_:   Fix GlideClientGlobal create_invalidate_constraint

`f0819b1 <https://github.com/HEPCloud/decisionengine_modules/commit/f0819b1e06f493a15a473f35f0802cb35313e753>`_:   pin pytest version

`ad59fed <https://github.com/HEPCloud/decisionengine_modules/commit/ad59fede98fa4be07cae4cc17ac5741191a35afa>`_:   [pre-commit.ci] pre-commit autoupdate

`0fc20e5 <https://github.com/HEPCloud/decisionengine_modules/commit/0fc20e56cc888db020bb78b9bb98dc6acd00771d>`_:   Added unlinked release notes for DEM 2.0.0

`123dd2b <https://github.com/HEPCloud/decisionengine_modules/commit/123dd2bea1367ffb3de76456b4a383eed273c75e>`_:   Drop extra lines

`0177318 <https://github.com/HEPCloud/decisionengine_modules/commit/0177318fb72f9d66d0f3bd7d3fcda6f044be4608>`_:   Rename product so that translation is not necessary.

`94e334c <https://github.com/HEPCloud/decisionengine_modules/commit/94e334c6e9ceeebe92da9406a0a81675f21e05bd>`_:   Explicitly pass .coveragerc to pytest.

`04456a9 <https://github.com/HEPCloud/decisionengine_modules/commit/04456a903e45d8fff400b2d5b532ce19145e2cb3>`_:   Updated documentation for 1.7.1 release

`240d937 <https://github.com/HEPCloud/decisionengine_modules/commit/240d937ade1ba169fa7c83bf660de858aff87866>`_:   [pre-commit.ci] pre-commit autoupdate

`f054532 <https://github.com/HEPCloud/decisionengine_modules/commit/f0545327a453dff7d7a5d5ba6bd4eb0d70e9f074>`_:   Use pre-commit.ci rather than local actions

`e2bc8d8 <https://github.com/HEPCloud/decisionengine_modules/commit/e2bc8d84a2e106415ac3078296d7d99ca5eba5ee>`_:   Update GlideinWMS dependencies

`4dfefb1 <https://github.com/HEPCloud/decisionengine_modules/commit/4dfefb175fde837e0328db8607fcc4081976b14a>`_:   Add SPDX blurbs.

`a0889aa <https://github.com/HEPCloud/decisionengine_modules/commit/a0889aab61229c50937626c86835f13a5ca13ccc>`_:   Update pre-commit hook versions and accommodate python-debian issue.

`7fd1c9c <https://github.com/HEPCloud/decisionengine_modules/commit/7fd1c9c3615fc8fa73fc1f929311baff7c189f9f>`_:   Change gwmw module to read cfg from DE framework

`d57ac6e <https://github.com/HEPCloud/decisionengine_modules/commit/d57ac6ee7376191f482fd0bebe14f013b8e16e79>`_:   Set Apache 2.0 license and added REUSE compliance

`cf43119 <https://github.com/HEPCloud/decisionengine_modules/commit/cf4311949d3c5fd991d1c5c4a6a190ba53a2eb71>`_:   Set fail-fast to false to allow py3.6 tests to complete also when higher version fail. Temporarly downgraded from py3.10 to py3.9 because the condor dependency is not available yet for py3.10.

`e2707e5 <https://github.com/HEPCloud/decisionengine_modules/commit/e2707e589142d40afdc5716fd4c4d6c9a38bc64e>`_:   Ignoring E203, whitespace after ':', since black is adding the whitespace

`b0e3526 <https://github.com/HEPCloud/decisionengine_modules/commit/b0e3526e5d050094a63474798fd9dec993a64b67>`_:   Remove modules that inherit from SourceProxy. Inheritance from SourceProxy has been forbidden by PR#526. In this commit it has been removed the SourceProxy module GCEResourceLimits that is not used.

`208a660 <https://github.com/HEPCloud/decisionengine_modules/commit/208a660d356df9fd74aad1a646555d83455e5b10>`_:   Revert "Add jsonnetfmt hook"

`efbf6b9 <https://github.com/HEPCloud/decisionengine_modules/commit/efbf6b9761fbc10860b392b56c723274436dc54c>`_:   Add jsonnetfmt hook

`9140330 <https://github.com/HEPCloud/decisionengine_modules/commit/91403308916ffb979e6ef29986e4fb96fa540f58>`_:   Recasting AWSOccupancy, AWSSpotPrice and associated unit tests as Transforms AWSOccupancy and AWSSpotPrice source proxies will be handled at config level

`81adb29 <https://github.com/HEPCloud/decisionengine_modules/commit/81adb2968541b46dc90c1634f7ed0528124f3e5d>`_:   Start testing against python 3.10

`a9c1f3c <https://github.com/HEPCloud/decisionengine_modules/commit/a9c1f3cb67686de9e49a53c39f953b585aedcd57>`_:   Support retries for contacting Graphite.

`3bd68e4 <https://github.com/HEPCloud/decisionengine_modules/commit/3bd68e428ce94f829dbc04b3eeaaed3f84784d66>`_:   Fix some errors, most caught by lgtm.

`89e21f0 <https://github.com/HEPCloud/decisionengine_modules/commit/89e21f0727b64291db96c5e4d5f605e9e83950b1>`_:   Simplify some code paths

`63f6315 <https://github.com/HEPCloud/decisionengine_modules/commit/63f6315046e8daa8613e7853c4967d903d73ab54>`_:   Homogenize parameter-naming.

`325ea37 <https://github.com/HEPCloud/decisionengine_modules/commit/325ea37f8e07dc43010ffc91d43452d170a749ee>`_:   Update pre-commit hooks via `pre-commit autoupdate`

`ee7d45c <https://github.com/HEPCloud/decisionengine_modules/commit/ee7d45cb784eb4f7e758c7bbda327c50b59e4cc4>`_:   More logging improvements.

`901291c <https://github.com/HEPCloud/decisionengine_modules/commit/901291c24326681caf67fba61b6b2cd20a8b75d5>`_:   Take advantage of simplified logging.

`f4752ab <https://github.com/HEPCloud/decisionengine_modules/commit/f4752abc0abe16c71a3f005218edadad7a9f1939>`_:   Fixup pre-commit hooks

`ad66754 <https://github.com/HEPCloud/decisionengine_modules/commit/ad66754eea2ac7bbe9a12372166d548056b8f516>`_:   Add Linters task

`ca61ae3 <https://github.com/HEPCloud/decisionengine_modules/commit/ca61ae3560f2d4f7f4347cfd3eee206a4a7891ea>`_:   Update to latest setuptools_scm

`3ad934b <https://github.com/HEPCloud/decisionengine_modules/commit/3ad934bd49a6c982f44e68e17c63f43b2b42905a>`_:   Fixed project name

`ec2a94e <https://github.com/HEPCloud/decisionengine_modules/commit/ec2a94ec9e97722423d8ad93acd6304fcc300e21>`_:   Added 1.1 release notes
