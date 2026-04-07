#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复YAML头部问题
移除旧的YAML头部，只保留最新的一个
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class DuplicateYAMLFixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        
    def fix_all(self):
        """修复所有重复YAML头部"""
        print("=" * 80)
        print("修复重复YAML头部")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找所有YAML块
                        yaml_pattern = r'^---\s*\n(.*?)\n---'
                        yaml_blocks = list(re.finditer(yaml_pattern, content, re.DOTALL))
                        
                        if len(yaml_blocks) > 1:
                            # 保留最后一个YAML块
                            last_yaml = yaml_blocks[-1]
                            
                            # 移除之前的所有YAML块
                            new_content = content
                            for match in reversed(yaml_blocks[:-1]):
                                # 移除整个YAML块（包括---标记）
                                start = match.start()
                                end = match.end()
                                new_content = new_content[:start] + new_content[end:]
                            
                            # 清理多余的空行
                            new_content = re.sub(r'\n{3,}', '\n\n', new_content)
                            
                            # 写回文件
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            self.fixed_files.append(str(rel_path))
                            print(f"  [OK] {rel_path} - 移除了 {len(yaml_blocks) - 1} 个重复YAML")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"DUPLICATE_YAML_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: DUPLICATE_YAML_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - 重复YAML头部修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# 重复YAML头部修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: 移除重复YAML头部

---

## 📊 修复概要

| 指标 | 数值 |
|------|------|
| **修复文件总数** | {len(self.fixed_files)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 修复文件列表

"""
        
        for file in self.fixed_files[:20]:
            report += f"- {file}\n"
        
        if len(self.fixed_files) > 20:
            report += f"\n*还有 {len(self.fixed_files) - 20} 个文件*\n"
        
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

- 移除了 {len(self.fixed_files)} 个文件中的重复YAML头部
- 保留了最新的YAML元数据
- 清理了多余的空行

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
    fixer = DuplicateYAMLFixer()
    fixer.fix_all()
