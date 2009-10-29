# -*- coding: utf-8 -*-
"""
    inyoka.application
    ~~~~~~~~~~~~~~~~~~

    The main WSGI application.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from werkzeug import ClosingIterator, redirect
from werkzeug.routing import Map
from sqlalchemy.exc import SQLAlchemyError

from inyoka import setup_components
from inyoka.core.api import db. config, logger, IController, Request, \
    Response
from inyoka.core.context import local, local_manager
from inyoka.core.http import DirectResponse
from inyoka.core.exceptions import HTTPException
from inyoka.core.middlewares import IMiddleware
from inyoka.core.routing import DateConverter


class InyokaApplication(object):
    """The WSGI application that binds everything."""

    def __init__(self):
        #TODO: this should go into some kind of setup process
        if not config.exists:
            # write the inyoka.ini file
            trans = config.edit()
            trans.commit(force=True)
            config.touch()

        #TODO: utilize that!
        setup_components([
            'inyoka.testing.controllers.*',
            'inyoka.core.routing.*',
            'inyoka.core.auth.*',
            'inyoka.portal.controllers.*',
            'inyoka.news.controllers.*',
            'inyoka.forum.controllers.*',
            'inyoka.paste.controllers.*',
            'inyoka.core.middlewares.services.*',
            'inyoka.core.middlewares.static.*',
        ])

        url_map = IController.get_urlmap() + IMiddleware.get_urlmap()
        self.url_map = Map(url_map,
            converters={
                'date': DateConverter,
        })
        self.url_adapter = self.url_map.bind(config['base_domain_name'])
        self.bind()

    def dispatch(self, environ, start_response):
        """The overall dispatch process.
        This binds the current request to the thread locals,
        binds the current application instance too and dispatches
        to a proper view.
        """
        # Create a new request object, register it with the application
        # and all the other stuff on the current thread but initialize
        # it afterwards.  We do this so that the request object can query
        # the database in the initialization method.
        request = object.__new__(Request)
        local.request = request
        self.bind()
        request.__init__(environ, self)

        response = None

        # wrap the real dispatching in a try/except so that we can
        # intercept exceptions that happen in the application.
        # TODO: implement real exception handling and logging
        try:
            urls = self.url_map.bind_to_environ(
                request.environ, server_name=config['base_domain_name'])

            for middleware in IMiddleware.iter_middlewares():
                if middleware.is_low_level:
                    response = middleware.process_request(environ, start_response)
                else:
                    response = middleware.process_request(request)

            if response is None:
                # dispatch the request if not already done by some middleware
                self.url_adapter = urls

                try:
                    rule, args = urls.match(request.path, return_rule=True)
                    response = IController.get_view(rule.endpoint)(request, **args)
                except HTTPException, e:
                    response = e.get_response(request)
                except SQLAlchemyError, e:
                    db.session.rollback()
                    logger.error(e)

            # let middlewares process the response
            for middleware in reversed(IMiddleware.iter_middlewares()):
                response = middleware.process_response(request, response)

            # force the response type to be a werkzeug response
            response = Response.force_type(response, environ)

        except DirectResponse, exc:
            # a response type that works around the call with
            # (environ, start_response).  Use it with care and only
            # if there's no other way!
            # Some usage example is a middleware that needs to respond
            # directly to the client and needs to be sure that no other
            # middlewares can modify the response object what, generally
            # all middlewares can do in the common request-pipeline
            return exc.response
        except ValueError:
            # url_adapter.bind_to_environ do raise this if we are not on the
            # proper base domain, so redirect
            response = redirect('http://%s/' % config['base_domain_name'])
        except:
            #TODO: proper exception handling!
            raise

        request.session.save_cookie(response)

        return response(environ, start_response)

    def bind(self):
        """Bind the application to a thread local"""
        local.application = self

    def __call__(self, environ, start_response):
        """Make the application object a WSGI application."""
        return ClosingIterator(self.dispatch(environ, start_response),
                               [local_manager.cleanup, db.session.close])


application = InyokaApplication()
