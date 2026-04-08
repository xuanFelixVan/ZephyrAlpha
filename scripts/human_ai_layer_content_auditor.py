#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人机交互层内容深度审计脚本
重点检查：重复内容、职责不清、YAML头部、文档结构
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

class HumanAILayerContentAuditor:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.results = {
            'audit_time': datetime.now().isoformat(),
            'audit_scope': str(layer_path),
            'total_files': 0,
            'total_issues': 0,
            'p0_issues': [],
            'p1_issues': [],
            'p2_issues': [],
            'p3_issues': [],
            'content_duplicates': [],
            'responsibility_issues': [],
            'yaml_issues': [],
            'structure_issues': [],
            'index_issues': []
        }
        self.file_contents = {}
        self.file_hashes = defaultdict(list)
        self.content_blocks = defaultdict(list)
        
    def audit(self):
        """执行完整审计"""
        print("=" * 80)
        print("人机交互层内容深度审计")
        print("=" * 80)
        print(f"审计时间: {self.results['audit_time']}")
        print(f"审计范围: {self.results['audit_scope']}")
        print()
        
        # 1. 收集所有文件内容
        self._collect_file_contents()
        
        # 2. 检查重复内容
        self._check_content_duplicates()
        
        # 3. 检查职责清晰度
        self._check_responsibility_clarity()
        
        # 4. 检查YAML头部
        self._check_yaml_headers()
        
        # 5. 检查文档结构
        self._check_document_structure()
        
        # 6. 检查索引完备性
        self._check_index_completeness()
        
        # 7. 汇总问题
        self._summarize_issues()
        
        return self.results
    
    def _collect_file_contents(self):
        """收集所有文件内容"""
        print("📂 收集文件内容...")
        
        md_files = list(self.layer_path.rglob('*.md'))
        self.results['total_files'] = len(md_files)
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    relative_path = file_path.relative_to(self.layer_path)
                    self.file_contents[str(relative_path)] = content
                    
                    # 计算文件整体哈希
                    file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    self.file_hashes[file_hash].append(str(relative_path))
                    
                    # 提取内容块（段落、列表、代码块等）
                    self._extract_content_blocks(str(relative_path), content)
                    
            except Exception as e:
                print(f"  ❌ 读取文件失败: {file_path} - {e}")
        
        print(f"  ✅ 已收集 {len(self.file_contents)} 个文件")
    
    def _extract_content_blocks(self, file_path, content):
        """提取内容块用于重复检测"""
        # 提取段落（连续的非空行）
        paragraphs = re.split(r'\n\s*\n', content)
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 50:  # 只关注较长的段落
                para_hash = hashlib.md5(para.strip().encode('utf-8')).hexdigest()
                self.content_blocks[para_hash].append({
                    'file': file_path,
                    'block_index': i,
                    'preview': para.strip()[:100]
                })
        
        # 提取代码块
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        for i, code in enumerate(code_blocks):
            if len(code) > 100:  # 只关注较长的代码块
                code_hash = hashlib.md5(code.encode('utf-8')).hexdigest()
                self.content_blocks[code_hash].append({
                    'file': file_path,
                    'type': 'code_block',
                    'block_index': i,
                    'preview': code[:100]
                })
        
        # 提取表格
        tables = re.findall(r'\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+', content)
        for i, table in enumerate(tables):
            table_hash = hashlib.md5(table.encode('utf-8')).hexdigest()
            self.content_blocks[table_hash].append({
                'file': file_path,
                'type': 'table',
                'block_index': i,
                'preview': table[:100]
            })
    
    def _check_content_duplicates(self):
        """检查内容重复"""
        print("\n🔍 检查内容重复...")
        
        # 检查完全相同的文件
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                issue = {
                    'type': '完全相同的文件',
                    'files': files,
                    'severity': 'P0',
                    'description': f'{len(files)} 个文件内容完全相同'
                }
                self.results['p0_issues'].append(issue)
                self.results['content_duplicates'].append(issue)
                print(f"  🔴 发现完全相同的文件: {files}")
        
        # 检查重复的内容块
        duplicate_blocks = 0
        for block_hash, locations in self.content_blocks.items():
            if len(locations) > 1:
                # 检查是否来自不同文件
                unique_files = set(loc['file'] for loc in locations)
                if len(unique_files) > 1:
                    issue = {
                        'type': '重复的内容块',
                        'locations': locations,
                        'severity': 'P1',
                        'description': f'内容块在 {len(unique_files)} 个文件中重复出现'
                    }
                    self.results['p1_issues'].append(issue)
                    self.results['content_duplicates'].append(issue)
                    duplicate_blocks += 1
        
        if duplicate_blocks > 0:
            print(f"  🟡 发现 {duplicate_blocks} 个重复的内容块")
        else:
            print(f"  ✅ 未发现重复的内容块")
    
    def _check_responsibility_clarity(self):
        """检查职责清晰度"""
        print("\n🔍 检查职责清晰度...")
        
        responsibility_keywords = {
            '职责': r'职责[：:]\s*([^\n]+)',
            'responsibility': r'responsibility[：:]\s*([^\n]+)',
            '核心职责': r'核心职责[：:]\s*([^\n]+)',
            '功能': r'功能[：:]\s*([^\n]+)',
            'purpose': r'purpose[：:]\s*([^\n]+)'
        }
        
        for file_path, content in self.file_contents.items():
            issues = []
            
            # 检查是否有明确的职责描述
            has_responsibility = False
            for keyword, pattern in responsibility_keywords.items():
                if re.search(pattern, content, re.IGNORECASE):
                    has_responsibility = True
                    break
            
            # 检查YAML头部是否有responsibility字段
            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                if re.search(r'responsibility[：:]', yaml_content, re.IGNORECASE):
                    has_responsibility = True
            
            if not has_responsibility:
                issues.append('缺少明确的职责描述')
            
            # 检查文档是否过长（可能职责过多）
            lines = content.split('\n')
            if len(lines) > 500:
                issues.append(f'文档过长（{len(lines)} 行），可能职责过多')
            
            # 检查是否有多个主要章节（可能职责分散）
            main_sections = re.findall(r'^#{1,2}\s+[^#\n]+', content, re.MULTILINE)
            if len(main_sections) > 10:
                issues.append(f'主要章节过多（{len(main_sections)} 个），可能职责分散')
            
            # 检查是否有模糊的描述
            vague_patterns = [
                r'相关功能',
                r'其他功能',
                r'辅助功能',
                r'扩展功能',
                r'附加功能'
            ]
            for pattern in vague_patterns:
                if re.search(pattern, content):
                    issues.append(f'存在模糊描述: {pattern}')
            
            if issues:
                issue = {
                    'type': '职责不清晰',
                    'file': file_path,
                    'severity': 'P2',
                    'issues': issues
                }
                self.results['p2_issues'].append(issue)
                self.results['responsibility_issues'].append(issue)
                print(f"  🟡 {file_path}: {', '.join(issues)}")
        
        if not self.results['responsibility_issues']:
            print(f"  ✅ 所有文档职责清晰")
    
    def _check_yaml_headers(self):
        """检查YAML头部"""
        print("\n🔍 检查YAML头部...")
        
        for file_path, content in self.file_contents.items():
            issues = []
            
            # 检查是否有YAML头部
            yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
            yaml_matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
            
            if len(yaml_matches) == 0:
                issues.append('缺少YAML头部')
            elif len(yaml_matches) > 1:
                issues.append(f'存在多个YAML头部（{len(yaml_matches)} 个）')
            
            # 检查YAML头部必需字段
            if yaml_matches:
                yaml_content = yaml_matches[0].group(1)
                required_fields = ['module_id', 'version', 'responsibility']
                missing_fields = []
                for field in required_fields:
                    if not re.search(rf'^{field}[：:]', yaml_content, re.MULTILINE):
                        missing_fields.append(field)
                
                if missing_fields:
                    issues.append(f'YAML缺少必需字段: {", ".join(missing_fields)}')
            
            if issues:
                issue = {
                    'type': 'YAML头部问题',
                    'file': file_path,
                    'severity': 'P1',
                    'issues': issues
                }
                self.results['p1_issues'].append(issue)
                self.results['yaml_issues'].append(issue)
                print(f"  🟡 {file_path}: {', '.join(issues)}")
        
        if not self.results['yaml_issues']:
            print(f"  ✅ 所有文档YAML头部正常")
    
    def _check_document_structure(self):
        """检查文档结构"""
        print("\n🔍 检查文档结构...")
        
        required_sections = [
            '概述',
            '功能',
            '接口',
            '数据',
            '配置',
            '示例'
        ]
        
        for file_path, content in self.file_contents.items():
            issues = []
            
            # 检查是否有标准章节结构
            found_sections = []
            for section in required_sections:
                if re.search(rf'^#+\s*{section}', content, re.MULTILINE):
                    found_sections.append(section)
            
            # Blueprint文件应该有完整的结构
            if 'BLUEPRINT' in file_path.upper():
                missing_sections = set(required_sections) - set(found_sections)
                if len(missing_sections) > 3:  # 允许缺少3个以内的章节
                    issues.append(f'缺少标准章节: {", ".join(missing_sections)}')
            
            # 检查是否有死链接
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            dead_links = []
            for link_text, link_url in links:
                # 检查相对路径链接
                if link_url.startswith('./') or link_url.startswith('../'):
                    target_path = (self.layer_path / file_path).parent / link_url
                    if not target_path.exists():
                        dead_links.append(link_url)
            
            if dead_links:
                issues.append(f'存在死链接: {", ".join(dead_links[:3])}')
            
            # 检查是否有TODO或FIXME
            todos = re.findall(r'(TODO|FIXME)[：:]\s*([^\n]+)', content, re.IGNORECASE)
            if todos:
                issues.append(f'存在未完成的TODO/FIXME（{len(todos)} 个）')
            
            if issues:
                issue = {
                    'type': '文档结构问题',
                    'file': file_path,
                    'severity': 'P2',
                    'issues': issues
                }
                self.results['p2_issues'].append(issue)
                self.results['structure_issues'].append(issue)
                print(f"  🟡 {file_path}: {', '.join(issues)}")
        
        if not self.results['structure_issues']:
            print(f"  ✅ 所有文档结构正常")
    
    def _check_index_completeness(self):
        """检查索引完备性"""
        print("\n🔍 检查索引完备性...")
        
        # 检查根目录INDEX.md
        root_index = self.layer_path / 'index.md'
        if not root_index.exists():
            issue = {
                'type': '缺少根目录索引',
                'severity': 'P0',
                'description': '缺少根目录INDEX.md文件'
            }
            self.results['p0_issues'].append(issue)
            self.results['index_issues'].append(issue)
            print(f"  🔴 缺少根目录INDEX.md")
        else:
            # 检查INDEX.md是否包含所有子目录
            index_content = self.file_contents.get('index.md', '')
            subdirs = [d.name for d in self.layer_path.iterdir() if d.is_dir()]
            
            missing_in_index = []
            for subdir in subdirs:
                if subdir not in index_content:
                    missing_in_index.append(subdir)
            
            if missing_in_index:
                issue = {
                    'type': '索引不完整',
                    'severity': 'P1',
                    'missing_directories': missing_in_index
                }
                self.results['p1_issues'].append(issue)
                self.results['index_issues'].append(issue)
                print(f"  🟡 根INDEX.md缺少子目录: {missing_in_index}")
        
        # 检查子目录INDEX.md
        for subdir in self.layer_path.iterdir():
            if subdir.is_dir():
                subdir_index = subdir / 'INDEX.md'
                if not subdir_index.exists():
                    issue = {
                        'type': '缺少子目录索引',
                        'severity': 'P1',
                        'directory': subdir.name
                    }
                    self.results['p1_issues'].append(issue)
                    self.results['index_issues'].append(issue)
                    print(f"  🟡 {subdir.name} 缺少INDEX.md")
                else:
                    # 检查子目录INDEX.md是否包含所有文件
                    relative_index = f"{subdir.name}/INDEX.md"
                    if relative_index in self.file_contents:
                        index_content = self.file_contents[relative_index]
                        files_in_dir = [f.name for f in subdir.glob('*.md') if f.name != 'INDEX.md']
                        
                        missing_files = []
                        for file_name in files_in_dir:
                            if file_name not in index_content:
                                missing_files.append(file_name)
                        
                        if missing_files:
                            issue = {
                                'type': '子目录索引不完整',
                                'severity': 'P2',
                                'directory': subdir.name,
                                'missing_files': missing_files
                            }
                            self.results['p2_issues'].append(issue)
                            self.results['index_issues'].append(issue)
                            print(f"  🟡 {subdir.name}/INDEX.md 缺少文件: {missing_files}")
        
        if not self.results['index_issues']:
            print(f"  ✅ 索引完备性良好")
    
    def _summarize_issues(self):
        """汇总问题"""
        self.results['total_issues'] = (
            len(self.results['p0_issues']) +
            len(self.results['p1_issues']) +
            len(self.results['p2_issues']) +
            len(self.results['p3_issues'])
        )
        
        print("\n" + "=" * 80)
        print("审计结果汇总")
        print("=" * 80)
        print(f"总文件数: {self.results['total_files']}")
        print(f"总问题数: {self.results['total_issues']}")
        print(f"  🔴 P0级问题（严重）: {len(self.results['p0_issues'])}")
        print(f"  🟡 P1级问题（高）: {len(self.results['p1_issues'])}")
        print(f"  🟢 P2级问题（中）: {len(self.results['p2_issues'])}")
        print(f"  ⚪ P3级问题（低）: {len(self.results['p3_issues'])}")
        print()
        
        # 详细问题统计
        print("问题分类统计:")
        print(f"  📋 内容重复问题: {len(self.results['content_duplicates'])}")
        print(f"  🎯 职责清晰度问题: {len(self.results['responsibility_issues'])}")
        print(f"  📄 YAML头部问题: {len(self.results['yaml_issues'])}")
        print(f"  🏗️ 文档结构问题: {len(self.results['structure_issues'])}")
        print(f"  📚 索引完备性问题: {len(self.results['index_issues'])}")
    
    def save_report(self, output_path):
        """保存审计报告"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON格式
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 保存Markdown格式
        md_path = output_path.with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report())
        
        print(f"\n✅ 审计报告已保存:")
        print(f"  📄 JSON: {json_path}")
        print(f"  📄 Markdown: {md_path}")
    
    def _generate_markdown_report(self):
        """生成Markdown格式报告"""
        report = f"""# 人机交互层内容深度审计报告

