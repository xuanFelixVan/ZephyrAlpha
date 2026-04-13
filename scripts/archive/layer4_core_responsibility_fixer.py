# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Layer 4核心职责修复脚本
修复文档正文中的"核心职责"部分
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

class Layer4CoreResponsibilityFixer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_result_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_v4_20260407_124902.json"
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fixed": 0,
            "details": []
        }
        self.audit_data = None
        
    def load_audit_data(self):
        """加载审计结果"""
        with open(self.audit_result_path, 'r', encoding='utf-8') as f:
            self.audit_data = json.load(f)
        print(f"已加载审计结果: {self.audit_result_path}")
        
    def enhance_core_responsibility(self, doc_name):
        """增强核心职责描述"""
        responsibility_map = {
            "BLUEPRINT": f"提供{doc_name.replace('_', ' ').lower()}的完整架构设计、技术选型和实施路径规划",
            "TECHNICAL_SPECIFICATION": f"定义{doc_name.replace('_', ' ').lower()}的技术规格、接口标准和实现细节",
            "AUDIT": "执行文档治理审计，生成审计报告和改进建议",
            "REPORT": "分析系统状态，生成评估报告和优化建议",
            "PROCESS": "定义操作流程和执行规范，确保流程标准化",
            "STANDARD": "制定标准规范和质量要求，确保文档质量",
            "TEMPLATE": "提供标准化模板和格式规范，统一文档格式",
            "GUIDE": "提供详细指南和最佳实践，指导用户操作",
            "CHECKLIST": "提供检查清单和验证标准，确保质量门控",
            "ARCHITECTURE": "定义系统架构和模块组织，确保架构清晰",
            "MIGRATION": "规划架构迁移路径和实施步骤，确保平滑过渡"
        }
        
        for key, value in responsibility_map.items():
            if key in doc_name.upper():
                return value
        
        return f"负责{doc_name.replace('_', ' ').lower()}的设计、实现和维护工作"
        
    def fix_core_responsibility(self):
        """修复核心职责"""
        print("\n" + "="*80)
        print("修复核心职责")
        print("="*80)
        
        L2_issues = self.audit_data.get("L2_document_content", {}).get("responsibility_driven", [])
        deep_issues = self.audit_data.get("deep_check", {}).get("unclear_responsibility", [])
        
        all_issues = L2_issues + deep_issues
        
        processed_docs = set()
        fixed_count = 0
        
        for issue in all_issues:
            doc = issue["doc"]
            
            if doc in processed_docs:
                continue
            processed_docs.add(doc)
            
            doc_path = self.project_root / doc
            
            if not doc_path.exists():
                print(f"  跳过: 文档不存在 - {doc}")
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_name = doc_path.stem
                new_responsibility = self.enhance_core_responsibility(doc_name)
                
                pattern = r'(>\s*\*\*核心职责\*\*:\s*)([^\n]+)'
                match = re.search(pattern, content)
                
                if match:
                    old_resp = match.group(2)
                    content = re.sub(pattern, f'\\1{new_responsibility}', content)
                    
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    self.fix_log["details"].append({
                        "doc": doc,
                        "old": old_resp,
                        "new": new_responsibility
                    })
                    print(f"  ✓ 修复: {doc}")
                    
            except Exception as e:
                print(f"  ✗ 错误: {doc} - {str(e)}")
        
        self.fix_log["fixed"] = fixed_count
        print(f"\n核心职责修复完成: {fixed_count}/{len(processed_docs)}")
        
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"layer4_core_responsibility_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        print(f"\n修复日志已保存至: {log_path}")
        
    def run(self):
        """执行修复"""
        print("="*80)
        print("Layer 4核心职责修复")
        print("="*80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-"*80)
        
        self.load_audit_data()
        
        self.fix_core_responsibility()
        
        self.save_fix_log()
        
        print("\n" + "="*80)
        print("修复完成统计")
        print("="*80)
        print(f"核心职责修复: {self.fix_log['fixed']} 个")
        print("="*80)

if __name__ == "__main__":
    fixer = Layer4CoreResponsibilityFixer()
    fixer.run()
