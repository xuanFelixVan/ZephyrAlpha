#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0问题综合修复工具
功能：
1. 修复死链接
2. 添加元数据
3. 添加职责描述
4. 修复编号重复
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

class P0IssueFixer:
    def __init__(self, docs_dir: Path):
        self.docs_dir = Path(docs_dir)
        self.fixes = {
            'dead_links': 0,
            'metadata': 0,
            'responsibility': 0,
            'duplicate_ids': 0
        }
        self.module_id_counter = defaultdict(int)
        
    def fix_all_p0_issues(self) -> Dict:
        print("\n" + "="*80)
        print("P0问题综合修复开始")
        print("="*80)
        
        print(f"\n[步骤1/4] 修复死链接...")
        self._fix_dead_links()
        
        print(f"\n[步骤2/4] 添加元数据...")
        self._add_metadata()
        
        print(f"\n[步骤3/4] 添加职责描述...")
        self._add_responsibility()
        
        print(f"\n[步骤4/4] 修复编号重复...")
        self._fix_duplicate_ids()
        
        return self._generate_fix_report()
    
    def _fix_dead_links(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        total_fixed = 0
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                original_content = content
                
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_path in links:
                    if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                        continue
                    
                    if not link_path.startswith(('#', 'http', 'mailto')):
                        target_path = (md_file.parent / link_path).resolve()
                        if not target_path.exists():
                            content = content.replace(f'[{link_text}]({link_path})', f'{link_text}')
                            total_fixed += 1
                
                if content != original_content:
                    md_file.write_text(content, encoding='utf-8')
                    
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        self.fixes['dead_links'] = total_fixed
        print(f"  修复死链接: {total_fixed}个")
    
    def _add_metadata(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        total_fixed = 0
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                
                if not re.search(r'^---\s*\n.*?\n---', content, re.DOTALL):
                    title = self._extract_title(content)
                    module_id = self._generate_module_id(md_file)
                    
                    frontmatter = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档管理团队
responsibility:
  - {title}文档
---

"""
                    content = frontmatter + content
                    md_file.write_text(content, encoding='utf-8')
                    total_fixed += 1
                    
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        self.fixes['metadata'] = total_fixed
        print(f"  添加元数据: {total_fixed}个")
    
    def _add_responsibility(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        total_fixed = 0
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                
                if not re.search(r'responsibility:\s*\n\s+-\s+.+', content):
                    if re.search(r'^---\s*\n.*?\n---', content, re.DOTALL):
                        title = self._extract_title(content)
                        
                        content = re.sub(
                            r'(owner:\s*[^\n]+\n)',
                            r'\1responsibility:\n  - ' + title + '文档\n',
                            content
                        )
                        md_file.write_text(content, encoding='utf-8')
                        total_fixed += 1
                        
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        self.fixes['responsibility'] = total_fixed
        print(f"  添加职责描述: {total_fixed}个")
    
    def _fix_duplicate_ids(self):
        md_files = list(self.docs_dir.rglob("*.md"))
        module_ids = {}
        total_fixed = 0
        
        for md_file in md_files:
            if md_file.name.startswith('06_ARCHIVE'):
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                match = re.search(r'module_id:\s*(.+)', content)
                
                if match:
                    module_id = match.group(1).strip()
                    
                    if module_id in module_ids:
                        new_module_id = self._generate_module_id(md_file)
                        content = re.sub(
                            r'module_id:\s*' + re.escape(module_id),
                            f'module_id: {new_module_id}',
                            content
                        )
                        md_file.write_text(content, encoding='utf-8')
                        total_fixed += 1
                    else:
                        module_ids[module_id] = md_file
                        
            except Exception as e:
                print(f"  警告: 无法处理文件 {md_file}: {e}")
        
        self.fixes['duplicate_ids'] = total_fixed
        print(f"  修复编号重复: {total_fixed}个")
    
    def _extract_title(self, content: str) -> str:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "未命名文档"
    
    def _generate_module_id(self, md_file: Path) -> str:
        rel_path = md_file.relative_to(self.docs_dir)
        parts = list(rel_path.parts[:-1])
        
        if parts:
            prefix = '_'.join(parts[:2]).upper()
            prefix = re.sub(r'[^A-Z0-9_]', '_', prefix)
        else:
            prefix = 'DOC'
        
        file_name = md_file.stem.upper()
        file_name = re.sub(r'[^A-Z0-9_]', '_', file_name)
        
        module_id = f"{prefix}_{file_name}"
        
        self.module_id_counter[module_id] += 1
        if self.module_id_counter[module_id] > 1:
            module_id = f"{module_id}_{self.module_id_counter[module_id]}"
        
        return module_id
    
    def _generate_fix_report(self) -> Dict:
        return {
            'fix_date': datetime.now().isoformat(),
            'fixes': self.fixes,
            'total_fixes': sum(self.fixes.values()),
            'summary': {
                'dead_links_fixed': self.fixes['dead_links'],
                'metadata_added': self.fixes['metadata'],
                'responsibility_added': self.fixes['responsibility'],
                'duplicate_ids_fixed': self.fixes['duplicate_ids']
            }
        }
    
    def save_report(self, report: Dict, output_file: Path):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {output_file}")

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    fixer = P0IssueFixer(docs_dir)
    
    report = fixer.fix_all_p0_issues()
    
    print("\n" + "="*80)
    print("P0问题修复结果")
    print("="*80)
    print(f"\n总修复数: {report['total_fixes']}")
    print(f"死链接修复: {report['summary']['dead_links_fixed']}")
    print(f"元数据添加: {report['summary']['metadata_added']}")
    print(f"职责描述添加: {report['summary']['responsibility_added']}")
    print(f"编号重复修复: {report['summary']['duplicate_ids_fixed']}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/p0_issue_fix_report.json"
    fixer.save_report(report, output_file)

if __name__ == "__main__":
    main()
