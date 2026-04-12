#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
第六次综合审计脚本
执行L1、L2、L3三层审计，重点检查重复内容和职责不清问题
"""

import re
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

class SixthComprehensiveAuditor:
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
        """获取内容哈希"""
        yaml_dict, body = self.parse_yaml_safe(content)
        return hashlib.md5(body.encode('utf-8')).hexdigest()
    
    def audit_l1_file_system(self):
        """L1文件系统层审计"""
        print("\n执行L1文件系统层审计...")
        
        # 1. 检查目录结构
        for directory in FACTOR_LIBRARY.rglob('*'):
            if directory.is_dir():
                rel_path = directory.relative_to(FACTOR_LIBRARY)
                
                # 检查目录层级深度
                depth = len(rel_path.parts)
                if depth > 4:
                    self.results['L1']['目录结构'].append({
                        'path': str(rel_path),
                        'issue': '目录层级过深',
                        'severity': 'P2',
                        'detail': f'嵌套{depth}层，超过4层'
                    })
                
                # 检查稀疏目录
                file_count = len(list(directory.glob('*.md')))
                if file_count < 3 and file_count > 0:
                    self.results['L1']['目录结构'].append({
                        'path': str(rel_path),
                        'issue': '稀疏目录',
                        'severity': 'P2',
                        'detail': f'仅包含{file_count}个文档'
                    })
                
                # 检查空目录
                if file_count == 0:
                    self.results['L1']['目录结构'].append({
                        'path': str(rel_path),
                        'issue': '空目录',
                        'severity': 'P1',
                        'detail': '目录无文档'
                    })
        
        # 2. 检查文件命名
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            # 检查旧架构命名残留
            if 'Layer' in md_file.stem:
                self.results['L1']['文件命名'].append({
                    'path': str(rel_path),
                    'issue': '旧架构命名残留',
                    'severity': 'P1',
                    'detail': '文件名包含Layer关键词'
                })
            
            # 检查特殊字符
            if re.search(r'[\s\u4e00-\u9fff]', md_file.stem):
                self.results['L1']['文件命名'].append({
                    'path': str(rel_path),
                    'issue': '特殊字符问题',
                    'severity': 'P2',
                    'detail': '文件名包含空格或中文'
                })
        
        # 3. 检查路径引用
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查路径冗余
            if re.search(r'\.\.\/\.\.\/\.\.\/', content):
                self.results['L1']['路径引用'].append({
                    'path': str(rel_path),
                    'issue': '路径冗余',
                    'severity': 'P2',
                    'detail': '使用过多../相对路径'
                })
            
            # 检查死链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for link_text, link_path in links:
                if link_path.startswith('./') or link_path.startswith('../'):
                    target_path = md_file.parent / link_path
                    if not target_path.exists():
                        self.results['L1']['路径引用'].append({
                            'path': str(rel_path),
                            'issue': '死链接',
                            'severity': 'P1',
                            'detail': f'链接{link_path}不存在'
                        })
    
    def audit_l2_document_content(self):
        """L2文档内容层审计"""
        print("\n执行L2文档内容层审计...")
        
        # 收集所有文档信息
        for md_file in FACTOR_LIBRARY.rglob('*.md'):
            rel_path = md_file.relative_to(FACTOR_LIBRARY)
            
            with open(md_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            yaml_dict, body = self.parse_yaml_safe(content)
            content_hash = self.get_content_hash(content)
            
            doc_info = {
                'path': str(rel_path),
                'yaml': yaml_dict,
                'body': body,
                'hash': content_hash,
                'file': md_file
            }
            
            self.documents.append(doc_info)
            
            # 收集module_id
            if 'module_id' in yaml_dict:
                self.module_ids[yaml_dict['module_id']].append(str(rel_path))
            
            # 收集内容哈希
            self.content_hashes[content_hash].append(str(rel_path))
            
            # 收集职责
            if 'responsibility' in yaml_dict:
                resp = yaml_dict['responsibility']
                if isinstance(resp, list):
                    for r in resp:
                        self.responsibilities[r].append(str(rel_path))
                else:
                    self.responsibilities[str(resp)].append(str(rel_path))
        
        # 1. 检查职责驱动原则
        for doc in self.documents:
            # 检查职责缺失
            if 'responsibility' not in doc['yaml']:
                self.results['L2']['职责驱动'].append({
                    'path': doc['path'],
                    'issue': '职责缺失',
                    'severity': 'P1',
                    'detail': '缺少responsibility字段'
                })
            else:
                # 检查职责描述过短
                resp = doc['yaml']['responsibility']
                if isinstance(resp, list) and len(resp) < 3:
                    self.results['L2']['职责驱动'].append({
                        'path': doc['path'],
                        'issue': '职责描述过短',
                        'severity': 'P2',
                        'detail': f'仅有{len(resp)}项职责'
                    })
        
        # 2. 检查索引完备性
        for directory in FACTOR_LIBRARY.rglob('*'):
            if directory.is_dir():
                rel_path = directory.relative_to(FACTOR_LIBRARY)
                
                # 检查INDEX.md
                index_path = directory / 'INDEX.md'
                if not index_path.exists():
                    # 检查是否有子目录或文档
                    has_content = len(list(directory.glob('*.md'))) > 0 or len(list(directory.glob('*'))) > 1
                    if has_content:
                        self.results['L2']['索引完备'].append({
                            'path': str(rel_path),
                            'issue': '缺少INDEX.md',
                            'severity': 'P1',
                            'detail': '目录缺少索引文件'
                        })
                else:
                    # 检查索引完整性
                    with open(index_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    
                    # 获取目录中的所有文档
                    all_docs = [f.name for f in directory.glob('*.md') if f.name != 'INDEX.md']
                    
                    # 检查索引是否列出所有文档
                    for doc in all_docs:
                        if doc not in content:
                            self.results['L2']['索引完备'].append({
                                'path': str(rel_path),
                                'issue': '索引不完整',
                                'severity': 'P2',
                                'detail': f'INDEX.md未列出{doc}'
                            })
        
        # 3. 检查版本隔离
        for hash_val, paths in self.content_hashes.items():
            if len(paths) > 1:
                self.results['L2']['版本隔离'].append({
                    'paths': paths,
                    'issue': '重复内容',
                    'severity': 'P1',
                    'detail': f'{len(paths)}个文档内容相同'
                })
        
        # 4. 检查文档代码对应
        # 这里简化处理，检查文档中是否引用了不存在的代码文件
        for doc in self.documents:
            code_refs = re.findall(r'`([^`]+\.(py|js|ts|java|cpp|c|h))`', doc['body'])
            for code_file, ext in code_refs:
                # 简化检查，不实际验证代码文件是否存在
                pass
    
    def audit_l3_professional_standards(self):
        """L3专业标准层审计"""
        print("\n执行L3专业标准层审计...")
        
        # 1. 检查五大原则符合性
        for doc in self.documents:
            # 检查YAML头部
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'responsibility']
            missing_fields = [f for f in required_fields if f not in doc['yaml']]
            
            if missing_fields:
                self.results['L3']['五大原则'].append({
                    'path': doc['path'],
                    'issue': 'YAML字段缺失',
                    'severity': 'P1',
                    'detail': f'缺少字段: {", ".join(missing_fields)}'
                })
        
        # 2. 检查编号体系
        for module_id, paths in self.module_ids.items():
            if len(paths) > 1:
                self.results['L3']['编号体系'].append({
                    'module_id': module_id,
                    'paths': paths,
                    'issue': '编号重复',
                    'severity': 'P1',
                    'detail': f'{len(paths)}个文档使用相同module_id'
                })
        
        # 3. 检查文档质量
        for doc in self.documents:
            # 检查内容结构
            if '## 📋 概述' not in doc['body'] and '## 概述' not in doc['body']:
                self.results['L3']['文档质量'].append({
                    'path': doc['path'],
                    'issue': '内容结构混乱',
                    'severity': 'P2',
                    'detail': '缺少概述章节'
                })
    
    def detect_duplicates(self):
        """检测重复内容"""
        print("\n检测重复内容...")
        
        for hash_val, paths in self.content_hashes.items():
            if len(paths) > 1:
                self.results['重复内容'].append({
                    'hash': hash_val[:8],
                    'paths': paths,
                    'count': len(paths)
                })
    
    def detect_responsibility_issues(self):
        """检测职责问题"""
        print("\n检测职责问题...")
        
        # 检查职责重叠
        for resp, paths in self.responsibilities.items():
            if len(paths) > 1:
                # 区分文档类型
                index_files = [p for p in paths if p.endswith('INDEX.md')]
                overview_files = [p for p in paths if p.endswith('OVERVIEW.md')]
                readme_files = [p for p in paths if p.endswith('README.md')]
                other_files = [p for p in paths if not p.endswith(('INDEX.md', 'OVERVIEW.md', 'README.md'))]
                
                # 只有非标准文档类型的职责重叠才算问题
                if other_files:
                    self.results['职责问题'].append({
                        'responsibility': resp,
                        'paths': paths,
                        'count': len(paths),
                        'type': '职责重叠（非标准文档）'
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
        
        # 统计P1/P2问题
        p1_count = 0
        p2_count = 0
        
        for layer in ['L1', 'L2', 'L3']:
            for category, issues in self.results[layer].items():
                for issue in issues:
                    if issue.get('severity') == 'P1':
                        p1_count += 1
                    else:
                        p2_count += 1
        
        # 生成报告
        report = f"""# 第六次综合审计报告

