#-*- coding: utf-8 -*-
"""
    inyoka.paste.models
    ~~~~~~~~~~~~~~~~~~~

    Models for the paste app.

    :copyright: 2009 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from operator import attrgetter
from sqlalchemy.orm import synonym
from inyoka.core.api import db, href
from inyoka.core.models import User
from inyoka.utils.highlight import highlight_code


class Entry(db.Model):
    __tablename__ = 'paste_entry'

    id = db.Column(db.Integer, primary_key=True)
    _code = db.Column('code', db.Text, nullable=False)
    title =  db.Column(db.String(50), nullable=True)
    rendered_code = db.Column(db.Text, nullable=False)
    _language = db.Column('language', db.String(30))
    author_id = db.Column(db.ForeignKey('core_user.id'), nullable=False)
    pub_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    author = db.relation(User)


    def __init__(self, code, author, language=None, title=None):
        self.author = author
        self.title = title
        # set language before code to avoid rendering twice
        self.language = language
        self.code = code

    def get_absolute_url(self, action='view', external=False):
        return href({
            'view': 'paste/view_paste',
            'raw': 'paste/raw_paste',
            }[action], id=self.id)

    def _rerender(self):
        """
        Re-render the entry's code and save it in rendered_code.

        This method normally does not have to be called manually, changing
        code or language does this automatically.
        """
        if self._code is not None:
            self.rendered_code = highlight_code(self._code, self._language)

    def _set_code(self, code):
        changed = code != self._code
        self._code = code
        if changed:
            self._rerender()
    code = synonym('_code', descriptor=property(attrgetter('_code'), _set_code))

    def _set_language(self, language):
        changed = language != self._language
        self._language = language
        if changed:
            self._rerender()
    language = synonym('_language', descriptor=property(
        attrgetter('_language'), fset=_set_language))


    @property
    def display_title(self):
        if self.title:
            return self.title
        return '#%d' % self.id
