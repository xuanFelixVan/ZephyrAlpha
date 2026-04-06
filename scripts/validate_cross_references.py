#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交叉引用链接验证工具
验证所有蓝图文档中的引用链接是否有效

功能：
1. 扫描所有蓝图文档
2. 提取所有引用链接
3. 检查链接目标文件是否存在
4. 生成验证报告

使用方法：
    python scripts/validate_cross_references.py [--verbose] [--report]
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from datetime import datetime


class CrossReferenceValidator:
    """交叉引用验证器"""
    
    def __init__(self, blueprints_dir: str, verbose: bool = False):
        self.blueprints_dir = Path(blueprints_dir)
        self.verbose = verbose
        self.all_docs: Set[str] = set()
        self.references: Dict[str, List[Dict]] = defaultdict(list)
        self.broken_links: List[Dict] = []
        self.valid_links: List[Dict] = []
        
    def scan_all_documents(self) -> Set[str]:
        """扫描所有蓝图文档"""
        if self.verbose:
            print(f"扫描目录: {self.blueprints_dir}")
        
        md_files = list(self.blueprints_dir.glob("*.md"))
        self.all_docs = {f.name for f in md_files if f.name != "INDEX.md"}
        
        if self.verbose:
            print(f"找到 {len(self.all_docs)} 个文档")
        
        return self.all_docs
    
    def extract_references(self, doc_path: Path) -> List[Dict]:
        """从文档中提取所有引用链接"""
        references = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配格式: [文档名称](./DOCUMENT_NAME.md)
            pattern = r'\[([^\]]+)\]\(\.\/([^\)]+\.md)\)'
            matches = re.findall(pattern, content)
            
            for link_text, link_target in matches:
                references.append({
                    'source_doc': doc_path.name,
                    'link_text': link_text,
                    'link_target': link_target,
                    'line_number': self._find_line_number(content, link_target)
                })
        
        except Exception as e:
            if self.verbose:
                print(f"读取文档 {doc_path.name} 时出错: {e}")
        
        return references
    
    def _find_line_number(self, content: str, target: str) -> int:
        """查找链接在文档中的行号"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if target in line:
                return i
        return 0
    
    def validate_all_references(self) -> Tuple[List[Dict], List[Dict]]:
        """验证所有引用链接"""
        if self.verbose:
            print("\n开始验证引用链接...")
        
        for doc_name in sorted(self.all_docs):
            doc_path = self.blueprints_dir / doc_name
            refs = self.extract_references(doc_path)
            
            for ref in refs:
                target_exists = ref['link_target'] in self.all_docs
                
                ref['target_exists'] = target_exists
                ref['status'] = '✅ 有效' if target_exists else '❌ 断链'
                
                if target_exists:
                    self.valid_links.append(ref)
                else:
                    self.broken_links.append(ref)
                
                self.references[doc_name].append(ref)
        
        if self.verbose:
            print(f"验证完成: {len(self.valid_links)} 个有效链接, {len(self.broken_links)} 个断链")
        
        return self.valid_links, self.broken_links
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        total_links = len(self.valid_links) + len(self.broken_links)
        valid_rate = (len(self.valid_links) / total_links * 100) if total_links > 0 else 0
        
        # 按文档统计断链
        broken_by_doc = defaultdict(list)
        for ref in self.broken_links:
            broken_by_doc[ref['source_doc']].append(ref)
        
        # 按目标统计缺失文档
        missing_targets = defaultdict(int)
        for ref in self.broken_links:
            missing_targets[ref['link_target']] += 1
        
        report = {
            'scan_time': datetime.now().isoformat(),
            'summary': {
                'total_documents': len(self.all_docs),
                'total_links': total_links,
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links),
                'valid_rate': f"{valid_rate:.2f}%",
                'status': '✅ 全部有效' if len(self.broken_links) == 0 else f'⚠️ 发现 {len(self.broken_links)} 个断链'
            },
            'broken_links': {
                'count': len(self.broken_links),
                'by_source_doc': {k: v for k, v in sorted(broken_by_doc.items())},
                'by_missing_target': {k: v for k, v in sorted(missing_targets.items(), key=lambda x: -x[1])}
            },
            'valid_links': {
                'count': len(self.valid_links)
            },
            'recommendations': self._generate_recommendations(missing_targets)
        }
        
        return report
    
    def _generate_recommendations(self, missing_targets: Dict[str, int]) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        if len(missing_targets) > 0:
            recommendations.append("## 修复建议")
            recommendations.append("")
            recommendations.append("### 1. 创建缺失的文档")
            recommendations.append("以下文档被引用但不存在，建议创建：")
            recommendations.append("")
            
            for target, count in sorted(missing_targets.items(), key=lambda x: -x[1]):
                recommendations.append(f"- `{target}` (被引用 {count} 次)")
            
            recommendations.append("")
            recommendations.append("### 2. 或更新引用链接")
            recommendations.append("如果文档已重命名或合并，请更新引用链接：")
            recommendations.append("")
            
            for target in sorted(missing_targets.keys()):
                recommendations.append(f"- 检查 `{target}` 是否已重命名")
        
        return recommendations
    
    def print_summary(self):
        """打印验证摘要"""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("📊 交叉引用验证报告")
        print("="*80)
        
        print(f"\n扫描时间: {report['scan_time']}")
        summary = report['summary']
        print(f"文档总数: {summary['total_documents']}")
        print(f"链接总数: {summary['total_links']}")
        print(f"有效链接: {summary['valid_links']}")
        print(f"断链数量: {summary['broken_links']}")
        print(f"有效率: {summary['valid_rate']}")
        print(f"状态: {summary['status']}")
        
        if len(self.broken_links) > 0:
            print("\n" + "-"*80)
            print("❌ 断链详情")
            print("-"*80)
            
            broken = report['broken_links']
            print(f"\n按源文档统计:")
            for doc, refs in broken['by_source_doc'].items():
                print(f"\n  📄 {doc}:")
                for ref in refs:
                    print(f"     - 行 {ref['line_number']}: [{ref['link_text']}](./{ref['link_target']})")
            
            print(f"\n按缺失目标统计:")
            for target, count in broken['by_missing_target'].items():
                print(f"  - {target}: 被引用 {count} 次")
            
            print("\n" + "-"*80)
            for line in report['recommendations']:
                print(line)
        
        print("\n" + "="*80)
    
    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"\n报告已保存到: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='验证蓝图文档交叉引用链接')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--report', '-r', type=str, help='保存报告到指定文件')
    parser.add_argument('--blueprints-dir', type=str, 
                       default='docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS',
                       help='蓝图文档目录路径')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    blueprints_dir = project_root / args.blueprints_dir
    
    # 创建验证器
    validator = CrossReferenceValidator(str(blueprints_dir), verbose=args.verbose)
    
    # 执行验证
    validator.scan_all_documents()
    validator.validate_all_references()
    
    # 打印摘要
    validator.print_summary()
    
    # 保存报告
    if args.report:
        report_path = project_root / args.report
        validator.save_report(str(report_path))


if __name__ == '__main__':
    main()