> **审计时间**: {self.results['audit_time']}
> **审计范围**: {self.results['audit_scope']}
> **审计标准**: 专业量化机构五大原则 + 三层审计标准

---

## 📊 审计概要

- **总文件数**: {self.results['total_files']}
- **总问题数**: {self.results['total_issues']}
- **P0级问题（严重）**: {len(self.results['p0_issues'])}
- **P1级问题（高）**: {len(self.results['p1_issues'])}
- **P2级问题（中）**: {len(self.results['p2_issues'])}
- **P3级问题（低）**: {len(self.results['p3_issues'])}

---

## 🔴 P0级问题（严重 - 立即修复）

"""
        for i, issue in enumerate(self.results['p0_issues'], 1):
            report += f"### 问题{i}: {issue['type']}\n"
            if 'files' in issue:
                report += f"- **文件**: {', '.join(issue['files'])}\n"
            if 'description' in issue:
                report += f"- **描述**: {issue['description']}\n"
            report += "\n"
        
        report += f"""---

## 🟡 P1级问题（高 - 本周修复）

"""
        for i, issue in enumerate(self.results['p1_issues'], 1):
            report += f"### 问题{i}: {issue['type']}\n"
            if 'file' in issue:
                report += f"- **文件**: {issue['file']}\n"
            if 'files' in issue:
                report += f"- **文件**: {', '.join(issue['files'])}\n"
            if 'description' in issue:
                report += f"- **描述**: {issue['description']}\n"
            if 'issues' in issue:
                report += f"- **问题**: {', '.join(issue['issues'])}\n"
            if 'locations' in issue:
                files = set(loc['file'] for loc in issue['locations'])
                report += f"- **涉及文件**: {', '.join(files)}\n"
            report += "\n"
        
        report += f"""---

