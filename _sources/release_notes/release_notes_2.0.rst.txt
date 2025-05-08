.. SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
.. SPDX-License-Identifier: Apache-2.0

Release 2.0.6
-------------

Improved separation and compatibility with GlideinWMS Frontend package.
Improved GCE billing and set hep-bill-calculator to 0.2.3.

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-`DEM 513 <https://github.com/HEPCloud/decisionengine_modules/pull/513>`_: Updated documentation for release 2.0.4
-`DEM 516 <https://github.com/HEPCloud/decisionengine_modules/pull/516>`_: Refactor Existing Test Script and Add New Unit Tests for GCE Billing

Full list of commits since version 2.0.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`46bfc52 <https://github.com/HEPCloud/decisionengine_modules/commit/46bfc52e160342e32a203a274a5d156b7dd40f40>`_:   Refactor Existing Test Script and Add New Unit Tests for GCE Billing (#516)

`b7accf0 <https://github.com/HEPCloud/decisionengine_modules/commit/b7accf04ed6e29338662d6f70b9a414cff2e1acf>`_:   Updated setuptools in  gh-pages workflow

`993e380 <https://github.com/HEPCloud/decisionengine_modules/commit/993e380a7f3860481878769d2f93c8c3e13ec763>`_:   Update gh-pages workflow and install sphinx as user, not as root


Release 2.0.4
-------------

This release brings a new packaging with RPM packages for dependencies and system files, and a Python wheel for the Python code.
There are also new Prometheus metrics and a few bug fixes like the superfacility API and AWS and GCE billing.

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-`DEM 444 <https://github.com/HEPCloud/decisionengine_modules/pull/444>`_: Add CodeQL workflow for GitHub code scanning  (@lgtm-com)
-`DEM 445 <https://github.com/HEPCloud/decisionengine_modules/pull/445>`_: Added CPU Metrics.  (@Redjacket45)
-`DEM 456 <https://github.com/HEPCloud/decisionengine_modules/pull/456>`_: Upgrading isort version to fix pre-config install error w/ poetry  (@mambelli)
-`DEM 461 <https://github.com/HEPCloud/decisionengine_modules/pull/461>`_: Eliminate escaping of double quotation marks to conform with NEWT API's changed behavior  (@namrathaurs)
-`DEM 459 <https://github.com/HEPCloud/decisionengine_modules/pull/459>`_: Disabling Python 3.6 and Fixing 3.9 Unit Tests in CI Workflow  (@namrathaurs)
-`DEM 462 <https://github.com/HEPCloud/decisionengine_modules/pull/462>`_: Feature/vito pandas2 updates  (@vitodb)
-`DEM 463 <https://github.com/HEPCloud/decisionengine_modules/pull/463>`_: Fixed Google dependency to work fine in Python 3.9  (@mambelli)
-`DEM 457 <https://github.com/HEPCloud/decisionengine_modules/pull/457>`_: Making CONTINUE_IF_NO_PROXY attribute configurable  (@namrathaurs)
-`DEM 465 <https://github.com/HEPCloud/decisionengine_modules/pull/465>`_: Update tests  (@vitodb)
-`DEM 472 <https://github.com/HEPCloud/decisionengine_modules/pull/472>`_: Adding DE modules EL9 CI container based on AlmaLinux9  (@vitodb)
-`DEM 468 <https://github.com/HEPCloud/decisionengine_modules/pull/468>`_: New Nersc Source Module using SuperFacilityApi  (@hyunwoo18)
-`DEM 474 <https://github.com/HEPCloud/decisionengine_modules/pull/474>`_: fix test_refresh_entry_token unit test  (@vitodb)
-`DEM 473 <https://github.com/HEPCloud/decisionengine_modules/pull/473>`_: Adding Jenkinsfile for EL9  (@vitodb)
-`DEM 477 <https://github.com/HEPCloud/decisionengine_modules/pull/477>`_: Adding one line  (@hyunwoo18)
-`DEM 481 <https://github.com/HEPCloud/decisionengine_modules/pull/481>`_: Refactor DEConfigSource and configure_gwms_frontend  (@BrunoCoimbra)
-`DEM 482 <https://github.com/HEPCloud/decisionengine_modules/pull/482>`_: Components of decisionengine dashboards  (@skylerfoster67)
-`DEM 484 <https://github.com/HEPCloud/decisionengine_modules/pull/484>`_: Change glideclient advertisement logic  (@BrunoCoimbra)
-`DEM 485 <https://github.com/HEPCloud/decisionengine_modules/pull/485>`_: Fix a typo in glideids_to_advertise  (@BrunoCoimbra)
-`DEM 487 <https://github.com/HEPCloud/decisionengine_modules/pull/487>`_: Fix configure_gwms_frontend tests  (@BrunoCoimbra)
-`DEM 486 <https://github.com/HEPCloud/decisionengine_modules/pull/486>`_: Re-enable flak8 linter  (@vitodb)
-`DEM 492 <https://github.com/HEPCloud/decisionengine_modules/pull/492>`_: Do not test external dependencies with flake8  (@vitodb)
-`DEM 489 <https://github.com/HEPCloud/decisionengine_modules/pull/489>`_: Added new metrics to job_q and source  (@IlyaBaburashvili)
-`DEM 493 <https://github.com/HEPCloud/decisionengine_modules/pull/493>`_: Add dem_htcondor_cores_count and dem_htcondor_cores_histogram metrics to source.py  (@IlyaBaburashvili)
-`DEM 498 <https://github.com/HEPCloud/decisionengine_modules/pull/498>`_: Added unit tests for dem_htcondor_slots_status_count, dem_htcondor_cores_count, dem_htcondor_memory_count. Fixed issues in source.py.  (@IlyaBaburashvili)
-`DEM 496 <https://github.com/HEPCloud/decisionengine_modules/pull/496>`_: New Figure of Merit Metric  (@skylerfoster67)
-`DEM 499 <https://github.com/HEPCloud/decisionengine_modules/pull/499>`_: Two dashboards for cores, slots, and runtimes  (@IlyaBaburashvili)
-`DEM 503 <https://github.com/HEPCloud/decisionengine_modules/pull/503>`_: In Jenkins pipeline config use podman instead of docker  (@vitodb)
-`DEM 502 <https://github.com/HEPCloud/decisionengine_modules/pull/502>`_: add new method of determining token expiration instead of relying on jwt.decode error code  (@StevenCTimm)
-`DEM 507 <https://github.com/HEPCloud/decisionengine_modules/pull/507>`_: Refactor time_left in security module  (@BrunoCoimbra)
-`DEM 505 <https://github.com/HEPCloud/decisionengine_modules/pull/505>`_: Migrating GCE Billing to BigQuery based Bill Calculations  (@namrathaurs)
-`DEM 506 <https://github.com/HEPCloud/decisionengine_modules/pull/506>`_: DEConfigSource converts nested dicts to OrderedDicts  (@BrunoCoimbra)
-`DEM 510 <https://github.com/HEPCloud/decisionengine_modules/pull/510>`_: Add retry functionality to NerscSFApi  (@vitodb)
-`DEM 511 <https://github.com/HEPCloud/decisionengine_modules/pull/511>`_: Packaging with uv and pyproject.toml  (@mambelli)
-`DEM 512 <https://github.com/HEPCloud/decisionengine_modules/pull/512>`_: Added codespell in pre-commit and fixed files to compliance  (@mambelli)

Full list of commits since version 2.0.2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`c481f85 <https://github.com/HEPCloud/decisionengine_modules/commit/c481f85a5c6a00a5bebeb94bb46c9d69658c5243>`_:   Added codespell in pre-commit and fixed files to compliance

`3bf56ab <https://github.com/HEPCloud/decisionengine_modules/commit/3bf56ab88fc81bacdb4b129e5a08f38ee2ea5408>`_:   Packaging with uv and pyproject.toml

`5577e9e <https://github.com/HEPCloud/decisionengine_modules/commit/5577e9e6958f01f32f20c124be20fb57c42473fc>`_:   [pre-commit.ci] auto fixes from pre-commit.com hooks

`230627f <https://github.com/HEPCloud/decisionengine_modules/commit/230627f4bf1bf5ebe1ac051f78c0d664613d1069>`_:   Add retry functionality to NerscSFApi

`b820998 <https://github.com/HEPCloud/decisionengine_modules/commit/b820998100bb925bfe5da231e9d80138834a4d82>`_:   DEConfigSource converts nested dicts to OrderedDicts

`8e78900 <https://github.com/HEPCloud/decisionengine_modules/commit/8e7890023da02c977be13b11a3a9aa1e0d7b8fd8>`_:   [pre-commit.ci] auto fixes from pre-commit.com hooks

`a85edeb <https://github.com/HEPCloud/decisionengine_modules/commit/a85edeb7b2f622eaf32915613200558eb15c41fa>`_:   migrating to using bigquery for GCE billing

`c4d0bc1 <https://github.com/HEPCloud/decisionengine_modules/commit/c4d0bc195e4da960f745b84c379388f2232224a2>`_:   Refactor time_left in security module

`a42d3bd <https://github.com/HEPCloud/decisionengine_modules/commit/a42d3bd37468bd0a103b32fff5e2061fb069431e>`_:   [pre-commit.ci] auto fixes from pre-commit.com hooks

`5305f59 <https://github.com/HEPCloud/decisionengine_modules/commit/5305f59739ddc8ad6c4ffc06b72c664539f5c7ae>`_:   remove the extraneous print statements

`b57507b <https://github.com/HEPCloud/decisionengine_modules/commit/b57507bcae4e69eda7841ce4760dd538d79553ce>`_:    changing the way that the NERSC SFApi access token expiration is calculated to not rely on jwt.decode() exit value

`c500a73 <https://github.com/HEPCloud/decisionengine_modules/commit/c500a73c38189ae14e0d2a127463a91f09e8c4ea>`_:   In Jenkins pipeline config use podman instead of docker

`aa975b8 <https://github.com/HEPCloud/decisionengine_modules/commit/aa975b8f7751867636e0402dc0aaa25d0096515a>`_:   Added dashboards  for cores, slots, and runtimes

`af1003b <https://github.com/HEPCloud/decisionengine_modules/commit/af1003b7eda33e0950770c7b28741d1948eacc60>`_:   New Figure of Merit Metric (#496)

`fb4c3f9 <https://github.com/HEPCloud/decisionengine_modules/commit/fb4c3f9033d48670b7e5129c2478ccfc0d28fd69>`_:   Remove extra line from dep5

`63adb86 <https://github.com/HEPCloud/decisionengine_modules/commit/63adb86a218c027e3385988d584094392ed17d4e>`_:   Add unit tests for metrics, fix issue in source.py

`4f590a6 <https://github.com/HEPCloud/decisionengine_modules/commit/4f590a6c0f06b6afb264891d4d0e16de89ce968b>`_:   Fixed commit history

`21ac8c4 <https://github.com/HEPCloud/decisionengine_modules/commit/21ac8c4c8983a36184e3b8b4a52781da1ae78b0e>`_:   Remove include Histogram

`aae8638 <https://github.com/HEPCloud/decisionengine_modules/commit/aae8638b709f0572036239b7e4ed4fe6396a0fe6>`_:   Remove debugging statements

`b673c4a <https://github.com/HEPCloud/decisionengine_modules/commit/b673c4ae1e91bb62883071e9133fc37ee0b9e441>`_:   Fix PR 489

`7601451 <https://github.com/HEPCloud/decisionengine_modules/commit/7601451fa3788240f0208fbbfac4ad801ba520ec>`_:   For flake8 skip build folder

`9980e3a <https://github.com/HEPCloud/decisionengine_modules/commit/9980e3a6974d2339c8412c83868596ab17a5ec1c>`_:   Make the test flake8 compliant

`85e6487 <https://github.com/HEPCloud/decisionengine_modules/commit/85e6487b9232c93305478d05b366e084dc5de087>`_:   Do not test external dependencies

`8a07b0e <https://github.com/HEPCloud/decisionengine_modules/commit/8a07b0e52a2a3acf21846fc3e08d8b98c8e95894>`_:   Add licence info to flake8 config file

`97f6f63 <https://github.com/HEPCloud/decisionengine_modules/commit/97f6f63d1ad8d816d66abacab3b43902c8ac6a0b>`_:   Re-enable flak8 linter

`a28c97d <https://github.com/HEPCloud/decisionengine_modules/commit/a28c97d50f13e3cb8019f7389442860fc93de71c>`_:   Update test_configure_gwms_frontend.py

`01c9c40 <https://github.com/HEPCloud/decisionengine_modules/commit/01c9c40dad52856d009c95ece1531a0652e8ba19>`_:   Fix configure_gwms_frontend tests

`5eb2f2b <https://github.com/HEPCloud/decisionengine_modules/commit/5eb2f2b6a6a7d8b9aa0dd4588914cf036aa43208>`_:   Fix a typo in glideids_to_advertise

`cb19a5b <https://github.com/HEPCloud/decisionengine_modules/commit/cb19a5b7ea7edc8ea7bfdccad63f61a4658bf04b>`_:   Fix glideclient advertisement logic

`9c1f8e5 <https://github.com/HEPCloud/decisionengine_modules/commit/9c1f8e5bc038d7990f77fe3eda9c2f0f25676e22>`_:   Added json files on Channel and Source Data dashboards with specific naming

`ea00e39 <https://github.com/HEPCloud/decisionengine_modules/commit/ea00e39904a53e57d5a4e8506cadbe7b583385c1>`_:   Adding license information for dashboard files because JSON does not allow comments

`c11a7e2 <https://github.com/HEPCloud/decisionengine_modules/commit/c11a7e247d5678cd7c438a40e1f44f1c36b71f4b>`_:   [pre-commit.ci] auto fixes from pre-commit.com hooks

`92b72b6 <https://github.com/HEPCloud/decisionengine_modules/commit/92b72b6cb88d95e79f9f6dd84fea5e010553bbc5>`_:   Refactor config source for configure_gwms_frontend

`02ab367 <https://github.com/HEPCloud/decisionengine_modules/commit/02ab367c1e2484114b07c2e7bf59752edbfa6333>`_:   Adding one line

`32d6114 <https://github.com/HEPCloud/decisionengine_modules/commit/32d6114e1aa277022316e2eeec63530716548f23>`_:   Added directory for Grafana dashboards

`5a5fb8b <https://github.com/HEPCloud/decisionengine_modules/commit/5a5fb8b80b866ef563f4b9ac38a685f8f36bf6c5>`_:   Adding Jenkinsfile for EL9

`aa59c49 <https://github.com/HEPCloud/decisionengine_modules/commit/aa59c4979036c35a52c7a922445fc746ae62c017>`_:   required jwt functionalities are provided by PyJWT

`2df1fc5 <https://github.com/HEPCloud/decisionengine_modules/commit/2df1fc5565c78642e0ce68430d30dc3508049ab4>`_:   Updated documentation for 1.7.5 release

`cf81d56 <https://github.com/HEPCloud/decisionengine_modules/commit/cf81d562a25fa93eff66cd45b4e594b28017f6c8>`_:   Last update to setup.py

`8bc6d24 <https://github.com/HEPCloud/decisionengine_modules/commit/8bc6d24aad1775966fc9e262e4b96b051a4f6e16>`_:   Last update to add KeyError

`85604ef <https://github.com/HEPCloud/decisionengine_modules/commit/85604ef8ce2f3ac30911050dde2cd8c7a656cfd2>`_:   Removed remaining hardcoded strings from the code

`8117652 <https://github.com/HEPCloud/decisionengine_modules/commit/811765255d057f51142b0f5349b3641f4529d952>`_:   Implementing Marco requests in the review

`1d59d49 <https://github.com/HEPCloud/decisionengine_modules/commit/1d59d49a4169791189dd1a7e334cd3a46c30b328>`_:   Fixed pre-commit issues and jwt package

`b107c06 <https://github.com/HEPCloud/decisionengine_modules/commit/b107c06e2ac4e95c8a04b3beb04c22b450090ea9>`_:   New Nersc Source Module using SuperFacilityApi

`e917838 <https://github.com/HEPCloud/decisionengine_modules/commit/e9178383a118d193377615c0cda7d0bb05057068>`_:   Adding DE modules EL9 CI container based on AlmaLinux9

`a5a2bae <https://github.com/HEPCloud/decisionengine_modules/commit/a5a2bae93473227283f9c69bec7f1fa81a560bb0>`_:   Update GH actions

`bdb70b0 <https://github.com/HEPCloud/decisionengine_modules/commit/bdb70b061826998a9a6d47424100655c7932a3a3>`_:   Enable some GH actions only on DE 1.7 branch

`6a22f44 <https://github.com/HEPCloud/decisionengine_modules/commit/6a22f44f2627301771822a83970a983642b9c3fa>`_:   Update runtime and devel python module versions in setup.py

`842fdc9 <https://github.com/HEPCloud/decisionengine_modules/commit/842fdc91a31879084906d71a7d0c317e5035a925>`_:   CONTINUE_IF_NO_PROXY True by default

`8906538 <https://github.com/HEPCloud/decisionengine_modules/commit/8906538884a2e49dd867ce2ebca28e5e7ebb95c9>`_:   added changes to make CONTINUE_IF_NO_PROXY configurable

`5a7bc0d <https://github.com/HEPCloud/decisionengine_modules/commit/5a7bc0dc61909ac97ea90d96de3304f05a8e8f9c>`_:   Fixed Google dependency to work fine in Python 3.9. Install via PIP succeeds

`d315736 <https://github.com/HEPCloud/decisionengine_modules/commit/d3157368ff21df34ae012794bccbb0caa3dded41>`_:   With pandas 2.x DataFrame.append() has been deprecated, use pandas.concat() instead

`0484401 <https://github.com/HEPCloud/decisionengine_modules/commit/0484401ef61ced5f1a8b37a1200c9e84b60aad7a>`_:   Address a pandas deprecation warning: FutureWarning: Calling float on a single element Series is deprecated and will raise a TypeError in the future. Use float(set.iloc[0]) instead. The warning is due to glidein_cpus that is a single element series.

`07292a4 <https://github.com/HEPCloud/decisionengine_modules/commit/07292a4ffd8f48e75685bd3d957b0ff9c8bc7b79>`_:   updated as per second round of review comments

`947e9b8 <https://github.com/HEPCloud/decisionengine_modules/commit/947e9b8f3590244fd29185b109fb4ddc1711012c>`_:   updated as per PR review comments

`e3608a0 <https://github.com/HEPCloud/decisionengine_modules/commit/e3608a0ad648157df43097b8e8fe6eaab227cd6e>`_:   fixes for python 3.6 and 3.9 unit tests failing in the CI workflow

`d8de2da <https://github.com/HEPCloud/decisionengine_modules/commit/d8de2dadaa8dfc8662cd8d4c44d6ab91378f0a34>`_:   updated as per PR#461 comment

`e6044f7 <https://github.com/HEPCloud/decisionengine_modules/commit/e6044f7603dcbdfa3c6c3ea82d05ce29329b39e3>`_:   removed escaping of quotes to conform with new API behavior

`4a59acc <https://github.com/HEPCloud/decisionengine_modules/commit/4a59accdd405e1c93c23e097318913e8f12a4a26>`_:   Upgrading isort version to fix install error w/ poetry

`7b96d46 <https://github.com/HEPCloud/decisionengine_modules/commit/7b96d46023ef714642441889701d2aa0c4221873>`_:   Started to add startd_manifests (glidein) metrics (TotalCpus, TotalSlotCpus, TotalSlots)

`2ab707f <https://github.com/HEPCloud/decisionengine_modules/commit/2ab707f1634bd9d1ee1c4299cb5f555aad7e7408>`_:   Started moving metrics into global dict

`58e62a4 <https://github.com/HEPCloud/decisionengine_modules/commit/58e62a4e9bd52d7a72cde8efefd93ded9defe796>`_:   Added Number_of_jobs metric.

`5a8a641 <https://github.com/HEPCloud/decisionengine_modules/commit/5a8a64117ab10b0fe6cb6b69c918edc2775c7284>`_:   Added license info


Release 2.0.3
-------------

Release tag skipped

Release 2.0.2
-------------

This is mainly a bug fix release.

Some features were added:
- Monotoring of the glideinwms module via Prometheus
- Initial version of a Rigetti source
- More flexible LogicEngine: Fsctory Entries categories are now configurable

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `428 <https://github.com/HEPCloud/decisionengine_modules/issues/428>`_ : Decision engine 1.7.3 bug too many open file descriptors in glide_frontend_element.py
- `427 <https://github.com/HEPCloud/decisionengine_modules/pull/427>`_ : Set CONTINUE_IF_NO_PROXY to False to allow hybrid configuration

Full list of commits since version 2.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`16e1751 <https://github.com/HEPCloud/decisionengine_modules/commit/16e17519253b85ee1cd89b9c48497f2cad14e3db>`_:   update GWMS transforms This update improves handling of factory-entries data product.

`0296667 <https://github.com/HEPCloud/decisionengine_modules/commit/0296667255c17eef466f035f1d0eb8a0255981ac>`_:   Add initial Rigetti source

`9d199a5 <https://github.com/HEPCloud/decisionengine_modules/commit/9d199a5d08adb7b5db656bbe80839679fa3ced35>`_:   Update refresh_entry_token to use context managers

`d45b799 <https://github.com/HEPCloud/decisionengine_modules/commit/d45b79928ec1848870d4dcc8be7fdb07079ee3e5>`_:   [pre-commit.ci] auto fixes from pre-commit.com hooks

`7b37e83 <https://github.com/HEPCloud/decisionengine_modules/commit/7b37e83158df45a1eef01ef172e35e334606054f>`_:   Renamed Variables (REQ_IDLE_GLIDEINS & REQ_MAX_GLIDEINS) and stored them into a global dictionary.

`d7d0849 <https://github.com/HEPCloud/decisionengine_modules/commit/d7d084929c95bc04d2f9f94306978e6ee325f829>`_:   Started moving metrics into global dict

`b1e56f0 <https://github.com/HEPCloud/decisionengine_modules/commit/b1e56f0ac41d1980500253a203c2861060225f36>`_:   added req_idle_glidens & req_max_glidens metrics

`cee9652 <https://github.com/HEPCloud/decisionengine_modules/commit/cee96523bfdd56c4f9ef1198937fc01c059c7d1f>`_:   Started to add NUMBER_OF_JOBS, NAME_OF_GROUPS, STATUS_OF_JOB METRICS

`893137c <https://github.com/HEPCloud/decisionengine_modules/commit/893137cb7f6a3e60a17abb702f7fa23646872bd4>`_:   Added Number_of_jobs metric.

`e530c10 <https://github.com/HEPCloud/decisionengine_modules/commit/e530c104360c30c013b639bbcd740e0fc00fedbf>`_:   Docker container and test setup for EL8

`ea02fc8 <https://github.com/HEPCloud/decisionengine_modules/commit/ea02fc8eeab05104fe6ac5b0b7a235f219cef34b>`_:   Test case with no glideins.

`4ae0bab <https://github.com/HEPCloud/decisionengine_modules/commit/4ae0bab9b99458c23300d08473a4148f09b93930>`_:   One monolithic factory-entries data product.

`cc6b01a <https://github.com/HEPCloud/decisionengine_modules/commit/cc6b01af421f4cb1503569da4873cf48c0b3ffd9>`_:   Merge pull request #436 from vitodb/vito_fix_de_client_call

`a6744f1 <https://github.com/HEPCloud/decisionengine_modules/commit/a6744f1d4a534fa4ef4114e0189d756aa84d600c>`_:   Fix de_client call This is required to allow de_client to get its output returned as text string rather then using a logger.

`f2057d1 <https://github.com/HEPCloud/decisionengine_modules/commit/f2057d16d2289a47c4b10ac50bd80e1d0583bf2c>`_:   Merge pull request #433 from jcpunk/coverage

`4f6dffd <https://github.com/HEPCloud/decisionengine_modules/commit/4f6dffdec19f23988d32e50809be5c6eda90fe38>`_:   Merge branch 'master' into coverage

`0922c6d <https://github.com/HEPCloud/decisionengine_modules/commit/0922c6dbfc2cd9f19f322071ac2fec511be839ba>`_:   No longer need to pin coverage version

`57a5599 <https://github.com/HEPCloud/decisionengine_modules/commit/57a5599cff8ce0d97ab6ae3a580fe6d3854ccf6a>`_:   Set upper limit version for flake8. This is needed to have pytest-flake8 and flake8 versions working together.

`6bf9b48 <https://github.com/HEPCloud/decisionengine_modules/commit/6bf9b48e3a38a46da37bfb40222b782472cf4a9f>`_:   Set default glidein params on GlideFrontendElement

`3ce646a <https://github.com/HEPCloud/decisionengine_modules/commit/3ce646a3c33087a7b6a47c67a895be2319cbbaad>`_:   Set CONTINUE_IF_NO_PROXY to False

`2290fb4 <https://github.com/HEPCloud/decisionengine_modules/commit/2290fb407fecf5a6fe4d62c6abb502dbcd6670ee>`_:   Updated release notes for 2.0.1 and porting of 1.7.3


Release 2.0.1
-------------

Patch level (bug fix) release.


Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Full list of commits since version 2.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

`97ca32a <https://github.com/HEPCloud/decisionengine_modules/commit/97ca32ad84d26b9059f6eda8988c8ddd80a0466a>`_:   Modified pre-commit bot suggestions. Avoid pyupgrade that requires python 3.7

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

`cf43119 <https://github.com/HEPCloud/decisionengine_modules/commit/cf4311949d3c5fd991d1c5c4a6a190ba53a2eb71>`_:   Set fail-fast to false to allow py3.6 tests to complete also when higher version fail. Temporarily downgraded from py3.10 to py3.9 because the condor dependency is not available yet for py3.10.

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
