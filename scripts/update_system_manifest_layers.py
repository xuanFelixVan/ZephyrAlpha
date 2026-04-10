#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新System_Manifest.md中的Layer归属
"""

import re
from pathlib import Path

# 需要更新Layer归属的文档
layer_updates = {
    'MODEL_LINEAGE_BLUEPRINT.md': 'Layer 0 (数据源层)',
    'ALTERNATIVE_DATA_FUSION_BLUEPRINT.md': 'Layer 0 (数据源层)',
    'TEMPORAL_FUSION_TRANSFORMER_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'SERVICE_MESH_INTEGRATION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'ORDER_FLOW_PREDICTION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'OPTIMIZER_VARIANTS_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'MULTI_TASK_LEARNING_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'MULTIMODAL_LLM_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'MODEL_SECURITY_SCANNER_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'MARKET_MAKING_MODEL_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'LLM_FINE_TUNING_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'KNOWLEDGE_DISTILLATION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'HYPERPARAMETER_OPTIMIZATION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'FAIRNESS_DETECTION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'ARBITRAGE_DETECTION_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'ADVERSARIAL_ROBUSTNESS_BLUEPRINT.md': 'Layer 2 (Alpha因子层)',
    'TRANSFER_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'PROMPT_ENGINEERING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'NEURAL_ARCHITECTURE_SEARCH_BLUEPRINT.md': 'Layer 3 (策略层)',
    'MULTIMODAL_FUSION_BLUEPRINT.md': 'Layer 3 (策略层)',
    'MODEL_WARMUP_BLUEPRINT.md': 'Layer 3 (策略层)',
    'MODEL_ROLLBACK_BLUEPRINT.md': 'Layer 3 (策略层)',
    'META_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'LEARNING_RATE_SCHEDULER_BLUEPRINT.md': 'Layer 3 (策略层)',
    'HIGH_FREQUENCY_SIGNAL_PROCESSING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'GRAYSCALE_RELEASE_BLUEPRINT.md': 'Layer 3 (策略层)',
    'FEATURE_SELECTION_AUTOMATION_BLUEPRINT.md': 'Layer 3 (策略层)',
    'EVENT_DRIVEN_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'ENSEMBLE_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'DISTRIBUTED_TRAINING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'CURRICULUM_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'CORRELATION_PREDICTION_BLUEPRINT.md': 'Layer 3 (策略层)',
    'ACTIVE_LEARNING_BLUEPRINT.md': 'Layer 3 (策略层)',
    'DISASTER_RECOVERY_FRAMEWORK_ENTRY.md': 'Layer 8 (框架入口 → 图纸柜灾备蓝图)',
}

print('=' * 80)
print('更新System_Manifest.md中的Layer归属')
print('=' * 80)
print()

# 读取System_Manifest.md
manifest_path = Path('docs/System_Manifest.md')
with open(manifest_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 统计更新
stats = {
    'total': len(layer_updates),
    'updated': 0,
    'not_found': [],
}

# 更新每个文档的Layer归属
for doc_name, new_layer in layer_updates.items():
    # 在System_Manifest.md中查找文档
    pattern = rf'\| \*\*{re.escape(doc_name.replace("_BLUEPRINT.md", ""))}\*\*.*?\| (Layer \d+) \|'
    match = re.search(pattern, content)
    
    if match:
        old_layer = match.group(1)
        # 更新Layer归属
        content = content.replace(
            match.group(0),
            match.group(0).replace(old_layer, new_layer)
        )
        stats['updated'] += 1
        print(f'✅ {doc_name}: {old_layer} → {new_layer}')
    else:
        stats['not_found'].append(doc_name)
        print(f'⚠️  {doc_name}: 未在System_Manifest.md中找到')

# 保存更新后的System_Manifest.md
with open(manifest_path, 'w', encoding='utf-8') as f:
    f.write(content)

print()
print('=' * 80)
print('更新统计')
print('=' * 80)
print(f'总文档数: {stats["total"]}')
print(f'成功更新: {stats["updated"]}')
print(f'未找到: {len(stats["not_found"])}')

if stats['not_found']:
    print()
    print('未找到的文档:')
    for doc in stats['not_found']:
        print(f'  - {doc}')

print()
print(f'✅ 已保存更新后的System_Manifest.md')
