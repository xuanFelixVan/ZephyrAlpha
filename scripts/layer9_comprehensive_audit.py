#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 9研究与创新层全面审计脚本
按照专业量化机构五大原则和三层审计标准进行全面审计
基于详细的文档治理审计问题清单
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple, Optional

class AuditIssue:
    """审计问题类"""
    def __init__(self, level: str, category: str, issue_type: str, 
                 description: str, file_path: str, severity: str, suggestion: str):
        self.level = level  # L1/L2/L3
        self.category = category  # 分类
        self.issue_type = issue_type  # 问题类型
        self.description = description  # 问题描述
        self.file_path = file_path  # 文件位置
        self.severity = severity  # 严重程度：严重/高/中/低
        self.suggestion = suggestion  # 改进建议

class DocumentInfo:
    """文档信息类"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.relative_path = os.path.relpath(file_path, 'docs/09_RESEARCH_INNOVATION')
        self.content = ''
        self.yaml_data = {}
        self.responsibility = ''
        self.module_id = ''
        self.version = ''
        self.has_yaml = False
        self.has_responsibility = False
        
    def load_content(self):
        """加载文档内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self._parse_yaml()
        except Exception as e:
            print(f"  ⚠️ 无法读取文件 {self.file_path}: {e}")
    
    def _parse_yaml(self):
        """解析YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---', self.content, re.DOTALL)
        if yaml_match:
            self.has_yaml = True
            yaml_content = yaml_match.group(1)
            
            # 提取responsibility
            resp_match = re.search(r'responsibility:\s*\n?\s*-\s*(.+?)(?:\n|$)', yaml_content, re.MULTILINE)
            if resp_match:
                self.responsibility = resp_match.group(1).strip()
                self.has_responsibility = True
            
            # 提取module_id
            module_match = re.search(r'module_id:\s*(.+?)(?:\n|$)', yaml_content)
            if module_match:
                self.module_id = module_match.group(1).strip()
            
            # 提取version
            version_match = re.search(r'version:\s*(.+?)(?:\n|$)', yaml_content)
            if version_match:
                self.version = version_match.group(1).strip()

class Layer9ComprehensiveAuditor:
    """Layer 9全面审计器"""
    
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.audit_issues: List[AuditIssue] = []
        self.documents: List[DocumentInfo] = []
        self.duplicate_pairs: List[Tuple[str, str, float]] = []
        self.responsibility_issues: List[Tuple[str, str]] = []
        
    def scan_documents(self):
        """扫描所有文档"""
        for root, dirs, files in os.walk(self.layer9_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    doc = DocumentInfo(full_path)
                    doc.load_content()
                    self.documents.append(doc)
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        print('  执行L1文件系统层审计...')
        
        # 1.1 目录结构问题
        self._check_directory_structure()
        
        # 1.2 文件命名问题
        self._check_file_naming()
        
        # 1.3 路径引用问题
        self._check_path_references()
    
    def _check_directory_structure(self):
        """检查目录结构问题"""
        # 检查目录稀疏
        for root, dirs, files in os.walk(self.layer9_dir):
            md_files = [f for f in files if f.endswith('.md')]
            if len(md_files) < 3 and root != self.layer9_dir:
                rel_path = os.path.relpath(root, self.layer9_dir)
                if len(md_files) == 0:
                    self.audit_issues.append(AuditIssue(
                        'L1', '目录结构', '空目录',
                        f'目录下没有任何文档文件',
                        root, '低', '考虑删除空目录或添加必要文档'
                    ))
                else:
                    self.audit_issues.append(AuditIssue(
                        'L1', '目录结构', '目录稀疏',
                        f'目录下只有 {len(md_files)} 个文档文件（<3个）',
                        root, '低', '考虑整合到父目录或增加相关文档'
                    ))
        
        # 检查目录层级深度
        for root, dirs, files in os.walk(self.layer9_dir):
            depth = root.replace(self.layer9_dir, '').count(os.sep)
            if depth > 4:
                self.audit_issues.append(AuditIssue(
                    'L1', '目录结构', '目录层级过深',
                    f'目录嵌套层级达到 {depth} 层（超过4层）',
                    root, '中', '考虑扁平化目录结构'
                ))
    
    def _check_file_naming(self):
        """检查文件命名问题"""
        for doc in self.documents:
            # 检查旧架构命名残留
            if re.search(r'Layer\s*[0-8]', doc.file_name):
                self.audit_issues.append(AuditIssue(
                    'L1', '文件命名', '旧架构命名残留',
                    f'文件名包含旧架构关键词（Layer 0-8）',
                    doc.file_path, '中', '更新为新的命名规范'
                ))
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', doc.file_name):
                self.audit_issues.append(AuditIssue(
                    'L1', '文件命名', '特殊字符问题',
                    f'文件名包含空格或中文字符',
                    doc.file_path, '中', '使用英文、数字、下划线命名'
                ))
            
            # 检查版本号缺失（归档文件除外）
            if '_archive' not in doc.file_path and not doc.version:
                self.audit_issues.append(AuditIssue(
                    'L1', '文件命名', '版本号缺失',
                    f'文档缺少版本标识',
                    doc.file_path, '低', '在YAML头部添加version字段'
                ))
    
    def _check_path_references(self):
        """检查路径引用问题"""
        for doc in self.documents:
            # 检查链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', doc.content)
            for link_text, link_path in links:
                # 检查路径冗余（过多../）
                if link_path.count('../') > 3:
                    self.audit_issues.append(AuditIssue(
                        'L1', '路径引用', '路径冗余',
                        f'链接使用过多相对路径引用（{link_path}）',
                        doc.file_path, '低', '简化路径引用'
                    ))
                
                # 检查死链接
                if link_path.endswith('.md') and not link_path.startswith('http'):
                    # 构建完整路径
                    doc_dir = os.path.dirname(doc.file_path)
                    full_link_path = os.path.normpath(os.path.join(doc_dir, link_path))
                    if not os.path.exists(full_link_path):
                        self.audit_issues.append(AuditIssue(
                            'L1', '路径引用', '死链接',
                            f'链接指向不存在的文件（{link_path}）',
                            doc.file_path, '高', '修复或删除无效链接'
                        ))
    
    def audit_l2_document_content(self):
        """L2文档内容层审计"""
        print('  执行L2文档内容层审计...')
        
        # 2.1 职责驱动原则问题
        self._check_responsibility_principle()
        
        # 2.2 索引完备性问题
        self._check_index_completeness()
        
        # 2.3 版本隔离问题
        self._check_version_isolation()
        
        # 2.4 文档代码对应问题
        self._check_document_code_correspondence()
    
    def _check_responsibility_principle(self):
        """检查职责驱动原则问题"""
        # 检查职责不清
        for doc in self.documents:
            if not doc.has_responsibility or len(doc.responsibility) < 20:
                self.audit_issues.append(AuditIssue(
                    'L2', '职责驱动', '职责不清',
                    f'文档缺少职责描述或职责描述过短（{len(doc.responsibility)}字）',
                    doc.file_path, '高', '添加清晰详细的职责描述（建议50-100字）'
                ))
        
        # 检查职责重叠
        responsibilities = [(doc.file_name, doc.responsibility) for doc in self.documents if doc.has_responsibility]
        for i, (name1, resp1) in enumerate(responsibilities):
            for name2, resp2 in responsibilities[i+1:]:
                similarity = SequenceMatcher(None, resp1, resp2).ratio()
                if similarity > 0.8:  # 80%相似度阈值
                    self.responsibility_issues.append((name1, name2))
                    self.audit_issues.append(AuditIssue(
                        'L2', '职责驱动', '职责重叠',
                        f'文档职责描述高度相似（{similarity:.1%}）',
                        f'{name1} <-> {name2}', '中', '区分文档职责，避免重叠'
                    ))
    
    def _check_index_completeness(self):
        """检查索引完备性问题"""
        # 检查主入口INDEX.md
        index_path = os.path.join(self.layer9_dir, 'INDEX.md')
        if not os.path.exists(index_path):
            self.audit_issues.append(AuditIssue(
                'L2', '索引完备', '入口混乱',
                '缺少主入口INDEX.md文件',
                self.layer9_dir, '严重', '创建INDEX.md主入口文件'
            ))
        else:
            # 检查索引完整性
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            for doc in self.documents:
                if doc.file_name != 'INDEX.md':
                    if doc.file_name not in index_content:
                        self.audit_issues.append(AuditIssue(
                            'L2', '索引完备', '索引不完整',
                            f'文档未被INDEX.md索引',
                            doc.file_path, '中', '在INDEX.md中添加文档索引'
                        ))
    
    def _check_version_isolation(self):
        """检查版本隔离问题"""
        # 检查重复文档（基于文件名相似度）
        file_names = [doc.file_name for doc in self.documents]
        for i, name1 in enumerate(file_names):
            for name2 in file_names[i+1:]:
                # 移除版本号后比较
                name1_base = re.sub(r'_v?\d+\.?\d*\.?\d*', '', name1)
                name2_base = re.sub(r'_v?\d+\.?\d*\.?\d*', '', name2)
                if name1_base == name2_base and name1 != name2:
                    self.audit_issues.append(AuditIssue(
                        'L2', '版本隔离', '重复文档',
                        f'存在相似文件名的文档（可能是不同版本）',
                        f'{name1} <-> {name2}', '中', '归档旧版本，仅保留最新版'
                    ))
    
    def _check_document_code_correspondence(self):
        """检查文档代码对应问题"""
        # 检查文档中提到的代码文件是否存在
        for doc in self.documents:
            # 查找代码文件引用
            code_refs = re.findall(r'`(src/[^`]+)`', doc.content)
            for code_ref in code_refs:
                if not os.path.exists(code_ref):
                    self.audit_issues.append(AuditIssue(
                        'L2', '文档代码对应', '文档描述代码不存在',
                        f'文档引用的代码文件不存在（{code_ref}）',
                        doc.file_path, '中', '更新文档或创建代码文件'
                    ))
    
    def audit_l3_professional_standard(self):
        """L3专业标准层审计"""
        print('  执行L3专业标准层审计...')
        
        # 3.1 五大原则符合性问题
        self._check_five_principles()
        
        # 3.2 文档分类问题
        self._check_document_classification()
        
        # 3.3 编号体系问题
        self._check_numbering_system()
        
        # 3.4 文档质量问题
        self._check_document_quality()
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        # 职责驱动原则已在L2检查
        # 索引完备性原则已在L2检查
        # 版本隔离原则已在L2检查
        
        # 检查命名规范原则
        for doc in self.documents:
            if not re.match(r'^[A-Z][A-Z0-9_]*\.md$', doc.file_name):
                if '_archive' not in doc.file_path:  # 归档文件例外
                    self.audit_issues.append(AuditIssue(
                        'L3', '五大原则', '命名规范不符合',
                        f'文件名不符合专业命名标准',
                        doc.file_path, '低', '使用大写字母、数字、下划线命名'
                    ))
    
    def _check_document_classification(self):
        """检查文档分类问题"""
        # 检查文档是否在正确的分类目录
        for doc in self.documents:
            # 检查归档文档
            if '_archive' in doc.file_path:
                if 'ACTIVE' in doc.content or 'status: Active' in doc.content:
                    self.audit_issues.append(AuditIssue(
                        'L3', '文档分类', '分类错误',
                        f'归档文档标记为Active状态',
                        doc.file_path, '中', '更新文档状态为Archived'
                    ))
    
    def _check_numbering_system(self):
        """检查编号体系问题"""
        module_ids = {}
        for doc in self.documents:
            if doc.module_id:
                if doc.module_id in module_ids:
                    self.audit_issues.append(AuditIssue(
                        'L3', '编号体系', '编号重复',
                        f'多个文档使用相同的module_id（{doc.module_id}）',
                        f'{module_ids[doc.module_id]} <-> {doc.file_path}', '高', '使用唯一的module_id'
                    ))
                else:
                    module_ids[doc.module_id] = doc.file_path
            else:
                if '_archive' not in doc.file_path:  # 归档文件例外
                    self.audit_issues.append(AuditIssue(
                        'L3', '编号体系', '编号缺失',
                        f'文档缺少module_id',
                        doc.file_path, '中', '在YAML头部添加module_id'
                    ))
    
    def _check_document_quality(self):
        """检查文档质量问题"""
        for doc in self.documents:
            # 检查YAML头部
            if not doc.has_yaml:
                self.audit_issues.append(AuditIssue(
                    'L3', '文档质量', 'YAML头部缺失',
                    f'文档缺少标准YAML元数据',
                    doc.file_path, '中', '添加标准YAML头部'
                ))
            else:
                # 检查YAML字段完整性
                required_fields = ['module_id', 'version', 'status', 'created_date', 'owner']
                missing_fields = []
                for field in required_fields:
                    if field not in doc.content[:500]:  # 只检查前500字符
                        missing_fields.append(field)
                
                if missing_fields:
                    self.audit_issues.append(AuditIssue(
                        'L3', '文档质量', 'YAML字段不完整',
                        f'YAML缺少必要字段（{", ".join(missing_fields)}）',
                        doc.file_path, '低', '补充缺失的YAML字段'
                    ))
            
            # 检查内容结构
            if len(doc.content) < 100:
                self.audit_issues.append(AuditIssue(
                    'L3', '文档质量', '内容过短',
                    f'文档内容过短（{len(doc.content)}字符）',
                    doc.file_path, '中', '补充文档内容'
                ))
    
    def detect_duplicate_content(self):
        """检测重复内容"""
        print('  检测重复内容...')
        
        # 基于内容相似度检测重复
        contents = [(doc.file_name, doc.content) for doc in self.documents if len(doc.content) > 100]
        
        for i, (name1, content1) in enumerate(contents):
            for name2, content2 in contents[i+1:]:
                similarity = SequenceMatcher(None, content1, content2).ratio()
                if similarity > 0.7:  # 70%内容相似度阈值
                    self.duplicate_pairs.append((name1, name2, similarity))
                    self.audit_issues.append(AuditIssue(
                        'L2', '版本隔离', '重复内容',
                        f'文档内容高度相似（{similarity:.1%}）',
                        f'{name1} <-> {name2}', '高', '归档旧版本或合并重复内容'
                    ))
    
    def detect_unclear_responsibility(self):
        """检测职责不清问题"""
        print('  检测职责不清问题...')
        
        # 检查职责描述中的模糊词汇
        vague_words = ['负责', '管理', '处理', '相关', '等', '各种', '其他']
        
        for doc in self.documents:
            if doc.has_responsibility:
                # 检查职责描述长度
                if len(doc.responsibility) < 30:
                    self.audit_issues.append(AuditIssue(
                        'L2', '职责驱动', '职责描述过短',
                        f'职责描述过短，无法清晰表达核心职责',
                        doc.file_path, '中', '扩展职责描述至50-100字'
                    ))
                
                # 检查模糊词汇使用过多
                vague_count = sum(1 for word in vague_words if word in doc.responsibility)
                if vague_count > 3:
                    self.audit_issues.append(AuditIssue(
                        'L2', '职责驱动', '职责描述模糊',
                        f'职责描述使用过多模糊词汇',
                        doc.file_path, '中', '使用更具体明确的表述'
                    ))
    
    def generate_report(self):
        """生成审计报告"""
        print('  生成审计报告...')
        
        # 统计问题
        total_issues = len(self.audit_issues)
        severe_issues = len([i for i in self.audit_issues if i.severity == '严重'])
        high_issues = len([i for i in self.audit_issues if i.severity == '高'])
        medium_issues = len([i for i in self.audit_issues if i.severity == '中'])
        low_issues = len([i for i in self.audit_issues if i.severity == '低'])
        
        # 按层级统计
        l1_issues = len([i for i in self.audit_issues if i.level == 'L1'])
        l2_issues = len([i for i in self.audit_issues if i.level == 'L2'])
        l3_issues = len([i for i in self.audit_issues if i.level == 'L3'])
        
        # 生成报告
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_path = f'docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_COMPREHENSIVE_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d")}.md'
        
        report_content = f"""# Layer 9 研究与创新层全面审计报告

