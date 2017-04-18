#!/usr/bin/python

#import time
import sqlite3
import traceback

#from UserDict import UserDict


class DataSpaceConnectionError(Exception):
    """
    Errors related to database access
    """
    pass


class DataSpaceError(Exception):
    """
    Errors related to database access
    """
    pass


class DataSpace(object):

    tables = {
        'header': [
            'taskmanager_id TEXT',
            'generation_id INT',
            'key TEXT',
            'create_time REAL',
            'expiration_time REAL',
            'scheduled_create_time REAL',
            'creator TEXT',
            'schema_id INT',
        ],
        'schema': [
            'schema_id INT', # Auto generated
            'schema BLOB',   # keys in the value dict of the dataproduct table
        ],
        'metadata': [
            'taskmanager_id TEXT',
            'generation_id INT',
            'key TEXT',
            'state TEXT',
            'generation_time REAL',
            'missed_update_count INT',
        ],
        'dataproduct': [
            'taskmanager_id TEXT',
            'generation_id INT',
            'key TEXT',
            'value BLOB'
        ]
    }

    dataproduct_table = 'dataproduct'
    header_table = 'header'
    metadata_table = 'metadata'

    def __init__(self, config, credentials=None):
        self.db_filename = config['dataspace']['filename']
        self.credentials = credentials

        try:
            # Creates DB if it does not exist
            self.conn = sqlite3.connect(self.db_filename)
        except:
            raise DataSpaceConnectionError(
                'Error connecting to the database %s' % db_filename)

    def close(self):
        self.conn.close()


    def _execute(self, cmd):
        cursor = self.conn.cursor()
        cursor.execute(cmd)
        self.conn.commit()


    def create(self):
        # TODO: implement dataspace creation from config
        # Create the necessary tables for the datablocks
        # Should be called only once or ignore if tables created
        # TODO: Need to add functionality to ignore if tables exist

        try:
            for table, cols in DataSpace.tables.iteritems():
                if isinstance(cols, list):
                    cmd = """CREATE TABLE %s (%s)""" % (table, ', '.join(str(c) for c in cols))
                    cursor = self.conn.cursor()
                    cursor.execute(cmd)
            self.conn.commit()
        except:
             raise
             #traceback.print_stack()
             #raise DataSpaceError('Error creating table %s' % table)


    def get_last_generation_id(self, taskmanager_id):
        # TODO: COALESCE is not safe. Find a better way check with DB experts
        try:
            cmd = """SELECT COALESCE(MAX(generation_id),0) FROM %s""" % DataSpace.dataproduct_table

            cursor = self.conn.cursor()
            cursor.execute(cmd)
            value = cursor.fetchall()   
	except:
            raise
        return value[0][0]


    def insert(self, taskmanager_id, generation_id, key, value, header, metadata):
        # Insert the data product, header and metadata to the database
        try:
            # Insert value in the dataproduct table
            cmd = """INSERT INTO %s VALUES ("%s", %i, "%s", "%s")""" % (
                DataSpace.dataproduct_table, taskmanager_id, generation_id,
                key, value)
            cursor = self.conn.cursor()
            cursor.execute(cmd)
  
            # Insert header in the header table
            cmd = """INSERT INTO %s VALUES ("%s", %i, "%s", %f, %f, %f, "%s", "%s")""" % (
                DataSpace.header_table, taskmanager_id, generation_id,
                key, header.get('create_time'), header.get('expiration_time'),
                header.get('scheduled_create_time'), header.get('creator'),
                header.get('schema_id'))
            cursor = self.conn.cursor()
            cursor.execute(cmd)

            # Insert metadata in the metadata table
            cmd = """INSERT INTO %s VALUES ("%s", %i, "%s", "%s", %f, %i)""" % (
                DataSpace.metadata_table, taskmanager_id, generation_id,
                key, metadata.get('state'), metadata.get('generation_time'),
                metadata.get('missed_update_count'))
            #print '=========== cmd ==========='
            #print cmd
            #print '=========== cmd ==========='
            cursor = self.conn.cursor()
            cursor.execute(cmd)

            # Commit data/header/metadata as a single transaction
            self.conn.commit()
        except:
            raise
            #traceback.print_stack()
            #raise DataSpaceError('Error creating table %s' % DataSpace.dataproduct_table)


    def update(self, taskmanager_id, generation_id, key, value, header, metadata):
        # Update the data product, header and metadata in the database
        try:
            params = (taskmanager_id, generation_id, key)
            cmd = """UPDATE %s SET value="%s" WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))""" % (DataSpace.dataproduct_table, value)
            cursor = self.conn.cursor()
            cursor.execute(cmd, params)

            cmd = """UPDATE %s SET create_time=%f, expiration_time=%f, scheduled_create_time=%f, creator="%s", schema_id=%i WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))""" % (DataSpace.header_table,
                header.get('create_time'), header.get('expiration_time'),
                header.get('scheduled_create_time'), header.get('creator'),
                header.get('schema_id'))
            cursor = self.conn.cursor()
            cursor.execute(cmd, params)

            cmd = """UPDATE %s SET state="%s", generation_time=%f, missed_update_count=%i WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))""" % (
                DataSpace.metadata_table, metadata.get('state'),
                metadata.get('generation_time'),
                metadata.get('missed_update_count'))
            cursor = self.conn.cursor()
            cursor.execute(cmd, params)

            # Commit data/header/metadata as a single transaction
            self.conn.commit()
        except:
            raise
            #traceback.print_stack()
            #raise DataSpaceError('Error updating table %s' % DataSpace.dataproduct_table)


    def _get_table_row(self, table, taskmanager_id,
                       generation_id, key, cols=None):
        # Get the data product from the database

        if not cols:
            cols = ['*']
        try:
            template = (taskmanager_id, generation_id, key)
            
            #print cmd
            cmd = """SELECT %s FROM %s WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))""" % (', '.join(str(c) for c in cols), table)
            params = (taskmanager_id, generation_id, key)

            cursor = self.conn.cursor()
            cursor.execute(cmd, params)
            value = cursor.fetchall()

            #self._execute(cmd)
        except:
            raise
            #traceback.print_stack()
            #raise DataSpaceError('Error creating table %s' % DataSpace.dataproduct_table)

        return value[-1]
        #return value


    def get_dataproduct(self, taskmanager_id, generation_id, key):
        value = self._get_table_row(DataSpace.dataproduct_table, taskmanager_id,
                                    generation_id, key, ['value'])
        return value


    def get_header(self, taskmanager_id, generation_id, key):
        cols = [(x.split())[0] for x in DataSpace.tables.get(DataSpace.header_table)]
        return self._get_table_row(DataSpace.header_table, taskmanager_id,
                                   generation_id, key, cols)


    def get_metadata(self, taskmanager_id, generation_id, key):
        cols = [(x.split())[0] for x in DataSpace.tables.get(DataSpace.metadata_table)]
        return self._get_table_row(DataSpace.metadata_table, taskmanager_id,
                                   generation_id, key, cols)


    def duplicate(self, taskmanager_id, generation_id, new_generation_id):

        cursor = self.conn.cursor()

        params = (taskmanager_id, generation_id)

        cmd = """INSERT INTO %s (taskmanager_id, generation_id, key, value) SELECT taskmanager_id, %i, key, value FROM %s WHERE (taskmanager_id=?) AND (generation_id=?)""" % (
            DataSpace.dataproduct_table, new_generation_id,
            DataSpace.dataproduct_table)
        cursor = self.conn.cursor()
        cursor.execute(cmd, params)

        cmd = """INSERT INTO %s (taskmanager_id, generation_id, key, create_time, expiration_time, scheduled_create_time, creator, schema_id) SELECT taskmanager_id, %i, key, create_time, expiration_time, scheduled_create_time, creator, schema_id FROM %s WHERE (taskmanager_id=?) AND (generation_id=?)""" % (
            DataSpace.header_table, new_generation_id,
            DataSpace.header_table)
        cursor = self.conn.cursor()
        cursor.execute(cmd, params)

        cmd = """INSERT INTO %s (taskmanager_id, generation_id, key, state, generation_time, missed_update_count) SELECT taskmanager_id, %i, key, state, generation_time, missed_update_count FROM %s WHERE (taskmanager_id=?) AND (generation_id=?)""" % (
            DataSpace.metadata_table, new_generation_id,
            DataSpace.metadata_table)
        cursor = self.conn.cursor()
        cursor.execute(cmd, params)

        self.conn.commit()


    def delete(self, taskmanager_id, all_generations=False):
        # Remove the latest generation of the datablock
        # If asked, remove all generations of the datablock
        pass
