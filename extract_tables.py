#!/usr/bin/python3

from pathlib import Path
from lxml import etree
from settings import IN_PATH, OUT_PATH

for article in list(IN_PATH.rglob('*.xml')):
    print(f'Parsing: {str(article)} ...')
    text = article.read_bytes()
    tree = etree.fromstring(text)
    tables = tree.xpath('//table-wrap')
    for i, table in enumerate(tables):
        subdir = OUT_PATH / Path(str(article.parts[-1]))
        subdir.mkdir(parents=True, exist_ok=True)
        outfile = subdir / Path(f'table-{str(i)}.xml')
        with open(outfile, "wb") as f:
            f.write(etree.tostring(table))
