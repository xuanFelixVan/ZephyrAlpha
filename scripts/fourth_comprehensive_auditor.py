#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
第四次全面深度审计脚本
基于专业量化机构五大原则和三层审计标准
重点检查重复内容和职责不清的内容
"""

import os
import re
import hashlib
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

class FourthComprehensiveAuditor:
    def __init__(self):
        self.results = {
            'L1': {
                '目录结构': [],
                '文件命名': [],
                '路径引用': []
            },
            'L2': {
                '职责驱动': [],
                '索引完备': [],
                '版本隔离': [],
                '文档代码对应': []
            },
            'L3': {
                '五大原则': [],
                '文档分类': [],
                '编号体系': [],
                '文档质量': []
            },
            '重复内容': [],
            '职责问题': []
        }
        
        self.documents = []
        self.module_ids = defaultdict(list)
        self.content_hashes = defaultdict(list)
        self.responsibilities = defaultdict(list)
        
    def parse_yaml_safe(self, content):
        """安全解析YAML头部"""
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            body_content = content[yaml_match.end():]
            
            try:
                yaml_dict = yaml.safe_load(yaml_content)
                return yaml_dict if yaml_dict else {}, body_content
            except:
                return {}, body_content
        
        return {}, content
    
    def get_content_hash(self, content):
        """获取内容哈希值"""
        # 移除YAML头部
        _, body = self.parse_yaml_safe(content)
        # 移除空白字符
        body = re.sub(r'\s+', '', body)
        return hashlib.md5(body.encode('utf-8')).hexdigest()
    
    def check_l1_file_system(self):
        """L1文件系统层审计"""
        print("\n执行L1文件系统层审计...")
        
        # 1.1 目录结构问题
        for root, dirs, files in os.walk(FACTOR_LIBRARY):
            root_path = Path(root)
            rel_path = root_path.relative_to(FACTOR_LIBRARY)
            
            # 检查稀疏目录
            md_files = [f for f in files if f.endswith('.md')]
            if len(md_files) < 3 and len(md_files) > 0:
                self.results['L1']['目录结构'].append({
                    'type': '稀疏目录',
                    'path': str(rel_path),
                    'file_count': len(md_files),
                    'severity': 'P2'
                })
            
            # 检查空目录
            if len(files) == 0 and len(dirs) == 0:
                self.results['L1']['目录结构'].append({
                    'type': '空目录',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
            
            # 检查目录层级深度
            depth = len(rel_path.parts)
            if depth > 4:
                self.results['L1']['目录结构'].append({
                    'type': '目录层级过深',
                    'path': str(rel_path),
                    'depth': depth,
                    'severity': 'P2'
                })
        
        # 1.2 文件命名问题
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            # 检查旧架构命名残留
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if 'Layer 0-11' in content or re.search(r'Layer\s+[0-9]+', content):
                self.results['L1']['文件命名'].append({
                    'type': '旧架构命名残留',
                    'path': str(rel_path),
                    'severity': 'P1'
                })
            
            # 检查特殊字符
            if ' ' in md_file.name or any(ord(c) > 127 for c in md_file.stem if not '\u4e00' <= c <= '\u9fff'):
                self.results['L1']['文件命名'].append({
                    'type': '特殊字符问题',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
        
        # 1.3 路径引用问题
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查路径冗余
            if re.search(r'\.\./\.\./\.\./', content):
                self.results['L1']['路径引用'].append({
                    'type': '路径冗余',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
            
            # 检查死链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in links:
                if link_path.startswith('./') or link_path.startswith('../'):
                    target_path = md_file.parent / link_path
                    if not target_path.exists():
                        self.results['L1']['路径引用'].append({
                            'type': '死链接',
                            'path': str(rel_path),
                            'link': link_path,
                            'severity': 'P1'
                        })
    
    def check_l2_document_content(self):
        """L2文档内容层审计"""
        print("执行L2文档内容层审计...")
        
        # 收集所有文档信息
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            yaml_dict, body = self.parse_yaml_safe(content)
            
            doc_info = {
                'path': str(rel_path),
                'yaml': yaml_dict,
                'body': body,
                'content': content
            }
            
            self.documents.append(doc_info)
            
            # 收集module_id
            if 'module_id' in yaml_dict:
                self.module_ids[yaml_dict['module_id']].append(str(rel_path))
            
            # 收集内容哈希
            content_hash = self.get_content_hash(content)
            self.content_hashes[content_hash].append(str(rel_path))
            
            # 收集职责信息
            if 'responsibility' in yaml_dict:
                resp = yaml_dict['responsibility']
                if isinstance(resp, list):
                    for r in resp:
                        self.responsibilities[r].append(str(rel_path))
                else:
                    self.responsibilities[str(resp)].append(str(rel_path))
        
        # 2.1 职责驱动原则问题
        for doc in self.documents:
            yaml_dict = doc['yaml']
            
            # 检查职责缺失
            if 'responsibility' not in yaml_dict or not yaml_dict['responsibility']:
                self.results['L2']['职责驱动'].append({
                    'type': '职责缺失',
                    'path': doc['path'],
                    'severity': 'P1'
                })
            
            # 检查职责描述模糊
            if 'responsibility' in yaml_dict:
                resp = yaml_dict['responsibility']
                if isinstance(resp, list) and len(resp) == 0:
                    self.results['L2']['职责驱动'].append({
                        'type': '职责描述模糊',
                        'path': doc['path'],
                        'severity': 'P2'
                    })
        
        # 检查职责重叠
        for resp, paths in self.responsibilities.items():
            if len(paths) > 1:
                self.results['L2']['职责驱动'].append({
                    'type': '职责重叠',
                    'responsibility': resp,
                    'paths': paths,
                    'severity': 'P1'
                })
        
        # 2.2 索引完备性问题
        for root, dirs, files in os.walk(FACTOR_LIBRARY):
            root_path = Path(root)
            rel_path = root_path.relative_to(FACTOR_LIBRARY)
            
            # 检查子目录缺索引
            if 'INDEX.md' not in files and len(files) > 0:
                self.results['L2']['索引完备'].append({
                    'type': '子目录缺索引',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
            
            # 检查索引不完整
            if 'INDEX.md' in files:
                index_path = root_path / 'INDEX.md'
                with open(index_path, 'r', encoding='utf-8-sig') as f:
                    index_content = f.read()
                
                # 获取目录下的所有.md文件
                md_files = [f for f in files if f.endswith('.md') and f != 'INDEX.md']
                
                # 检查索引是否包含这些文件
                for md_file in md_files:
                    if md_file.replace('.md', '') not in index_content:
                        self.results['L2']['索引完备'].append({
                            'type': '索引不完整',
                            'path': str(rel_path / 'INDEX.md'),
                            'missing': md_file,
                            'severity': 'P2'
                        })
        
        # 2.3 版本隔离问题
        for content_hash, paths in self.content_hashes.items():
            if len(paths) > 1:
                self.results['L2']['版本隔离'].append({
                    'type': '重复文档',
                    'paths': paths,
                    'severity': 'P1'
                })
        
        # 2.4 文档代码对应问题（简化检查）
        for doc in self.documents:
            yaml_dict = doc['yaml']
            
            # 检查YAML字段缺失
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'responsibility']
            missing_fields = [f for f in required_fields if f not in yaml_dict]
            
            if missing_fields:
                self.results['L2']['文档代码对应'].append({
                    'type': 'YAML字段缺失',
                    'path': doc['path'],
                    'missing_fields': missing_fields,
                    'severity': 'P1'
                })
    
    def check_l3_professional_standards(self):
        """L3专业标准层审计"""
        print("执行L3专业标准层审计...")
        
        # 3.1 五大原则符合性问题
        for doc in self.documents:
            yaml_dict = doc['yaml']
            
            # 职责驱动原则
            if 'responsibility' not in yaml_dict:
                self.results['L3']['五大原则'].append({
                    'type': '职责驱动原则违反',
                    'path': doc['path'],
                    'severity': 'P1'
                })
            
            # 命名规范原则
            if 'module_id' in yaml_dict:
                module_id = yaml_dict['module_id']
                if not re.match(r'^[A-Z_0-9]+$', module_id):
                    self.results['L3']['五大原则'].append({
                        'type': '命名规范原则违反',
                        'path': doc['path'],
                        'module_id': module_id,
                        'severity': 'P2'
                    })
        
        # 3.2 编号体系问题
        for module_id, paths in self.module_ids.items():
            if len(paths) > 1:
                self.results['L3']['编号体系'].append({
                    'type': '编号重复',
                    'module_id': module_id,
                    'paths': paths,
                    'severity': 'P1'
                })
        
        # 3.3 文档质量问题
        for doc in self.documents:
            yaml_dict = doc['yaml']
            
            # 检查YAML头部缺失
            if not yaml_dict:
                self.results['L3']['文档质量'].append({
                    'type': 'YAML头部缺失',
                    'path': doc['path'],
                    'severity': 'P1'
                })
            
            # 检查变更记录缺失
            if '变更记录' not in doc['content'] and '## 变更记录' not in doc['content']:
                self.results['L3']['文档质量'].append({
                    'type': '变更记录缺失',
                    'path': doc['path'],
                    'severity': 'P2'
                })
    
    def check_duplicates(self):
        """检查重复内容"""
        print("检查重复内容...")
        
        for content_hash, paths in self.content_hashes.items():
            if len(paths) > 1:
                # 读取文件内容进行详细比较
                contents = []
                for path in paths:
                    full_path = FACTOR_LIBRARY / path
                    with open(full_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    _, body = self.parse_yaml_safe(content)
                    contents.append({
                        'path': path,
                        'body_length': len(body)
                    })
                
                self.results['重复内容'].append({
                    'type': '内容重复',
                    'paths': paths,
                    'details': contents,
                    'severity': 'P1'
                })
    
    def check_unclear_responsibilities(self):
        """检查职责不清的内容"""
        print("检查职责不清的内容...")
        
        for doc in self.documents:
            yaml_dict = doc['yaml']
            body = doc['body']
            
            # 检查职责描述模糊
            if 'responsibility' in yaml_dict:
                resp = yaml_dict['responsibility']
                if isinstance(resp, list):
                    resp_text = ' '.join(resp)
                else:
                    resp_text = str(resp)
                
                # 检查职责描述是否过于简短
                if len(resp_text) < 10:
                    self.results['职责问题'].append({
                        'type': '职责描述过短',
                        'path': doc['path'],
                        'responsibility': resp,
                        'severity': 'P2'
                    })
            
            # 检查文档内容是否包含多个核心职责
            responsibility_keywords = [
                '核心职责', '主要职责', '负责', '职责边界',
                '本文档负责', '本文档不负责'
            ]
            
            resp_count = sum(1 for kw in responsibility_keywords if kw in body)
            if resp_count > 6:
                self.results['职责问题'].append({
                    'type': '职责过多',
                    'path': doc['path'],
                    'responsibility_count': resp_count,
                    'severity': 'P2'
                })
    
    def generate_report(self):
        """生成审计报告"""
        print("\n生成审计报告...")
        
        # 统计问题数量
        l1_count = sum(len(v) for v in self.results['L1'].values())
        l2_count = sum(len(v) for v in self.results['L2'].values())
        l3_count = sum(len(v) for v in self.results['L3'].values())
        duplicate_count = len(self.results['重复内容'])
        responsibility_count = len(self.results['职责问题'])
        total_count = l1_count + l2_count + l3_count + duplicate_count + responsibility_count
        
        # 按严重程度分类
        p0_count = 0
        p1_count = 0
        p2_count = 0
        
        for category in ['L1', 'L2', 'L3']:
            for subcategory in self.results[category].values():
                for issue in subcategory:
                    if issue.get('severity') == 'P0':
                        p0_count += 1
                    elif issue.get('severity') == 'P1':
                        p1_count += 1
                    else:
                        p2_count += 1
        
        for issue in self.results['重复内容']:
            if issue.get('severity') == 'P0':
                p0_count += 1
            elif issue.get('severity') == 'P1':
                p1_count += 1
            else:
                p2_count += 1
        
        for issue in self.results['职责问题']:
            if issue.get('severity') == 'P0':
                p0_count += 1
            elif issue.get('severity') == 'P1':
                p1_count += 1
            else:
                p2_count += 1
        
        # 生成报告
        report = f"""# 第四次全面深度审计报告

