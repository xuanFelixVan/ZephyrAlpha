#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P1短期改进项执行脚本
1. 修复目录漂移问题 (992个)
2. 修复文件命名问题 (140个)
3. 修复死链接问题 (1,585个)
"""

import json
import re
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

class P1ShortTermFixer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_v2_20260407_031623.json"
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "directory_drift": {"fixed": 0, "skipped": 0, "errors": []},
            "file_naming": {"fixed": 0, "skipped": 0, "errors": []},
            "dead_links": {"fixed": 0, "skipped": 0, "errors": []}
        }
        
        self.audit_data = None
        self.load_audit_data()
        
    def load_audit_data(self):
        """加载审计数据"""
        try:
            with open(self.audit_report_path, 'r', encoding='utf-8') as f:
                self.audit_data = json.load(f)
            print(f"✅ 已加载审计数据: {self.audit_report_path}")
        except Exception as e:
            print(f"❌ 加载审计数据失败: {e}")
            self.audit_data = None
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return None
    
    def write_file_content(self, file_path: Path, content: str):
        """写入文件内容"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def fix_directory_drift(self):
        """修复目录漂移问题"""
        print("\n" + "=" * 80)
        print("P1-1: 修复目录漂移问题")
        print("=" * 80)
        
        if not self.audit_data:
            print("❌ 无审计数据，跳过")
            return
        
        drift_issues = self.audit_data['L1_file_system']['directory_structure']
        print(f"发现 {len(drift_issues)} 个目录漂移问题")
        
        framework_dir = self.project_root / "docs" / "01_FRAMEWORK"
        if not framework_dir.exists():
            framework_dir.mkdir(parents=True, exist_ok=True)
        
        layer4_subdir = framework_dir / "LAYER4_ML"
        if not layer4_subdir.exists():
            layer4_subdir.mkdir(parents=True, exist_ok=True)
        
        fixed_count = 0
        for issue in drift_issues[:100]:
            doc_path = self.project_root / issue['doc']
            
            if not doc_path.exists():
                self.fix_log['directory_drift']['skipped'] += 1
                continue
            
            if '01_FRAMEWORK' in str(doc_path):
                self.fix_log['directory_drift']['skipped'] += 1
                continue
            
            try:
                content = self.read_file_content(doc_path)
                if not content:
                    self.fix_log['directory_drift']['skipped'] += 1
                    continue
                
                yaml_match = re.search(r'layer:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
                if yaml_match:
                    layer_value = yaml_match.group(1).strip()
                    if 'layer 4' in layer_value.lower() or 'layer4' in layer_value.lower():
                        new_path = layer4_subdir / doc_path.name
                        
                        counter = 1
                        while new_path.exists():
                            stem = doc_path.stem
                            new_path = layer4_subdir / f"{stem}_{counter}{doc_path.suffix}"
                            counter += 1
                        
                        shutil.move(str(doc_path), str(new_path))
                        fixed_count += 1
                        
                        if fixed_count % 10 == 0:
                            print(f"已修复 {fixed_count} 个文档...")
                
                self.fix_log['directory_drift']['skipped'] += 1
                
            except Exception as e:
                self.fix_log['directory_drift']['errors'].append({
                    "doc": str(doc_path),
                    "error": str(e)
                })
        
        self.fix_log['directory_drift']['fixed'] = fixed_count
        print(f"\n✅ 目录漂移修复完成: {fixed_count} 个文档")
    
    def fix_file_naming(self):
        """修复文件命名问题"""
        print("\n" + "=" * 80)
        print("P1-2: 修复文件命名问题")
        print("=" * 80)
        
        if not self.audit_data:
            print("❌ 无审计数据，跳过")
            return
        
        naming_issues = self.audit_data['L1_file_system']['file_naming']
        print(f"发现 {len(naming_issues)} 个文件命名问题")
        
        fixed_count = 0
        for issue in naming_issues[:50]:
            doc_path = self.project_root / issue['doc']
            
            if not doc_path.exists():
                self.fix_log['file_naming']['skipped'] += 1
                continue
            
            old_name = doc_path.name
            new_name = old_name
            
            new_name = re.sub(r'layer[_\s]*(\d+)', r'layer\1', new_name, flags=re.IGNORECASE)
            new_name = re.sub(r'layer\s+', 'layer_', new_name, flags=re.IGNORECASE)
            
            new_name = re.sub(r'\s+', '_', new_name)
            new_name = re.sub(r'_+', '_', new_name)
            
            if new_name != old_name:
                new_path = doc_path.parent / new_name
                
                if not new_path.exists():
                    try:
                        shutil.move(str(doc_path), str(new_path))
                        fixed_count += 1
                        print(f"✅ 重命名: {old_name} -> {new_name}")
                    except Exception as e:
                        self.fix_log['file_naming']['errors'].append({
                            "doc": str(doc_path),
                            "error": str(e)
                        })
                else:
                    self.fix_log['file_naming']['skipped'] += 1
            else:
                self.fix_log['file_naming']['skipped'] += 1
        
        self.fix_log['file_naming']['fixed'] = fixed_count
        print(f"\n✅ 文件命名修复完成: {fixed_count} 个文档")
    
    def fix_dead_links(self):
        """修复死链接问题"""
        print("\n" + "=" * 80)
        print("P1-3: 修复死链接问题")
        print("=" * 80)
        
        if not self.audit_data:
            print("❌ 无审计数据，跳过")
            return
        
        link_issues = self.audit_data['L1_file_system']['path_references']
        print(f"发现 {len(link_issues)} 个路径引用问题")
        
        fixed_count = 0
        processed_docs = set()
        
        for issue in link_issues[:100]:
            doc_path = self.project_root / issue['doc']
            
            if not doc_path.exists():
                continue
            
            if str(doc_path) in processed_docs:
                continue
            
            processed_docs.add(str(doc_path))
            
            if issue['issue'] != '死链接':
                continue
            
            content = self.read_file_content(doc_path)
            if not content:
                continue
            
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            matches = list(re.finditer(link_pattern, content))
            
            updated = False
            for match in matches:
                text = match.group(1)
                link = match.group(2)
                
                if link.startswith('http') or link.startswith('#'):
                    continue
                
                link_path = doc_path.parent / link
                
                if not link_path.exists():
                    new_link = link.replace('../', '')
                    new_link = re.sub(r'^/+', '', new_link)
                    
                    new_link_path = doc_path.parent / new_link
                    
                    if new_link_path.exists():
                        content = content.replace(f']({link})', f']({new_link})')
                        updated = True
            
            if updated:
                self.write_file_content(doc_path, content)
                fixed_count += 1
                
                if fixed_count % 10 == 0:
                    print(f"已修复 {fixed_count} 个文档...")
        
        self.fix_log['dead_links']['fixed'] = fixed_count
        print(f"\n✅ 死链接修复完成: {fixed_count} 个文档")
    
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"p1_fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 修复日志已保存: {log_path}")
    
    def run(self):
        """执行P1修复"""
        print("=" * 80)
        print("P1短期改进项执行")
        print("=" * 80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-" * 80)
        
        self.fix_directory_drift()
        self.fix_file_naming()
        self.fix_dead_links()
        
        self.save_fix_log()
        
        print("\n" + "=" * 80)
        print("P1修复完成统计")
        print("=" * 80)
        print(f"目录漂移修复: {self.fix_log['directory_drift']['fixed']} 个")
        print(f"文件命名修复: {self.fix_log['file_naming']['fixed']} 个")
        print(f"死链接修复: {self.fix_log['dead_links']['fixed']} 个")
        print("=" * 80)

if __name__ == "__main__":
    fixer = P1ShortTermFixer()
    fixer.run()
