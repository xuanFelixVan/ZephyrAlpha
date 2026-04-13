#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
第25轮深度审计脚本 - Alpha因子层
功能：全面审计Alpha因子层的所有文档，重点检查重复内容和职责不清问题
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
ALPHA_FACTOR_DIR = DOCS_DIR / "02_FACTOR_LIBRARY"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

class Layer25DeepAudit:
    """第25轮深度审计器"""
    
    def __init__(self):
        self.documents = []
        self.l1_issues = []
        self.l2_issues = []
        self.l3_issues = []
        self.duplicates = []
        self.responsibility_issues = []
        
    def run_full_audit(self):
        """执行完整审计"""
        print("=" * 80)
        print("第25轮深度审计 - Alpha因子层")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {ALPHA_FACTOR_DIR}")
        print()
        
        # 阶段1: 扫描文档
        self._scan_documents()
        
        # 阶段2: L1文件系统层审计
        self._audit_l1_filesystem()
        
        # 阶段3: L2文档内容层审计
        self._audit_l2_content()
        
        # 阶段4: L3专业标准层审计
        self._audit_l3_standards()
        
        # 阶段5: 检测重复内容
        self._detect_duplicates()
        
        # 阶段6: 检测职责不清问题
        self._detect_responsibility_issues()
        
        # 阶段7: 生成报告
        self._generate_report()
        
        print()
        print("=" * 80)
        print("审计完成")
        print("=" * 80)
        
        self._print_summary()
    
    def _scan_documents(self):
        """扫描文档"""
        print("阶段1: 扫描文档文件...")
        
        for root, dirs, files in os.walk(ALPHA_FACTOR_DIR):
            # 排除特定目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    # 提取文档信息
                    doc_info = {
                        'path': rel_path,
                        'abs_path': file_path,
                        'content': content,
                        'size': len(content),
                        'lines': content.count('\n') + 1,
                        'has_yaml': content.startswith('---'),
                        'has_responsibility': '**核心职责**' in content,
                        'module_id': self._extract_module_id(content),
                        'title': self._extract_title(content),
                        'responsibility_text': self._extract_responsibility(content)
                    }
                    
                    self.documents.append(doc_info)
                except Exception as e:
                    print(f"  ⚠️ 无法读取文件: {rel_path} - {str(e)}")
        
        print(f"  ✅ 扫描到 {len(self.documents)} 个文档")
    
    def _extract_module_id(self, content):
        """提取Module ID"""
        match = re.search(r'module_id:\s*(.+)', content)
        return match.group(1).strip() if match else None
    
    def _extract_title(self, content):
        """提取标题"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _extract_responsibility(self, content):
        """提取职责描述"""
        match = re.search(r'\*\*核心职责\*\*:\s*(.+)', content)
        return match.group(1).strip() if match else None
    
    def _audit_l1_filesystem(self):
        """L1文件系统层审计"""
        print("阶段2: L1文件系统层审计...")
        
        # 检查目录结构
        self._check_directory_structure()
        
        # 检查文件命名
        self._check_file_naming()
        
        # 检查路径引用
        self._check_path_references()
        
        print(f"  ✅ 发现 {len(self.l1_issues)} 个问题")
    
    def _check_directory_structure(self):
        """检查目录结构"""
        # 检查稀疏目录
        for root, dirs, files in os.walk(ALPHA_FACTOR_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            md_files = [f for f in files if f.endswith('.md')]
            
            if len(md_files) < 3 and len(md_files) > 0:
                rel_path = os.path.relpath(root, DOCS_DIR)
                self.l1_issues.append({
                    'type': '稀疏目录',
                    'level': 'P2',
                    'path': rel_path,
                    'description': f'目录下仅有 {len(md_files)} 个文档，建议整合',
                    'suggestion': '考虑整合到父目录或补充必要文档'
                })
    
    def _check_file_naming(self):
        """检查文件命名"""
        for doc in self.documents:
            file_name = os.path.basename(doc['path'])
            
            # 检查中文
            if any('\u4e00' <= char <= '\u9fff' for char in file_name):
                self.l1_issues.append({
                    'type': '命名包含中文',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': f'文件名包含中文: {file_name}',
                    'suggestion': '使用英文命名'
                })
            
            # 检查空格
            if ' ' in file_name:
                self.l1_issues.append({
                    'type': '命名包含空格',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': f'文件名包含空格: {file_name}',
                    'suggestion': '使用下划线替代空格'
                })
            
            # 检查旧架构命名
            if re.search(r'Layer[_\s]*\d', file_name, re.IGNORECASE):
                self.l1_issues.append({
                    'type': '旧架构命名残留',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': f'文件名包含旧架构关键词: {file_name}',
                    'suggestion': '更新为新架构命名'
                })
    
    def _check_path_references(self):
        """检查路径引用"""
        for doc in self.documents:
            # 检查链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', doc['content'])
            
            for link_text, link_path in links:
                # 检查绝对路径
                if link_path.startswith('D:/') or link_path.startswith('D:\\'):
                    self.l1_issues.append({
                        'type': '绝对路径硬编码',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'使用绝对路径: {link_path}',
                        'suggestion': '使用相对路径'
                    })
                
                # 检查过多的../
                if link_path.count('../') > 3:
                    self.l1_issues.append({
                        'type': '路径冗余',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'路径层级过深: {link_path}',
                        'suggestion': '简化路径引用'
                    })
    
    def _audit_l2_content(self):
        """L2文档内容层审计"""
        print("阶段3: L2文档内容层审计...")
        
        # 检查职责驱动原则
        self._check_responsibility_principle()
        
        # 检查索引完备性
        self._check_index_completeness()
        
        # 检查版本隔离
        self._check_version_isolation()
        
        # 检查文档代码对应
        self._check_document_code_correspondence()
        
        print(f"  ✅ 发现 {len(self.l2_issues)} 个问题")
    
    def _check_responsibility_principle(self):
        """检查职责驱动原则"""
        # 检查职责描述缺失
        for doc in self.documents:
            if not doc['has_responsibility']:
                self.l2_issues.append({
                    'type': '职责描述缺失',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': '文档缺少核心职责描述',
                    'suggestion': '添加标准职责描述块'
                })
        
        # 检查职责重叠
        responsibility_map = defaultdict(list)
        for doc in self.documents:
            if doc['responsibility_text']:
                responsibility_map[doc['responsibility_text']].append(doc['path'])
        
        for responsibility, paths in responsibility_map.items():
            if len(paths) > 1:
                self.l2_issues.append({
                    'type': '职责重叠',
                    'level': 'P1',
                    'path': ', '.join(paths),
                    'description': f'{len(paths)} 个文档职责相同: {responsibility}',
                    'suggestion': '明确各文档职责边界或合并文档'
                })
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        # 检查INDEX.md是否存在
        for root, dirs, files in os.walk(ALPHA_FACTOR_DIR):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            if 'INDEX.md' not in files:
                rel_path = os.path.relpath(root, DOCS_DIR)
                md_files = [f for f in files if f.endswith('.md')]
                
                if len(md_files) > 0:
                    self.l2_issues.append({
                        'type': '索引缺失',
                        'level': 'P1',
                        'path': rel_path,
                        'description': '目录缺少INDEX.md导航文件',
                        'suggestion': '创建INDEX.md索引文件'
                    })
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        # 检查相似文件名（可能是重复版本）
        file_names = [os.path.basename(doc['path']) for doc in self.documents]
        name_groups = defaultdict(list)
        
        for name in file_names:
            # 移除版本号和日期
            base_name = re.sub(r'[_-]v?\d+[\.\d]*', '', name, flags=re.IGNORECASE)
            base_name = re.sub(r'[_-]\d{8}', '', base_name)
            name_groups[base_name].append(name)
        
        for base_name, names in name_groups.items():
            if len(names) > 1:
                self.l2_issues.append({
                    'type': '疑似重复版本',
                    'level': 'P2',
                    'path': ', '.join(names),
                    'description': f'发现 {len(names)} 个相似文件名',
                    'suggestion': '检查是否为重复版本，保留最新版本'
                })
    
    def _check_document_code_correspondence(self):
        """检查文档代码对应"""
        # 简化检查：检查文档中提到的代码文件是否存在
        for doc in self.documents:
            # 查找代码文件引用
            code_refs = re.findall(r'`([^`]+\.(py|js|ts|java|cpp))`', doc['content'])
            
            for code_file, ext in code_refs:
                # 检查代码文件是否存在
                code_path = PROJECT_ROOT / 'src' / code_file
                if not code_path.exists():
                    self.l2_issues.append({
                        'type': '代码文件缺失',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'引用的代码文件不存在: {code_file}',
                        'suggestion': '更新文档或创建代码文件'
                    })
    
    def _audit_l3_standards(self):
        """L3专业标准层审计"""
        print("阶段4: L3专业标准层审计...")
        
        # 检查五大原则符合性
        self._check_five_principles()
        
        # 检查文档分类
        self._check_document_classification()
        
        # 检查编号体系
        self._check_numbering_system()
        
        # 检查文档质量
        self._check_document_quality()
        
        print(f"  ✅ 发现 {len(self.l3_issues)} 个问题")
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        for doc in self.documents:
            # 职责驱动原则
            if not doc['has_responsibility']:
                self.l3_issues.append({
                    'type': '违反职责驱动原则',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': '缺少明确的职责描述',
                    'suggestion': '添加核心职责描述'
                })
            
            # 命名规范原则
            file_name = os.path.basename(doc['path'])
            if not re.match(r'^[A-Z_0-9]+\.md$', file_name) and file_name not in ['INDEX.md', 'README.md', 'ARCHITECTURE.md', 'SITEMAP.md']:
                self.l3_issues.append({
                    'type': '违反命名规范原则',
                    'level': 'P2',
                    'path': doc['path'],
                    'description': f'文件名不符合规范: {file_name}',
                    'suggestion': '使用标准命名格式'
                })
    
    def _check_document_classification(self):
        """检查文档分类"""
        # 检查文档是否在正确的分类目录
        for doc in self.documents:
            dir_path = os.path.dirname(doc['path'])
            
            # 检查是否在标准分类目录
            standard_dirs = [
                '01_STANDARDS', '02_BLUEPRINTS', '03_RISK_FACTORS',
                '04_ALPHA_FACTORS', '05_BACKTEST', '06_PRODUCTION'
            ]
            
            is_standard = any(std_dir in dir_path for std_dir in standard_dirs)
            
            if not is_standard and '02_FACTOR_LIBRARY' in dir_path:
                self.l3_issues.append({
                    'type': '分类不规范',
                    'level': 'P2',
                    'path': doc['path'],
                    'description': '文档不在标准分类目录',
                    'suggestion': '移动到正确的分类目录'
                })
    
    def _check_numbering_system(self):
        """检查编号体系"""
        # 检查Module ID
        module_ids = {}
        for doc in self.documents:
            if doc['module_id']:
                if doc['module_id'] in module_ids:
                    self.l3_issues.append({
                        'type': 'Module ID重复',
                        'level': 'P0',
                        'path': doc['path'],
                        'description': f'Module ID重复: {doc["module_id"]}',
                        'suggestion': '修改Module ID确保唯一性'
                    })
                else:
                    module_ids[doc['module_id']] = doc['path']
            else:
                self.l3_issues.append({
                    'type': 'Module ID缺失',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': '缺少Module ID',
                    'suggestion': '添加唯一的Module ID'
                })
    
    def _check_document_quality(self):
        """检查文档质量"""
        for doc in self.documents:
            # 检查YAML头部
            if not doc['has_yaml']:
                self.l3_issues.append({
                    'type': 'YAML头部缺失',
                    'level': 'P1',
                    'path': doc['path'],
                    'description': '缺少标准YAML头部',
                    'suggestion': '添加完整的YAML头部'
                })
            
            # 检查文档大小
            if doc['size'] < 500:
                self.l3_issues.append({
                    'type': '文档内容过少',
                    'level': 'P2',
                    'path': doc['path'],
                    'description': f'文档内容过少: {doc["size"]} 字节',
                    'suggestion': '补充文档内容或整合到其他文档'
                })
            
            # 检查文档结构
            if '##' not in doc['content']:
                self.l3_issues.append({
                    'type': '文档结构不完整',
                    'level': 'P2',
                    'path': doc['path'],
                    'description': '文档缺少章节结构',
                    'suggestion': '添加标准章节结构'
                })
    
    def _detect_duplicates(self):
        """检测重复内容"""
        print("阶段5: 检测重复内容...")
        
        # 使用内容哈希检测完全重复
        content_hashes = defaultdict(list)
        for doc in self.documents:
            # 移除空白字符后计算哈希
            normalized_content = re.sub(r'\s+', '', doc['content'])
            content_hash = hashlib.md5(normalized_content.encode()).hexdigest()
            content_hashes[content_hash].append(doc['path'])
        
        for content_hash, paths in content_hashes.items():
            if len(paths) > 1:
                self.duplicates.append({
                    'type': '完全重复',
                    'level': 'P0',
                    'paths': paths,
                    'description': f'{len(paths)} 个文档内容完全相同',
                    'suggestion': '删除重复文档，保留一个版本'
                })
        
        # 检测相似内容（使用标题和职责）
        title_map = defaultdict(list)
        for doc in self.documents:
            if doc['title']:
                title_map[doc['title']].append(doc['path'])
        
        for title, paths in title_map.items():
            if len(paths) > 1:
                self.duplicates.append({
                    'type': '标题重复',
                    'level': 'P1',
                    'paths': paths,
                    'description': f'{len(paths)} 个文档标题相同: {title}',
                    'suggestion': '检查是否为重复内容或明确职责差异'
                })
        
        print(f"  ✅ 发现 {len(self.duplicates)} 对重复内容")
    
    def _detect_responsibility_issues(self):
        """检测职责不清问题"""
        print("阶段6: 检测职责不清问题...")
        
        for doc in self.documents:
            # 检查职责描述是否模糊
            if doc['responsibility_text']:
                responsibility = doc['responsibility_text']
                
                # 检查职责描述是否过于简短
                if len(responsibility) < 10:
                    self.responsibility_issues.append({
                        'type': '职责描述过短',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'职责描述过于简短: {responsibility}',
                        'suggestion': '补充详细的职责描述'
                    })
                
                # 检查职责描述是否包含模糊词汇
                vague_words = ['管理', '处理', '相关', '等', '其他']
                if any(word in responsibility for word in vague_words):
                    self.responsibility_issues.append({
                        'type': '职责描述模糊',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'职责描述包含模糊词汇: {responsibility}',
                        'suggestion': '使用更具体的职责描述'
                    })
            
            # 检查文档内容是否超出职责范围
            if doc['responsibility_text'] and doc['title']:
                # 简单检查：标题和职责是否匹配
                responsibility_keywords = set(re.findall(r'[\u4e00-\u9fa5]+', doc['responsibility_text']))
                title_keywords = set(re.findall(r'[\u4e00-\u9fa5]+', doc['title']))
                
                common_keywords = responsibility_keywords & title_keywords
                
                if len(common_keywords) == 0:
                    self.responsibility_issues.append({
                        'type': '职责与标题不匹配',
                        'level': 'P2',
                        'path': doc['path'],
                        'description': f'职责描述与标题关键词不匹配',
                        'suggestion': '检查职责描述是否准确'
                    })
        
        print(f"  ✅ 发现 {len(self.responsibility_issues)} 个职责不清问题")
    
    def _generate_report(self):
        """生成审计报告"""
        print("阶段7: 生成审计报告...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = OUTPUT_DIR / f'LAYER25_DEEP_AUDIT_REPORT_{timestamp}.md'
        
        # 统计问题
        all_issues = self.l1_issues + self.l2_issues + self.l3_issues
        p0_count = sum(1 for issue in all_issues if issue.get('level') == 'P0')
        p1_count = sum(1 for issue in all_issues if issue.get('level') == 'P1')
        p2_count = sum(1 for issue in all_issues if issue.get('level') == 'P2')
        
        report_content = f"""---