> **审计时间**: {report_time}
> **审计范围**: {self.layer9_dir}
> **审计标准**: 专业量化机构文档治理五大原则 + 三层审计标准
> **审计类型**: 全面三层审计（L1-L3）+ 重复内容检测 + 职责不清检测

---

## 📊 一、审计概要

**审计文档数**: {len(self.documents)}个
**发现问题数**: {total_issues}个
**重复内容对**: {len(self.duplicate_pairs)}对
**职责不清问题**: {len(self.responsibility_issues)}个

### 1.1 问题分布

| 审计层级 | 问题数量 | 占比 |
|----------|----------|------|
| L1文件系统层 | {l1_issues} | {l1_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |
| L2文档内容层 | {l2_issues} | {l2_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |
| L3专业标准层 | {l3_issues} | {l3_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |

### 1.2 严重程度分布

| 严重程度 | 数量 | 占比 |
|----------|------|------|
| 严重 | {severe_issues} | {severe_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |
| 高 | {high_issues} | {high_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |
| 中 | {medium_issues} | {medium_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |
| 低 | {low_issues} | {low_issues/total_issues*100 if total_issues > 0 else 0:.1f}% |

---

## 📝 二、L1文件系统层审计结果

"""
        
        # 添加L1问题详情
        l1_issues_list = [i for i in self.audit_issues if i.level == 'L1']
        if l1_issues_list:
            for issue in l1_issues_list:
                severity_icon = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_content += f"""
### {severity_icon} {issue.category} - {issue.severity}

**问题描述**: {issue.issue_type} - {issue.description}
**文件位置**: {issue.file_path}
**改进建议**: {issue.suggestion}

"""
        else:
            report_content += "\n✅ 未发现L1文件系统层问题\n\n"
        
        report_content += "---\n\n## 📝 三、L2文档内容层审计结果\n\n"
        
        # 添加L2问题详情
        l2_issues_list = [i for i in self.audit_issues if i.level == 'L2']
        if l2_issues_list:
            for issue in l2_issues_list:
                severity_icon = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_content += f"""
### {severity_icon} {issue.category} - {issue.severity}

**问题描述**: {issue.issue_type} - {issue.description}
**文件位置**: {issue.file_path}
**改进建议**: {issue.suggestion}

"""
        else:
            report_content += "\n✅ 未发现L2文档内容层问题\n\n"
        
        report_content += "---\n\n## 📝 四、L3专业标准层审计结果\n\n"
        
        # 添加L3问题详情
        l3_issues_list = [i for i in self.audit_issues if i.level == 'L3']
        if l3_issues_list:
            for issue in l3_issues_list:
                severity_icon = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_content += f"""
### {severity_icon} {issue.category} - {issue.severity}

**问题描述**: {issue.issue_type} - {issue.description}
**文件位置**: {issue.file_path}
**改进建议**: {issue.suggestion}

"""
        else:
            report_content += "\n✅ 未发现L3专业标准层问题\n\n"
        
        report_content += "---\n\n## 🔄 五、重复内容检测结果\n\n"
        
        if self.duplicate_pairs:
            for name1, name2, similarity in self.duplicate_pairs:
                report_content += f"- **{name1}** <-> **{name2}**: {similarity:.1%}相似度\n"
        else:
            report_content += "\n✅ 未发现内容高度相似的文档\n"
        
        report_content += "\n---\n\n## ⚠️ 六、职责不清问题检测结果\n\n"
        
        if self.responsibility_issues:
            for name1, name2 in self.responsibility_issues:
                report_content += f"- **{name1}** <-> **{name2}**: 职责描述高度相似\n"
        else:
            report_content += "\n✅ 所有文档职责描述清晰\n"
        
        report_content += f"""
---

## 🎯 七、改进建议

### 严重问题（立即修复）

"""
        severe_list = [i for i in self.audit_issues if i.severity == '严重']
        if severe_list:
            for i, issue in enumerate(severe_list, 1):
                report_content += f"{i}. {issue.issue_type}: {issue.description} - {issue.suggestion}\n"
        else:
            report_content += "✅ 无严重问题\n"
        
        report_content += "\n### 高优先级问题（近期修复）\n\n"
        high_list = [i for i in self.audit_issues if i.severity == '高']
        if high_list:
            for i, issue in enumerate(high_list, 1):
                report_content += f"{i}. {issue.issue_type}: {issue.description} - {issue.suggestion}\n"
        else:
            report_content += "✅ 无高优先级问题\n"
        
        report_content += "\n### 中优先级问题（短期改进）\n\n"
        medium_list = [i for i in self.audit_issues if i.severity == '中']
        if medium_list:
            for i, issue in enumerate(medium_list, 1):
                report_content += f"{i}. {issue.issue_type}: {issue.description} - {issue.suggestion}\n"
        else:
            report_content += "✅ 无中优先级问题\n"
        
        report_content += "\n### 低优先级问题（长期优化）\n\n"
        low_list = [i for i in self.audit_issues if i.severity == '低']
        if low_list:
            for i, issue in enumerate(low_list, 1):
                report_content += f"{i}. {issue.issue_type}: {issue.description} - {issue.suggestion}\n"
        else:
            report_content += "✅ 无低优先级问题\n"
        
        report_content += f"""
---

**报告生成时间**: {report_time}
"""
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'  ✅ 报告已保存: {report_path}')
    
    def run_full_audit(self):
        """执行完整的三层审计"""
        print('=' * 80)
        print('Layer 9 研究与创新层全面审计')
        print('=' * 80)
        print(f'审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'审计范围: {self.layer9_dir}')
        print()
        
        print('阶段1: 扫描文档文件...')
        self.scan_documents()
        print(f'  ✅ 扫描到 {len(self.documents)} 个文档')
        print()
        
        print('阶段2: L1文件系统层审计...')
        self.audit_l1_file_system()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L1"])} 个问题')
        print()
        
        print('阶段3: L2文档内容层审计...')
        self.audit_l2_document_content()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L2"])} 个问题')
        print()
        
        print('阶段4: L3专业标准层审计...')
        self.audit_l3_professional_standard()
        print(f'  ✅ 发现 {len([i for i in self.audit_issues if i.level == "L3"])} 个问题')
        print()
        
        print('阶段5: 检测重复内容...')
        self.detect_duplicate_content()
        print(f'  ✅ 发现 {len(self.duplicate_pairs)} 对重复内容')
        print()
        
        print('阶段6: 检测职责不清问题...')
        self.detect_unclear_responsibility()
        print(f'  ✅ 发现 {len(self.responsibility_issues)} 个职责不清问题')
        print()
        
        print('阶段7: 生成审计报告...')
        self.generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('审计完成')
        print('=' * 80)
        
        self.print_summary()
    
    def print_summary(self):
        """打印审计摘要"""
        total_issues = len(self.audit_issues)
        severe_issues = len([i for i in self.audit_issues if i.severity == '严重'])
        high_issues = len([i for i in self.audit_issues if i.severity == '高'])
        medium_issues = len([i for i in self.audit_issues if i.severity == '中'])
        low_issues = len([i for i in self.audit_issues if i.severity == '低'])
        
        print()
        print('审计摘要:')
        print(f'  文档总数: {len(self.documents)}')
        print(f'  问题总数: {total_issues}')
        print(f'  重复内容: {len(self.duplicate_pairs)}对')
        print(f'  职责不清: {len(self.responsibility_issues)}个')
        print()
        print('问题分布:')
        print(f'  L1文件系统层: {len([i for i in self.audit_issues if i.level == "L1"])}')
        print(f'  L2文档内容层: {len([i for i in self.audit_issues if i.level == "L2"])}')
        print(f'  L3专业标准层: {len([i for i in self.audit_issues if i.level == "L3"])}')
        print()
        print('严重程度:')
        print(f'  严重: {severe_issues}')
        print(f'  高: {high_issues}')
        print(f'  中: {medium_issues}')
        print(f'  低: {low_issues}')

if __name__ == "__main__":
    auditor = Layer9ComprehensiveAuditor()
    auditor.run_full_audit()
