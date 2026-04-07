#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完善Layer 8主索引
添加所有活跃文档到主索引
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8IndexCompleter:
    def __init__(self):
        self.added_files = []
        self.errors = []
        
    def complete_index(self):
        """完善主索引"""
        print("=" * 80)
        print("Layer 8 主索引完善")
        print("=" * 80)
        print(f"完善时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描所有蓝图文档
        print("\n[阶段1] 扫描所有蓝图文档...")
        blueprint_files = self.scan_blueprint_files()
        
        # 2. 更新主索引
        print("\n[阶段2] 更新主索引...")
        self.update_main_index(blueprint_files)
        
        # 3. 生成报告
        print("\n[阶段3] 生成完善报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("完善完成！")
        print(f"添加文件数: {len(self.added_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def scan_blueprint_files(self):
        """扫描所有蓝图文档"""
        blueprint_files = []
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('_BLUEPRINT.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    dir_name = file_path.parent.name
                    
                    blueprint_files.append({
                        "name": file.replace('_BLUEPRINT.md', ''),
                        "path": str(rel_path).replace('\\', '/'),
                        "dir": dir_name
                    })
        
        print(f"  扫描到 {len(blueprint_files)} 个蓝图文档")
        return blueprint_files
    
    def update_main_index(self, blueprint_files):
        """更新主索引"""
        index_file = BASE_DIR / "index.md"
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找"其他活跃文档"部分
            other_docs_match = re.search(r'## 📁 其他活跃文档\n\n(.*?)(?=\n---|\n## |$)', content, re.DOTALL)
            
            if other_docs_match:
                # 构建新的文档列表
                new_doc_list = "\n"
                for bp in sorted(blueprint_files, key=lambda x: x['dir']):
                    link = f"- [{bp['name']}_BLUEPRINT]({bp['path']})\n"
                    new_doc_list += link
                    
                    # 检查是否是新添加的
                    if link not in content:
                        self.added_files.append(bp['path'])
                
                # 替换文档列表
                new_content = content[:other_docs_match.start(1)] + new_doc_list + content[other_docs_match.end(1):]
                
                # 写回文件
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"  [OK] 主索引已更新，添加了 {len(self.added_files)} 个文档链接")
            else:
                print("  [警告] 未找到'其他活跃文档'部分")
                
        except Exception as e:
            self.errors.append({
                "file": "index.md",
                "error": str(e)
            })
            print(f"  [错误] index.md - {e}")
    
    def generate_report(self):
        """生成完善报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_INDEX_COMPLETION_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_INDEX_COMPLETION_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 主索引完善报告
standard_type: 完善报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 主索引完善报告

**完善时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**完善范围**: Layer 8 人机交互层  
**完善类型**: 主索引完善

---

## 📊 完善概要

| 指标 | 数值 |
|------|------|
| **添加文件总数** | {len(self.added_files)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 完善详情

### 添加的文档链接

"""
        
        for file in self.added_files[:20]:
            report += f"- {file}\n"
        
        if len(self.added_files) > 20:
            report += f"\n*还有 {len(self.added_files) - 20} 个文件*\n"
        
        if self.errors:
            report += f"""
---

## ❌ 错误列表

"""
            for error in self.errors:
                report += f"- **{error['file']}**: {error['error']}\n"
        
        report += f"""
---

## 📝 完善总结

### 主要成果

- 添加了 {len(self.added_files)} 个文档链接到主索引
- 提高了索引的完备性
- 符合专业量化机构索引完备性原则

### 后续建议

1. 验证索引链接
2. 重新运行审计
3. 保持索引更新

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**完善执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 完善报告已生成: {report_file}")


if __name__ == "__main__":
    completer = Layer8IndexCompleter()
    completer.complete_index()
