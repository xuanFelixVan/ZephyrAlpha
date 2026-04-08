#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复Layer 8所有P1级问题
为所有缺少responsibility字段的文档添加职责描述
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8CompleteP1Fixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        self.skipped_files = []
        
    def fix_all(self):
        """修复所有P1级问题"""
        print("=" * 80)
        print("Layer 8 P1级问题全面修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描所有文件
        print("\n[阶段1] 扫描所有文件...")
        self.scan_all_files()
        
        # 2. 为缺少responsibility的文件添加字段
        print("\n[阶段2] 为缺少responsibility的文件添加字段...")
        self.add_missing_responsibility()
        
        # 3. 生成报告
        print("\n[阶段3] 生成修复报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"跳过文件数: {len(self.skipped_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def scan_all_files(self):
        """扫描所有文件"""
        total_files = 0
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    total_files += 1
        
        print(f"  扫描到 {total_files} 个Markdown文件")
    
    def get_responsibility(self, file_name, dir_name):
        """根据文件名和目录名确定职责"""
        # 职责映射表
        responsibility_map = {
            # 蓝图文档
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
            
            # 索引文档
            "INDEX": f"{dir_name}模块目录导航与文档索引管理与优化维护",
            
            # 其他文档
            "BLUEPRINT_CHAPTER_NAMING_STANDARD": "蓝图章节命名标准文档",
            "INDEX_TEMPLATE": "索引模板文档",
        }
        
        # 提取文件名（不含扩展名）
        file_base = file_name.replace('.md', '')
        
        # 查找匹配的职责
        for key, value in responsibility_map.items():
            if key in file_base:
                return value
        
        # 默认职责
        return "系统模块设计与实施方案与优化维护"
    
    def add_missing_responsibility(self):
        """为缺少responsibility的文件添加字段"""
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
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
                            
                            # 检查是否缺少responsibility字段
                            if 'responsibility:' not in yaml_content:
                                # 获取职责
                                responsibility = self.get_responsibility(file, dir_name)
                                
                                # 添加responsibility字段
                                new_yaml = yaml_content + f"\nresponsibility:\n  - {responsibility}"
                                new_content = content.replace(yaml_content, new_yaml)
                                
                                # 写回文件
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                self.fixed_files.append({
                                    "file": str(rel_path),
                                    "responsibility": responsibility
                                })
                                print(f"  [OK] {rel_path}")
                            else:
                                self.skipped_files.append(str(rel_path))
                        else:
                            # 没有YAML头部，创建一个新的
                            responsibility = self.get_responsibility(file, dir_name)
                            module_id = f"08_HUMAN_AI_INTERFACE_{file.replace('.md', '')}"
                            
                            yaml_header = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档管理团队
responsibility:
  - {responsibility}
standard_type: 蓝图文档
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

"""
                            new_content = yaml_header + content
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            self.fixed_files.append({
                                "file": str(rel_path),
                                "responsibility": responsibility
                            })
                            print(f"  [OK] {rel_path} (添加YAML头部)")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_COMPLETE_P1_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_COMPLETE_P1_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 P1级问题全面修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 P1级问题全面修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: P1级问题全面修复

---

## 📊 修复概要

| 指标 | 数值 |
|------|------|
| **修复文件总数** | {len(self.fixed_files)} |
| **跳过文件数** | {len(self.skipped_files)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 修复详情

### 修复的文件列表

"""
        
        for item in self.fixed_files[:30]:
            report += f"- **{item['file']}**: {item['responsibility']}\n"
        
        if len(self.fixed_files) > 30:
            report += f"\n*还有 {len(self.fixed_files) - 30} 个文件*\n"
        
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

- 为 {len(self.fixed_files)} 个文件添加了responsibility字段
- 跳过了 {len(self.skipped_files)} 个已有responsibility字段的文件
- 提高了文档的职责清晰度

### 职责分配原则

1. **蓝图文档**: 根据模块功能分配具体职责
2. **索引文档**: 根据模块名称分配导航职责
3. **标准文档**: 根据文档类型分配标准职责

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
    fixer = Layer8CompleteP1Fixer()
    fixer.fix_all()
