#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能批量链接修复脚本
系统性修复所有无效链接
"""

import re
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict

class SmartLinkFixer:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.stats = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'fixed_links': 0,
            'unfixable_links': 0,
            'skipped_links': 0,
            'files_processed': 0,
            'fix_details': [],
            'unfixable_details': []
        }
        self.file_index = self._build_file_index()
    
    def _build_file_index(self):
        """构建文件索引，支持快速查找"""
        index = {
            'by_name': {},  # 按文件名索引
            'by_path': {},  # 按完整路径索引
            'by_name_lower': {}  # 按文件名小写索引
        }
        
        for md_file in self.docs_root.rglob('*.md'):
            rel_path = str(md_file.relative_to(self.docs_root)).replace('\\', '/')
            
            # 按完整路径索引
            index['by_path'][rel_path.lower()] = rel_path
            
            # 按文件名索引
            filename = md_file.name
            if filename not in index['by_name']:
                index['by_name'][filename] = []
            index['by_name'][filename].append(rel_path)
            
            # 按文件名小写索引
            filename_lower = filename.lower()
            if filename_lower not in index['by_name_lower']:
                index['by_name_lower'][filename_lower] = []
            index['by_name_lower'][filename_lower].append(rel_path)
        
        return index
    
    def _find_file_by_name(self, filename):
        """通过文件名查找文件"""
        # 先尝试精确匹配
        if filename in self.file_index['by_name']:
            matches = self.file_index['by_name'][filename]
            if len(matches) == 1:
                return matches[0]
        
        # 尝试小写匹配
        filename_lower = filename.lower()
        if filename_lower in self.file_index['by_name_lower']:
            matches = self.file_index['by_name_lower'][filename_lower]
            if len(matches) == 1:
                return matches[0]
        
        # 尝试部分匹配
        for name, paths in self.file_index['by_name_lower'].items():
            if filename_lower in name or name in filename_lower:
                if len(paths) == 1:
                    return paths[0]
        
        return None
    
    def _resolve_file_link(self, link_url, source_file):
        """解析文件链接"""
        source_dir = Path(source_file).parent
        
        # 1. 尝试直接解析
        candidates = [
            source_dir / link_url,
            self.docs_root / link_url,
            Path(link_url.lstrip('./')),
        ]
        
        for candidate in candidates:
            # 尝试添加.md扩展名
            if not candidate.suffix:
                test_path = Path(str(candidate) + '.md')
                if test_path.exists() and str(test_path).startswith(str(self.docs_root)):
                    try:
                        return str(test_path.relative_to(self.docs_root)).replace('\\', '/')
                    except ValueError:
                        pass
        
        # 2. 提取文件名并查找
        filename = Path(link_url).name
        if filename:
            found_path = self._find_file_by_name(filename)
            if found_path:
                return found_path
        
        return None
    
    def _fix_file_protocol_link(self, link_url):
        """修复file://协议链接"""
        # 提取路径部分
        match = re.match(r'file:///(.+?)(?:\.md)?$', link_url, re.IGNORECASE)
        if match:
            file_path = match.group(1)
            # 提取文件名
            filename = Path(file_path).name
            if filename:
                found_path = self._find_file_by_name(filename)
                if found_path:
                    return found_path
        return None
    
    def _fix_relative_path(self, link_url, source_file):
        """修复相对路径链接"""
        # 提取文件名
        filename = Path(link_url).name
        
        if filename:
            # 尝试查找文件
            found_path = self._find_file_by_name(filename)
            if found_path:
                # 计算相对路径
                source_dir = Path(source_file).parent
                try:
                    target_path = self.docs_root / found_path
                    relative_path = str(target_path.relative_to(self.docs_root / source_dir))
                    # 标准化路径
                    if not relative_path.startswith('.'):
                        relative_path = './' + relative_path
                    return relative_path.replace('\\', '/')
                except ValueError:
                    # 如果无法计算相对路径，返回绝对路径
                    return found_path
        
        return None
    
    def _fix_link(self, link_url, source_file):
        """智能修复链接"""
        # 1. 修复file://协议链接
        if link_url.startswith('file://'):
            return self._fix_file_protocol_link(link_url)
        
        # 2. 修复相对路径链接
        if link_url.startswith('./') or link_url.startswith('../'):
            return self._fix_relative_path(link_url, source_file)
        
        # 3. 修复普通链接
        return self._resolve_file_link(link_url, source_file)
    
    def process_file(self, file_path):
        """处理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'file': str(file_path), 'error': str(e), 'fixed': 0}
        
        original_content = content
        fixed_count = 0
        source_file = str(file_path.relative_to(self.docs_root)).replace('\\', '/')
        
        # 匹配markdown链接
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        
        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_url = match.group(2).strip()
            
            # 跳过非文件链接
            if link_url.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
                self.stats['skipped_links'] += 1
                continue
            
            self.stats['total_links'] += 1
            
            # 检查链接是否有效
            if link_url.startswith('file://'):
                # file://协议链接需要修复
                self.stats['invalid_links'] += 1
                fixed_path = self._fix_link(link_url, source_file)
                
                if fixed_path:
                    old_link = f'[{link_text}]({link_url})'
                    new_link = f'[{link_text}]({fixed_path})'
                    content = content.replace(old_link, new_link)
                    fixed_count += 1
                    self.stats['fixed_links'] += 1
                    self.stats['fix_details'].append({
                        'source_file': source_file,
                        'link_text': link_text,
                        'old_url': link_url,
                        'new_url': fixed_path,
                        'fix_type': 'file_protocol'
                    })
                else:
                    self.stats['unfixable_links'] += 1
                    self.stats['unfixable_details'].append({
                        'source_file': source_file,
                        'link_text': link_text,
                        'link_url': link_url,
                        'reason': 'file_not_found'
                    })
            else:
                # 检查普通链接
                source_dir = Path(source_file).parent
                target_path = source_dir / link_url
                
                # 尝试多种路径
                possible_paths = [
                    target_path,
                    self.docs_root / link_url.lstrip('./'),
                    Path(str(target_path) + '.md'),
                ]
                
                exists = any(
                    p.exists() and str(p).startswith(str(self.docs_root))
                    for p in possible_paths
                )
                
                if exists:
                    self.stats['valid_links'] += 1
                else:
                    self.stats['invalid_links'] += 1
                    fixed_path = self._fix_link(link_url, source_file)
                    
                    if fixed_path:
                        old_link = f'[{link_text}]({link_url})'
                        new_link = f'[{link_text}]({fixed_path})'
                        content = content.replace(old_link, new_link)
                        fixed_count += 1
                        self.stats['fixed_links'] += 1
                        self.stats['fix_details'].append({
                            'source_file': source_file,
                            'link_text': link_text,
                            'old_url': link_url,
                            'new_url': fixed_path,
                            'fix_type': 'relative_path'
                        })
                    else:
                        self.stats['unfixable_links'] += 1
                        self.stats['unfixable_details'].append({
                            'source_file': source_file,
                            'link_text': link_text,
                            'link_url': link_url,
                            'reason': 'file_not_found'
                        })
        
        # 如果有修复，写回文件
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['files_processed'] += 1
            except Exception as e:
                return {'file': str(file_path), 'error': str(e), 'fixed': 0}
        
        return {'file': str(file_path), 'fixed': fixed_count}
    
    def fix_all_files(self):
        """修复所有文件"""
        md_files = list(self.docs_root.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        print(f"开始处理 {len(md_files)} 个文件...")
        
        for i, md_file in enumerate(md_files, 1):
            if i % 100 == 0:
                print(f"  进度: {i}/{len(md_files)} ({i/len(md_files)*100:.1f}%)")
            
            result = self.process_file(md_file)
            if result.get('fixed', 0) > 0:
                print(f"  ✓ {result['file']}: 修复 {result['fixed']} 个链接")
        
        return self.stats

def generate_report(stats, output_file):
    """生成修复报告"""
    report_lines = [
        "# 智能批量链接修复报告",
        "",
        f"> **修复时间**: {stats['scan_time']}",
        "",
        "## 📊 修复概要",
        "",
        f"- **扫描文件数**: {stats['total_files']}",
        f"- **总链接数**: {stats['total_links']}",
        f"- **有效链接数**: {stats['valid_links']}",
        f"- **无效链接数**: {stats['invalid_links']}",
        f"- **已修复链接数**: {stats['fixed_links']}",
        f"- **无法修复链接数**: {stats['unfixable_links']}",
        f"- **跳过链接数**: {stats['skipped_links']}",
        f"- **已处理文件数**: {stats['files_processed']}",
        "",
        f"**修复成功率**: {stats['fixed_links'] / stats['invalid_links'] * 100:.2f}%" if stats['invalid_links'] > 0 else "**修复成功率**: N/A",
        ""
    ]
    
    if stats['fixed_links'] > 0:
        report_lines.extend([
            "## ✅ 已修复链接详情（前100个）",
            "",
            "| 源文件 | 链接文本 | 原链接 | 新链接 | 修复类型 |",
            "|--------|---------|--------|--------|----------|"
        ])
        
        for detail in stats['fix_details'][:100]:
            report_lines.append(
                f"| {detail['source_file']} | {detail['link_text']} | {detail['old_url']} | {detail['new_url']} | {detail['fix_type']} |"
            )
        report_lines.append("")
    
    if stats['unfixable_links'] > 0:
        report_lines.extend([
            "## ❌ 无法修复链接详情（前50个）",
            "",
            "| 源文件 | 链接文本 | 链接URL | 原因 |",
            "|--------|---------|---------|------|"
        ])
        
        for detail in stats['unfixable_details'][:50]:
            report_lines.append(
                f"| {detail['source_file']} | {detail['link_text']} | {detail['link_url']} | {detail['reason']} |"
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
    output_file = 'docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/SMART_LINK_FIX_REPORT_20260407.md'
    
    print("=" * 60)
    print("智能批量链接修复工具")
    print("=" * 60)
    
    fixer = SmartLinkFixer(docs_root)
    stats = fixer.fix_all_files()
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print("=" * 60)
    print(f"扫描文件数: {stats['total_files']}")
    print(f"总链接数: {stats['total_links']}")
    print(f"有效链接数: {stats['valid_links']}")
    print(f"无效链接数: {stats['invalid_links']}")
    print(f"已修复链接数: {stats['fixed_links']}")
    print(f"无法修复链接数: {stats['unfixable_links']}")
    if stats['invalid_links'] > 0:
        print(f"修复成功率: {stats['fixed_links'] / stats['invalid_links'] * 100:.2f}%")
    
    report_path = generate_report(stats, output_file)
    print(f"\n报告已生成: {report_path}")
    
    # 保存JSON格式结果
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"JSON结果已保存: {json_file}")

if __name__ == '__main__':
    main()
