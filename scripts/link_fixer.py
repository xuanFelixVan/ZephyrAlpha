#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
链接自动修复工具 v1.0.0

功能：
1. 自动修复锚点链接格式问题
2. 删除指向不存在文件的链接
3. 更新链接为正确的新文件名
4. 生成修复报告

使用方法：
    python scripts/link_fixer.py --dir docs/10_AI_WORKFLOW --report reports/link_fix_report.json
    python scripts/link_fixer.py --dir docs/ --fix --report reports/full_link_fix_report.json
    python scripts/link_fixer.py --help

作者: 蓝图架构师
创建日期: 2026-04-04
版本: v1.0.0
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
import unicodedata


class LinkFixer:
    """链接自动修复器"""
    
    def __init__(self, target_dir: str, auto_fix: bool = False):
        """
        初始化修复器
        
        Args:
            target_dir: 目标目录
            auto_fix: 是否自动修复
        """
        self.target_dir = Path(target_dir)
        self.auto_fix = auto_fix
        
        self.documents = {}
        self.fixes = []
        self.file_index = {}
        
    def scan_documents(self) -> Dict[str, Dict]:
        """
        扫描目录中的所有文档
        
        Returns:
            文档信息字典
        """
        print("开始扫描文档...")
        
        md_files = list(self.target_dir.rglob('*.md'))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.documents[str(md_file)] = {
                    'path': str(md_file),
                    'content': content,
                    'lines': content.split('\n'),
                }
                
                # 建立文件索引（用于查找文件）
                self.file_index[md_file.name] = str(md_file)
                
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        print(f"扫描完成，共发现 {len(self.documents)} 个文档")
        return self.documents
    
    def generate_anchor(self, heading: str) -> str:
        """
        根据标题生成正确的锚点
        
        Args:
            heading: 标题文本
            
        Returns:
            正确的锚点
        """
        # 移除标题标记（#、##等）
        heading = re.sub(r'^#+\s*', '', heading)
        
        # 移除特殊字符，只保留中文、英文、数字、空格、连字符
        anchor = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s-]', '', heading)
        
        # 转换为小写（英文部分）
        anchor = anchor.lower()
        
        # 替换空格为连字符
        anchor = re.sub(r'\s+', '-', anchor)
        
        # 移除多余的连字符
        anchor = re.sub(r'-+', '-', anchor)
        anchor = anchor.strip('-')
        
        return anchor
    
    def extract_headings(self, content: str) -> Dict[str, str]:
        """
        提取文档中的所有标题及其锚点
        
        Args:
            content: 文档内容
            
        Returns:
            标题到锚点的映射
        """
        headings = {}
        
        for line in content.split('\n'):
            # 匹配Markdown标题
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                heading_text = match.group(2)
                anchor = self.generate_anchor(heading_text)
                headings[heading_text] = anchor
                headings[anchor] = anchor  # 同时存储锚点本身
        
        return headings
    
    def fix_anchor_links(self, doc_path: str, content: str) -> Tuple[str, List[Dict]]:
        """
        修复锚点链接
        
        Args:
            doc_path: 文档路径
            content: 文档内容
            
        Returns:
            (修复后的内容, 修复列表)
        """
        fixes = []
        headings = self.extract_headings(content)
        
        # 查找所有锚点链接
        pattern = r'\[([^\]]+)\]\((#[^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # 提取锚点部分
            anchor = link_url[1:]  # 移除开头的#
            
            # 检查锚点是否存在
            if anchor in headings.values():
                # 锚点已存在，无需修复
                return match.group(0)
            
            # 尝试找到匹配的标题
            for heading_text, heading_anchor in headings.items():
                if anchor in heading_text or heading_text in anchor:
                    # 找到匹配的标题，生成正确的锚点
                    correct_anchor = heading_anchor
                    if correct_anchor != anchor:
                        new_link = f'[{link_text}](#{correct_anchor})'
                        fixes.append({
                            'type': 'anchor_fix',
                            'file': doc_path,
                            'original': match.group(0),
                            'fixed': new_link,
                            'description': f'修复锚点链接: {anchor} -> {correct_anchor}'
                        })
                        return new_link
            
            # 未找到匹配的标题，保留原链接
            return match.group(0)
        
        fixed_content = re.sub(pattern, replace_link, content)
        
        return fixed_content, fixes
    
    def fix_file_links(self, doc_path: str, content: str) -> Tuple[str, List[Dict]]:
        """
        修复文件链接
        
        Args:
            doc_path: 文档路径
            content: 文档内容
            
        Returns:
            (修复后的内容, 修复列表)
        """
        fixes = []
        
        # 查找所有文件链接
        pattern = r'\[([^\]]+)\]\(([^)#]+)(?:#[^)]*)?\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # 跳过外部链接
            if link_url.startswith('http://') or link_url.startswith('https://'):
                return match.group(0)
            
            # 解析相对路径
            doc_dir = Path(doc_path).parent
            target_path = (doc_dir / link_url).resolve()
            
            # 检查文件是否存在
            if target_path.exists():
                # 文件存在，无需修复
                return match.group(0)
            
            # 文件不存在，检查是否有新文件名
            target_name = target_path.name
            
            # 检查是否是旧架构命名（LAYER3_XXX -> SENTIMENT_ANALYSIS_XXX）
            if 'LAYER3_' in target_name:
                new_name = target_name.replace('LAYER3_', 'SENTIMENT_ANALYSIS_')
                if new_name in self.file_index:
                    # 找到新文件名，更新链接
                    new_path = Path(self.file_index[new_name])
                    relative_path = os.path.relpath(new_path, doc_dir)
                    new_link = f'[{link_text}]({relative_path})'
                    fixes.append({
                        'type': 'file_rename',
                        'file': doc_path,
                        'original': match.group(0),
                        'fixed': new_link,
                        'description': f'更新文件链接: {target_name} -> {new_name}'
                    })
                    return new_link
            
            # 检查是否是其他已知文件
            if target_name in self.file_index:
                # 文件存在但路径不对，更新路径
                new_path = Path(self.file_index[target_name])
                relative_path = os.path.relpath(new_path, doc_dir)
                new_link = f'[{link_text}]({relative_path})'
                fixes.append({
                    'type': 'path_fix',
                    'file': doc_path,
                    'original': match.group(0),
                    'fixed': new_link,
                    'description': f'修复文件路径: {link_url} -> {relative_path}'
                })
                return new_link
            
            # 文件不存在且无法修复，删除链接（保留文本）
            fixes.append({
                'type': 'broken_link',
                'file': doc_path,
                'original': match.group(0),
                'fixed': link_text,  # 只保留文本
                'description': f'删除失效链接: {link_url}'
            })
            return link_text
        
        fixed_content = re.sub(pattern, replace_link, content)
        
        return fixed_content, fixes
    
    def fix_document(self, doc_path: str) -> Dict:
        """
        修复单个文档
        
        Args:
            doc_path: 文档路径
            
        Returns:
            修复结果
        """
        doc_info = self.documents[doc_path]
        content = doc_info['content']
        
        all_fixes = []
        
        # 修复文件链接
        content, file_fixes = self.fix_file_links(doc_path, content)
        all_fixes.extend(file_fixes)
        
        # 修复锚点链接
        content, anchor_fixes = self.fix_anchor_links(doc_path, content)
        all_fixes.extend(anchor_fixes)
        
        # 如果有修复且启用自动修复，则保存文件
        if all_fixes and self.auto_fix:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复 {doc_path}: {len(all_fixes)} 处")
        
        return {
            'file': doc_path,
            'fix_count': len(all_fixes),
            'fixes': all_fixes,
        }
    
    def run_fixes(self) -> Dict:
        """
        运行所有修复
        
        Returns:
            修复结果字典
        """
        print("\n开始修复链接...")
        
        results = []
        total_fixes = 0
        
        for doc_path in self.documents.keys():
            result = self.fix_document(doc_path)
            results.append(result)
            total_fixes += result['fix_count']
        
        print(f"\n修复完成，共修复 {total_fixes} 处链接")
        
        return {
            'scan_info': {
                'target_dir': str(self.target_dir),
                'scan_time': datetime.now().isoformat(),
                'document_count': len(self.documents),
                'auto_fix': self.auto_fix,
            },
            'summary': {
                'total_fixes': total_fixes,
                'files_fixed': len([r for r in results if r['fix_count'] > 0]),
            },
            'results': results,
        }
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """
        生成修复报告
        
        Args:
            results: 修复结果
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        report_lines = [
            "# 链接修复报告",
            "",
            f"**修复时间**: {results['scan_info']['scan_time']}",
            f"**修复范围**: {results['scan_info']['target_dir']}",
            f"**文档总数**: {results['scan_info']['document_count']}",
            f"**自动修复**: {'是' if results['scan_info']['auto_fix'] else '否'}",
            "",
            "---",
            "",
            "## 📊 修复结果概览",
            "",
            f"- **总修复数**: {results['summary']['total_fixes']}",
            f"- **修复文件数**: {results['summary']['files_fixed']}",
            "",
        ]
        
        # 按修复类型分组
        fix_types = {}
        for result in results['results']:
            for fix in result['fixes']:
                fix_type = fix['type']
                if fix_type not in fix_types:
                    fix_types[fix_type] = []
                fix_types[fix_type].append(fix)
        
        # 输出各类型修复详情
        type_labels = {
            'anchor_fix': '锚点链接修复',
            'file_rename': '文件重命名修复',
            'path_fix': '路径修复',
            'broken_link': '失效链接删除',
        }
        
        for fix_type, fixes in fix_types.items():
            label = type_labels.get(fix_type, fix_type)
            report_lines.extend([
                f"## 🔧 {label}",
                "",
                f"**修复数量**: {len(fixes)}",
                "",
            ])
            
            for fix in fixes[:10]:  # 只显示前10个
                report_lines.extend([
                    f"### {Path(fix['file']).name}",
                    "",
                    f"**原链接**: `{fix['original']}`",
                    f"**修复后**: `{fix['fixed']}`",
                    f"**说明**: {fix['description']}",
                    "",
                ])
            
            if len(fixes) > 10:
                report_lines.append(f"*...还有 {len(fixes) - 10} 处修复*")
                report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            f"**修复工具**: link_fixer.py v1.0.0",
            f"**修复日期**: {datetime.now().strftime('%Y-%m-%d')}",
        ])
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"\n报告已保存到: {output_file}")
        
        return report_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='链接自动修复工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 扫描并生成修复报告（不自动修复）
  python scripts/link_fixer.py --dir docs/10_AI_WORKFLOW --report reports/link_fix_report.json
  
  # 扫描并自动修复
  python scripts/link_fixer.py --dir docs/10_AI_WORKFLOW --fix --report reports/link_fix_report.json
  
  # 扫描全系统并自动修复
  python scripts/link_fixer.py --dir docs/ --fix --report reports/full_link_fix_report.json
        """
    )
    
    parser.add_argument('--dir', required=True, help='要扫描的目录路径')
    parser.add_argument('--fix', action='store_true', help='自动修复链接')
    parser.add_argument('--report', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    # 创建修复器
    fixer = LinkFixer(
        target_dir=args.dir,
        auto_fix=args.fix,
    )
    
    # 扫描文档
    fixer.scan_documents()
    
    # 运行修复
    results = fixer.run_fixes()
    
    # 生成报告
    if args.report:
        report = fixer.generate_report(results, args.report)
    else:
        report = fixer.generate_report(results)
        print("\n" + "="*80)
        print(report)
    
    # 保存JSON结果
    if args.report:
        json_output = args.report.replace('.json', '_data.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"详细数据已保存到: {json_output}")
    
    # 返回退出码
    if results['summary']['total_fixes'] > 0 and not args.fix:
        print("\n提示: 使用 --fix 参数自动修复链接")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
