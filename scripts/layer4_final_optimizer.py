# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Layer 4最终优化修复脚本
处理剩余的文档分类和职责重叠问题
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

class Layer4FinalOptimizer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "classification_fix": {"fixed": 0, "details": []},
            "responsibility_differentiation": {"fixed": 0, "details": []}
        }
        
    def fix_layer_classification(self):
        """修复Layer分类错误"""
        print("\n" + "="*80)
        print("修复Layer分类错误")
        print("="*80)
        
        doc_path = self.project_root / "docs" / "01_FRAMEWORK" / "LAYER4_ML" / "DEEP_AUDIT_REPORT_V3_20260407.md"
        
        if not doc_path.exists():
            print(f"  文档不存在: {doc_path}")
            return
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_layer = "layer: Layer 10 (治理合规层)"
        new_layer = "layer: Layer 4 (机器学习层)"
        
        if old_layer in content:
            content = content.replace(old_layer, new_layer)
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fix_log["classification_fix"]["fixed"] = 1
            self.fix_log["classification_fix"]["details"].append({
                "doc": str(doc_path.relative_to(self.project_root)),
                "old": old_layer,
                "new": new_layer
            })
            print(f"  ✓ 修复: {doc_path.name}")
            print(f"    旧Layer: {old_layer}")
            print(f"    新Layer: {new_layer}")
        else:
            print(f"  跳过: Layer已正确或格式不同")
        
    def differentiate_responsibilities(self):
        """差异化职责描述"""
        print("\n" + "="*80)
        print("差异化职责描述")
        print("="*80)
        
        differentiation_map = {
            "docs/01_FRAMEWORK/ARCHITECTURE.md": {
                "old": "定义清风量化系统的整体架构设计、模块组织和层级关系，确保系统架构清晰可维护",
                "new": "定义清风量化系统的整体架构设计、模块组织和层级关系，作为系统架构的权威参考文档"
            },
            "docs/01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md": {
                "old": "定义清风量化系统的整体架构设计、模块组织和层级关系，确保系统架构清晰可维护",
                "new": "规划系统架构迁移的具体路径、时间节点和实施步骤，确保从旧架构到新架构的平滑过渡"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/DEEP_AUDIT_REPORT_20260407.md": {
                "old": "执行Layer 4机器学习层深度审计（20260407），生成审计报告和问题清单",
                "new": "执行Layer 4机器学习层首轮深度审计（20260407），生成审计报告和问题清单"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/MACHINE_LEARNING_GOVERNANCE_DEEP_AUDIT_REPORT_20260407.md": {
                "old": "执行Layer 4机器学习层深度审计（20260407），生成审计报告和问题清单",
                "new": "执行Layer 4机器学习层治理合规深度审计（20260407），重点检查治理标准和最佳实践符合性"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/DEEP_AUDIT_REPORT_V2_20260407.md": {
                "old": "执行Layer 4机器学习层第2轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层第2轮深度审计，聚焦职责驱动和索引完备性问题"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/ML_LAYER_DEEP_GOVERNANCE_AUDIT_V2_20260406.md": {
                "old": "执行Layer 4机器学习层第2轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层治理合规第2轮审计，重点检查文档治理合规性"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/DEEP_AUDIT_REPORT_V5_20260407.md": {
                "old": "执行Layer 4机器学习层第5轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层第5轮深度审计，聚焦职责描述增强和核心职责修复"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/ML_COMPREHENSIVE_AUDIT_V5_20260404.md": {
                "old": "执行Layer 4机器学习层第5轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层全面综合审计（第5轮），覆盖所有文档和模块的完整性检查"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/INDEX.md": {
                "old": "提供Layer 4机器学习层的文档导航和索引服务，帮助用户快速定位相关文档",
                "new": "提供Layer 4机器学习层的快速导航索引，列出核心模块和关键文档入口"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/MASTER_INDEX.md": {
                "old": "提供Layer 4机器学习层的文档导航和索引服务，帮助用户快速定位相关文档",
                "new": "提供Layer 4机器学习层的完整主索引，包含所有文档的详细清单和分类"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/ML_LAYER_COMPREHENSIVE_AUDIT_V1_20260405.md": {
                "old": "执行Layer 4机器学习层第1轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层全面综合审计（第1轮），建立审计基线和问题清单"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/ML_LAYER_GOVERNANCE_AUDIT_V1_20260405.md": {
                "old": "执行Layer 4机器学习层第1轮深度审计，生成详细审计报告和改进建议",
                "new": "执行Layer 4机器学习层治理合规首轮审计，建立治理合规检查标准"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/README.md": {
                "old": "提供Layer 4机器学习层的概述说明、快速开始指南和模块介绍",
                "new": "提供Layer 4机器学习层的主要概述说明、快速开始指南和核心模块介绍"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/README_1.md": {
                "old": "提供Layer 4机器学习层的概述说明、快速开始指南和模块介绍",
                "new": "提供Layer 4机器学习层的补充说明、扩展信息和最佳实践指南"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/YAML_COMPLETENESS_CHECK_REPORT.md": {
                "old": "检查Layer 4机器学习层文档YAML元数据完整性，生成检查报告和修复建议",
                "new": "检查Layer 4机器学习层文档YAML元数据完整性，生成完整性检查报告"
            },
            "docs/01_FRAMEWORK/LAYER4_ML/YAML_FIX_PROGRESS_REPORT_20260406.md": {
                "old": "检查Layer 4机器学习层文档YAML元数据完整性，生成检查报告和修复建议",
                "new": "跟踪Layer 4机器学习层文档YAML修复进度，生成修复进度报告"
            }
        }
        
        fixed_count = 0
        
        for doc, resp_map in differentiation_map.items():
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                print(f"  跳过: 文档不存在 - {doc}")
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                old_resp = resp_map["old"]
                new_resp = resp_map["new"]
                
                pattern = r'(>\s*\*\*核心职责\*\*:\s*)([^\n]+)'
                match = re.search(pattern, content)
                
                if match:
                    current_resp = match.group(2)
                    
                    if old_resp in current_resp or current_resp == old_resp:
                        content = re.sub(pattern, f'\\1{new_resp}', content)
                        
                        with open(doc_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        fixed_count += 1
                        self.fix_log["responsibility_differentiation"]["details"].append({
                            "doc": doc,
                            "old": old_resp,
                            "new": new_resp
                        })
                        print(f"  ✓ 修复: {doc_path.name}")
                        print(f"    新职责: {new_resp}")
                    else:
                        print(f"  跳过: 职责已不同 - {doc_path.name}")
                        
            except Exception as e:
                print(f"  ✗ 错误: {doc} - {str(e)}")
        
        self.fix_log["responsibility_differentiation"]["fixed"] = fixed_count
        print(f"\n职责差异化完成: {fixed_count}")
        
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_final_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        print(f"\n修复日志已保存至: {log_path}")
        
    def run(self):
        """执行修复"""
        print("="*80)
        print("Layer 4最终优化修复")
        print("="*80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-"*80)
        
        self.fix_layer_classification()
        self.differentiate_responsibilities()
        
        self.save_fix_log()
        
        print("\n" + "="*80)
        print("修复完成统计")
        print("="*80)
        print(f"Layer分类修复: {self.fix_log['classification_fix']['fixed']} 个")
        print(f"职责差异化修复: {self.fix_log['responsibility_differentiation']['fixed']} 个")
        
        total_fixed = self.fix_log['classification_fix']['fixed'] + self.fix_log['responsibility_differentiation']['fixed']
        print(f"\n总修复数: {total_fixed} 个")
        print("="*80)

if __name__ == "__main__":
    optimizer = Layer4FinalOptimizer()
    optimizer.run()
