#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 8人机交互层深度审计脚本
审计范围：所有文档文件的每一个内容
重点检查：重复内容、职责不清的内容
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import json

BASE_DIR = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")

class Layer8DeepAuditor:
    def __init__(self):
        self.files = []
        self.yaml_headers = {}
        self.responsibilities = {}
        self.module_ids = {}
        self.content_hashes = {}
        self.duplicates = defaultdict(list)
        self.issues = {
            'L1': [],  # 文件系统层问题
            'L2': [],  # 文档内容层问题
            'L3': []   # 专业标准层问题
        }
        
    def scan_all_files(self):
        """扫描所有.md文件"""
        print("=" * 80)
        print("第一步：扫描所有文档文件")
        print("=" * 80)
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    self.files.append({
                        'path': str(file_path),
                        'rel_path': str(rel_path),
                        'name': file,
                        'dir': file_path.parent.name
                    })
        
        print(f"✅ 扫描完成：共发现 {len(self.files)} 个文档文件")
        return len(self.files)
    
    def extract_yaml_header(self, file_path: str) -> dict:
        """提取YAML头部"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1].strip()
                    return yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"⚠️  解析YAML失败: {file_path} - {e}")
        return {}
    
    def check_yaml_headers(self):
        """检查所有文件的YAML头部"""
        print("\n" + "=" * 80)
        print("第二步：检查YAML头部")
        print("=" * 80)
        
        required_fields = ['module_id', 'version', 'status', 'owner', 'responsibility']
        
        for file_info in self.files:
            yaml_header = self.extract_yaml_header(file_info['path'])
            self.yaml_headers[file_info['path']] = yaml_header
            
            # 检查必需字段
            missing_fields = [f for f in required_fields if f not in yaml_header]
            if missing_fields:
                self.issues['L3'].append({
                    'type': 'YAML字段缺失',
                    'file': file_info['rel_path'],
                    'details': f"缺少字段: {', '.join(missing_fields)}",
                    'severity': 'P1'
                })
            
            # 检查module_id重复
            if 'module_id' in yaml_header:
                module_id = yaml_header['module_id']
                if module_id in self.module_ids:
                    self.issues['L2'].append({
                        'type': 'module_id重复',
                        'file': file_info['rel_path'],
                        'details': f"module_id '{module_id}' 与 {self.module_ids[module_id]} 重复",
                        'severity': 'P0'
                    })
                else:
                    self.module_ids[module_id] = file_info['rel_path']
            
            # 收集职责信息
            if 'responsibility' in yaml_header:
                resp = yaml_header['responsibility']
                if isinstance(resp, list):
                    resp_str = ' '.join(resp)
                else:
                    resp_str = str(resp)
                self.responsibilities[file_info['path']] = resp_str
        
        print(f"✅ YAML检查完成：发现 {len([i for i in self.issues['L3'] if i['type'] == 'YAML字段缺失'])} 个字段缺失问题")
        print(f"✅ module_id检查完成：发现 {len([i for i in self.issues['L2'] if i['type'] == 'module_id重复'])} 个重复问题")
    
    def check_file_naming(self):
        """检查文件命名规范"""
        print("\n" + "=" * 80)
        print("第三步：检查文件命名规范")
        print("=" * 80)
        
        naming_issues = []
        
        for file_info in self.files:
            file_name = file_info['name']
            
            # 检查BLUEPRINT文件命名
            if 'BLUEPRINT' in file_name:
                # 应该符合: MODULE_NAME_BLUEPRINT.md
                if not file_name.endswith('_BLUEPRINT.md'):
                    naming_issues.append({
                        'file': file_info['rel_path'],
                        'issue': 'BLUEPRINT文件命名不规范',
                        'expected': '应以_BLUEPRINT.md结尾'
                    })
            
            # 检查INDEX文件
            if file_name == 'INDEX.md' or file_name == 'index.md':
                # INDEX文件应该在每个模块目录下
                pass
            
            # 检查README文件
            if file_name == 'README.md':
                # README文件应该在每个模块目录下
                pass
            
            # 检查特殊字符
            if ' ' in file_name:
                naming_issues.append({
                    'file': file_info['rel_path'],
                    'issue': '文件名包含空格',
                    'expected': '应使用下划线或连字符'
                })
        
        if naming_issues:
            for issue in naming_issues:
                self.issues['L1'].append({
                    'type': '文件命名不规范',
                    'file': issue['file'],
                    'details': issue['issue'],
                    'severity': 'P2'
                })
        
        print(f"✅ 命名检查完成：发现 {len(naming_issues)} 个命名问题")
    
    def check_directory_structure(self):
        """检查目录结构"""
        print("\n" + "=" * 80)
        print("第四步：检查目录结构")
        print("=" * 80)
        
        # 检查每个模块目录
        module_dirs = set()
        for file_info in self.files:
            module_dirs.add(file_info['dir'])
        
        # 检查目录命名
        for dir_name in module_dirs:
            # 模块目录应该以数字开头
            if not re.match(r'^\d{2}_', dir_name) and dir_name != '08_HUMAN_AI_INTERFACE':
                self.issues['L1'].append({
                    'type': '目录命名不规范',
                    'file': dir_name,
                    'details': '模块目录应以两位数字开头',
                    'severity': 'P2'
                })
        
        print(f"✅ 目录结构检查完成：发现 {len([i for i in self.issues['L1'] if i['type'] == '目录命名不规范'])} 个问题")
    
    def check_responsibilities(self):
        """检查职责清晰度"""
        print("\n" + "=" * 80)
        print("第五步：检查职责清晰度")
        print("=" * 80)
        
        # 检查职责描述是否清晰
        for file_path, resp in self.responsibilities.items():
            # 职责描述应该具体明确
            if len(resp) < 10:
                self.issues['L2'].append({
                    'type': '职责描述过于简短',
                    'file': str(Path(file_path).relative_to(BASE_DIR)),
                    'details': f"职责描述: {resp}",
                    'severity': 'P2'
                })
            
            # 检查职责是否包含关键词
            keywords = ['管理', '监控', '分析', '配置', '优化', '审计', '报告', '控制']
            if not any(kw in resp for kw in keywords):
                self.issues['L2'].append({
                    'type': '职责描述不够具体',
                    'file': str(Path(file_path).relative_to(BASE_DIR)),
                    'details': f"职责描述: {resp}",
                    'severity': 'P2'
                })
        
        print(f"✅ 职责检查完成：发现 {len([i for i in self.issues['L2'] if '职责' in i['type']])} 个问题")
    
    def check_duplicates(self):
        """检查重复内容"""
        print("\n" + "=" * 80)
        print("第六步：检查重复内容")
        print("=" * 80)
        
        # 读取所有文件内容
        file_contents = {}
        for file_info in self.files:
            try:
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_contents[file_info['path']] = content
            except Exception as e:
                print(f"⚠️  读取文件失败: {file_info['path']} - {e}")
        
        # 检查内容相似度
        checked_pairs = set()
        for path1, content1 in file_contents.items():
            for path2, content2 in file_contents.items():
                if path1 >= path2:
                    continue
                
                pair_key = (Path(path1).name, Path(path2).name)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                # 计算相似度
                similarity = self.calculate_similarity(content1, content2)
                
                if similarity > 0.8:  # 80%以上相似度
                    self.issues['L2'].append({
                        'type': '内容高度相似',
                        'file': str(Path(path1).relative_to(BASE_DIR)),
                        'details': f"与 {Path(path2).relative_to(BASE_DIR)} 相似度 {similarity:.1%}",
                        'severity': 'P0'
                    })
        
        print(f"✅ 重复检查完成：发现 {len([i for i in self.issues['L2'] if i['type'] == '内容高度相似'])} 个问题")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的相似度计算：基于共同行数
        lines1 = set(text1.split('\n'))
        lines2 = set(text2.split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        common_lines = lines1 & lines2
        similarity = len(common_lines) / max(len(lines1), len(lines2))
        return similarity
    
    def check_index_completeness(self):
        """检查索引完备性"""
        print("\n" + "=" * 80)
        print("第七步：检查索引完备性")
        print("=" * 80)
        
        # 检查主索引文件
        main_index = BASE_DIR / "index.md"
        if not main_index.exists():
            self.issues['L2'].append({
                'type': '缺少主索引文件',
                'file': 'index.md',
                'details': '根目录缺少index.md主入口',
                'severity': 'P0'
            })
        else:
            # 检查主索引是否包含所有模块
            with open(main_index, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            # 检查BLUEPRINT文件是否被索引
            blueprint_files = [f for f in self.files if 'BLUEPRINT' in f['name']]
            for bp_file in blueprint_files:
                if bp_file['name'].replace('.md', '') not in index_content:
                    self.issues['L2'].append({
                        'type': '索引不完整',
                        'file': bp_file['rel_path'],
                        'details': 'BLUEPRINT文件未被主索引包含',
                        'severity': 'P1'
                    })
        
        # 检查每个模块目录是否有INDEX.md
        module_dirs = set()
        for file_info in self.files:
            if file_info['dir'] != '08_HUMAN_AI_INTERFACE':
                module_dirs.add(file_info['dir'])
        
        for dir_name in module_dirs:
            index_file = BASE_DIR / dir_name / "INDEX.md"
            if not index_file.exists():
                # 检查是否有index.md（小写）
                index_file_lower = BASE_DIR / dir_name / "index.md"
                if not index_file_lower.exists():
                    self.issues['L2'].append({
                        'type': '模块缺少索引文件',
                        'file': f"{dir_name}/INDEX.md",
                        'details': '模块目录缺少INDEX.md导航文件',
                        'severity': 'P2'
                    })
        
        print(f"✅ 索引检查完成：发现 {len([i for i in self.issues['L2'] if '索引' in i['type']])} 个问题")
    
    def generate_report(self):
        """生成审计报告"""
        print("\n" + "=" * 80)
        print("生成审计报告")
        print("=" * 80)
        
        # 统计问题数量
        l1_count = len(self.issues['L1'])
        l2_count = len(self.issues['L2'])
        l3_count = len(self.issues['L3'])
        total_count = l1_count + l2_count + l3_count
        
        # 按严重程度分类
        p0_count = len([i for layer in self.issues.values() for i in layer if i['severity'] == 'P0'])
        p1_count = len([i for layer in self.issues.values() for i in layer if i['severity'] == 'P1'])
        p2_count = len([i for layer in self.issues.values() for i in layer if i['severity'] == 'P2'])
        
        report = f"""
