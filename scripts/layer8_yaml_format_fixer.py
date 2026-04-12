#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复Layer 8 YAML头部格式问题
确保YAML头部只包含YAML内容
"""

import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("D:/ZephyrAlpha/docs/08_HUMAN_AI_INTERFACE")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state")

class Layer8YAMLFormatFixer:
    def __init__(self):
        self.fixed_files = []
        self.errors = []
        
    def fix_all(self):
        """修复所有YAML头部格式问题"""
        print("=" * 80)
        print("Layer 8 YAML头部格式修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 扫描所有文件
        print("\n[阶段1] 扫描所有文件...")
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
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查YAML头部
                        yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                        
                        if yaml_match:
                            yaml_content = yaml_match.group(1)
                            
                            # 检查YAML头部是否包含非YAML内容
                            if '**' in yaml_content or '##' in yaml_content:
                                # 提取有效的YAML字段
                                valid_yaml_fields = self.extract_valid_yaml_fields(yaml_content)
                                
                                # 构建新的YAML头部
                                new_yaml = self.build_clean_yaml(valid_yaml_fields, file, file_path.parent.name)
                                
                                # 替换旧的YAML头部
                                new_content = content.replace(yaml_content, new_yaml)
                                
                                # 写回文件
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                self.fixed_files.append(str(rel_path))
                                print(f"  [OK] {rel_path}")
                        
                    except Exception as e:
                        self.errors.append({
                            "file": str(rel_path),
                            "error": str(e)
                        })
                        print(f"  [错误] {rel_path} - {e}")
    
    def extract_valid_yaml_fields(self, yaml_content):
        """提取有效的YAML字段"""
        valid_fields = {}
        
        # 提取module_id
        module_id_match = re.search(r'module_id:\s*(.+)', yaml_content)
        if module_id_match:
            valid_fields['module_id'] = module_id_match.group(1).strip()
        
        # 提取version
        version_match = re.search(r'version:\s*(.+)', yaml_content)
        if version_match:
            valid_fields['version'] = version_match.group(1).strip()
        
        # 提取status
        status_match = re.search(r'status:\s*(.+)', yaml_content)
        if status_match:
            valid_fields['status'] = status_match.group(1).strip()
        
        # 提取created_date
        created_date_match = re.search(r'created_date:\s*(.+)', yaml_content)
        if created_date_match:
            valid_fields['created_date'] = created_date_match.group(1).strip()
        
        # 提取last_updated
        last_updated_match = re.search(r'last_updated:\s*(.+)', yaml_content)
        if last_updated_match:
            valid_fields['last_updated'] = last_updated_match.group(1).strip()
        
        # 提取owner
        owner_match = re.search(r'owner:\s*(.+)', yaml_content)
        if owner_match:
            valid_fields['owner'] = owner_match.group(1).strip()
        
        # 提取responsibility
        responsibility_match = re.search(r'responsibility:\s*\n\s+-\s+(.+)', yaml_content)
        if responsibility_match:
            valid_fields['responsibility'] = responsibility_match.group(1).strip()
        
        return valid_fields
    
    def build_clean_yaml(self, valid_fields, file_name, dir_name):
        """构建干净的YAML头部"""
        # 如果缺少必要字段，添加默认值
        if 'module_id' not in valid_fields:
            module_name = file_name.replace('.md', '')
            valid_fields['module_id'] = f"08_HUMAN_AI_INTERFACE_{module_name}"
        
        if 'version' not in valid_fields:
            valid_fields['version'] = '1.0.0'
        
        if 'status' not in valid_fields:
            valid_fields['status'] = 'Active'
        
        if 'created_date' not in valid_fields:
            valid_fields['created_date'] = datetime.now().strftime('%Y-%m-%d')
        
        if 'last_updated' not in valid_fields:
            valid_fields['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        if 'owner' not in valid_fields:
            valid_fields['owner'] = '文档管理团队'
        
        if 'responsibility' not in valid_fields:
            # 根据文件名确定职责
            responsibility_map = {
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
            
            file_base = file_name.replace('.md', '')
            valid_fields['responsibility'] = responsibility_map.get(file_base, "系统模块设计与实施方案与优化维护")
        
        # 构建YAML字符串
        yaml_str = f"""module_id: {valid_fields['module_id']}
version: {valid_fields['version']}
status: {valid_fields['status']}
created_date: {valid_fields['created_date']}
last_updated: {valid_fields['last_updated']}
owner: {valid_fields['owner']}
responsibility:
  - {valid_fields['responsibility']}"""
        
        return yaml_str
    
    def generate_report(self):
        """生成修复报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = OUTPUT_DIR / f"LAYER8_YAML_FORMAT_FIX_REPORT_{timestamp}.md"
        
        report = f"""---
module_id: LAYER8_YAML_FORMAT_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Audit Sentinel
responsibility:
  - Layer 8 YAML头部格式修复报告
standard_type: 修复报告
applicable_scope: Layer 8 - 人机交互层
compliance_level: 专业标准
---

# Layer 8 YAML头部格式修复报告

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: Layer 8 人机交互层  
**修复类型**: YAML头部格式修复

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

- 修复了 {len(self.fixed_files)} 个文件的YAML头部格式
- 确保YAML头部只包含YAML内容
- 提高了文档的规范性和可解析性

### 后续建议

1. 验证修复效果
2. 重新运行审计
3. 保持YAML格式规范

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复执行者**: Audit Sentinel
"""
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] 修复报告已生成: {report_file}")


if __name__ == "__main__":
    fixer = Layer8YAMLFormatFixer()
    fixer.fix_all()
