#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
战略决策层深度审计脚本
审计目标：识别职责重叠、重复内容、文档质量问题
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

class StrategicDecisionDeepAuditor:
    def __init__(self, docs_root):
        self.docs_root = Path(docs_root)
        self.strategic_dir = self.docs_root / "11_STRATEGIC_DECISION"
        self.documents = []
        self.issues = []
        self.responsibilities = defaultdict(list)
        self.content_hashes = defaultdict(list)
        
    def run_audit(self):
        """执行完整审计"""
        print("=" * 80)
        print("战略决策层深度审计")
        print("=" * 80)
        print(f"审计目录: {self.strategic_dir}")
        print(f"审计时间: {self.get_current_time()}")
        print()
        
        # 1. 扫描所有文档
        print("1. 扫描所有文档...")
        self.scan_documents()
        
        # 2. 提取职责信息
        print("\n2. 提取职责信息...")
        self.extract_responsibilities()
        
        # 3. 检查职责重叠
        print("\n3. 检查职责重叠...")
        self.check_responsibility_overlap()
        
        # 4. 检查重复内容
        print("\n4. 检查重复内容...")
        self.check_duplicate_content()
        
        # 5. 检查文档质量
        print("\n5. 检查文档质量...")
        self.check_document_quality()
        
        # 6. 生成审计报告
        print("\n6. 生成审计报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成")
        print("=" * 80)
        
    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def scan_documents(self):
        """扫描所有文档"""
        md_files = list(self.strategic_dir.rglob("*.md"))
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取YAML头部
                yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                yaml_header = yaml_match.group(1) if yaml_match else ""
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else md_file.stem
                
                # 提取职责描述
                responsibility_match = re.search(r'核心职责[：:]\s*(.+?)(?:\n|$)', content)
                responsibility = responsibility_match.group(1) if responsibility_match else ""
                
                doc_info = {
                    'path': str(md_file.relative_to(self.docs_root)),
                    'filename': md_file.name,
                    'title': title,
                    'responsibility': responsibility,
                    'yaml_header': yaml_header,
                    'content': content,
                    'content_length': len(content),
                    'is_index': md_file.name == 'INDEX.md',
                    'is_archive': 'archive' in str(md_file).lower()
                }
                
                self.documents.append(doc_info)
                
            except Exception as e:
                print(f"  ⚠️ 读取文件失败: {md_file.name} - {str(e)}")
        
        print(f"  ✅ 扫描完成: {len(self.documents)} 个文档")
        
    def extract_responsibilities(self):
        """提取职责信息"""
        for doc in self.documents:
            if doc['is_index'] or doc['is_archive']:
                continue
            
            # 提取核心职责
            if doc['responsibility']:
                self.responsibilities[doc['responsibility']].append(doc['filename'])
            
            # 提取关键词
            keywords = self.extract_keywords(doc['content'])
            for keyword in keywords:
                self.responsibilities[keyword].append(doc['filename'])
        
        print(f"  ✅ 提取完成: {len(self.responsibilities)} 个职责关键词")
        
    def extract_keywords(self, content):
        """提取关键词"""
        keywords = set()
        
        # 提取文档中的关键概念
        patterns = [
            r'资产配置',
            r'风险预算',
            r'策略选择',
            r'战略调整',
            r'投资组合',
            r'风险管理',
            r'绩效归因',
            r'再平衡',
            r'流动性',
            r'杠杆',
            r'税收',
            r'ESG',
            r'基准',
            r'宏观因子',
            r'市场环境',
            r'情景分析',
            r'投资约束',
            r'IPS',
            r'决策审计',
            r'技术选择',
            r'开源集成',
            r'多策略协调',
            r'组合保险',
            r'资本配置'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                keywords.add(pattern)
        
        return keywords
    
    def check_responsibility_overlap(self):
        """检查职责重叠"""
        overlap_count = 0
        
        # 检查相同职责的文档
        for responsibility, files in self.responsibilities.items():
            if len(files) > 1:
                # 排除INDEX文件
                non_index_files = [f for f in files if not f.startswith('INDEX')]
                if len(non_index_files) > 1:
                    overlap_count += 1
                    self.issues.append({
                        'type': '职责重叠',
                        'severity': 'HIGH',
                        'description': f'职责"{responsibility}"出现在多个文档中',
                        'files': non_index_files,
                        'recommendation': '建议合并或明确职责边界'
                    })
        
        print(f"  ✅ 检查完成: 发现 {overlap_count} 个职责重叠问题")
        
    def check_duplicate_content(self):
        """检查重复内容"""
        duplicate_count = 0
        
        # 检查内容相似度
        for i, doc1 in enumerate(self.documents):
            if doc1['is_index'] or doc1['is_archive']:
                continue
                
            for doc2 in self.documents[i+1:]:
                if doc2['is_index'] or doc2['is_archive']:
                    continue
                
                # 计算内容相似度
                similarity = self.calculate_similarity(doc1['content'], doc2['content'])
                
                if similarity > 0.7:  # 70%相似度阈值
                    duplicate_count += 1
                    self.issues.append({
                        'type': '内容重复',
                        'severity': 'HIGH',
                        'description': f'文档内容高度相似 ({similarity:.1%})',
                        'files': [doc1['filename'], doc2['filename']],
                        'similarity': similarity,
                        'recommendation': '建议合并或删除重复内容'
                    })
        
        print(f"  ✅ 检查完成: 发现 {duplicate_count} 个内容重复问题")
        
    def calculate_similarity(self, content1, content2):
        """计算内容相似度"""
        # 简单的相似度计算：基于共同词汇
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def check_document_quality(self):
        """检查文档质量"""
        quality_issues = 0
        
        for doc in self.documents:
            if doc['is_archive']:
                continue
            
            issues = []
            
            # 检查YAML头部
            if not doc['yaml_header']:
                issues.append('缺少YAML头部')
            
            # 检查标题
            if not doc['title'] or doc['title'] == doc['filename'].replace('.md', ''):
                issues.append('缺少明确标题')
            
            # 检查职责描述
            if not doc['is_index'] and not doc['responsibility']:
                issues.append('缺少职责描述')
            
            # 检查内容长度
            if doc['content_length'] < 500 and not doc['is_index']:
                issues.append('内容过短')
            
            if issues:
                quality_issues += 1
                self.issues.append({
                    'type': '文档质量',
                    'severity': 'MEDIUM',
                    'description': '; '.join(issues),
                    'files': [doc['filename']],
                    'recommendation': '建议补充缺失内容'
                })
        
        print(f"  ✅ 检查完成: 发现 {quality_issues} 个质量问题")
        
    def generate_report(self):
        """生成审计报告"""
        report_path = self.docs_root / "05_IMPLEMENTATION" / "07_OPERATIONS" / "audit_state" / "STRATEGIC_DECISION_DEEP_AUDIT_REPORT_20260407.md"
        
        # 统计问题
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        
        report = f"""# 战略决策层深度审计报告

> **审计时间**: {self.get_current_time()}
> **审计范围**: 11_STRATEGIC_DECISION（战略决策层）
> **审计标准**: 专业量化机构五大原则 + 三层审计标准
> **审计类型**: 职责重叠检查 + 重复内容识别 + 文档质量评估

---

## 📊 一、审计概览

### 1.1 审计统计

| 统计项 | 数量 |
|--------|------|
| **文档总数** | {len(self.documents)} |
| **活跃文档** | {len([d for d in self.documents if not d['is_archive']])} |
| **归档文档** | {len([d for d in self.documents if d['is_archive']])} |
| **索引文档** | {len([d for d in self.documents if d['is_index']])} |

### 1.2 问题统计

| 问题类型 | 高优先级 | 中优先级 | 低优先级 | 总计 |
|----------|----------|----------|----------|------|
| **职责重叠** | {len([i for i in high_issues if i['type'] == '职责重叠'])} | 0 | 0 | {len([i for i in self.issues if i['type'] == '职责重叠'])} |
| **内容重复** | {len([i for i in high_issues if i['type'] == '内容重复'])} | 0 | 0 | {len([i for i in self.issues if i['type'] == '内容重复'])} |
| **文档质量** | 0 | {len([i for i in medium_issues if i['type'] == '文档质量'])} | 0 | {len([i for i in self.issues if i['type'] == '文档质量'])} |
| **总计** | **{len(high_issues)}** | **{len(medium_issues)}** | **0** | **{len(self.issues)}** |

---

## 🔍 二、详细审计发现

### 2.1 高优先级问题 (P0)

"""
        
        if high_issues:
            for idx, issue in enumerate(high_issues, 1):
                report += f"""
#### 问题 {idx}: {issue['type']}

- **严重程度**: 🔴 {issue['severity']}
- **问题描述**: {issue['description']}
- **涉及文件**: {', '.join(issue['files'])}
- **修复建议**: {issue['recommendation']}

"""
        else:
            report += "✅ 未发现高优先级问题\n\n"
        
        report += f"""
### 2.2 中优先级问题 (P1)

"""
        
        if medium_issues:
            for idx, issue in enumerate(medium_issues, 1):
                report += f"""
#### 问题 {idx}: {issue['type']}

- **严重程度**: 🟡 {issue['severity']}
- **问题描述**: {issue['description']}
- **涉及文件**: {', '.join(issue['files'])}
- **修复建议**: {issue['recommendation']}

"""
        else:
            report += "✅ 未发现中优先级问题\n\n"
        
        report += f"""
---

## 📋 三、文档清单

### 3.1 根目录文档

| 文档名称 | 标题 | 职责 | 状态 |
|----------|------|------|------|
"""
        
        root_docs = [d for d in self.documents if d['path'].count('\\') == 1 and not d['is_index'] and not d['is_archive']]
        for doc in root_docs:
            status = "✅" if doc['responsibility'] else "⚠️"
            report += f"| {doc['filename']} | {doc['title'][:30]} | {doc['responsibility'][:30] if doc['responsibility'] else '未定义'} | {status} |\n"
        
        report += f"""
### 3.2 子目录文档

"""
        
        subdirs = ['01_asset_allocation', '02_risk_budgeting', '03_strategy_selection', '04_strategic_adjustment']
        for subdir in subdirs:
            subdir_docs = [d for d in self.documents if subdir in d['path'] and not d['is_index']]
            if subdir_docs:
                report += f"""
#### {subdir}

| 文档名称 | 标题 | 职责 | 状态 |
|----------|------|------|------|
"""
                for doc in subdir_docs:
                    status = "✅" if doc['responsibility'] else "⚠️"
                    report += f"| {doc['filename']} | {doc['title'][:30]} | {doc['responsibility'][:30] if doc['responsibility'] else '未定义'} | {status} |\n"
        
        report += f"""
---

## 🎯 四、修复建议

### 4.1 立即修复项 (P0)

"""
        
        if high_issues:
            for idx, issue in enumerate(high_issues, 1):
                report += f"{idx}. **{issue['type']}**: {issue['recommendation']}\n"
        else:
            report += "✅ 无需立即修复\n"
        
        report += f"""
### 4.2 短期改进项 (P1)

"""
        
        if medium_issues:
            for idx, issue in enumerate(medium_issues, 1):
                report += f"{idx}. **{issue['type']}**: {issue['recommendation']}\n"
        else:
            report += "✅ 无需短期改进\n"
        
        report += f"""
---

## 📊 五、质量指标

| 指标 | 当前值 | 目标值 | 状态 |
|------|--------|--------|------|
| **职责清晰度** | {len([d for d in self.documents if d['responsibility']]) / len([d for d in self.documents if not d['is_index'] and not d['is_archive']]) * 100:.1f}% | ≥95% | {'✅' if len([d for d in self.documents if d['responsibility']]) / len([d for d in self.documents if not d['is_index'] and not d['is_archive']]) >= 0.95 else '⚠️'} |
| **YAML完整性** | {len([d for d in self.documents if d['yaml_header']]) / len(self.documents) * 100:.1f}% | ≥95% | {'✅' if len([d for d in self.documents if d['yaml_header']]) / len(self.documents) >= 0.95 else '⚠️'} |
| **问题总数** | {len(self.issues)} | 0 | {'✅' if len(self.issues) == 0 else '⚠️'} |

---

## 📝 六、审计声明

**审计方法**: 三层审计标准（L1文件系统层 + L2文档内容层 + L3专业标准层）

**审计范围**: 
- ✅ 职责重叠检查
- ✅ 重复内容识别
- ✅ 文档质量评估
- ✅ YAML完整性检查

**审计局限性**:
- 本审计基于文档内容分析，未涉及代码实现
- 相似度计算基于词汇统计，可能存在误差
- 需要人工复核确认问题

**后续建议**:
1. 对高优先级问题立即修复
2. 对中优先级问题制定修复计划
3. 建立定期审计机制

---

**审计完成时间**: {self.get_current_time()}
**审计报告路径**: {report_path.relative_to(self.docs_root)}
"""
        
        # 保存报告
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ 报告已生成: {report_path.relative_to(self.docs_root)}")
        
        # 保存JSON数据
        json_path = report_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'audit_time': self.get_current_time(),
                'documents': self.documents,
                'issues': self.issues,
                'statistics': {
                    'total_documents': len(self.documents),
                    'high_issues': len(high_issues),
                    'medium_issues': len(medium_issues)
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 数据已保存: {json_path.relative_to(self.docs_root)}")

if __name__ == "__main__":
    auditor = StrategicDecisionDeepAuditor("docs")
    auditor.run_audit()
