#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
全系统无效链接修复脚本
系统性修复所有无效链接
"""

import re
import os
from pathlib import Path
from datetime import datetime
import json

class ComprehensiveLinkFixer:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.stats = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'fixed_links': 0,
            'skipped_links': 0,
            'files_processed': 0,
            'details': []
        }
        self.known_files = self._build_file_index()
    
    def _build_file_index(self):
        """构建所有markdown文件的索引"""
        files = {}
        for md_file in self.docs_root.rglob('*.md'):
            rel_path = md_file.relative_to(self.docs_root)
            files[str(rel_path).replace('\\', '/').lower()] = str(rel_path)
            files[md_file.name.lower()] = str(rel_path)
        return files
    
    def _resolve_link(self, link_url, source_file):
        """尝试解析链接到正确的文件路径"""
        source_dir = Path(source_file).parent
        
        # 尝试多种路径解析方式
        candidates = [
            source_dir / link_url,
            self.docs_root / link_url,
            Path(link_url.lstrip('./')),
            source_dir / link_url.lstrip('./'),
        ]
        
        for candidate in candidates:
            # 尝试直接匹配
            if candidate.exists() and str(candidate).startswith(str(self.docs_root)):
                try:
                    return str(candidate.relative_to(self.docs_root)).replace('\\', '/')
                except ValueError:
                    continue
            
            # 尝试添加.md扩展名
            if not candidate.suffix:
                test_path = Path(str(candidate) + '.md')
                if test_path.exists() and str(test_path).startswith(str(self.docs_root)):
                    try:
                        return str(test_path.relative_to(self.docs_root)).replace('\\', '/')
                    except ValueError:
                        continue
                
                # 尝试INDEX.md
                test_path = Path(str(candidate) + '/INDEX.md')
                if test_path.exists() and str(test_path).startswith(str(self.docs_root)):
                    try:
                        return str(test_path.relative_to(self.docs_root)).replace('\\', '/')
                    except ValueError:
                        continue
                
                test_path = Path(str(candidate) + '/index.md')
                if test_path.exists() and str(test_path).startswith(str(self.docs_root)):
                    try:
                        return str(test_path.relative_to(self.docs_root)).replace('\\', '/')
                    except ValueError:
                        continue
            
            # 尝试小写匹配
            test_path_lower = Path(str(candidate).lower())
            for f in self.docs_root.rglob('*.md'):
                if str(f.relative_to(self.docs_root)).lower().replace('\\', '/') == str(test_path_lower).replace('\\', '/'):
                    return str(f.relative_to(self.docs_root)).replace('\\', '/')
        
        # 在已知文件中查找
        link_name = Path(link_url).name.lower()
        for known_file, full_path in self.known_files.items():
            if known_file.endswith(link_name.lower()) or link_name.lower() in known_file:
                return full_path
        
        return None
    
    def _find_correct_path(self, link_url, source_file):
        """查找链接的正确路径"""
        # 提取链接的文件名
        link_name = Path(link_url).name
        
        # 在文件索引中查找
        for known_path in self.known_files:
            if link_name.lower() in known_path.lower() or known_path.lower().endswith(link_name.lower()):
                return self.known_files[known_path]
        
        return None
    
    def process_file(self, file_path):
        """处理单个文件中的所有链接"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'file': str(file_path), 'error': str(e), 'links_fixed': 0}
        
        original_content = content
        links_fixed = 0
        
        # 匹配markdown链接 [text](url)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        
        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2).strip()
            
            # 跳过非文件链接
            if link_url.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
                self.stats['skipped_links'] += 1
                continue
            
            # 跳过锚点链接
            if link_url.startswith('#'):
                self.stats['skipped_links'] += 1
                continue
            
            self.stats['total_links'] += 1
            
            # 检查链接是否有效
            source_file = str(file_path.relative_to(self.docs_root))
            resolved_path = self._resolve_link(link_url, source_file)
            
            if resolved_path:
                # 链接有效
                self.stats['valid_links'] += 1
            else:
                # 链接无效，尝试修复
                self.stats['invalid_links'] += 1
                
                correct_path = self._find_correct_path(link_url, source_file)
                
                if correct_path:
                    # 构建新的链接
                    source_dir = Path(source_file).parent
                    try:
                        relative_path = str(Path(correct_path).relative_to(source_dir))
                    except ValueError:
                        relative_path = correct_path
                    
                    # 标准化路径分隔符
                    relative_path = relative_path.replace('\\', '/')
                    if not relative_path.startswith('./') and not relative_path.startswith('../'):
                        relative_path = './' + relative_path
                    
                    old_link = f'[{link_text}]({link_url})'
                    new_link = f'[{link_text}]({relative_path})'
                    
                    if old_link in content:
                        content = content.replace(old_link, new_link)
                        links_fixed += 1
                        self.stats['fixed_links'] += 1
                        self.stats['details'].append({
                            'source_file': source_file,
                            'link_text': link_text,
                            'old_url': link_url,
                            'new_url': relative_path,
                            'status': 'fixed'
                        })
        
        # 如果有修复，写回文件
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['files_processed'] += 1
            except Exception as e:
                return {'file': str(file_path), 'error': str(e), 'links_fixed': 0}
        
        return {'file': str(file_path), 'links_fixed': links_fixed}
    
    def scan_all_files(self):
        """扫描并修复所有文件"""
        md_files = list(self.docs_root.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        for md_file in md_files:
            result = self.process_file(md_file)
            if result.get('links_fixed', 0) > 0:
                print(f"  修复: {result['file']} - {result['links_fixed']} 个链接")
        
        return self.stats

def generate_report(stats, output_file):
    """生成修复报告"""
    report_lines = [
        "# 全系统无效链接修复报告",
        "",
        f"> **处理时间**: {stats['scan_time']}",
        "",
        "## 📊 处理概要",
        "",
        f"- **扫描文件数**: {stats['total_files']}",
        f"- **总链接数**: {stats['total_links']}",
        f"- **有效链接数**: {stats['valid_links']}",
        f"- **无效链接数**: {stats['invalid_links']}",
        f"- **已修复链接数**: {stats['fixed_links']}",
        f"- **跳过链接数**: {stats['skipped_links']}",
        f"- **已处理文件数**: {stats['files_processed']}",
        "",
    ]
    
    if stats['fixed_links'] > 0:
        report_lines.extend([
            "## 🔧 已修复链接详情（前100个）",
            "",
            "| 源文件 | 链接文本 | 原链接 | 新链接 | 状态 |",
            "|--------|---------|--------|--------|------|"
        ])
        
        for detail in stats['details'][:100]:
            report_lines.append(
                f"| {detail['source_file']} | {detail['link_text']} | {detail['old_url']} | {detail['new_url']} | ✅ |"
            )
        report_lines.append("")
    
    report_lines.extend([
        "---",
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return output_file

def main():
    """主函数"""
    docs_root = 'docs'
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/COMPREHENSIVE_LINK_FIX_REPORT_20260407.md'
    
    print("=" * 60)
    print("开始全系统无效链接修复...")
    print("=" * 60)
    
    fixer = ComprehensiveLinkFixer(docs_root)
    stats = fixer.scan_all_files()
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("=" * 60)
    print(f"扫描文件数: {stats['total_files']}")
    print(f"总链接数: {stats['total_links']}")
    print(f"有效链接数: {stats['valid_links']}")
    print(f"无效链接数: {stats['invalid_links']}")
    print(f"已修复链接数: {stats['fixed_links']}")
    print(f"跳过链接数: {stats['skipped_links']}")
    print(f"已处理文件数: {stats['files_processed']}")
    
    report_path = generate_report(stats, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 保存JSON格式结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
