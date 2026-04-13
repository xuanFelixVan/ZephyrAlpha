#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Alpha因子层第三次全面深度审计（修复版）
修复YAML解析问题
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import yaml

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

class ThirdComprehensiveAuditorFixed:
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
    
    def scan_documents(self):
        """扫描所有文档"""
        print("\n扫描文档...")
        
        for file_path in FACTOR_LIBRARY.rglob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                rel_path = file_path.relative_to(FACTOR_LIBRARY)
                
                yaml_dict, body_content = self.parse_yaml_safe(content)
                
                # 计算内容哈希（用于检测重复）
                body_hash = hashlib.md5(body_content.encode()).hexdigest()
                self.content_hashes[body_hash].append(str(rel_path))
                
                # 提取module_id
                module_id = yaml_dict.get('module_id', '')
                if module_id:
                    self.module_ids[module_id].append(str(rel_path))
                
                # 提取职责
                responsibility = yaml_dict.get('responsibility', [])
                if responsibility and isinstance(responsibility, list):
                    resp_str = '|'.join(sorted([str(r) for r in responsibility]))
                    self.responsibilities[resp_str].append(str(rel_path))
                
                self.documents.append({
                    'path': str(rel_path),
                    'file_size': file_path.stat().st_size,
                    'yaml': yaml_dict,
                    'body': body_content,
                    'module_id': module_id,
                    'responsibility': responsibility if isinstance(responsibility, list) else []
                })
                
            except Exception as e:
                print(f"错误: {file_path} - {e}")
        
        print(f"扫描完成: {len(self.documents)}个文档")
    
    def audit_L1_filesystem(self):
        """L1文件系统层审计"""
        print("\nL1文件系统层审计...")
        
        # 检查目录结构
        for root, dirs, files in os.walk(FACTOR_LIBRARY):
            md_files = [f for f in files if f.endswith('.md')]
            file_count = len(md_files)
            
            rel_path = Path(root).relative_to(FACTOR_LIBRARY)
            
            # 检查空目录
            if file_count == 0 and len(dirs) == 0:
                self.results['L1']['目录结构'].append({
                    'type': '空目录',
                    'path': str(rel_path),
                    'severity': 'P2'
                })
            
            # 检查稀疏目录
            elif file_count < 3 and file_count > 0:
                self.results['L1']['目录结构'].append({
                    'type': '稀疏目录',
                    'path': str(rel_path),
                    'file_count': file_count,
                    'severity': 'P2'
                })
        
        # 检查文件命名
        for doc in self.documents:
            file_name = Path(doc['path']).name
            
            # 检查旧架构命名
            if re.search(r'Layer\s*[0-8]', doc['body'], re.IGNORECASE):
                self.results['L1']['文件命名'].append({
                    'type': '旧架构命名残留',
                    'path': doc['path'],
                    'severity': 'P1'
                })
            
            # 检查特殊字符
            if re.search(r'[\u4e00-\u9fa5\s]', file_name):
                self.results['L1']['文件命名'].append({
                    'type': '特殊字符问题',
                    'path': doc['path'],
                    'severity': 'P2'
                })
        
        print(f"L1审计完成: 目录结构{len(self.results['L1']['目录结构'])}个, 文件命名{len(self.results['L1']['文件命名'])}个")
    
    def audit_L2_content(self):
        """L2文档内容层审计"""
        print("\nL2文档内容层审计...")
        
        for doc in self.documents:
            yaml_dict = doc['yaml']
            body = doc['body']
            
            # 检查职责驱动
            responsibility = yaml_dict.get('responsibility', [])
            if not responsibility:
                self.results['L2']['职责驱动'].append({
                    'type': '职责缺失',
                    'path': doc['path'],
                    'severity': 'P1'
                })
            elif isinstance(responsibility, list) and len(responsibility) == 1:
                if '文档支持' in str(responsibility[0]) and '相关' in str(responsibility[0]):
                    self.results['L2']['职责驱动'].append({
                        'type': '职责模糊',
                        'path': doc['path'],
                        'responsibility': responsibility,
                        'severity': 'P1'
                    })
            
            # 检查索引完备
            if 'INDEX.md' in doc['path']:
                # 检查索引是否列出所有文档
                parent_dir = Path(doc['path']).parent
                actual_files = list((FACTOR_LIBRARY / parent_dir).glob('*.md'))
                actual_files = [f.name for f in actual_files if f.name != 'INDEX.md']
                
                mentioned_files = re.findall(r'\[([^\]]+)\]\([^\)]*\.md\)', body)
                mentioned_files = [f + '.md' if not f.endswith('.md') else f for f in mentioned_files]
                
                missing_files = set(actual_files) - set(mentioned_files) - {'INDEX.md'}
                if missing_files:
                    self.results['L2']['索引完备'].append({
                        'type': '索引不完整',
                        'path': doc['path'],
                        'missing_files': list(missing_files),
                        'severity': 'P2'
                    })
            
            # 检查版本隔离
            if '变更记录' not in body and '变更历史' not in body:
                self.results['L2']['版本隔离'].append({
                    'type': '变更记录缺失',
                    'path': doc['path'],
                    'severity': 'P2'
                })
        
        print(f"L2审计完成: 职责驱动{len(self.results['L2']['职责驱动'])}个, 索引完备{len(self.results['L2']['索引完备'])}个, 版本隔离{len(self.results['L2']['版本隔离'])}个")
    
    def audit_L3_standards(self):
        """L3专业标准层审计"""
        print("\nL3专业标准层审计...")
        
        for doc in self.documents:
            yaml_dict = doc['yaml']
            
            # 检查YAML字段完整性
            required_fields = ['module_id', 'version', 'status', 'created_date', 'owner', 'responsibility']
            missing_fields = [f for f in required_fields if f not in yaml_dict or not yaml_dict.get(f)]
            
            if missing_fields:
                self.results['L3']['文档质量'].append({
                    'type': 'YAML字段缺失',
                    'path': doc['path'],
                    'missing_fields': missing_fields,
                    'severity': 'P1'
                })
            
            # 检查文档内容过少
            if doc['file_size'] < 200:
                self.results['L3']['文档质量'].append({
                    'type': '文档内容过少',
                    'path': doc['path'],
                    'file_size': doc['file_size'],
                    'severity': 'P2'
                })
        
        # 检查module_id重复
        for module_id, paths in self.module_ids.items():
            if len(paths) > 1:
                self.results['L3']['编号体系'].append({
                    'type': 'module_id重复',
                    'module_id': module_id,
                    'paths': paths,
                    'severity': 'P0'
                })
        
        print(f"L3审计完成: 文档质量{len(self.results['L3']['文档质量'])}个, 编号体系{len(self.results['L3']['编号体系'])}个")
    
    def check_duplicates(self):
        """检查重复内容"""
        print("\n检查重复内容...")
        
        for content_hash, paths in self.content_hashes.items():
            if len(paths) > 1:
                # 计算相似度
                self.results['重复内容'].append({
                    'type': '内容完全相同',
                    'paths': paths,
                    'count': len(paths),
                    'severity': 'P1'
                })
        
        print(f"重复内容检查完成: {len(self.results['重复内容'])}对")
    
    def check_responsibility_clarity(self):
        """检查职责清晰度"""
        print("\n检查职责清晰度...")
        
        for resp_str, paths in self.responsibilities.items():
            if len(paths) > 1 and resp_str:
                # 检查职责是否完全相同
                responsibilities = resp_str.split('|')
                if len(responsibilities) == 1 and '文档支持' in responsibilities[0]:
                    continue  # 跳过已经标记为模糊的职责
                
                if len(paths) > 3:  # 超过3个文档有相同职责
                    self.results['职责问题'].append({
                        'type': '职责完全相同',
                        'responsibility': responsibilities,
                        'paths': paths,
                        'count': len(paths),
                        'severity': 'P1'
                    })
        
        print(f"职责清晰度检查完成: {len(self.results['职责问题'])}对")
    
    def generate_report(self):
        """生成审计报告"""
        print("\n生成审计报告...")
        
        # 统计问题数量
        l1_count = sum(len(v) for v in self.results['L1'].values())
        l2_count = sum(len(v) for v in self.results['L2'].values())
        l3_count = sum(len(v) for v in self.results['L3'].values())
        total_count = l1_count + l2_count + l3_count + len(self.results['重复内容']) + len(self.results['职责问题'])
        
        # 按严重程度分类
        p0_count = sum(1 for category in self.results['L1'].values() for item in category if item.get('severity') == 'P0')
        p0_count += sum(1 for category in self.results['L2'].values() for item in category if item.get('severity') == 'P0')
        p0_count += sum(1 for category in self.results['L3'].values() for item in category if item.get('severity') == 'P0')
        p0_count += sum(1 for item in self.results['重复内容'] if item.get('severity') == 'P0')
        p0_count += sum(1 for item in self.results['职责问题'] if item.get('severity') == 'P0')
        
        p1_count = sum(1 for category in self.results['L1'].values() for item in category if item.get('severity') == 'P1')
        p1_count += sum(1 for category in self.results['L2'].values() for item in category if item.get('severity') == 'P1')
        p1_count += sum(1 for category in self.results['L3'].values() for item in category if item.get('severity') == 'P1')
        p1_count += sum(1 for item in self.results['重复内容'] if item.get('severity') == 'P1')
        p1_count += sum(1 for item in self.results['职责问题'] if item.get('severity') == 'P1')
        
        p2_count = sum(1 for category in self.results['L1'].values() for item in category if item.get('severity') == 'P2')
        p2_count += sum(1 for category in self.results['L2'].values() for item in category if item.get('severity') == 'P2')
        p2_count += sum(1 for category in self.results['L3'].values() for item in category if item.get('severity') == 'P2')
        p2_count += sum(1 for item in self.results['重复内容'] if item.get('severity') == 'P2')
        p2_count += sum(1 for item in self.results['职责问题'] if item.get('severity') == 'P2')
        
        report = f"""# Alpha因子层第三次全面深度审计报告（修复版）

## 审计概要

- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **审计范围**: D:\\ZephyrAlpha\\docs\\02_FACTOR_LIBRARY
- **审计方法**: 三层审计（L1-L3）+ 重复内容检查 + 职责清晰度检查
- **审计结论**: 发现{total_count}个问题，需要立即处理{p0_count}个P0级别问题

## 统计概览

| 统计项 | 数量 |
|--------|------|
| 总文档数 | {len(self.documents)} |
| 总问题数 | {total_count} |
| L1问题 | {l1_count} |
| L2问题 | {l2_count} |
| L3问题 | {l3_count} |
| 重复内容 | {len(self.results['重复内容'])} |
| 职责问题 | {len(self.results['职责问题'])} |

## 问题严重程度分布

| 级别 | 数量 | 说明 |
|------|------|------|
| P0（立即处理） | {p0_count} | 严重问题，影响系统完整性 |
| P1（短期改进） | {p1_count} | 重要问题，影响文档质量 |
| P2（长期优化） | {p2_count} | 次要问题，建议改进 |

## L1文件系统层审计结果

### 1.1 目录结构问题 ({len(self.results['L1']['目录结构'])}个)

"""
        
        for item in self.results['L1']['目录结构'][:20]:
            report += f"- **{item['type']}**: {item['path']}"
            if 'file_count' in item:
                report += f" (文件数: {item['file_count']})"
            report += f" [{item['severity']}]\n"
        
        if len(self.results['L1']['目录结构']) > 20:
            report += f"- ... 还有{len(self.results['L1']['目录结构']) - 20}个问题\n"
        
        report += f"""
### 1.2 文件命名问题 ({len(self.results['L1']['文件命名'])}个)

"""
        
        for item in self.results['L1']['文件命名'][:20]:
            report += f"- **{item['type']}**: {item['path']} [{item['severity']}]\n"
        
        if len(self.results['L1']['文件命名']) > 20:
            report += f"- ... 还有{len(self.results['L1']['文件命名']) - 20}个问题\n"
        
        report += f"""
## L2文档内容层审计结果

### 2.1 职责驱动问题 ({len(self.results['L2']['职责驱动'])}个)

"""
        
        for item in self.results['L2']['职责驱动'][:20]:
            report += f"- **{item['type']}**: {item['path']}"
            if 'responsibility' in item:
                report += f" (职责: {item['responsibility']})"
            report += f" [{item['severity']}]\n"
        
        if len(self.results['L2']['职责驱动']) > 20:
            report += f"- ... 还有{len(self.results['L2']['职责驱动']) - 20}个问题\n"
        
        report += f"""
### 2.2 索引完备问题 ({len(self.results['L2']['索引完备'])}个)

"""
        
        for item in self.results['L2']['索引完备'][:20]:
            report += f"- **{item['type']}**: {item['path']}"
            if 'missing_files' in item:
                report += f" (缺失: {', '.join(item['missing_files'][:3])}"
                if len(item['missing_files']) > 3:
                    report += f"等{len(item['missing_files'])}个文件"
                report += ")"
            report += f" [{item['severity']}]\n"
        
        if len(self.results['L2']['索引完备']) > 20:
            report += f"- ... 还有{len(self.results['L2']['索引完备']) - 20}个问题\n"
        
        report += f"""
### 2.3 版本隔离问题 ({len(self.results['L2']['版本隔离'])}个)

"""
        
        for item in self.results['L2']['版本隔离'][:20]:
            report += f"- **{item['type']}**: {item['path']} [{item['severity']}]\n"
        
        if len(self.results['L2']['版本隔离']) > 20:
            report += f"- ... 还有{len(self.results['L2']['版本隔离']) - 20}个问题\n"
        
        report += f"""
## L3专业标准层审计结果

### 3.1 编号体系问题 ({len(self.results['L3']['编号体系'])}个)

"""
        
        for item in self.results['L3']['编号体系'][:20]:
            report += f"- **{item['type']}**: {item['module_id']}\n"
            report += f"  - 涉及文件: {', '.join(item['paths'][:3])}"
            if len(item['paths']) > 3:
                report += f"等{len(item['paths'])}个文件"
            report += f" [{item['severity']}]\n"
        
        if len(self.results['L3']['编号体系']) > 20:
            report += f"- ... 还有{len(self.results['L3']['编号体系']) - 20}个问题\n"
        
        report += f"""
### 3.2 文档质量问题 ({len(self.results['L3']['文档质量'])}个)

"""
        
        for item in self.results['L3']['文档质量'][:20]:
            report += f"- **{item['type']}**: {item['path']}"
            if 'missing_fields' in item:
                report += f" (缺失字段: {', '.join(item['missing_fields'])})"
            if 'file_size' in item:
                report += f" (文件大小: {item['file_size']}字节)"
            report += f" [{item['severity']}]\n"
        
        if len(self.results['L3']['文档质量']) > 20:
            report += f"- ... 还有{len(self.results['L3']['文档质量']) - 20}个问题\n"
        
        report += f"""
## 重复内容检查结果 ({len(self.results['重复内容'])}对)

"""
        
        for item in self.results['重复内容'][:20]:
            report += f"- **{item['type']}** ({item['count']}个文件):\n"
            for path in item['paths'][:5]:
                report += f"  - {path}\n"
            if len(item['paths']) > 5:
                report += f"  - ... 还有{len(item['paths']) - 5}个文件\n"
        
        if len(self.results['重复内容']) > 20:
            report += f"- ... 还有{len(self.results['重复内容']) - 20}对重复内容\n"
        
        report += f"""
## 职责清晰度检查结果 ({len(self.results['职责问题'])}对)

"""
        
        for item in self.results['职责问题'][:20]:
            report += f"- **{item['type']}** (职责: {', '.join(item['responsibility'][:3])}):\n"
            for path in item['paths'][:5]:
                report += f"  - {path}\n"
            if len(item['paths']) > 5:
                report += f"  - ... 还有{len(item['paths']) - 5}个文件\n"
        
        if len(self.results['职责问题']) > 20:
            report += f"- ... 还有{len(self.results['职责问题']) - 20}对职责问题\n"
        
        report += f"""
## 改进建议

### 立即行动 (P0级别)
"""
        
        if p0_count == 0:
            report += "- ✅ 无P0级别问题\n"
        else:
            report += f"- 处理{p0_count}个P0级别问题\n"
        
        report += f"""
### 短期改进 (P1级别)
- 处理{p1_count}个P1级别问题
- 修复职责模糊的文档
- 解决重复内容问题

### 长期优化 (P2级别)
- 处理{p2_count}个P2级别问题
- 整合稀疏目录
- 补充变更记录

---

## Git备份

- **备份标签**: v3.4-pre-third-comprehensive-audit
- **备份时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **可恢复**: 是

---

**审计完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = Path(rf'D:\ZephyrAlpha\docs\09_AUDIT\STATE\THIRD_COMPREHENSIVE_AUDIT_REPORT_FIXED_{timestamp}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存JSON数据
        json_path = Path(rf'D:\ZephyrAlpha\docs\09_AUDIT\STATE\THIRD_COMPREHENSIVE_AUDIT_REPORT_FIXED_{timestamp}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已生成: {report_path}")
        print(f"JSON数据: {json_path}")
    
    def run(self):
        """运行审计"""
        print("=" * 80)
        print("Alpha因子层第三次全面深度审计（修复版）")
        print("=" * 80)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.scan_documents()
        self.audit_L1_filesystem()
        self.audit_L2_content()
        self.audit_L3_standards()
        self.check_duplicates()
        self.check_responsibility_clarity()
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("审计完成")
        print("=" * 80)

if __name__ == '__main__':
    auditor = ThirdComprehensiveAuditorFixed()
    auditor.run()
