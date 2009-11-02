# -*- coding: utf-8 -*-
"""
    inyoka.core.templating
    ~~~~~~~~~~~~~~~~~~~~~~

    Description goes here...

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
import os
import simplejson
from jinja2 import Environment, FileSystemLoader
from inyoka import INYOKA_REVISION
from inyoka.core.context import local, get_request
from inyoka.core.http import Response
from inyoka.core.config import config
from inyoka.utils.urls import url_encode, url_quote


def populate_context_defaults(context):
    """Fill in context defaults."""
    if get_request():
        context.update(
            CURRENT_URL=get_request().build_absolute_url(),
        )


def render_template(template_name, context):
    """Render a template.  You might want to set `req` to `None`."""
    tmpl = jinja_env.get_template(template_name)
    populate_context_defaults(context)
    return tmpl.render(context)


def urlencode_filter(value):
    """URL encode a string or dict."""
    if isinstance(value, dict):
        return url_encode(value)
    return url_quote(value)


class TemplateResponse(Response):
    """
    Special Response object for using templates.

    :param template_name: The name of the template file.
    :param context: The context for rendering the template.

    All other parameters (except `response` are the same as in the normal
    `Response`.
    """
    def __init__(self, template_name, context, **kwargs):
        if 'response' in kwargs:
            raise TypeError('TemplateResponse does not accept `response` '
                            'parameter')
        data = render_template(template_name, context)
        if config['debug']:
            self.template_context = context
        Response.__init__(self, data, **kwargs)


def templated(template_name):
    """
    Decorator for views. The decorated view must return a dictionary which is
    default_mimetype = 'text/html'
    then used as context for the given template. Returns a Response object.
    """
    def decorator(f):
        def proxy(*args, **kwargs):
            ret = f(*args, **kwargs)
            if ret is None:
                ret = {}
            if isinstance(ret, dict):
                return TemplateResponse(template_name, context=ret)
            return Response.force_type(ret)
        return proxy
    return decorator


class InyokaEnvironment(Environment):
    """
    Beefed up version of the jinja environment but without security features
    to improve the performance of the lookups.
    """

    def __init__(self):
        template_paths = [os.path.join(os.path.dirname(__file__), os.pardir,
                                       'templates')]
        if config['template_path']:
            template_paths.insert(0,  config['template_path'])

        loader = FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                               os.pardir, 'templates'))
        #TODO: link `auto_reload` to a config setting
        Environment.__init__(self, loader=loader,
                             extensions=['jinja2.ext.i18n', 'jinja2.ext.do'],
                             auto_reload=True,
                             cache_size=-1)
        self.globals.update(
            INYOKA_REVISION=INYOKA_REVISION,
            REQUEST=local('request'),
        )
        self.filters.update(
            jsonencode=simplejson.dumps
        )

        self.install_null_translations()

jinja_env = InyokaEnvironment()
