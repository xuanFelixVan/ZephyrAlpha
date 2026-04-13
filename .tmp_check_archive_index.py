import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

REPO  = Path('.')

# Sample the 06_ARCHIVE/INDEX.md broken links
d = json.loads(Path('docs/09_AUDIT/STATE/SENTINEL_L2_SCAN_20260413.json').read_text(encoding='utf-8'))
invalid = d['links']['invalid_details_sample']

archive_index_links = [item for item in invalid if item['source'] == 'docs/06_ARCHIVE/INDEX.md']
print(f'docs/06_ARCHIVE/INDEX.md broken links: {len(archive_index_links)}')
print()
print('First 15:')
for item in archive_index_links[:15]:
    print(f'  url     : {item["url"]}')
    print(f'  resolved: {item["resolved"]}')
    # Check if resolved target exists
    exists = (REPO / item["resolved"]).exists()
    print(f'  exists  : {exists}')
    print()

# Also check what's IN docs/06_ARCHIVE/INDEX.md
idx_path = REPO / 'docs/06_ARCHIVE/INDEX.md'
if idx_path.exists():
    content = idx_path.read_text(encoding='utf-8', errors='ignore')
    print(f'docs/06_ARCHIVE/INDEX.md size: {len(content)} chars')
    # Count links
    import re
    links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
    print(f'Total links in file: {len(links)}')
    print()
    print('First 10 links:')
    for text, url in links[:10]:
        print(f'  [{text}]({url})')
else:
    print('docs/06_ARCHIVE/INDEX.md does not exist!')
