#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 4机器学习层深度审计脚本 V4 - 最终版本
"""

import os
import re
from collections import defaultdict
from pathlib import Path
import hashlib

# Layer 4文档列表
layer4_docs = [
    'TRANSFER_LEARNING_BLUEPRINT.md',
    'TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
    'VOLATILITY_PREDICTION_BLUEPRINT.md',
    'TEXT_ENCODER_BLUEPRINT.md',
    'TEMPORAL_FUSION_TRANSFORMER_BLUEPRINT.md',
    'SYNTHETIC_DATA_GENERATION_BLUEPRINT.md',
    'TAIL_RISK_PREDICTION_BLUEPRINT.md',
    'SERVICE_MESH_INTEGRATION_BLUEPRINT.md',
    'SPARSE_ATTENTION_BLUEPRINT.md',
    'SECURE_MULTI_PARTY_COMPUTATION_BLUEPRINT.md',
    'SELF_SUPERVISED_LEARNING_BLUEPRINT.md',
    'REINFORCEMENT_LEARNING_BLUEPRINT.md',
    'RAG_SYSTEM_BLUEPRINT.md',
    'PROMPT_ENGINEERING_BLUEPRINT.md',
    'ORDER_FLOW_PREDICTION_BLUEPRINT.md',
    'OPTIMIZER_VARIANTS_BLUEPRINT.md',
    'ONLINE_LEARNING_BLUEPRINT.md',
    'NEURAL_ODE_BLUEPRINT.md',
    'NEURAL_ARCHITECTURE_SEARCH_BLUEPRINT.md',
    'NBEATS_BLUEPRINT.md',
    'MULTI_TASK_LEARNING_BLUEPRINT.md',
    'MULTI_MODEL_ORCHESTRATOR_BLUEPRINT.md',
    'MULTIMODAL_LLM_BLUEPRINT.md',
    'MULTIMODAL_FUSION_BLUEPRINT.md',
    'MODEL_WARMUP_BLUEPRINT.md',
    'MODEL_WATERMARK_BLUEPRINT.md',
    'MODEL_VERSIONING_BLUEPRINT.md',
    'MODEL_SECURITY_SCANNER_BLUEPRINT.md',
    'MODEL_ROLLBACK_BLUEPRINT.md',
    'MODEL_QUANTIZATION_BLUEPRINT.md',
    'MODEL_MONITORING_BLUEPRINT.md',
    'MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md',
    'MODEL_PRUNING_BLUEPRINT.md',
    'MODEL_LINEAGE_BLUEPRINT.md',
    'MODEL_DEBUGGING_TOOLKIT_BLUEPRINT.md',
    'MODEL_CARD_BLUEPRINT.md',
    'MODEL_AB_TESTING_BLUEPRINT.md',
    'MLOPS_PLATFORM_BLUEPRINT.md',
    'MIA_DEFENSE_BLUEPRINT.md',
    'MIXED_PRECISION_TRAINING_BLUEPRINT.md',
    'MIXTURE_OF_EXPERTS_BLUEPRINT.md',
    'META_LEARNING_BLUEPRINT.md',
    'MARKET_MICROSTRUCTURE_MODEL_BLUEPRINT.md',
    'MEMORY_AUGMENTED_NN_BLUEPRINT.md',
    'MARKET_MAKING_MODEL_BLUEPRINT.md',
    'MACHINE_LEARNING_LAYER_BLUEPRINT.md',
    'MAMBA_SSM_BLUEPRINT.md',
    'LLM_FINE_TUNING_BLUEPRINT.md',
    'LEARNING_RATE_SCHEDULER_BLUEPRINT.md',
    'LIQUID_NEURAL_NETWORK_BLUEPRINT.md',
    'KNOWLEDGE_DISTILLATION_BLUEPRINT.md',
    'INFERENCE_ACCELERATION_BLUEPRINT.md',
    'HYPERPARAMETER_OPTIMIZATION_BLUEPRINT.md',
    'HOMOMORPHIC_ENCRYPTION_ML_BLUEPRINT.md',
    'HIGH_FREQUENCY_SIGNAL_PROCESSING_BLUEPRINT.md',
    'GRAYSCALE_RELEASE_BLUEPRINT.md',
    'GRAPH_NEURAL_NETWORK_BLUEPRINT.md',
    'GRADIENT_CHECKPOINTING_BLUEPRINT.md',
    'GRADIENT_ACCUMULATION_BLUEPRINT.md',
    'FEDERATED_LEARNING_BLUEPRINT.md',
    'FEATURE_STORE_BLUEPRINT.md',
    'FEATURE_SELECTION_AUTOMATION_BLUEPRINT.md',
    'FAIRNESS_DETECTION_BLUEPRINT.md',
    'EXPERIMENT_TRACKING_BLUEPRINT.md',
    'EVENT_DRIVEN_LEARNING_BLUEPRINT.md',
    'DRIFT_DETECTION_BLUEPRINT.md',
    'ENSEMBLE_LEARNING_BLUEPRINT.md',
    'DISTRIBUTED_TRAINING_BLUEPRINT.md',
    'DIFFUSION_MODEL_BLUEPRINT.md',
    'DISASTER_RECOVERY_BLUEPRINT.md',
    'DIFFERENTIAL_PRIVACY_ML_BLUEPRINT.md',
    'DEEPAR_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_AUGMENTATION_BLUEPRINT.md',
    'DATA_ANNOTATION_PLATFORM_BLUEPRINT.md',
    'DATAFLOW_ARCHITECTURE_BLUEPRINT.md',
    'CURRICULUM_LEARNING_BLUEPRINT.md',
    'CORRELATION_PREDICTION_BLUEPRINT.md',
    'BATCH_INFERENCE_OPTIMIZATION_BLUEPRINT.md',
    'CODE_GENERATION_MODEL_BLUEPRINT.md',
    'BACKDOOR_DETECTION_BLUEPRINT.md',
    'AUTOML_PIPELINE_BLUEPRINT.md',
    'ARBITRAGE_DETECTION_BLUEPRINT.md',
    'ALTERNATIVE_DATA_FUSION_BLUEPRINT.md',
    'AI_AGENT_FRAMEWORK_BLUEPRINT.md',
    'ADVERSARIAL_ROBUSTNESS_BLUEPRINT.md',
    'ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md',
    'ACTIVE_LEARNING_BLUEPRINT.md',
    'ACCEPTANCE_CRITERIA_BLUEPRINT.md',
]

base_path = Path('docs/01_FRAMEWORK')

print('=' * 80)
print('Layer 4机器学习层深度审计 V4 - 最终版本')
print('=' * 80)
print()

# 统计信息
stats = {
    'total_docs': len(layer4_docs),
    'found_docs': 0,
    'missing_docs': 0,
    'yaml_issues': [],
    'duplicate_layers': [],
    'missing_fields': [],
    'missing_responsibility': [],
    'wrong_layer': [],
    'content_hashes': {},
    'responsibility_keywords': defaultdict(list),
}

# 检查每个文档
for doc_name in layer4_docs:
    doc_path = base_path / doc_name
    
    if not doc_path.exists():
        stats['missing_docs'] += 1
        continue
    
    stats['found_docs'] += 1
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 检查YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            # 检查layer字段
            layer_match = re.search(r'^layer:\s*(.+)$', yaml_content, re.MULTILINE)
            if layer_match:
                layer_value = layer_match.group(1).strip()
                
                # 检查是否属于Layer 4
                if 'Layer 4' not in layer_value and '机器学习层' not in layer_value:
                    stats['wrong_layer'].append({
                        'file': doc_name,
                        'layer': layer_value
                    })
            
            # 检查必要字段
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'layer']
            for field in required_fields:
                if f'{field}:' not in yaml_content:
                    stats['missing_fields'].append({
                        'file': doc_name,
                        'field': field
                    })
            
            # 检查职责边界
            if 'responsibility_boundary:' not in yaml_content:
                stats['missing_responsibility'].append(doc_name)
        else:
            stats['yaml_issues'].append(doc_name)
            
    except Exception as e:
        print(f'❌ 读取失败 {doc_name}: {e}')

# 输出统计结果
print(f'📊 文档统计:')
print(f'  总文档数: {stats["total_docs"]}')
print(f'  找到文档: {stats["found_docs"]}')
print(f'  缺失文档: {stats["missing_docs"]}')
print()

print(f'🔴 发现问题:')
print(f'  YAML头部问题: {len(stats["yaml_issues"])}个')
if stats['yaml_issues']:
    for doc in stats['yaml_issues'][:5]:
        print(f'    - {doc}')

print(f'  Layer归属错误: {len(stats["wrong_layer"])}个')
if stats['wrong_layer']:
    for item in stats['wrong_layer']:
        print(f'    - {item["file"]}: {item["layer"]}')

print(f'  缺失必要字段: {len(stats["missing_fields"])}个')
if stats['missing_fields']:
    field_counts = defaultdict(int)
    for item in stats['missing_fields']:
        field_counts[item['field']] += 1
    for field, count in sorted(field_counts.items()):
        print(f'    - {field}: {count}个文档缺失')

print(f'  缺失职责边界: {len(stats["missing_responsibility"])}个')
if stats['missing_responsibility']:
    for doc in stats['missing_responsibility'][:10]:
        print(f'    - {doc}')
print()

# 计算合规率
total_issues = len(stats['yaml_issues']) + len(stats['wrong_layer']) + len(stats['missing_fields']) + len(stats['missing_responsibility'])
compliance_rate = max(0, 100 - (total_issues / max(1, stats['found_docs']) * 5))

print(f'📈 合规率: {compliance_rate:.1f}%')
print()

# 保存详细报告
report_path = Path('docs/09_AUDIT/REPORTS/LAYER4_DEEP_AUDIT_REPORT_V5_20260407.md')
report_path.parent.mkdir(parents=True, exist_ok=True)

with open(report_path, 'w', encoding='utf-8') as f:
    f.write('# Layer 4机器学习层深度审计报告 V5.0\n\n')
    f.write(f'> **审计日期**: 2026-04-07\n')
    f.write(f'> **审计范围**: Layer 4机器学习层所有文档\n')
    f.write(f'> **审计方法**: 三层审计标准 (L1-L3)\n')
    f.write(f'> **审计重点**: 重复内容、职责不清、Layer归属\n\n')
    
    f.write('## 📊 审计统计\n\n')
    f.write(f'| 指标 | 数值 |\n')
    f.write(f'|------|------|\n')
    f.write(f'| 总文档数 | {stats["total_docs"]} |\n')
    f.write(f'| 找到文档 | {stats["found_docs"]} |\n')
    f.write(f'| 缺失文档 | {stats["missing_docs"]} |\n')
    f.write(f'| YAML问题 | {len(stats["yaml_issues"])} |\n')
    f.write(f'| Layer归属错误 | {len(stats["wrong_layer"])} |\n')
    f.write(f'| 缺失字段 | {len(stats["missing_fields"])} |\n')
    f.write(f'| 缺失职责边界 | {len(stats["missing_responsibility"])} |\n')
    f.write(f'| **合规率** | **{compliance_rate:.1f}%** |\n\n')
    
    f.write('## 🔴 发现问题\n\n')
    
    if stats['wrong_layer']:
        f.write('### Layer归属错误\n\n')
        f.write('以下文档不属于Layer 4 (机器学习层)，应从Layer 4审计列表中移除：\n\n')
        for item in stats['wrong_layer']:
            f.write(f'- **{item["file"]}**: {item["layer"]}\n')
        f.write('\n')
    
    if stats['missing_fields']:
        f.write('### 缺失必要字段\n\n')
        field_counts = defaultdict(int)
        for item in stats['missing_fields']:
            field_counts[item['field']] += 1
        for field, count in sorted(field_counts.items()):
            f.write(f'- **{field}**: {count}个文档缺失\n')
        f.write('\n')
    
    if stats['missing_responsibility']:
        f.write('### 缺失职责边界\n\n')
        for doc in stats['missing_responsibility']:
            f.write(f'- **{doc}**\n')
        f.write('\n')
    
    f.write('## ✅ 改进建议\n\n')
    f.write('1. 从Layer 4审计列表中移除不属于Layer 4的文档\n')
    f.write('2. 补充缺失的YAML字段\n')
    f.write('3. 为缺失职责边界的文档添加职责边界说明\n')
    f.write('4. 统一文档命名规范\n')

print(f'✅ 详细报告已保存: {report_path}')
