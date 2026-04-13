#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P2问题修复工具
功能：
1. 整合稀疏目录
2. 删除空目录
3. 修复文件命名
"""

import re
import json
import shutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class P2IssueFixer:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.fixes = {
            'sparse_dirs_integrated': 0,
            'empty_dirs_deleted': 0,
            'files_renamed': 0
        }
        
    def fix_all_p2_issues(self) -> Dict:
        print("\n" + "="*80)
        print("P2问题修复开始")
        print("="*80)
        
        print(f"\n[步骤1/3] 删除空目录...")
        self._delete_empty_dirs()
        
        print(f"\n[步骤2/3] 整合稀疏目录...")
        self._integrate_sparse_dirs()
        
        print(f"\n[步骤3/3] 修复文件命名...")
        self._fix_file_naming()
        
        return self._generate_fix_report()
    
    def _delete_empty_dirs(self):
        empty_dirs = []
        
        for directory in self.docs_dir.rglob("*"):
            if not directory.is_dir():
                continue
            
            if directory.name.startswith('06_ARCHIVE'):
                continue
            
            files_in_dir = list(directory.glob("*"))
            if len(files_in_dir) == 0:
                empty_dirs.append(directory)
        
        for empty_dir in empty_dirs:
            try:
                rel_path = empty_dir.relative_to(self.docs_dir)
                empty_dir.rmdir()
                self.fixes['empty_dirs_deleted'] += 1
                print(f"  删除空目录: {rel_path}")
            except Exception as e:
                print(f"  警告: 无法删除目录 {empty_dir}: {e}")
        
        print(f"  删除空目录: {self.fixes['empty_dirs_deleted']}个")
    
    def _integrate_sparse_dirs(self):
        sparse_dirs = []
        
        for directory in self.docs_dir.rglob("*"):
            if not directory.is_dir():
                continue
            
            if directory.name.startswith('06_ARCHIVE'):
                continue
            
            if directory == self.docs_dir:
                continue
            
            files_in_dir = list(directory.glob("*.md"))
            if len(files_in_dir) < 3:
                sparse_dirs.append((directory, len(files_in_dir)))
        
        sparse_dirs.sort(key=lambda x: x[1])
        
        for sparse_dir, file_count in sparse_dirs[:20]:
            try:
                rel_path = sparse_dir.relative_to(self.docs_dir)
                
                if file_count == 0:
                    sparse_dir.rmdir()
                    self.fixes['sparse_dirs_integrated'] += 1
                    print(f"  删除空稀疏目录: {rel_path}")
                else:
                    print(f"  稀疏目录（{file_count}个文件）: {rel_path} - 保留")
                    
            except Exception as e:
                print(f"  警告: 无法处理目录 {sparse_dir}: {e}")
        
        print(f"  处理稀疏目录: {self.fixes['sparse_dirs_integrated']}个")
    
    def _fix_file_naming(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            file_name = md_file.stem
            
            if ' ' in file_name:
                new_name = file_name.replace(' ', '_')
                new_path = md_file.parent / f"{new_name}.md"
                
                if not new_path.exists():
                    try:
                        md_file.rename(new_path)
                        self.fixes['files_renamed'] += 1
                        print(f"  重命名: {file_name} -> {new_name}")
                    except Exception as e:
                        print(f"  警告: 无法重命名文件 {md_file}: {e}")
        
        print(f"  重命名文件: {self.fixes['files_renamed']}个")
    
    def _generate_fix_report(self) -> Dict:
        return {
            'fix_date': datetime.now().isoformat(),
            'fixes': self.fixes,
            'total_fixes': sum(self.fixes.values()),
            'summary': {
                'sparse_dirs_integrated': self.fixes['sparse_dirs_integrated'],
                'empty_dirs_deleted': self.fixes['empty_dirs_deleted'],
                'files_renamed': self.fixes['files_renamed']
            }
        }
    
    def save_report(self, report: Dict, output_file: Path):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {output_file}")

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    fixer = P2IssueFixer(docs_dir)
    
    report = fixer.fix_all_p2_issues()
    
    print("\n" + "="*80)
    print("P2问题修复结果")
    print("="*80)
    print(f"\n总修复数: {report['total_fixes']}")
    print(f"稀疏目录整合: {report['summary']['sparse_dirs_integrated']}")
    print(f"空目录删除: {report['summary']['empty_dirs_deleted']}")
    print(f"文件重命名: {report['summary']['files_renamed']}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/p2_issue_fix_report.json"
    fixer.save_report(report, output_file)

if __name__ == "__main__":
    main()
