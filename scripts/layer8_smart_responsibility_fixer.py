#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能修复Layer 8文档职责描述
根据文件类型（BLUEPRINT/README/INDEX）设置不同的职责
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8SmartResponsibilityFixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        
        # 蓝图文档职责映射表
        self.blueprint_responsibility_map = {
            "01_MONITORING": "系统监控仪表板架构设计、实时监控指标展示、告警规则配置与触发机制实现",
            "05_BACKTEST_UI": "回测界面交互设计、回测参数配置、回测结果可视化展示、性能指标分析图表实现",
            "06_REPORTING": "报告系统架构设计、报告模板管理、报告生成引擎、报告导出与分发功能实现",
            "17_DOCUMENTATION_CENTER": "文档中心架构设计、文档分类管理、文档搜索与导航、文档版本控制实现",
            "24_RISK_DASHBOARD": "风险管理仪表板设计、风险指标实时监控、风险预警机制、风险报告生成实现",
            "25_STRATEGY_IDE": "策略开发IDE设计、代码编辑器集成、策略调试工具、策略回测与优化功能实现",
            "26_FACTOR_ANALYSIS": "因子分析工具设计、因子挖掘算法、因子有效性测试、因子组合优化实现",
            "27_RISK_CONTROL_PANEL": "风控面板设计、风控规则配置、风控参数调整、风控日志记录与审计实现",
            "28_API_GATEWAY": "API网关架构设计、API路由管理、API认证与授权、API限流与监控实现",
            "29_WEBSOCKET_REALTIME": "WebSocket实时通信架构设计、消息推送机制、连接管理、数据同步实现",
            "30_COMPLIANCE_MONITORING": "合规监控界面设计、合规规则配置、合规检查引擎、合规报告生成实现",
            "31_CAPITAL_MANAGEMENT": "资金管理界面设计、资金分配算法、资金使用监控、资金调拨功能实现",
            "32_USER_BEHAVIOR_ANALYTICS": "用户行为分析设计、行为数据采集、行为模式识别、用户画像构建实现",
            "33_I18N_SUPPORT": "多语言支持架构设计、语言包管理、动态语言切换、本地化内容管理实现",
            "34_THEME_CUSTOMIZATION": "主题定制系统设计、主题模板管理、主题切换机制、主题配置持久化实现",
            "35_DATA_EXPORT_TOOLS": "数据导出工具设计、导出格式支持、导出任务管理、导出进度监控实现",
            "36_USER_TRAINING": "用户培训系统设计、培训内容管理、培训进度跟踪、培训效果评估实现",
            "37_ACCESSIBILITY": "无障碍支持设计、屏幕阅读器支持、键盘导航、高对比度主题实现",
            "38_OFFLINE_SUPPORT": "离线支持架构设计、离线数据缓存、离线操作同步、网络状态检测实现",
            "39_THIRD_PARTY_INTEGRATION": "第三方集成架构设计、集成接口管理、数据格式转换、集成测试框架实现"
        }
    
    def fix_all(self):
        """修复所有文档的职责描述"""
        print("=" * 80)
        print("Layer 8 智能职责修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描并修复文件
        print("\n[阶段1] 扫描并修复文件...")
        self.scan_and_fix_files()
        
        # 2. 生成报告
        print("\n[阶段2] 生成修复报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def scan_and_fix_files(self):
        """扫描并修复文件"""
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
                            
                            # 根据文件类型确定职责
                            responsibility = self.determine_responsibility(file, dir_name)
                            
                            # 清理YAML内容中的重复responsibility字段
                            clean_yaml = self.clean_yaml_content(yaml_content, responsibility)
                            
                            # 如果YAML内容有变化，则更新文件
                            if clean_yaml != yaml_content:
                                new_content = content.replace(yaml_content, clean_yaml)
                                
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
    
    def determine_responsibility(self, file_name, dir_name):
        """根据文件类型确定职责"""
        # 获取模块名称（去掉编号）
        module_name = dir_name.split('_', 1)[1] if '_' in dir_name else dir_name
        
        if file_name == 'INDEX.md':
            return f"{module_name}模块目录导航与文档索引管理"
        elif file_name == 'README.md':
            return f"{module_name}模块概述与快速开始指南"
        elif '_BLUEPRINT.md' in file_name:
            return self.blueprint_responsibility_map.get(dir_name, f"{module_name}设计与实现")
        else:
            return f"{module_name}文档"
    
    def clean_yaml_content(self, yaml_content, responsibility):
        """清理YAML内容，移除重复的responsibility字段"""
        lines = yaml_content.split('\n')
        clean_lines = []
        skip_next = False
        responsibility_added = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            
            # 如果遇到responsibility字段
            if line.strip().startswith('responsibility:'):
                if not responsibility_added:
                    # 添加正确的responsibility字段
                    clean_lines.append('responsibility:')
                    clean_lines.append(f'  - {responsibility}')
                    responsibility_added = True
                # 跳过后续的responsibility字段和其值
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
                    skip_next = True
            else:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_SMART_RESPONSIBILITY_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_SMART_RESPONSIBILITY_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 智能职责修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 智能职责修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: 智能职责描述修复

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

- 为 {len(self.fixed_files)} 个文档设置了智能职责描述
- 根据文件类型（BLUEPRINT/README/INDEX）设置不同的职责
- 避免了职责重叠问题
- 提高了文档的职责清晰度

### 职责分配策略

1. **BLUEPRINT文档**: 具体的设计和实现职责
2. **README文档**: 模块概述与快速开始指南
3. **INDEX文档**: 目录导航与文档索引管理

### 后续建议

1. 验证修复效果
2. 重新运行审计
3. 保持职责描述的一致性

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 修复报告已生成: {report_file}")


if __name__ == "__main__":
    fixer = Layer8SmartResponsibilityFixer()
    fixer.fix_all()
