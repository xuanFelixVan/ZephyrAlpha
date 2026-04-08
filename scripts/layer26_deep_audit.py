#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
第26轮深度审计脚本 - Alpha因子层全文档审计
功能：
1. L1文件系统层审计：目录结构、文件命名、路径引用
2. L2文档内容层审计：职责驱动、索引完备、版本隔离、文档代码对应
3. L3专业标准层审计：五大原则、分类体系、编号体系、文档质量
4. 重点检查：重复内容、职责不清楚
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
FACTOR_LIBRARY = DOCS_DIR / "02_FACTOR_LIBRARY"
REPORT_DIR = DOCS_DIR / "09_AUDIT" / "STATE"

class Layer26DeepAudit:
    def __init__(self):
        self.issues = []
        self.duplicates = []
        self.responsibility_issues = []
        self.file_hashes = {}
        self.file_contents = {}
        self.module_ids = {}
        self.responsibilities = {}
        
    def run_audit(self):
        """执行完整审计"""
        print("=" * 80)
        print("第26轮深度审计 - Alpha因子层全文档审计")
        print("=" * 80)
        
        # L1 文件系统层审计
        l1_results = self.audit_l1_file_system()
        
        # L2 文档内容层审计
        l2_results = self.audit_l2_document_content()
        
        # L3 专业标准层审计
        l3_results = self.audit_l3_professional_standards()
        
        # 重点检查：重复内容
        duplicate_results = self.check_duplicates()
        
        # 重点检查：职责不清楚
        responsibility_results = self.check_responsibility_clarity()
        
        # 生成报告
        report_file = self.generate_report(
            l1_results, l2_results, l3_results,
            duplicate_results, responsibility_results
        )
        
        return report_file
    
    def audit_l1_file_system(self):
        """L1 文件系统层审计"""
        print("\n" + "=" * 80)
        print("L1 文件系统层审计")
        print("=" * 80)
        
        results = {
            'directory_issues': [],
            'naming_issues': [],
            'path_issues': [],
            'stats': {}
        }
        
        # 1. 目录结构检查
        print("\n检查目录结构...")
        results['directory_issues'] = self.check_directory_structure()
        
        # 2. 文件命名检查
        print("检查文件命名...")
        results['naming_issues'] = self.check_file_naming()
        
        # 3. 路径引用检查
        print("检查路径引用...")
        results['path_issues'] = self.check_path_references()
        
        # 统计
        results['stats'] = {
            'total_files': sum(1 for _ in FACTOR_LIBRARY.rglob('*.md')),
            'total_dirs': sum(1 for _ in FACTOR_LIBRARY.rglob('*') if _.is_dir()),
            'directory_issues': len(results['directory_issues']),
            'naming_issues': len(results['naming_issues']),
            'path_issues': len(results['path_issues'])
        }
        
        print(f"\nL1审计完成:")
        print(f"  总文件数: {results['stats']['total_files']}")
        print(f"  总目录数: {results['stats']['total_dirs']}")
        print(f"  目录问题: {results['stats']['directory_issues']}")
        print(f"  命名问题: {results['stats']['naming_issues']}")
        print(f"  路径问题: {results['stats']['path_issues']}")
        
        return results
    
    def check_directory_structure(self):
        """检查目录结构"""
        issues = []
        
        # 标准分类目录
        standard_categories = [
            '01_STANDARDS',
            '02_ALPHA_FACTORS_INDEX',
            '03_RISK_FACTORS',
            '04_DATA_SOURCE',
            '05_BACKTEST',
            '06_REGISTRY',
            '07_FACTOR_MONITORING',
            '08_OPTIMIZATION',
            '09_AUDIT',
            '10_MANUAL'
        ]
        
        # 检查根目录文档
        root_docs = []
        for item in FACTOR_LIBRARY.iterdir():
            if item.is_file() and item.suffix == '.md':
                if item.name not in ['INDEX.md', 'README.md', 'SITEMAP.md']:
                    root_docs.append(item.name)
                    issues.append({
                        'type': '目录漂移',
                        'severity': 'P2',
                        'file': item.name,
                        'issue': '文档应在分类目录中',
                        'suggestion': f'移动到合适的分类目录'
                    })
        
        # 检查稀疏目录
        for category in standard_categories:
            category_path = FACTOR_LIBRARY / category
            if category_path.exists():
                md_files = list(category_path.rglob('*.md'))
                if len(md_files) < 3:
                    issues.append({
                        'type': '目录稀疏',
                        'severity': 'P2',
                        'directory': category,
                        'issue': f'目录下仅{len(md_files)}个文档',
                        'suggestion': '考虑整合到相关目录'
                    })
        
        # 检查空目录
        for item in FACTOR_LIBRARY.iterdir():
            if item.is_dir():
                if item.name.startswith('.'):
                    continue
                has_content = any(item.rglob('*.md'))
                if not has_content:
                    issues.append({
                        'type': '空目录',
                        'severity': 'P1',
                        'directory': item.name,
                        'issue': '目录无任何文档',
                        'suggestion': '删除空目录或添加文档'
                    })
        
        return issues
    
    def check_file_naming(self):
        """检查文件命名"""
        issues = []
        
        naming_pattern = re.compile(r'^[A-Z][A-Z0-9_]*\.md$')
        exceptions = ['INDEX.md', 'README.md', 'SITEMAP.md', 'BLUEPRINT.md', 'FAQ.md']
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            if file_path.name in exceptions:
                continue
            
            if not naming_pattern.match(file_path.name):
                issues.append({
                    'type': '命名不规范',
                    'severity': 'P2',
                    'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                    'current': file_path.name,
                    'suggested': file_path.name.upper().replace(' ', '_').replace('-', '_'),
                    'issue': '不符合大写命名规范'
                })
        
        return issues
    
    def check_path_references(self):
        """检查路径引用"""
        issues = []
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查过多的 ../
                if content.count('../') > 5:
                    issues.append({
                        'type': '路径冗余',
                        'severity': 'P3',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'使用过多../引用 ({content.count("../")}次)',
                        'suggestion': '简化路径引用'
                    })
                
                # 检查绝对路径
                abs_paths = re.findall(r'\[.*?\]\(([A-Z]:\\[^)]+)\)', content)
                if abs_paths:
                    issues.append({
                        'type': '绝对路径',
                        'severity': 'P2',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'使用绝对路径: {abs_paths[0]}',
                        'suggestion': '使用相对路径'
                    })
                
            except Exception as e:
                pass
        
        return issues
    
    def audit_l2_document_content(self):
        """L2 文档内容层审计"""
        print("\n" + "=" * 80)
        print("L2 文档内容层审计")
        print("=" * 80)
        
        results = {
            'responsibility_issues': [],
            'index_issues': [],
            'version_issues': [],
            'code_doc_issues': [],
            'stats': {}
        }
        
        # 1. 职责驱动原则检查
        print("\n检查职责驱动原则...")
        results['responsibility_issues'] = self.check_responsibility_principle()
        
        # 2. 索引完备性检查
        print("检查索引完备性...")
        results['index_issues'] = self.check_index_completeness()
        
        # 3. 版本隔离检查
        print("检查版本隔离...")
        results['version_issues'] = self.check_version_isolation()
        
        # 4. 文档代码对应检查
        print("检查文档代码对应...")
        results['code_doc_issues'] = self.check_code_document_correspondence()
        
        # 统计
        results['stats'] = {
            'responsibility_issues': len(results['responsibility_issues']),
            'index_issues': len(results['index_issues']),
            'version_issues': len(results['version_issues']),
            'code_doc_issues': len(results['code_doc_issues'])
        }
        
        print(f"\nL2审计完成:")
        print(f"  职责问题: {results['stats']['responsibility_issues']}")
        print(f"  索引问题: {results['stats']['index_issues']}")
        print(f"  版本问题: {results['stats']['version_issues']}")
        print(f"  代码对应问题: {results['stats']['code_doc_issues']}")
        
        return results
    
    def check_responsibility_principle(self):
        """检查职责驱动原则"""
        issues = []
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 提取职责描述
                resp_match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
                
                if not resp_match:
                    issues.append({
                        'type': '职责缺失',
                        'severity': 'P1',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': '缺少职责描述',
                        'suggestion': '添加核心职责描述'
                    })
                else:
                    responsibility = resp_match.group(1).strip()
                    
                    # 检查职责描述长度
                    if len(responsibility) < 15:
                        issues.append({
                            'type': '职责过短',
                            'severity': 'P2',
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'issue': f'职责描述过短: {responsibility} ({len(responsibility)}字符)',
                            'suggestion': '扩展职责描述至15字符以上'
                        })
                    
                    # 检查模糊词汇
                    vague_words = ['管理', '处理', '相关', '等', '内容', '工作']
                    for word in vague_words:
                        if word in responsibility and len(responsibility) < 30:
                            issues.append({
                                'type': '职责模糊',
                                'severity': 'P2',
                                'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                                'issue': f'职责描述含模糊词汇"{word}": {responsibility}',
                                'suggestion': '使用更具体的动词和对象'
                            })
                            break
                    
                    # 记录职责用于后续重复检查
                    self.responsibilities[str(file_path.relative_to(FACTOR_LIBRARY))] = responsibility
                
                # 检查职责边界
                boundary_match = re.search(r'\*\*职责边界\*\*:', content)
                if not boundary_match:
                    issues.append({
                        'type': '边界缺失',
                        'severity': 'P2',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': '缺少职责边界描述',
                        'suggestion': '添加职责边界说明'
                    })
                
            except Exception as e:
                pass
        
        return issues
    
    def check_index_completeness(self):
        """检查索引完备性"""
        issues = []
        
        # 检查根目录INDEX.md
        root_index = FACTOR_LIBRARY / 'INDEX.md'
        if not root_index.exists():
            issues.append({
                'type': '入口缺失',
                'severity': 'P0',
                'file': 'INDEX.md',
                'issue': '根目录缺少INDEX.md',
                'suggestion': '创建主入口INDEX.md'
            })
        
        # 检查各子目录INDEX.md
        for item in FACTOR_LIBRARY.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                index_file = item / 'INDEX.md'
                if not index_file.exists():
                    issues.append({
                        'type': '子索引缺失',
                        'severity': 'P1',
                        'directory': item.name,
                        'issue': '子目录缺少INDEX.md',
                        'suggestion': f'创建{item.name}/INDEX.md'
                    })
        
        return issues
    
    def check_version_isolation(self):
        """检查版本隔离"""
        issues = []
        
        # 检查module_id重复
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                module_id_match = re.search(r'module_id:\s*(.+)', content)
                if module_id_match:
                    module_id = module_id_match.group(1).strip()
                    if module_id in self.module_ids:
                        issues.append({
                            'type': 'module_id重复',
                            'severity': 'P1',
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'issue': f'module_id重复: {module_id}',
                            'duplicate_of': self.module_ids[module_id],
                            'suggestion': '修改module_id使其唯一'
                        })
                    else:
                        self.module_ids[module_id] = str(file_path.relative_to(FACTOR_LIBRARY))
            
            except Exception as e:
                pass
        
        return issues
    
    def check_code_document_correspondence(self):
        """检查文档代码对应"""
        issues = []
        
        # 检查文档中引用的代码文件是否存在
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 查找代码文件引用
                code_refs = re.findall(r'`(src/[^\`]+)`', content)
                for code_ref in code_refs:
                    code_path = PROJECT_ROOT / code_ref
                    if not code_path.exists():
                        issues.append({
                            'type': '代码文件缺失',
                            'severity': 'P2',
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'issue': f'引用的代码文件不存在: {code_ref}',
                            'suggestion': '更新文档或创建代码文件'
                        })
            
            except Exception as e:
                pass
        
        return issues
    
    def audit_l3_professional_standards(self):
        """L3 专业标准层审计"""
        print("\n" + "=" * 80)
        print("L3 专业标准层审计")
        print("=" * 80)
        
        results = {
            'principle_issues': [],
            'classification_issues': [],
            'numbering_issues': [],
            'quality_issues': [],
            'stats': {}
        }
        
        # 1. 五大原则符合性检查
        print("\n检查五大原则符合性...")
        results['principle_issues'] = self.check_five_principles()
        
        # 2. 文档分类检查
        print("检查文档分类...")
        results['classification_issues'] = self.check_document_classification()
        
        # 3. 编号体系检查
        print("检查编号体系...")
        results['numbering_issues'] = self.check_numbering_system()
        
        # 4. 文档质量检查
        print("检查文档质量...")
        results['quality_issues'] = self.check_document_quality()
        
        # 统计
        results['stats'] = {
            'principle_issues': len(results['principle_issues']),
            'classification_issues': len(results['classification_issues']),
            'numbering_issues': len(results['numbering_issues']),
            'quality_issues': len(results['quality_issues'])
        }
        
        print(f"\nL3审计完成:")
        print(f"  原则问题: {results['stats']['principle_issues']}")
        print(f"  分类问题: {results['stats']['classification_issues']}")
        print(f"  编号问题: {results['stats']['numbering_issues']}")
        print(f"  质量问题: {results['stats']['quality_issues']}")
        
        return results
    
    def check_five_principles(self):
        """检查五大原则符合性"""
        issues = []
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查YAML头部
                if not content.startswith('---'):
                    issues.append({
                        'type': 'YAML缺失',
                        'severity': 'P1',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': '缺少YAML元数据头部',
                        'principle': '命名规范原则',
                        'suggestion': '添加标准YAML头部'
                    })
                else:
                    # 检查必要字段
                    required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
                    for field in required_fields:
                        if f'{field}:' not in content[:500]:
                            issues.append({
                                'type': 'YAML字段缺失',
                                'severity': 'P2',
                                'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                                'issue': f'YAML缺少必要字段: {field}',
                                'principle': '命名规范原则',
                                'suggestion': f'添加{field}字段'
                            })
            
            except Exception as e:
                pass
        
        return issues
    
    def check_document_classification(self):
        """检查文档分类"""
        issues = []
        
        # 标准分类
        standard_categories = {
            '01_STANDARDS': '标准规范',
            '02_ALPHA_FACTORS_INDEX': 'Alpha因子索引',
            '03_RISK_FACTORS': '风险因子',
            '04_DATA_SOURCE': '数据源',
            '05_BACKTEST': '回测系统',
            '06_REGISTRY': '注册中心',
            '07_FACTOR_MONITORING': '因子监控',
            '08_OPTIMIZATION': '优化系统',
            '09_AUDIT': '审计报告',
            '10_MANUAL': '手册文档'
        }
        
        # 检查分类目录命名
        for item in FACTOR_LIBRARY.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name not in standard_categories:
                    issues.append({
                        'type': '非标准分类',
                        'severity': 'P2',
                        'directory': item.name,
                        'issue': '不符合标准分类命名',
                        'suggestion': '使用标准分类命名或整合到现有分类'
                    })
        
        return issues
    
    def check_numbering_system(self):
        """检查编号体系"""
        issues = []
        
        # 已在L2中检查module_id重复，这里检查编号格式
        for module_id, file_path in self.module_ids.items():
            # 检查编号格式
            if not re.match(r'^[A-Z][A-Z0-9_]+(_\d{3})?$', module_id):
                issues.append({
                    'type': '编号格式不规范',
                    'severity': 'P2',
                    'file': file_path,
                    'issue': f'module_id格式不规范: {module_id}',
                    'suggestion': '使用大写字母、下划线和可选的三位数字后缀'
                })
        
        return issues
    
    def check_document_quality(self):
        """检查文档质量"""
        issues = []
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查文档结构
                if not re.search(r'^#\s+.+', content, re.MULTILINE):
                    issues.append({
                        'type': '缺少标题',
                        'severity': 'P1',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': '文档缺少一级标题',
                        'suggestion': '添加一级标题'
                    })
                
                # 检查内容长度
                content_without_yaml = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
                if len(content_without_yaml.strip()) < 100:
                    issues.append({
                        'type': '内容过短',
                        'severity': 'P2',
                        'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'issue': f'文档内容过短 ({len(content_without_yaml.strip())}字符)',
                        'suggestion': '补充文档内容'
                    })
                
                # 检查死链接
                links = re.findall(r'\[.*?\]\(([^)]+)\)', content)
                for link in links:
                    if link.startswith('http'):
                        continue
                    if link.startswith('#'):
                        continue
                    
                    # 检查相对链接
                    link_path = file_path.parent / link
                    if not link_path.exists():
                        issues.append({
                            'type': '死链接',
                            'severity': 'P2',
                            'file': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'issue': f'链接不存在: {link}',
                            'suggestion': '修复或删除链接'
                        })
            
            except Exception as e:
                pass
        
        return issues
    
    def check_duplicates(self):
        """重点检查：重复内容"""
        print("\n" + "=" * 80)
        print("重点检查：重复内容")
        print("=" * 80)
        
        results = {
            'content_duplicates': [],
            'title_duplicates': [],
            'responsibility_duplicates': [],
            'stats': {}
        }
        
        # 1. 内容重复检查（基于内容哈希）
        print("\n检查内容重复...")
        content_hashes = {}
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 提取主要内容（去除YAML头部）
                main_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
                main_content = main_content.strip()
                
                # 计算哈希
                content_hash = hashlib.md5(main_content.encode()).hexdigest()
                
                if content_hash in content_hashes:
                    results['content_duplicates'].append({
                        'type': '内容重复',
                        'severity': 'P0',
                        'file1': content_hashes[content_hash],
                        'file2': str(file_path.relative_to(FACTOR_LIBRARY)),
                        'hash': content_hash,
                        'suggestion': '删除重复文档或合并内容'
                    })
                else:
                    content_hashes[content_hash] = str(file_path.relative_to(FACTOR_LIBRARY))
            
            except Exception as e:
                pass
        
        # 2. 标题重复检查
        print("检查标题重复...")
        titles = {}
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    if title in titles:
                        results['title_duplicates'].append({
                            'type': '标题重复',
                            'severity': 'P1',
                            'file1': titles[title],
                            'file2': str(file_path.relative_to(FACTOR_LIBRARY)),
                            'title': title,
                            'suggestion': '修改标题使其具有区分度'
                        })
                    else:
                        titles[title] = str(file_path.relative_to(FACTOR_LIBRARY))
            
            except Exception as e:
                pass
        
        # 3. 职责重复检查
        print("检查职责重复...")
        resp_counts = Counter(self.responsibilities.values())
        for resp, count in resp_counts.items():
            if count > 1:
                files = [f for f, r in self.responsibilities.items() if r == resp]
                results['responsibility_duplicates'].append({
                    'type': '职责重复',
                    'severity': 'P1',
                    'files': files,
                    'responsibility': resp,
                    'count': count,
                    'suggestion': '明确各文档职责边界或合并文档'
                })
        
        # 统计
        results['stats'] = {
            'content_duplicates': len(results['content_duplicates']),
            'title_duplicates': len(results['title_duplicates']),
            'responsibility_duplicates': len(results['responsibility_duplicates'])
        }
        
        print(f"\n重复内容检查完成:")
        print(f"  内容重复: {results['stats']['content_duplicates']}")
        print(f"  标题重复: {results['stats']['title_duplicates']}")
        print(f"  职责重复: {results['stats']['responsibility_duplicates']}")
        
        return results
    
    def check_responsibility_clarity(self):
        """重点检查：职责不清楚"""
        print("\n" + "=" * 80)
        print("重点检查：职责不清楚")
        print("=" * 80)
        
        results = {
            'unclear_responsibilities': [],
            'overlapping_responsibilities': [],
            'missing_responsibilities': [],
            'stats': {}
        }
        
        # 1. 职责不清楚检查
        print("\n检查职责不清楚...")
        for file_path, responsibility in self.responsibilities.items():
            # 检查模糊词汇
            vague_patterns = [
                (r'管理.*相关', '使用"管理"和"相关"等模糊词汇'),
                (r'处理.*内容', '使用"处理"和"内容"等模糊词汇'),
                (r'.*等.*', '使用"等"等模糊词汇'),
                (r'^.{1,14}$', '职责描述过短（少于15字符）'),
                (r'^(文档|文件|模块|系统)$', '仅使用名词，缺少动词')
            ]
            
            for pattern, issue in vague_patterns:
                if re.search(pattern, responsibility):
                    results['unclear_responsibilities'].append({
                        'type': '职责不清楚',
                        'severity': 'P1',
                        'file': file_path,
                        'responsibility': responsibility,
                        'issue': issue,
                        'suggestion': '使用具体动词和对象描述职责'
                    })
                    break
        
        # 2. 职责重叠检查
        print("检查职责重叠...")
        responsibility_files = defaultdict(list)
        for file_path, responsibility in self.responsibilities.items():
            # 提取关键词
            keywords = set(re.findall(r'[\u4e00-\u9fa5]+', responsibility))
            responsibility_files[frozenset(keywords)].append(file_path)
        
        for keywords, files in responsibility_files.items():
            if len(files) > 1 and len(keywords) > 2:  # 至少3个关键词相同
                results['overlapping_responsibilities'].append({
                    'type': '职责重叠',
                    'severity': 'P1',
                    'files': files,
                    'keywords': list(keywords),
                    'suggestion': '明确各文档职责边界或合并文档'
                })
        
        # 3. 缺失职责检查
        print("检查缺失职责...")
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = str(file_path.relative_to(FACTOR_LIBRARY))
            if rel_path not in self.responsibilities:
                results['missing_responsibilities'].append({
                    'type': '职责缺失',
                    'severity': 'P1',
                    'file': rel_path,
                    'issue': '文档缺少职责描述',
                    'suggestion': '添加核心职责描述'
                })
        
        # 统计
        results['stats'] = {
            'unclear_responsibilities': len(results['unclear_responsibilities']),
            'overlapping_responsibilities': len(results['overlapping_responsibilities']),
            'missing_responsibilities': len(results['missing_responsibilities'])
        }
        
        print(f"\n职责不清楚检查完成:")
        print(f"  职责不清楚: {results['stats']['unclear_responsibilities']}")
        print(f"  职责重叠: {results['stats']['overlapping_responsibilities']}")
        print(f"  职责缺失: {results['stats']['missing_responsibilities']}")
        
        return results
    
    def generate_report(self, l1_results, l2_results, l3_results,
                       duplicate_results, responsibility_results):
        """生成审计报告"""
        print("\n" + "=" * 80)
        print("生成审计报告")
        print("=" * 80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = REPORT_DIR / f"LAYER26_DEEP_AUDIT_REPORT_{timestamp}.md"
        
        # 统计总问题数
        total_issues = (
            l1_results['stats']['directory_issues'] +
            l1_results['stats']['naming_issues'] +
            l1_results['stats']['path_issues'] +
            l2_results['stats']['responsibility_issues'] +
            l2_results['stats']['index_issues'] +
            l2_results['stats']['version_issues'] +
            l2_results['stats']['code_doc_issues'] +
            l3_results['stats']['principle_issues'] +
            l3_results['stats']['classification_issues'] +
            l3_results['stats']['numbering_issues'] +
            l3_results['stats']['quality_issues'] +
            duplicate_results['stats']['content_duplicates'] +
            duplicate_results['stats']['title_duplicates'] +
            duplicate_results['stats']['responsibility_duplicates'] +
            responsibility_results['stats']['unclear_responsibilities'] +
            responsibility_results['stats']['overlapping_responsibilities'] +
            responsibility_results['stats']['missing_responsibilities']
        )
        
        report_content = f'''---
module_id: LAYER26_DEEP_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 深度审计报告
applicable_scope: Alpha因子层全文档审计
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 第26轮深度审计报告 - Alpha因子层全文档审计

> **核心职责**: 全面审计Alpha因子层所有文档，发现并记录所有问题
> **职责边界**: 
> - ✅ 本文档负责：问题发现、问题记录、问题分类、风险评估
> - ❌ 本文档不负责：问题修复执行、文档内容修改

---

## 📋 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: Alpha因子层所有文档  
**审计方法**: 三层审计方法论（L1-L3）+ 重复内容检查 + 职责清晰度检查  
**审计结论**: 发现 {total_issues} 个问题

---

## 📊 审计统计

### 总体统计

| 层级 | 问题类型 | 问题数量 | 严重程度 |
|------|---------|---------|---------|
| **L1 文件系统层** | 目录结构 | {l1_results['stats']['directory_issues']} | P1-P2 |
| **L1 文件系统层** | 文件命名 | {l1_results['stats']['naming_issues']} | P2 |
| **L1 文件系统层** | 路径引用 | {l1_results['stats']['path_issues']} | P2-P3 |
| **L2 文档内容层** | 职责驱动 | {l2_results['stats']['responsibility_issues']} | P1-P2 |
| **L2 文档内容层** | 索引完备 | {l2_results['stats']['index_issues']} | P0-P1 |
| **L2 文档内容层** | 版本隔离 | {l2_results['stats']['version_issues']} | P1 |
| **L2 文档内容层** | 文档代码对应 | {l2_results['stats']['code_doc_issues']} | P2 |
| **L3 专业标准层** | 五大原则 | {l3_results['stats']['principle_issues']} | P1-P2 |
| **L3 专业标准层** | 文档分类 | {l3_results['stats']['classification_issues']} | P2 |
| **L3 专业标准层** | 编号体系 | {l3_results['stats']['numbering_issues']} | P2 |
| **L3 专业标准层** | 文档质量 | {l3_results['stats']['quality_issues']} | P1-P2 |
| **重点检查** | 内容重复 | {duplicate_results['stats']['content_duplicates']} | P0 |
| **重点检查** | 标题重复 | {duplicate_results['stats']['title_duplicates']} | P1 |
| **重点检查** | 职责重复 | {duplicate_results['stats']['responsibility_duplicates']} | P1 |
| **重点检查** | 职责不清楚 | {responsibility_results['stats']['unclear_responsibilities']} | P1 |
| **重点检查** | 职责重叠 | {responsibility_results['stats']['overlapping_responsibilities']} | P1 |
| **重点检查** | 职责缺失 | {responsibility_results['stats']['missing_responsibilities']} | P1 |
| **总计** | - | **{total_issues}** | - |

---

## 🔴 L1 文件系统层审计结果

### 1.1 目录结构问题

**问题数量**: {l1_results['stats']['directory_issues']} 个

'''

        # 添加目录结构问题
        for issue in l1_results['directory_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue.get('file', issue.get('directory', ''))} - {issue['issue']}\n"
        
        report_content += f'''
### 1.2 文件命名问题

**问题数量**: {l1_results['stats']['naming_issues']} 个

'''
        
        # 添加文件命名问题
        for issue in l1_results['naming_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
### 1.3 路径引用问题

**问题数量**: {l1_results['stats']['path_issues']} 个

'''
        
        # 添加路径引用问题
        for issue in l1_results['path_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
---

## 🟡 L2 文档内容层审计结果

### 2.1 职责驱动原则问题

**问题数量**: {l2_results['stats']['responsibility_issues']} 个

'''
        
        # 添加职责驱动问题
        for issue in l2_results['responsibility_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
### 2.2 索引完备性问题

**问题数量**: {l2_results['stats']['index_issues']} 个

'''
        
        # 添加索引完备性问题
        for issue in l2_results['index_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue.get('file', issue.get('directory', ''))} - {issue['issue']}\n"
        
        report_content += f'''
### 2.3 版本隔离问题

**问题数量**: {l2_results['stats']['version_issues']} 个

'''
        
        # 添加版本隔离问题
        for issue in l2_results['version_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
---

## 🟢 L3 专业标准层审计结果

### 3.1 五大原则符合性问题

**问题数量**: {l3_results['stats']['principle_issues']} 个

'''
        
        # 添加五大原则问题
        for issue in l3_results['principle_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
### 3.2 文档质量问题

**问题数量**: {l3_results['stats']['quality_issues']} 个

'''
        
        # 添加文档质量问题
        for issue in l3_results['quality_issues'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']} - {issue['issue']}\n"
        
        report_content += f'''
---

## 🔍 重点检查结果

### 4.1 内容重复

**问题数量**: {duplicate_results['stats']['content_duplicates']} 对

'''
        
        # 添加内容重复
        for dup in duplicate_results['content_duplicates']:
            report_content += f"- **{dup['type']}** ({dup['severity']}):\n"
            report_content += f"  - 文件1: {dup['file1']}\n"
            report_content += f"  - 文件2: {dup['file2']}\n"
            report_content += f"  - 建议: {dup['suggestion']}\n\n"
        
        report_content += f'''
### 4.2 标题重复

**问题数量**: {duplicate_results['stats']['title_duplicates']} 对

'''
        
        # 添加标题重复
        for dup in duplicate_results['title_duplicates'][:10]:
            report_content += f"- **{dup['type']}** ({dup['severity']}): 标题\"{dup['title']}\"\n"
            report_content += f"  - 文件1: {dup['file1']}\n"
            report_content += f"  - 文件2: {dup['file2']}\n\n"
        
        report_content += f'''
### 4.3 职责重复

**问题数量**: {duplicate_results['stats']['responsibility_duplicates']} 组

'''
        
        # 添加职责重复
        for dup in duplicate_results['responsibility_duplicates'][:10]:
            report_content += f"- **{dup['type']}** ({dup['severity']}): {dup['count']}个文档职责相同\n"
            report_content += f"  - 职责: {dup['responsibility']}\n"
            report_content += f"  - 文件: {', '.join(dup['files'][:3])}\n\n"
        
        report_content += f'''
### 4.4 职责不清楚

**问题数量**: {responsibility_results['stats']['unclear_responsibilities']} 个

'''
        
        # 添加职责不清楚
        for issue in responsibility_results['unclear_responsibilities'][:10]:
            report_content += f"- **{issue['type']}** ({issue['severity']}): {issue['file']}\n"
            report_content += f"  - 职责: {issue['responsibility']}\n"
            report_content += f"  - 问题: {issue['issue']}\n\n"
        
        report_content += f'''
---

## 🎯 风险评估与优先级

### P0 立即修复（严重问题）

'''

        # P0问题
        p0_issues = []
        for dup in duplicate_results['content_duplicates']:
            p0_issues.append(f"- 内容重复: {dup['file1']} 与 {dup['file2']}")
        for issue in l2_results['index_issues']:
            if issue['severity'] == 'P0':
                p0_issues.append(f"- 索引缺失: {issue.get('file', issue.get('directory', ''))}")
        
        if p0_issues:
            report_content += '\n'.join(p0_issues[:10])
        else:
            report_content += "✅ 无P0级别问题\n"
        
        report_content += f'''
### P1 高优先级修复

'''

        # P1问题统计
        p1_count = 0
        for results in [l1_results, l2_results, l3_results, duplicate_results, responsibility_results]:
            for key in results:
                if isinstance(results[key], list):
                    for issue in results[key]:
                        if isinstance(issue, dict) and issue.get('severity') == 'P1':
                            p1_count += 1
        
        report_content += f"共 {p1_count} 个P1级别问题\n"
        
        report_content += f'''
### P2 中优先级优化

'''

        # P2问题统计
        p2_count = 0
        for results in [l1_results, l2_results, l3_results, duplicate_results, responsibility_results]:
            for key in results:
                if isinstance(results[key], list):
                    for issue in results[key]:
                        if isinstance(issue, dict) and issue.get('severity') == 'P2':
                            p2_count += 1
        
        report_content += f"共 {p2_count} 个P2级别问题\n"
        
        report_content += f'''
---

## 💡 改进建议与行动计划

### 立即修复（本周内）

1. ⏸️ 删除内容重复文档
2. ⏸️ 创建缺失的INDEX.md文件
3. ⏸️ 修复P0级别问题

### 短期改进（本月内）

1. ⏸️ 优化职责不清楚的文档
2. ⏸️ 修复命名不规范文件
3. ⏸️ 补充缺失的YAML字段

### 长期优化（持续）

1. ⏸️ 建立自动化检查机制
2. ⏸️ 定期执行审查机制
3. ⏸️ 持续优化质量标准

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，第26轮深度审计报告 | 首席文档架构师 |
'''
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 报告生成: {report_file.name}")
        
        return report_file

def main():
    """主函数"""
    audit = Layer26DeepAudit()
    report_file = audit.run_audit()
    
    print("\n" + "=" * 80)
    print("第26轮深度审计完成")
    print("=" * 80)
    print(f"报告位置: {report_file}")

if __name__ == '__main__':
    main()
