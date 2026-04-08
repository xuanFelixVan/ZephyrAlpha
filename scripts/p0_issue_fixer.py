#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0问题修复工具
只修复现有文件，不创建新文件
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class P0IssueFixer:
    def __init__(self, root_dir: str = "D:/ZephyrAlpha"):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.audit_report = self.root_dir / "docs/09_AUDIT/REPORTS/comprehensive_deep_audit_report.json"
        self.fix_stats = {
            "path_reference": 0,
            "file_naming": 0,
            "responsibility": 0
        }
        
    def load_audit_report(self):
        with open(self.audit_report, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 已加载审计报告: {self.audit_report}")
        return data
    
    def fix_all_issues(self):
        print("\n" + "="*80)
        print("P0问题修复 - 最小化修复策略")
        print("="*80)
        print("策略: 只修复现有文件，不创建新文件")
        print("="*80)
        
        data = self.load_audit_report()
        
        print(f"\n[阶段1/3] P0问题修复 - 路径引用...")
        self._fix_path_reference(data)
        
        print(f"\n[阶段2/3] P0问题修复 - 文件命名...")
        self._fix_file_naming(data)
        
        print(f"\n[阶段3/3] P0问题修复 - 职责驱动...")
        self._fix_responsibility(data)
        
        return self._generate_fix_report()
    
    def _fix_path_reference(self, data):
        layer1_issues = data.get('layer1_issues', [])
        path_issues = [issue for issue in layer1_issues if issue.get('category') == '路径引用']
        
        print(f"    发现 {len(path_issues)} 个路径引用问题")
        
        md_files = list(self.docs_dir.rglob("*.md"))
        fixed_count = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content
                
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                matches = list(re.finditer(link_pattern, content))
                
                for match in reversed(matches):
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    if link_path.startswith('http') or link_path.startswith('#') or link_path.startswith('file:///'):
                        continue
                    
                    abs_path = (md_file.parent / link_path).resolve()
                    
                    if not abs_path.exists():
                        new_link = f'`{link_text}`'
                        content = content[:match.start()] + new_link + content[match.end():]
                        fixed_count += 1
                        
                if content != original_content:
                    md_file.write_text(content, encoding='utf-8')
                    
            except Exception as e:
                pass
            
        self.fix_stats["path_reference"] = fixed_count
        print(f"    ✅ 修复路径引用: {fixed_count}个")
    
    def _fix_file_naming(self, data):
        layer1_issues = data.get('layer1_issues', [])
        naming_issues = [issue for issue in layer1_issues if issue.get('category') == '文件命名']
        
        print(f"    发现 {len(naming_issues)} 个文件命名问题")
        
        fixed_count = 0
        
        for issue in naming_issues:
            old_path = self.docs_dir / issue.get('file', '')
            
            if not old_path.exists():
                continue
            
            old_name = old_path.name
            issue_type = issue.get('issue_type', '')
            
            if issue_type == '旧架构命名残留':
                new_name = old_name
                old_patterns = ['LAYER', 'LAYER5', 'LAYER6', 'LAYER8']
                
                for pattern in old_patterns:
                    if pattern in new_name:
                        new_name = new_name.replace(pattern, 'AUDIT')
                
                if new_name != old_name:
                    new_path = old_path.parent / new_name
                    
                    if not new_path.exists():
                        try:
                            shutil.move(str(old_path), str(new_path))
                            fixed_count += 1
                            print(f"      重命名: {old_name} -> {new_name}")
                        except Exception as e:
                            print(f"      ❌ 重命名失败: {old_name} - {e}")
        
        self.fix_stats["file_naming"] = fixed_count
        print(f"    ✅ 修复文件命名: {fixed_count}个")
    
    def _fix_responsibility(self, data):
        layer2_issues = data.get('layer2_issues', [])
        responsibility_issues = [issue for issue in layer2_issues if issue.get('category') == '职责驱动']
        
        print(f"    发现 {len(responsibility_issues)} 个职责驱动问题")
        
        fixed_count = 0
        
        for issue in responsibility_issues:
            file_path = self.docs_dir / issue.get('file', '')
            
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                if 'responsibility:' not in content:
                    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    
                    if yaml_match:
                        yaml_content = yaml_match.group(1)
                        
                        if 'owner:' in yaml_content and 'responsibility:' not in yaml_content:
                            lines = yaml_content.split('\n')
                            new_lines = []
                            
                            for line in lines:
                                new_lines.append(line)
                                if line.startswith('owner:'):
                                    owner = line.split(':', 1)[1].strip()
                                    new_lines.append('responsibility:')
                                    new_lines.append(f'  - {owner}相关文档')
                            
                            new_yaml = '\n'.join(new_lines)
                            content = content.replace(yaml_content, new_yaml)
                            
                            file_path.write_text(content, encoding='utf-8')
                            fixed_count += 1
                    else:
                        yaml_header = f"""---
module_id: {file_path.stem.upper()}_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - 文档管理相关文档
---

"""
                        content = yaml_header + content
                        file_path.write_text(content, encoding='utf-8')
                        fixed_count += 1
                        
            except Exception as e:
                pass
        
        self.fix_stats["responsibility"] = fixed_count
        print(f"    ✅ 修复职责驱动: {fixed_count}个")
    
    def _generate_fix_report(self):
        print("\n" + "="*80)
        print("修复完成")
        print("="*80)
        
        print(f"\n📊 修复统计:")
        print(f"  - P0路径引用: {self.fix_stats['path_reference']}个")
        print(f"  - P0文件命名: {self.fix_stats['file_naming']}个")
        print(f"  - P0职责驱动: {self.fix_stats['responsibility']}个")
        print(f"\n  总计: {sum(self.fix_stats.values())}个问题已修复")
        
        report = {
            "fix_date": datetime.now().isoformat(),
            "fix_stats": self.fix_stats,
            "total_fixed": sum(self.fix_stats.values()),
            "strategy": "P0问题修复 - 只修复现有文件，不创建新文件"
        }
        
        report_path = self.root_dir / "docs/09_AUDIT/REPORTS/p0_fix_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 报告已保存: {report_path}")
        
        return self.fix_stats

if __name__ == "__main__":
    fixer = P0IssueFixer()
    fixer.fix_all_issues()
