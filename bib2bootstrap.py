#!/usr/bin/env python

import argparse
import operator
import re
import sys
from collections import defaultdict

import bibtexparser
import jinja2

TEMPLATE_FOLDER = './templates/'
labelColor = defaultdict(lambda: 'label-default',
                         {
                             'inproceedings': 'label-success',
                             'article': 'label-primary',
                             'techreport': 'label-default'
                         })


def clean_brackets(s):
    """
    Gets rid of the extra brackets in the bibtex entry
    :param s:
    :return:
    """
    return s.replace('{', '').replace('}', '')


def format_authors(author_string):
    """
    Format the authors.
    :param author_string: Author string as it appears in bibtex file
    :return: A more human readable string.
    """
    authors = re.split(r'\s+and\s+', author_string)
    formatted_authors = []
    for a in authors:
        a = a.strip()
        # print (a)
        if ',' in a:
            a = ' '.join(reversed(a.split(','))).strip()
        formatted_authors.append(a)
    return ', '.join(formatted_authors)


def get_venue(d):
    """
    Prettify the name of the venue that the papaer appeared in.
    :param d:
    :return:
    """
    et = d['ENTRYTYPE'].lower()
    if et == 'inproceedings':
        return 'In ' + d['booktitle']
    elif et == 'article':
        return d['journal']
    elif et == 'misc':
        return d['howpublished']
    elif et == 'techreport':
        return 'Technical Report. ' + d['institution']
    else:
        raise Exception("Do not know how to parse entry type {}".format(et))


def get_badge(d):
    """
    Get the name of badge to be used in the list. Only 3 types supported so far: conference, journal, techreport.
    :param d:
    :return:
    """
    et = d['ENTRYTYPE'].lower()
    if et == 'inproceedings':
        return 'Conference paper'
    elif et == 'article':
        return 'Journal paper'
    elif et == 'techreport':
        return 'Technical Report'
    else:
        return ''


def process_entry(d):
    """
    Process a single bibtex entry. Return our own custom item
    :param d: dictionary as given by bibtexparser
    :return:
    """
    return {'title': clean_brackets(d['title']),
            'author': format_authors(d['author']),
            'venue': get_venue(d), 'year': int(d['year']),
            'note': d['annote'] if 'annote' in d else '',
            'url': d['link'] if 'link' in d else '',
            'venueseries': d['series'] if 'series' in d else '',
            'type': d['ENTRYTYPE'],
            'badge': get_badge(d)
            }


def process_file(fname, skip):
    """
    Process the bibtex file and return a dictionary of items for rendering
    :param fname: filename of the bibtex file (as string)
    :param skip: a particular types of bibtex entries we don't want to show (as list of strings)
    :return:
    """
    with open(fname) as bib:
        db = bibtexparser.load(bib)
        results = []
        for key, d in db.entries_dict.items():
            e = process_entry(d)
            if skip is None or e['type'] not in skip:
                results.append(e)
        return results


def render(items, fd, template_name='listtemplate.html',
           template_folder=TEMPLATE_FOLDER):
    """
    Render the HTML with Jinja's help
    :param items: items of the bibliography list
    :param fd: file descriptor to render to (either file of stdout)
    :param template_name: Name of jinja template.
    :param template_folder: Folder that stores the Jinja templates (as string)
    :return:
    """
    loader = jinja2.FileSystemLoader(template_folder)
    template = loader.load(jinja2.Environment(), template_name)
    print(template.render(items=items, labelColor=labelColor), file=fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', required=True, help='Bibtex file to parse.')
    parser.add_argument(
        '-o', '--output', help='Output file. Otherwise written to stdout.')
    parser.add_argument(
        '-s', '--sort', choices=['year', 'author'], default='year',
        help='Sort by this field.')
    parser.add_argument('--template', help='Name of the template',
        default='listtemplate.html')
    parser.add_argument('-r', '--reverse',
                        action='store_true',
                        help='Reverse sorting direction.')
    parser.add_argument('--skip', nargs='+',
                        help='Skip entries of given types')
    options = parser.parse_args()

    # Parse our file
    res = process_file(options.file, options.skip)
    # See if we need to sort or not
    if options.sort is not None:
        res.sort(key=lambda x: operator.getitem(x, options.sort),
                 reverse=options.reverse)
    if options.output:
        # If we have a file name, dump ot file
        with open(options.output, 'w') as f:
            render(res, f, template_name=options.template)
    else:
        # Otherwise write to stdout
        render(res, sys.stdout, template_name=options.template)
