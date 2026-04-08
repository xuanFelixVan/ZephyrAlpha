#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人机交互层深度审计脚本
基于专业量化机构五大原则和三层审计标准
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class HumanAILayerDeepAuditor:
    def __init__(self):
        self.layer_path = Path('docs/08_HUMAN_AI_INTERFACE')
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'l1_file_system': {},
            'l2_document_content': {},
            'l3_professional_standard': {},
            'summary': {}
        }
        self.issues = {
            'critical': [],  # P0级问题
            'high': [],      # P1级问题
            'medium': [],    # P2级问题
            'low': []        # P3级问题
        }
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        print("🔍 执行L1文件系统层审计...")
        
        l1_results = {
            'directory_structure': self._check_directory_structure(),
            'file_naming': self._check_file_naming(),
            'path_references': self._check_path_references()
        }
        
        self.results['l1_file_system'] = l1_results
        return l1_results
    
    def _check_directory_structure(self):
        """检查目录结构"""
        issues = []
        
        # 检查空目录
        for directory in self.layer_path.rglob('*'):
            if directory.is_dir():
                files = list(directory.glob('*.md'))
                if len(files) == 0:
                    issues.append({
                        'type': 'empty_directory',
                        'path': str(directory.relative_to(self.layer_path)),
                        'severity': 'medium',
                        'description': '空目录，应删除或添加内容'
                    })
                elif len(files) < 3:
                    issues.append({
                        'type': 'sparse_directory',
                        'path': str(directory.relative_to(self.layer_path)),
                        'file_count': len(files),
                        'severity': 'low',
                        'description': f'稀疏目录，仅{len(files)}个文件'
                    })
        
        # 检查目录层级深度
        for md_file in self.layer_path.rglob('*.md'):
            depth = len(md_file.relative_to(self.layer_path).parts)
            if depth > 4:
                issues.append({
                    'type': 'deep_nesting',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'depth': depth,
                    'severity': 'medium',
                    'description': f'目录层级过深({depth}层)，难以导航'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_file_naming(self):
        """检查文件命名"""
        issues = []
        
        for md_file in self.layer_path.rglob('*.md'):
            filename = md_file.name
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', filename):
                issues.append({
                    'type': 'special_characters',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'medium',
                    'description': '文件名包含空格或中文字符'
                })
            
            # 检查命名一致性
            if not re.match(r'^[A-Z_0-9]+\.md$', filename) and filename != 'index.md':
                issues.append({
                    'type': 'naming_inconsistent',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'low',
                    'description': '文件命名不符合标准格式'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_path_references(self):
        """检查路径引用"""
        issues = []
        
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查绝对路径
            abs_paths = re.findall(r'\[([^\]]+)\]\(([A-Z]:\\[^)]+)\)', content)
            if abs_paths:
                issues.append({
                    'type': 'absolute_path',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'count': len(abs_paths),
                    'severity': 'high',
                    'description': f'使用绝对路径{len(abs_paths)}个'
                })
            
            # 检查过多的../
            deep_refs = re.findall(r'\.\.\/\.\.\/\.\.\/\.\.\/', content)
            if deep_refs:
                issues.append({
                    'type': 'redundant_path',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'count': len(deep_refs),
                    'severity': 'medium',
                    'description': f'路径引用冗余{len(deep_refs)}处'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def audit_l2_document_content(self):
        """L2文档内容层审计"""
        print("🔍 执行L2文档内容层审计...")
        
        l2_results = {
            'responsibility_driven': self._check_responsibility_driven(),
            'index_completeness': self._check_index_completeness(),
            'version_isolation': self._check_version_isolation()
        }
        
        self.results['l2_document_content'] = l2_results
        return l2_results
    
    def _check_responsibility_driven(self):
        """检查职责驱动原则"""
        issues = []
        
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查重复的YAML头部
            yaml_count = content.count('---')
            if yaml_count > 2:
                issues.append({
                    'type': 'duplicate_yaml',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'yaml_count': yaml_count // 2,
                    'severity': 'critical',
                    'description': f'发现{yaml_count // 2}个YAML头部，应仅保留1个'
                })
                self.issues['critical'].append({
                    'file': str(md_file.relative_to(self.layer_path)),
                    'issue': '重复的YAML头部',
                    'count': yaml_count // 2
                })
            
            # 检查重复的module_id
            module_ids = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)
            if len(module_ids) > 1:
                issues.append({
                    'type': 'duplicate_module_id',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'module_ids': module_ids,
                    'severity': 'critical',
                    'description': f'发现{len(module_ids)}个module_id，应仅保留1个'
                })
            
            # 检查重复的responsibility字段
            responsibilities = re.findall(r'^responsibility:', content, re.MULTILINE)
            if len(responsibilities) > 1:
                issues.append({
                    'type': 'duplicate_responsibility',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'count': len(responsibilities),
                    'severity': 'high',
                    'description': f'发现{len(responsibilities)}个responsibility字段'
                })
            
            # 检查职责描述是否清晰
            if 'responsibility_boundary' not in content and 'responsibility:' in content:
                issues.append({
                    'type': 'unclear_responsibility',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'medium',
                    'description': '缺少responsibility_boundary字段，职责描述不清晰'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        issues = []
        
        # 检查主索引文件
        main_index = self.layer_path / 'index.md'
        if not main_index.exists():
            issues.append({
                'type': 'missing_main_index',
                'path': '',
                'severity': 'critical',
                'description': '缺少主索引文件index.md'
            })
        else:
            # 检查索引是否列出所有文档
            try:
                with open(main_index, 'r', encoding='utf-8') as f:
                    index_content = f.read()
                
                all_md_files = list(self.layer_path.rglob('*.md'))
                for md_file in all_md_files:
                    if md_file.name != 'index.md':
                        rel_path = str(md_file.relative_to(self.layer_path))
                        if rel_path not in index_content and md_file.name not in index_content:
                            issues.append({
                                'type': 'missing_in_index',
                                'path': rel_path,
                                'severity': 'medium',
                                'description': '文档未在主索引中列出'
                            })
            except Exception:
                pass
        
        # 检查子目录索引
        for directory in self.layer_path.iterdir():
            if directory.is_dir():
                sub_index = directory / 'INDEX.md'
                if not sub_index.exists():
                    issues.append({
                        'type': 'missing_sub_index',
                        'path': str(directory.relative_to(self.layer_path)),
                        'severity': 'high',
                        'description': '子目录缺少INDEX.md索引文件'
                    })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        issues = []
        
        # 检查重复文档
        file_contents = {}
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取标题作为内容标识
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)
                    if title in file_contents:
                        issues.append({
                            'type': 'duplicate_content',
                            'path': str(md_file.relative_to(self.layer_path)),
                            'duplicate_of': file_contents[title],
                            'title': title,
                            'severity': 'high',
                            'description': f'重复文档，与{file_contents[title]}内容相似'
                        })
                    else:
                        file_contents[title] = str(md_file.relative_to(self.layer_path))
            except Exception:
                continue
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def audit_l3_professional_standard(self):
        """L3专业标准层审计"""
        print("🔍 执行L3专业标准层审计...")
        
        l3_results = {
            'five_principles': self._check_five_principles(),
            'document_classification': self._check_document_classification(),
            'numbering_system': self._check_numbering_system(),
            'document_quality': self._check_document_quality()
        }
        
        self.results['l3_professional_standard'] = l3_results
        return l3_results
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        issues = []
        
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查职责驱动原则
            if 'responsibility' not in content.lower() and '职责' not in content:
                issues.append({
                    'type': 'missing_responsibility',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'high',
                    'description': '缺少职责描述，违反职责驱动原则'
                })
            
            # 检查命名规范原则
            filename = md_file.stem
            if not re.match(r'^[A-Z_0-9]+$', filename) and filename != 'index':
                issues.append({
                    'type': 'naming_non_standard',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'medium',
                    'description': '文件命名不符合专业标准'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_document_classification(self):
        """检查文档分类"""
        issues = []
        
        # 检查文档是否放置在正确的分类目录
        for md_file in self.layer_path.rglob('*.md'):
            rel_path = str(md_file.relative_to(self.layer_path))
            
            # 检查是否在正确的子目录中
            if md_file.parent != self.layer_path and md_file.name != 'INDEX.md':
                # 检查文件名是否与目录名匹配
                dir_name = md_file.parent.name
                file_name = md_file.stem
                
                # 如果文件名不包含目录名的关键词，可能是分类错误
                if dir_name.split('_')[0] not in file_name and file_name != 'index':
                    issues.append({
                        'type': 'potential_misclassification',
                        'path': rel_path,
                        'severity': 'low',
                        'description': '文件可能放置在错误的分类目录'
                    })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_numbering_system(self):
        """检查编号体系"""
        issues = []
        module_ids = defaultdict(list)
        
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 提取module_id
            matches = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)
            for module_id in matches:
                module_ids[module_id].append(str(md_file.relative_to(self.layer_path)))
        
        # 检查重复的module_id
        for module_id, files in module_ids.items():
            if len(files) > 1:
                issues.append({
                    'type': 'duplicate_module_id',
                    'module_id': module_id,
                    'files': files,
                    'severity': 'critical',
                    'description': f'module_id重复，出现在{len(files)}个文件中'
                })
                self.issues['critical'].append({
                    'module_id': module_id,
                    'files': files,
                    'issue': 'module_id重复'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def _check_document_quality(self):
        """检查文档质量"""
        issues = []
        
        for md_file in self.layer_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查YAML头部
            if not content.strip().startswith('---'):
                issues.append({
                    'type': 'missing_yaml_header',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'high',
                    'description': '缺少YAML元数据头部'
                })
            else:
                # 检查必需字段
                required_fields = ['version', 'module_id']
                for field in required_fields:
                    if f'{field}:' not in content[:500]:  # 只检查前500字符（YAML头部区域）
                        issues.append({
                            'type': 'missing_required_field',
                            'path': str(md_file.relative_to(self.layer_path)),
                            'field': field,
                            'severity': 'medium',
                            'description': f'YAML头部缺少必需字段: {field}'
                        })
            
            # 检查文档结构
            if not re.search(r'^#\s+', content, re.MULTILINE):
                issues.append({
                    'type': 'missing_title',
                    'path': str(md_file.relative_to(self.layer_path)),
                    'severity': 'high',
                    'description': '文档缺少标题'
                })
        
        return {'issues': issues, 'total_issues': len(issues)}
    
    def generate_report(self):
        """生成审计报告"""
        output_dir = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_dir / f'HUMAN_AI_LAYER_DEEP_AUDIT_{timestamp}.md'
        json_file = output_dir / f'HUMAN_AI_LAYER_DEEP_AUDIT_{timestamp}.json'
        
        # 统计问题数量
        total_issues = sum([
            self.results['l1_file_system'].get('directory_structure', {}).get('total_issues', 0),
            self.results['l1_file_system'].get('file_naming', {}).get('total_issues', 0),
            self.results['l1_file_system'].get('path_references', {}).get('total_issues', 0),
            self.results['l2_document_content'].get('responsibility_driven', {}).get('total_issues', 0),
            self.results['l2_document_content'].get('index_completeness', {}).get('total_issues', 0),
            self.results['l2_document_content'].get('version_isolation', {}).get('total_issues', 0),
            self.results['l3_professional_standard'].get('five_principles', {}).get('total_issues', 0),
            self.results['l3_professional_standard'].get('document_classification', {}).get('total_issues', 0),
            self.results['l3_professional_standard'].get('numbering_system', {}).get('total_issues', 0),
            self.results['l3_professional_standard'].get('document_quality', {}).get('total_issues', 0)
        ])
        
        critical_count = len(self.issues['critical'])
        high_count = len(self.issues['high'])
        medium_count = len(self.issues['medium'])
        low_count = len(self.issues['low'])
        
        # 生成Markdown报告
        report_lines = [
            "# 人机交互层深度审计报告",
            "",
            f"> **审计时间**: {self.results['scan_time']}",
            f"> **审计范围**: docs/08_HUMAN_AI_INTERFACE",
            f"> **审计标准**: 专业量化机构五大原则 + 三层审计标准",
            "",
            "---",
            "",
            "## 📊 审计概要",
            "",
            f"- **总问题数**: {total_issues}",
            f"- **P0级问题（严重）**: {critical_count}",
            f"- **P1级问题（高）**: {high_count}",
            f"- **P2级问题（中）**: {medium_count}",
            f"- **P3级问题（低）**: {low_count}",
            ""
        ]
        
        # P0级问题
        if self.issues['critical']:
            report_lines.extend([
                "---",
                "",
                "## 🔴 P0级问题（严重 - 立即修复）",
                ""
            ])
            for i, issue in enumerate(self.issues['critical'], 1):
                report_lines.append(f"### 问题{i}: {issue.get('issue', '未知问题')}")
                if 'file' in issue:
                    report_lines.append(f"- **文件**: {issue['file']}")
                if 'module_id' in issue:
                    report_lines.append(f"- **module_id**: {issue['module_id']}")
                if 'files' in issue:
                    report_lines.append(f"- **涉及文件**: {', '.join(issue['files'])}")
                if 'count' in issue:
                    report_lines.append(f"- **数量**: {issue['count']}")
                report_lines.append("")
        
        # L1审计结果
        report_lines.extend([
            "---",
            "",
            "## 🔴 L1 文件系统层审计结果",
            ""
        ])
        
        for category, data in self.results['l1_file_system'].items():
            report_lines.append(f"### {category}")
            report_lines.append(f"- **问题数**: {data.get('total_issues', 0)}")
            if data.get('issues'):
                report_lines.append("")
                for issue in data['issues'][:10]:
                    report_lines.append(f"- [{issue['severity'].upper()}] {issue['path']}: {issue['description']}")
            report_lines.append("")
        
        # L2审计结果
        report_lines.extend([
            "---",
            "",
            "## 🟡 L2 文档内容层审计结果",
            ""
        ])
        
        for category, data in self.results['l2_document_content'].items():
            report_lines.append(f"### {category}")
            report_lines.append(f"- **问题数**: {data.get('total_issues', 0)}")
            if data.get('issues'):
                report_lines.append("")
                for issue in data['issues'][:10]:
                    report_lines.append(f"- [{issue['severity'].upper()}] {issue['path']}: {issue['description']}")
            report_lines.append("")
        
        # L3审计结果
        report_lines.extend([
            "---",
            "",
            "## 🟢 L3 专业标准层审计结果",
            ""
        ])
        
        for category, data in self.results['l3_professional_standard'].items():
            report_lines.append(f"### {category}")
            report_lines.append(f"- **问题数**: {data.get('total_issues', 0)}")
            if data.get('issues'):
                report_lines.append("")
                for issue in data['issues'][:10]:
                    report_lines.append(f"- [{issue['severity'].upper()}] {issue['path']}: {issue['description']}")
            report_lines.append("")
        
        # 改进建议
        report_lines.extend([
            "---",
            "",
            "## 💡 改进建议",
            "",
            "### 立即修复（P0级）",
            ""
        ])
        
        if self.issues['critical']:
            for issue in self.issues['critical']:
                if '重复的YAML头部' in issue.get('issue', ''):
                    report_lines.append("- 删除重复的YAML头部，仅保留一个完整的YAML元数据块")
                elif 'module_id重复' in issue.get('issue', ''):
                    report_lines.append("- 为重复的module_id分配唯一标识符")
        
        report_lines.extend([
            "",
            "### 短期修复（P1级）",
            "",
            "- 为缺少INDEX.md的子目录创建索引文件",
            "- 补充缺失的responsibility_boundary字段",
            "- 修复绝对路径引用",
            "",
            "### 中期优化（P2级）",
            "",
            "- 统一文件命名格式",
            "- 清理稀疏目录",
            "- 优化路径引用结构",
            "",
            "### 长期改进（P3级）",
            "",
            "- 建立文档创建审核流程",
            "- 定期执行质量检查",
            "- 持续优化文档结构",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        # 保存JSON结果
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 审计报告已生成: {report_file}")
        print(f"✅ JSON结果已保存: {json_file}")
        
        return report_file
    
    def run(self):
        """执行完整审计"""
        print("=" * 60)
        print("人机交互层深度审计")
        print("=" * 60)
        
        self.audit_l1_file_system()
        self.audit_l2_document_content()
        self.audit_l3_professional_standard()
        
        print("\n" + "=" * 60)
        print("审计完成!")
        print("=" * 60)
        
        self.generate_report()

if __name__ == '__main__':
    auditor = HumanAILayerDeepAuditor()
    auditor.run()
