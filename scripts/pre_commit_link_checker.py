#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Git Pre-commit Hook: 文档引用检查
在Git提交前自动检查文档链接有效性，防止新增无效链接
"""

import re
import sys
from pathlib import Path
from datetime import datetime

class PreCommitLinkChecker:
    def __init__(self):
        self.docs_root = Path('docs')
        self.errors = []
        self.warnings = []
        self.stats = {
            'files_checked': 0,
            'links_checked': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'skipped_links': 0
        }
    
    def build_file_index(self):
        """构建文件索引"""
        file_index = {}
        
        if not self.docs_root.exists():
            return file_index
        
        for md_file in self.docs_root.rglob('*.md'):
            rel_path = str(md_file.relative_to(self.docs_root)).replace('\\', '/')
            file_index[rel_path.lower()] = rel_path
            file_index[md_file.name.lower()] = rel_path
        
        return file_index
    
    def check_file_links(self, file_path, file_index):
        """检查单个文件的链接"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.warnings.append(f"无法读取文件 {file_path}: {e}")
            return
        
        self.stats['files_checked'] += 1
        
        # 匹配markdown链接
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2).strip()
            
            # 跳过非文件链接
            if link_url.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
                self.stats['skipped_links'] += 1
                continue
            
            self.stats['links_checked'] += 1
            
            # 检查链接是否存在
            if link_url.startswith('./') or link_url.startswith('../'):
                # 相对路径
                source_dir = file_path.parent.relative_to(self.docs_root)
                target_path = (Path(source_dir) / link_url).resolve()
                try:
                    target_rel = str(target_path.relative_to(self.docs_root)).replace('\\', '/')
                except ValueError:
                    target_rel = link_url
            else:
                target_rel = link_url
            
            # 检查文件是否存在
            target_file = self.docs_root / target_rel
            
            possible_paths = [
                target_file,
                self.docs_root / target_rel.lstrip('./'),
                self.docs_root / (target_rel + '.md'),
                self.docs_root / (target_rel.rstrip('/') + '.md'),
                self.docs_root / (target_rel + '/INDEX.md'),
                self.docs_root / (target_rel + '/index.md'),
            ]
            
            exists = any(p.exists() for p in possible_paths)
            
            if exists:
                self.stats['valid_links'] += 1
            else:
                self.stats['invalid_links'] += 1
                line_number = content[:match.start()].count('\n') + 1
                self.errors.append({
                    'file': str(file_path.relative_to(self.docs_root)).replace('\\', '/'),
                    'line': line_number,
                    'text': link_text,
                    'url': link_url
                })
    
    def check_staged_files(self):
        """检查Git暂存区的文件"""
        import subprocess
        
        # 获取暂存的markdown文件
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = [
                f for f in result.stdout.strip().split('\n')
                if f.endswith('.md') and f.startswith('docs/')
            ]
        except Exception as e:
            print(f"⚠️  无法获取暂存文件列表: {e}")
            return
        
        if not staged_files:
            print("✅ 没有暂存的Markdown文件需要检查")
            return
        
        print(f"🔍 检查 {len(staged_files)} 个暂存的Markdown文件...")
        
        # 构建文件索引
        file_index = self.build_file_index()
        
        # 检查每个文件
        for file_path_str in staged_files:
            file_path = Path(file_path_str)
            if file_path.exists():
                self.check_file_links(file_path, file_index)
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "=" * 60)
        print("📊 文档引用检查报告")
        print("=" * 60)
        
        print(f"\n检查统计:")
        print(f"  - 检查文件数: {self.stats['files_checked']}")
        print(f"  - 检查链接数: {self.stats['links_checked']}")
        print(f"  - 有效链接数: {self.stats['valid_links']}")
        print(f"  - 无效链接数: {self.stats['invalid_links']}")
        print(f"  - 跳过链接数: {self.stats['skipped_links']}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings[:5]:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个无效链接:")
            for error in self.errors[:10]:
                print(f"  - {error['file']}:{error['line']} - [{error['text']}]({error['url']})")
            
            if len(self.errors) > 10:
                print(f"  ... 还有 {len(self.errors) - 10} 个错误")
        
        print("=" * 60)
    
    def run(self):
        """运行检查"""
        print("🚀 Git Pre-commit Hook: 文档引用检查")
        print("=" * 60)
        
        self.check_staged_files()
        self.generate_report()
        
        # 如果有错误，阻止提交
        if self.errors:
            print("\n❌ 提交被阻止！请修复无效链接后再提交。")
            print("\n💡 提示:")
            print("  - 使用 'git commit --no-verify' 跳过此检查（不推荐）")
            print("  - 修复无效链接后重新提交")
            sys.exit(1)
        else:
            print("\n✅ 所有链接检查通过！")
            sys.exit(0)

if __name__ == '__main__':
    checker = PreCommitLinkChecker()
    checker.run()