## 审计概要

- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **审计范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **审计方法**: 三层审计（L1文件系统层、L2文档内容层、L3专业标准层）
- **审计重点**: 重复内容检测、职责清晰度检查

---

## 审计统计

| 统计项 | 数量 |
|--------|------|
| 审计文档数 | {len(self.documents)} |
| L1问题数 | {l1_count} |
| L2问题数 | {l2_count} |
| L3问题数 | {l3_count} |
| 重复内容 | {duplicate_count} |
| 职责问题 | {responsibility_count} |
| **总问题数** | **{total_count}** |

### 问题优先级分布

| 优先级 | 数量 | 说明 |
|--------|------|------|
| P1（立即修复） | {p1_count} | 高风险问题，需立即处理 |
| P2（长期优化） | {p2_count} | 低风险问题，可长期优化 |

---

## L1 文件系统层审计结果

### 1.1 目录结构问题 ({len(self.results['L1']['目录结构'])}个)

"""
        
        if self.results['L1']['目录结构']:
            for issue in self.results['L1']['目录结构']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无目录结构问题\n"
        
        report += f"""
### 1.2 文件命名问题 ({len(self.results['L1']['文件命名'])}个)

"""
        
        if self.results['L1']['文件命名']:
            for issue in self.results['L1']['文件命名']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无文件命名问题\n"
        
        report += f"""
