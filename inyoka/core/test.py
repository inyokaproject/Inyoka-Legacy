#-*- coding: utf-8 -*-
"""
    inyoka.core.test
    ~~~~~~~~~~~~~~~~

    This module abstracts nosetest and provides an interface for our unittests
    and doctests.  It also implements various helper classes and functions.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
import os
import sys
import urlparse
import shutil
import unittest
import tempfile
import nose
from os import path
from functools import update_wrapper
from werkzeug import Client, BaseResponse
from nose.plugins.base import Plugin
from inyoka.core.api import config, db, get_application, href, logger

# disable the logger
logger.disabled = True


MESSAGE_TEMPLATE = '''
From: %s
To: %s
Subject: %s
Message: %s'''


csrf_token_re = re.compile(r'<input\s+.*?name=[\'"]_form_token[\'"]\s+.*?value=[\'"](.*?)[\'"][^>]*?>(?is)')


class Context(object):
    """
    This is the context for our tests. It provides
    some required things like the `admin` and `user`
    attributes to create a overall test experience.
    """
    admin = None
    res_dir = None
    anonymous = None
    instance_dir = None

    def setup_instance(self, instance_dir):
        """
        Setup the test context. That means: Create an admin
        and normal test user and patch required libraries.
        """
        self.instance_dir = instance_dir
        #TODO: setup admin, anonymous once models are up again

    def teardown_instance(self):
        db.session.rollback()
        db.session.expunge_all()
        db.metadata.drop_all()
        try:
            os.rmdir(self.instance_dir)
        except:
            # fail silently
            pass

context = Context()

class ResponseWrapper(object):

    def __init__(self, app, status, headers):
        self.app = app
        self.status = status
        self.headers = headers


class ViewTestCase(unittest.TestCase):

    component = 'portal'
    response = None
    client = Client(get_application(), response_wrapper=ResponseWrapper)

    def open_location(self, path, method='GET', **kwargs):
        """Open a location (path)"""
        if not 'follow_redirects' in kwargs:
            kwargs['follow_redirects'] = True
        self.response = self.client.open(path, method=method,
            base_url=href(self.component), **kwargs)
        return self.response

    def login(self, credentials):
        return

    def logout(self):
        return


def setup_folders():
    tmpdir = tempfile.gettempdir()
    instance_folder = os.path.join(tmpdir, 'inyoka_test')
    if not path.exists(instance_folder):
        os.mkdir(instance_folder)
        trans = config.edit()
        trans['media_root'] = os.path.join(instance_folder, 'media')
        trans.commit()
        config.touch()
        os.mkdir(config['media_root'])

    return instance_folder


#XXX: yet unused
def _initialize_database(uri):
    from sqlalchemy import create_engine
    from migrate.versioning import api
    from migrate.versioning.repository import Repository
    from migrate.versioning.exceptions import DatabaseAlreadyControlledError, \
                                              DatabaseNotControlledError

    repository = Repository('inyoka/migrations')

    try:
        schema = api.ControlledSchema(db.engine, repository)
    except DatabaseNotControlledError:
        pass

    try:
        schema = api.ControlledSchema.create(db.engine, repository, None)
    except DatabaseAlreadyControlledError:
        pass

    api.upgrade(db.engine, repository, None)


def run_suite(tests_path=None, clean_db=False, base=None):
    if tests_path is None:
        raise RuntimeError('You must specify a path for the unittests')
    # setup our folder structure
    instance_dir = setup_folders()

    # initialize the database
    #XXX: _initialize_database(config['database_url'])

    # setup the test context
    _res = path.join(tests_path, 'res')
    if not path.exists(_res):
        os.mkdir(_res)
    context.res_dir = _res
    context.setup_instance(instance_dir)

    import nose.plugins.builtin
    plugins = [x() for x in nose.plugins.builtin.plugins]
    try:
        nose.main(plugins=plugins)
    finally:
        # cleanup the test context
        context.teardown_instance()
        shutil.rmtree(instance_dir)

        # optionally delete our test database
        if clean_db and db.engine.url.drivername == 'sqlite':
            try:
                database = db.engine.url.database
                if path.isabs(db.engine.url.database):
                    os.remove(database)
                else:
                    os.remove(path.join(tests_path, path.pardir, database))
            except (OSError, AttributeError):
                # fail silently
                pass