## 审计概要

- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **审计范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **审计方法**: 三层审计标准（L1文件系统层、L2文档内容层、L3专业标准层）
- **审计重点**: 重复内容检查、职责不清内容检查

---

## 审计统计

### 总体统计

| 统计项 | 数量 |
|--------|------|
| 扫描文档总数 | {len(self.documents)} |
| 发现问题总数 | {total_count} |
| L1文件系统层问题 | {l1_count} |
| L2文档内容层问题 | {l2_count} |
| L3专业标准层问题 | {l3_count} |
| 重复内容问题 | {duplicate_count} |
| 职责问题 | {responsibility_count} |

### 按严重程度分类

| 严重程度 | 数量 | 说明 |
|---------|------|------|
| 🔴 P0 | {p0_count} | 立即修复 |
| 🟡 P1 | {p1_count} | 短期修复 |
| 🟢 P2 | {p2_count} | 长期优化 |

---

## L1 文件系统层审计结果

### 1.1 目录结构问题 ({len(self.results['L1']['目录结构'])}个)

"""
        
        if self.results['L1']['目录结构']:
            for issue in self.results['L1']['目录结构'][:20]:
                report += f"- **{issue['type']}**: {issue['path']}"
                if 'file_count' in issue:
                    report += f" ({issue['file_count']}个文件)"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 1.2 文件命名问题 ({len(self.results['L1']['文件命名'])}个)

"""
        
        if self.results['L1']['文件命名']:
            for issue in self.results['L1']['文件命名'][:20]:
                report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 1.3 路径引用问题 ({len(self.results['L1']['路径引用'])}个)

