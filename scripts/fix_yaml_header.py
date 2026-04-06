import shutil

source_file = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION.md'
target_file = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(source_file, 'r', encoding='utf-8') as f:
    source_lines = f.readlines()

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    target_content = f.read()

yaml_header = '''---
module_id: SENTIMENT_ANALYSIS_SHORT_TERM_TS_001
version: 1.1.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-04
owner: 首席架构师
standard_type: 技术规格书
applicable_scope: 舆情分析层短期改进模块
compliance_level: 专业标准
applicable_modules:
  - 数据源扩展
  - 深度学习情感分析
  - 实时预警系统
---
'''

import re
content_without_yaml = re.sub(r'^---\n.*?\n---\n', '', target_content, flags=re.DOTALL)

new_content = yaml_header + content_without_yaml

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('文件YAML头部修复完成！')
print('\n前20行:')
with open(target_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f.readlines()[:20], 1):
        print(f'{i}: {line}', end='')
