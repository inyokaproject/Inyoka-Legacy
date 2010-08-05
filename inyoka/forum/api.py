# -*- coding: utf-8 -*-
"""
    inyoka.forum.api
    ~~~~~~~~~~~~~~~~

    API description for the forum application.

    :copyright: 2010 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from inyoka.core.api import IResource
from inyoka.forum.admin import ForumAdminProvider
from inyoka.forum.controllers import ForumController
from inyoka.forum.models import QuestionsContentProvider, Forum, Vote, Entry, \
    Question, Answer, question_tag, forum_tag


class ForumResoruce(IResource):
    models = [Forum, Vote, question_tag, forum_tag,
              Entry, Question, Answer]
