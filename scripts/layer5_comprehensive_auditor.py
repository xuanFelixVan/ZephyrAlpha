#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 全面深度审计工具
基于专业量化机构五大原则和三层审计标准
审计每一个文档的每一个内容
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict


class Layer5ComprehensiveAuditor:
    """Layer 5全面深度审计器"""
    
    def __init__(self):
        self.base_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.l1_issues = []
        self.l2_issues = []
        self.l3_issues = []
        self.duplicates = []
        self.responsibility_issues = []
        self.content_issues = []
        self.all_documents = {}
        self.module_ids = defaultdict(list)
        
    def read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        encodings = ['utf-8', 'gbk', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception:
                return ''
        
        return ''
    
    def scan_all_documents(self):
        """扫描所有文档"""
        print('\n📁 扫描所有文档...')
        
        md_files = list(self.base_dir.rglob('*.md'))
        
        for md_file in md_files:
            rel_path = md_file.relative_to(self.base_dir)
            content = self.read_file(md_file)
            
            if content:
                self.all_documents[str(rel_path)] = {
                    'path': md_file,
                    'content': content,
                    'size': len(content),
                    'lines': content.count('\n') + 1
                }
        
        print(f'  ✅ 扫描完成: {len(self.all_documents)}个文档')
    
    def audit_l1_filesystem(self):
        """L1文件系统层审计"""
        print('\n🔍 L1文件系统层审计...')
        
        print('  📂 检查目录结构...')
        self._check_directory_structure()
        
        print('  📝 检查文件命名...')
        self._check_file_naming()
        
        print('  🔗 检查路径引用...')
        self._check_path_references()
        
        print(f'  ✅ L1审计完成: 发现{len(self.l1_issues)}个问题')
    
    def _check_directory_structure(self):
        """检查目录结构"""
        expected_dirs = ['01_BLUEPRINTS', '02_IMPLEMENTATION_GUIDES', '03_OPERATION_MANUALS',
                        '04_CONFIG_TEMPLATES', '05_DESIGN_DOCS', '06_CHECKLISTS']
        
        actual_dirs = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        for expected in expected_dirs:
            if expected not in actual_dirs:
                self.l1_issues.append({
                    'type': '目录缺失',
                    'severity': 'P1',
                    'location': expected,
                    'description': f'缺少标准目录: {expected}'
                })
        
        for actual in actual_dirs:
            if actual not in expected_dirs and not actual.startswith('.'):
                self.l1_issues.append({
                    'type': '非标准目录',
                    'severity': 'P2',
                    'location': actual,
                    'description': f'存在非标准目录: {actual}'
                })
    
    def _check_file_naming(self):
        """检查文件命名"""
        old_architecture_keywords = ['Layer 0', 'Layer 1', 'Layer 2', 'Layer 3', 'Layer 4',
                                    'Layer 5', 'Layer 6', 'Layer 7', 'Layer 8']
        
        for doc_path, doc_info in self.all_documents.items():
            filename = Path(doc_path).name
            
            if ' ' in filename:
                self.l1_issues.append({
                    'type': '文件名包含空格',
                    'severity': 'P2',
                    'location': doc_path,
                    'description': f'文件名包含空格: {filename}'
                })
            
            for keyword in old_architecture_keywords:
                if keyword in filename:
                    self.l1_issues.append({
                        'type': '旧架构命名残留',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': f'文件名包含旧架构关键词: {keyword}'
                    })
                    break
    
    def _check_path_references(self):
        """检查路径引用"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            redundant_paths = re.findall(r'\.\./\.\./\.\./\.\.', content)
            if redundant_paths:
                self.l1_issues.append({
                    'type': '路径冗余',
                    'severity': 'P2',
                    'location': doc_path,
                    'description': f'发现冗余路径引用: ../../../..'
                })
            
            md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in md_links:
                if link_path.startswith('http'):
                    continue
                if link_path.startswith('#'):
                    continue
                    
                doc_dir = doc_info['path'].parent
                target_path = doc_dir / link_path
                
                if not target_path.exists():
                    self.l1_issues.append({
                        'type': '死链接',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': f'链接指向不存在的文件: {link_path}'
                    })
    
    def audit_l2_content(self):
        """L2文档内容层审计"""
        print('\n🔍 L2文档内容层审计...')
        
        print('  📋 检查职责驱动原则...')
        self._check_responsibility()
        
        print('  📚 检查索引完备性...')
        self._check_index_completeness()
        
        print('  🔄 检查版本隔离...')
        self._check_version_isolation()
        
        print('  🔗 检查文档代码对应...')
        self._check_doc_code_correspondence()
        
        print(f'  ✅ L2审计完成: 发现{len(self.l2_issues)}个问题')
    
    def _check_responsibility(self):
        """检查职责驱动原则"""
        responsibilities = {}
        
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            resp_match = re.search(r'^##\s+核心定位\s*\n\n(.+?)(?=\n##|\n#|\Z)', content, re.MULTILINE | re.DOTALL)
            
            if resp_match:
                responsibility = resp_match.group(1).strip()
                responsibilities[doc_path] = responsibility
                
                if len(responsibility) < 50:
                    self.l2_issues.append({
                        'type': '职责描述过短',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': f'职责描述长度: {len(responsibility)}字 (最少50字)'
                    })
                
                if len(responsibility) > 200:
                    self.l2_issues.append({
                        'type': '职责描述过长',
                        'severity': 'P2',
                        'location': doc_path,
                        'description': f'职责描述长度: {len(responsibility)}字 (最多200字)'
                    })
                
                vague_words = ['管理', '处理', '提供', '支持', '实现']
                vague_count = sum(1 for word in vague_words if word in responsibility)
                
                if vague_count >= 4:
                    self.responsibility_issues.append({
                        'type': '职责描述模糊',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': f'职责描述包含{vague_count}个模糊词汇'
                    })
            else:
                self.l2_issues.append({
                    'type': '缺少职责描述',
                    'severity': 'P1',
                    'location': doc_path,
                    'description': '文档缺少核心定位章节'
                })
        
        doc_list = list(responsibilities.items())
        for i, (doc1, resp1) in enumerate(doc_list):
            for doc2, resp2 in doc_list[i+1:]:
                similarity = SequenceMatcher(None, resp1, resp2).ratio()
                
                if similarity > 0.7:
                    self.duplicates.append({
                        'file1': doc1,
                        'file2': doc2,
                        'similarity': similarity,
                        'severity': 'P1' if similarity > 0.9 else 'P2',
                        'type': '职责描述相似'
                    })
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        root_index = self.base_dir / 'INDEX.md'
        
        if not root_index.exists():
            self.l2_issues.append({
                'type': '缺少主索引',
                'severity': 'P0',
                'location': '根目录',
                'description': '缺少根目录INDEX.md主入口文件'
            })
        else:
            index_content = self.read_file(root_index)
            
            for doc_path in self.all_documents.keys():
                doc_name = Path(doc_path).name
                if doc_name != 'INDEX.md' and doc_name not in index_content:
                    self.l2_issues.append({
                        'type': '索引不完整',
                        'severity': 'P2',
                        'location': 'INDEX.md',
                        'description': f'索引未包含文档: {doc_path}'
                    })
        
        for subdir in self.base_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                sub_index = subdir / 'INDEX.md'
                if not sub_index.exists():
                    self.l2_issues.append({
                        'type': '子目录缺少索引',
                        'severity': 'P1',
                        'location': str(subdir.relative_to(self.base_dir)),
                        'description': f'子目录缺少INDEX.md导航文件'
                    })
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                module_id_match = re.search(r'module_id:\s*(.+)', yaml_content)
                if module_id_match:
                    module_id = module_id_match.group(1).strip()
                    self.module_ids[module_id].append(doc_path)
        
        for module_id, docs in self.module_ids.items():
            if len(docs) > 1:
                self.l2_issues.append({
                    'type': 'module_id重复',
                    'severity': 'P1',
                    'location': ', '.join(docs),
                    'description': f'module_id "{module_id}" 在多个文档中重复使用'
                })
    
    def _check_doc_code_correspondence(self):
        """检查文档代码对应"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            code_refs = re.findall(r'```python\s*\n(.+?)```', content, re.DOTALL)
            
            for code_block in code_refs:
                if 'import ' in code_block:
                    imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', code_block)
                    for imp in imports:
                        module = imp[0] or imp[1]
                        if module.startswith('src.'):
                            src_path = Path('src') / (module.replace('.', '/') + '.py')
                            if not src_path.exists():
                                self.l2_issues.append({
                                    'type': '代码引用失效',
                                    'severity': 'P2',
                                    'location': doc_path,
                                    'description': f'引用的代码模块不存在: {module}'
                                })
    
    def audit_l3_standards(self):
        """L3专业标准层审计"""
        print('\n🔍 L3专业标准层审计...')
        
        print('  ⭐ 检查五大原则符合性...')
        self._check_five_principles()
        
        print('  📂 检查文档分类...')
        self._check_classification()
        
        print('  🔢 检查编号体系...')
        self._check_numbering()
        
        print('  📊 检查文档质量...')
        self._check_quality()
        
        print(f'  ✅ L3审计完成: 发现{len(self.l3_issues)}个问题')
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
            
            required_sections = ['核心定位', '设计目标']
            for section in required_sections:
                if section not in sections:
                    self.l3_issues.append({
                        'type': '缺少标准章节',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': f'缺少标准章节: {section}'
                    })
    
    def _check_classification(self):
        """检查文档分类"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                layer_match = re.search(r'layer:\s*(.+)', yaml_content)
                if layer_match:
                    layer = layer_match.group(1).strip()
                    if 'Layer 5' not in layer and 'Layer' in layer:
                        self.l3_issues.append({
                            'type': '分类层级错误',
                            'severity': 'P2',
                            'location': doc_path,
                            'description': f'文档层级标识错误: {layer}'
                        })
    
    def _check_numbering(self):
        """检查编号体系"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                if 'module_id:' not in yaml_content:
                    self.l3_issues.append({
                        'type': '缺少module_id',
                        'severity': 'P1',
                        'location': doc_path,
                        'description': '文档YAML头部缺少module_id字段'
                    })
                
                if 'version:' not in yaml_content:
                    self.l3_issues.append({
                        'type': '缺少版本号',
                        'severity': 'P2',
                        'location': doc_path,
                        'description': '文档YAML头部缺少version字段'
                    })
    
    def _check_quality(self):
        """检查文档质量"""
        for doc_path, doc_info in self.all_documents.items():
            content = doc_info['content']
            
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if not yaml_match:
                self.l3_issues.append({
                    'type': 'YAML头部缺失',
                    'severity': 'P1',
                    'location': doc_path,
                    'description': '文档缺少标准YAML元数据头部'
                })
            else:
                yaml_content = yaml_match.group(1)
                required_fields = ['module_id', 'version', 'status', 'created_date']
                
                for field in required_fields:
                    if f'{field}:' not in yaml_content:
                        self.l3_issues.append({
                            'type': 'YAML字段缺失',
                            'severity': 'P2',
                            'location': doc_path,
                            'description': f'YAML头部缺少必要字段: {field}'
                        })
            
            if len(content) < 500:
                self.l3_issues.append({
                    'type': '文档内容过短',
                    'severity': 'P2',
                    'location': doc_path,
                    'description': f'文档内容过短: {len(content)}字符'
                })
    
    def check_content_duplicates(self):
        """检查内容重复"""
        print('\n🔍 检查内容重复...')
        
        doc_list = list(self.all_documents.items())
        for i, (doc1_path, doc1_info) in enumerate(doc_list):
            for doc2_path, doc2_info in doc_list[i+1:]:
                content1 = doc1_info['content'][:2000]
                content2 = doc2_info['content'][:2000]
                
                similarity = SequenceMatcher(None, content1, content2).ratio()
                
                if similarity > 0.8:
                    self.content_issues.append({
                        'file1': doc1_path,
                        'file2': doc2_path,
                        'similarity': similarity,
                        'severity': 'P0' if similarity > 0.95 else 'P1',
                        'type': '内容高度相似'
                    })
        
        print(f'  ✅ 内容重复检测完成: 发现{len(self.content_issues)}对相似文档')
    
    def generate_report(self):
        """生成审计报告"""
        print('\n📊 生成审计报告...')
        
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.audit_dir / f'LAYER5_COMPREHENSIVE_AUDIT_REPORT_{timestamp}.md'
        
        total_issues = (len(self.l1_issues) + len(self.l2_issues) + len(self.l3_issues) + 
                       len(self.duplicates) + len(self.responsibility_issues) + len(self.content_issues))
        
        p0_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P0')
        p0_count += sum(1 for issue in self.content_issues if issue.get('severity') == 'P0')
        p1_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P1')
        p1_count += len(self.duplicates) + len(self.responsibility_issues)
        p1_count += sum(1 for issue in self.content_issues if issue.get('severity') == 'P1')
        p2_count = sum(1 for issue in self.l1_issues + self.l2_issues + self.l3_issues if issue.get('severity') == 'P2')
        p2_count += sum(1 for issue in self.content_issues if issue.get('severity') == 'P2')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 全面深度审计报告\n\n')
            f.write(f'> **审计时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'> **审计范围**: {self.base_dir}\n')
            f.write(f'> **审计类型**: 全面深度审计（三层审计标准）\n')
            f.write(f'> **审计状态**: ✅ 完成\n\n')
            
            f.write('---\n\n')
            f.write('## 📊 审计概要\n\n')
            f.write(f'- **扫描文档数**: {len(self.all_documents)}个\n')
            f.write(f'- **发现问题数**: {total_issues}个\n')
            f.write(f'- **P0问题**: {p0_count}个\n')
            f.write(f'- **P1问题**: {p1_count}个\n')
            f.write(f'- **P2问题**: {p2_count}个\n')
            f.write(f'- **重复文档对**: {len(self.duplicates)}对\n')
            f.write(f'- **职责问题**: {len(self.responsibility_issues)}个\n')
            f.write(f'- **内容相似**: {len(self.content_issues)}对\n\n')
            
            f.write('---\n\n')
            f.write('## 🔍 三层审计发现\n\n')
            
            f.write('### L1 文件系统层审计\n\n')
            f.write(f'发现问题: {len(self.l1_issues)}个\n\n')
            if self.l1_issues:
                self._write_issues(f, self.l1_issues, 'L1')
            else:
                f.write('✅ 无L1问题\n\n')
            
            f.write('### L2 文档内容层审计\n\n')
            f.write(f'发现问题: {len(self.l2_issues)}个\n\n')
            if self.l2_issues:
                self._write_issues(f, self.l2_issues, 'L2')
            else:
                f.write('✅ 无L2问题\n\n')
            
            f.write('### L3 专业标准层审计\n\n')
            f.write(f'发现问题: {len(self.l3_issues)}个\n\n')
            if self.l3_issues:
                self._write_issues(f, self.l3_issues, 'L3')
            else:
                f.write('✅ 无L3问题\n\n')
            
            f.write('---\n\n')
            f.write('## 🔄 重复内容检测\n\n')
            f.write(f'发现重复: {len(self.duplicates)}对\n\n')
            if self.duplicates:
                for i, dup in enumerate(self.duplicates, 1):
                    f.write(f'{i}. **{dup["file1"]}** ↔ **{dup["file2"]}**\n')
                    f.write(f'   - 相似度: {dup["similarity"]*100:.1f}%\n')
                    f.write(f'   - 严重程度: {dup["severity"]}\n')
                    f.write(f'   - 类型: {dup["type"]}\n\n')
            else:
                f.write('✅ 无重复内容\n\n')
            
            f.write('---\n\n')
            f.write('## 📝 职责清晰度检查\n\n')
            f.write(f'发现问题: {len(self.responsibility_issues)}个\n\n')
            if self.responsibility_issues:
                self._write_issues(f, self.responsibility_issues, '职责')
            else:
                f.write('✅ 无职责清晰度问题\n\n')
            
            f.write('---\n\n')
            f.write('## 📄 内容相似度检查\n\n')
            f.write(f'发现相似: {len(self.content_issues)}对\n\n')
            if self.content_issues:
                for i, issue in enumerate(self.content_issues, 1):
                    f.write(f'{i}. **{issue["file1"]}** ↔ **{issue["file2"]}**\n')
                    f.write(f'   - 相似度: {issue["similarity"]*100:.1f}%\n')
                    f.write(f'   - 严重程度: {issue["severity"]}\n')
                    f.write(f'   - 类型: {issue["type"]}\n\n')
            else:
                f.write('✅ 无内容相似问题\n\n')
            
            f.write('---\n\n')
            f.write(f'**审计完成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        print(f'  ✅ 审计报告已生成: {report_file}')
        return report_file
    
    def _write_issues(self, f, issues, category):
        """写入问题列表"""
        p0_issues = [i for i in issues if i.get('severity') == 'P0']
        p1_issues = [i for i in issues if i.get('severity') == 'P1']
        p2_issues = [i for i in issues if i.get('severity') == 'P2']
        
        if p0_issues:
            f.write('#### 🔴 P0 问题（立即修复）\n\n')
            for i, issue in enumerate(p0_issues, 1):
                f.write(f'{i}. **{issue["type"]}**: {issue["location"]}\n')
                f.write(f'   - {issue["description"]}\n\n')
        
        if p1_issues:
            f.write('#### 🟡 P1 问题（优先修复）\n\n')
            for i, issue in enumerate(p1_issues, 1):
                f.write(f'{i}. **{issue["type"]}**: {issue["location"]}\n')
                f.write(f'   - {issue["description"]}\n\n')
        
        if p2_issues:
            f.write('#### 🟢 P2 问题（建议修复）\n\n')
            for i, issue in enumerate(p2_issues, 1):
                f.write(f'{i}. **{issue["type"]}**: {issue["location"]}\n')
                f.write(f'   - {issue["description"]}\n\n')
    
    def run(self):
        """执行审计"""
        print('=' * 80)
        print('Layer 5 全面深度审计')
        print('基于专业量化机构五大原则和三层审计标准')
        print('=' * 80)
        
        self.scan_all_documents()
        
        self.audit_l1_filesystem()
        self.audit_l2_content()
        self.audit_l3_standards()
        self.check_content_duplicates()
        
        self.generate_report()
        
        print('\n' + '=' * 80)
        print('审计完成')
        print('=' * 80)
        print(f'\n📊 审计统计:')
        print(f'  - 扫描文档: {len(self.all_documents)}个')
        print(f'  - L1问题: {len(self.l1_issues)}个')
        print(f'  - L2问题: {len(self.l2_issues)}个')
        print(f'  - L3问题: {len(self.l3_issues)}个')
        print(f'  - 重复文档: {len(self.duplicates)}对')
        print(f'  - 职责问题: {len(self.responsibility_issues)}个')
        print(f'  - 内容相似: {len(self.content_issues)}对')


if __name__ == '__main__':
    auditor = Layer5ComprehensiveAuditor()
    auditor.run()