module_id: LAYER25_DEEP_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 深度审计报告
applicable_scope: Alpha因子层全面审计
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 第25轮深度审计报告 - Alpha因子层

> **核心职责**: 全面审计Alpha因子层所有文档，发现并修复问题
> **职责边界**: 
> - ✅ 本文档负责：审计结果总结、问题分析、改进建议
> - ❌ 本文档不负责：具体问题修复执行

---

## 📋 审计概要

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: Alpha因子层 ({ALPHA_FACTOR_DIR})  
**审计方法**: 三层审计 + 重复检测 + 职责分析  
**审计结论**: 发现 {len(all_issues)} 个问题，{len(self.duplicates)} 对重复内容，{len(self.responsibility_issues)} 个职责不清问题

---

## 📊 审计统计

### 文档统计

| 指标 | 数量 |
|------|------|
| **文档总数** | {len(self.documents)} |
| **有YAML头部** | {sum(1 for doc in self.documents if doc['has_yaml'])} |
| **有职责描述** | {sum(1 for doc in self.documents if doc['has_responsibility'])} |
| **有Module ID** | {sum(1 for doc in self.documents if doc['module_id'])} |

### 问题统计

| 问题级别 | 数量 | 占比 |
|---------|------|------|
| **P0 严重** | {p0_count} | {p0_count/len(all_issues)*100 if all_issues else 0:.1f}% |
| **P1 高优先级** | {p1_count} | {p1_count/len(all_issues)*100 if all_issues else 0:.1f}% |
| **P2 中优先级** | {p2_count} | {p2_count/len(all_issues)*100 if all_issues else 0:.1f}% |
| **总计** | {len(all_issues)} | 100% |

