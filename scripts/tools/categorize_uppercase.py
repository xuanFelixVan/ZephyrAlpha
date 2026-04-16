"""临时分析脚本：分类所有大写文件"""
import os, re
from pathlib import Path

root = Path('D:/ZephyrAlpha')
fixed_names = {'README.md', 'INDEX.md', 'AGENTS.md', 'CHANGELOG.md',
               'LICENSE', 'SITEMAP.md', 'CONTRIBUTING.md', 'SECURITY.md'}
ke_pat = re.compile(r'^KE-\d{3}-[a-z0-9-]+\.md$')
dr_pat = re.compile(r'^DR-[A-Z]+-\d{8}-\d{3}\.md$')
sess_pat = re.compile(r'^session-\d{8}.*\.md$')

EXCLUDE_DIRS = {'.git', '.venv', '.venv-1', '.trae', 'review_materials_package'}

rename_core = []
rename_archive = []
skip_compliant = []

for fp in root.rglob('*.md'):
    parts = set(fp.parts)
    if any(e in parts for e in EXCLUDE_DIRS):
        continue
    fname = fp.name
    if fname in fixed_names:
        continue
    if not re.search(r'[A-Z]', fname):
        continue
    if ke_pat.match(fname) or dr_pat.match(fname) or sess_pat.match(fname):
        skip_compliant.append(str(fp.relative_to(root)))
        continue
    rel = str(fp.relative_to(root))
    if any(x in rel for x in ['09_AUDIT\\STATE', '09_AUDIT\\REPORTS', '06_ARCHIVE', '11_STRATEGIC']):
        rename_archive.append(rel)
    else:
        rename_core.append(rel)

print('=== 核心文件（高引用率，需优先重命名）===')
for f in sorted(rename_core):
    print('  ' + f)

print()
print('=== 存档/状态文件（低引用，后期波次）===')
for f in sorted(rename_archive):
    print('  ' + f)

print()
print('=== 汇总 ===')
print('  核心文件（需重命名）:', len(rename_core))
print('  存档文件（需重命名）:', len(rename_archive))
print('  KE/DR/session（已合规，无需改）:', len(skip_compliant))
