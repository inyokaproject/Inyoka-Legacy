# -*- coding: utf-8 -*-
"""
"""
import os
import pytz
from time import strptime
from datetime import datetime
from gettext import NullTranslations
from babel import Locale, dates, UnknownLocaleError
from babel.support import Translations


from babel.support import Translations, LazyProxy
from babel.dates import format_date as babel_format_date, \
    format_datetime as babel_format_datetime, format_time as babel_format_time

from inyoka.core.context import local


__all__ = ['_', 'gettext', 'ngettext', 'lazy_gettext', 'lazy_ngettext']


UTC = pytz.timezone('UTC')

local.translations = local.locale = None
_translations = local('translations')
_current_locale = local('locale')

_translations = {
    None: NullTranslations()
}


def get_translations(locale):
    """Get the translation for a locale.  This sets up the i18n process."""
    locale = Locale.parse(locale)
    translations = _translations.get(str(locale))
    if translations is not None:
        return translations
    rv = Translations.load(os.path.dirname(__file__), [locale])
    _translations[str(locale)] = rv
    _current_locale = locale
    return rv


def get_timezone(name=None):
    """Return the timezone for the given identifier or the timezone
    of the application based on the configuration.
    """
    if name is None:
        return UTC
    return timezone(name)


def get_locale():
    """Return the current locale."""
    return _current_locale or None


def lazy_gettext(string):
    """A lazy version of `gettext`."""
    return LazyProxy(gettext, string)


def lazy_ngettext(singular, plural, n):
    """A lazy version of `ngettext`."""
    return LazyProxy(ngettext, singular, plural, n)


def gettext(string):
    """Translate the given string to the language of the application."""
    return unicode(_translations[get_locale()].ugettext(string))


def ngettext(singular, plural, n):
    """Translate the possible pluralized string to the language of the
    application.
    """
    if get_locale() is None:
        if n == 1:
            return singular
        return plural
    return unicode(_translations[get_locale()].ungettext(singular, plural, n))


def _date_format(formatter, obj, format):
    return formatter(obj, format, locale=get_locale())


def format_datetime(datetime=None, format='medium'):
    """Return a date formatted according to the given pattern."""
    return _date_format(dates.format_datetime, datetime, format)


def list_languages():
    """Return a list of all languages."""
    languages = [('en', Locale('en').display_name)]
    folder = os.path.dirname(__file__)

    for filename in os.listdir(folder):
        if filename == 'en' or not \
           os.path.isdir(os.path.join(folder, filename)):
            continue
        try:
            l = Locale.parse(filename)
        except UnknownLocaleError:
            continue
        languages.append((str(l), l.display_name))

    languages.sort(key=lambda x: x[1].lower())
    return languages


def has_language(language):
    """Check if a language exists."""
    return language in dict(list_languages())


def rebase_to_timezone(datetime):
    """Convert a datetime object to the blog timezone."""
    if datetime.tzinfo is None:
        datetime = datetime.replace(tzinfo=UTC)
    tzinfo = get_timezone()
    return tzinfo.normalize(datetime.astimezone(tzinfo))


_ = gettext