---

## 🔍 L1 文件系统层审计结果

**发现问题**: {len(self.l1_issues)} 个

"""
        
        if self.l1_issues:
            for i, issue in enumerate(self.l1_issues[:30], 1):
                report_content += f"{i}. **{issue['type']}** ({issue['level']})\n"
                report_content += f"   - 路径: {issue['path']}\n"
                report_content += f"   - 描述: {issue['description']}\n"
                report_content += f"   - 建议: {issue['suggestion']}\n\n"
            
            if len(self.l1_issues) > 30:
                report_content += f"... 还有 {len(self.l1_issues) - 30} 个问题\n\n"
        else:
            report_content += "✅ 无L1层问题\n\n"
        
        report_content += f"""
---

## 🟡 L2 文档内容层审计结果

**发现问题**: {len(self.l2_issues)} 个

"""
        
        if self.l2_issues:
            for i, issue in enumerate(self.l2_issues[:30], 1):
                report_content += f"{i}. **{issue['type']}** ({issue['level']})\n"
                report_content += f"   - 路径: {issue['path']}\n"
                report_content += f"   - 描述: {issue['description']}\n"
                report_content += f"   - 建议: {issue['suggestion']}\n\n"
            
            if len(self.l2_issues) > 30:
                report_content += f"... 还有 {len(self.l2_issues) - 30} 个问题\n\n"
        else:
            report_content += "✅ 无L2层问题\n\n"
        
        report_content += f"""
