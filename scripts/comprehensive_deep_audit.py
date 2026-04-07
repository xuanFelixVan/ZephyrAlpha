#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人机交互层全面深度审计脚本
基于专业量化机构五大原则和三层审计标准
重点检查重复内容和职责清晰度
"""

import re
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ComprehensiveDeepAuditor:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.audit_results = {
            'L1_file_system': {
                'directory_structure': [],
                'file_naming': [],
                'path_references': []
            },
            'L2_document_content': {
                'responsibility_driven': [],
                'index_completeness': [],
                'version_isolation': [],
                'doc_code_correspondence': []
            },
            'L3_professional_standard': {
                'five_principles': [],
                'document_classification': [],
                'numbering_system': [],
                'document_quality': []
            },
            'deep_content_check': {
                'duplicate_content': [],
                'unclear_responsibility': [],
                'content_overlap': []
            }
        }
        
        self.stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_issues': 0,
            'critical_issues': 0,
            'major_issues': 0,
            'minor_issues': 0
        }
        
        self.content_hashes = defaultdict(list)
        self.responsibility_map = defaultdict(list)
        self.module_id_map = defaultdict(list)
    
    def run_full_audit(self):
        """执行全面深度审计"""
        print("=" * 80)
        print("人机交互层全面深度审计")
        print("=" * 80)
        print(f"审计范围: {self.layer_path}")
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计标准: 专业量化机构五大原则 + 三层审计标准")
        print()
        
        # L1: 文件系统层审计
        print("=" * 80)
        print("L1: 文件系统层审计")
        print("=" * 80)
        self.audit_L1_file_system()
        
        # L2: 文档内容层审计
        print()
        print("=" * 80)
        print("L2: 文档内容层审计")
        print("=" * 80)
        self.audit_L2_document_content()
        
        # L3: 专业标准层审计
        print()
        print("=" * 80)
        print("L3: 专业标准层审计")
        print("=" * 80)
        self.audit_L3_professional_standard()
        
        # 深度内容检查
        print()
        print("=" * 80)
        print("深度内容检查")
        print("=" * 80)
        self.deep_content_analysis()
        
        # 生成报告
        self.generate_report()
    
    def audit_L1_file_system(self):
        """L1: 文件系统层审计"""
        # 1.1 目录结构问题
        self.check_directory_structure()
        
        # 1.2 文件命名问题
        self.check_file_naming()
        
        # 1.3 路径引用问题
        self.check_path_references()
    
    def check_directory_structure(self):
        """检查目录结构"""
        print("\n[1.1] 检查目录结构...")
        
        directories = list(self.layer_path.rglob('*'))
        self.stats['total_directories'] = len([d for d in directories if d.is_dir()])
        
        for directory in directories:
            if not directory.is_dir():
                continue
            
            # 检查目录稀疏
            files_in_dir = list(directory.glob('*.md'))
            if len(files_in_dir) < 2 and directory != self.layer_path:
                self.add_issue('L1_file_system', 'directory_structure', {
                    'type': '目录稀疏',
                    'file': str(directory.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': f'目录下文件过少({len(files_in_dir)}个)，建议整合',
                    'suggestion': '考虑与相邻目录合并或补充文档'
                })
            
            # 检查目录层级深度
            depth = len(directory.relative_to(self.layer_path).parts)
            if depth > 4:
                self.add_issue('L1_file_system', 'directory_structure', {
                    'type': '目录层级过深',
                    'file': str(directory.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': f'目录嵌套超过4层({depth}层)，难以导航',
                    'suggestion': '考虑扁平化目录结构'
                })
            
            # 检查空目录
            if len(list(directory.iterdir())) == 0:
                self.add_issue('L1_file_system', 'directory_structure', {
                    'type': '空目录',
                    'file': str(directory.relative_to(self.layer_path)),
                    'severity': 'P1',
                    'description': '目录存在但无内容',
                    'suggestion': '删除空目录或补充内容'
                })
    
    def check_file_naming(self):
        """检查文件命名"""
        print("[1.2] 检查文件命名...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        self.stats['total_files'] = len(md_files)
        
        for md_file in md_files:
            filename = md_file.name
            
            # 检查旧架构命名残留
            if re.search(r'Layer\s*[0-9]', filename, re.IGNORECASE):
                self.add_issue('L1_file_system', 'file_naming', {
                    'type': '旧架构命名残留',
                    'file': str(md_file.relative_to(self.layer_path)),
                    'severity': 'P1',
                    'description': '文件名包含Layer 0-8等旧架构关键词',
                    'suggestion': '更新文件名以反映新架构'
                })
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', filename):
                self.add_issue('L1_file_system', 'file_naming', {
                    'type': '特殊字符问题',
                    'file': str(md_file.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': '文件名包含空格或中文等特殊字符',
                    'suggestion': '使用英文和下划线命名'
                })
    
    def check_path_references(self):
        """检查路径引用"""
        print("[1.3] 检查路径引用...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除BOM字符
                content = content.lstrip('\ufeff')
                
                # 移除代码块中的内容（避免误判代码块中的链接）
                content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
                
                # 检查链接
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content_no_code)
                
                for link_text, link_path in links:
                    # 跳过外部链接和锚点
                    if link_path.startswith('http') or link_path.startswith('#'):
                        continue
                    
                    # 跳过模板占位符链接（包含{和}的链接）
                    if '{' in link_path or '}' in link_path:
                        continue
                    
                    # 跳过空链接
                    if not link_path.strip():
                        continue
                    
                    # 检查路径冗余
                    if link_path.count('../') > 3:
                        self.add_issue('L1_file_system', 'path_references', {
                            'type': '路径冗余',
                            'file': str(md_file.relative_to(self.layer_path)),
                            'severity': 'P2',
                            'description': f'链接使用过多../相对路径: {link_path}',
                            'suggestion': '简化路径引用'
                        })
                    
                    # 检查死链接
                    if not link_path.startswith('http'):
                        target_path = (md_file.parent / link_path).resolve()
                        if not target_path.exists():
                            self.add_issue('L1_file_system', 'path_references', {
                                'type': '死链接',
                                'file': str(md_file.relative_to(self.layer_path)),
                                'severity': 'P1',
                                'description': f'链接指向不存在的文件: {link_path}',
                                'suggestion': '修复或删除链接'
                            })
            
            except Exception as e:
                pass
    
    def audit_L2_document_content(self):
        """L2: 文档内容层审计"""
        # 2.1 职责驱动原则
        self.check_responsibility_driven()
        
        # 2.2 索引完备性
        self.check_index_completeness()
        
        # 2.3 版本隔离
        self.check_version_isolation()
        
        # 2.4 文档代码对应
        self.check_doc_code_correspondence()
    
    def check_responsibility_driven(self):
        """检查职责驱动原则"""
        print("\n[2.1] 检查职责驱动原则...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除BOM字符
                content = content.lstrip('\ufeff')
                
                # 提取YAML头部
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                
                if not yaml_match:
                    self.add_issue('L2_document_content', 'responsibility_driven', {
                        'type': 'YAML头部缺失',
                        'file': str(md_file.relative_to(self.layer_path)),
                        'severity': 'P1',
                        'description': '文档缺少标准YAML元数据',
                        'suggestion': '添加标准YAML头部'
                    })
                    continue
                
                # 解析YAML
                try:
                    yaml_content = yaml.safe_load(yaml_match.group(1))
                except:
                    continue
                
                # 检查职责描述
                if 'responsibility' not in yaml_content:
                    self.add_issue('L2_document_content', 'responsibility_driven', {
                        'type': '职责缺失',
                        'file': str(md_file.relative_to(self.layer_path)),
                        'severity': 'P1',
                        'description': '文档缺少职责描述',
                        'suggestion': '添加明确的职责描述'
                    })
                else:
                    responsibility = yaml_content['responsibility']
                    if isinstance(responsibility, list):
                        resp_str = ' '.join(responsibility)
                    else:
                        resp_str = str(responsibility)
                    
                    # 记录职责描述用于后续重叠检查
                    self.responsibility_map[resp_str].append(str(md_file.relative_to(self.layer_path)))
                
                # 检查module_id
                if 'module_id' in yaml_content:
                    module_id = yaml_content['module_id']
                    self.module_id_map[module_id].append(str(md_file.relative_to(self.layer_path)))
            
            except Exception as e:
                pass
    
    def check_index_completeness(self):
        """检查索引完备性"""
        print("[2.2] 检查索引完备性...")
        
        # 检查根目录INDEX.md
        root_index = self.layer_path / 'index.md'
        if not root_index.exists():
            self.add_issue('L2_document_content', 'index_completeness', {
                'type': '入口混乱',
                'file': '根目录',
                'severity': 'P0',
                'description': '根目录缺少清晰的主入口INDEX.md',
                'suggestion': '创建主入口INDEX.md'
            })
        
        # 检查子目录INDEX.md
        directories = [d for d in self.layer_path.rglob('*') if d.is_dir()]
        
        for directory in directories:
            index_file = directory / 'INDEX.md'
            if not index_file.exists():
                self.add_issue('L2_document_content', 'index_completeness', {
                    'type': '子目录缺索引',
                    'file': str(directory.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': '子目录缺少INDEX.md导航文件',
                    'suggestion': '创建INDEX.md索引文件'
                })
    
    def check_version_isolation(self):
        """检查版本隔离"""
        print("[2.3] 检查版本隔离...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        
        # 检查重复文档（基于内容哈希）
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除BOM字符
                content = content.lstrip('\ufeff')
                
                # 计算内容哈希
                content_hash = hashlib.md5(content.encode()).hexdigest()
                self.content_hashes[content_hash].append(str(md_file.relative_to(self.layer_path)))
            
            except Exception as e:
                pass
        
        # 检查重复内容
        for hash_value, files in self.content_hashes.items():
            if len(files) > 1:
                self.add_issue('L2_document_content', 'version_isolation', {
                    'type': '重复文档',
                    'file': ', '.join(files),
                    'severity': 'P0',
                    'description': f'发现{len(files)}个内容完全相同的文档',
                    'suggestion': '保留最新版本，归档或删除其他版本'
                })
    
    def check_doc_code_correspondence(self):
        """检查文档代码对应"""
        print("[2.4] 检查文档代码对应...")
        
        # 检查旧架构引用
        md_files = list(self.layer_path.rglob('*.md'))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除BOM字符
                content = content.lstrip('\ufeff')
                
                # 检查旧架构引用
                if re.search(r'Layer\s*[0-9]', content, re.IGNORECASE):
                    self.add_issue('L2_document_content', 'doc_code_correspondence', {
                        'type': '文档滞后',
                        'file': str(md_file.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': '文档包含旧架构引用(Layer 0-8)',
                        'suggestion': '更新文档以反映新架构'
                    })
            
            except Exception as e:
                pass
    
    def audit_L3_professional_standard(self):
        """L3: 专业标准层审计"""
        # 3.1 五大原则符合性
        self.check_five_principles()
        
        # 3.2 文档分类
        self.check_document_classification()
        
        # 3.3 编号体系
        self.check_numbering_system()
        
        # 3.4 文档质量
        self.check_document_quality()
    
    def check_five_principles(self):
        """检查五大原则符合性"""
        print("\n[3.1] 检查五大原则符合性...")
        
        # 职责驱动原则 - 检查职责重叠
        for responsibility, files in self.responsibility_map.items():
            if len(files) > 1:
                self.add_issue('L3_professional_standard', 'five_principles', {
                    'type': '职责驱动原则违反',
                    'file': ', '.join(files),
                    'severity': 'P1',
                    'description': f'{len(files)}个文档具有相同的职责描述',
                    'suggestion': '为每个文档定义独特的职责'
                })
    
    def check_document_classification(self):
        """检查文档分类"""
        print("[3.2] 检查文档分类...")
        
        # 检查BLUEPRINT文件是否在正确的目录
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        
        for blueprint_file in blueprint_files:
            parent_dir = blueprint_file.parent.name
            
            # 检查是否在编号目录下
            if not re.match(r'^\d{2}_', parent_dir):
                self.add_issue('L3_professional_standard', 'document_classification', {
                    'type': '分类错误',
                    'file': str(blueprint_file.relative_to(self.layer_path)),
                    'severity': 'P2',
                    'description': 'BLUEPRINT文件未放置在编号目录下',
                    'suggestion': '移动到正确的分类目录'
                })
    
    def check_numbering_system(self):
        """检查编号体系"""
        print("[3.3] 检查编号体系...")
        
        # 检查module_id重复
        for module_id, files in self.module_id_map.items():
            if len(files) > 1:
                self.add_issue('L3_professional_standard', 'numbering_system', {
                    'type': '编号重复',
                    'file': ', '.join(files),
                    'severity': 'P0',
                    'description': f'{len(files)}个文档使用相同的module_id: {module_id}',
                    'suggestion': '为每个文档分配唯一的module_id'
                })
    
    def check_document_quality(self):
        """检查文档质量"""
        print("[3.4] 检查文档质量...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除BOM字符
                content = content.lstrip('\ufeff')
                
                lines = content.split('\n')
                
                # 检查文档过短
                if len(lines) < 15:
                    self.add_issue('L3_professional_standard', 'document_quality', {
                        'type': '内容过短',
                        'file': str(md_file.relative_to(self.layer_path)),
                        'severity': 'P2',
                        'description': f'文档内容过短({len(lines)}行)',
                        'suggestion': '补充详细内容'
                    })
            
            except Exception as e:
                pass
    
    def deep_content_analysis(self):
        """深度内容分析"""
        print("\n[深度] 检查重复内容和职责清晰度...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        
        # 检查内容相似度
        for i, file1 in enumerate(md_files):
            for file2 in md_files[i+1:]:
                try:
                    with open(file1, 'r', encoding='utf-8') as f:
                        content1 = f.read()
                    with open(file2, 'r', encoding='utf-8') as f:
                        content2 = f.read()
                    
                    # 移除BOM字符
                    content1 = content1.lstrip('\ufeff')
                    content2 = content2.lstrip('\ufeff')
                    
                    # 计算相似度（简化版）
                    similarity = self.calculate_similarity(content1, content2)
                    
                    if similarity > 0.8:  # 80%相似度
                        self.add_issue('deep_content_check', 'duplicate_content', {
                            'type': '内容高度相似',
                            'file': f'{file1.relative_to(self.layer_path)}, {file2.relative_to(self.layer_path)}',
                            'severity': 'P1',
                            'description': f'两个文档内容相似度达到{similarity*100:.1f}%',
                            'suggestion': '合并或区分文档内容'
                        })
                
                except Exception as e:
                    pass
        
        # 检查职责清晰度
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取YAML头部
                yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                
                if yaml_match:
                    try:
                        yaml_content = yaml.safe_load(yaml_match.group(1))
                        
                        if 'responsibility' in yaml_content:
                            responsibility = yaml_content['responsibility']
                            
                            # 检查职责描述是否模糊
                            if isinstance(responsibility, list):
                                resp_str = ' '.join(responsibility)
                            else:
                                resp_str = str(responsibility)
                            
                            # 检查是否包含模糊词汇
                            vague_words = ['管理', '处理', '负责', '相关']
                            vague_count = sum(1 for word in vague_words if word in resp_str)
                            
                            if vague_count > 2:
                                self.add_issue('deep_content_check', 'unclear_responsibility', {
                                    'type': '职责描述模糊',
                                    'file': str(md_file.relative_to(self.layer_path)),
                                    'severity': 'P2',
                                    'description': '职责描述包含过多模糊词汇',
                                    'suggestion': '使用更具体的职责描述'
                                })
                    
                    except:
                        pass
            
            except Exception as e:
                pass
    
    def calculate_similarity(self, content1, content2):
        """计算内容相似度（简化版）"""
        # 移除YAML头部
        content1 = re.sub(r'^---\s*\n.*?\n---', '', content1, flags=re.DOTALL)
        content2 = re.sub(r'^---\s*\n.*?\n---', '', content2, flags=re.DOTALL)
        
        # 简单的词汇重叠度计算
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def add_issue(self, layer, category, issue):
        """添加问题"""
        self.audit_results[layer][category].append(issue)
        self.stats['total_issues'] += 1
        
        severity = issue.get('severity', 'P2')
        if severity == 'P0':
            self.stats['critical_issues'] += 1
        elif severity == 'P1':
            self.stats['major_issues'] += 1
        else:
            self.stats['minor_issues'] += 1
    
    def generate_report(self):
        """生成审计报告"""
        report_path = Path(f"docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/COMPREHENSIVE_DEEP_AUDIT_{self.timestamp}.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 人机交互层全面深度审计报告\n\n")
            f.write(f"> **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"> **审计范围**: {self.layer_path}\n")
            f.write(f"> **审计标准**: 专业量化机构五大原则 + 三层审计标准\n")
            f.write(f"> **审计类型**: 全面深度审计（重复内容、职责清晰度）\n\n")
            
            f.write("---\n\n")
            
            # 审计概要
            f.write("## 1. 审计概要\n\n")
            f.write("### 1.1 审计范围\n\n")
            f.write(f"- **总文件数**: {self.stats['total_files']}\n")
            f.write(f"- **总目录数**: {self.stats['total_directories']}\n")
            f.write(f"- **发现问题数**: {self.stats['total_issues']}\n\n")
            
            f.write("### 1.2 问题分布\n\n")
            f.write(f"- **P0级问题（严重）**: {self.stats['critical_issues']}\n")
            f.write(f"- **P1级问题（重要）**: {self.stats['major_issues']}\n")
            f.write(f"- **P2级问题（次要）**: {self.stats['minor_issues']}\n\n")
            
            # L1审计结果
            f.write("## 2. L1文件系统层审计\n\n")
            self.write_section(f, 'L1_file_system', '文件系统层')
            
            # L2审计结果
            f.write("## 3. L2文档内容层审计\n\n")
            self.write_section(f, 'L2_document_content', '文档内容层')
            
            # L3审计结果
            f.write("## 4. L3专业标准层审计\n\n")
            self.write_section(f, 'L3_professional_standard', '专业标准层')
            
            # 深度内容检查
            f.write("## 5. 深度内容检查\n\n")
            self.write_section(f, 'deep_content_check', '深度内容检查')
            
            # 改进建议
            f.write("## 6. 改进建议\n\n")
            self.write_recommendations(f)
            
            # 附录
            f.write("## 7. 附录\n\n")
            f.write("### 7.1 审计标准\n\n")
            f.write("- 专业量化机构五大原则\n")
            f.write("- 三层审计标准（L1-L3）\n")
            f.write("- 文档治理审计问题清单\n\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print()
        print("=" * 80)
        print("审计报告已生成")
        print("=" * 80)
        print(f"报告位置: {report_path}")
    
    def write_section(self, f, layer, title):
        """写入章节"""
        categories = self.audit_results[layer]
        
        for category, issues in categories.items():
            if issues:
                category_name = category.replace('_', ' ').title()
                f.write(f"### {category_name}\n\n")
                
                for issue in issues:
                    severity = issue.get('severity', 'P2')
                    severity_emoji = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(severity, '⚪')
                    
                    f.write(f"{severity_emoji} **{issue['type']}**\n")
                    f.write(f"   - 文件: {issue['file']}\n")
                    f.write(f"   - 严重性: {severity}\n")
                    f.write(f"   - 描述: {issue['description']}\n")
                    f.write(f"   - 建议: {issue['suggestion']}\n\n")
    
    def write_recommendations(self, f):
        """写入改进建议"""
        # P0级问题
        if self.stats['critical_issues'] > 0:
            f.write("### 6.1 立即修复（P0级）\n\n")
            self.write_issues_by_severity(f, 'P0')
        
        # P1级问题
        if self.stats['major_issues'] > 0:
            f.write("### 6.2 短期改进（P1级）\n\n")
            self.write_issues_by_severity(f, 'P1')
        
        # P2级问题
        if self.stats['minor_issues'] > 0:
            f.write("### 6.3 长期优化（P2级）\n\n")
            self.write_issues_by_severity(f, 'P2')
    
    def write_issues_by_severity(self, f, severity):
        """按严重性写入问题"""
        for layer, categories in self.audit_results.items():
            for category, issues in categories.items():
                for issue in issues:
                    if issue.get('severity') == severity:
                        f.write(f"- **{issue['type']}**: {issue['file']}\n")
                        f.write(f"  - {issue['suggestion']}\n\n")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    auditor = ComprehensiveDeepAuditor(layer_path)
    auditor.run_full_audit()
    
    print()
    print("=" * 80)
    print("全面深度审计完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
