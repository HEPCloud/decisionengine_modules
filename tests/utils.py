#!/usr/bin/python

import classad

def input_from_file(fname):
    with open(fname) as fd:
        return eval(fd.read())

def raw_input_from_file(fname):
    with open(fname) as fd:
        return fd.read()
