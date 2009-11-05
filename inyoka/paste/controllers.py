#-*- coding: utf-8 -*-
"""
    inyoka.paste.controllers
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Controllers for the paste app.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from werkzeug.exceptions import NotFound
from inyoka.core.api import IController, Rule, register, register_service, \
    href, Response, templated, href, db, redirect
from inyoka.paste.forms import AddPasteForm
from inyoka.paste.models import Entry


class PasteController(IController):
    name = 'paste'

    url_rules = [
        Rule('/', endpoint='index'),
        Rule('/paste/<int:id>/', endpoint='view_paste'),
        Rule('/raw/<int:id>/', endpoint='raw_paste'),
    ]


    @register('index')
    @templated('paste/index.html')
    def index(self, request):
        form = AddPasteForm()
        if request.method == 'POST' and form.validate(request.form):
            e = Entry(code=form.data['code'],
                      language=form.data['language'],
                      author=1)
            db.session.add(e)
            db.session.commit()
            return redirect(href(e))

        recent_pastes = Entry.query.order_by(Entry.pub_date.desc())[:10]

        return {
            'recent_pastes': recent_pastes,
            'form': form.as_widget(),
        }

    @register('view_paste')
    @templated('paste/view.html')
    def view_paste(self, request, id):
        e = Entry.query.get(id)
        if e is None:
            raise NotFound
        return {
            'paste': e,
        }

    @register('raw_paste')
    def raw_paste(self, request, id):
        e = Entry.query.get(id)
        if e is None:
            raise NotFound
        return Response(e.code, mimetype='text/plain')

