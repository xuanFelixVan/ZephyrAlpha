import yaml

def parse_frontmatter(text_or_path):
    if isinstance(text_or_path, str) and len(text_or_path) < 260 and '\n' not in text_or_path:
        try:
            with open(text_or_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except (OSError, IOError):
            text = str(text_or_path)
    else:
        text = str(text_or_path)
    metadata = {}
    body = text
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            try:
                metadata = yaml.safe_load(text[3:end]) or {}
            except Exception:
                metadata = {}
            body = text[end + 3:].lstrip('\n')
    return metadata, body

def parse_frontmatter_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse_frontmatter(text)
