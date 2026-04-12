#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
移除文件的UTF-8 BOM字符
"""

from pathlib import Path

docs = [
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_AUGMENTATION_BLUEPRINT.md',
]

base_path = Path('docs/01_FRAMEWORK')

print('=' * 80)
print('移除UTF-8 BOM字符')
print('=' * 80)
print()

stats = {
    'total': len(docs),
    'success': 0,
    'skipped': 0,
    'failed': 0,
}

for doc_name in docs:
    doc_path = base_path / doc_name
    
    try:
        # 读取文件内容
        with open(doc_path, 'rb') as f:
            raw_content = f.read()
        
        # 检查是否有UTF-8 BOM
        if raw_content.startswith(b'\xef\xbb\xbf'):
            # 移除BOM
            content = raw_content[3:].decode('utf-8')
            
            # 重新写入文件（不带BOM）
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            stats['success'] += 1
            print(f'✅ {doc_name}: 已移除BOM字符')
        else:
            stats['skipped'] += 1
            print(f'⏭️  {doc_name}: 无BOM字符，跳过')
    except Exception as e:
        stats['failed'] += 1
        print(f'❌ {doc_name}: {e}')

print()
print('=' * 80)
print('处理统计')
print('=' * 80)
print(f'总文档数: {stats["total"]}')
print(f'成功处理: {stats["success"]}')
print(f'已跳过: {stats["skipped"]}')
print(f'失败数: {stats["failed"]}')
