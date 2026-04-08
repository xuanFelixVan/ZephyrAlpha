#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文件开头的BOM字符
"""

import chardet
from pathlib import Path

docs = [
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_AUGMENTATION_BLUEPRINT.md',
]

base_path = Path('docs/01_FRAMEWORK')

print('=' * 80)
print('检查文件开头的BOM字符')
print('=' * 80)
print()

for doc_name in docs:
    doc_path = base_path / doc_name
    
    with open(doc_path, 'rb') as f:
        raw = f.read(100)
    
    print(f'{doc_name}:')
    print(f'  前10字节: {raw[:10]}')
    print(f'  是否有UTF-8 BOM: {raw.startswith(b"\\xef\\xbb\\xbf")}')
    print(f'  是否有UTF-16 LE BOM: {raw.startswith(b"\\xff\\xfe")}')
    print(f'  是否有UTF-16 BE BOM: {raw.startswith(b"\\xfe\\xff")}')
    print(f'  检测编码: {chardet.detect(raw)}')
    print()
