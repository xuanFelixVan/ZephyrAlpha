#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交叉引用关系报告生成器
生成完整的文档引用关系图谱和统计报告

功能：
1. 分析所有文档的引用关系
2. 按层级分类引用关系
3. 生成Mermaid关系图
4. 生成统计报告

使用方法：
    python scripts/generate_cross_reference_report.py [--output OUTPUT_PATH]
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime


class CrossReferenceReportGenerator:
    """交叉引用关系报告生成器"""
    
    def __init__(self, blueprints_dir: str):
        self.blueprints_dir = Path(blueprints_dir)
        self.all_docs: Dict[str, Dict] = {}
        self.references: Dict[str, Dict] = {}
        self.layer_mapping: Dict[str, str] = {}
        
    def scan_all_documents(self) -> Dict[str, Dict]:
        """扫描所有蓝图文档并提取元数据"""
        md_files = list(self.blueprints_dir.glob("*.md"))
        
        for md_file in md_files:
            if md_file.name == "INDEX.md":
                continue
            
            doc_info = self._extract_doc_info(md_file)
            self.all_docs[md_file.name] = doc_info
            
            if doc_info.get('layer'):
                self.layer_mapping[md_file.name] = doc_info['layer']
        
        return self.all_docs
    
    def _extract_doc_info(self, doc_path: Path) -> Dict:
        """从文档中提取信息"""
        doc_info = {
            'file_name': doc_path.name,
            'module_id': None,
            'layer': None,
            'title': None,
            'upstream_refs': [],
            'downstream_refs': [],
            'tech_deps': []
        }
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取YAML头部信息
            yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 提取module_id
                module_match = re.search(r'module_id:\s*(.+)', yaml_content)
                if module_match:
                    doc_info['module_id'] = module_match.group(1).strip()
                
                # 提取layer
                layer_match = re.search(r'layer:\s*["\']?(.+?)["\']?\s*$', yaml_content, re.MULTILINE)
                if layer_match:
                    doc_info['layer'] = layer_match.group(1).strip()
            
            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                doc_info['title'] = title_match.group(1).strip()
            
            # 提取上游依赖
            upstream_pattern = r'###\s*上游依赖\s*\n\n\|.*?\n\|.*?\n([\s\S]*?)(?=\n###|\n##|$)'
            upstream_match = re.search(upstream_pattern, content)
            if upstream_match:
                upstream_content = upstream_match.group(1)
                refs = re.findall(r'\[([^\]]+)\]\(\.\/([^\)]+\.md)\)', upstream_content)
                doc_info['upstream_refs'] = [{'text': text, 'target': target} for text, target in refs]
            
            # 提取下游依赖
            downstream_pattern = r'###\s*下游依赖\s*\n\n\|.*?\n\|.*?\n([\s\S]*?)(?=\n###|\n##|$)'
            downstream_match = re.search(downstream_pattern, content)
            if downstream_match:
                downstream_content = downstream_match.group(1)
                refs = re.findall(r'\[([^\]]+)\]\(\.\/([^\)]+\.md)\)', downstream_content)
                doc_info['downstream_refs'] = [{'text': text, 'target': target} for text, target in refs]
            
            # 提取技术依赖
            tech_pattern = r'###\s*技术依赖\s*\n\n\|.*?\n\|.*?\n([\s\S]*?)(?=\n###|\n##|$)'
            tech_match = re.search(tech_pattern, content)
            if tech_match:
                tech_content = tech_match.group(1)
                techs = re.findall(r'\*\*([^*]+)\*\*', tech_content)
                doc_info['tech_deps'] = techs
        
        except Exception as e:
            print(f"读取文档 {doc_path.name} 时出错: {e}")
        
        return doc_info
    
    def analyze_references(self) -> Dict:
        """分析引用关系"""
        analysis = {
            'total_docs': len(self.all_docs),
            'total_upstream_refs': 0,
            'total_downstream_refs': 0,
            'docs_with_refs': 0,
            'docs_without_refs': 0,
            'most_referenced': [],
            'most_referencing': [],
            'layer_stats': defaultdict(lambda: {'docs': 0, 'refs': 0}),
            'tech_stack': defaultdict(int)
        }
        
        # 统计引用数量
        ref_count = defaultdict(int)
        referencing_count = defaultdict(int)
        
        for doc_name, doc_info in self.all_docs.items():
            upstream_count = len(doc_info['upstream_refs'])
            downstream_count = len(doc_info['downstream_refs'])
            
            analysis['total_upstream_refs'] += upstream_count
            analysis['total_downstream_refs'] += downstream_count
            
            if upstream_count > 0 or downstream_count > 0:
                analysis['docs_with_refs'] += 1
            else:
                analysis['docs_without_refs'] += 1
            
            # 统计被引用次数
            for ref in doc_info['downstream_refs']:
                ref_count[ref['target']] += 1
            
            # 统计引用次数
            referencing_count[doc_name] = upstream_count + downstream_count
            
            # 按层级统计
            layer = doc_info.get('layer', 'Unknown')
            analysis['layer_stats'][layer]['docs'] += 1
            analysis['layer_stats'][layer]['refs'] += upstream_count + downstream_count
            
            # 统计技术栈
            for tech in doc_info['tech_deps']:
                analysis['tech_stack'][tech] += 1
        
        # 最常被引用的文档
        analysis['most_referenced'] = sorted(ref_count.items(), key=lambda x: -x[1])[:10]
        
        # 引用最多的文档
        analysis['most_referencing'] = sorted(referencing_count.items(), key=lambda x: -x[1])[:10]
        
        return analysis
    
    def generate_mermaid_graph(self, max_nodes: int = 50) -> str:
        """生成Mermaid关系图"""
        lines = ["graph TD"]
        
        # 按层级分组
        layer_docs = defaultdict(list)
        for doc_name, doc_info in self.all_docs.items():
            layer = doc_info.get('layer', 'Unknown')
            layer_docs[layer].append(doc_name)
        
        # 为每个层级创建子图
        for layer, docs in sorted(layer_docs.items()):
            if len(docs) > max_nodes:
                continue
            
            layer_id = layer.replace(' ', '_').replace('(', '').replace(')', '')
            lines.append(f"    subgraph {layer_id}[{layer}]")
            
            for doc in docs[:max_nodes]:
                node_id = doc.replace('.md', '').replace('_', '')
                title = self.all_docs[doc].get('title', doc)
                if title and len(title) > 20:
                    title = title[:20] + '...'
                elif not title:
                    title = doc.replace('.md', '')
                lines.append(f"        {node_id}[\"{title}\"]")
            
            lines.append("    end")
        
        # 添加引用关系（限制数量）
        edge_count = 0
        for doc_name, doc_info in self.all_docs.items():
            if edge_count >= max_nodes * 2:
                break
            
            source_id = doc_name.replace('.md', '').replace('_', '')
            
            for ref in doc_info['downstream_refs'][:3]:  # 限制每个节点的出边数量
                target_id = ref['target'].replace('.md', '').replace('_', '')
                lines.append(f"    {source_id} --> {target_id}")
                edge_count += 1
                
                if edge_count >= max_nodes * 2:
                    break
        
        return '\n'.join(lines)
    
    def generate_report(self) -> Dict:
        """生成完整报告"""
        analysis = self.analyze_references()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_documents': analysis['total_docs'],
                'total_upstream_references': analysis['total_upstream_refs'],
                'total_downstream_references': analysis['total_downstream_refs'],
                'documents_with_references': analysis['docs_with_refs'],
                'documents_without_references': analysis['docs_without_refs'],
                'reference_coverage': f"{(analysis['docs_with_refs'] / analysis['total_docs'] * 100):.2f}%" if analysis['total_docs'] > 0 else "0%"
            },
            'top_referenced_documents': [
                {'document': doc, 'reference_count': count}
                for doc, count in analysis['most_referenced']
            ],
            'top_referencing_documents': [
                {'document': doc, 'reference_count': count}
                for doc, count in analysis['most_referencing']
            ],
            'layer_statistics': {
                layer: {
                    'document_count': stats['docs'],
                    'reference_count': stats['refs'],
                    'avg_refs_per_doc': f"{(stats['refs'] / stats['docs']):.2f}" if stats['docs'] > 0 else "0"
                }
                for layer, stats in analysis['layer_stats'].items()
            },
            'technology_stack': {
                tech: count for tech, count in sorted(analysis['tech_stack'].items(), key=lambda x: -x[1])
            },
            'mermaid_graph': self.generate_mermaid_graph()
        }
        
        return report
    
    def print_report(self):
        """打印报告"""
        report = self.generate_report()
        
        print("\n" + "="*80)
        print("📊 交叉引用关系报告")
        print("="*80)
        
        print(f"\n生成时间: {report['generated_at']}")
        
        print("\n## 📈 总体统计")
        print(f"- 文档总数: {report['summary']['total_documents']}")
        print(f"- 上游引用总数: {report['summary']['total_upstream_references']}")
        print(f"- 下游引用总数: {report['summary']['total_downstream_references']}")
        print(f"- 有引用的文档: {report['summary']['documents_with_references']}")
        print(f"- 无引用的文档: {report['summary']['documents_without_references']}")
        print(f"- 引用覆盖率: {report['summary']['reference_coverage']}")
        
        print("\n## 🔝 最常被引用的文档（Top 10）")
        for i, item in enumerate(report['top_referenced_documents'], 1):
            print(f"{i}. {item['document']}: {item['reference_count']} 次")
        
        print("\n## 📝 引用最多的文档（Top 10）")
        for i, item in enumerate(report['top_referencing_documents'], 1):
            print(f"{i}. {item['document']}: {item['reference_count']} 个引用")
        
        print("\n## 📊 按层级统计")
        for layer, stats in sorted(report['layer_statistics'].items()):
            print(f"\n### {layer}")
            print(f"- 文档数: {stats['document_count']}")
            print(f"- 引用数: {stats['reference_count']}")
            print(f"- 平均引用: {stats['avg_refs_per_doc']}")
        
        print("\n## 🔧 技术栈统计（Top 20）")
        for i, (tech, count) in enumerate(list(report['technology_stack'].items())[:20], 1):
            print(f"{i}. {tech}: {count} 个文档使用")
        
        print("\n" + "="*80)
    
    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存到: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='生成交叉引用关系报告')
    parser.add_argument('--output', '-o', type=str, 
                       default='reports/cross_reference_report.json',
                       help='输出报告文件路径')
    parser.add_argument('--blueprints-dir', type=str, 
                       default='docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS',
                       help='蓝图文档目录路径')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    blueprints_dir = project_root / args.blueprints_dir
    
    # 创建报告生成器
    generator = CrossReferenceReportGenerator(str(blueprints_dir))
    
    # 扫描文档
    print("正在扫描文档...")
    generator.scan_all_documents()
    
    # 打印报告
    generator.print_report()
    
    # 保存报告
    output_path = project_root / args.output
    generator.save_report(str(output_path))


if __name__ == '__main__':
    main()
