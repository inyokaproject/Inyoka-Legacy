# -*- coding: utf-8 -*-
"""
    inyoka.forum.forms
    ~~~~~~~~~~~~~~~~~~

    Formulars for the forum system.

    :copyright: 2010 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from inyoka.core.api import _, db, forms
from inyoka.i18n import _
from inyoka.forum.models import Forum, Tag


class AskQuestionForm(forms.Form):

    title = forms.TextField(_(u'Title'), max_length=160, required=True)
    text = forms.TextField(_(u'Text'), widget=forms.widgets.Textarea,
        required=True)
    tags = forms.Autocomplete(forms.ModelField(Tag, 'name'),
                              label=_(u'Tags'), sep=',', min_size=1)


class AnswerQuestionForm(forms.Form):

    text = forms.TextField(_(u'Text'), widget=forms.widgets.Textarea,
        required=True)


class EditForumForm(forms.Form):

    name = forms.TextField(_(u'Name'), max_length=160, required=True)
    slug = forms.TextField(_(u'Slug'), max_length=160, required=True)
    parent = forms.ModelField(Forum, 'id', _(u'Parent'),
                                widget=forms.widgets.SelectBox)
    description = forms.TextField(_(u'Description'), widget=forms.widgets.Textarea,
            required=True)
    tags = forms.Autocomplete(forms.ModelField(Tag, 'name'), label=_(u'Tags'), sep=',', min_size=1)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        # setup the possible choices for the parent forum
        self.parent.choices = ['']
        self.parent.choices.extend([(f.id, f.name) for f in Forum.query.all()])
