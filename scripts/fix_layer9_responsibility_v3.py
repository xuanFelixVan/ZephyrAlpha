#!/usr/bin/env python3
"""
Layer 9文档治理responsibility字段修复脚本 v3
功能：修复被错误修改的responsibility字段
"""
import os
import re
from pathlib import Path
from datetime import datetime

class Layer9ResponsibilityFixerV3:
    """Layer 9文档治理responsibility字段修复器 v3"""
    
    def __init__(self):
        self.layer_path = Path("docs/09_RESEARCH_INNOVATION")
        self.fix_count = 0
        self.fix_log = []
        
        # 正确的responsibility映射
        self.responsibility_mapping = {
            'LAYER9_DOCUMENT_GOVERNANCE_AUDIT_REPORT.md': '文档审计',
            'LAYER9_DOCUMENT_GOVERNANCE_FIX_REPORT.md': '文档修复',
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_PLAN.md': '文档维护',
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_SUMMARY.md': '文档维护总结',
            'LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT.md': '文档深度审计',
            'LAYER9_DOCUMENT_GOVERNANCE_CRITICAL_ISSUES_REPORT.md': '文档严重问题',
            'LAYER9_WEEKLY_MAINTENANCE_REPORT_20260407.md': '文档周维护',
        }
    
    def fix_all(self):
        """修复所有文档"""
        print("=" * 80)
        print("Layer 9文档治理responsibility字段修复 v3")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修复路径: {self.layer_path}")
        print()
        
        # 修复每个文档
        for filename, correct_responsibility in self.responsibility_mapping.items():
            file_path = self.layer_path / filename
            if file_path.exists():
                self.fix_document(file_path, correct_responsibility)
        
        # 输出修复结果
        print()
        print("=" * 80)
        print("修复结果汇总")
        print("=" * 80)
        print(f"修复文档数: {self.fix_count}")
        print()
        
        # 保存修复日志
        self.save_fix_log()
    
    def fix_document(self, file_path: Path, correct_responsibility: str):
        """修复单个文档"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否需要修复
        if '扩展功能、辅助模块' in content:
            # 替换responsibility字段
            old_pattern = r'responsibility:\s*\n\s*-\s*扩展功能、辅助模块'
            new_text = f'responsibility:\n  - {correct_responsibility}'
            
            new_content = re.sub(old_pattern, new_text, content)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fix_count += 1
            self.fix_log.append({
                'file': str(file_path),
                'old': '扩展功能、辅助模块',
                'new': correct_responsibility,
                'time': datetime.now().isoformat()
            })
            
            print(f"✅ 已修复: {file_path.name}")
            print(f"   旧responsibility: 扩展功能、辅助模块")
            print(f"   新responsibility: {correct_responsibility}")
        else:
            print(f"⏭️  跳过: {file_path.name} (无需修复)")
    
    def save_fix_log(self):
        """保存修复日志"""
        import json
        
        log_path = Path("docs/09_AUDIT/STATE/layer9_responsibility_fix_v3_log.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'fix_time': datetime.now().isoformat(),
                'fix_count': self.fix_count,
                'fix_log': self.fix_log
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 修复日志已保存: {log_path}")

if __name__ == "__main__":
    fixer = Layer9ResponsibilityFixerV3()
    fixer.fix_all()