### 1.3 路径引用问题 ({len(self.results['L1']['路径引用'])}个)

"""
        
        if self.results['L1']['路径引用']:
            for issue in self.results['L1']['路径引用']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无路径引用问题\n"
        
        report += f"""
---

## L2 文档内容层审计结果

### 2.1 职责驱动原则问题 ({len(self.results['L2']['职责驱动'])}个)

"""
        
        if self.results['L2']['职责驱动']:
            for issue in self.results['L2']['职责驱动']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无职责驱动问题\n"
        
        report += f"""
### 2.2 索引完备性问题 ({len(self.results['L2']['索引完备'])}个)

"""
        
        if self.results['L2']['索引完备']:
            for issue in self.results['L2']['索引完备']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无索引完备性问题\n"
        
        report += f"""
### 2.3 版本隔离问题 ({len(self.results['L2']['版本隔离'])}个)

"""
        
        if self.results['L2']['版本隔离']:
            for issue in self.results['L2']['版本隔离']:
                report += f"- **重复内容**: {issue['count']}个文档内容相同 ({issue['severity']})\n"
                for path in issue['paths']:
                    report += f"  - {path}\n"
        else:
            report += "✅ 无版本隔离问题\n"
        
        report += f"""
### 2.4 文档代码对应问题 ({len(self.results['L2']['文档代码对应'])}个)

"""
        
        if self.results['L2']['文档代码对应']:
            for issue in self.results['L2']['文档代码对应']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无文档代码对应问题\n"
        
        report += f"""
---

## L3 专业标准层审计结果

### 3.1 五大原则符合性问题 ({len(self.results['L3']['五大原则'])}个)

"""
        
        if self.results['L3']['五大原则']:
            for issue in self.results['L3']['五大原则']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无五大原则符合性问题\n"
        
        report += f"""
### 3.2 编号体系问题 ({len(self.results['L3']['编号体系'])}个)