"""
        
        if self.results['L1']['路径引用']:
            for issue in self.results['L1']['路径引用'][:20]:
                report += f"- **{issue['type']}**: {issue['path']}"
                if 'link' in issue:
                    report += f" -> {issue['link']}"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
---

## L2 文档内容层审计结果

### 2.1 职责驱动原则问题 ({len(self.results['L2']['职责驱动'])}个)

"""
        
        if self.results['L2']['职责驱动']:
            for issue in self.results['L2']['职责驱动'][:20]:
                report += f"- **{issue['type']}**: "
                if 'path' in issue:
                    report += issue['path']
                elif 'responsibility' in issue:
                    report += f"职责'{issue['responsibility']}'出现在{len(issue['paths'])}个文档"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 2.2 索引完备性问题 ({len(self.results['L2']['索引完备'])}个)

"""
        
        if self.results['L2']['索引完备']:
            for issue in self.results['L2']['索引完备'][:20]:
                report += f"- **{issue['type']}**: {issue['path']}"
                if 'missing' in issue:
                    report += f" (缺失{issue['missing']})"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 2.3 版本隔离问题 ({len(self.results['L2']['版本隔离'])}个)

"""
        
        if self.results['L2']['版本隔离']:
            for issue in self.results['L2']['版本隔离'][:20]:
                report += f"- **{issue['type']}**: {len(issue['paths'])}个文档重复\n"
                for path in issue['paths'][:5]:
                    report += f"  - {path}\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 2.4 文档代码对应问题 ({len(self.results['L2']['文档代码对应'])}个)

