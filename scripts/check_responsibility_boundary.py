#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定文档的职责边界
"""

import re
from pathlib import Path

docs = [
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'REINFORCEMENT_LEARNING_BLUEPRINT.md',
    'ONLINE_LEARNING_BLUEPRINT.md',
    'MODEL_MONITORING_BLUEPRINT.md',
    'MLOPS_PLATFORM_BLUEPRINT.md',
    'FEATURE_STORE_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'DRIFT_DETECTION_BLUEPRINT.md',
    'DISASTER_RECOVERY_FRAMEWORK_ENTRY.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
]

base_path = Path('docs/01_FRAMEWORK')

print('=' * 80)
print('检查文档的职责边界')
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
            
            # 检查是否有responsibility_boundary字段
            if 'responsibility_boundary:' in yaml_content:
                # 提取responsibility_boundary内容
                resp_match = re.search(r'responsibility_boundary:\s*\|?\s*(.*?)(?=\n\w+:|\n---)', yaml_content, re.DOTALL)
                
                if resp_match:
                    resp_text = resp_match.group(1).strip()
                    print(f'✅ {doc_name}')
                    print(f'   职责边界长度: {len(resp_text)} 字符')
                    print(f'   职责边界预览: {resp_text[:80]}...')
                else:
                    print(f'⚠️  {doc_name}: 有responsibility_boundary字段但无法提取内容')
            else:
                print(f'❌ {doc_name}: 缺少responsibility_boundary字段')
        else:
            print(f'❌ {doc_name}: 未找到YAML头部')
        
        print()
        
    except Exception as e:
        print(f'❌ 读取失败 {doc_name}: {e}')
        print()
