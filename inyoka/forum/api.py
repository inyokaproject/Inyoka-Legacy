# -*- coding: utf-8 -*-
"""
    inyoka.forum.api
    ~~~~~~~~~~~~~~~~

    API description for the forum application.

    :copyright: 2010 by the Inyoka Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""
from inyoka.core.api import IResourceManager
from inyoka.forum.models import Forum, Vote, Entry, Question, Answer, \
    question_tag, forum_tag
from inyoka.forum.search import QuestionSearchProvider, AnswerSearchProvider


class ForumResourceManager(IResourceManager):
    models = [Forum, Vote, question_tag, forum_tag,
              Entry, Question, Answer]
    search_providers = [QuestionSearchProvider(), AnswerSearchProvider()]
