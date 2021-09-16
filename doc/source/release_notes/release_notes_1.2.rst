Release 1.2.0
-------------

In this release:

* Switched to python3
* NERSC newt interface adapted to changed NERSC RESTful API
* Improved unit tests
* Added Jenkins CI pipeline


Patches:
~~~~~~~~

`30d928b <https://github.com/HEPCloud/decisionengine_modules/commit/30d928b67a442206ad7fe7114b44ff6a2b9ff404>`_
:   clone version 1.2.0 of decisionengine

`ae7c5a6 <https://github.com/HEPCloud/decisionengine_modules/commit/ae7c5a6b9985e2270459635f315fd30a706352f8>`_
:   Jenkins pipeline improvements (#236)

`310befd <https://github.com/HEPCloud/decisionengine_modules/commit/310befdbf805fd6168132b852b881a4c6f5ed9dc>`_
:   T198 (#235)

`a65886d <https://github.com/HEPCloud/decisionengine_modules/commit/a65886d0a52ffd8b898a7daebe3ab155466c0820>`_
:   Fix import as reported in : https://github.com/HEPCloud/decisionengin… (#232)

`93711cc <https://github.com/HEPCloud/decisionengine_modules/commit/93711ccd802c8ee99ecfa9b9f824ae312c5b8d89>`_
:   Run coveralls even if tests fail (#229)

`03d763a <https://github.com/HEPCloud/decisionengine_modules/commit/03d763ae2646f5bbdbdbffffed0735daf68fc830>`_
:   Jenkins pipeline improvements (#230)

`f48d30f <https://github.com/HEPCloud/decisionengine_modules/commit/f48d30fa1e436b602f5a5f7c35645b97f3db6d83>`_
:   Fix/223 (#228)

`c8aa262 <https://github.com/HEPCloud/decisionengine_modules/commit/c8aa262964f7cd3891a8421fbaad9667d8e4f525>`_
:   github ticket 199 (#222)

`0323bda <https://github.com/HEPCloud/decisionengine_modules/commit/0323bda0241903ab8cc57fd37e66bbfcd40c412c>`_
:   Address : https://github.com/HEPCloud/decisionengine_modules/issues/224 (#226)

`62e4df6 <https://github.com/HEPCloud/decisionengine_modules/commit/62e4df697fe290f0780b8e10fc81727fdc31dfc1>`_
:   Add support to run CI on Jenkins (#221)

`5ab1541 <https://github.com/HEPCloud/decisionengine_modules/commit/5ab15411b79505d752cf21c3b2ec15213bd83be3>`_
:   bump master version to 1.2.0 (for now) (#219)

`bc19c65 <https://github.com/HEPCloud/decisionengine_modules/commit/bc19c6528ab89922a95465c3c67c60273255e039>`_
:   decisionengine_modules/NERSC: Added retry loop for NERSC API Calls (#220)

`41a50de <https://github.com/HEPCloud/decisionengine_modules/commit/41a50de88209542fd5ed15a8b529794a3ff66098>`_
:   Sync up pep8speaks and run_pylint.sh with decisionengine settings (#218)

`db4634f <https://github.com/HEPCloud/decisionengine_modules/commit/db4634f89f35b8f5dde6bac11ad5b66a756d68ed>`_
:   silence pylint error (#217)

`1b95141 <https://github.com/HEPCloud/decisionengine_modules/commit/1b95141a7ae7ef9f9b9d8a6da1cf7c69acc35379>`_
:   Fix whitespace around operator error

`746ea38 <https://github.com/HEPCloud/decisionengine_modules/commit/746ea38446c5908e5b24184299ce5e3b6eb6c0e9>`_
:   ignore W503

`8a8b5f4 <https://github.com/HEPCloud/decisionengine_modules/commit/8a8b5f4277a2d005249c4f75c03edb1e4408d800>`_
:   remove unused variable

`a6668bf <https://github.com/HEPCloud/decisionengine_modules/commit/a6668bf2b18cfd770be377419126e17004053e7c>`_
:   fix PEP8 warnings

`13773ee <https://github.com/HEPCloud/decisionengine_modules/commit/13773ee0ae5a25c5fd5bfc62feb1b899d2010bb4>`_
:   address pep8 warnings

`6bea4ca <https://github.com/HEPCloud/decisionengine_modules/commit/6bea4cadd184bbefd2339dcece2a2db2fe27c39d>`_
:   silence pylint error

`f589895 <https://github.com/HEPCloud/decisionengine_modules/commit/f5898958cd10f99137333ec314fc4cfecc97bcff>`_
:   Pass sort=True parameter to fix future warning (#215)

`a1d0507 <https://github.com/HEPCloud/decisionengine_modules/commit/a1d0507b62fc0fbe5386cdaf518e23702bf53159>`_
:   fixing pep8 warning

`a10bd17 <https://github.com/HEPCloud/decisionengine_modules/commit/a10bd17ed8160d1397c3d2c4462e39c60dd1b8b4>`_
:   debugging one import error

`ec501ad <https://github.com/HEPCloud/decisionengine_modules/commit/ec501ad738ef885e70e08dad59f15b2db555fc1c>`_
:   make coveralls.io links work

`deab1a7 <https://github.com/HEPCloud/decisionengine_modules/commit/deab1a77eac6a8a4315bdedf4fc1241df032b25e>`_
:   T201 (#204)

`69f2645 <https://github.com/HEPCloud/decisionengine_modules/commit/69f26451705f3d2b7336bb98db2387b70f0ba329>`_
:   Add coveragerc

`6d8a5f5 <https://github.com/HEPCloud/decisionengine_modules/commit/6d8a5f5f45159c18b2b79efab7e1dcabedbe039a>`_
:   decisionengine_modules/NERSC: Make Nersc API call backward-compatible with old config (#196)

`a7e0af9 <https://github.com/HEPCloud/decisionengine_modules/commit/a7e0af9572cc62987008dd8d7164cc1efc37921f>`_
:   Only run Github Actions for python3.6 (#24)
