# Bib2Bootstrap

A quick tool generate an HTML bibliography with bootstrap styling. 
[bib2html](https://sourceforge.net/projects/bib2html/) is
great, but I wanted the ability to produce a bit more modern-looking result for
my website and have a little more control over parsing of the bib file and
bibtex-to-html mapping.

### Requirements

[bibtexparser](https://pypi.python.org/pypi/bibtexparser) and 
[jinja2](https://pypi.python.org/pypi/Jinja2)

### Usage

``python bib2bootstrap.py -f BIBTEX_FILE [-o OUTPUT_FILE]``

Additional options include:

``[-s {year,author}]`` sort by year or author

``[-r]`` Reverse the sorting order

``[--skip SKIP [SKIP ...]]`` Skip entries of particular type (e.g., techreport)

By default only the ``<ul></ul>`` list, containing the bibliography, is
produced. You can copy it, or load dynamically into your webpage. For a
full standalone page, use

``--template=fulltemplate.html``

# Disclaimer:
This is a quick and dirty implementation, use at your own risk.