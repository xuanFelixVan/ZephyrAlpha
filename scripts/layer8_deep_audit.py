#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 8 人机交互层深度审计脚本
执行三层审计：L1文件系统层、L2文档内容层、L3专业标准层
重点检查：重复内容、职责不清、文档质量
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8DeepAuditor:
    def __init__(self):
        self.audit_results = {
            "L1_file_system": {
                "directory_structure": [],
                "file_naming": [],
                "path_references": []
            },
            "L2_document_content": {
                "responsibility_issues": [],
                "index_completeness": [],
                "version_isolation": [],
                "doc_code_correspondence": []
            },
            "L3_professional_standards": {
                "five_principles": [],
                "classification": [],
                "numbering": [],
                "quality": []
            },
            "statistics": {
                "total_files": 0,
                "total_directories": 0,
                "total_size": 0,
                "issues_found": 0
            }
        }
        self.all_documents = []
        self.responsibility_map = defaultdict(list)
        self.content_hashes = {}
        
    def audit_all(self):
        """执行完整的三层审计"""
        print("=" * 80)
        print("Layer 8 人机交互层深度审计")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"审计范围: {BASE_DIR}")
        print("=" * 80)
        
        # L1: 文件系统层审计
        print("\n[阶段1] L1 文件系统层审计...")
        self.audit_l1_file_system()
        
        # L2: 文档内容层审计
        print("\n[阶段2] L2 文档内容层审计...")
        self.audit_l2_document_content()
        
        # L3: 专业标准层审计
        print("\n[阶段3] L3 专业标准层审计...")
        self.audit_l3_professional_standards()
        
        # 生成报告
        print("\n[阶段4] 生成审计报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成！")
        print(f"发现问题总数: {self.audit_results['statistics']['issues_found']}")
        print("=" * 80)
        
    def audit_l1_file_system(self):
        """L1: 文件系统层审计"""
        # 1.1 目录结构审计
        self.audit_directory_structure()
        
        # 1.2 文件命名审计
        self.audit_file_naming()
        
        # 1.3 路径引用审计
        self.audit_path_references()
        
    def audit_directory_structure(self):
        """审计目录结构"""
        print("  [1.1] 审计目录结构...")
        
        # 检查空目录
        for root, dirs, files in os.walk(BASE_DIR):
            root_path = Path(root)
            
            # 检查空目录
            if not files and not dirs:
                self.add_issue("L1", "directory_structure", {
                    "type": "空目录",
                    "path": str(root_path.relative_to(BASE_DIR)),
                    "severity": "P2",
                    "description": "目录存在但无内容",
                    "recommendation": "删除空目录或添加内容"
                })
            
            # 检查稀疏目录（文件数<3）
            elif len(files) < 3 and len(files) > 0:
                # 排除蓝图目录（通常只有1-2个文件是正常的）
                if "BLUEPRINT" not in root_path.name:
                    self.add_issue("L1", "directory_structure", {
                        "type": "稀疏目录",
                        "path": str(root_path.relative_to(BASE_DIR)),
                        "severity": "P2",
                        "description": f"目录下文件过少（{len(files)}个）",
                        "recommendation": "考虑整合到父目录或添加更多文件"
                    })
            
            # 检查目录层级深度
            depth = len(root_path.relative_to(BASE_DIR).parts)
            if depth > 4:
                self.add_issue("L1", "directory_structure", {
                    "type": "层级过深",
                    "path": str(root_path.relative_to(BASE_DIR)),
                    "severity": "P2",
                    "description": f"目录层级过深（{depth}层）",
                    "recommendation": "考虑扁平化目录结构"
                })
            
            self.audit_results["statistics"]["total_directories"] += 1
    
    def audit_file_naming(self):
        """审计文件命名"""
        print("  [1.2] 审计文件命名...")
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BASE_DIR)
                
                # 统计文件
                self.audit_results["statistics"]["total_files"] += 1
                self.audit_results["statistics"]["total_size"] += file_path.stat().st_size
                
                # 检查文件命名规范
                if file.endswith('.md'):
                    # 检查是否包含旧架构关键词
                    old_keywords = ['Layer 0', 'Layer 1', 'Layer 2', 'Layer 3', 'Layer 4',
                                   'Layer 5', 'Layer 6', 'Layer 7', 'Layer 8', 'Layer 9',
                                   'Layer 10', 'Layer 11', 'LAYER0', 'LAYER1', 'LAYER2']
                    for keyword in old_keywords:
                        if keyword in file:
                            self.add_issue("L1", "file_naming", {
                                "type": "旧架构命名残留",
                                "file": str(rel_path),
                                "severity": "P1",
                                "description": f"文件名包含旧架构关键词: {keyword}",
                                "recommendation": "更新文件名以符合新架构"
                            })
                            break
                    
                    # 检查特殊字符
                    if ' ' in file or any(ord(c) > 127 for c in file if c not in '中文'):
                        self.add_issue("L1", "file_naming", {
                            "type": "特殊字符问题",
                            "file": str(rel_path),
                            "severity": "P2",
                            "description": "文件名包含空格或特殊字符",
                            "recommendation": "使用下划线或连字符替代"
                        })
    
    def audit_path_references(self):
        """审计路径引用"""
        print("  [1.3] 审计路径引用...")
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 检查路径引用
                        # 检查过多的 ../
                        if content.count('../') > 5:
                            self.add_issue("L1", "path_references", {
                                "type": "路径冗余",
                                "file": str(rel_path),
                                "severity": "P2",
                                "description": f"使用过多 ../ 相对路径（{content.count('../')}次）",
                                "recommendation": "简化路径引用"
                            })
                        
                        # 检查死链接
                        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                        for link_text, link_path in links:
                            if link_path.startswith('http') or link_path.startswith('#'):
                                continue
                            
                            # 检查相对路径是否存在
                            target_path = (file_path.parent / link_path).resolve()
                            if not target_path.exists():
                                self.add_issue("L1", "path_references", {
                                    "type": "死链接",
                                    "file": str(rel_path),
                                    "severity": "P1",
                                    "description": f"链接不存在: [{link_text}]({link_path})",
                                    "recommendation": "修复或删除死链接"
                                })
                    except Exception as e:
                        print(f"    [警告] 无法读取文件: {rel_path} - {e}")
    
    def audit_l2_document_content(self):
        """L2: 文档内容层审计"""
        # 2.1 职责驱动原则审计
        self.audit_responsibility()
        
        # 2.2 索引完备性审计
        self.audit_index_completeness()
        
        # 2.3 版本隔离审计
        self.audit_version_isolation()
        
        # 2.4 文档代码对应审计
        self.audit_doc_code_correspondence()
    
    def audit_responsibility(self):
        """审计职责驱动原则"""
        print("  [2.1] 审计职责驱动原则...")
        
        # 收集所有文档的职责信息
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取YAML元数据
                        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            
                            # 提取responsibility
                            resp_match = re.search(r'responsibility:\s*\n((?:\s+-.*\n)+)', yaml_content)
                            if resp_match:
                                responsibilities = []
                                for line in resp_match.group(1).strip().split('\n'):
                                    if line.strip().startswith('-'):
                                        resp = line.strip()[1:].strip()
                                        responsibilities.append(resp)
                                
                                # 记录职责映射
                                for resp in responsibilities:
                                    self.responsibility_map[resp].append(str(rel_path))
                                
                                # 检查职责数量
                                if len(responsibilities) > 3:
                                    self.add_issue("L2", "responsibility_issues", {
                                        "type": "职责过多",
                                        "file": str(rel_path),
                                        "severity": "P1",
                                        "description": f"文档承担{len(responsibilities)}项职责，建议单一职责",
                                        "responsibilities": responsibilities,
                                        "recommendation": "拆分文档或合并职责"
                                    })
                            else:
                                self.add_issue("L2", "responsibility_issues", {
                                    "type": "职责缺失",
                                    "file": str(rel_path),
                                    "severity": "P1",
                                    "description": "文档缺少responsibility字段",
                                    "recommendation": "添加明确的职责描述"
                                })
                        
                        # 计算内容哈希
                        content_hash = hashlib.md5(content.encode()).hexdigest()
                        if content_hash in self.content_hashes:
                            self.add_issue("L2", "responsibility_issues", {
                                "type": "重复内容",
                                "file": str(rel_path),
                                "severity": "P0",
                                "description": f"与 {self.content_hashes[content_hash]} 内容完全相同",
                                "recommendation": "删除重复文档或合并内容"
                            })
                        else:
                            self.content_hashes[content_hash] = str(rel_path)
                        
                        # 保存文档信息
                        self.all_documents.append({
                            "path": str(rel_path),
                            "size": len(content),
                            "lines": content.count('\n'),
                            "has_yaml": bool(yaml_match)
                        })
                        
                    except Exception as e:
                        print(f"    [警告] 无法分析文件: {rel_path} - {e}")
        
        # 检查职责重叠
        for resp, files in self.responsibility_map.items():
            if len(files) > 1:
                self.add_issue("L2", "responsibility_issues", {
                    "type": "职责重叠",
                    "severity": "P1",
                    "description": f"职责 '{resp}' 被 {len(files)} 个文档共享",
                    "files": files,
                    "recommendation": "明确各文档的职责边界或合并文档"
                })
    
    def audit_index_completeness(self):
        """审计索引完备性"""
        print("  [2.2] 审计索引完备性...")
        
        # 检查主索引
        main_index = BASE_DIR / "INDEX.md"
        if not main_index.exists():
            self.add_issue("L2", "index_completeness", {
                "type": "缺少主索引",
                "severity": "P0",
                "description": "Layer 8缺少主入口INDEX.md",
                "recommendation": "创建主索引文档"
            })
        else:
            # 检查索引完整性
            with open(main_index, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            # 获取所有实际文件
            actual_files = set()
            for root, dirs, files in os.walk(BASE_DIR):
                for file in files:
                    if file.endswith('.md') and file != 'INDEX.md':
                        file_path = Path(root) / file
                        rel_path = file_path.relative_to(BASE_DIR)
                        actual_files.add(str(rel_path))
            
            # 检查索引中引用的文件
            indexed_files = set()
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', index_content)
            for _, link in links:
                if link.endswith('.md') and not link.startswith('http'):
                    indexed_files.add(link)
            
            # 检查未索引的文件
            unindexed = actual_files - indexed_files
            if unindexed:
                self.add_issue("L2", "index_completeness", {
                    "type": "索引不完整",
                    "severity": "P1",
                    "description": f"{len(unindexed)}个文件未被索引",
                    "files": list(unindexed)[:10],  # 只显示前10个
                    "recommendation": "更新INDEX.md以包含所有活跃文档"
                })
        
        # 检查子目录索引
        for root, dirs, files in os.walk(BASE_DIR):
            if root != str(BASE_DIR):
                sub_index = Path(root) / "INDEX.md"
                if not sub_index.exists() and files:
                    # 检查是否有.md文件
                    md_files = [f for f in files if f.endswith('.md')]
                    if len(md_files) > 2:  # 超过2个md文件应该有索引
                        self.add_issue("L2", "index_completeness", {
                            "type": "子目录缺索引",
                            "severity": "P2",
                            "description": f"子目录缺少INDEX.md导航文件",
                            "path": str(Path(root).relative_to(BASE_DIR)),
                            "recommendation": "创建子目录索引文档"
                        })
    
    def audit_version_isolation(self):
        """审计版本隔离"""
        print("  [2.3] 审计版本隔离...")
        
        # 检查重复文档（通过文件名相似性）
        file_names = defaultdict(list)
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    # 提取基础名称（去掉版本号）
                    base_name = re.sub(r'_v?\d+\.?\d*\.md$', '.md', file)
                    base_name = re.sub(r'_\d{8}_\d{6}\.md$', '.md', base_name)
                    file_names[base_name].append(file)
        
        # 检查重复
        for base_name, files in file_names.items():
            if len(files) > 1:
                self.add_issue("L2", "version_isolation", {
                    "type": "潜在重复文档",
                    "severity": "P1",
                    "description": f"发现{len(files)}个相似文件名",
                    "base_name": base_name,
                    "files": files,
                    "recommendation": "检查是否为重复版本，归档旧版本"
                })
    
    def audit_doc_code_correspondence(self):
        """审计文档代码对应"""
        print("  [2.4] 审计文档代码对应...")
        
        # 检查蓝图文档是否引用了实际代码
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if 'BLUEPRINT' in file and file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否引用了代码文件
                        code_refs = re.findall(r'```(?:python|typescript|javascript)', content)
                        if not code_refs:
                            self.add_issue("L2", "doc_code_correspondence", {
                                "type": "蓝图缺少代码示例",
                                "file": str(rel_path),
                                "severity": "P2",
                                "description": "蓝图文档缺少代码示例",
                                "recommendation": "添加实现代码示例"
                            })
                    except Exception as e:
                        print(f"    [警告] 无法检查文件: {rel_path} - {e}")
    
    def audit_l3_professional_standards(self):
        """L3: 专业标准层审计"""
        # 3.1 五大原则符合性审计
        self.audit_five_principles()
        
        # 3.2 文档分类审计
        self.audit_classification()
        
        # 3.3 编号体系审计
        self.audit_numbering()
        
        # 3.4 文档质量审计
        self.audit_quality()
    
    def audit_five_principles(self):
        """审计五大原则符合性"""
        print("  [3.1] 审计五大原则符合性...")
        
        # 职责驱动原则
        # 已在L2审计中检查
        
        # 索引完备性原则
        # 已在L2审计中检查
        
        # 版本隔离原则
        # 已在L2审计中检查
        
        # 文档代码对应原则
        # 已在L2审计中检查
        
        # 命名规范原则
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    # 检查命名是否规范
                    if not re.match(r'^[A-Z_0-9]+\.md$', file):
                        # 允许index.md和特殊文件
                        if file.lower() not in ['index.md', 'readme.md']:
                            self.add_issue("L3", "five_principles", {
                                "type": "命名不规范",
                                "file": str(rel_path),
                                "severity": "P2",
                                "description": "文件名不符合命名规范",
                                "recommendation": "使用大写字母和下划线命名"
                            })
    
    def audit_classification(self):
        """审计文档分类"""
        print("  [3.2] 审计文档分类...")
        
        # 检查目录分类是否合理
        expected_categories = [
            "01_MONITORING", "02_ALERTING", "03_AUTH", "04_API_DOCS",
            "05_BACKTEST_UI", "06_REPORTING", "07_AUDIT_LOG",
            "24_RISK_DASHBOARD", "25_STRATEGY_IDE", "26_FACTOR_ANALYSIS"
        ]
        
        actual_categories = []
        for item in BASE_DIR.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                actual_categories.append(item.name)
        
        # 检查是否有未预期的分类
        for category in actual_categories:
            if not any(cat in category for cat in ["MONITORING", "ALERTING", "AUTH", "API", 
                                                     "BACKTEST", "REPORTING", "AUDIT", "RISK",
                                                     "STRATEGY", "FACTOR", "USER", "COMPLIANCE",
                                                     "CAPITAL", "I18N", "THEME", "DATA", "TRAINING",
                                                     "ACCESSIBILITY", "OFFLINE", "THIRD_PARTY"]):
                self.add_issue("L3", "classification", {
                    "type": "分类可能不当",
                    "severity": "P2",
                    "description": f"目录分类 '{category}' 可能不符合标准",
                    "recommendation": "检查分类是否正确"
                })
    
    def audit_numbering(self):
        """审计编号体系"""
        print("  [3.3] 审计编号体系...")
        
        module_ids = defaultdict(list)
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取module_id
                        module_id_match = re.search(r'module_id:\s*(\S+)', content)
                        if module_id_match:
                            module_id = module_id_match.group(1)
                            module_ids[module_id].append(str(rel_path))
                        else:
                            self.add_issue("L3", "numbering", {
                                "type": "缺少module_id",
                                "file": str(rel_path),
                                "severity": "P1",
                                "description": "文档缺少module_id标识",
                                "recommendation": "添加标准的module_id"
                            })
                    except Exception as e:
                        print(f"    [警告] 无法检查文件: {rel_path} - {e}")
        
        # 检查重复的module_id
        for module_id, files in module_ids.items():
            if len(files) > 1:
                self.add_issue("L3", "numbering", {
                    "type": "module_id重复",
                    "severity": "P0",
                    "description": f"module_id '{module_id}' 被 {len(files)} 个文档使用",
                    "files": files,
                    "recommendation": "为每个文档分配唯一的module_id"
                })
    
    def audit_quality(self):
        """审计文档质量"""
        print("  [3.4] 审计文档质量...")
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查YAML头部
                        if not content.startswith('---'):
                            self.add_issue("L3", "quality", {
                                "type": "YAML头部缺失",
                                "file": str(rel_path),
                                "severity": "P1",
                                "description": "文档缺少标准YAML元数据",
                                "recommendation": "添加完整的YAML头部"
                            })
                        else:
                            # 检查YAML字段完整性
                            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                            if yaml_match:
                                yaml_content = yaml_match.group(1)
                                required_fields = ['module_id', 'version', 'status', 'owner']
                                
                                for field in required_fields:
                                    if field not in yaml_content:
                                        self.add_issue("L3", "quality", {
                                            "type": "YAML字段不完整",
                                            "file": str(rel_path),
                                            "severity": "P2",
                                            "description": f"YAML缺少必要字段: {field}",
                                            "recommendation": f"添加{field}字段"
                                        })
                        
                        # 检查文档长度
                        lines = content.count('\n')
                        if lines > 500:
                            self.add_issue("L3", "quality", {
                                "type": "文档过长",
                                "file": str(rel_path),
                                "severity": "P2",
                                "description": f"文档过长（{lines}行），建议拆分",
                                "recommendation": "拆分为多个小文档"
                            })
                        
                    except Exception as e:
                        print(f"    [警告] 无法检查文件: {rel_path} - {e}")
    
    def add_issue(self, layer, category, issue):
        """添加问题"""
        # 映射简写层名到完整层名
        layer_map = {
            "L1": "L1_file_system",
            "L2": "L2_document_content",
            "L3": "L3_professional_standards"
        }
        full_layer = layer_map.get(layer, layer)
        self.audit_results[full_layer][category].append(issue)
        self.audit_results["statistics"]["issues_found"] += 1
    
    def generate_report(self):
        """生成审计报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_DEEP_AUDIT_REPORT_{timestamp}.md"
        
        # 统计问题
        p0_issues = []
        p1_issues = []
        p2_issues = []
        
        for layer in ['L1_file_system', 'L2_document_content', 'L3_professional_standards']:
            for category, issues in self.audit_results[layer].items():
                for issue in issues:
                    severity = issue.get('severity', 'P2')
                    if severity == 'P0':
                        p0_issues.append((layer, category, issue))
                    elif severity == 'P1':
                        p1_issues.append((layer, category, issue))
                    else:
                        p2_issues.append((layer, category, issue))
        
        # 生成报告
        report = f"""---
module_id: LAYER8_DEEP_AUDIT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8深度审计报告
standard_type: 审计报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 人机交互层深度审计报告

**审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计范围**: {BASE_DIR}  
**审计标准**: 专业量化机构五大原则 + 三层审计标准  
**审计类型**: 深度审计（全文档全内容）

---

## 📊 审计概要

### 统计信息

| 指标 | 数值 |
|------|------|
| **审计文件总数** | {self.audit_results['statistics']['total_files']} |
| **审计目录总数** | {self.audit_results['statistics']['total_directories']} |
| **总文件大小** | {self.audit_results['statistics']['total_size'] / 1024:.2f} KB |
| **发现问题总数** | {self.audit_results['statistics']['issues_found']} |
| **P0级问题** | {len(p0_issues)} |
| **P1级问题** | {len(p1_issues)} |
| **P2级问题** | {len(p2_issues)} |

### 问题分布

| 优先级 | 数量 | 占比 | 说明 |
|--------|------|------|------|
| **P0（紧急）** | {len(p0_issues)} | {len(p0_issues)/max(1,self.audit_results['statistics']['issues_found'])*100:.1f}% | 必须立即修复 |
| **P1（重要）** | {len(p1_issues)} | {len(p1_issues)/max(1,self.audit_results['statistics']['issues_found'])*100:.1f}% | 本周内修复 |
| **P2（一般）** | {len(p2_issues)} | {len(p2_issues)/max(1,self.audit_results['statistics']['issues_found'])*100:.1f}% | 本月内修复 |

---

## 🔴 P0级问题（紧急 - 必须立即修复）

"""
        
        if p0_issues:
            for i, (layer, category, issue) in enumerate(p0_issues, 1):
                report += f"""
### 问题 {i}: {issue['type']}

- **层级**: {layer} / {category}
- **文件**: {issue.get('file', 'N/A')}
- **描述**: {issue['description']}
- **建议**: {issue['recommendation']}

"""
        else:
            report += "\n✅ **无P0级问题**\n\n"
        
        report += f"""
---

## 🟡 P1级问题（重要 - 本周内修复）

"""
        
        if p1_issues:
            for i, (layer, category, issue) in enumerate(p1_issues[:20], 1):  # 只显示前20个
                report += f"""
### 问题 {i}: {issue['type']}

- **层级**: {layer} / {category}
- **文件**: {issue.get('file', 'N/A')}
- **描述**: {issue['description']}
- **建议**: {issue['recommendation']}

"""
            if len(p1_issues) > 20:
                report += f"\n*还有 {len(p1_issues) - 20} 个P1级问题未显示*\n\n"
        else:
            report += "\n✅ **无P1级问题**\n\n"
        
        report += f"""
---

## 🟢 P2级问题（一般 - 本月内修复）

"""
        
        if p2_issues:
            report += f"\n**总计**: {len(p2_issues)} 个P2级问题\n\n"
            report += "**问题类型分布**:\n"
            p2_types = defaultdict(int)
            for _, _, issue in p2_issues:
                p2_types[issue['type']] += 1
            for issue_type, count in sorted(p2_types.items(), key=lambda x: -x[1]):
                report += f"- {issue_type}: {count}个\n"
        else:
            report += "\n✅ **无P2级问题**\n\n"
        
        report += f"""
---

## 📋 详细审计结果

### L1 文件系统层审计

#### 1.1 目录结构问题

"""
        
        dir_issues = self.audit_results['L1_file_system']['directory_structure']
        if dir_issues:
            for issue in dir_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('path', issue.get('file', 'N/A'))} - {issue['description']}\n"
        else:
            report += "✅ 无目录结构问题\n"
        
        report += """
#### 1.2 文件命名问题

"""
        
        naming_issues = self.audit_results['L1_file_system']['file_naming']
        if naming_issues:
            for issue in naming_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无文件命名问题\n"
        
        report += """
#### 1.3 路径引用问题

"""
        
        path_issues = self.audit_results['L1_file_system']['path_references']
        if path_issues:
            for issue in path_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无路径引用问题\n"
        
        report += """
### L2 文档内容层审计

#### 2.1 职责驱动原则问题

"""
        
        resp_issues = self.audit_results['L2_document_content']['responsibility_issues']
        if resp_issues:
            for issue in resp_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无职责驱动原则问题\n"
        
        report += """
#### 2.2 索引完备性问题

"""
        
        index_issues = self.audit_results['L2_document_content']['index_completeness']
        if index_issues:
            for issue in index_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', issue.get('path', 'N/A'))} - {issue['description']}\n"
        else:
            report += "✅ 无索引完备性问题\n"
        
        report += """
#### 2.3 版本隔离问题

"""
        
        version_issues = self.audit_results['L2_document_content']['version_isolation']
        if version_issues:
            for issue in version_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('base_name', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无版本隔离问题\n"
        
        report += """
#### 2.4 文档代码对应问题

"""
        
        doc_code_issues = self.audit_results['L2_document_content']['doc_code_correspondence']
        if doc_code_issues:
            for issue in doc_code_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无文档代码对应问题\n"
        
        report += """
### L3 专业标准层审计

#### 3.1 五大原则符合性问题

"""
        
        principles_issues = self.audit_results['L3_professional_standards']['five_principles']
        if principles_issues:
            for issue in principles_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无五大原则符合性问题\n"
        
        report += """
#### 3.2 文档分类问题

"""
        
        class_issues = self.audit_results['L3_professional_standards']['classification']
        if class_issues:
            for issue in class_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('severity', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无文档分类问题\n"
        
        report += """
#### 3.3 编号体系问题

"""
        
        numbering_issues = self.audit_results['L3_professional_standards']['numbering']
        if numbering_issues:
            for issue in numbering_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无编号体系问题\n"
        
        report += """
#### 3.4 文档质量问题

"""
        
        quality_issues = self.audit_results['L3_professional_standards']['quality']
        if quality_issues:
            for issue in quality_issues[:10]:
                report += f"- **{issue['type']}**: {issue.get('file', 'N/A')} - {issue['description']}\n"
        else:
            report += "✅ 无文档质量问题\n"
        
        report += f"""
---

## 💡 改进建议

### 立即行动（P0级问题）

"""
        
        if p0_issues:
            for i, (layer, category, issue) in enumerate(p0_issues, 1):
                report += f"{i}. **{issue['type']}**: {issue['recommendation']}\n"
        else:
            report += "✅ 无需立即行动\n"
        
        report += f"""
### 本周行动（P1级问题）

"""
        
        if p1_issues:
            for i, (layer, category, issue) in enumerate(p1_issues[:10], 1):
                report += f"{i}. **{issue['type']}**: {issue['recommendation']}\n"
        else:
            report += "✅ 无需本周行动\n"
        
        report += f"""
### 本月行动（P2级问题）

"""
        
        if p2_issues:
            p2_types = defaultdict(int)
            for _, _, issue in p2_issues:
                p2_types[issue['type']] += 1
            for issue_type, count in sorted(p2_types.items(), key=lambda x: -x[1]):
                report += f"- **{issue_type}**: {count}个问题待处理\n"
        else:
            report += "✅ 无需本月行动\n"
        
        report += f"""
---

## 📊 合规率评估

### 五大原则符合率

| 原则 | 符合率 | 说明 |
|------|--------|------|
| **职责驱动原则** | {self.calculate_compliance_rate('responsibility_issues'):.1f}% | 基于{len(resp_issues)}个问题 |
| **索引完备性原则** | {self.calculate_compliance_rate('index_completeness'):.1f}% | 基于{len(index_issues)}个问题 |
| **版本隔离原则** | {self.calculate_compliance_rate('version_isolation'):.1f}% | 基于{len(version_issues)}个问题 |
| **文档代码对应原则** | {self.calculate_compliance_rate('doc_code_correspondence'):.1f}% | 基于{len(doc_code_issues)}个问题 |
| **命名规范原则** | {self.calculate_compliance_rate('five_principles'):.1f}% | 基于{len(principles_issues)}个问题 |

**总体合规率**: {self.calculate_overall_compliance():.1f}%

---

## 📝 审计总结

### 主要发现

1. **P0级问题**: {len(p0_issues)}个 - {'需要立即修复' if p0_issues else '无紧急问题'}
2. **P1级问题**: {len(p1_issues)}个 - {'需要本周修复' if p1_issues else '无重要问题'}
3. **P2级问题**: {len(p2_issues)}个 - {'需要本月修复' if p2_issues else '无一般问题'}

### 审计质量

- ✅ 审计覆盖率: 100%
- ✅ 审计深度: 三层审计（L1-L3）
- ✅ 审计标准: 专业量化机构五大原则
- ✅ 问题分类: P0/P1/P2优先级

### 后续建议

1. **立即修复P0级问题**（如有）
2. **本周内修复P1级问题**
3. **本月内修复P2级问题**
4. **定期执行审计**（建议每月一次）

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**审计执行者**: Audit Sentinel  
**审计标准版本**: v5.1  
**下次审计建议**: 30天后
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 审计报告已生成: {report_file}")
        
        # 同时保存JSON格式的详细结果
        json_file = OUTPUT_DIR / f"LAYER8_DEEP_AUDIT_DATA_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 审计数据已保存: {json_file}")
    
    def calculate_compliance_rate(self, category):
        """计算合规率"""
        total_files = self.audit_results['statistics']['total_files']
        if total_files == 0:
            return 100.0
        
        # 统计该类别的问题数量
        issue_count = 0
        for layer in ['L1_file_system', 'L2_document_content', 'L3_professional_standards']:
            if category in self.audit_results[layer]:
                issue_count += len(self.audit_results[layer][category])
        
        # 计算合规率
        compliance_rate = max(0, 100 - (issue_count / total_files * 100))
        return compliance_rate
    
    def calculate_overall_compliance(self):
        """计算总体合规率"""
        categories = [
            'directory_structure', 'file_naming', 'path_references',
            'responsibility_issues', 'index_completeness', 'version_isolation',
            'doc_code_correspondence', 'five_principles', 'classification',
            'numbering', 'quality'
        ]
        
        total_rate = 0
        for category in categories:
            total_rate += self.calculate_compliance_rate(category)
        
        return total_rate / len(categories)


if __name__ == "__main__":
    auditor = Layer8DeepAuditor()
    auditor.audit_all()