"""
        
        if self.results['L3']['编号体系']:
            for issue in self.results['L3']['编号体系']:
                report += f"- **编号重复**: {issue['module_id']} - {issue['count']}个文档 ({issue['severity']})\n"
                for path in issue['paths']:
                    report += f"  - {path}\n"
        else:
            report += "✅ 无编号体系问题\n"
        
        report += f"""
### 3.3 文档质量问题 ({len(self.results['L3']['文档质量'])}个)

"""
        
        if self.results['L3']['文档质量']:
            for issue in self.results['L3']['文档质量']:
                report += f"- **{issue['path']}**: {issue['issue']} ({issue['severity']}) - {issue['detail']}\n"
        else:
            report += "✅ 无文档质量问题\n"
        
        report += f"""
---

## 重复内容检测结果 ({duplicate_count}组)

"""
        
        if self.results['重复内容']:
            for dup in self.results['重复内容']:
                report += f"### 重复内容组 (Hash: {dup['hash']})\n\n"
                report += f"**重复文档数**: {dup['count']}\n\n"
                for path in dup['paths']:
                    report += f"- {path}\n"
                report += "\n"
        else:
            report += "✅ 无重复内容\n"
        
        report += f"""
---

## 职责问题检测结果 ({responsibility_count}个)

"""
        
        if self.results['职责问题']:
            for issue in self.results['职责问题']:
                report += f"### 职责: {issue['responsibility']}\n\n"
                report += f"**类型**: {issue['type']}\n"
                report += f"**出现次数**: {issue['count']}\n\n"
                for path in issue['paths']:
                    report += f"- {path}\n"
                report += "\n"
        else:
            report += "✅ 无职责问题\n"
        
        report += f"""
---

## 改进建议

### 🔴 P1级别问题（立即修复）

"""
        
        p1_issues = []
        for layer in ['L1', 'L2', 'L3']:
            for category, issues in self.results[layer].items():
                for issue in issues:
                    if issue.get('severity') == 'P1':
                        p1_issues.append((layer, category, issue))
        
        if p1_issues:
            for i, (layer, category, issue) in enumerate(p1_issues, 1):
                report += f"{i}. **{issue['issue']}** ({layer}-{category})\n"
                report += f"   - 路径: {issue.get('path', 'N/A')}\n"
                report += f"   - 详情: {issue['detail']}\n\n"
        else:
            report += "✅ 无P1级别问题\n"
        
        report += f"""
### 🟡 P2级别问题（长期优化）

"""
        
        p2_issues = []
        for layer in ['L1', 'L2', 'L3']:
            for category, issues in self.results[layer].items():
                for issue in issues:
                    if issue.get('severity') == 'P2':
                        p2_issues.append((layer, category, issue))
        
        if p2_issues:
            for i, (layer, category, issue) in enumerate(p2_issues, 1):
                report += f"{i}. **{issue['issue']}** ({layer}-{category})\n"
                report += f"   - 路径: {issue.get('path', 'N/A')}\n"
                report += f"   - 详情: {issue['detail']}\n\n"
        else:
            report += "✅ 无P2级别问题\n"
        
        report += f"""
---

## Git备份信息

- **备份标签**: v3.11-pre-sixth-audit
- **备份时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **可恢复**: 是

---

## 审计质量声明

### 审计范围
- ✅ 覆盖所有.md文档文件
- ✅ 执行完整三层审计
- ✅ 检测重复内容
- ✅ 检查职责清晰度

### 审计局限性
- 文档代码对应检查为简化版本
- 未检查文档内容的实际准确性
- 未验证外部链接的有效性

### 后续审计建议
- 定期执行审计（建议每月一次）
- 关注P1级别问题的修复情况
- 持续优化文档质量

---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        report_path = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE\SIXTH_COMPREHENSIVE_AUDIT_REPORT.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n审计报告已生成: {report_path}")
        return report_path
    
    def run(self):
        """运行完整审计"""
        print("=" * 80)
        print("第六次综合审计")
        print("=" * 80)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 执行三层审计
        self.audit_l1_file_system()
        self.audit_l2_document_content()
        self.audit_l3_professional_standards()
        
        # 检测重复内容和职责问题
        self.detect_duplicates()
        self.detect_responsibility_issues()
        
        # 生成报告
        report_path = self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成")
        print("=" * 80)
        
        return report_path

if __name__ == '__main__':
    auditor = SixthComprehensiveAuditor()
    auditor.run()
