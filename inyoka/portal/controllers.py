#-*- coding: utf-8 -*-
"""
    inyoka.portal.controllers
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Controllers for the portal app.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from inyoka.core.api import IController, Rule, register, register_service, \
    href, Response, templated, href, redirect
from inyoka.core.auth import get_auth_system

class PortalController(IController):
    name = 'portal'

    url_rules = [
        Rule('/', endpoint='index'),
        Rule('/login', endpoint='login'),
        Rule('/logout', endpoint='logout'),
    ]

    @register('index')
    @templated('portal/index.html')
    def index(self, request):
        return { 'called_url': request.build_absolute_url(),
                 'link': href('portal/index') }

    @register('login')
    @templated('portal/login.html')
    def login(self, request):
        #form = get_auth_system().get_login_form()
        #if request.method == 'POST' and form.validate(request.form):
        #    get_auth_system().login(request, form.data['username'],
        #                            form['password'])
        #    return redirect(href('portal/index'))
        #return { 'login_form': form.as_widget() }
        return get_auth_system().login(request)

    @register('logout')
    def logout(self, request):
        get_auth_system().logout(request)
        return redirect(href('portal/index'))


class CalendarController(IController):
    name = 'calendar'

    url_rules = [
        Rule('/', endpoint='index'),
        Rule('/<date:date>/<slug>/', endpoint='entry'),
    ]

    @register('index')
    def index(self, request):
        return Response('this is calendar index page')

    @register('entry')
    def entry(self, request, date, slug):
        return Response('this is calendar entry %r from %r' % (slug, date))