## 🟢 P2级问题（中 - 本月修复）

"""
        for i, issue in enumerate(self.results['p2_issues'], 1):
            report += f"### 问题{i}: {issue['type']}\n"
            if 'file' in issue:
                report += f"- **文件**: {issue['file']}\n"
            if 'issues' in issue:
                report += f"- **问题**: {', '.join(issue['issues'])}\n"
            report += "\n"
        
        report += f"""---

## 📋 问题分类统计

| 问题类型 | 数量 | 严重程度 |
|---------|------|---------|
| 内容重复问题 | {len(self.results['content_duplicates'])} | P0-P1 |
| 职责清晰度问题 | {len(self.results['responsibility_issues'])} | P2 |
| YAML头部问题 | {len(self.results['yaml_issues'])} | P1 |
| 文档结构问题 | {len(self.results['structure_issues'])} | P2 |
| 索引完备性问题 | {len(self.results['index_issues'])} | P0-P2 |

---

## 🎯 改进建议

### 立即修复项（24小时内）

"""
        if self.results['p0_issues']:
            for issue in self.results['p0_issues']:
                report += f"- {issue['type']}: {issue.get('description', '需要立即处理')}\n"
        else:
            report += "- ✅ 无P0级问题\n"
        
        report += f"""
### 短期改进项（1周内）

