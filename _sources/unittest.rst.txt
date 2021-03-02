Decisionengine_modules
======================

Prerequisites:
^^^^^^^^^^^^^^
.. code-block::

   yum install postgresql11 postgresql11-server
   sudo localedef -v -c -i en_US -f UTF-8 C.UTF-8 # (needed for tests)

Test
^^^^

.. code-block::

  

   git clone https://github.com/HEPCloud/decisionengine_modules
   ./decisionengine_modules/.github/actions/unittest-in-sl7-docker/entrypoint.sh
