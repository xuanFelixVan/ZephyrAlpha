#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
人机交互层深度审计脚本
执行L1、L2、L3三层审计，重点检查重复内容和职责不清问题
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class HumanAIDeepAuditor:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.audit_results = {
            'L1': {
                'directory_structure': [],
                'file_naming': [],
                'path_references': []
            },
            'L2': {
                'responsibility': [],
                'index_completeness': [],
                'version_isolation': [],
                'doc_code_mapping': []
            },
            'L3': {
                'five_principles': [],
                'classification': [],
                'numbering': [],
                'quality': []
            },
            'duplicates': [],
            'unclear_responsibilities': []
        }
        self.stats = {
            'total_files': 0,
            'total_directories': 0,
            'issues_found': 0,
            'critical_issues': 0
        }
    
    def run_full_audit(self):
        """执行完整的三层审计"""
        print("=" * 80)
        print("人机交互层深度审计")
        print("=" * 80)
        print(f"审计范围: {self.layer_path}")
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # L1 文件系统层审计
        print("🔍 执行L1文件系统层审计...")
        self.audit_l1_file_system()
        
        # L2 文档内容层审计
        print("🔍 执行L2文档内容层审计...")
        self.audit_l2_content()
        
        # L3 专业标准层审计
        print("🔍 执行L3专业标准层审计...")
        self.audit_l3_standard()
        
        # 重点检查重复内容和职责不清
        print("🔍 重点检查重复内容和职责不清问题...")
        self.check_duplicates_and_responsibilities()
        
        # 生成审计报告
        print("📝 生成审计报告...")
        self.generate_report()
        
        print()
        print("=" * 80)
        print("审计完成！")
        print("=" * 80)
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        # 1.1 目录结构问题
        self.check_directory_structure()
        
        # 1.2 文件命名问题
        self.check_file_naming()
        
        # 1.3 路径引用问题
        self.check_path_references()
    
    def check_directory_structure(self):
        """检查目录结构问题"""
        print("  - 检查目录结构...")
        
        # 检查目录漂移
        expected_dirs = [f"{i:02d}_{name}" for i, name in enumerate([
            'MONITORING', 'ALERTING', 'AUTH', 'API_DOCS', 'BACKTEST_UI',
            'REPORTING', 'AUDIT_LOG', 'MOBILE_PUSH', 'TRADING_JOURNAL',
            'CONFIG_MANAGEMENT', 'USER_PREFERENCES', 'SYSTEM_STATUS',
            'DATA_MANAGEMENT', 'STRATEGY_MANAGEMENT', 'PERMISSION_MANAGEMENT',
            'API_RATE_LIMITING', 'DOCUMENTATION_CENTER', 'KNOWLEDGE_BASE',
            'CI_CD_INTEGRATION', 'DATA_BACKUP', 'ONLINE_RESEARCH_ENVIRONMENT',
            'PARAMETER_OPTIMIZATION', 'LIVE_TRADING_INTERFACE'
        ], 1)]
        
        actual_dirs = [d.name for d in self.layer_path.iterdir() if d.is_dir()]
        
        # 检查目录稀疏（文件数<3）
        for dir_path in self.layer_path.iterdir():
            if dir_path.is_dir():
                file_count = len(list(dir_path.glob('*.md')))
                if file_count < 3:
                    self.audit_results['L1']['directory_structure'].append({
                        'type': '目录稀疏',
                        'directory': dir_path.name,
                        'file_count': file_count,
                        'severity': 'P2',
                        'description': f"目录下文件过少（{file_count}个），建议整合"
                    })
        
        # 检查空目录
        for dir_path in self.layer_path.iterdir():
            if dir_path.is_dir():
                if not list(dir_path.glob('*.md')):
                    self.audit_results['L1']['directory_structure'].append({
                        'type': '空目录',
                        'directory': dir_path.name,
                        'severity': 'P1',
                        'description': '目录存在但无内容'
                    })
        
        # 检查目录命名规范
        for dir_name in actual_dirs:
            if not re.match(r'^\d{2}_[A-Z_]+$', dir_name):
                self.audit_results['L1']['directory_structure'].append({
                    'type': '目录命名不规范',
                    'directory': dir_name,
                    'severity': 'P2',
                    'description': '不符合专业命名标准（应为XX_MODULE_NAME格式）'
                })
        
        self.stats['total_directories'] = len(actual_dirs)
    
    def check_file_naming(self):
        """检查文件命名问题"""
        print("  - 检查文件命名...")
        
        all_files = list(self.layer_path.rglob('*.md'))
        self.stats['total_files'] = len(all_files)
        
        for file_path in all_files:
            file_name = file_path.name
            
            # 检查旧架构命名残留
            if 'Layer' in file_name or 'layer' in file_name:
                self.audit_results['L1']['file_naming'].append({
                    'type': '旧架构命名残留',
                    'file': str(file_path.relative_to(self.layer_path)),
                    'severity': 'P1',
                    'description': '文件名包含Layer关键词'
                })
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', file_name):
                self.audit_results['L1']['file_naming'].append({
                    'type': '特殊字符问题',
                    'file': str(file_path.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': '文件名包含空格或中文'
                })
            
            # 检查BLUEPRINT文件命名
            if 'BLUEPRINT' in file_name and not re.match(r'^[A-Z_]+_BLUEPRINT\.md$', file_name):
                self.audit_results['L1']['file_naming'].append({
                    'type': 'BLUEPRINT命名不规范',
                    'file': str(file_path.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': 'BLUEPRINT文件命名不符合标准'
                })
    
    def check_path_references(self):
        """检查路径引用问题"""
        print("  - 检查路径引用...")
        
        all_files = list(self.layer_path.rglob('*.md'))
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查路径冗余（过多的../）
                redundant_paths = re.findall(r'\.\./\.\./\.\./', content)
                if redundant_paths:
                    self.audit_results['L1']['path_references'].append({
                        'type': '路径冗余',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': f'使用过多的../相对路径（{len(redundant_paths)}处）'
                    })
                
                # 检查死链接
                links = re.findall(r'\[.*?\]\((.*?)\)', content)
                for link in links:
                    if link.startswith('http') or link.startswith('#'):
                        continue
                    
                    # 解析相对路径
                    target_path = file_path.parent / link
                    if not target_path.exists():
                        self.audit_results['L1']['path_references'].append({
                            'type': '死链接',
                            'file': str(file_path.relative_to(self.layer_path)),
                            'severity': 'P1',
                            'description': f'链接指向不存在的文件: {link}'
                        })
            
            except Exception as e:
                pass
    
    def audit_l2_content(self):
        """L2文档内容层审计"""
        # 2.1 职责驱动原则
        self.check_responsibility()
        
        # 2.2 索引完备性
        self.check_index_completeness()
        
        # 2.3 版本隔离
        self.check_version_isolation()
        
        # 2.4 文档代码对应
        self.check_doc_code_mapping()
    
    def check_responsibility(self):
        """检查职责驱动原则"""
        print("  - 检查职责驱动原则...")
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for file_path in blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查YAML头部是否有responsibility字段
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    if 'responsibility:' not in yaml_content:
                        self.audit_results['L2']['responsibility'].append({
                            'type': '职责描述缺失',
                            'file': str(file_path.relative_to(self.layer_path)),
                            'severity': 'P1',
                            'description': 'YAML头部缺少responsibility字段'
                        })
                    else:
                        # 检查职责描述是否清晰
                        responsibility_match = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', yaml_content)
                        if responsibility_match:
                            responsibilities = responsibility_match.group(1).strip()
                            if len(responsibilities) < 20:
                                self.audit_results['L2']['responsibility'].append({
                                    'type': '职责描述模糊',
                                    'file': str(file_path.relative_to(self.layer_path)),
                                    'severity': 'P2',
                                    'description': '职责描述过于简短，建议详细说明'
                                })
            
            except Exception as e:
                pass
    
    def check_index_completeness(self):
        """检查索引完备性"""
        print("  - 检查索引完备性...")
        
        # 检查根目录INDEX.md
        root_index = self.layer_path / 'index.md'
        if not root_index.exists():
            self.audit_results['L2']['index_completeness'].append({
                'type': '根目录缺索引',
                'file': 'index.md',
                'severity': 'P0',
                'description': '根目录缺少INDEX.md主入口'
            })
        
        # 检查子目录INDEX.md
        for dir_path in self.layer_path.iterdir():
            if dir_path.is_dir():
                index_file = dir_path / 'INDEX.md'
                if not index_file.exists():
                    self.audit_results['L2']['index_completeness'].append({
                        'type': '子目录缺索引',
                        'file': str(dir_path.relative_to(self.layer_path)),
                        'severity': 'P1',
                        'description': '子目录缺少INDEX.md导航文件'
                    })
                else:
                    # 检查索引是否完整
                    try:
                        with open(index_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 获取目录下的所有文档
                        actual_docs = [f.name for f in dir_path.glob('*.md') if f.name != 'INDEX.md']
                        
                        # 检查索引中是否包含所有文档
                        for doc in actual_docs:
                            if doc not in content:
                                self.audit_results['L2']['index_completeness'].append({
                                    'type': '索引不完整',
                                    'file': str(index_file.relative_to(self.layer_path)),
                                    'severity': 'P2',
                                    'description': f'索引未列出文档: {doc}'
                                })
                    
                    except Exception as e:
                        pass
    
    def check_version_isolation(self):
        """检查版本隔离"""
        print("  - 检查版本隔离...")
        
        # 检查重复文档
        all_files = list(self.layer_path.rglob('*.md'))
        content_hashes = defaultdict(list)
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 计算内容哈希（简化版：使用前500字符）
                content_hash = hash(content[:500])
                content_hashes[content_hash].append(file_path)
            
            except Exception as e:
                pass
        
        # 检查重复内容
        for content_hash, files in content_hashes.items():
            if len(files) > 1:
                self.audit_results['L2']['version_isolation'].append({
                    'type': '重复文档',
                    'files': [str(f.relative_to(self.layer_path)) for f in files],
                    'severity': 'P1',
                    'description': f'发现{len(files)}个内容相似的文档'
                })
    
    def check_doc_code_mapping(self):
        """检查文档代码对应"""
        print("  - 检查文档代码对应...")
        
        # 检查文档是否描述了不存在的代码模块
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for file_path in blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有过时的架构引用
                if 'Layer 8' in content or 'Layer 7' in content:
                    self.audit_results['L2']['doc_code_mapping'].append({
                        'type': '旧架构引用',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': '文档包含旧架构引用（Layer 7/8）'
                    })
            
            except Exception as e:
                pass
    
    def audit_l3_standard(self):
        """L3专业标准层审计"""
        # 3.1 五大原则符合性
        self.check_five_principles()
        
        # 3.2 文档分类
        self.check_classification()
        
        # 3.3 编号体系
        self.check_numbering()
        
        # 3.4 文档质量
        self.check_quality()
    
    def check_five_principles(self):
        """检查五大原则符合性"""
        print("  - 检查五大原则符合性...")
        
        # 检查职责驱动原则
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for file_path in blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查YAML头部
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not yaml_match:
                    self.audit_results['L3']['five_principles'].append({
                        'type': 'YAML头部缺失',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P1',
                        'description': '文档缺少标准YAML元数据'
                    })
                else:
                    yaml_content = yaml_match.group(1)
                    
                    # 检查必要字段
                    required_fields = ['module_id', 'version', 'status', 'owner']
                    for field in required_fields:
                        if field not in yaml_content:
                            self.audit_results['L3']['five_principles'].append({
                                'type': f'YAML字段缺失',
                                'file': str(file_path.relative_to(self.layer_path)),
                                'severity': 'P2',
                                'description': f'YAML缺少必要字段: {field}'
                            })
            
            except Exception as e:
                pass
    
    def check_classification(self):
        """检查文档分类"""
        print("  - 检查文档分类...")
        
        # 检查文档是否放置在正确的分类目录
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for file_path in blueprint_files:
            # 检查BLUEPRINT文件是否在正确的目录
            parent_dir = file_path.parent.name
            file_prefix = file_path.stem.replace('_BLUEPRINT', '')
            
            if not parent_dir.endswith(file_prefix):
                self.audit_results['L3']['classification'].append({
                    'type': '分类错误',
                    'file': str(file_path.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': f'BLUEPRINT文件放置在错误的目录（应为{file_prefix}）'
                })
    
    def check_numbering(self):
        """检查编号体系"""
        print("  - 检查编号体系...")
        
        all_files = list(self.layer_path.rglob('*.md'))
        module_ids = defaultdict(list)
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取module_id
                module_id_match = re.search(r'module_id:\s*(.+)', content)
                if module_id_match:
                    module_id = module_id_match.group(1).strip()
                    module_ids[module_id].append(file_path)
                else:
                    self.audit_results['L3']['numbering'].append({
                        'type': '编号缺失',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P1',
                        'description': '文档缺少module_id'
                    })
            
            except Exception as e:
                pass
        
        # 检查重复的module_id
        for module_id, files in module_ids.items():
            if len(files) > 1:
                self.audit_results['L3']['numbering'].append({
                    'type': '编号重复',
                    'module_id': module_id,
                    'files': [str(f.relative_to(self.layer_path)) for f in files],
                    'severity': 'P1',
                    'description': f'{len(files)}个文档使用相同的module_id'
                })
    
    def check_quality(self):
        """检查文档质量"""
        print("  - 检查文档质量...")
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for file_path in blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查文档长度
                lines = content.split('\n')
                if len(lines) < 20:
                    self.audit_results['L3']['quality'].append({
                        'type': '文档过短',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': f'文档内容过短（{len(lines)}行），可能不完整'
                    })
                
                # 检查章节结构
                if '## 1.' not in content and '## 一、' not in content:
                    self.audit_results['L3']['quality'].append({
                        'type': '章节结构混乱',
                        'file': str(file_path.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': '文档缺少标准章节结构'
                    })
            
            except Exception as e:
                pass
    
    def check_duplicates_and_responsibilities(self):
        """重点检查重复内容和职责不清问题"""
        print("  - 重点检查重复内容和职责不清问题...")
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        # 收集所有职责描述
        responsibilities = []
        
        for file_path in blueprint_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取职责描述
                responsibility_match = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', content)
                if responsibility_match:
                    resp = responsibility_match.group(1).strip()
                    responsibilities.append({
                        'file': str(file_path.relative_to(self.layer_path)),
                        'responsibility': resp
                    })
                
                # 检查内容重复
                # 提取核心功能描述
                core_func_match = re.search(r'## 1\. 概述\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                if core_func_match:
                    core_func = core_func_match.group(1).strip()
                    
                    # 检查是否有相似的描述
                    for other_file in blueprint_files:
                        if other_file != file_path:
                            with open(other_file, 'r', encoding='utf-8') as f2:
                                other_content = f2.read()
                            
                            other_core_match = re.search(r'## 1\. 概述\s*\n(.*?)(?=\n##|\Z)', other_content, re.DOTALL)
                            if other_core_match:
                                other_core = other_core_match.group(1).strip()
                                
                                # 简单的相似度检查
                                if self.calculate_similarity(core_func, other_core) > 0.7:
                                    self.audit_results['duplicates'].append({
                                        'type': '内容重复',
                                        'files': [
                                            str(file_path.relative_to(self.layer_path)),
                                            str(other_file.relative_to(self.layer_path))
                                        ],
                                        'severity': 'P2',
                                        'description': '两个文档的核心功能描述相似度超过70%'
                                    })
            
            except Exception as e:
                pass
        
        # 检查职责重叠
        for i, resp1 in enumerate(responsibilities):
            for resp2 in responsibilities[i+1:]:
                if self.calculate_similarity(resp1['responsibility'], resp2['responsibility']) > 0.6:
                    self.audit_results['unclear_responsibilities'].append({
                        'type': '职责重叠',
                        'files': [resp1['file'], resp2['file']],
                        'severity': 'P1',
                        'description': '两个文档的职责描述相似度超过60%'
                    })
    
    def calculate_similarity(self, text1, text2):
        """计算文本相似度（简化版）"""
        # 使用简单的词汇重叠度
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_report(self):
        """生成审计报告"""
        report_path = self.layer_path.parent.parent / '05_IMPLEMENTATION' / '04_OPERATIONS' / 'audit_state'
        report_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_path / f'HUMAN_AI_LAYER_DEEP_AUDIT_{timestamp}.md'
        
        # 统计问题数量
        total_issues = 0
        critical_issues = 0
        
        for level in ['L1', 'L2', 'L3']:
            for category in self.audit_results[level]:
                issues = self.audit_results[level][category]
                total_issues += len(issues)
                critical_issues += sum(1 for issue in issues if issue.get('severity') == 'P0')
        
        total_issues += len(self.audit_results['duplicates'])
        total_issues += len(self.audit_results['unclear_responsibilities'])
        
        self.stats['issues_found'] = total_issues
        self.stats['critical_issues'] = critical_issues
        
        # 生成报告内容
        report_content = f"""---
module_id: HUMAN_AI_LAYER_DEEP_AUDIT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档治理系统
standard_type: 审计报告
applicable_scope: 人机交互层文档
compliance_level: 专业标准
---

# 人机交互层深度审计报告

> **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **审计范围**: {self.layer_path}
> **审计标准**: 专业量化机构五大原则 + 三层审计标准

---

## 📊 审计概要

### 总体统计

| 指标 | 数值 |
|------|------|
| **审计文件数** | {self.stats['total_files']} |
| **审计目录数** | {self.stats['total_directories']} |
| **发现问题数** | {self.stats['issues_found']} |
| **严重问题数** | {self.stats['critical_issues']} |

### 问题分布

| 审计层级 | 问题类型 | 问题数量 | 严重问题 |
|---------|---------|---------|---------|
"""
        
        # 添加各层级问题统计
        for level in ['L1', 'L2', 'L3']:
            level_names = {
                'L1': '文件系统层',
                'L2': '文档内容层',
                'L3': '专业标准层'
            }
            
            for category in self.audit_results[level]:
                issues = self.audit_results[level][category]
                if issues:
                    critical = sum(1 for issue in issues if issue.get('severity') == 'P0')
                    report_content += f"| {level_names[level]} | {category} | {len(issues)} | {critical} |\n"
        
        # 添加重复内容和职责不清问题
        if self.audit_results['duplicates']:
            report_content += f"| 重点检查 | 内容重复 | {len(self.audit_results['duplicates'])} | 0 |\n"
        
        if self.audit_results['unclear_responsibilities']:
            report_content += f"| 重点检查 | 职责不清 | {len(self.audit_results['unclear_responsibilities'])} | {sum(1 for issue in self.audit_results['unclear_responsibilities'] if issue.get('severity') == 'P1')} |\n"
        
        report_content += """
---

## 🔴 L1 文件系统层审计结果

"""
        
        # 添加L1审计结果
        for category, issues in self.audit_results['L1'].items():
            if issues:
                report_content += f"### {category}\n\n"
                for issue in issues:
                    severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(issue.get('severity'), '⚪')
                    report_content += f"{severity_icon} **{issue.get('type', 'Unknown')}**\n"
                    report_content += f"   - 文件: `{issue.get('file', 'N/A')}`\n"
                    report_content += f"   - 严重性: {issue.get('severity', 'N/A')}\n"
                    report_content += f"   - 描述: {issue.get('description', 'N/A')}\n\n"
        
        report_content += """
---

## 🟡 L2 文档内容层审计结果

"""
        
        # 添加L2审计结果
        for category, issues in self.audit_results['L2'].items():
            if issues:
                report_content += f"### {category}\n\n"
                for issue in issues:
                    severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(issue.get('severity'), '⚪')
                    report_content += f"{severity_icon} **{issue.get('type', 'Unknown')}**\n"
                    if 'files' in issue:
                        report_content += f"   - 文件: {', '.join(issue['files'])}\n"
                    else:
                        report_content += f"   - 文件: `{issue.get('file', 'N/A')}`\n"
                    report_content += f"   - 严重性: {issue.get('severity', 'N/A')}\n"
                    report_content += f"   - 描述: {issue.get('description', 'N/A')}\n\n"
        
        report_content += """
---

## 🟢 L3 专业标准层审计结果

"""
        
        # 添加L3审计结果
        for category, issues in self.audit_results['L3'].items():
            if issues:
                report_content += f"### {category}\n\n"
                for issue in issues:
                    severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(issue.get('severity'), '⚪')
                    report_content += f"{severity_icon} **{issue.get('type', 'Unknown')}**\n"
                    if 'files' in issue:
                        report_content += f"   - 文件: {', '.join(issue['files'])}\n"
                    else:
                        report_content += f"   - 文件: `{issue.get('file', 'N/A')}`\n"
                    report_content += f"   - 严重性: {issue.get('severity', 'N/A')}\n"
                    report_content += f"   - 描述: {issue.get('description', 'N/A')}\n\n"
        
        report_content += """
---

## 🎯 重点问题：重复内容

"""
        
        # 添加重复内容问题
        if self.audit_results['duplicates']:
            for issue in self.audit_results['duplicates']:
                severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(issue.get('severity'), '⚪')
                report_content += f"{severity_icon} **{issue.get('type', 'Unknown')}**\n"
                report_content += f"   - 文件: {', '.join(issue.get('files', []))}\n"
                report_content += f"   - 严重性: {issue.get('severity', 'N/A')}\n"
                report_content += f"   - 描述: {issue.get('description', 'N/A')}\n\n"
        else:
            report_content += "✅ 未发现明显的重复内容问题\n\n"
        
        report_content += """
---

## 🎯 重点问题：职责不清

"""
        
        # 添加职责不清问题
        if self.audit_results['unclear_responsibilities']:
            for issue in self.audit_results['unclear_responsibilities']:
                severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(issue.get('severity'), '⚪')
                report_content += f"{severity_icon} **{issue.get('type', 'Unknown')}**\n"
                report_content += f"   - 文件: {', '.join(issue.get('files', []))}\n"
                report_content += f"   - 严重性: {issue.get('severity', 'N/A')}\n"
                report_content += f"   - 描述: {issue.get('description', 'N/A')}\n\n"
        else:
            report_content += "✅ 未发现明显的职责不清问题\n\n"
        
        report_content += f"""
---

## 📋 改进建议

### 立即修复（P0）

"""
        
        # 添加P0级问题
        p0_issues = []
        for level in ['L1', 'L2', 'L3']:
            for category, issues in self.audit_results[level].items():
                for issue in issues:
                    if issue.get('severity') == 'P0':
                        p0_issues.append(issue)
        
        if p0_issues:
            for i, issue in enumerate(p0_issues, 1):
                report_content += f"{i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'N/A')}\n"
        else:
            report_content += "✅ 无P0级问题\n"
        
        report_content += """
### 短期改进（P1）

"""
        
        # 添加P1级问题
        p1_issues = []
        for level in ['L1', 'L2', 'L3']:
            for category, issues in self.audit_results[level].items():
                for issue in issues:
                    if issue.get('severity') == 'P1':
                        p1_issues.append(issue)
        
        p1_issues.extend(self.audit_results['unclear_responsibilities'])
        
        if p1_issues:
            for i, issue in enumerate(p1_issues[:10], 1):  # 只显示前10个
                report_content += f"{i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'N/A')}\n"
            if len(p1_issues) > 10:
                report_content += f"... 还有 {len(p1_issues) - 10} 个P1级问题\n"
        else:
            report_content += "✅ 无P1级问题\n"
        
        report_content += """
### 长期优化（P2）

"""
        
        # 添加P2级问题
        p2_issues = []
        for level in ['L1', 'L2', 'L3']:
            for category, issues in self.audit_results[level].items():
                for issue in issues:
                    if issue.get('severity') == 'P2':
                        p2_issues.append(issue)
        
        p2_issues.extend(self.audit_results['duplicates'])
        
        if p2_issues:
            for i, issue in enumerate(p2_issues[:10], 1):  # 只显示前10个
                report_content += f"{i}. {issue.get('type', 'Unknown')}: {issue.get('description', 'N/A')}\n"
            if len(p2_issues) > 10:
                report_content += f"... 还有 {len(p2_issues) - 10} 个P2级问题\n"
        else:
            report_content += "✅ 无P2级问题\n"
        
        report_content += f"""
---

## 📚 相关文档

- [专业文档治理审计指南](../../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
- [文档治理审计检查清单](../../09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
- [文档版本号命名标准](../../09_AUDIT/STANDARDS/DOCUMENT_VERSION_NAMING_STANDARD.md)

---

**审计状态**: ✅ 完成
**审计质量**: 专业标准
**下次审计**: 按需执行
"""
        
        # 写入报告文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 审计报告已生成: {report_file}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    auditor = HumanAIDeepAuditor(layer_path)
    auditor.run_full_audit()


if __name__ == '__main__':
    main()
