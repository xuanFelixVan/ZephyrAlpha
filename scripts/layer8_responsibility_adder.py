#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
为Layer 8所有缺少responsibility字段的文档添加职责描述
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8ResponsibilityAdder:
    def __init__(self):
        self.added_files = []
        self.errors = []
        
        # 职责映射表
        self.responsibility_map = {
            "MONITORING_DASHBOARD_BLUEPRINT": "系统监控仪表板设计与实施方案与优化维护",
            "BACKTEST_UI_BLUEPRINT": "回测界面设计与实施方案与优化维护",
            "REPORTING_BLUEPRINT": "报告系统设计与实施方案与优化维护",
            "DOCUMENTATION_CENTER_BLUEPRINT": "文档中心设计与实施方案与优化维护",
            "RISK_DASHBOARD_BLUEPRINT": "风险管理仪表板设计与实施方案与优化维护",
            "STRATEGY_IDE_BLUEPRINT": "策略开发IDE设计与实施方案与优化维护",
            "FACTOR_ANALYSIS_BLUEPRINT": "因子分析工具设计与实施方案与优化维护",
            "RISK_CONTROL_PANEL_BLUEPRINT": "风控面板设计与实施方案与优化维护",
            "API_GATEWAY_BLUEPRINT": "API网关设计与实施方案与优化维护",
            "WEBSOCKET_REALTIME_BLUEPRINT": "WebSocket实时通信设计与实施方案与优化维护",
            "COMPLIANCE_MONITORING_BLUEPRINT": "合规监控界面设计与实施方案与优化维护",
            "CAPITAL_MANAGEMENT_BLUEPRINT": "资金管理界面设计与实施方案与优化维护",
            "USER_BEHAVIOR_ANALYTICS_BLUEPRINT": "用户行为分析设计与实施方案与优化维护",
            "I18N_SUPPORT_BLUEPRINT": "多语言支持设计与实施方案与优化维护",
            "THEME_CUSTOMIZATION_BLUEPRINT": "主题定制系统设计与实施方案与优化维护",
            "DATA_EXPORT_TOOLS_BLUEPRINT": "数据导出工具设计与实施方案与优化维护",
            "USER_TRAINING_BLUEPRINT": "用户培训系统设计与实施方案与优化维护",
            "ACCESSIBILITY_BLUEPRINT": "无障碍支持设计与实施方案与优化维护",
            "OFFLINE_SUPPORT_BLUEPRINT": "离线支持设计与实施方案与优化维护",
            "THIRD_PARTY_INTEGRATION_BLUEPRINT": "第三方集成设计与实施方案与优化维护",
            "BLUEPRINT_CHAPTER_NAMING_STANDARD": "蓝图章节命名标准文档",
            "INDEX_TEMPLATE": "索引模板文档",
        }
    
    def add_all(self):
        """为所有缺少responsibility字段的文档添加职责描述"""
        print("=" * 80)
        print("Layer 8 职责字段添加")
        print("=" * 80)
        print(f"添加时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描所有文件
        print("\n[阶段1] 扫描所有文件...")
        self.scan_and_add_responsibility()
        
        # 2. 生成报告
        print("\n[阶段2] 生成添加报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("添加完成！")
        print(f"添加文件数: {len(self.added_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def scan_and_add_responsibility(self):
        """扫描并添加responsibility字段"""
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取YAML头部
                        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            
                            # 检查是否缺少responsibility字段
                            resp_match = re.search(r'responsibility:\s*\n((?:\s+-[^\n]+\n?)+)', yaml_content)
                            
                            if not resp_match:
                                # 确定职责
                                responsibility = self.determine_responsibility(file, file_path.parent.name)
                                
                                # 添加responsibility字段
                                new_yaml = yaml_content + f"\nresponsibility:\n  - {responsibility}"
                                new_content = content.replace(yaml_content, new_yaml)
                                
                                # 写回文件
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                self.added_files.append({
                                    "file": str(rel_path),
                                    "responsibility": responsibility
                                })
                                print(f"  [OK] {rel_path}")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def determine_responsibility(self, file_name, dir_name):
        """确定文档的职责"""
        # 移除.md后缀
        file_base = file_name.replace('.md', '')
        
        # 检查是否在映射表中
        if file_base in self.responsibility_map:
            return self.responsibility_map[file_base]
        
        # 根据文件类型确定职责
        if file_name == 'INDEX.md':
            return f"{dir_name}模块目录导航与文档索引管理与优化维护"
        elif file_name == 'README.md':
            return f"{dir_name}模块概述与快速开始指南"
        elif '_BLUEPRINT' in file_name:
            return f"{file_base.replace('_BLUEPRINT', '')}设计与实施方案与优化维护"
        else:
            return f"{file_base}文档"
    
    def generate_report(self):
        """生成添加报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_RESPONSIBILITY_ADD_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_RESPONSIBILITY_ADD_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 职责字段添加报告
standard_type: 添加报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 职责字段添加报告

**添加时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**添加范围**: Layer 8 人机交互层  
**添加类型**: responsibility字段添加

---

## 📊 添加概要

| 指标 | 数值 |
|------|------|
| **添加文件总数** | {len(self.added_files)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 添加详情

### 添加的文件列表

"""
        
        for item in self.added_files[:20]:
            report += f"- **{item['file']}**: {item['responsibility']}\n"
        
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

## 📝 添加总结

### 主要成果

- 为 {len(self.added_files)} 个文档添加了responsibility字段
- 提高了文档的职责清晰度
- 符合专业量化机构职责驱动原则

### 后续建议

1. 验证添加效果
2. 重新运行审计
3. 保持职责描述的一致性

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**添加执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 添加报告已生成: {report_file}")


if __name__ == "__main__":
    adder = Layer8ResponsibilityAdder()
    adder.add_all()
