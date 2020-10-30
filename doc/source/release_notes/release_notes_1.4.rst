Release 1.4.1
-------------

In this release:

* Bug fixes to 1.4.0 release 

Issues fixed in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `281 <https://github.com/HEPCloud/decisionengine_modules/issues/281>`_ : New exception in NERSC newt get_usage (`4d1301e <https://github.com/HEPCloud/decisionengine_modules/commit/4d1301e9ca4d3a28856b4e8f6a4a4b82a1993fe5>`_)


Full list of commits since version 1.4.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`4d1301e <https://github.com/HEPCloud/decisionengine_modules/commit/4d1301e9ca4d3a28856b4e8f6a4a4b82a1993fe5>`_
:   decisionengine_modules/NERSC/util:  Added more 5xx codes to retry (#285)



Release 1.4.0
-------------

In this release:


* Works with python3 glideinWMS package
* Uses new AWS bill calculator
* Improved Jenkins CI pipeline

Issues fixes in this release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `59 <https://github.com/HEPCloud/decisionengine_modules/issues/59>`_ : Replace AWS Billing and GCE Billing modules with revamped bill Calculator code (`71f25ea <https://github.com/HEPCloud/decisionengine_modules/commit/71f25ead76f53355be1dc13f280880744d861cfa>`_)
- `246 <https://github.com/HEPCloud/decisionengine_modules/issues/246>`_ : Modify NERSCAllocation main() so that it can be run standalone (`11ce772 <https://github.com/HEPCloud/decisionengine_modules/commit/11ce772e808e9d2a408aaa9a4f53d1c7d19e1a7f>`_)
- `263 <https://github.com/HEPCloud/decisionengine_modules/issues/263>`_ : Python3 encodes hex strings differently, resulting in malformed htcondor classads (`13a24e4 <https://github.com/HEPCloud/decisionengine_modules/commit/13a24e4c99fb8915651200685bdd9a98b0302c61>`_)
- `255 <https://github.com/HEPCloud/decisionengine_modules/issues/255>`_ : Add option to config of condor/sources/job_q.py and slots.py (`6f65af4 <https://github.com/HEPCloud/decisionengine_modules/commit/6f65af466364f9c28480fefef0ba4136d4ff8cec>`_)

Full list of commits since version 1.3.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`42f62d3 <https://github.com/HEPCloud/decisionengine_modules/commit/42f62d3d50e88df52719c50cd7159ccdbec81e77>`_
:   remove py3 from package name

`6e56c4d <https://github.com/HEPCloud/decisionengine_modules/commit/6e56c4d2cdd7a8dee9e87adb310f4aefd5c19962>`_
:   bump version number

`6433dba <https://github.com/HEPCloud/decisionengine_modules/commit/6433dba66071a6b3c0cbfcd1c971d454013549bb>`_
:   Add support to test any branch in Jenkins for DE modules repo (#276)

`60db1b3 <https://github.com/HEPCloud/decisionengine_modules/commit/60db1b3a43e7916aca427d88c44bc56e4d7e0f09>`_
:   Accommodate breaking changes to framework's configuration system. (#273)

`13a24e4 <https://github.com/HEPCloud/decisionengine_modules/commit/13a24e4c99fb8915651200685bdd9a98b0302c61>`_
:   Fix263 (#272)

`a866e47 <https://github.com/HEPCloud/decisionengine_modules/commit/a866e479f057c485dabc15c891d050cdf7f5fcf0>`_
:   Correct 'file_cache is unavailable when using oauth2client >= 4.0.0' (#267)

`2c82064 <https://github.com/HEPCloud/decisionengine_modules/commit/2c8206479a1cbe4a1aeba31b0d0aaf69e459af00>`_
:   Fix requirements.txt for #266 (#268)

`6f65af4 <https://github.com/HEPCloud/decisionengine_modules/commit/6f65af466364f9c28480fefef0ba4136d4ff8cec>`_
:   A more generic solution for the issue 255 (#265)

`df08cb4 <https://github.com/HEPCloud/decisionengine_modules/commit/df08cb41a253460ca7a1ebc0936ed099251db611>`_
:   Speed up tests. (#264)

`057e578 <https://github.com/HEPCloud/decisionengine_modules/commit/057e5788aaf99ae87d1cd05a3e53f2c6cf897b1c>`_
:   Update Jenkins pipeline to properly test closing PR (#262)

`a28f272 <https://github.com/HEPCloud/decisionengine_modules/commit/a28f2723327a6a29fc094f92bd831b6c888185f0>`_
:   Adding Jenkins pipeline documentation (#261)

`71f25ea <https://github.com/HEPCloud/decisionengine_modules/commit/71f25ead76f53355be1dc13f280880744d861cfa>`_
:   T59 (#258)

`90b6580 <https://github.com/HEPCloud/decisionengine_modules/commit/90b658089230713b9ca7739620507603f621bce9>`_
:   Updating Jenkins pipeline configuration (#260)

`b4bd759 <https://github.com/HEPCloud/decisionengine_modules/commit/b4bd7598cd747477bcf35745b6d520a275ffdbb8>`_
:   dealing with 2 columnsindividually (#257)

`11ce772 <https://github.com/HEPCloud/decisionengine_modules/commit/11ce772e808e9d2a408aaa9a4f53d1c7d19e1a7f>`_
:   decisionengine_modules/NERSC:  Can run NerscAllocationInfo.py without (#256)

`4a70465 <https://github.com/HEPCloud/decisionengine_modules/commit/4a70465b2096e0d57aa1ed9a78aacf0dc2c9a338>`_
:   doc: add release notes
