#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据预处理层深度审计工具
对Layer 1的所有文档进行全面深度审计

功能：
1. 扫描所有Layer 1文档
2. 检查职责清晰度
3. 检测重复内容
4. 验证YAML头部完整性
5. 检查文档结构规范性
6. 生成详细审计报告

使用方法：
    python scripts/deep_audit_layer1.py [--output OUTPUT_PATH] [--backup]
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import subprocess


class Layer1DeepAuditor:
    """数据预处理层深度审计器"""
    
    def __init__(self, blueprints_dir: str, backup: bool = False):
        self.blueprints_dir = Path(blueprints_dir)
        self.backup = backup
        self.layer1_docs: Dict[str, Dict] = {}
        self.audit_results: Dict = {
            'scan_time': datetime.now().isoformat(),
            'layer': 'Layer 1 (数据预处理层)',
            'summary': {},
            'issues': [],
            'duplicates': [],
            'responsibility_overlap': [],
            'yaml_issues': [],
            'structure_issues': [],
            'recommendations': []
        }
        
    def scan_layer1_documents(self) -> Dict[str, Dict]:
        """扫描所有Layer 1文档"""
        print("\n" + "="*80)
        print("🔍 扫描Layer 1文档")
        print("="*80)
        
        md_files = list(self.blueprints_dir.glob("*.md"))
        
        for md_file in md_files:
            if md_file.name == "INDEX.md":
                continue
            
            doc_info = self._extract_doc_info(md_file)
            
            # 只处理Layer 1文档
            if doc_info.get('layer') and 'Layer 1' in doc_info['layer']:
                self.layer1_docs[md_file.name] = doc_info
                print(f"  ✓ {md_file.name}: {doc_info.get('layer', 'Unknown')}")
        
        print(f"\n找到 {len(self.layer1_docs)} 个Layer 1文档")
        
        return self.layer1_docs
    
    def _extract_doc_info(self, doc_path: Path) -> Dict:
        """从文档中提取完整信息"""
        doc_info = {
            'file_name': doc_path.name,
            'file_path': str(doc_path),
            'module_id': None,
            'layer': None,
            'title': None,
            'version': None,
            'status': None,
            'responsibility': None,
            'content_hash': None,
            'content_length': 0,
            'yaml_complete': False,
            'has_responsibility_section': False,
            'has_cross_references': False,
            'sections': [],
            'keywords': [],
            'similar_docs': [],
            'issues': []
        }
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_info['content_length'] = len(content)
            doc_info['content_hash'] = hashlib.md5(content.encode()).hexdigest()
            
            # 提取YAML头部
            yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # 提取各个字段
                fields = {
                    'module_id': r'module_id:\s*(.+)',
                    'layer': r'layer:\s*["\']?(.+?)["\']?\s*$',
                    'version': r'version:\s*(.+)',
                    'status': r'status:\s*(.+)'
                }
                
                for field, pattern in fields.items():
                    match = re.search(pattern, yaml_content, re.MULTILINE)
                    if match:
                        doc_info[field] = match.group(1).strip()
                
                # 检查YAML完整性
                required_fields = ['module_id', 'layer', 'version', 'status', 'created_date']
                doc_info['yaml_complete'] = all(
                    re.search(f'{field}:', yaml_content) for field in required_fields
                )
            
            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                doc_info['title'] = title_match.group(1).strip()
            
            # 提取职责描述
            resp_patterns = [
                r'核心定位[：:]\s*(.+?)(?:\n|$)',
                r'单一职责[：:]\s*(.+?)(?:\n|$)',
                r'职责[：:]\s*(.+?)(?:\n|$)',
                r'核心职责[：:]\s*(.+?)(?:\n|$)'
            ]
            
            for pattern in resp_patterns:
                match = re.search(pattern, content)
                if match:
                    doc_info['responsibility'] = match.group(1).strip()
                    break
            
            # 检查职责边界章节
            doc_info['has_responsibility_section'] = bool(
                re.search(r'##\s*.*职责边界', content) or
                re.search(r'##\s*.*职责说明', content) or
                re.search(r'##\s*.*职责定义', content)
            )
            
            # 检查交叉引用
            doc_info['has_cross_references'] = bool(
                re.search(r'##\s*📚\s*相关文档', content) or
                re.search(r'##\s*相关文档', content)
            )
            
            # 提取所有章节
            sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
            doc_info['sections'] = sections
            
            # 提取关键词
            keywords = set()
            keyword_patterns = [
                r'数据预处理',
                r'数据清洗',
                r'数据转换',
                r'数据验证',
                r'数据标准化',
                r'缺失值处理',
                r'异常值检测',
                r'特征工程',
                r'数据质量',
                r'数据源'
            ]
            
            for pattern in keyword_patterns:
                if pattern in content:
                    keywords.add(pattern)
            
            doc_info['keywords'] = list(keywords)
        
        except Exception as e:
            doc_info['issues'].append(f"读取文档时出错: {str(e)}")
        
        return doc_info
    
    def audit_responsibility_clarity(self) -> List[Dict]:
        """审计职责清晰度"""
        print("\n" + "="*80)
        print("📋 审计职责清晰度")
        print("="*80)
        
        issues = []
        
        for doc_name, doc_info in self.layer1_docs.items():
            doc_issues = []
            
            # 检查职责描述是否存在
            if not doc_info.get('responsibility'):
                issue = {
                    'document': doc_name,
                    'issue_type': '职责缺失',
                    'severity': '高',
                    'description': '文档缺少明确的职责描述',
                    'recommendation': '添加清晰的职责描述，说明文档的核心功能'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            # 检查职责描述是否过短
            elif len(doc_info['responsibility']) < 10:
                issue = {
                    'document': doc_name,
                    'issue_type': '职责不清',
                    'severity': '中',
                    'description': f'职责描述过短: "{doc_info["responsibility"]}"',
                    'recommendation': '扩充职责描述，使其更加具体和清晰'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            # 检查是否有职责边界章节
            if not doc_info.get('has_responsibility_section'):
                issue = {
                    'document': doc_name,
                    'issue_type': '职责边界缺失',
                    'severity': '中',
                    'description': '文档缺少职责边界说明章节',
                    'recommendation': '添加职责边界章节，明确文档的职责范围'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            if doc_issues:
                print(f"\n  ❌ {doc_name}:")
                for issue in doc_issues:
                    print(f"     - [{issue['severity']}] {issue['issue_type']}: {issue['description']}")
            else:
                print(f"  ✓ {doc_name}: 职责清晰")
        
        self.audit_results['responsibility_issues'] = issues
        print(f"\n发现 {len(issues)} 个职责清晰度问题")
        
        return issues
    
    def detect_duplicates(self) -> List[Dict]:
        """检测重复文档"""
        print("\n" + "="*80)
        print("🔍 检测重复文档")
        print("="*80)
        
        duplicates = []
        
        # 基于内容哈希检测完全重复
        hash_groups = defaultdict(list)
        for doc_name, doc_info in self.layer1_docs.items():
            hash_groups[doc_info['content_hash']].append(doc_name)
        
        for hash_val, docs in hash_groups.items():
            if len(docs) > 1:
                duplicate = {
                    'type': '完全重复',
                    'severity': '高',
                    'documents': docs,
                    'description': f'{len(docs)}个文档内容完全相同',
                    'recommendation': '保留一个文档，删除其他重复文档'
                }
                duplicates.append(duplicate)
                print(f"\n  ❌ 发现完全重复的文档:")
                for doc in docs:
                    print(f"     - {doc}")
        
        # 基于职责描述检测相似文档
        resp_groups = defaultdict(list)
        for doc_name, doc_info in self.layer1_docs.items():
            if doc_info.get('responsibility'):
                # 标准化职责描述
                resp_normalized = doc_info['responsibility'].lower().strip()
                resp_groups[resp_normalized].append(doc_name)
        
        for resp, docs in resp_groups.items():
            if len(docs) > 1:
                duplicate = {
                    'type': '职责重复',
                    'severity': '高',
                    'documents': docs,
                    'description': f'{len(docs)}个文档职责描述相同: "{resp}"',
                    'recommendation': '合并重复职责的文档，或明确区分职责'
                }
                duplicates.append(duplicate)
                print(f"\n  ❌ 发现职责重复的文档:")
                for doc in docs:
                    print(f"     - {doc}")
                print(f"     职责: {resp}")
        
        # 基于关键词检测相似文档
        keyword_groups = defaultdict(list)
        for doc_name, doc_info in self.layer1_docs.items():
            if doc_info['keywords']:
                key = tuple(sorted(doc_info['keywords']))
                if len(key) >= 3:  # 至少3个关键词相同
                    keyword_groups[key].append(doc_name)
        
        for keywords, docs in keyword_groups.items():
            if len(docs) > 1:
                duplicate = {
                    'type': '功能相似',
                    'severity': '中',
                    'documents': docs,
                    'description': f'{len(docs)}个文档关键词高度相似: {", ".join(keywords)}',
                    'recommendation': '检查是否需要合并或明确区分'
                }
                duplicates.append(duplicate)
                print(f"\n  ⚠️  发现功能相似的文档:")
                for doc in docs:
                    print(f"     - {doc}")
                print(f"     关键词: {', '.join(keywords)}")
        
        self.audit_results['duplicates'] = duplicates
        print(f"\n发现 {len(duplicates)} 组重复文档")
        
        return duplicates
    
    def audit_yaml_completeness(self) -> List[Dict]:
        """审计YAML头部完整性"""
        print("\n" + "="*80)
        print("📝 审计YAML头部完整性")
        print("="*80)
        
        issues = []
        
        required_fields = ['module_id', 'layer', 'version', 'status', 'created_date', 'owner']
        
        for doc_name, doc_info in self.layer1_docs.items():
            doc_issues = []
            
            # 检查YAML是否存在
            yaml_match = re.search(r'^---\n(.*?)\n---', 
                                   open(doc_info['file_path'], 'r', encoding='utf-8').read(), 
                                   re.DOTALL)
            
            if not yaml_match:
                issue = {
                    'document': doc_name,
                    'issue_type': 'YAML缺失',
                    'severity': '高',
                    'description': '文档缺少YAML头部',
                    'recommendation': '添加标准YAML头部'
                }
                doc_issues.append(issue)
                issues.append(issue)
            else:
                yaml_content = yaml_match.group(1)
                
                # 检查必需字段
                for field in required_fields:
                    if not re.search(f'{field}:', yaml_content):
                        issue = {
                            'document': doc_name,
                            'issue_type': f'缺少{field}',
                            'severity': '中',
                            'description': f'YAML头部缺少{field}字段',
                            'recommendation': f'添加{field}字段'
                        }
                        doc_issues.append(issue)
                        issues.append(issue)
            
            if doc_issues:
                print(f"\n  ❌ {doc_name}:")
                for issue in doc_issues:
                    print(f"     - [{issue['severity']}] {issue['issue_type']}")
            else:
                print(f"  ✓ {doc_name}: YAML完整")
        
        self.audit_results['yaml_issues'] = issues
        print(f"\n发现 {len(issues)} 个YAML问题")
        
        return issues
    
    def audit_document_structure(self) -> List[Dict]:
        """审计文档结构规范性"""
        print("\n" + "="*80)
        print("📐 审计文档结构规范性")
        print("="*80)
        
        issues = []
        
        # 标准章节结构
        standard_sections = [
            '概述', '模块概述', '核心定位',
            '功能设计', '架构设计', '技术实现',
            '接口定义', '数据模型',
            '变更历史', '文档治理'
        ]
        
        for doc_name, doc_info in self.layer1_docs.items():
            doc_issues = []
            
            # 检查章节结构
            sections = doc_info.get('sections', [])
            
            # 检查是否有概述章节
            has_overview = any('概述' in s or '模块概述' in s or '核心定位' in s for s in sections)
            if not has_overview:
                issue = {
                    'document': doc_name,
                    'issue_type': '缺少概述章节',
                    'severity': '中',
                    'description': '文档缺少概述或核心定位章节',
                    'recommendation': '添加概述章节，说明模块的核心功能'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            # 检查是否有变更历史
            has_changelog = any('变更历史' in s or '版本历史' in s for s in sections)
            if not has_changelog:
                issue = {
                    'document': doc_name,
                    'issue_type': '缺少变更历史',
                    'severity': '低',
                    'description': '文档缺少变更历史章节',
                    'recommendation': '添加变更历史章节，记录文档变更'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            # 检查是否有文档治理章节
            has_governance = any('文档治理' in s for s in sections)
            if not has_governance:
                issue = {
                    'document': doc_name,
                    'issue_type': '缺少文档治理章节',
                    'severity': '低',
                    'description': '文档缺少文档治理章节',
                    'recommendation': '添加文档治理章节'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            # 检查是否有交叉引用
            if not doc_info.get('has_cross_references'):
                issue = {
                    'document': doc_name,
                    'issue_type': '缺少交叉引用',
                    'severity': '中',
                    'description': '文档缺少交叉引用章节',
                    'recommendation': '添加相关文档章节，说明上下游依赖'
                }
                doc_issues.append(issue)
                issues.append(issue)
            
            if doc_issues:
                print(f"\n  ❌ {doc_name}:")
                for issue in doc_issues:
                    print(f"     - [{issue['severity']}] {issue['issue_type']}")
            else:
                print(f"  ✓ {doc_name}: 结构规范")
        
        self.audit_results['structure_issues'] = issues
        print(f"\n发现 {len(issues)} 个结构问题")
        
        return issues
    
    def check_responsibility_overlap(self) -> List[Dict]:
        """检查职责重叠"""
        print("\n" + "="*80)
        print("🔍 检查职责重叠")
        print("="*80)
        
        overlaps = []
        
        # 提取所有职责关键词
        responsibility_keywords = defaultdict(list)
        
        for doc_name, doc_info in self.layer1_docs.items():
            if doc_info.get('responsibility'):
                # 提取关键词
                keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', doc_info['responsibility'])
                for keyword in keywords:
                    if len(keyword) >= 2:
                        responsibility_keywords[keyword].append(doc_name)
        
        # 检查重叠
        for keyword, docs in responsibility_keywords.items():
            if len(docs) > 1:
                overlap = {
                    'keyword': keyword,
                    'documents': docs,
                    'description': f'{len(docs)}个文档的职责都涉及"{keyword}"',
                    'recommendation': '检查这些文档是否职责重叠，需要合并或明确区分'
                }
                overlaps.append(overlap)
                print(f"\n  ⚠️  关键词 '{keyword}' 出现在多个文档:")
                for doc in docs:
                    print(f"     - {doc}")
        
        self.audit_results['responsibility_overlap'] = overlaps
        print(f"\n发现 {len(overlaps)} 个职责重叠")
        
        return overlaps
    
    def generate_summary(self) -> Dict:
        """生成审计摘要"""
        total_issues = (
            len(self.audit_results.get('responsibility_issues', [])) +
            len(self.audit_results.get('duplicates', [])) +
            len(self.audit_results.get('yaml_issues', [])) +
            len(self.audit_results.get('structure_issues', []))
        )
        
        high_severity = sum(
            1 for issue in (
                self.audit_results.get('responsibility_issues', []) +
                self.audit_results.get('yaml_issues', []) +
                self.audit_results.get('structure_issues', [])
            ) if issue.get('severity') == '高'
        )
        
        summary = {
            'total_documents': len(self.layer1_docs),
            'total_issues': total_issues,
            'high_severity_issues': high_severity,
            'responsibility_issues': len(self.audit_results.get('responsibility_issues', [])),
            'duplicate_groups': len(self.audit_results.get('duplicates', [])),
            'yaml_issues': len(self.audit_results.get('yaml_issues', [])),
            'structure_issues': len(self.audit_results.get('structure_issues', [])),
            'overlap_count': len(self.audit_results.get('responsibility_overlap', [])),
            'compliance_rate': f"{((len(self.layer1_docs) * 10 - total_issues) / (len(self.layer1_docs) * 10) * 100):.2f}%" if self.layer1_docs else "0%"
        }
        
        self.audit_results['summary'] = summary
        
        return summary
    
    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于审计结果生成建议
        if self.audit_results.get('duplicates'):
            recommendations.append("## 🔴 高优先级建议")
            recommendations.append("")
            recommendations.append("### 1. 处理重复文档")
            recommendations.append("- 识别并删除完全重复的文档")
            recommendations.append("- 合并职责相似的文档")
            recommendations.append("- 明确区分功能相似但职责不同的文档")
            recommendations.append("")
        
        if self.audit_results.get('responsibility_issues'):
            recommendations.append("### 2. 明确职责定义")
            recommendations.append("- 为缺少职责描述的文档添加清晰的职责说明")
            recommendations.append("- 扩充过短的职责描述")
            recommendations.append("- 添加职责边界章节，明确文档范围")
            recommendations.append("")
        
        if self.audit_results.get('yaml_issues'):
            recommendations.append("## 🟡 中优先级建议")
            recommendations.append("")
            recommendations.append("### 3. 完善YAML头部")
            recommendations.append("- 为缺少YAML的文档添加标准头部")
            recommendations.append("- 补充缺失的必需字段")
            recommendations.append("- 确保YAML格式规范")
            recommendations.append("")
        
        if self.audit_results.get('structure_issues'):
            recommendations.append("### 4. 规范文档结构")
            recommendations.append("- 添加缺失的概述章节")
            recommendations.append("- 添加变更历史记录")
            recommendations.append("- 添加文档治理章节")
            recommendations.append("- 添加交叉引用章节")
            recommendations.append("")
        
        if self.audit_results.get('responsibility_overlap'):
            recommendations.append("## 🟢 低优先级建议")
            recommendations.append("")
            recommendations.append("### 5. 解决职责重叠")
            recommendations.append("- 检查职责重叠的文档")
            recommendations.append("- 明确各文档的职责边界")
            recommendations.append("- 避免职责分散或重叠")
            recommendations.append("")
        
        self.audit_results['recommendations'] = recommendations
        
        return recommendations
    
    def print_report(self):
        """打印审计报告"""
        summary = self.generate_summary()
        
        print("\n" + "="*80)
        print("📊 Layer 1 数据预处理层深度审计报告")
        print("="*80)
        
        print(f"\n扫描时间: {self.audit_results['scan_time']}")
        print(f"审计层级: {self.audit_results['layer']}")
        
        print("\n## 📈 审计摘要")
        print(f"- 文档总数: {summary['total_documents']}")
        print(f"- 问题总数: {summary['total_issues']}")
        print(f"- 高严重度问题: {summary['high_severity_issues']}")
        print(f"- 职责问题: {summary['responsibility_issues']}")
        print(f"- 重复文档组: {summary['duplicate_groups']}")
        print(f"- YAML问题: {summary['yaml_issues']}")
        print(f"- 结构问题: {summary['structure_issues']}")
        print(f"- 职责重叠: {summary['overlap_count']}")
        print(f"- 合规率: {summary['compliance_rate']}")
        
        # 打印建议
        recommendations = self.generate_recommendations()
        print("\n" + "="*80)
        print("💡 改进建议")
        print("="*80)
        for line in recommendations:
            print(line)
        
        print("\n" + "="*80)
    
    def save_report(self, output_path: str):
        """保存审计报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n审计报告已保存到: {output_path}")
    
    def create_git_backup(self, backup_message: str = "backup: Layer 1深度审计前备份"):
        """创建Git备份"""
        if not self.backup:
            return
        
        print("\n" + "="*80)
        print("💾 创建Git备份")
        print("="*80)
        
        try:
            # 添加所有更改
            subprocess.run(['git', 'add', '-A'], cwd=self.blueprints_dir.parent.parent.parent, check=True)
            
            # 创建提交
            subprocess.run(['git', 'commit', '--no-verify', '-m', backup_message], 
                         cwd=self.blueprints_dir.parent.parent.parent, check=True)
            
            print("✓ Git备份创建成功")
        except subprocess.CalledProcessError as e:
            print(f"✗ Git备份创建失败: {e}")
    
    def run_full_audit(self) -> Dict:
        """执行完整审计"""
        print("\n" + "="*80)
        print("🔍 Layer 1 数据预处理层深度审计")
        print("="*80)
        
        # 创建备份
        self.create_git_backup()
        
        # 执行审计
        self.scan_layer1_documents()
        self.audit_responsibility_clarity()
        self.detect_duplicates()
        self.audit_yaml_completeness()
        self.audit_document_structure()
        self.check_responsibility_overlap()
        
        # 生成报告
        self.print_report()
        
        return self.audit_results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 1数据预处理层深度审计')
    parser.add_argument('--output', '-o', type=str, 
                       default='reports/layer1_deep_audit_report.json',
                       help='输出报告文件路径')
    parser.add_argument('--backup', '-b', action='store_true',
                       help='审计前创建Git备份')
    parser.add_argument('--blueprints-dir', type=str, 
                       default='docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS',
                       help='蓝图文档目录路径')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    blueprints_dir = project_root / args.blueprints_dir
    
    # 创建审计器
    auditor = Layer1DeepAuditor(str(blueprints_dir), backup=args.backup)
    
    # 执行审计
    results = auditor.run_full_audit()
    
    # 保存报告
    output_path = project_root / args.output
    auditor.save_report(str(output_path))


if __name__ == '__main__':
    main()
