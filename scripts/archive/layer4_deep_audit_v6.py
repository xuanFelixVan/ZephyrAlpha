#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 4深度审计脚本V6
检查重复内容、职责重叠、职责不清等问题
"""

import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

class Layer4DeepAuditor:
    def __init__(self):
        self.layer4_docs = []
        self.audit_results = {
            'L1_file_system': [],
            'L2_content': [],
            'L3_professional': []
        }
        self.duplicate_content = []
        self.responsibility_overlap = []
        self.unclear_responsibility = []
        
    def scan_layer4_docs(self):
        """扫描所有Layer 4文档"""
        print('=' * 80)
        print('Layer 4深度审计')
        print('=' * 80)
        print()
        
        # 使用Grep结果
        layer4_files = [
            'docs/10_AI_WORKFLOW/OPEN_SOURCE_INTEGRATION_BLUEPRINT.md',
            'docs/08_HUMAN_AI_INTERFACE/10_CONFIG_MANAGEMENT/CONFIG_MANAGEMENT_BLUEPRINT.md',
            'docs/08_HUMAN_AI_INTERFACE/06_REPORTING/REPORTING_BLUEPRINT.md',
            'docs/08_HUMAN_AI_INTERFACE/02_ALERTING/ALERTING_SYSTEM_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LIQUIDITY_CONSTRAINED_OPTIMIZATION_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONSTRAINT_SOLVER_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AUTO_REPAIR_ENGINE_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/REINFORCEMENT_LEARNING_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/PROBABILISTIC_FORECASTING_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MODEL_MONITORING_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MODEL_INTERPRETABILITY_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MLOPS_PLATFORM_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/DRIFT_DETECTION_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/CAUSAL_INFERENCE_TECHNICAL_SPECIFICATION.md',
            'docs/01_FRAMEWORK/TRUSTED_EXECUTION_ENVIRONMENT_BLUEPRINT.md',
            'docs/01_FRAMEWORK/VOLATILITY_PREDICTION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/TEXT_ENCODER_BLUEPRINT.md',
            'docs/01_FRAMEWORK/TAIL_RISK_PREDICTION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/SYNTHETIC_DATA_GENERATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/SPARSE_ATTENTION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/SENTIMENT_ANALYSIS_LAYER_BLUEPRINT.md',
            'docs/01_FRAMEWORK/SELF_SUPERVISED_LEARNING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/SECURE_MULTI_PARTY_COMPUTATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/RAG_SYSTEM_BLUEPRINT.md',
            'docs/01_FRAMEWORK/NEURAL_ODE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/NBEATS_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_WATERMARK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_VERSIONING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_SERVING_FRAMEWORK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_REGISTRY_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_QUANTIZATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_PRUNING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_PERFORMANCE_BENCHMARK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_MONITORING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_DEBUGGING_TOOLKIT_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_AB_TESTING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MODEL_CARD_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MLOPS_PLATFORM_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MIXED_PRECISION_TRAINING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MIXTURE_OF_EXPERTS_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MIA_DEFENSE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MEMORY_AUGMENTED_NN_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MARKET_MICROSTRUCTURE_MODEL_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MAMBA_SSM_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MACHINE_LEARNING_LAYER_BLUEPRINT.md',
            'docs/01_FRAMEWORK/LIQUID_NEURAL_NETWORK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/INFERENCE_ACCELERATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/HOMOMORPHIC_ENCRYPTION_ML_BLUEPRINT.md',
            'docs/01_FRAMEWORK/GRAPH_NEURAL_NETWORK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/GRADIENT_CHECKPOINTING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/GRADIENT_ACCUMULATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/FEDERATED_LEARNING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/EXPERIMENT_TRACKING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DIFFUSION_MODEL_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DIFFERENTIAL_PRIVACY_ML_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DEEPAR_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DATA_AUGMENTATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DATA_ANNOTATION_PLATFORM_BLUEPRINT.md',
            'docs/01_FRAMEWORK/CODE_GENERATION_MODEL_BLUEPRINT.md',
            'docs/01_FRAMEWORK/BACKDOOR_DETECTION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/BATCH_INFERENCE_OPTIMIZATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/AUTOML_PIPELINE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/AI_AGENT_FRAMEWORK_BLUEPRINT.md',
            'docs/01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_HEDGING_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_METRICS_EXTENSION_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_PATTERN_RECOGNITION_ENGINE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DATA_QUALITY_MONITORING_BLUEPRINT.md',
            'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER4_ML_COMPREHENSIVE_AUDIT_V5_20260404.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/ONLINE_LEARNING_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MODEL_GOVERNANCE_TECHNICAL_SPECIFICATION.md',
            'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/FEATURE_STORE_TECHNICAL_SPECIFICATION.md',
            'docs/11_STRATEGIC_DECISION/MARKET_REGIME_BLUEPRINT.md',
            'docs/10_AI_WORKFLOW/MODEL_DRIFT_DETECTION_BLUEPRINT.md',
            'docs/10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/REINFORCEMENT_LEARNING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/ONLINE_LEARNING_BLUEPRINT.md',
            'docs/01_FRAMEWORK/MULTI_MODEL_ORCHESTRATOR_BLUEPRINT.md',
            'docs/01_FRAMEWORK/NEWLY_DISCOVERED_MODULES_BLUEPRINT_COLLECTION.md',
            'docs/01_FRAMEWORK/LAYER4_MACHINE_LEARNING_COMPREHENSIVE_ANALYSIS.md',
            'docs/01_FRAMEWORK/LAYER4_P2_FRONTIER_MODULES_BLUEPRINT_COLLECTION.md',
            'docs/01_FRAMEWORK/FEATURE_STORE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DRIFT_DETECTION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DATA_PREPROCESSING_LAYER_BLUEPRINT.md',
            'docs/01_FRAMEWORK/DATAFLOW_ARCHITECTURE_BLUEPRINT.md',
            'docs/01_FRAMEWORK/AI_TRUST_CALIBRATION_BLUEPRINT.md',
            'docs/01_FRAMEWORK/AI_CAPABILITY_GAP_BLUEPRINT.md',
            'docs/01_FRAMEWORK/ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md',
            'docs/06_ARCHIVE/20260404_audit_reports_archive/audit_state/LAYER4_ML_COMPREHENSIVE_GAP_ANALYSIS_V2_20260403.md',
        ]
        
        for file_path in layer4_files:
            if os.path.exists(file_path):
                self.layer4_docs.append(file_path)
        
        print(f'扫描到 {len(self.layer4_docs)} 个Layer 4文档')
        print()
        
        return self.layer4_docs
    
    def extract_yaml_field(self, content, field_name):
        """提取YAML字段"""
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        yaml_match = re.search(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            field_pattern = rf'^{field_name}:\s*(.+)$'
            field_match = re.search(field_pattern, yaml_content, re.MULTILINE)
            
            if field_match:
                return field_match.group(1).strip()
        
        return None
    
    def extract_responsibility(self, content):
        """提取职责描述"""
        # 从YAML头部提取responsibility字段
        responsibility = self.extract_yaml_field(content, 'responsibility')
        if responsibility:
            return responsibility
        
        # 从文档内容提取职责描述
        responsibility_patterns = [
            r'\*\*本文档职责\*\*:\s*(.+?)(?:\n|$)',
            r'核心定位[：:]\s*(.+?)(?:\n|$)',
            r'职责[：:]\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in responsibility_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def check_duplicate_content(self):
        """检查重复内容"""
        print('检查重复内容...')
        
        content_hashes = defaultdict(list)
        
        for doc_path in self.layer4_docs:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取核心内容（去除YAML头部）
                yaml_pattern = r'^---\s*\n.*?\n---'
                core_content = re.sub(yaml_pattern, '', content, flags=re.DOTALL | re.MULTILINE)
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', core_content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    content_hashes[title].append(doc_path)
                
                # 提取module_id
                module_id = self.extract_yaml_field(content, 'module_id')
                if module_id:
                    content_hashes[f'module_id:{module_id}'].append(doc_path)
                
            except Exception as e:
                print(f'  ✗ {doc_path}: {str(e)}')
        
        # 找出重复的内容
        for key, docs in content_hashes.items():
            if len(docs) > 1:
                self.duplicate_content.append({
                    'type': '标题重复' if not key.startswith('module_id:') else 'module_id重复',
                    'key': key,
                    'docs': docs
                })
        
        print(f'  发现 {len(self.duplicate_content)} 个重复内容')
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        print('检查职责重叠...')
        
        responsibilities = {}
        
        for doc_path in self.layer4_docs:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                responsibility = self.extract_responsibility(content)
                if responsibility:
                    responsibilities[doc_path] = responsibility
                
            except Exception as e:
                print(f'  ✗ {doc_path}: {str(e)}')
        
        # 检查职责重叠
        responsibility_groups = defaultdict(list)
        for doc_path, responsibility in responsibilities.items():
            # 提取关键词
            keywords = re.findall(r'[\u4e00-\u9fa5]+', responsibility)
            for keyword in keywords:
                if len(keyword) >= 2:  # 至少2个字符
                    responsibility_groups[keyword].append({
                        'doc': doc_path,
                        'responsibility': responsibility
                    })
        
        # 找出职责重叠的文档
        for keyword, docs in responsibility_groups.items():
            if len(docs) > 1:
                self.responsibility_overlap.append({
                    'keyword': keyword,
                    'docs': docs
                })
        
        print(f'  发现 {len(self.responsibility_overlap)} 个职责重叠')
    
    def check_unclear_responsibility(self):
        """检查职责不清的文档"""
        print('检查职责不清的文档...')
        
        for doc_path in self.layer4_docs:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                responsibility = self.extract_responsibility(content)
                
                if not responsibility:
                    self.unclear_responsibility.append({
                        'doc': doc_path,
                        'issue': '缺少职责描述'
                    })
                elif len(responsibility) < 10:
                    self.unclear_responsibility.append({
                        'doc': doc_path,
                        'issue': '职责描述过短',
                        'responsibility': responsibility
                    })
                
            except Exception as e:
                print(f'  ✗ {doc_path}: {str(e)}')
        
        print(f'  发现 {len(self.unclear_responsibility)} 个职责不清的文档')
    
    def generate_audit_report(self):
        """生成审计报告"""
        print()
        print('=' * 80)
        print('审计结果汇总')
        print('=' * 80)
        print()
        
        report_lines = []
        report_lines.append('# Layer 4深度审计报告\n')
        report_lines.append(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        report_lines.append(f'> **审计范围**: Layer 4机器学习层\n')
        report_lines.append(f'> **审计文档数**: {len(self.layer4_docs)}\n\n')
        
        # L1文件系统层问题
        report_lines.append('## 🔴 L1文件系统层问题\n\n')
        report_lines.append(f'### 1.1 目录结构问题\n\n')
        report_lines.append(f'- **文档分布**: Layer 4文档分布在多个目录\n')
        report_lines.append(f'  - docs/01_FRAMEWORK/: {len([d for d in self.layer4_docs if "01_FRAMEWORK" in d])}个\n')
        report_lines.append(f'  - docs/05_IMPLEMENTATION/: {len([d for d in self.layer4_docs if "05_IMPLEMENTATION" in d])}个\n')
        report_lines.append(f'  - docs/10_AI_WORKFLOW/: {len([d for d in self.layer4_docs if "10_AI_WORKFLOW" in d])}个\n')
        report_lines.append(f'  - docs/08_HUMAN_AI_INTERFACE/: {len([d for d in self.layer4_docs if "08_HUMAN_AI_INTERFACE" in d])}个\n')
        report_lines.append(f'  - docs/11_STRATEGIC_DECISION/: {len([d for d in self.layer4_docs if "11_STRATEGIC_DECISION" in d])}个\n\n')
        
        # L2文档内容层问题
        report_lines.append('## 🟡 L2文档内容层问题\n\n')
        
        # 重复内容
        report_lines.append(f'### 2.1 重复内容问题\n\n')
        if self.duplicate_content:
            report_lines.append(f'发现 {len(self.duplicate_content)} 个重复内容问题：\n\n')
            for dup in self.duplicate_content[:10]:  # 只显示前10个
                report_lines.append(f'**{dup["type"]}**: {dup["key"]}\n')
                for doc in dup["docs"]:
                    report_lines.append(f'  - {doc}\n')
                report_lines.append('\n')
        else:
            report_lines.append('✅ 未发现重复内容问题\n\n')
        
        # 职责重叠
        report_lines.append(f'### 2.2 职责重叠问题\n\n')
        if self.responsibility_overlap:
            report_lines.append(f'发现 {len(self.responsibility_overlap)} 个职责重叠问题：\n\n')
            for overlap in self.responsibility_overlap[:10]:  # 只显示前10个
                report_lines.append(f'**关键词**: {overlap["keyword"]}\n')
                for doc_info in overlap["docs"]:
                    report_lines.append(f'  - {doc_info["doc"]}: {doc_info["responsibility"]}\n')
                report_lines.append('\n')
        else:
            report_lines.append('✅ 未发现职责重叠问题\n\n')
        
        # 职责不清
        report_lines.append(f'### 2.3 职责不清问题\n\n')
        if self.unclear_responsibility:
            report_lines.append(f'发现 {len(self.unclear_responsibility)} 个职责不清的文档：\n\n')
            for unclear in self.unclear_responsibility:
                report_lines.append(f'- {unclear["doc"]}: {unclear["issue"]}\n')
                if 'responsibility' in unclear:
                    report_lines.append(f'  - 职责描述: {unclear["responsibility"]}\n')
            report_lines.append('\n')
        else:
            report_lines.append('✅ 未发现职责不清问题\n\n')
        
        # L3专业标准层问题
        report_lines.append('## 🟢 L3专业标准层问题\n\n')
        report_lines.append(f'### 3.1 五大原则符合性\n\n')
        report_lines.append(f'- **职责驱动原则**: {len(self.unclear_responsibility)}个文档存在问题\n')
        report_lines.append(f'- **索引完备性原则**: 需要检查INDEX.md\n')
        report_lines.append(f'- **版本隔离原则**: 需要检查重复文档\n')
        report_lines.append(f'- **文档代码对应原则**: 需要检查代码目录\n')
        report_lines.append(f'- **命名规范原则**: 需要检查命名格式\n\n')
        
        # 改进建议
        report_lines.append('## 📋 改进建议\n\n')
        report_lines.append('### 立即修复项 (P0)\n\n')
        if self.duplicate_content:
            report_lines.append('1. **删除重复文档**: 合并或删除重复的文档\n')
        if self.unclear_responsibility:
            report_lines.append('2. **明确职责描述**: 为职责不清的文档添加明确的职责描述\n')
        report_lines.append('\n### 短期改进项 (P1)\n\n')
        report_lines.append('1. **优化目录结构**: 将Layer 4文档集中管理\n')
        report_lines.append('2. **完善索引**: 确保所有文档都被索引\n')
        report_lines.append('\n### 长期优化项 (P2)\n\n')
        report_lines.append('1. **建立文档治理流程**: 定期审计文档质量\n')
        report_lines.append('2. **自动化检查**: 使用脚本定期检查文档质量\n\n')
        
        # 保存报告
        report_path = Path('docs/09_AUDIT/REPORTS/LAYER4_DEEP_AUDIT_REPORT_V6_20260407.md')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(report_lines)
        
        print(f'审计报告已保存: {report_path}')
        
        # 保存JSON结果
        result = {
            'audit_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_docs': len(self.layer4_docs),
            'duplicate_content_count': len(self.duplicate_content),
            'responsibility_overlap_count': len(self.responsibility_overlap),
            'unclear_responsibility_count': len(self.unclear_responsibility),
            'duplicate_content': self.duplicate_content,
            'responsibility_overlap': self.responsibility_overlap,
            'unclear_responsibility': self.unclear_responsibility
        }
        
        result_path = Path('docs/09_AUDIT/STATE/layer4_deep_audit_result_v6.json')
        result_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f'审计结果已保存: {result_path}')
    
    def run_audit(self):
        """运行完整审计"""
        self.scan_layer4_docs()
        self.check_duplicate_content()
        self.check_responsibility_overlap()
        self.check_unclear_responsibility()
        self.generate_audit_report()

if __name__ == '__main__':
    auditor = Layer4DeepAuditor()
    auditor.run_audit()