---

## 🟢 L3 专业标准层审计结果

**发现问题**: {len(self.l3_issues)} 个

"""
        
        if self.l3_issues:
            for i, issue in enumerate(self.l3_issues[:30], 1):
                report_content += f"{i}. **{issue['type']}** ({issue['level']})\n"
                report_content += f"   - 路径: {issue['path']}\n"
                report_content += f"   - 描述: {issue['description']}\n"
                report_content += f"   - 建议: {issue['suggestion']}\n\n"
            
            if len(self.l3_issues) > 30:
                report_content += f"... 还有 {len(self.l3_issues) - 30} 个问题\n\n"
        else:
            report_content += "✅ 无L3层问题\n\n"
        
        report_content += f"""
---

## 🔄 重复内容检测结果

**发现重复**: {len(self.duplicates)} 对

"""
        
        if self.duplicates:
            for i, dup in enumerate(self.duplicates, 1):
                report_content += f"### {i}. {dup['type']} ({dup['level']})\n\n"
                report_content += f"**描述**: {dup['description']}\n\n"
                report_content += f"**文件列表**:\n"
                for path in dup['paths']:
                    report_content += f"- {path}\n"
                report_content += f"\n**建议**: {dup['suggestion']}\n\n"
                report_content += "---\n\n"
        else:
            report_content += "✅ 无重复内容\n\n"
        
        report_content += f"""