# Layer 8人机交互层深度审计报告

**审计时间**: 2026-04-08
**审计范围**: 所有文档文件的每一个内容
**审计方法**: 三层审计标准（L1-L3）

---

## 📊 审计统计

| 指标 | 数值 |
|------|------|
| **审计文件总数** | {len(self.files)} |
| **发现问题总数** | {total_count} |
| **L1文件系统层问题** | {l1_count} |
| **L2文档内容层问题** | {l2_count} |
| **L3专业标准层问题** | {l3_count} |

### 问题严重程度分布

| 级别 | 数量 | 说明 |
|------|------|------|
| **P0（严重）** | {p0_count} | 需立即修复 |
| **P1（重要）** | {p1_count} | 需尽快修复 |
| **P2（一般）** | {p2_count} | 可选优化 |

---

## 🔴 L1 文件系统层问题（{l1_count}个）

"""
        
        if self.issues['L1']:
            for i, issue in enumerate(self.issues['L1'], 1):
                report += f"""
### 问题{i}: {issue['type']} [{issue['severity']}]

- **文件**: `{issue['file']}`
- **详情**: {issue['details']}

"""
        else:
            report += "\n✅ 未发现L1层问题\n"
        
        report += f"""
---

## 🟡 L2 文档内容层问题（{l2_count}个）

