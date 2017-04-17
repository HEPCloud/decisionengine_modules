#!/usr/bin/python

import time
import sqlite3
import traceback

from UserDict import UserDict

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
        'header': None,
        'metadata': None,
        'datablock': [
            'datablock_id INT',
            'generation_id INT',
            'key TEXT',
            'value BLOB'
        ]
    }

    datablock_table = 'datablock'


    def __init__(self, db_filename, credentials=None):
        self.db_filename = db_filename
        self.credentials = credentials
        try:
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
        for table, cols in DataSpace.tables.iteritems():
            if isinstance(cols, list):
                try:
                    cmd = """CREATE TABLE %s (%s)""" % (table, ', '.join(str(c) for c in cols))
                    self._execute(cmd)
                except:
                    traceback.print_stack()
                    raise DataSpaceError('Error creating table %s' % table)


    def insert(self, datablock_id, generation_id, key, value):
        try:
            cmd = """INSERT INTO %s VALUES (%i, %i, "%s", "%s")""" % (
                DataSpace.datablock_table, datablock_id, generation_id,
                key, value)
            self._execute(cmd)
        except:
            traceback.print_stack()
            raise DataSpaceError('Error creating table %s' % DataSpace.datablock_table)


    def update(self, datablock_id, generation_id, key, value):
        try:
            cmd = """UPDATE datablock SET value="%s" WHERE ((datablock_id=?) AND (generation_id=?) AND (key=?))""" % value
            params = (datablock_id, generation_id, key)
            cursor = self.conn.cursor()
            cursor.execute(cmd, params)
        except:
            raise
            traceback.print_stack()
            raise DataSpaceError('Error updating table %s' % DataSpace.datablock_table)


    def get(self, datablock_id, generation_id, key):
        try:
            template = (datablock_id, generation_id, key)
            
            #print cmd
            cmd = """SELECT value FROM datablock WHERE ((datablock_id=?) AND (generation_id=?) AND (key=?))"""
            params = (datablock_id, generation_id, key)

            cursor = self.conn.cursor()
            cursor.execute(cmd, params)
            value = cursor.fetchall()

            #self._execute(cmd)
        except:
            raise
            traceback.print_stack()
            raise DataSpaceError('Error creating table %s' % DataSpace.datablock_table)

        #return value[-1][0]
        return value


    def duplicate(self, datablock_id, generation_id, new_generation_id):

        cursor = self.conn.cursor()
        
        cmd = """INSERT INTO datablock (datablock_id, generation_id, key, value) SELECT datablock_id, %i, key, value FROM datablock WHERE (datablock_id=?) AND (generation_id=?)   """ % (new_generation_id)
        params = (datablock_id, generation_id)
        cursor = self.conn.cursor()
        cursor.execute(cmd, params)
        self.conn.commit()


    def delete(self, datablock_id, all_generations=False):
        # Remove the latest generation of the datablock
        # If asked, remove all generations of the datablock
        pass
