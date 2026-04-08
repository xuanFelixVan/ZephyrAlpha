#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 9研究与创新层职责字段修复脚本
自动为缺少responsibility字段的文档添加正确的职责定义
"""

import os
import re
from pathlib import Path
from datetime import datetime

class Layer9ResponsibilityFixer:
    """Layer 9职责字段修复器"""
    
    def __init__(self):
        self.layer9_path = Path("docs/09_RESEARCH_INNOVATION")
        self.fix_count = 0
        self.fix_log = []
        
        # 职责映射表
        self.responsibility_map = {
            "BLUEPRINT.md": "负责提供Layer 9研究与创新层的完整蓝图设计，包括所有模块的架构设计、技术实现、开源替代方案和实施计划，为研究与创新层开发提供全面指导。",
            
            "DOCUMENT_QUALITY_MONITORING_MECHANISM.md": "负责监控Layer 9研究与创新层文档质量，包括文档完整性、规范性、一致性等指标的监控和报告，为文档质量持续改进提供依据。",
            
            "IMPLEMENTATION_GUIDE.md": "负责提供Layer 9研究与创新层的实施指南，包括模块实施顺序、技术选型、配置方法、测试验证等，为研究与创新层开发提供实施指导。",
            
            "LAYER9_DOCUMENT_GOVERNANCE_DEEP_AUDIT_SUMMARY.md": "负责总结Layer 9研究与创新层文档治理深度审计的结果，提供审计发现、问题分析和改进建议的摘要，为快速了解审计结果提供入口。",
            
            "_archive/COMPLETE_BLUEPRINT_V3.md": "负责提供Layer 9研究与创新层的完整蓝图设计（历史版本V3），已归档，仅供参考。",
            
            "_archive/COMPLETE_SUPPLEMENT_v2.md": "负责补充Layer 9研究与创新层的缺失模块设计（历史版本V2），已归档，仅供参考。",
            
            "_archive/CRITICAL_MISSING_V4.md": "负责记录Layer 9研究与创新层的关键缺失模块（历史版本V4），已归档，仅供参考。",
            
            "_archive/MISSING_MODULES_SUPPLEMENT.md": "负责补充Layer 9研究与创新层的缺失模块设计，已归档，仅供参考。"
        }
        
    def run_fix(self):
        """执行修复"""
        print("=" * 80)
        print("Layer 9研究与创新层职责字段修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修复路径: {self.layer9_path}")
        print()
        
        # 遍历所有需要修复的文件
        for filename, responsibility in self.responsibility_map.items():
            file_path = self.layer9_path / filename
            
            if not file_path.exists():
                print(f"⚠️  文件不存在: {filename}")
                continue
            
            print(f"📝 处理文件: {filename}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否已有responsibility字段
            if re.search(r'^responsibility:\s*\n(\s+-\s+.+\n)+', content, re.MULTILINE):
                print(f"  ✅ 已有responsibility字段，跳过")
                print()
                continue
            
            # 检查是否有YAML头部
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            
            if yaml_match:
                # 有YAML头部，在YAML头部中添加responsibility字段
                yaml_header = yaml_match.group(1)
                
                # 在YAML头部末尾添加responsibility字段
                new_yaml_header = yaml_header + f"\nresponsibility:\n  - {responsibility}"
                
                # 替换YAML头部
                new_content = content.replace(yaml_header, new_yaml_header, 1)
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                self.fix_count += 1
                self.fix_log.append({
                    "filename": filename,
                    "action": "添加responsibility字段",
                    "responsibility": responsibility
                })
                
                print(f"  ✅ 已添加responsibility字段")
                print()
            else:
                # 没有YAML头部，创建YAML头部
                yaml_header = f"""---
module_id: {filename.replace('.md', '').upper()}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席蓝图架构师
responsibility:
  - {responsibility}
---

"""
                
                # 在文件开头添加YAML头部
                new_content = yaml_header + content
                
                # 写回文件
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                self.fix_count += 1
                self.fix_log.append({
                    "filename": filename,
                    "action": "创建YAML头部并添加responsibility字段",
                    "responsibility": responsibility
                })
                
                print(f"  ✅ 已创建YAML头部并添加responsibility字段")
                print()
        
        # 输出修复摘要
        print("=" * 80)
        print("修复摘要")
        print("=" * 80)
        print(f"修复文件数: {self.fix_count}")
        print()
        
        if self.fix_log:
            print("修复详情:")
            for i, log in enumerate(self.fix_log, 1):
                print(f"  {i}. {log['filename']}")
                print(f"     操作: {log['action']}")
                print(f"     职责: {log['responsibility'][:50]}...")
                print()
        
        print("✅ 修复完成")
        print()

if __name__ == "__main__":
    fixer = Layer9ResponsibilityFixer()
    fixer.run_fix()
