#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM清理和YAML修复工具
修复BOM字符导致的YAML格式问题
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict

class BOMAndYAMLFixer:
    def __init__(self, root_dir: str = "D:/ZephyrAlpha"):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        
        self.fix_stats = {
            "bom_removed": 0,
            "yaml_fixed": 0,
            "yaml_added": 0
        }
        
    def fix_all_issues(self):
        print("\n" + "="*80)
        print("BOM清理和YAML修复")
        print("="*80)
        
        print(f"\n[步骤1/3] 清理BOM字符...")
        self._remove_bom()
        
        print(f"\n[步骤2/3] 修复YAML格式...")
        self._fix_yaml_format()
        
        print(f"\n[步骤3/3] 添加缺失的YAML...")
        self._add_missing_yaml()
        
        return self._generate_fix_report()
        
    def _remove_bom(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        fixed_count = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8-sig')
                
                if content.startswith('\ufeff'):
                    content = content[1:]
                    md_file.write_text(content, encoding='utf-8')
                    fixed_count += 1
                elif md_file.read_bytes().startswith(b'\xef\xbb\xbf'):
                    content = md_file.read_text(encoding='utf-8-sig')
                    md_file.write_text(content, encoding='utf-8')
                    fixed_count += 1
                    
            except Exception as e:
                pass
                
        self.fix_stats["bom_removed"] = fixed_count
        print(f"    ✅ 清理BOM字符: {fixed_count}个")
        
    def _fix_yaml_format(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        fixed_count = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        
                        lines = yaml_content.strip().split('\n')
                        fixed_lines = []
                        
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                fixed_lines.append(line)
                        
                        if len(fixed_lines) != len(lines):
                            new_yaml = '\n'.join(fixed_lines)
                            new_content = f"---\n{new_yaml}\n---{content[yaml_end+3:]}"
                            md_file.write_text(new_content, encoding='utf-8')
                            fixed_count += 1
                            
            except Exception as e:
                pass
                
        self.fix_stats["yaml_fixed"] = fixed_count
        print(f"    ✅ 修复YAML格式: {fixed_count}个")
        
    def _add_missing_yaml(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        fixed_count = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                if not content.startswith('---'):
                    relative_path = md_file.relative_to(self.docs_dir)
                    parts = list(relative_path.parts)
                    
                    if len(parts) >= 2:
                        module_id = '_'.join(parts[:-1]).upper()
                    else:
                        module_id = md_file.stem.upper()
                    
                    module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
                    module_id = re.sub(r'_+', '_', module_id).strip('_')
                    
                    if not module_id:
                        module_id = "UNKNOWN"
                    
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    yaml_header = f"""---
module_id: {module_id}_001
version: 1.0.0
status: Active
created_date: {today}
last_updated: {today}
owner: 文档管理团队
responsibility:
  - 提供文档支持
---

"""
                    
                    new_content = yaml_header + content
                    md_file.write_text(new_content, encoding='utf-8')
                    fixed_count += 1
                    
            except Exception as e:
                pass
                
        self.fix_stats["yaml_added"] = fixed_count
        print(f"    ✅ 添加YAML头部: {fixed_count}个")
        
    def _generate_fix_report(self) -> Dict:
        print("\n" + "="*80)
        print("修复完成")
        print("="*80)
        print(f"\n📊 修复统计:")
        print(f"  - BOM字符清理: {self.fix_stats['bom_removed']}个")
        print(f"  - YAML格式修复: {self.fix_stats['yaml_fixed']}个")
        print(f"  - YAML头部添加: {self.fix_stats['yaml_added']}个")
        print(f"\n  总计: {sum(self.fix_stats.values())}个问题已修复")
        
        return self.fix_stats

if __name__ == "__main__":
    fixer = BOMAndYAMLFixer()
    fixer.fix_all_issues()
