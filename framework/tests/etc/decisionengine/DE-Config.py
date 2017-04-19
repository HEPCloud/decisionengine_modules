{
    'logger' : {'log_file': '%s/de_log/decision_engine_log'%(os.environ.get('HOME'),),
                'max_file_size': 200*1000000,
                'max_backup_count': 6,
            },
    'channels' : 'conf.d',

    'dataspace': {
        'filename': '%s/tmp/test-db.db'%(os.environ.get('HOME'),)
    },
}