"""
        
        if self.issues['L2']:
            for i, issue in enumerate(self.issues['L2'], 1):
                report += f"""
### 问题{i}: {issue['type']} [{issue['severity']}]

- **文件**: `{issue['file']}`
- **详情**: {issue['details']}

"""
        else:
            report += "\n✅ 未发现L2层问题\n"
        
        report += f"""
---

## 🟢 L3 专业标准层问题（{l3_count}个）

"""
        
        if self.issues['L3']:
            for i, issue in enumerate(self.issues['L3'], 1):
                report += f"""
### 问题{i}: {issue['type']} [{issue['severity']}]

- **文件**: `{issue['file']}`
- **详情**: {issue['details']}

"""
        else:
            report += "\n✅ 未发现L3层问题\n"
        
        report += f"""
---

## 📋 审计结论

### 总体评估

- **文件系统层**: {'✅ 符合标准' if l1_count == 0 else f'⚠️ 发现{l1_count}个问题'}
- **文档内容层**: {'✅ 符合标准' if l2_count == 0 else f'⚠️ 发现{l2_count}个问题'}
- **专业标准层**: {'✅ 符合标准' if l3_count == 0 else f'⚠️ 发现{l3_count}个问题'}

### 优先修复建议

"""
        
        # 列出P0级问题
        p0_issues = [i for layer in self.issues.values() for i in layer if i['severity'] == 'P0']
        if p0_issues:
            report += "#### P0级问题（需立即修复）\n\n"
            for i, issue in enumerate(p0_issues, 1):
                report += f"{i}. **{issue['type']}**: {issue['file']}\n"
        else:
            report += "✅ 无P0级问题\n"
        
        report += """
---

**报告生成时间**: 2026-04-08
**审计工具**: Layer8DeepAuditor v1.0.0
"""
        
        # 保存报告
        report_path = BASE_DIR.parent.parent / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state" / "LAYER8_DEEP_AUDIT_REPORT_20260408.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 审计报告已生成: {report_path}")
        print(f"\n📊 审计总结:")
        print(f"   - 审计文件: {len(self.files)}个")
        print(f"   - 发现问题: {total_count}个")
        print(f"   - P0级: {p0_count}个")
        print(f"   - P1级: {p1_count}个")
        print(f"   - P2级: {p2_count}个")
        
        return report

def main():
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Layer 8人机交互层深度审计系统" + " " * 20 + "║")
    print("╚" + "═" * 78 + "╝")
    
    auditor = Layer8DeepAuditor()
    
    # 执行审计
    auditor.scan_all_files()
    auditor.check_yaml_headers()
    auditor.check_file_naming()
    auditor.check_directory_structure()
    auditor.check_responsibilities()
    auditor.check_duplicates()
    auditor.check_index_completeness()
    
    # 生成报告
    auditor.generate_report()
    
    print("\n" + "=" * 80)
    print("审计完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
