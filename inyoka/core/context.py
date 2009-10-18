# -*- coding: utf-8 -*-
"""
    inyoka.core.context
    ~~~~~~~~~~~~~~~~~~~

    Thread Locals

    Use these thread locals with caution and only where
    you don't have access to the current request/application
    object at all.  If there are easy ways of *not* using
    thread locals, you should not use them.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

from werkzeug import Local, LocalManager, LocalProxy

# NOTE: Never ever store custom values on `_local`!
#       Use some middleware that is able to store them
#       on a per-request and thread-safe way so that
#       you are able to clean them up.
_local = Local()
_local_manager = LocalManager(_local)

# the current request object.  This object is managed
# by _local_manager and cleaned up by the current :cls:`InyokaApplication`
# instance.
_current_request = LocalProxy(_local, 'request')
_current_application = LocalProxy(_local, 'application')


# some special api defintions

def get_application():
    return getattr(_local, 'application', None)

def get_request():
    return getattr(_local, 'request', None)
