from datetime import timedelta

import bleach
from markdown import Markdown
from unidecode import unidecode
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify as django_slugify
from django.utils.translation import ugettext_lazy as _, ungettext_lazy


def slugify(string):
    string = unicode(string)
    string = unidecode(string)
    return django_slugify(string.replace('_', ' '))


"""
Utils for resolving requests destination
"""
def _is_request_path_under_misago(request):
    # We are assuming that forum_index link is root of all Misago links
    forum_index = reverse('misago:index')
    path_info = request.path_info

    if len(forum_index) > len(path_info):
        return False
    return path_info[:len(forum_index)] == forum_index


def is_request_to_misago(request):
    try:
        return request._request_to_misago
    except AttributeError:
        request._request_to_misago = _is_request_path_under_misago(request)
        return request._request_to_misago


"""
Utility that humanizes time amount.

Expects number of seconds as first argument
"""
def time_amount(value):
    delta = timedelta(seconds=value)

    units_dict = {
        'd': delta.days,
        'h': 0,
        'm': 0,
        's': delta.seconds,
    }

    if units_dict['s'] >= 3600:
        units_dict['h'] = units_dict['s'] / 3600
        units_dict['s'] -= units_dict['h'] * 3600

    if units_dict['s'] >= 60:
        units_dict['m'] = units_dict['s'] / 60
        units_dict['s'] -= units_dict['m'] * 60

    precisions = []

    if units_dict['d']:
        string = ungettext_lazy(
            '%(days)s day', '%(days)s days', units_dict['d'])
        precisions.append(string % {'days': units_dict['d']})

    if units_dict['h']:
        string = ungettext_lazy(
            '%(hours)s hour', '%(hours)s hours', units_dict['h'])
        precisions.append(string % {'hours': units_dict['h']})

    if units_dict['m']:
        string = ungettext_lazy(
            '%(minutes)s minute', '%(minutes)s minutes', units_dict['m'])
        precisions.append(string % {'minutes': units_dict['m']})

    if units_dict['s']:
        string = ungettext_lazy(
            '%(seconds)s second', '%(seconds)s seconds', units_dict['s'])
        precisions.append(string % {'seconds': units_dict['s']})

    if not precisions:
        precisions.append(_("0 seconds"))

    if len(precisions) == 1:
        return precisions[0]
    else:
        formats = {
            'first_part': ', '.join(precisions[:-1]),
            'and_part': precisions[-1],
        }

        return _("%(first_part)s and %(and_part)s") % formats


"""
MD subset for use for enchancing items descriptions
"""
MD_SUBSET_FORBID_SYNTAX = (
    # References are evil
    'reference', 'reference', 'image_reference', 'short_reference',

    # Blocks are evil too
    'hashheader', 'setextheader', 'code', 'quote', 'hr', 'olist', 'ulist',
)


def subset_markdown(text):
    if not text:
        return ''

    md = Markdown(safe_mode='escape', extensions=['nl2br'])

    for key in md.preprocessors.keys():
        if key in MD_SUBSET_FORBID_SYNTAX:
            del md.preprocessors[key]

    for key in md.inlinePatterns.keys():
        if key in MD_SUBSET_FORBID_SYNTAX:
            del md.inlinePatterns[key]

    for key in md.parser.blockprocessors.keys():
        if key in MD_SUBSET_FORBID_SYNTAX:
            del md.parser.blockprocessors[key]

    for key in md.treeprocessors.keys():
        if key in MD_SUBSET_FORBID_SYNTAX:
            del md.treeprocessors[key]

    for key in md.postprocessors.keys():
        if key in MD_SUBSET_FORBID_SYNTAX:
            del md.postprocessors[key]

    return bleach.linkify(md.convert(text))
