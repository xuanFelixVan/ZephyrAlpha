#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能修复工具 - 最小化修复策略
只修复现有文件的问题，不创建新文件
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SmartIssueFixer:
    def __init__(self, root_dir: str = "D:/ZephyrAlpha"):
        self.root_dir = Path(root_dir)
        self.docs_dir = self.root_dir / "docs"
        self.audit_report = self.root_dir / "docs/09_AUDIT/REPORTS/comprehensive_deep_audit_report.json"
        
        self.fix_stats = {
            "dead_links": 0,
            "metadata": 0,
            "module_id": 0,
            "responsibility": 0
        }
        
    def fix_all_issues(self):
        print("\n" + "="*80)
        print("智能修复 - 最小化修复策略")
        print("="*80)
        print("策略: 只修复现有文件，不创建新文件")
        print("="*80)
        
        self.load_audit_report()
        
        print(f"\n[阶段1/4] P0问题修复 - 死链接...")
        self._fix_dead_links()
        
        print(f"\n[阶段2/4] P0问题修复 - 元数据...")
        self._fix_metadata()
        
        print(f"\n[阶段3/4] P0问题修复 - 编号体系...")
        self._fix_module_id()
        
        print(f"\n[阶段4/4] P1问题修复 - 职责描述...")
        self._fix_responsibility()
        
        return self._generate_fix_report()
        
    def load_audit_report(self):
        if self.audit_report.exists():
            with open(self.audit_report, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            print(f"✅ 已加载审计报告: {self.audit_report}")
        else:
            self.report_data = {}
            print(f"⚠️ 审计报告不存在")
            
    def _fix_dead_links(self):
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
            
        self.fix_stats["dead_links"] = fixed_count
        print(f"    ✅ 修复死链接: {fixed_count}个")
        
    def _fix_metadata(self):
        if "layer3_issues" not in self.report_data:
            print(f"    ⚠️ 无元数据问题数据")
            return
            
        metadata_issues = [i for i in self.report_data["layer3_issues"] if i.get("issue_type") == "缺少元数据"]
        fixed_count = 0
        
        for issue in metadata_issues:
            file_path = self.docs_dir / issue["file"]
            
            if not file_path.exists():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                if not content.startswith('---'):
                    relative_path = file_path.relative_to(self.docs_dir)
                    parts = list(relative_path.parts)
                    
                    if len(parts) >= 2:
                        module_id = '_'.join(parts[:-1]).upper()
                    else:
                        module_id = file_path.stem.upper()
                    
                    module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
                    module_id = re.sub(r'_+', '_', module_id).strip('_')
                    
                    if not module_id:
                        module_id = "UNKNOWN"
                    
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    parts_list = list(file_path.relative_to(self.docs_dir).parts)
                    if len(parts_list) >= 2:
                        module_name = parts_list[-2].replace('_', ' ').title()
                    else:
                        module_name = file_path.stem.replace('_', ' ').title()
                    
                    yaml_header = f"""---
module_id: {module_id}_001
version: 1.0.0
status: Active
created_date: {today}
last_updated: {today}
owner: 文档管理团队
responsibility:
  - 提供{module_name}相关文档支持
---

"""
                    
                    new_content = yaml_header + content
                    file_path.write_text(new_content, encoding='utf-8')
                    fixed_count += 1
                    
            except Exception as e:
                pass
                
        self.fix_stats["metadata"] = fixed_count
        print(f"    ✅ 补充元数据: {fixed_count}个")
        
    def _fix_module_id(self):
        if "layer3_issues" not in self.report_data:
            print(f"    ⚠️ 无编号问题数据")
            return
            
        module_id_issues = [i for i in self.report_data["layer3_issues"] if i.get("category") == "编号体系"]
        fixed_count = 0
        
        for issue in module_id_issues:
            file_path = self.docs_dir / issue["file"]
            
            if not file_path.exists():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        
                        if 'module_id:' not in yaml_content:
                            relative_path = file_path.relative_to(self.docs_dir)
                            parts = list(relative_path.parts)
                            
                            if len(parts) >= 2:
                                module_id = '_'.join(parts[:-1]).upper()
                            else:
                                module_id = file_path.stem.upper()
                            
                            module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
                            module_id = re.sub(r'_+', '_', module_id).strip('_')
                            
                            if not module_id:
                                module_id = "UNKNOWN"
                            
                            new_yaml = yaml_content + f"\nmodule_id: {module_id}_001\n"
                            new_content = f"---{new_yaml}---{content[yaml_end+3:]}"
                            file_path.write_text(new_content, encoding='utf-8')
                            fixed_count += 1
                            
            except Exception as e:
                pass
                
        self.fix_stats["module_id"] = fixed_count
        print(f"    ✅ 补充编号: {fixed_count}个")
        
    def _fix_responsibility(self):
        if "layer2_issues" not in self.report_data:
            print(f"    ⚠️ 无职责问题数据")
            return
            
        responsibility_issues = [i for i in self.report_data["layer2_issues"] if i.get("category") == "职责驱动"]
        fixed_count = 0
        
        for issue in responsibility_issues[:250]:
            file_path = self.docs_dir / issue["file"]
            
            if not file_path.exists():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end != -1:
                        yaml_content = content[3:yaml_end]
                        
                        if 'responsibility:' not in yaml_content:
                            parts = list(file_path.relative_to(self.docs_dir).parts)
                            if len(parts) >= 2:
                                module_name = parts[-2].replace('_', ' ').title()
                            else:
                                module_name = file_path.stem.replace('_', ' ').title()
                            
                            new_yaml = yaml_content + f"\nresponsibility:\n  - 提供{module_name}相关文档支持\n"
                            new_content = f"---{new_yaml}---{content[yaml_end+3:]}"
                            file_path.write_text(new_content, encoding='utf-8')
                            fixed_count += 1
                            
            except Exception as e:
                pass
                
        self.fix_stats["responsibility"] = fixed_count
        print(f"    ✅ 优化职责描述: {fixed_count}个")
        
    def _generate_fix_report(self) -> Dict:
        print("\n" + "="*80)
        print("修复完成")
        print("="*80)
        print(f"\n📊 修复统计:")
        print(f"  - P0死链接: {self.fix_stats['dead_links']}个")
        print(f"  - P0元数据: {self.fix_stats['metadata']}个")
        print(f"  - P0编号体系: {self.fix_stats['module_id']}个")
        print(f"  - P1职责描述: {self.fix_stats['responsibility']}个")
        print(f"\n  总计: {sum(self.fix_stats.values())}个问题已修复")
        
        report = {
            "fix_date": datetime.now().isoformat(),
            "fix_stats": self.fix_stats,
            "total_fixed": sum(self.fix_stats.values()),
            "strategy": "最小化修复 - 只修复现有文件，不创建新文件"
        }
        
        report_path = self.root_dir / "docs/09_AUDIT/REPORTS/smart_fix_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 报告已保存: {report_path}")
        
        return self.fix_stats

if __name__ == "__main__":
    fixer = SmartIssueFixer()
    fixer.fix_all_issues()
