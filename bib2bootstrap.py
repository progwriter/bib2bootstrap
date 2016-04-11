#!/usr/bin/env python

import bibtexparser
import argparse
import re
import operator
import jinja2
import sys
from collections import defaultdict


TEMPLATE_FOLDER = './templates/'
labelColor = defaultdict(
    lambda: 'label-default',
    {
    'inproceedings': 'label-success',
    'article': 'label-primary',
    'techreport': 'label-default'
    })

def cleanBrackets(s):
    return s.replace('{', '').replace('}', '')


def formatAuthors(authorString):
    authors = re.split(r'\s+and\s+', authorString)
    formattedAuthors = []
    for a in authors:
        a = a.strip()
        # print (a)
        if ',' in a:
            a = ' '.join(reversed(a.split(','))).strip()
        formattedAuthors.append(a)
    return ', '.join(formattedAuthors)


def getVenue(d):
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

def getBadge(d):
    et = d['ENTRYTYPE'].lower()
    if et == 'inproceedings':
        return 'Conference paper'
    elif et == 'article':
        return 'Journal paper'
    elif et == 'techreport':
        return 'Technical Report'
    else:
        return ''

def processEntry(d):
    return {'title': cleanBrackets(d['title']),
            'author': formatAuthors(d['author']),
            'venue': getVenue(d), 'year': int(d['year']),
            'note': d['annote'] if 'annote' in d else '',
            'url': d['link'] if 'link' in d else '',
            'venueseries': d['series'] if 'series' in d else '',
            'type': d['ENTRYTYPE'],
            'badge': getBadge(d)
            }


def processFile(fname, skip):
    with open(fname) as bib:
        db = bibtexparser.load(bib)
        results = []
        for key, d in db.entries_dict.items():
            e = processEntry(d)
            if skip is None or e['type'] not in skip:
                results.append(e)
        return results


def render(listofItems, fd, templateName='listtemplate.html',
           templateFolder=TEMPLATE_FOLDER):
    loader = jinja2.FileSystemLoader(templateFolder)
    template = loader.load(jinja2.Environment(), templateName)
    print(template.render(items=listofItems, labelColor=labelColor), file=fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', required=True, help='Bibtex file to parse.')
    parser.add_argument(
        '-o', '--output', help='Output file. Otherwise written to stdout.')
    parser.add_argument(
        '-s', '--sort', choices=['year', 'author'], default='year',
        help='Sort by this field.')
    parser.add_argument('-r', '--reverse',
                        action='store_true',
                        help='Reverse sorting direction.')
    parser.add_argument('--skip', nargs='+',
        help='Skip entries of given types')
    # TODO: add filtering by type
    # TODO: add ability to add header
    options = parser.parse_args()

    res = processFile(options.file, options.skip)
    if options.sort is not None:
        res.sort(key=lambda x: operator.getitem(x, options.sort),
                 reverse=options.reverse)
    if options.output:
        with open(options.output, 'w') as f:
            render(res, f)
    else:
        render(res, sys.stdout)
