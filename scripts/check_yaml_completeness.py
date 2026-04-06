#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML字段完整性检查脚本
用于检查蓝图文件的YAML头部字段是否完整

使用方法:
    python check_yaml_completeness.py [--fix] [--report]

参数:
    --fix: 自动修复缺失字段
    --report: 生成详细报告
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class YAMLFieldCheck:
    """YAML字段检查结果"""
    file_path: str
    module_id: str
    missing_fields: List[str] = field(default_factory=list)
    has_change_history: bool = False
    encoding_issues: bool = False
    yaml_valid: bool = True
    error_message: str = ""

@dataclass
class BlueprintStandard:
    """蓝图标准字段定义"""
    required_fields: List[str] = field(default_factory=lambda: [
        "module_id",
        "version", 
        "status",
        "created_date",
        "last_updated",
        "owner",
        "standard_type",
        "applicable_scope",
        "compliance_level",
        "parent_document",
        "implementation_status"
    ])
    
    recommended_fields: List[str] = field(default_factory=lambda: [
        "open_source_dependency",
        "estimated_effort",
        "priority"
    ])

class YAMLCompletenessChecker:
    """YAML完整性检查器"""
    
    def __init__(self, blueprints_dir: str):
        self.blueprints_dir = Path(blueprints_dir)
        self.standard = BlueprintStandard()
        self.results: List[YAMLFieldCheck] = []
        
    def extract_yaml_block(self, content: str) -> Tuple[Optional[str], str]:
        """提取YAML头部块"""
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(yaml_pattern, content, re.DOTALL)
        if match:
            return match.group(1), content[match.end():]
        return None, content
    
    def check_file(self, file_path: Path) -> YAMLFieldCheck:
        """检查单个文件"""
        result = YAMLFieldCheck(file_path=str(file_path), module_id="UNKNOWN")
        
        try:
            # 尝试多种编码读取
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if content is None:
                result.yaml_valid = False
                result.error_message = "无法识别文件编码"
                return result
            
            # 检查乱码字符
            if '�' in content or '?' in content[:500]:
                result.encoding_issues = True
            
            # 提取YAML块
            yaml_block, remaining_content = self.extract_yaml_block(content)
            
            if yaml_block is None:
                result.yaml_valid = False
                result.error_message = "未找到YAML头部块"
                return result
            
            # 解析YAML
            try:
                yaml_data = yaml.safe_load(yaml_block)
                if not isinstance(yaml_data, dict):
                    result.yaml_valid = False
                    result.error_message = "YAML格式错误"
                    return result
            except yaml.YAMLError as e:
                result.yaml_valid = False
                result.error_message = f"YAML解析错误: {str(e)}"
                return result
            
            # 提取module_id
            result.module_id = yaml_data.get('module_id', 'UNKNOWN')
            
            # 检查必需字段
            for field in self.standard.required_fields:
                if field not in yaml_data or not yaml_data[field]:
                    result.missing_fields.append(field)
            
            # 检查推荐字段
            for field in self.standard.recommended_fields:
                if field not in yaml_data or not yaml_data[field]:
                    result.missing_fields.append(f"[推荐]{field}")
            
            # 检查变更历史
            history_patterns = [
                r'##\s*\d+\.\s*变更历史',
                r'##\s*变更历史',
                r'##\s*版本历史',
                r'\*\*版本历史\*\*',
                r'\*\*变更历史\*\*'
            ]
            
            result.has_change_history = any(
                re.search(pattern, remaining_content) 
                for pattern in history_patterns
            )
            
        except Exception as e:
            result.yaml_valid = False
            result.error_message = f"处理错误: {str(e)}"
        
        return result
    
    def scan_all(self) -> List[YAMLFieldCheck]:
        """扫描所有蓝图文件"""
        blueprint_files = list(self.blueprints_dir.glob("*_BLUEPRINT.md"))
        print(f"📁 找到 {len(blueprint_files)} 个蓝图文件")
        
        for file_path in blueprint_files:
            result = self.check_file(file_path)
            self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> str:
        """生成检查报告"""
        report_lines = [
            "# YAML字段完整性检查报告",
            f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**检查范围**: {self.blueprints_dir}",
            f"**文件总数**: {len(self.results)}",
            "\n---\n",
            "## 1. 检查概要\n"
        ]
        
        # 统计数据
        valid_count = sum(1 for r in self.results if r.yaml_valid)
        invalid_count = len(self.results) - valid_count
        missing_fields_count = sum(1 for r in self.results if r.missing_fields)
        no_history_count = sum(1 for r in self.results if not r.has_change_history)
        encoding_issues_count = sum(1 for r in self.results if r.encoding_issues)
        
        report_lines.extend([
            "| 检查项 | 数量 | 占比 |",
            "|--------|------|------|",
            f"| YAML格式有效 | {valid_count} | {valid_count/len(self.results)*100:.1f}% |",
            f"| YAML格式无效 | {invalid_count} | {invalid_count/len(self.results)*100:.1f}% |",
            f"| 缺失必需字段 | {missing_fields_count} | {missing_fields_count/len(self.results)*100:.1f}% |",
            f"| 缺失变更历史 | {no_history_count} | {no_history_count/len(self.results)*100:.1f}% |",
            f"| 编码问题 | {encoding_issues_count} | {encoding_issues_count/len(self.results)*100:.1f}% |",
            "\n---\n",
            "## 2. 详细问题列表\n"
        ])
        
        # YAML格式无效的文件
        invalid_files = [r for r in self.results if not r.yaml_valid]
        if invalid_files:
            report_lines.append("### 2.1 YAML格式无效\n")
            for r in invalid_files:
                report_lines.append(f"- **{Path(r.file_path).name}**: {r.error_message}")
            report_lines.append("")
        
        # 缺失必需字段的文件
        missing_fields_files = [r for r in self.results if r.missing_fields and r.yaml_valid]
        if missing_fields_files:
            report_lines.append("### 2.2 缺失必需字段\n")
            for r in missing_fields_files:
                report_lines.append(f"- **{r.module_id}** ({Path(r.file_path).name})")
                report_lines.append(f"  - 缺失: {', '.join(r.missing_fields)}")
            report_lines.append("")
        
        # 缺失变更历史的文件
        no_history_files = [r for r in self.results if not r.has_change_history and r.yaml_valid]
        if no_history_files:
            report_lines.append("### 2.3 缺失变更历史\n")
            for r in no_history_files[:20]:  # 只显示前20个
                report_lines.append(f"- **{r.module_id}** ({Path(r.file_path).name})")
            if len(no_history_files) > 20:
                report_lines.append(f"- ... 还有 {len(no_history_files) - 20} 个文件")
            report_lines.append("")
        
        # 编码问题文件
        encoding_issue_files = [r for r in self.results if r.encoding_issues]
        if encoding_issue_files:
            report_lines.append("### 2.4 编码问题\n")
            for r in encoding_issue_files:
                report_lines.append(f"- **{r.module_id}** ({Path(r.file_path).name})")
            report_lines.append("")
        
        report_lines.extend([
            "---\n",
            "## 3. 修复建议\n",
            "### 3.1 立即修复（P0）\n",
            "- 修复YAML格式无效的文件",
            "- 修复编码问题文件",
            "\n### 3.2 本周修复（P1）\n",
            "- 补充缺失的必需字段",
            "- 补充变更历史章节",
            "\n### 3.3 长期优化（P2）\n",
            "- 补充推荐字段（open_source_dependency, estimated_effort, priority）",
            "- 建立自动化检查机制"
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, output_path: str):
        """保存报告"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已保存至: {output_path}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YAML字段完整性检查工具')
    parser.add_argument('--fix', action='store_true', help='自动修复缺失字段')
    parser.add_argument('--report', action='store_true', help='生成详细报告')
    parser.add_argument('--dir', default='docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS', 
                       help='蓝图目录路径')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    blueprints_dir = project_root / args.dir
    
    print(f"🔍 开始检查YAML字段完整性...")
    print(f"📁 蓝图目录: {blueprints_dir}")
    
    checker = YAMLCompletenessChecker(str(blueprints_dir))
    results = checker.scan_all()
    
    # 生成报告
    if args.report:
        report_path = project_root / "docs" / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state" / "YAML_COMPLETENESS_CHECK_REPORT.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        checker.save_report(str(report_path))
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 检查摘要")
    print("="*60)
    
    valid_count = sum(1 for r in results if r.yaml_valid)
    missing_fields_count = sum(1 for r in results if r.missing_fields)
    no_history_count = sum(1 for r in results if not r.has_change_history)
    
    print(f"✅ YAML格式有效: {valid_count}/{len(results)} ({valid_count/len(results)*100:.1f}%)")
    print(f"⚠️  缺失必需字段: {missing_fields_count}/{len(results)} ({missing_fields_count/len(results)*100:.1f}%)")
    print(f"⚠️  缺失变更历史: {no_history_count}/{len(results)} ({no_history_count/len(results)*100:.1f}%)")
    
    if args.fix:
        print("\n🔧 自动修复功能开发中...")

if __name__ == "__main__":
    main()
