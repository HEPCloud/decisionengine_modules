#!/usr/bin/python

import time
import copy
import cPickle as pickle
import ast
import uuid

from UserDict import UserDict

# from dataspace import DataSpace

###############################################################################
# TODO:
# 1) Need to make sure there are no race conditions
# 2) Add mutex/locks/critical sections where ever required
# 3) Manipulations on the Header functionality
# 4) Manipulations on the Metadata functionality
# 5) get() needs to error in case of expired data
###############################################################################

STATE_NEW = 'NEW'
STATE_STEADY = 'STEADY'
STATE_ERROR = 'ERROR'


class KeyNotFoundError(Exception):
    """
    Errors due to invalid Metadata
    """
    pass


class InvalidMetadataError(Exception):
    """
    Errors due to invalid Metadata
    """
    pass


class Metadata(UserDict):

    # Minimum information required for the Metadata dict to be valid
    required_keys = {
        'taskmanager_id', 'state', 'generation_id',
        'generation_time', 'missed_update_count'}

    # Valid states
    valid_states = {'NEW', 'START_BACKUP', 'METADATA_UPDATE', 'END_CYCLE'}

    def __init__(self, taskmanager_id, state='NEW', generation_id=None,
                 generation_time=None, missed_update_count=0):

        UserDict.__init__(self)
        if state not in Metadata.valid_states:
            raise InvalidMetadataError('Invalid Metadata state "%s"' % state)
        if not generation_time:
            generation_time = time.time()

        self.data = {
            'taskmanager_id': taskmanager_id,
            'state': state,
            'generation_id': generation_id,
            'generation_time': generation_time,
            'missed_update_count': missed_update_count
        }


    def set_state(self, state):
        """
        Set the state for the Metadata
        """

        if state not in Metadata.valid_states:
            raise InvalidMetadataError('%s is not a valid Metadata state' % state)
        self.data['state'] = state


class Header(UserDict):

    # Minimum information required for the Header dict to be valid
    required_keys = {
        'taskmanager_id', 'create_time', 'expiration_time',
        'scheduled_create_time', 'creator', 'schema_id'
    }

    # Default lifetime of the data if the expiration time is not specified
    default_data_lifetime = 1800

    def __init__(self, taskmanager_id, create_time=None, expiration_time=None,
                 scheduled_create_time=None, creator='module', schema_id=None):

        UserDict.__init__(self)
        if not create_time:
            create_time = time.time()
        if not expiration_time:
            expiration_time = create_time + Header.default_data_lifetime
        if not scheduled_create_time:
            scheduled_create_time = time.time()

        self.data = {
            'taskmanager_id': taskmanager_id,
            'create_time': create_time,
            'expiration_time': expiration_time,
            'scheduled_create_time': scheduled_create_time,
            'creator': creator,
            'schema_id': schema_id
        }


    def is_valid(self):
        """
        Check if the Header has minimum required information
        """

        return set(self.data.keys()).issubset(Header.required_keys)


class DataBlock(object):

    def __init__(self, dataspace, taskmanager_id=None, generation_id=None):
        self.dataspace = dataspace

        # If taskmanager_id is None create new or 
        if taskmanager_id:
            self.taskmanager_id = taskmanager_id
        else:
            self.taskmanager_id = ('%s' % uuid.uuid1()).upper()

        if generation_id:
            self.generation_id = generation_id
        else:
            self.generation_id = self.dataspace.get_last_generation_id(taskmanager_id) + 1
        self.keys_inserted = []


    def put(self, key, value, header, metadata):
        self.__setitem__(key, value, header, metadata)


    def get(self, key):
        return self.__getitem__(key)


    def _insert(self, key, value, header, metadata):
        # Store data product, header and metadata to the database
        self.dataspace.insert(self.taskmanager_id, self.generation_id,
                              key, value, header, metadata)
        self.keys_inserted.append(key)


    def _update(self, key, value, header, metadata):
        # Update data product, header and metadata to the database
        self.dataspace.update(self.taskmanager_id, self.generation_id,
                              key, value, header, metadata)


    def __setitem__(self, key, value, header, metadata):

        if isinstance(value, dict):
            store_value = {'pickled': False, 'value': value}
        else:
            store_value = {'pickled': True, 'value': pickle.dumps(value)}

        if key in self.keys_inserted:
            # This has been already inserted, so you are working on a copy
            # that was backedup. You need to update and adjust the update
            # counter
            self._update(key, store_value, header, metadata)
        else:
            self._insert(key, store_value, header, metadata)


    def __getitem__(self, key, default=None):
        """
        Return the value associated with the key in the database
        """

        try:
            value_row = self.dataspace.get_dataproduct(self.taskmanager_id,
                                                       self.generation_id, key)
            value = ast.literal_eval(value_row[0])
        except KeyNotFoundError, e:
            value = default
        except:
            # TODO: FINSIH with more exceptions, content
            raise

        #print '-------'
        #print value
        if value.get('pickled'):
            return_value = pickle.loads(value.get('value'))
        else:
            return_value = value.get('value')
        return return_value


    def get_header(self, key):
        """
        Return the header associated with the key in the database
        """
        try:
            header_row = self.dataspace.get_header(self.taskmanager_id,
                                                   self.generation_id, key)
            header = Header(header_row[0], create_time=header_row[3],
                            expiration_time=header_row[4],
                            scheduled_create_time=header_row[5],
                            creator=header_row[6],
                            schema_id=header_row[7])
        #except KeyNotFoundError, e:
        #    value = default
        except:
            # TODO: FINSIH with more exceptions, content
            raise
        return header


    def get_metadata(self, key):
        """
        Return the metadata associated with the key in the database
        """
        try:
            metadata_row = self.dataspace.get_metadata(self.taskmanager_id,
                                                       self.generation_id, key)
            metadata = Metadata(metadata_row[0], state=metadata_row[3],
                                generation_id=metadata_row[1],
                                generation_time=metadata_row[4],
                                missed_update_count=metadata_row[5])
        #except KeyNotFoundError, e:
        #    value = default
        except:
            # TODO: FINSIH with more exceptions, content
            raise
        return metadata


    def duplicate(self):
        """
        Duplicate the datablock with the given id and return id of the new
        datablock created. Only information from the sources is backed up.
        TODO: Also update the header and the metadata information
        TODO: Make this threadsafe
        """

        dup_datablock = copy.copy(self)
        self.generation_id += 1
        dup_datablock.keys_inserted = copy.deepcopy(self.keys_inserted)
        self.dataspace.duplicate(self.taskmanager_id,
                                 dup_datablock.generation_id,
                                 self.generation_id)
        return dup_datablock