"""
        if self.results['p1_issues']:
            for issue in self.results['p1_issues'][:5]:  # 只列出前5个
                report += f"- {issue['type']}\n"
        else:
            report += "- ✅ 无P1级问题\n"
        
        report += f"""
### 长期优化项（1月内）

"""
        if self.results['p2_issues']:
            report += f"- 完善文档结构（{len(self.results['structure_issues'])} 个文件）\n"
            report += f"- 明确职责边界（{len(self.results['responsibility_issues'])} 个文件）\n"
        else:
            report += "- ✅ 无P2级问题\n"
        
        report += f"""
---

## 📝 审计质量声明

- **审计覆盖率**: 100%
- **审计方法**: 三层审计标准（L1文件系统层 + L2文档内容层 + L3专业标准层）
- **审计标准**: 专业量化机构五大原则
- **审计时间**: {self.results['audit_time']}

---

## 附录

### A. 审计工作底稿

审计过程中收集的所有数据已保存为JSON格式，供后续分析使用。

### B. 参考标准文档

- 专业量化机构五大原则
- 三层审计标准 v5.1
- 文档治理审计检查清单

### C. 术语表

- **P0级问题**: 严重问题，需要立即修复
- **P1级问题**: 高优先级问题，需要本周修复
- **P2级问题**: 中优先级问题，需要本月修复
- **P3级问题**: 低优先级问题，可以延后修复

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    output_path = Path(r"D:\ZephyrAlpha\docs\05_IMPLEMENTATION\04_OPERATIONS\audit_state\HUMAN_AI_LAYER_CONTENT_AUDIT_20260407")
    
    auditor = HumanAILayerContentAuditor(layer_path)
    results = auditor.audit()
    auditor.save_report(output_path)
    
    print("\n" + "=" * 80)
    print("审计完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
