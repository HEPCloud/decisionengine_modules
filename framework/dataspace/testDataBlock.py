#!/usr/bin/python

from dataspace import DataSpace
from datablock import DataBlock, duplicate
import os

filename = '/tmp/test-wdd.db'

if os.path.exists(filename):
    os.unlink(filename)

dataspace = DataSpace(filename)

dataspace.create()

datablock_id = 1
generation_id = 1

datablock = DataBlock(datablock_id, generation_id, dataspace)

key = 'aKey'
value = { "m1": "v1" }

#datablock.put(key, value)
datablock[key] = value

print datablock.get(key)

newValue = { "m2": "v2" }
datablock.put(key, newValue)

print datablock.get(key)

newdatablock = duplicate(datablock)

print newdatablock.get(key)

newValue = { "m3": "v3" }
newdatablock.put(key, newValue)

print newdatablock.get(key)

dataspace.close()

