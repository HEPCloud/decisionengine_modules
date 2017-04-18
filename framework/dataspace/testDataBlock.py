#!/usr/bin/python
import os
import sys
import time

from dataspace import DataSpace
from datablock import DataBlock, Header, Metadata

config = {
    'dataspace': {
        'filename': '/tmp/test-wdd.db'
    }
}

filename = config['dataspace']['filename']
if os.path.exists(filename):
    os.unlink(filename)

print 'creating dataspace object ... %s\n' % filename
dataspace = DataSpace(config)

print 'creating dataspace tables ...\n'
dataspace.create()

taskmanager_id = 'E0B9A7F5-B55E-47F6-B5EF-DCCB8B977AFE'
generation_id = 9999
print 'Using taskmanager id = %s\n' % taskmanager_id

print 'creating datablock object ...\n'
datablock = DataBlock(dataspace, taskmanager_id, generation_id=9999)

timestamp = time.time()
key = 'aKey'
value = { "m1": "v1" }
header = Header(taskmanager_id, create_time=timestamp,
                scheduled_create_time=timestamp+600,
                schema_id=0)
metadata = Metadata(taskmanager_id, generation_time=timestamp)

print 'Doing put:\nkey=%s\nvalue=%s\nheader=%s\nmetadata=%s\n' % (
    key, value, header, metadata)
datablock.put(key, value, header, metadata)
#datablock[key] = value

print 'Doing get: key=%s ...\n' % key
print datablock.get(key)
print 'Doing get_header: key=%s ...\n' % key
print datablock.get_header(key)
print 'Doing get_metadata: key=%s ...\n' % key
print datablock.get_metadata(key)


new_value = { "m2": "v2" }
print 'Doing put:\nkey=%s\nvalue=%s\nheader=%s\nmetadata=%s\n' % (
    key, new_value, header, metadata)
datablock.put(key, new_value, header, metadata)
print 'Doing get: key=%s ...\n' % key
print datablock.get(key)

print '-----------------------'
print 'Duplicating datablock ...\n'
dup_datablock = datablock.duplicate()

print '---'
print 'Doing get: key=%s ...\n' % key
print datablock.get(key)
print 'Doing get_header: key=%s ...\n' % key
print datablock.get_header(key)
print 'Doing get_metadata: key=%s ...\n' % key
print datablock.get_metadata(key)
print '---'
print 'Doing get on dup_datablock: key=%s\n' % key
print dup_datablock.get(key)
print 'Doing get_header on dup_datablock: key=%s ...\n' % key
print dup_datablock.get_header(key)
print 'Doing get_metadata on dup_datablock: key=%s ...\n' % key
print dup_datablock.get_metadata(key)
print '---'

new_value = { "m3": "v3" }
dup_datablock.put(key, new_value, dup_datablock.get_header(key), dup_datablock.get_metadata(key))

print dup_datablock.get(key)
print dup_datablock.get_header(key)
print dup_datablock.get_metadata(key)

dataspace.close()

sys.exit(0)
