from __future__ import unicode_literals
# -*- coding: utf-8 -*-
import random
import json
import math
import re
import unicodedata
from decimal import Decimal
from dateutil import parser
from money import Money

from bentodev.utils.image_utils import generate_resize_url, get_raw_image_url
from bentodev.utils.text import Truncator
from bentodev.utils.safestring import mark_safe


def linebreaksbr(value):
    """
    Convert all newlines in a piece of plain text to HTML line breaks
    (``<br />``).
    """
    return value.replace('\n', '<br />')


def datetime(value, format='%d-%m-%Y %H:%M'):
    if not value:
        return value

    if type(value) is str or type(value) is unicode:
        value = parser.parse(value)

    return value.strftime(format)


def date(value, format='%d-%m-%Y'):
    if not value:
        return value

    if type(value) is str or type(value) is unicode:
        value = parser.parse(value)

    return value.strftime(format)


def time(value, format='%H:%M'):
    if not value:
        return value

    if type(value) is str or type(value) is unicode:
        value = parser.parse(value)

    return value.strftime(format)


def image_url(source):
    if not source:
        return ''

    try:
        return source['image_path']
    except (TypeError, KeyError):
        pass

    try:
        return source['url']
    except (TypeError, KeyError):
        pass

    return source


def image_alt(source):
    if not source:
        return ''
    try:
        return source['alt_text']
    except (TypeError, KeyError):
        return ''


def raw_image(source):
    return get_raw_image_url(source)


def thumbnail(source):
    return generate_resize_url(source, width=100)


def small(source):
    return generate_resize_url(source, width=300)


def medium(source):
    return generate_resize_url(source, width=600)


def large(source):
    return generate_resize_url(source, width=1000)


def xlarge(source):
    return generate_resize_url(source, width=1800)


def resize(source, width=1200, height=None, fit='max'):
    return generate_resize_url(source, width, height, fit)


def money(amount, locale='en_US', format=u'¤#,##0.00', currency_digits=False):
    try:
        amount = Decimal(amount)
    except (ValueError, TypeError):
        return amount

    m = Money(amount, 'USD')

    formatted = m.format(locale, format, currency_digits)

    return formatted


def round_money(amount):
    if not amount:
        return amount

    # take the amount and convert it to a float, then
    amount_as_float = float(amount)

    # round it UP to the nearest non-decimal value (1.23 -> 2.00)
    rounded_float_amount = math.ceil(amount_as_float)

    # checks if rounded number is bigger then stores that as a new variable
    has_decimal = rounded_float_amount > amount_as_float

    # format money for if price is int
    money_format = u'#,##0'

    # format money for if price is float
    if has_decimal:
        money_format = u'#,##0.00'

    # return price in correct format
    return money(amount, format=money_format)


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str`` by using the application's
    configured encoder (:attr:`~flask.Flask.json_encoder`) if there is an
    application on the stack.
    This function can return ``unicode`` strings or ascii-only bytestrings by
    default which coerce into unicode strings automatically.  That behavior by
    default is controlled by the ``JSON_AS_ASCII`` configuration variable
    and can be overridden by the simplejson ``ensure_ascii`` parameter.
    """
    encoding = kwargs.pop('encoding', None)
    try:
        rv = json.dumps(obj, **kwargs)
    except TypeError:
        rv = u'{}'
    if encoding is not None and isinstance(rv, str):
        rv = rv.encode(encoding)
    return rv


def htmlsafe_dumps(obj, **kwargs):
    _slash_escape = '\\/' not in json.dumps('/')

    rv = dumps(obj, **kwargs) \
        .replace(u'<', u'\\u003c') \
        .replace(u'>', u'\\u003e') \
        .replace(u'&', u'\\u0026') \
        .replace(u"'", u'\\u0027')
    if not _slash_escape:
        rv = rv.replace('\\/', '/')
    return rv


def tojson(obj, **kwargs):
    return htmlsafe_dumps(obj, **kwargs)


def shuffle(obj):
    result = list(obj)
    random.shuffle(result)

    return result


def obfuscate_string(value):
    return ''.join(['&#{0:s};'.format(str(ord(char))) for char in value])


def normalize_internal_url(url):
    # Only act if a value was passed
    if not url:
        return ''

    # Get rid of any trailing or leading spaces
    url = url.strip()

    # Strip any combination of trailing slashes and spaces
    url = re.sub(r'[\/|\s]+$', '', url)

    # Strip any combination of leading slashes and spaces
    url = re.sub(r'^[\/|\s]+', '', url)

    # If value is a root-relative hompage link, or it is a hash
    # value - just return it as-is
    if url == '/' or url.startswith('#'):
        return url

    # Define all of the protcol that we want to allow, followed
    # by a colon
    protocol_whitelist_pattern = r'^(tel|ftp|sms|mailto):'

    # If a whitelisted protocol exists, return the url as-is
    match = re.match(protocol_whitelist_pattern, url)

    if match:
        group = match.groups()[0]

        # If the protocol is mailto - we obfuscate the url
        if group == 'mailto':
            url = obfuscate_string(url)

        return url

    # if no protocol exists or it's not whitelisted,
    # force the url to be url root-relative
    # i.e. you don't ever want a url like "href="about"
    # because that will go to different places depending on which
    # pages you're on

    return '/%s/' % url


def truncatechars_html(value, arg):
    """
    Truncate HTML after `arg` number of chars.
    Preserve newlines in the HTML.
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.
    return Truncator(value).chars(length, html=True)


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return mark_safe(re.sub(r'[-\s]+', '-', value))