---

## ⚠️ 职责不清问题检测结果

**发现问题**: {len(self.responsibility_issues)} 个

"""
        
        if self.responsibility_issues:
            for i, issue in enumerate(self.responsibility_issues[:30], 1):
                report_content += f"{i}. **{issue['type']}** ({issue['level']})\n"
                report_content += f"   - 路径: {issue['path']}\n"
                report_content += f"   - 描述: {issue['description']}\n"
                report_content += f"   - 建议: {issue['suggestion']}\n\n"
            
            if len(self.responsibility_issues) > 30:
                report_content += f"... 还有 {len(self.responsibility_issues) - 30} 个问题\n\n"
        else:
            report_content += "✅ 无职责不清问题\n\n"
        
        report_content += f"""
---

## 💡 改进建议

### 立即修复（P0）

"""
        
        p0_issues = [issue for issue in all_issues if issue.get('level') == 'P0']
        if p0_issues:
            for issue in p0_issues:
                report_content += f"- **{issue['type']}**: {issue['path']}\n"
        else:
            report_content += "✅ 无P0级别问题\n"
        
        report_content += f"""
### 高优先级修复（P1）

"""
        
        p1_issues = [issue for issue in all_issues if issue.get('level') == 'P1']
        if p1_issues:
            report_content += f"共 {len(p1_issues)} 个P1级别问题，建议本周内修复\n"
        else:
            report_content += "✅ 无P1级别问题\n"
        
        report_content += f"""
