#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
检查特定文档的YAML头部问题
"""

import re
from pathlib import Path

docs = [
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_AUGMENTATION_BLUEPRINT.md',
]

base_path = Path('docs/01_FRAMEWORK')

print('=' * 80)
print('检查特定文档的YAML头部')
print('=' * 80)
print()

for doc_name in docs:
    doc_path = base_path / doc_name
    
    if not doc_path.exists():
        print(f'❌ 文档不存在: {doc_name}')
        continue
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            print(f'✅ {doc_name}')
            print(f'   YAML头部长度: {len(yaml_content)} 字符')
            print(f'   包含responsibility_boundary: {"responsibility_boundary:" in yaml_content}')
            print(f'   包含layer: {"layer:" in yaml_content}')
            print(f'   包含module_id: {"module_id:" in yaml_content}')
            print()
        else:
            print(f'❌ {doc_name}: 未找到YAML头部')
            print()
            
    except Exception as e:
        print(f'❌ 读取失败 {doc_name}: {e}')
        print()
