#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合修复Layer 8所有P1级问题
1. 删除重复的YAML头部
2. 为所有缺少responsibility字段的文件添加字段
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8ComprehensiveP1Fixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        self.removed_duplicates = []
        
    def fix_all(self):
        """修复所有P1级问题"""
        print("=" * 80)
        print("Layer 8 P1级问题综合修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 删除重复的YAML头部
        print("\n[阶段1] 删除重复的YAML头部...")
        self.remove_duplicate_yaml()
        
        # 2. 为缺少responsibility的文件添加字段
        print("\n[阶段2] 为缺少responsibility的文件添加字段...")
        self.add_missing_responsibility()
        
        # 3. 生成报告
        print("\n[阶段3] 生成修复报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"删除重复YAML数: {len(self.removed_duplicates)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def remove_duplicate_yaml(self):
        """删除重复的YAML头部"""
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找所有YAML块
                        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
                        yaml_blocks = list(re.finditer(yaml_pattern, content, re.DOTALL | re.MULTILINE))
                        
                        if len(yaml_blocks) > 1:
                            # 保留最后一个YAML块
                            last_yaml = yaml_blocks[-1]
                            
                            # 构建新内容：只保留最后一个YAML块和之后的内容
                            new_content = content[last_yaml.start():]
                            
                            # 清理多余的空行
                            new_content = re.sub(r'\n{3,}', '\n\n', new_content)
                            
                            # 写回文件
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            self.removed_duplicates.append(str(rel_path))
                            print(f"  [OK] {rel_path} - 删除了 {len(yaml_blocks) - 1} 个重复YAML")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
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
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_COMPREHENSIVE_P1_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_COMPREHENSIVE_P1_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 P1级问题综合修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 P1级问题综合修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: P1级问题综合修复

---

## 📊 修复概要

| 指标 | 数值 |
|------|------|
| **修复文件总数** | {len(self.fixed_files)} |
| **删除重复YAML数** | {len(self.removed_duplicates)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 修复详情

### 1. 删除重复的YAML头部

删除了 {len(self.removed_duplicates)} 个文件的重复YAML头部：

"""
        
        for file in self.removed_duplicates[:20]:
            report += f"- {file}\n"
        
        if len(self.removed_duplicates) > 20:
            report += f"\n*还有 {len(self.removed_duplicates) - 20} 个文件*\n"
        
        report += f"""
### 2. 添加responsibility字段

为 {len(self.fixed_files)} 个文件添加了responsibility字段：

"""
        
        for item in self.fixed_files[:20]:
            report += f"- **{item['file']}**: {item['responsibility']}\n"
        
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

- 删除了 {len(self.removed_duplicates)} 个文件的重复YAML头部
- 为 {len(self.fixed_files)} 个文件添加了responsibility字段
- 提高了文档的完整性和一致性

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
    fixer = Layer8ComprehensiveP1Fixer()
    fixer.fix_all()