### 中优先级优化（P2）

"""
        
        p2_issues = [issue for issue in all_issues if issue.get('level') == 'P2']
        if p2_issues:
            report_content += f"共 {len(p2_issues)} 个P2级别问题，建议本月内优化\n"
        else:
            report_content += "✅ 无P2级别问题\n"
        
        report_content += f"""
---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，第25轮深度审计报告 | 首席文档架构师 |
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  ✅ 报告已保存: {report_path}")
        
        # 保存JSON结果
        json_path = OUTPUT_DIR / f'LAYER25_DEEP_AUDIT_RESULT_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_documents': len(self.documents),
                'l1_issues': self.l1_issues,
                'l2_issues': self.l2_issues,
                'l3_issues': self.l3_issues,
                'duplicates': self.duplicates,
                'responsibility_issues': self.responsibility_issues,
                'summary': {
                    'total_issues': len(all_issues),
                    'p0_count': p0_count,
                    'p1_count': p1_count,
                    'p2_count': p2_count,
                    'duplicates_count': len(self.duplicates),
                    'responsibility_issues_count': len(self.responsibility_issues)
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ JSON结果已保存: {json_path}")
    
    def _print_summary(self):
        """打印审计摘要"""
        all_issues = self.l1_issues + self.l2_issues + self.l3_issues
        
        print("\n审计摘要:")
        print(f"  文档总数: {len(self.documents)}")
        print(f"  问题总数: {len(all_issues)}")
        print(f"  重复内容: {len(self.duplicates)}对")
        print(f"  职责不清: {len(self.responsibility_issues)}个")
        
        p0_count = sum(1 for issue in all_issues if issue.get('level') == 'P0')
        p1_count = sum(1 for issue in all_issues if issue.get('level') == 'P1')
        p2_count = sum(1 for issue in all_issues if issue.get('level') == 'P2')
        
        print(f"  严重问题: {p0_count}")
        print(f"  高优先级: {p1_count}")
        print(f"  中优先级: {p2_count}")

def main():
    """主函数"""
    auditor = Layer25DeepAudit()
    auditor.run_full_audit()

if __name__ == '__main__':
    main()
