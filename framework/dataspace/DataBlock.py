#!/usr/bin/python

import time

from UserDict import UserDict

"""
HEADER = {
    datablock_id: 0,
    create_time: 0,
    expiration_time: 0,
    scheduled_create_time: 0,
    creator: 'a',
    schema_id: 0
}

METADATA = {
    datablock_id: 0,
    state: ('NEW', 'START_BACKUP', 'METADATA_UPDATE', 'END_CYCLE'),
    generation_id: 0, # Not sure what this is??
    generation_time: 0,
    missed_update_count: 0,
}

"""


class InvalidMetadataError(Exception):
    """
    Errors due to invalid Metadata
    """
    pass


class Metadata(UserDict):

    # Minimum information required for the Metadata dict to be valid
    required_keys = set(['datablock_id', 'state', 'generation_id',
                         'generation_time', 'missed_update_count'])

    # Valid states
    valid_states = set(['NEW', 'START_BACKUP', 'METADATA_UPDATE', 'END_CYCLE'])

    def __init__(self, datablock_id, state='NEW', generation_id=None,
                 generation_time=None, missed_update_count=0):

        if not state in Metadata.valid_states:
            raise InvalidMetadataError('Invalid Metadata state "%s"' % state)
        if not generation_time:
            generation_time = time.time()

        self.data = {
            'datablock_id': datablock_id,
            'state': state,
            'generation_id': generation_id,
            'generation_time': generation_time,
            'missed_update_count': missed_update_count
        }


    def set_state(self, state):
        """
        Set the state for the Metadata
        """

        if not state in Metadata.valid_states:
            raise InvalidMetadataError('%s is not a valid Metadata state' % state)
        self.data['state'] = state


class Header(UserDict):

    # Minimum information required for the Header dict to be valid
    required_keys = set(['datablock_id', 'create_time', 'expiration_time',
                         'scheduled_create_time', 'creator', 'schema_id'])

    # Default lifetime of the data if the expiration time is not specified
    default_data_lifetime = 1800

    def __init__(self, datablock_id, create_time=None, expiration_time=None,
                 scheduled_create_time=None, creator='module', schema_id=None):

        if not create_time:
            create_time = time.time()
        if not expiration_time:
            expiration_time = create_time + Header.default_data_lifetime
        if not scheduled_create_time:
            scheduled_create_time = time.time()

        self.data = {
            'datablock_id': datablock_id,
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

    def __init__(self):
        self.id = 1111


    def put(self, key, value):
        header = None
        metadata = None
        data = None

        # Generate Header

        # Generate Metadata

        # Store data product to the database

        return (data, header, metadata)

    def get(self, key):
        """
        Return the value associated with the key in the database
        """
        pass


    def get_header(self, key):
        """
        Return the header associated with the key in the database
        """
        pass


    def get_metadata(self, key):
        """
        Return the metadata associated with the key in the database
        """
        pass


def duplicate(datablock_id):
    """
    Duplicate the datablock with the given id and return id of the new
    datablock created. Only information from the sources is backed up.
    """

    dup_db_id = None
    # Can be handled with subquery
    # Create a new datablock from the source data of existing datablock


    # return the datablock_id of the duplicate created
    return dup_db_id
