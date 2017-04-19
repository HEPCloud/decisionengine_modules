import pytest
import os
import sys
import time
import getpass

from decisionengine.framework.dataspace.datablock import DataBlock, Header, Metadata
from decisionengine.framework.dataspace.dataspace import DataSpace

config = {
    'dataspace': {
        'filename': '/tmp/test-%s.db' % getpass.getuser()
    }
}

def are_dicts_same(x, y):
    shared_items = set(x.items()) & set(y.items())

    #print '--------------------------------'
    #print '--------------------------------'
    #print len(shared_items)
    #print shared_items
    #print '--------------------------------'
    #print len(x.items())
    #print x.items()
    #print '--------------------------------'
    #print '--------------------------------'
    if len(shared_items) != len(x.items()):
        return False
    else:
        return True

class TestDataBlock:




    def test_datablock(self):

        filename = config['dataspace']['filename']
        if os.path.exists(filename):
            os.unlink(filename)

        dataspace = DataSpace(config)

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
        metadata = Metadata(taskmanager_id, generation_time=timestamp, generation_id=generation_id)

        print 'Doing put:\nkey=%s\nvalue=%s\n\nheader=%s\n\nmetadata=%s\n\n' % (
            key, value, header, metadata)
        datablock.put(key, value, header, metadata)
        #datablock[key] = value

        print 'Doing get: key=%s ...\n' % key
        db_value = datablock.get(key)
        print db_value
        print 'Doing get_header: key=%s ...\n' % key
        db_header = datablock.get_header(key)
        print db_header
        print 'Doing get_metadata: key=%s ...\n' % key
        db_metadata = datablock.get_metadata(key)
        print db_metadata

        print 'Performing comparison of value, header and metadata ...'
        if (are_dicts_same(value, db_value) and
            are_dicts_same(header, db_header) and
            are_dicts_same(metadata, db_metadata)):
            print 'DICTS CONSISTENCY CHECK PASSED\n'
        else:
            print 'DICTS CONSISTENCY CHECK FAILED\n'

        # TEST: Insert new value for same key
        new_value = { "m2": "v2" }
        print 'Doing put:\nkey=%s\nvalue=%s\nheader=%s\nmetadata=%s\n' % (
            key, new_value, header, metadata)
        datablock.put(key, new_value, header, metadata)
        print 'Doing get: key=%s ...\n' % key
        print datablock.get(key)

        # TEST: Duplicate functionality

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

        # TEST: Insert new value on duplicated datablock
        new_value = { "m3": "v3" }
        dup_datablock.put(key, new_value, dup_datablock.get_header(key), dup_datablock.get_metadata(key))

        print dup_datablock.get(key)
        print dup_datablock.get_header(key)
        print dup_datablock.get_metadata(key)

        dataspace.close()