"""
        
        if self.results['L2']['文档代码对应']:
            for issue in self.results['L2']['文档代码对应'][:20]:
                report += f"- **{issue['type']}**: {issue['path']}"
                if 'missing_fields' in issue:
                    report += f" (缺失字段: {', '.join(issue['missing_fields'])})"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
---

## L3 专业标准层审计结果

### 3.1 五大原则符合性问题 ({len(self.results['L3']['五大原则'])}个)

"""
        
        if self.results['L3']['五大原则']:
            for issue in self.results['L3']['五大原则'][:20]:
                report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 3.2 编号体系问题 ({len(self.results['L3']['编号体系'])}个)

"""
        
        if self.results['L3']['编号体系']:
            for issue in self.results['L3']['编号体系'][:20]:
                report += f"- **{issue['type']}**: {issue['module_id']}\n"
                for path in issue['paths'][:5]:
                    report += f"  - {path}\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
### 3.3 文档质量问题 ({len(self.results['L3']['文档质量'])}个)

"""
        
        if self.results['L3']['文档质量']:
            for issue in self.results['L3']['文档质量'][:20]:
                report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        else:
            report += "✅ 无问题\n"
        
        report += f"""
---

## 重复内容检查结果 ({len(self.results['重复内容'])}个)

"""
        
        if self.results['重复内容']:
            for i, issue in enumerate(self.results['重复内容'][:20], 1):
                report += f"### 重复组 {i}\n\n"
                report += f"**重复文档数**: {len(issue['paths'])}\n\n"
                for detail in issue['details']:
                    report += f"- {detail['path']} (内容长度: {detail['body_length']}字符)\n"
                report += "\n"
        else:
            report += "✅ 无重复内容\n"
        
        report += f"""
---

## 职责不清内容检查结果 ({len(self.results['职责问题'])}个)

"""
        
        if self.results['职责问题']:
            for issue in self.results['职责问题'][:20]:
                report += f"- **{issue['type']}**: {issue['path']}"
                if 'responsibility' in issue:
                    report += f" (职责: {issue['responsibility']})"
                if 'responsibility_count' in issue:
                    report += f" (职责标记数: {issue['responsibility_count']})"
                report += f" [{issue['severity']}]\n"
        else:
            report += "✅ 无职责不清内容\n"
        
        report += f"""
---

## 优先修复建议

### 🔴 P0级别问题（立即修复）

"""
        
        p0_issues = []
        for category in ['L1', 'L2', 'L3']:
            for subcategory, issues in self.results[category].items():
                for issue in issues:
                    if issue.get('severity') == 'P0':
                        p0_issues.append((category, subcategory, issue))
        
        for issue in self.results['重复内容']:
            if issue.get('severity') == 'P0':
                p0_issues.append(('重复内容', '', issue))
        
        for issue in self.results['职责问题']:
            if issue.get('severity') == 'P0':
                p0_issues.append(('职责问题', '', issue))
        
        if p0_issues:
            for category, subcategory, issue in p0_issues[:10]:
                report += f"- [{category}] {issue['type']}: {issue.get('path', 'N/A')}\n"
        else:
            report += "✅ 无P0级别问题\n"
        
        report += f"""
### 🟡 P1级别问题（短期修复）

"""
        
        p1_issues = []
        for category in ['L1', 'L2', 'L3']:
            for subcategory, issues in self.results[category].items():
                for issue in issues:
                    if issue.get('severity') == 'P1':
                        p1_issues.append((category, subcategory, issue))
        
        for issue in self.results['重复内容']:
            if issue.get('severity') == 'P1':
                p1_issues.append(('重复内容', '', issue))
        
        for issue in self.results['职责问题']:
            if issue.get('severity') == 'P1':
                p1_issues.append(('职责问题', '', issue))
        
        if p1_issues:
            for category, subcategory, issue in p1_issues[:20]:
                report += f"- [{category}] {issue['type']}: {issue.get('path', 'N/A')}\n"
        else:
            report += "✅ 无P1级别问题\n"
        
        report += f"""
### 🟢 P2级别问题（长期优化）

"""
        
        p2_issues = []
        for category in ['L1', 'L2', 'L3']:
            for subcategory, issues in self.results[category].items():
                for issue in issues:
                    if issue.get('severity') == 'P2':
                        p2_issues.append((category, subcategory, issue))
        
        for issue in self.results['重复内容']:
            if issue.get('severity') == 'P2':
                p2_issues.append(('重复内容', '', issue))
        
        for issue in self.results['职责问题']:
            if issue.get('severity') == 'P2':
                p2_issues.append(('职责问题', '', issue))
        
        if p2_issues:
            report += f"P2级别问题共{len(p2_issues)}个，建议长期优化\n"
        else:
            report += "✅ 无P2级别问题\n"
        
        report += f"""
---

## Git备份

- **备份标签**: v3.7-pre-fourth-audit
- **备份时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **可恢复**: 是

---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        report_path = FACTOR_LIBRARY.parent / '09_AUDIT' / 'STATE' / f'FOURTH_COMPREHENSIVE_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n审计报告已生成: {report_path}")
        return report_path
    
    def run(self):
        """执行完整审计"""
        print("=" * 80)
        print("第四次全面深度审计")
        print("=" * 80)
        print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 执行三层审计
        self.check_l1_file_system()
        self.check_l2_document_content()
        self.check_l3_professional_standards()
        
        # 执行重点检查
        self.check_duplicates()
        self.check_unclear_responsibilities()
        
        # 生成报告
        report_path = self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成")
        print("=" * 80)
        
        return report_path

if __name__ == '__main__':
    auditor = FourthComprehensiveAuditor()
    auditor.run()
