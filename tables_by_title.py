import re
from pathlib import Path
from lxml import etree
import json
from slugify import slugify

TABLES_PATH = Path('./tables')
OUT_PATH = Path('./html')
STYLESHEET = "<link rel='stylesheet' href='https://cdn.jsdelivr.net/gh/kognise/water.css@1.2.1/dist/light.css' />"


def get_child_text(parent):
    text = "".join(parent.itertext())
    text = re.sub("\s+", " ", text).strip()
    return text

def get_labels(parent):
    labels = parent.xpath('//label')
    return [get_child_text(l) for l in labels if get_child_text(l)]

def get_titles(parent):
    titles = parent.xpath('//title')
    return [get_child_text(t) for t in titles if get_child_text(t)]

def get_article_num(path):
    match = re.match(r'elife-([0-9]+)-v([0-9]+)\.xml', path.parts[-2])
    num = match.group(1)
    # version = num.group(2)
    return num

def normalize_text(text):
    return text.lower().strip().rstrip('.')

def write_html_file(filename, content):
    filepath = OUT_PATH / filename
    with open(filepath, 'w') as f:
        f.write(content)

def get_tables_html(title, tables):
    html = f"""
        <html>
            <head>
                {STYLESHEET}
            </head>
            <body>
                <h1>{title} ({len(tables)})</h1>
    """

    for table in sorted(tables):
        paperxml = str(table.parts[-2])
        link = f"https://github.com/elifesciences/elife-article-xml/tree/master/articles/{paperxml}"
        html = html + f'<br><h2><a href="{link}">{paperxml}</a></h2>'
        html = html + table.read_text()

    html = html + """
            </body>
        </html>
    """

    return html

def get_index_html(duplicate_tables):
    html = f"""
        <html>
            <head>
                {STYLESHEET}
            </head>
            <body>
                <h1>Tables</h1>
                <ul>
    """

    for title, tables in duplicate_tables.items():
        html = html + f'<li><a href="{slugify(title)}.html">{title}</a> ({len(tables)} tables found)</li>'

    html = html + """
                </ul>
            </body>
        </html>
    """

    return html

def get_duplicate_tables(all_titles):
    duplicate_tables = {}
    for title, tables in all_titles.items():
        if len(tables) > 2:

            distinct_articles = set()
            for table in tables:
                distinct_articles.add(get_article_num(table))
            if len(distinct_articles) == 1:
                # if all the tables we've found are either from the exact
                # same article or different versions of the same article,
                # this probably isn't interesting
                continue

            duplicate_tables[title] = list(tables)

    return duplicate_tables


all_titles = {}

for table in list(TABLES_PATH.rglob('*.xml')):
    if table.is_dir():
        continue
    print(f'Parsing: {str(table)} ...')
    text = table.read_bytes()
    tree = etree.fromstring(text)
    titles = get_titles(tree)
    for title in titles:
        title = normalize_text(title)
        if title in all_titles:
            all_titles[title].add(table)
        else:
            all_titles[title] = {table}

duplicate_tables = get_duplicate_tables(all_titles)

for title, tables in duplicate_tables.items():
    write_html_file(slugify(title) + '.html', get_tables_html(title, tables))

write_html_file('index.html', get_index_html(duplicate_tables))
