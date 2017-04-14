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
            'taskmanager_id INT',
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


    def execute(self, cmd):
        cursor = self.conn.cursor()
        cursor.execute(cmd)
        self.conn.commit()


    def create(self):
        for table, cols in DataSpace.tables.iteritems():
            if isinstance(cols, list):
                try:
                    cmd = """CREATE TABLE %s (%s)""" % (table, ', '.join(str(c) for c in cols))
                    self.execute(cmd)
                except:
                    traceback.print_stack()
                    raise DataSpaceError('Error creating table %s' % table)


    def insert(self, taskmanager_id, generation_id, key, value): 
        try:
            cmd = """INSERT INTO %s VALUES (%i, %i, "%s", "%s")""" % (
                DataSpace.datablock_table, taskmanager_id, generation_id,
                key, value)
            self.execute(cmd)
        except:
            traceback.print_stack()
            raise DataSpaceError('Error creating table %s' % DataSpace.datablock_table)


    def update(self, taskmanager_id, generation_id, key, value): 
        try:
            cmd = """UPDATE datablock SET value="%s" WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))""" % value
            params = (taskmanager_id, generation_id, key)
            cursor = self.conn.cursor()
            cursor.execute(cmd, params)
        except:
            raise
            traceback.print_stack()
            raise DataSpaceError('Error updating table %s' % DataSpace.datablock_table)


    def get(self, taskmanager_id, generation_id, key): 
        try:
            template = (taskmanager_id, generation_id, key)
            
            #print cmd
            cmd = """SELECT value FROM datablock WHERE ((taskmanager_id=?) AND (generation_id=?) AND (key=?))"""
            params = (taskmanager_id, generation_id, key)

            cursor = self.conn.cursor()
            cursor.execute(cmd, params)
            value = cursor.fetchall()

            #self.execute(cmd)
        except:
            raise
            traceback.print_stack()
            raise DataSpaceError('Error creating table %s' % DataSpace.datablock_table)

        #return value[-1][0]
        return value


    def duplicate(self, taskmanager_id, generation_id, new_generation_id):

        cursor = self.conn.cursor()
        
        cmd = """INSERT INTO datablock (taskmanager_id, generation_id, key, value) SELECT taskmanager_id, %i, key, value FROM datablock WHERE (taskmanager_id=?) AND (generation_id=?)   """ % (new_generation_id)
        params = (taskmanager_id, generation_id)
        cursor = self.conn.cursor()
        cursor.execute(cmd, params)
        self.conn.commit()
