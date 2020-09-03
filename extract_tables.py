from pathlib import Path
from lxml import etree
from settings import IN_PATH, OUT_PATH


for article in list(IN_PATH.rglob('*.xml')):
    print(f'Parsing: {str(article)} ...')
    text = article.read_bytes()
    tree = etree.fromstring(text)
    sections = tree.xpath('//sec')
    section_types = set()
    for sec in sections:
        if sec.get('sec-type'):
            section_types.add(sec.get('sec-type'))

    for sec_type in section_types:
        tables = tree.xpath(f'//sec[@sec-type="{sec_type}"]//table-wrap')
        for i, table in enumerate(tables):
            subdir = OUT_PATH / Path(str(article.parts[-1])) / Path(sec_type)
            subdir.mkdir(parents=True, exist_ok=True)
            outfile = subdir / Path(f'table-{str(i)}.xml')
            with open(outfile, "wb") as f:
                f.write(etree.tostring(table))
