"""Utility functions
Quite a lot of the functions are meant for jinja
Some are used as jinja filters and some are global functions
"""
import os
import random
import string
import re
from datetime import datetime

from slugify import slugify
from flask import request


def abs_path(path, relative_to=None):
    """Generate absolute path relative to the `relative_to` path.
    There are two use cases, one is get the absolute path relative to the
    current python file, `__file__` is used for `relative_to`
    The other one use case is to get the absolute path relative to the
    Flask app file, `os.getcwd()` is used for `relative_to`, which is the default value
    :param relative_to: either use __file__, or os.getcwd(),
    :param path: the relative path to the file/folder
    :return: absolute path to `path`
    """

    #: Already is a absolute path
    #: TODO: find a way to handle Windows system (or maybe just forget it)
    if path[0] == os.path.sep:
        return path

    if relative_to is None:
        relative_to = os.getcwd()
    elif os.path.isfile(relative_to):
        relative_to = os.path.dirname(relative_to)
    # Windows and Linux/Mac has different path separators \ & /
    # Clean up the input path and let python join them back with the correct separator
    return os.path.join(relative_to, *re.split(r'\\|/', path))


def clean_filename(filename, dirname=None):
    base, extension = os.path.splitext(filename.lower())
    cleaned = gen_slug(base) + extension

    if dirname and filename != cleaned:
        os.rename(os.path.join(dirname, filename),
                  os.paht.join(dirname, cleaned))
    return cleaned


def random_string(l=16):
    """Generate a random string of length l
    Code copied from StackOverflow, looks a bit confusing but works well
    """
    return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(l))


def gen_slug(input_string, existing_slugs=[], delimiter='-'):
    """Generate a slug for given title
    If the title conflicts with existing another page title
    add -1, -2 etc to differentiate it
    :param input_string:        Input string
    :param existing_slugs:      Exiting slugs
    :return:
    """
    base = slugify(input_string, ok=delimiter, only_ascii=True)
    # Some problem with the library, cannot handle japanese characters well
    # End up having uppercase letters and spaces
    if base.find(' ') > -1:
        base = slugify(base, ok=delimiter)
    slug = base
    counter = 1
    while slug in existing_slugs:
        slug = '%s%s%i' % (base, delimiter, counter)
        counter += 1
    return slug


def add_http(url, prefix='http://'):
    """Add http:// or https:// for url.
    This is to avoid user input URL without any http://
    and the browser cannot open the link properly
    :param url: url input by the user
    :param prefix: 'http://' or 'https://' to be added, can be 'ws://' in theory, but it's unlikely we need the user to input an unusual URI
    :return: url ensured to have http:// or https:// in front
    """
    if not re.match('^http(s?)://', url):
        return prefix + url
    else:
        return url


def add_https(url):
    return add_http(url, 'https://')


def leading_zero(n, min_len=2):
    """Add leading zeroes for a number.
    Most commonly used for day or month numbers
    :param n: input number, e.g. 1,2
    :param min_len: length required for the number to match, e.g. 01, 02
    :return: number padded with zeroes
    """
    s = str(n)
    while len(s) < min_len:
        s = "0" + s
    return s


def format_currency(value):
    """
    Format input value into currency format, e.g. 1000 -> $1,000.0
    :param value:   input value, supposed to be number only, but sometimes can be string,
                    or something can't be converted into a number
    :return:        number in currency format,
                    or the same as input value if the input is not a number
    """
    try:
        value = float(value)
        return "${:,.2f}".format(value)
    except (ValueError, TypeError):
        return value


def format_date(d, format='%d/%m/%Y'):
    """Format date into string with desired format.
    Meant to be used in template files to avoid calling strftime function to an empty string
    Default format is DD/MM/YYYY
    :param d: date object to be formatted
    :param format: desired format
    :return:
    """
    if not d:
        return ''
    elif not type(d) == 'datetime':
        return d
    else:
        return d.strftime(format)


def format_datetime(d, format='%d/%m/%Y %H:%M'):
    """Format datetime into string with desired format
    Meant to be used in template files to avoid calling strftime function to an empty string
    Default format is DD/MM/YYYY HH:MM
    :param d: date object to be formatted
    :param format: desired format
    :return:
    """
    if not d:
        return ''
    elif not type(d) == 'datetime':
        return d
    else:
        return d.strftime(format)


def readable_number(num, single_thing='', plura_thing='',):
    """
    Convert numbers into human readable format e.g 1000000 to 1M
    :param num: the number
    :param single_thing: 1 apple
    :param plural_thing: 2 apples
    """
    if num is None:
        return ''

    # Add a space in front of the thing
    if single_thing:
        single_thing = ' '+single_thing
    if plura_thing:
        plura_thing = ' '+plura_thing

    # 0/1 thing
    if num <= 1:
        return '%i%s' % (num, single_thing)

    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    if magnitude == 0:
        return '%i%s' % (num, plura_thing)
    else:
        return '%.1f%s%s' % (num, ['', 'K', 'M', 'B'][magnitude], plura_thing)


def add_p(text):
    """Add <p> tags for text based on line breaks
    :param text: input text
    :return: html text with <p> tags surrounding each block
    """
    if not isinstance(text, basestring):
        return ''
    arr = re.split('\n+', text)
    return '\n'.join(['<p>' + line + '</p>' for line in arr if len(line) > 0])


def add_br(text):
    """Replace line breaks with <br/>
    :param text: input text
    :return: html text with <br/> as line breaks instead of \n
    """
    return re.sub('(\n+)|(\r+)/g', '<br/>', text)


def remove_linebreaks(text):
    """Remove line breaks, \n, \r but not <br/>
    Useful for compressing HTML
    :param text:    input text
    :return:        text without line breaks
    """
    return re.sub('(\n+)|(\r+)/g', '', text)


def highlight_link(pattern, css_class='active'):
    """Check if request url matches with the link
    :param pattern: patterns to match
    :param css_class: name of the css class for current link, default as 'active
    :return:        css_class if the link matches the url, '' if not
    """
    if re.search(pattern, request.path):
        return css_class
    else:
        return ''


def relative_years(start=-90, end=-12):
    """Generate a range of years for birthday
    :param min_age: Minimum age allowed to use the website, default value is 12, an arbitrary number
    :param max_age: Maximum age allowed to use the website, default value is 90, another arbitrary number
    :return: list of years of possible/allowed year of birth, most recent year to oldest year
    """
    d = datetime.now()
    return range(d.year + start, d.year + end)


def next_year(d=None):
    """Get the timestamp of next year of this time
    :return:
    """
    if not d:
        d = datetime.now()
    try:
        d = d.replace(year=d.year + 1)
    except ValueError:
        # Feb 29 problem
        d = d.replace(year=d.year + 1, month=3, day=1)
    return d


def copyright_year(since=None):
    """Added copyright symbol based on the current year
    :param since: starting of the business, can be empty
    :return: copyright year
    """
    text = datetime.strftime(datetime.now(), '%Y')
    if since:
        text = since + ' - ' + text
    return '&copy;' + text
