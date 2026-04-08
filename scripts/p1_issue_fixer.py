#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P1问题修复工具
功能：
1. 处理重复文档
2. 处理职责重叠
"""

import re
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

class P1IssueFixer:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.archive_dir = self.docs_dir / "06_ARCHIVE"
        self.archive_dir.mkdir(exist_ok=True)
        self.fixes = {
            'duplicates_archived': 0,
            'responsibility_merged': 0
        }
        
    def fix_all_p1_issues(self) -> Dict:
        print("\n" + "="*80)
        print("P1问题修复开始")
        print("="*80)
        
        print(f"\n[步骤1/2] 处理重复文档...")
        self._handle_duplicates()
        
        print(f"\n[步骤2/2] 处理职责重叠...")
        self._handle_responsibility_overlap()
        
        return self._generate_fix_report()
    
    def _handle_duplicates(self):
        content_hashes = defaultdict(list)
        md_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                content_hash = hashlib.md5(content.encode()).hexdigest()
                content_hashes[content_hash].append(md_file)
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        duplicates_found = 0
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                duplicates_found += 1
                
                files_with_dates = []
                for f in files:
                    stat = f.stat()
                    files_with_dates.append((f, stat.st_mtime))
                
                files_with_dates.sort(key=lambda x: x[1], reverse=True)
                keep_file = files_with_dates[0][0]
                archive_files = [f for f, _ in files_with_dates[1:]]
                
                for archive_file in archive_files:
                    try:
                        rel_path = archive_file.relative_to(self.docs_dir)
                        archive_path = self.archive_dir / f"duplicate_{archive_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        shutil.move(str(archive_file), str(archive_path))
                        self.fixes['duplicates_archived'] += 1
                        print(f"  归档重复文档: {rel_path}")
                    except Exception as e:
                        print(f"  警告: 无法归档文件 {archive_file}: {e}")
        
        print(f"  发现重复组: {duplicates_found}组")
        print(f"  归档重复文档: {self.fixes['duplicates_archived']}个")
    
    def _handle_responsibility_overlap(self):
        responsibilities = defaultdict(list)
        md_files = list(self.docs_dir.rglob("*.md"))
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                match = re.search(r'responsibility:\s*\n\s+-\s*(.+)', content)
                
                if match:
                    responsibility = match.group(1).strip()
                    responsibilities[responsibility].append(md_file)
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        overlaps_found = 0
        for responsibility, files in responsibilities.items():
            if len(files) > 1:
                overlaps_found += 1
                
                files_with_sizes = []
                for f in files:
                    stat = f.stat()
                    files_with_sizes.append((f, stat.st_size))
                
                files_with_sizes.sort(key=lambda x: x[1], reverse=True)
                keep_file = files_with_sizes[0][0]
                merge_files = [f for f, _ in files_with_sizes[1:]]
                
                for merge_file in merge_files:
                    try:
                        rel_path = merge_file.relative_to(self.docs_dir)
                        archive_path = self.archive_dir / f"overlap_{merge_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        shutil.move(str(merge_file), str(archive_path))
                        self.fixes['responsibility_merged'] += 1
                        print(f"  归档职责重叠文档: {rel_path}")
                    except Exception as e:
                        print(f"  警告: 无法归档文件 {merge_file}: {e}")
        
        print(f"  发现职责重叠组: {overlaps_found}组")
        print(f"  归档重叠文档: {self.fixes['responsibility_merged']}个")
    
    def _generate_fix_report(self) -> Dict:
        return {
            'fix_date': datetime.now().isoformat(),
            'fixes': self.fixes,
            'total_fixes': sum(self.fixes.values()),
            'summary': {
                'duplicates_archived': self.fixes['duplicates_archived'],
                'responsibility_merged': self.fixes['responsibility_merged']
            }
        }
    
    def save_report(self, report: Dict, output_file: Path):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {output_file}")

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    fixer = P1IssueFixer(docs_dir)
    
    report = fixer.fix_all_p1_issues()
    
    print("\n" + "="*80)
    print("P1问题修复结果")
    print("="*80)
    print(f"\n总修复数: {report['total_fixes']}")
    print(f"重复文档归档: {report['summary']['duplicates_archived']}")
    print(f"职责重叠归档: {report['summary']['responsibility_merged']}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/p1_issue_fix_report.json"
    fixer.save_report(report, output_file)

if __name__ == "__main__":
    main()
