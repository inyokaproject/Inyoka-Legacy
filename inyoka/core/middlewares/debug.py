# -*- coding: utf-8 -*-
"""
    inyoka.core.middlewares.debug
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2010 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
import re
from uuid import uuid4
from StringIO import StringIO
from inyoka.core.middlewares import IMiddleware
from inyoka.utils.debug import inject_query_info
from inyoka.utils.logger import logger

re_htmlmime = re.compile(r'^text/x?html')


class DebugMiddleware(IMiddleware):

    def __init__(self, ctx):
        IMiddleware.__init__(self, ctx)
        self.enabled = ctx.cfg['debug']

    def process_response(self, request, response):
        if self.enabled and response.status == '200 OK' \
            and re_htmlmime.match(response.content_type):
            inject_query_info(request, response)
        return response


class TwillRecordMiddleware(IMiddleware):

    def __init__(self, ctx):
        IMiddleware.__init__(self, ctx)
        self.enabled = ctx.cfg['middleware.enable_twill']
        if self.enabled:
            self._id = unicode(uuid4().get_hex())
            self._filename = 'regressions/inyoka_%s_regressiontest' % self._id
            self._generate_unittest_function()

    @property
    def _out(self):
        if self.enabled:
            return open(self._filename, 'a')
        return StringIO()

    def _generate_unittest_function(self):
        _buffer = []
        _buffer.append(u'def test_use_case_%s():' % self._id)
        _buffer.append(u'    from inyoka.core.test import twill as tw')
        _buffer.append(u'')
        _buffer.append(u'    # autogenerated twill commands:\n')
        self._out.write(u'\n'.join(_buffer))
        self._out.flush()

    def process_response(self, request, response):
        if not self.enabled:
            return response

        filter_ctypes = ('image', 'css', 'javascript')
        filter_url = ('.jpg', '.png', '.gif', '.css', '.js')

        ctype = response.headers.get('content-type', '')
        url = request.current_url
        if ([t for t in filter_ctypes if t in ctype] or
            [u for u in filter_url if url.endswith(u)]):
            logger.debug("twill will not log request – %s, %s" % (ctype, url))
            return response

        logger.debug("twill log request %s" % url)

        _buffer = []

        # create twill script line
        if request.method.lower() == 'get':
            _buffer.append(u'    # check that we can access %s properly'
                             % request.current_url)
            _buffer.append(u'    tw.c.go("%s")' % request.current_url)
            _buffer.append(u'    tw.c.code(200)')
            _buffer.append(u'    tw.c.url("%s")' % request.current_url)
        elif request.method.lower() == 'post':
            counter = 1
            #TODO: try to check something here!
            _buffer.append(u'    # replay form submit')
            _buffer.append(u'    tw.c.formclear(%i)' % counter)
            fvl = u'    tw.c.formvalue("%s", "' % unicode(counter)
            for key, value in request.form.iteritems():
                _buffer.append(fvl + key + u'", """' + value + u'""")')
            _buffer.append(u'    tw.c.submit()')

        self._out.write(u'\n'.join(_buffer))
        self._out.write(u'\n')
        self._out.flush()
        self._out.close()

        return response
