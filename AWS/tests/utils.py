#!/usr/bin/python

import classad
import datetime

def input_from_file(fname):
    with open(fname) as fd:
        return eval(fd.read())

def raw_input_from_file(fname):
    with open(fname) as fd:
        return fd.read()
