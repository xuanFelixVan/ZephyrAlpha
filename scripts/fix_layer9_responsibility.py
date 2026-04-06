#!/usr/bin/env python3
"""
修复Layer 9文档治理相关文档的responsibility字段
问题：多个文档治理相关文档的responsibility字段不正确
"""
import os
import re
from pathlib import Path
from typing import Dict, List

class ResponsibilityFixer:
    """responsibility字段修复器"""
    
    def __init__(self, layer_path: str):
        self.layer_path = Path(layer_path)
        self.fixes = {
            'LAYER9_DOCUMENT_GOVERNANCE_AUDIT_REPORT.md': ['文档审计'],
            'LAYER9_DOCUMENT_GOVERNANCE_FIX_REPORT.md': ['文档修复'],
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_PLAN.md': ['文档维护'],
            'LAYER9_DOCUMENT_GOVERNANCE_MAINTENANCE_SUMMARY.md': ['文档维护总结'],
            'LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_REPORT.md': ['文档深度审计'],
            'LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_SUMMARY.md': ['文档深度审计总结'],
            'LAYER9_WEEKLY_MAINTENANCE_REPORT_20260407.md': ['文档周维护']
        }
        self.fixed_count = 0
        self.failed_count = 0
    
    def fix_all(self):
        """修复所有文档"""
        print("=" * 80)
        print("Layer 9文档治理responsibility字段修复")
        print("=" * 80)
        print(f"修复时间: {self._get_current_time()}")
        print(f"修复路径: {self.layer_path}")
        print()
        
        for filename, correct_responsibility in self.fixes.items():
            self.fix_file(filename, correct_responsibility)
        
        print()
        print("=" * 80)
        print("修复结果汇总")
        print("=" * 80)
        print(f"修复文档数: {self.fixed_count}")
        print(f"失败文档数: {self.failed_count}")
        print()
    
    def fix_file(self, filename: str, correct_responsibility: List[str]):
        """修复单个文档"""
        file_path = self.layer_path / filename
        
        if not file_path.exists():
            print(f"⚠️ 文件不存在: {filename}")
            self.failed_count += 1
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 提取YAML头部
            yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            
            if not yaml_match:
                print(f"⚠️ 未找到YAML头部: {filename}")
                self.failed_count += 1
                return
            
            yaml_content = yaml_match.group(1)
            
            # 替换responsibility字段
            new_yaml = self._replace_responsibility(yaml_content, correct_responsibility)
            
            if new_yaml == yaml_content:
                print(f"ℹ️ 无需修复: {filename}")
                return
            
            # 替换整个YAML头部
            new_content = content.replace(yaml_content, new_yaml, 1)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已修复: {filename}")
            print(f"   旧responsibility: {self._extract_responsibility(yaml_content)}")
            print(f"   新responsibility: {correct_responsibility}")
            self.fixed_count += 1
            
        except Exception as e:
            print(f"❌ 修复失败: {filename}")
            print(f"   错误: {str(e)}")
            self.failed_count += 1
    
    def _replace_responsibility(self, yaml_content: str, correct_responsibility: List[str]) -> str:
        """替换responsibility字段"""
        # 查找responsibility字段
        responsibility_pattern = r'responsibility:\s*\n(\s+-\s+.+\n)+'
        
        # 构建新的responsibility字段
        new_responsibility_lines = ['responsibility:']
        for item in correct_responsibility:
            new_responsibility_lines.append(f'  - {item}')
        new_responsibility = '\n'.join(new_responsibility_lines) + '\n'
        
        # 替换
        if re.search(responsibility_pattern, yaml_content):
            new_yaml = re.sub(responsibility_pattern, new_responsibility, yaml_content)
        else:
            # 如果没有responsibility字段，添加到YAML头部末尾
            new_yaml = yaml_content.rstrip() + '\n' + new_responsibility
        
        return new_yaml
    
    def _extract_responsibility(self, yaml_content: str) -> List[str]:
        """提取当前的responsibility字段"""
        responsibility_match = re.search(r'responsibility:\s*\n(\s+-\s+.+\n)+', yaml_content)
        
        if not responsibility_match:
            return []
        
        responsibility_text = responsibility_match.group(0)
        items = re.findall(r'-\s+(.+)', responsibility_text)
        
        return items
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    import sys
    
    layer_path = 'docs/09_RESEARCH_INNOVATION'
    
    if len(sys.argv) > 1:
        layer_path = sys.argv[1]
    
    fixer = ResponsibilityFixer(layer_path)
    fixer.fix_all()
