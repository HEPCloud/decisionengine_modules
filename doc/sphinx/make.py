# -*- coding: utf-8 -*-

"""
Make HTML developer documentation files for Decision Engine using Sphinx.
"""

# Python imports
#from __future__ import print_function
import argparse
import distutils.spawn
import os
import subprocess
import sys

# Parse arguments
parser = argparse.ArgumentParser(description=__doc__.strip())

parser.add_argument('builddir',
                    help=('Build directory'))
args = parser.parse_args()

# Test Sphinx for availability
try:
    import sphinx
except ImportError:
    msg = ('Sphinx could not be imported. '
           'To install it for Python 2.7.9 or newer, run as root:\n'
           '\tpython -m ensurepip --upgrade\n'
           '\tpip install --upgrade pip\n'
           '\tpip install --upgrade sphinx')
    exit(msg)
# Note: Minimal version requirement for Sphinx is defined in source/conf.py.

# Test Graphviz dot for availability
if distutils.spawn.find_executable('dot') is None:
    msg = ("The Graphviz dot executable is required but could not be found. "
           "To install its x86_64 RPM, run:\n"
           "\tyum install graphviz.x86_64")
    exit(msg)

# Determine make directory
make_dir = os.path.abspath(os.path.dirname(__file__))
py_rst_dir = os.path.join(make_dir, 'source', 'modules')

# Determine and export build directory
build_dir = os.path.abspath(args.builddir)
os.environ['BUILDDIR'] = build_dir
# Note: The build directory is created automatically if it doesn't exist.

print("""The HTML directory path is printed after the build has finished.

General troubleshooting steps:
• If the HTML output fails to get generated for a Python module, ensure the
  module can be imported by Python, and that its .rst file exists in
  {}.
• If the HTML output exists but fails to get updated for a Python module,
  "touch" the module's .rst file.
""".format(py_rst_dir))

# GNU make
make_cmd = 'make --directory="{}" html'.format(make_dir)
make_exit_status = subprocess.call(make_cmd, shell=True)
# Note: Not using "shell=True" raises "OSError: [Errno 2]".
exit(make_exit_status)
