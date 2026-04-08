#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Layer 8 P1级问题
1. 更新主索引，删除死链接
2. 为现有文件添加缺失的responsibility和module_id字段
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8P1FixerV2:
    def __init__(self):
        self.fixed_files = []
        self.removed_links = []
        self.errors = []
        
    def fix_all(self):
        """修复所有P1级问题"""
        print("=" * 80)
        print("Layer 8 P1级问题修复 V2")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 更新主索引
        print("\n[任务1] 更新主索引...")
        self.update_main_index()
        
        # 2. 为现有文件添加缺失的字段
        print("\n[任务2] 为现有文件添加缺失字段...")
        self.add_missing_fields()
        
        # 3. 生成报告
        print("\n[任务3] 生成修复报告...")
        self.generate_report()
        
        print("\n" + "=" * 80)
        print("修复完成！")
        print(f"修复文件数: {len(self.fixed_files)}")
        print(f"删除死链接数: {len(self.removed_links)}")
        print(f"错误数: {len(self.errors)}")
        print("=" * 80)
    
    def update_main_index(self):
        """更新主索引，删除死链接"""
        index_file = BASE_DIR / "index.md"
        
        if not index_file.exists():
            print("  [警告] 主索引文件不存在")
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有链接
            links = re.findall(r'- \[([^\]]+)\]\(([^)]+)\)', content)
            
            # 检查每个链接是否存在
            new_content = content
            for link_text, link_path in links:
                target_path = BASE_DIR / link_path
                if not target_path.exists():
                    # 删除死链接
                    pattern = re.escape(f"- [{link_text}]({link_path})")
                    new_content = re.sub(pattern + r'\n?', '', new_content)
                    self.removed_links.append({
                        "text": link_text,
                        "path": link_path
                    })
                    print(f"  [删除] {link_text} -> {link_path}")
            
            # 写回文件
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.fixed_files.append("index.md")
            print(f"  [OK] 主索引已更新，删除了 {len(self.removed_links)} 个死链接")
            
        except Exception as e:
            self.errors.append({
                "file": "index.md",
                "error": str(e)
            })
            print(f"  [错误] index.md - {e}")
    
    def add_missing_fields(self):
        """为现有文件添加缺失的responsibility和module_id字段"""
        # 职责映射
        responsibility_map = {
            "MONITORING_DASHBOARD": "系统监控仪表板设计与实施方案与优化维护",
            "BACKTEST_UI": "回测界面设计与实施方案与优化维护",
            "REPORTING": "报告系统设计与实施方案与优化维护",
            "DOCUMENTATION_CENTER": "文档中心设计与实施方案与优化维护",
            "RISK_DASHBOARD": "风险管理仪表板设计与实施方案与优化维护",
            "STRATEGY_IDE": "策略开发IDE设计与实施方案与优化维护",
            "FACTOR_ANALYSIS": "因子分析工具设计与实施方案与优化维护",
            "RISK_CONTROL_PANEL": "风控面板设计与实施方案与优化维护",
            "API_GATEWAY": "API网关设计与实施方案与优化维护",
            "WEBSOCKET_REALTIME": "WebSocket实时通信设计与实施方案与优化维护",
            "COMPLIANCE_MONITORING": "合规监控界面设计与实施方案与优化维护",
            "CAPITAL_MANAGEMENT": "资金管理界面设计与实施方案与优化维护",
            "USER_BEHAVIOR_ANALYTICS": "用户行为分析设计与实施方案与优化维护",
            "I18N_SUPPORT": "多语言支持设计与实施方案与优化维护",
            "THEME_CUSTOMIZATION": "主题定制系统设计与实施方案与优化维护",
            "DATA_EXPORT_TOOLS": "数据导出工具设计与实施方案与优化维护",
            "USER_TRAINING": "用户培训系统设计与实施方案与优化维护",
            "ACCESSIBILITY": "无障碍支持设计与实施方案与优化维护",
            "OFFLINE_SUPPORT": "离线支持设计与实施方案与优化维护",
            "THIRD_PARTY_INTEGRATION": "第三方集成设计与实施方案与优化维护",
        }
        
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file.endswith('.md') and file != 'index.md':
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(BASE_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否有YAML头部
                        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if not yaml_match:
                            # 没有YAML头部，创建一个新的
                            module_name = file.replace('_BLUEPRINT.md', '').replace('.md', '')
                            module_id = f"08_HUMAN_AI_INTERFACE_{module_name}"
                            responsibility = responsibility_map.get(module_name, "系统模块设计与实施方案与优化维护")
                            
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
                            
                            self.fixed_files.append(str(rel_path))
                            print(f"  [OK] {rel_path} - 添加了YAML头部")
                        else:
                            # 检查是否缺少responsibility字段
                            yaml_content = yaml_match.group(1)
                            
                            if 'responsibility:' not in yaml_content:
                                # 添加responsibility字段
                                module_name = file.replace('_BLUEPRINT.md', '').replace('.md', '')
                                responsibility = responsibility_map.get(module_name, "系统模块设计与实施方案与优化维护")
                                
                                new_yaml = yaml_content + f"\nresponsibility:\n  - {responsibility}"
                                new_content = content.replace(yaml_content, new_yaml)
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                self.fixed_files.append(str(rel_path))
                                print(f"  [OK] {rel_path} - 添加了responsibility字段")
                            
                            # 检查是否缺少module_id字段
                            if 'module_id:' not in yaml_content:
                                # 添加module_id字段
                                module_name = file.replace('_BLUEPRINT.md', '').replace('.md', '')
                                module_id = f"08_HUMAN_AI_INTERFACE_{module_name}"
                                
                                new_yaml = f"module_id: {module_id}\n" + yaml_content
                                new_content = content.replace(yaml_content, new_yaml)
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                if str(rel_path) not in self.fixed_files:
                                    self.fixed_files.append(str(rel_path))
                                print(f"  [OK] {rel_path} - 添加了module_id字段")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_P1_FIX_REPORT_V2_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_P1_FIX_REPORT_V2_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 P1级问题修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 P1级问题修复报告 V2

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: P1级问题修复

---

## 📊 修复概要

| 指标 | 数值 |
|------|------|
| **修复文件总数** | {len(self.fixed_files)} |
| **删除死链接数** | {len(self.removed_links)} |
| **错误数** | {len(self.errors)} |

---

## ✅ 修复详情

### 1. 更新主索引

删除了 {len(self.removed_links)} 个死链接：

"""
        
        for link in self.removed_links[:20]:
            report += f"- [{link['text']}]({link['path']})\n"
        
        if len(self.removed_links) > 20:
            report += f"\n*还有 {len(self.removed_links) - 20} 个死链接*\n"
        
        report += f"""
### 2. 添加缺失字段

为 {len(self.fixed_files)} 个文件添加了缺失的字段：

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

- 更新了主索引，删除了 {len(self.removed_links)} 个死链接
- 为 {len(self.fixed_files)} 个文件添加了缺失的字段
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
    fixer = Layer8P1FixerV2()
    fixer.fix_all()
