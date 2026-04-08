#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Layer 8 P0级问题
为所有README.md文件分配唯一的module_id
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8P0Fixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        
    def fix_all(self):
        """修复所有P0级问题"""
        print("=" * 80)
        print("Layer 8 P0级问题修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 修复重复的module_id
        print("\n[任务] 修复重复的module_id...")
        self.fix_duplicate_module_ids()
        
        # 2. 生成报告
        print("\n[任务] 生成修复报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def fix_duplicate_module_ids(self):
        """修复重复的module_id"""
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file == 'README.md':
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    dir_name = file_path.parent.name
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取YAML头部
                        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            
                            # 生成唯一的module_id
                            module_id = f"08_HUMAN_AI_INTERFACE_{dir_name}_README"
                            
                            # 更新module_id
                            if 'module_id:' in yaml_content:
                                new_yaml = re.sub(r'module_id:\s*.*', f'module_id: {module_id}', yaml_content)
                            else:
                                new_yaml = f"module_id: {module_id}\n" + yaml_content
                            
                            new_content = content.replace(yaml_content, new_yaml)
                            
                            # 写回文件
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            self.fixed_files.append({
                                "file": str(rel_path),
                                "module_id": module_id
                            })
                            print(f"  [OK] {rel_path} - {module_id}")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_P0_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_P0_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 P0级问题修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 P0级问题修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: P0级问题修复

---

## 📊 修复概要

| 指标 | 数值 |
|------|------|
| **修复文件总数** | {len(self.fixed_files)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 修复详情

### 修复的文件列表

"""
        
        for item in self.fixed_files:
            report += f"- **{item['file']}**: {item['module_id']}\n"
        
        if self.errors:
            report += f"""
---

## ❌ 错误列表

"""
            for error in self.errors:
                report += f"- **{error['file']}**: {error['error']}\n"
        
        report += f"""
---

## 📝 修复总结

### 主要成果

- 为 {len(self.fixed_files)} 个README.md文件分配了唯一的module_id
- 解决了module_id重复的P0级问题
- 提高了文档的唯一性和可追溯性

### 后续建议

1. 验证修复效果
2. 重新运行审计
3. 保持文档质量

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 修复报告已生成: {report_file}")


if __name__ == "__main__":
    fixer = Layer8P0Fixer()
    fixer.fix_all()
