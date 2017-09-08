#!/usr/bin/python
"""
A library to send newt query and return results as JSON
"""
import subprocess
import json
import urllib2
import cookielib
import os
import shutil
import filecmp
import logging

import decisionengine.framework.modules.de_logger as de_logger

logger = logging.getLogger(__name__)
#logging.basicConfig(filename='output.log', level=logging.INFO)

class NewtQuery(object):

    """
    Query NERSC information using NEWT API
    """

    def __init__(self):
        pass

    @staticmethod
    def send_query(cookie_file, renew_cookie_script, query):
        """
        Send query using NEWT API, if the cookie expires, renew the cookies and 
		rerun the query immediately. For other HTTP errors, return empty list.
        """
        cookie_file = os.path.abspath(cookie_file)
        renew_cookie_script = os.path.abspath(renew_cookie_script)

        cookie_jar = cookielib.MozillaCookieJar(cookie_file)
        try:
            cookie_jar.load() # it won't load expired cookies
        except (cookielib.LoadError, IOError):
            raise RuntimeError('error when loading cookie file')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        response = None
        while True:
            try:
                response = opener.open(query)
                break
            except urllib2.HTTPError, err:
                if (err.code == 403) and (not any(cookie_jar)):
                    subprocess.call(renew_cookie_script) # this is blocking
                    # compare if current dir == cookie file dir
                    # if not, move the cookie file there
                    cookie_dir, cookie_filename = os.path.split(cookie_file)
                    cwd = os.getcwd()
                    dirs = filecmp.dircmp(cookie_dir, cwd)
                    if dirs.left != dirs.right:
                        shutil.move(cookie_filename, cookie_file)
                    cookie_jar.load()
                    continue
                else:
                    de_logger.get_logger().info('HTTP error with code = %d when querying %s' %(err.code, query))
                    return []
            except urllib2.URLError, err:
                de_logger.get_logger().info('URL error when querying %s' %(query))
                de_logger.get_logger().info(err.args)
                return []
            except RuntimeError, e:
                de_logger.get_logger().info('unkown error when querying %s' %(query))
                return []

        data = response.read()
        values = json.loads(data)
        return values
