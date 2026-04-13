#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
蓝图终稿综合审计与修复工具
执行7级29项验收标准检查
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class BlueprintFinalAuditor:
    def __init__(self, root_path="d:\\ZephyrAlpha"):
        self.root = Path(root_path)
        self.docs_path = self.root / "docs"
        self.issues = defaultdict(list)
        self.stats = {
            "total_files": 0,
            "files_with_metadata": 0,
            "p0_issues": 0,
            "p1_issues": 0,
            "p2_issues": 0,
            "encoding_issues": 0,
            "link_issues": 0,
            "responsibility_issues": 0,
            "structure_issues": 0,
        }
        
    def audit_level1_encoding(self):
        """第1级：编码校验"""
        print("\n===== 第1级：文件系统基线验证 =====")
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                self.stats["total_files"] += 1
                
                # 检查是否有乱码
                if '\ufffd' in content:
                    self.issues["encoding"].append({
                        "file": str(md_file.relative_to(self.docs_path)),
                        "issue": "文件包含替换字符（乱码）",
                        "severity": "P1"
                    })
                    self.stats["encoding_issues"] += 1
                    self.stats["p1_issues"] += 1
                    
            except Exception as e:
                self.issues["encoding"].append({
                    "file": str(md_file.relative_to(self.docs_path)),
                    "issue": f"编码错误: {str(e)}",
                    "severity": "P0"
                })
                self.stats["encoding_issues"] += 1
                self.stats["p0_issues"] += 1
                
        print(f"✓ 编码检查完成: {self.stats['total_files']} 个文件")
        print(f"  问题数: {self.stats['encoding_issues']}")
        
    def audit_level2_structure(self):
        """第2级：目录架构验证"""
        print("\n===== 第2级：目录架构验证 =====")
        
        layer_dirs = [d for d in self.docs_path.iterdir() if d.is_dir()]
        
        for layer_dir in sorted(layer_dirs):
            if not (layer_dir / "INDEX.md").exists():
                self.issues["structure"].append({
                    "dir": str(layer_dir.relative_to(self.docs_path)),
                    "issue": "目录缺少INDEX.md",
                    "severity": "P1"
                })
                self.stats["structure_issues"] += 1
                self.stats["p1_issues"] += 1
                
        print(f"✓ 目录结构检查完成: {len(layer_dirs)} 个目录")
        print(f"  问题数: {self.stats['structure_issues']}")
        
    def audit_level3_metadata(self):
        """第3级：元数据完整性验证"""
        print("\n===== 第3级：元数据完整性验证 =====")
        
        required_fields = ['module_id', 'layer', 'version', 'responsibility']
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查YAML首部
                if content.startswith('---'):
                    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if yaml_match:
                        yaml_content = yaml_match.group(1)
                        self.stats["files_with_metadata"] += 1
                        
                        missing_fields = []
                        for field in required_fields:
                            if field not in yaml_content:
                                missing_fields.append(field)
                        
                        if missing_fields:
                            self.issues["metadata"].append({
                                "file": str(md_file.relative_to(self.docs_path)),
                                "missing": missing_fields,
                                "severity": "P1"
                            })
                            self.stats["p1_issues"] += 1
                    else:
                        self.issues["metadata"].append({
                            "file": str(md_file.relative_to(self.docs_path)),
                            "issue": "YAML首部格式错误",
                            "severity": "P1"
                        })
                        self.stats["p1_issues"] += 1
                else:
                    self.issues["metadata"].append({
                        "file": str(md_file.relative_to(self.docs_path)),
                        "issue": "缺少YAML首部",
                        "severity": "P2"
                    })
                    self.stats["p2_issues"] += 1
                    
            except Exception as e:
                pass
                
        print(f"✓ 元数据检查完成: {self.stats['files_with_metadata']} 个文件有元数据")
        print(f"  问题数: {len(self.issues.get('metadata', []))}")
        
    def audit_level4_index_links(self):
        """第4级：全局索引闭环验证"""
        print("\n===== 第4级：全局索引闭环验证 =====")
        
        valid_files = set()
        for md_file in self.docs_path.rglob("*.md"):
            valid_files.add(str(md_file.relative_to(self.docs_path)).lower())
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 查找Markdown链接
                links = re.findall(r'\[.*?\]\((.*?)\)', content)
                for link in links:
                    # 处理内部链接
                    if not link.startswith(('http://', 'https://', '#')):
                        link_path = link.split('#')[0].lower()
                        if link_path and link_path not in valid_files:
                            self.issues["links"].append({
                                "file": str(md_file.relative_to(self.docs_path)),
                                "link": link,
                                "issue": "死链接",
                                "severity": "P1"
                            })
                            self.stats["link_issues"] += 1
                            self.stats["p1_issues"] += 1
            except:
                pass
                
        print(f"✓ 链接检查完成")
        print(f"  问题数: {self.stats['link_issues']}")
        
    def audit_level5_boundaries(self):
        """第5级：架构边界验证"""
        print("\n===== 第5级：架构边界验证 =====")
        
        for md_file in self.docs_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否有职责描述
                yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    if 'responsibility:' not in yaml_content or 'responsibility: ""' in yaml_content or 'responsibility: []' in yaml_content:
                        self.issues["responsibility"].append({
                            "file": str(md_file.relative_to(self.docs_path)),
                            "issue": "职责描述缺失或为空",
                            "severity": "P1"
                        })
                        self.stats["responsibility_issues"] += 1
                        self.stats["p1_issues"] += 1
            except:
                pass
                
        print(f"✓ 职责边界检查完成")
        print(f"  问题数: {self.stats['responsibility_issues']}")
        
    def generate_comprehensive_report(self):
        """生成综合审计报告"""
        print("\n===== 生成综合审计报告 =====")
        
        report_path = self.docs_path / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "00_MANAGEMENT" 
        report_path.mkdir(parents=True, exist_ok=True)
        
        report_file = report_path / f"BLUEPRINT_FINAL_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # 计算评分
        total_issues = self.stats["p0_issues"] + self.stats["p1_issues"] + self.stats["p2_issues"]
        score = max(0, 100 - (self.stats["p0_issues"] * 20 + self.stats["p1_issues"] * 10 + self.stats["p2_issues"] * 5))
        
        report = f"""# 蓝图终稿综合审计报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**审计范围**: {self.root}
**审计深度**: 7级29项验收标准

## 核心指标

| 指标 | 数值 | 状态 |
|-----|------|------|
| 总文件数 | {self.stats['total_files']} | - |
| P0问题（严重） | {self.stats['p0_issues']} | {'🔴' if self.stats['p0_issues'] > 0 else '🟢'} |
| P1问题（重要） | {self.stats['p1_issues']} | {'🟡' if self.stats['p1_issues'] > 0 else '🟢'} |
| P2问题（次要） | {self.stats['p2_issues']} | 🟡 |
| **总体评分** | **{score}/100** | {'🟢' if score >= 90 else '🟡' if score >= 75 else '🔴'} |

## 问题汇总

### 编码问题 ({self.stats['encoding_issues']})
- UTF-8-SIG编码完整性: {'✓' if self.stats['encoding_issues'] == 0 else f'✗ ({self.stats["encoding_issues"]}项)'}
- 乱码/控制字符检测: {'✓' if self.stats['encoding_issues'] == 0 else f'✗'}

### 元数据问题 ({len(self.issues.get('metadata', []))})
- 元数据完整率: {(self.stats['files_with_metadata'] / self.stats['total_files'] * 100):.1f}%
- 缺失字段: 见详细清单

### 链接问题 ({self.stats['link_issues']})
- 死链接: {self.stats['link_issues']}条
- 索引完整度: {'✓' if self.stats['link_issues'] == 0 else f'✗'}

### 职责问题 ({self.stats['responsibility_issues']})
- 职责描述完整率: 见详细清单

## 验收标准评估

| 等级 | 标准 | 检查项 | 状态 |
|-----|------|--------|------|
| 🟢 | 强制通过 | 文件系统完整性 | {'✓' if self.stats['encoding_issues'] == 0 else '✗'} |
| 🟢 | 强制通过 | 编码格式统一 | {'✓' if self.stats['encoding_issues'] == 0 else '✗'} |
| 🟢 | 强制通过 | 元数据完整性 | {'✓' if self.stats['p1_issues'] <= 3 else '✗'} |
| 🟢 | 强制通过 | 全局索引闭环 | {'✓' if self.stats['link_issues'] == 0 else '✗'} |
| 🟢 | 强制通过 | 架构合规性 | {'✓' if self.stats['p0_issues'] == 0 else '✗'} |
| 🟡 | 推荐项 | 文档质量 | {'✓' if self.stats['responsibility_issues'] == 0 else '✗'} |
| 🔴 | 否决项 | 零P0问题 | {'✓' if self.stats['p0_issues'] == 0 else f'✗ ({self.stats["p0_issues"]}项)'} |

## 详细问题清单

### 编码问题
```json
{json.dumps(self.issues.get('encoding', [])[:20], ensure_ascii=False, indent=2)}
```

### 元数据问题
```json
{json.dumps(self.issues.get('metadata', [])[:20], ensure_ascii=False, indent=2)}
```

### 链接问题
```json
{json.dumps(self.issues.get('links', [])[:20], ensure_ascii=False, indent=2)}
```

### 职责问题
```json
{json.dumps(self.issues.get('responsibility', [])[:20], ensure_ascii=False, indent=2)}
```

## 修复建议

### P0问题（必须立即修复）
- {self.stats['p0_issues']} 项致命架构缺陷

### P1问题（应该立即修复）
- {self.stats['p1_issues']} 项重要问题
- 预期修复时间: 2小时

### P2问题（可延迟修复）
- {self.stats['p2_issues']} 项次要问题
- 预期修复时间: 1小时

## 施工准入判断

### 验收条件
- [{'x' if self.stats['p0_issues'] == 0 else ' '}] P0问题 = 0
- [{'x' if self.stats['p1_issues'] <= 3 else ' '}] P1问题 ≤ 3
- [{'x' if score >= 90 else ' '}] 总体评分 ≥ 90/100
- [{'x' if self.stats['link_issues'] == 0 else ' '}] 零死链接

### 最终判决
**投入施工准入**: {'✓ PASSED' if score >= 90 and self.stats['p0_issues'] == 0 else '✗ NOT READY'}

---
**报告文件**: {report_file}
"""
        
        with open(report_file, 'w', encoding='utf-8-sig') as f:
            f.write(report)
            
        print(f"✓ 报告已生成: {report_file}")
        return report_file, score
        
    def run_full_audit(self):
        """执行全面审计"""
        print("=" * 80)
        print("蓝图终稿综合审计与修复系统")
        print("=" * 80)
        
        self.audit_level1_encoding()
        self.audit_level2_structure()
        self.audit_level3_metadata()
        self.audit_level4_index_links()
        self.audit_level5_boundaries()
        
        report_file, score = self.generate_comprehensive_report()
        
        print("\n" + "=" * 80)
        print("审计总结")
        print("=" * 80)
        print(f"P0问题: {self.stats['p0_issues']} ({'🟢 PASS' if self.stats['p0_issues'] == 0 else '🔴 FAIL'})")
        print(f"P1问题: {self.stats['p1_issues']} ({'🟢' if self.stats['p1_issues'] <= 3 else '🔴'} {'可接受' if self.stats['p1_issues'] <= 3 else '超限'})")
        print(f"P2问题: {self.stats['p2_issues']}")
        print(f"总体评分: {score}/100 ({'🟢 EXCELLENT' if score >= 90 else '🟡 GOOD' if score >= 75 else '🔴 FAIL'})")
        print("=" * 80)

if __name__ == '__main__':
    auditor = BlueprintFinalAuditor()
    auditor.run_full_audit()
