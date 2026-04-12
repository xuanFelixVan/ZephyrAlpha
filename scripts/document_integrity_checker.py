#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档完整性检查工具 v1.0.0

功能：
1. 检查文档大小异常（过小可能内容丢失）
2. 检查YAML头部完整性
3. 检查文档结构完整性
4. 检查必需章节是否存在
5. 生成完整性检查报告

使用方法：
    python scripts/document_integrity_checker.py --dir docs/ --output reports/integrity_check.json
    python scripts/document_integrity_checker.py --dir docs/10_AI_WORKFLOW --min-size 100
    python scripts/document_integrity_checker.py --help

作者: 蓝图架构师
创建日期: 2026-04-03
版本: v1.0.0
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re


class DocumentIntegrityChecker:
    """文档完整性检查器"""
    
    def __init__(self, 
                 target_dir: str,
                 min_size: int = 100,
                 check_yaml: bool = True,
                 check_structure: bool = True,
                 required_sections: List[str] = None):
        """
        初始化检查器
        
        Args:
            target_dir: 目标目录
            min_size: 最小文件大小（字节）
            check_yaml: 是否检查YAML头部
            check_structure: 是否检查文档结构
            required_sections: 必需章节列表
        """
        self.target_dir = Path(target_dir)
        self.min_size = min_size
        self.check_yaml = check_yaml
        self.check_structure = check_structure
        self.required_sections = required_sections or [
            '概述', '架构', '实施', '风险'
        ]
        
        self.documents = {}
        self.issues = []
        
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
                
                file_size = md_file.stat().st_size
                line_count = len(content.split('\n'))
                
                self.documents[str(md_file)] = {
                    'path': str(md_file),
                    'content': content,
                    'size': file_size,
                    'line_count': line_count,
                    'has_yaml': content.strip().startswith('---'),
                }
                
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        print(f"扫描完成，共发现 {len(self.documents)} 个文档")
        return self.documents
    
    def check_size_anomalies(self) -> List[Dict]:
        """
        检查文档大小异常
        
        Returns:
            大小异常问题列表
        """
        issues = []
        
        for doc_path, doc_info in self.documents.items():
            if doc_info['size'] < self.min_size:
                issues.append({
                    'type': 'size_anomaly',
                    'severity': 'P0',
                    'file': doc_path,
                    'size': doc_info['size'],
                    'min_size': self.min_size,
                    'description': f'文档大小异常: {doc_info["size"]}字节 < {self.min_size}字节',
                    'suggestion': '检查文档内容是否丢失，从Git历史恢复'
                })
        
        return issues
    
    def check_yaml_headers(self) -> List[Dict]:
        """
        检查YAML头部完整性
        
        Returns:
            YAML头部问题列表
        """
        issues = []
        
        if not self.check_yaml:
            return issues
        
        required_fields = ['module_id', 'version', 'created_date']
        
        for doc_path, doc_info in self.documents.items():
            if not doc_info['has_yaml']:
                # 跳过INDEX.md等特殊文件
                if 'INDEX.md' in doc_path or 'README.md' in doc_path:
                    continue
                    
                issues.append({
                    'type': 'yaml_missing',
                    'severity': 'P1',
                    'file': doc_path,
                    'description': '文档缺少YAML头部',
                    'suggestion': '添加标准YAML头部元数据'
                })
                continue
            
            # 提取YAML头部
            content = doc_info['content']
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 检查必需字段
                missing_fields = []
                for field in required_fields:
                    if f'{field}:' not in yaml_content:
                        missing_fields.append(field)
                
                if missing_fields:
                    issues.append({
                        'type': 'yaml_incomplete',
                        'severity': 'P2',
                        'file': doc_path,
                        'missing_fields': missing_fields,
                        'description': f'YAML头部缺少必需字段: {", ".join(missing_fields)}',
                        'suggestion': f'添加缺失字段: {", ".join(missing_fields)}'
                    })
        
        return issues
    
    def check_document_structure(self) -> List[Dict]:
        """
        检查文档结构完整性
        
        Returns:
            文档结构问题列表
        """
        issues = []
        
        if not self.check_structure:
            return issues
        
        for doc_path, doc_info in self.documents.items():
            # 跳过特殊文件
            if 'INDEX.md' in doc_path or 'README.md' in doc_path:
                continue
            
            content = doc_info['content']
            
            # 检查必需章节
            missing_sections = []
            for section in self.required_sections:
                # 检查多种可能的章节格式
                patterns = [
                    f'# {section}',
                    f'## {section}',
                    f'# 一、{section}',
                    f'## 一、{section}',
                    f'# 一{section}',
                    f'## 一{section}',
                ]
                
                found = False
                for pattern in patterns:
                    if pattern in content:
                        found = True
                        break
                
                if not found:
                    missing_sections.append(section)
            
            if missing_sections:
                issues.append({
                    'type': 'structure_incomplete',
                    'severity': 'P2',
                    'file': doc_path,
                    'missing_sections': missing_sections,
                    'description': f'文档缺少推荐章节: {", ".join(missing_sections)}',
                    'suggestion': f'添加缺失章节: {", ".join(missing_sections)}'
                })
        
        return issues
    
    def check_content_quality(self) -> List[Dict]:
        """
        检查内容质量
        
        Returns:
            内容质量问题列表
        """
        issues = []
        
        for doc_path, doc_info in self.documents.items():
            content = doc_info['content']
            
            # 检查空文档
            if len(content.strip()) < 50:
                issues.append({
                    'type': 'empty_document',
                    'severity': 'P0',
                    'file': doc_path,
                    'description': '文档内容过少，可能为空文档',
                    'suggestion': '检查文档内容是否丢失'
                })
            
            # 检查TODO标记
            todo_count = content.count('TODO') + content.count('todo')
            if todo_count > 3:
                issues.append({
                    'type': 'too_many_todos',
                    'severity': 'P2',
                    'file': doc_path,
                    'todo_count': todo_count,
                    'description': f'文档包含过多TODO标记: {todo_count}个',
                    'suggestion': '完成TODO项或转换为Issue跟踪'
                })
            
            # 检查旧架构关键词
            old_keywords = ['Layer 0', 'Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 
                          'Layer 5', 'Layer 6', 'Layer 7', 'Layer 8']
            found_keywords = []
            for keyword in old_keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            if found_keywords:
                issues.append({
                    'type': 'old_architecture_keywords',
                    'severity': 'P1',
                    'file': doc_path,
                    'keywords': found_keywords,
                    'description': f'文档包含旧架构关键词: {", ".join(found_keywords)}',
                    'suggestion': '更新为新的架构命名规范'
                })
        
        return issues
    
    def run_checks(self) -> Dict:
        """
        运行所有检查
        
        Returns:
            检查结果字典
        """
        print("\n检查文档大小异常...")
        size_issues = self.check_size_anomalies()
        self.issues.extend(size_issues)
        print(f"发现 {len(size_issues)} 个大小异常问题")
        
        print("\n检查YAML头部完整性...")
        yaml_issues = self.check_yaml_headers()
        self.issues.extend(yaml_issues)
        print(f"发现 {len(yaml_issues)} 个YAML头部问题")
        
        print("\n检查文档结构完整性...")
        structure_issues = self.check_document_structure()
        self.issues.extend(structure_issues)
        print(f"发现 {len(structure_issues)} 个结构问题")
        
        print("\n检查内容质量...")
        quality_issues = self.check_content_quality()
        self.issues.extend(quality_issues)
        print(f"发现 {len(quality_issues)} 个质量问题")
        
        return {
            'scan_info': {
                'target_dir': str(self.target_dir),
                'scan_time': datetime.now().isoformat(),
                'document_count': len(self.documents),
                'min_size': self.min_size,
            },
            'summary': {
                'total_issues': len(self.issues),
                'p0_issues': len([i for i in self.issues if i['severity'] == 'P0']),
                'p1_issues': len([i for i in self.issues if i['severity'] == 'P1']),
                'p2_issues': len([i for i in self.issues if i['severity'] == 'P2']),
            },
            'issues': self.issues,
        }
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """
        生成检查报告
        
        Args:
            results: 检查结果
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        report_lines = [
            "# 文档完整性检查报告",
            "",
            f"**检查时间**: {results['scan_info']['scan_time']}",
            f"**检查范围**: {results['scan_info']['target_dir']}",
            f"**文档总数**: {results['scan_info']['document_count']}",
            f"**最小文件大小**: {results['scan_info']['min_size']}字节",
            "",
            "---",
            "",
            "## 📊 检查结果概览",
            "",
            f"- **总问题数**: {results['summary']['total_issues']}",
            f"- **P0级问题**: {results['summary']['p0_issues']}",
            f"- **P1级问题**: {results['summary']['p1_issues']}",
            f"- **P2级问题**: {results['summary']['p2_issues']}",
            "",
        ]
        
        # 按严重程度分组
        for severity in ['P0', 'P1', 'P2']:
            severity_issues = [i for i in results['issues'] if i['severity'] == severity]
            
            if not severity_issues:
                continue
            
            severity_emoji = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}
            severity_label = {'P0': '严重问题', 'P1': '重要问题', 'P2': '一般问题'}
            
            report_lines.extend([
                f"## {severity_emoji[severity]} {severity}级{severity_label[severity]}",
                "",
            ])
            
            for issue in severity_issues:
                report_lines.extend([
                    f"### {issue['type']}",
                    "",
                    f"**问题等级**: {issue['severity']}",
                    f"**问题描述**: {issue['description']}",
                    f"**源文件**: `{Path(issue['file']).name}`",
                    f"**建议**: {issue['suggestion']}",
                    "",
                ])
        
        report_lines.extend([
            "---",
            "",
            f"**检查工具**: document_integrity_checker.py v1.0.0",
            f"**检查日期**: {datetime.now().strftime('%Y-%m-%d')}",
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
        description='文档完整性检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检查docs目录下所有文档
  python scripts/document_integrity_checker.py --dir docs/ --output reports/integrity_check.json
  
  # 检查特定目录，设置最小文件大小
  python scripts/document_integrity_checker.py --dir docs/10_AI_WORKFLOW --min-size 100
  
  # 只检查YAML头部
  python scripts/document_integrity_checker.py --dir docs/ --no-structure
        """
    )
    
    parser.add_argument('--dir', required=True, help='要检查的目录路径')
    parser.add_argument('--output', help='输出报告文件路径（JSON格式）')
    parser.add_argument('--min-size', type=int, default=100, 
                       help='最小文件大小（字节），默认100')
    parser.add_argument('--no-yaml', action='store_true', help='跳过YAML头部检查')
    parser.add_argument('--no-structure', action='store_true', help='跳过文档结构检查')
    parser.add_argument('--required-sections', nargs='+', 
                       help='必需章节列表，默认: 概述 架构 实施 风险')
    
    args = parser.parse_args()
    
    # 创建检查器
    checker = DocumentIntegrityChecker(
        target_dir=args.dir,
        min_size=args.min_size,
        check_yaml=not args.no_yaml,
        check_structure=not args.no_structure,
        required_sections=args.required_sections,
    )
    
    # 扫描文档
    checker.scan_documents()
    
    # 运行检查
    results = checker.run_checks()
    
    # 生成报告
    if args.output:
        report = checker.generate_report(results, args.output)
    else:
        report = checker.generate_report(results)
        print("\n" + "="*80)
        print(report)
    
    # 保存JSON结果
    if args.output:
        json_output = args.output.replace('.json', '_data.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"详细数据已保存到: {json_output}")
    
    # 返回退出码
    if results['summary']['p0_issues'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
