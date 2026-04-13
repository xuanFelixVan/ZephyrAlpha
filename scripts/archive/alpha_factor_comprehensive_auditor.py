#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层全面深度审计
基于专业量化机构五大原则和三层审计标准
"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

class ComprehensiveAuditor:
    def __init__(self):
        self.results = {
            'L1': {'目录结构': [], '文件命名': [], '路径引用': []},
            'L2': {'职责驱动': [], '索引完备': [], '版本隔离': [], '文档代码对应': []},
            'L3': {'五大原则': [], '文档分类': [], '编号体系': [], '文档质量': []},
            '重复内容': [],
            '职责问题': []
        }
        self.documents = []
        self.module_ids = defaultdict(list)
        self.content_hashes = defaultdict(list)
        
    def scan_documents(self):
        """扫描所有文档"""
        print("=" * 80)
        print("扫描所有文档")
        print("=" * 80)
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                rel_path = file_path.relative_to(FACTOR_LIBRARY)
                
                doc_info = {
                    'path': file_path,
                    'rel_path': str(rel_path),
                    'content': content,
                    'content_hash': hashlib.md5(content.encode()).hexdigest(),
                    'size': len(content)
                }
                
                # 解析YAML头部
                yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    doc_info['yaml'] = self.parse_yaml(yaml_content)
                else:
                    doc_info['yaml'] = {}
                
                # 提取标题
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                doc_info['title'] = title_match.group(1) if title_match else None
                
                # 提取所有链接
                doc_info['links'] = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                self.documents.append(doc_info)
                
                # 记录module_id
                if 'module_id' in doc_info['yaml']:
                    self.module_ids[doc_info['yaml']['module_id']].append(str(rel_path))
                
                # 记录内容哈希
                self.content_hashes[doc_info['content_hash']].append(str(rel_path))
                
            except Exception as e:
                print(f"错误: {file_path.relative_to(FACTOR_LIBRARY)} - {e}")
        
        print(f"\n扫描完成: {len(self.documents)}个文档")
    
    def parse_yaml(self, yaml_content):
        """解析YAML内容"""
        yaml_dict = {}
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value:
                    yaml_dict[key] = value
                elif key == 'responsibility':
                    yaml_dict[key] = []
        
        # 处理responsibility列表
        if 'responsibility' in yaml_dict and isinstance(yaml_dict['responsibility'], list):
            in_responsibility = False
            responsibility_list = []
            for line in yaml_content.split('\n'):
                if line.strip().startswith('responsibility:'):
                    in_responsibility = True
                    continue
                if in_responsibility:
                    if line.strip().startswith('-'):
                        responsibility_list.append(line.strip()[1:].strip())
                    elif not line.strip().startswith(' ') and line.strip():
                        break
            yaml_dict['responsibility'] = responsibility_list
        
        return yaml_dict
    
    def audit_L1_filesystem(self):
        """L1文件系统层审计"""
        print("\n" + "=" * 80)
        print("L1文件系统层审计")
        print("=" * 80)
        
        # 1.1 目录结构问题
        print("\n检查目录结构...")
        self._check_directory_structure()
        
        # 1.2 文件命名问题
        print("\n检查文件命名...")
        self._check_file_naming()
        
        # 1.3 路径引用问题
        print("\n检查路径引用...")
        self._check_path_references()
    
    def _check_directory_structure(self):
        """检查目录结构"""
        # 检查稀疏目录
        for dir_path in FACTOR_LIBRARY.rglob('*'):
            if not dir_path.is_dir():
                continue
            
            files = list(dir_path.glob('*.md'))
            if len(files) < 3:
                rel_path = dir_path.relative_to(FACTOR_LIBRARY)
                self.results['L1']['目录结构'].append({
                    'type': '稀疏目录',
                    'path': str(rel_path),
                    'file_count': len(files),
                    'severity': 'P2'
                })
        
        # 检查空目录
        for dir_path in FACTOR_LIBRARY.rglob('*'):
            if not dir_path.is_dir():
                continue
            
            if not any(dir_path.iterdir()):
                rel_path = dir_path.relative_to(FACTOR_LIBRARY)
                self.results['L1']['目录结构'].append({
                    'type': '空目录',
                    'path': str(rel_path),
                    'severity': 'P1'
                })
        
        # 检查目录层级深度
        for dir_path in FACTOR_LIBRARY.rglob('*'):
            if not dir_path.is_dir():
                continue
            
            depth = len(dir_path.relative_to(FACTOR_LIBRARY).parts)
            if depth > 4:
                rel_path = dir_path.relative_to(FACTOR_LIBRARY)
                self.results['L1']['目录结构'].append({
                    'type': '层级过深',
                    'path': str(rel_path),
                    'depth': depth,
                    'severity': 'P2'
                })
    
    def _check_file_naming(self):
        """检查文件命名"""
        for doc in self.documents:
            file_name = Path(doc['rel_path']).name
            
            # 检查旧架构命名残留
            if 'Layer' in file_name or 'layer' in file_name:
                self.results['L1']['文件命名'].append({
                    'type': '旧架构命名残留',
                    'path': doc['rel_path'],
                    'severity': 'P1'
                })
            
            # 检查特殊字符
            if re.search(r'[\u4e00-\u9fa5\s]', file_name):
                self.results['L1']['文件命名'].append({
                    'type': '特殊字符',
                    'path': doc['rel_path'],
                    'severity': 'P2'
                })
    
    def _check_path_references(self):
        """检查路径引用"""
        for doc in self.documents:
            for link_text, link_path in doc['links']:
                # 检查死链接
                if link_path.startswith('./') or link_path.startswith('../'):
                    # 相对路径
                    doc_dir = Path(doc['rel_path']).parent
                    target_path = (FACTOR_LIBRARY / doc_dir / link_path).resolve()
                    
                    if not target_path.exists():
                        self.results['L1']['路径引用'].append({
                            'type': '死链接',
                            'source': doc['rel_path'],
                            'target': link_path,
                            'severity': 'P1'
                        })
    
    def audit_L2_content(self):
        """L2文档内容层审计"""
        print("\n" + "=" * 80)
        print("L2文档内容层审计")
        print("=" * 80)
        
        # 2.1 职责驱动原则问题
        print("\n检查职责驱动原则...")
        self._check_responsibility()
        
        # 2.2 索引完备性问题
        print("\n检查索引完备性...")
        self._check_index_completeness()
        
        # 2.3 版本隔离问题
        print("\n检查版本隔离...")
        self._check_version_isolation()
        
        # 2.4 文档代码对应问题
        print("\n检查文档代码对应...")
        self._check_doc_code_correspondence()
    
    def _check_responsibility(self):
        """检查职责驱动原则"""
        for doc in self.documents:
            # 检查职责描述缺失
            if 'responsibility' not in doc['yaml'] or not doc['yaml']['responsibility']:
                self.results['L2']['职责驱动'].append({
                    'type': '职责描述缺失',
                    'path': doc['rel_path'],
                    'severity': 'P1'
                })
            
            # 检查职责描述模糊
            if 'responsibility' in doc['yaml'] and doc['yaml']['responsibility']:
                for resp in doc['yaml']['responsibility']:
                    if len(resp) < 10 or '提供' in resp and '文档支持' in resp:
                        self.results['L2']['职责驱动'].append({
                            'type': '职责描述模糊',
                            'path': doc['rel_path'],
                            'responsibility': resp,
                            'severity': 'P2'
                        })
                        break
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        # 检查缺少INDEX的目录
        for dir_path in FACTOR_LIBRARY.rglob('*'):
            if not dir_path.is_dir():
                continue
            
            if not (dir_path / 'INDEX.md').exists():
                rel_path = dir_path.relative_to(FACTOR_LIBRARY)
                self.results['L2']['索引完备'].append({
                    'type': '缺少INDEX',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
    
    def _check_version_isolation(self):
        """检查版本隔离"""
        # 检查重复module_id
        for module_id, paths in self.module_ids.items():
            if len(paths) > 1:
                self.results['L2']['版本隔离'].append({
                    'type': '重复module_id',
                    'module_id': module_id,
                    'paths': paths,
                    'severity': 'P1'
                })
        
        # 检查变更记录缺失
        for doc in self.documents:
            if '变更记录' not in doc['content'] and '变更历史' not in doc['content']:
                self.results['L2']['版本隔离'].append({
                    'type': '变更记录缺失',
                    'path': doc['rel_path'],
                    'severity': 'P2'
                })
    
    def _check_doc_code_correspondence(self):
        """检查文档代码对应"""
        # 检查标题缺失
        for doc in self.documents:
            if not doc['title']:
                self.results['L2']['文档代码对应'].append({
                    'type': '标题缺失',
                    'path': doc['rel_path'],
                    'severity': 'P2'
                })
    
    def audit_L3_standards(self):
        """L3专业标准层审计"""
        print("\n" + "=" * 80)
        print("L3专业标准层审计")
        print("=" * 80)
        
        # 3.1 五大原则符合性问题
        print("\n检查五大原则符合性...")
        self._check_five_principles()
        
        # 3.2 文档分类问题
        print("\n检查文档分类...")
        self._check_document_classification()
        
        # 3.3 编号体系问题
        print("\n检查编号体系...")
        self._check_numbering_system()
        
        # 3.4 文档质量问题
        print("\n检查文档质量...")
        self._check_document_quality()
    
    def _check_five_principles(self):
        """检查五大原则符合性"""
        for doc in self.documents:
            # 检查YAML头部完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'responsibility']
            missing_fields = [f for f in required_fields if f not in doc['yaml']]
            
            if missing_fields:
                self.results['L3']['五大原则'].append({
                    'type': 'YAML字段缺失',
                    'path': doc['rel_path'],
                    'missing_fields': missing_fields,
                    'severity': 'P1'
                })
    
    def _check_document_classification(self):
        """检查文档分类"""
        # 检查文档是否在正确的分类目录
        pass
    
    def _check_numbering_system(self):
        """检查编号体系"""
        # 检查module_id格式
        for doc in self.documents:
            if 'module_id' in doc['yaml']:
                module_id = doc['yaml']['module_id']
                
                # 检查module_id是否包含中文
                if re.search(r'[\u4e00-\u9fa5]', module_id):
                    self.results['L3']['编号体系'].append({
                        'type': 'module_id包含中文',
                        'path': doc['rel_path'],
                        'module_id': module_id,
                        'severity': 'P2'
                    })
    
    def _check_document_quality(self):
        """检查文档质量"""
        for doc in self.documents:
            # 检查文档大小过小
            if doc['size'] < 200:
                self.results['L3']['文档质量'].append({
                    'type': '文档内容过少',
                    'path': doc['rel_path'],
                    'size': doc['size'],
                    'severity': 'P2'
                })
    
    def check_duplicates(self):
        """检查重复内容"""
        print("\n" + "=" * 80)
        print("检查重复内容")
        print("=" * 80)
        
        # 检查完全相同的文档
        for content_hash, paths in self.content_hashes.items():
            if len(paths) > 1:
                self.results['重复内容'].append({
                    'type': '完全相同',
                    'paths': paths,
                    'severity': 'P0'
                })
        
        # 检查相似内容
        print("\n检查相似内容...")
        for i, doc1 in enumerate(self.documents):
            for doc2 in self.documents[i+1:]:
                # 简单的相似度检查
                if doc1['size'] > 500 and doc2['size'] > 500:
                    # 提取内容关键词
                    keywords1 = set(re.findall(r'[\u4e00-\u9fa5]{2,}', doc1['content']))
                    keywords2 = set(re.findall(r'[\u4e00-\u9fa5]{2,}', doc2['content']))
                    
                    if keywords1 and keywords2:
                        similarity = len(keywords1 & keywords2) / min(len(keywords1), len(keywords2))
                        
                        if similarity > 0.7 and doc1['content_hash'] != doc2['content_hash']:
                            self.results['重复内容'].append({
                                'type': '内容相似',
                                'path1': doc1['rel_path'],
                                'path2': doc2['rel_path'],
                                'similarity': f"{similarity:.2%}",
                                'severity': 'P1'
                            })
    
    def check_responsibility_clarity(self):
        """检查职责清晰度"""
        print("\n" + "=" * 80)
        print("检查职责清晰度")
        print("=" * 80)
        
        # 收集所有职责描述
        responsibilities = []
        for doc in self.documents:
            if 'responsibility' in doc['yaml'] and doc['yaml']['responsibility']:
                for resp in doc['yaml']['responsibility']:
                    responsibilities.append({
                        'path': doc['rel_path'],
                        'responsibility': resp
                    })
        
        # 检查职责重叠
        for i, resp1 in enumerate(responsibilities):
            for resp2 in responsibilities[i+1:]:
                if resp1['responsibility'] == resp2['responsibility']:
                    self.results['职责问题'].append({
                        'type': '职责完全相同',
                        'path1': resp1['path'],
                        'path2': resp2['path'],
                        'responsibility': resp1['responsibility'],
                        'severity': 'P1'
                    })
    
    def generate_report(self):
        """生成审计报告"""
        print("\n" + "=" * 80)
        print("生成审计报告")
        print("=" * 80)
        
        # 统计问题数量
        l1_count = sum(len(v) for v in self.results['L1'].values())
        l2_count = sum(len(v) for v in self.results['L2'].values())
        l3_count = sum(len(v) for v in self.results['L3'].values())
        duplicate_count = len(self.results['重复内容'])
        responsibility_count = len(self.results['职责问题'])
        
        total_count = l1_count + l2_count + l3_count + duplicate_count + responsibility_count
        
        # 生成报告
        report = f"""# Alpha因子层全面深度审计报告

## 审计概要

- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **审计范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **审计方法**: 专业量化机构五大原则 + 三层审计标准
- **审计结论**: 发现{total_count}个问题

## 审计统计

| 统计项 | 数量 |
|--------|------|
| 总文档数 | {len(self.documents)} |
| 总问题数 | {total_count} |
| L1问题 | {l1_count} |
| L2问题 | {l2_count} |
| L3问题 | {l3_count} |
| 重复内容 | {duplicate_count} |
| 职责问题 | {responsibility_count} |

## L1 文件系统层问题

### 目录结构问题 ({len(self.results['L1']['目录结构'])}个)

"""
        
        for issue in self.results['L1']['目录结构'][:20]:
            report += f"- **{issue['type']}**: {issue['path']}"
            if 'file_count' in issue:
                report += f" ({issue['file_count']}个文件)"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
### 文件命名问题 ({len(self.results['L1']['文件命名'])}个)

"""
        
        for issue in self.results['L1']['文件命名'][:20]:
            report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        
        report += f"""
### 路径引用问题 ({len(self.results['L1']['路径引用'])}个)

"""
        
        for issue in self.results['L1']['路径引用'][:20]:
            report += f"- **{issue['type']}**: {issue['source']} -> {issue['target']} [{issue['severity']}]\n"
        
        report += f"""
## L2 文档内容层问题

### 职责驱动问题 ({len(self.results['L2']['职责驱动'])}个)

"""
        
        for issue in self.results['L2']['职责驱动'][:20]:
            report += f"- **{issue['type']}**: {issue['path']}"
            if 'responsibility' in issue:
                report += f" - {issue['responsibility']}"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
### 索引完备问题 ({len(self.results['L2']['索引完备'])}个)

"""
        
        for issue in self.results['L2']['索引完备'][:20]:
            report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        
        report += f"""
### 版本隔离问题 ({len(self.results['L2']['版本隔离'])}个)

"""
        
        for issue in self.results['L2']['版本隔离'][:20]:
            report += f"- **{issue['type']}**: {issue.get('path', issue.get('module_id', ''))}"
            if 'paths' in issue:
                report += f" ({len(issue['paths'])}个文件)"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
### 文档代码对应问题 ({len(self.results['L2']['文档代码对应'])}个)

"""
        
        for issue in self.results['L2']['文档代码对应'][:20]:
            report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        
        report += f"""
## L3 专业标准层问题

### 五大原则问题 ({len(self.results['L3']['五大原则'])}个)

"""
        
        for issue in self.results['L3']['五大原则'][:20]:
            report += f"- **{issue['type']}**: {issue['path']}"
            if 'missing_fields' in issue:
                report += f" (缺失: {', '.join(issue['missing_fields'])})"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
### 编号体系问题 ({len(self.results['L3']['编号体系'])}个)

"""
        
        for issue in self.results['L3']['编号体系'][:20]:
            report += f"- **{issue['type']}**: {issue['path']} [{issue['severity']}]\n"
        
        report += f"""
### 文档质量问题 ({len(self.results['L3']['文档质量'])}个)

"""
        
        for issue in self.results['L3']['文档质量'][:20]:
            report += f"- **{issue['type']}**: {issue['path']}"
            if 'size' in issue:
                report += f" ({issue['size']}字节)"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
## 重复内容问题 ({len(self.results['重复内容'])}个)

"""
        
        for issue in self.results['重复内容'][:20]:
            if issue['type'] == '完全相同':
                report += f"- **完全相同**: {', '.join(issue['paths'])} [{issue['severity']}]\n"
            else:
                report += f"- **内容相似**: {issue['path1']} <-> {issue['path2']} (相似度: {issue['similarity']}) [{issue['severity']}]\n"
        
        report += f"""
## 职责问题 ({len(self.results['职责问题'])}个)

"""
        
        for issue in self.results['职责问题'][:20]:
            report += f"- **{issue['type']}**: {issue['path1']} <-> {issue['path2']}"
            if 'responsibility' in issue:
                report += f" - {issue['responsibility']}"
            report += f" [{issue['severity']}]\n"
        
        report += f"""
## 改进建议

### 立即行动 (P0)

"""
        
        p0_issues = []
        for category in self.results.values():
            if isinstance(category, dict):
                for issues in category.values():
                    for issue in issues:
                        if issue.get('severity') == 'P0':
                            p0_issues.append(issue)
            else:
                for issue in category:
                    if issue.get('severity') == 'P0':
                        p0_issues.append(issue)
        
        if p0_issues:
            for issue in p0_issues[:10]:
                report += f"- 处理{issue['type']}: {issue.get('path', issue.get('paths', ''))}\n"
        else:
            report += "- 无P0级别问题\n"
        
        report += f"""
### 短期改进 (P1)

"""
        
        p1_issues = []
        for category in self.results.values():
            if isinstance(category, dict):
                for issues in category.values():
                    for issue in issues:
                        if issue.get('severity') == 'P1':
                            p1_issues.append(issue)
            else:
                for issue in category:
                    if issue.get('severity') == 'P1':
                        p1_issues.append(issue)
        
        if p1_issues:
            report += f"- 修复{len(p1_issues)}个P1级别问题\n"
        else:
            report += "- 无P1级别问题\n"
        
        report += f"""
### 长期优化 (P2)

"""
        
        p2_issues = []
        for category in self.results.values():
            if isinstance(category, dict):
                for issues in category.values():
                    for issue in issues:
                        if issue.get('severity') == 'P2':
                            p2_issues.append(issue)
            else:
                for issue in category:
                    if issue.get('severity') == 'P2':
                        p2_issues.append(issue)
        
        if p2_issues:
            report += f"- 优化{len(p2_issues)}个P2级别问题\n"
        else:
            report += "- 无P2级别问题\n"
        
        report += f"""
---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        report_path = FACTOR_LIBRARY.parent / '09_AUDIT' / 'STATE' / f'ALPHA_FACTOR_COMPREHENSIVE_AUDIT_REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n报告已生成: {report_path}")
        
        # 保存JSON数据
        json_path = report_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存: {json_path}")
        
        return report_path
    
    def run(self):
        """运行审计"""
        print("=" * 80)
        print("Alpha因子层全面深度审计")
        print("=" * 80)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.scan_documents()
        self.audit_L1_filesystem()
        self.audit_L2_content()
        self.audit_L3_standards()
        self.check_duplicates()
        self.check_responsibility_clarity()
        self.generate_report()

if __name__ == '__main__':
    auditor = ComprehensiveAuditor()
    auditor.run()
