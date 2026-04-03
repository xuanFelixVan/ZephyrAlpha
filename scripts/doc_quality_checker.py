#!/usr/bin/env python3
"""
文档质量检查脚本（个人开发者版）

功能:
- 检查文档完整性（必需字段）
- 检查Markdown格式
- 检查链接有效性
- 生成质量报告

使用方法:
    python scripts/doc_quality_checker.py
    python scripts/doc_quality_checker.py --fix  # 自动修复部分问题
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class DocumentQualityChecker:
    """文档质量检查器"""
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.results = {
            "total_files": 0,
            "passed_files": 0,
            "failed_files": 0,
            "warnings": 0,
            "errors": 0,
            "details": []
        }
        
        self.required_fields = [
            "module_id",
            "version",
            "status",
            "created_date",
            "last_updated",
            "owner"
        ]
        
        self.recommended_fields = [
            "standard_type",
            "applicable_scope",
            "compliance_level",
            "parent_document",
            "implementation_status"
        ]
    
    def check_all_documents(self) -> Dict[str, Any]:
        """检查所有文档"""
        print("🔍 开始检查文档质量...")
        print(f"📁 文档根目录: {self.docs_root.absolute()}")
        print("-" * 60)
        
        # 遍历所有Markdown文件
        for md_file in self.docs_root.rglob("*.md"):
            if self._should_skip(md_file):
                continue
            
            self.results["total_files"] += 1
            file_result = self.check_document(md_file)
            
            if file_result["passed"]:
                self.results["passed_files"] += 1
            else:
                self.results["failed_files"] += 1
            
            self.results["warnings"] += file_result["warnings"]
            self.results["errors"] += file_result["errors"]
            self.results["details"].append(file_result)
        
        # 生成报告
        self._print_summary()
        return self.results
    
    def _should_skip(self, file_path: Path) -> bool:
        """判断是否跳过该文件"""
        skip_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            "README.md"  # README通常不需要完整元数据
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def check_document(self, file_path: Path) -> Dict[str, Any]:
        """检查单个文档"""
        result = {
            "file": str(file_path.relative_to(self.docs_root)),
            "passed": True,
            "warnings": 0,
            "errors": 0,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查元数据
            metadata_issues = self._check_metadata(content)
            result["issues"].extend(metadata_issues)
            
            # 检查Markdown格式
            format_issues = self._check_markdown_format(content)
            result["issues"].extend(format_issues)
            
            # 检查链接
            link_issues = self._check_links(content, file_path)
            result["issues"].extend(link_issues)
            
            # 统计问题
            for issue in result["issues"]:
                if issue["severity"] == "error":
                    result["errors"] += 1
                    result["passed"] = False
                elif issue["severity"] == "warning":
                    result["warnings"] += 1
            
            # 打印结果
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['file']}")
            if result["issues"]:
                for issue in result["issues"]:
                    icon = "⚠️" if issue["severity"] == "warning" else "❌"
                    print(f"   {icon} {issue['message']}")
        
        except Exception as e:
            result["passed"] = False
            result["errors"] += 1
            result["issues"].append({
                "type": "file_error",
                "severity": "error",
                "message": f"无法读取文件: {str(e)}"
            })
            print(f"❌ {result['file']} - 无法读取文件")
        
        return result
    
    def _check_metadata(self, content: str) -> List[Dict[str, Any]]:
        """检查元数据"""
        issues = []
        
        # 提取YAML前置元数据
        metadata_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        
        if not metadata_match:
            issues.append({
                "type": "metadata_missing",
                "severity": "warning",
                "message": "缺少YAML元数据块"
            })
            return issues
        
        metadata_text = metadata_match.group(1)
        
        # 检查必需字段
        for field in self.required_fields:
            if f"{field}:" not in metadata_text:
                issues.append({
                    "type": "missing_required_field",
                    "severity": "error",
                    "message": f"缺少必需字段: {field}"
                })
        
        # 检查推荐字段
        for field in self.recommended_fields:
            if f"{field}:" not in metadata_text:
                issues.append({
                    "type": "missing_recommended_field",
                    "severity": "warning",
                    "message": f"缺少推荐字段: {field}"
                })
        
        # 检查日期格式
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        if 'created_date:' in metadata_text:
            if not re.search(date_pattern, metadata_text):
                issues.append({
                    "type": "invalid_date_format",
                    "severity": "warning",
                    "message": "created_date格式不正确（应为YYYY-MM-DD）"
                })
        
        return issues
    
    def _check_markdown_format(self, content: str) -> List[Dict[str, Any]]:
        """检查Markdown格式"""
        issues = []
        lines = content.split('\n')
        
        # 检查标题层级
        prev_heading_level = 0
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                heading_level = len(line) - len(line.lstrip('#'))
                
                # 标题层级跳跃检查
                if heading_level > prev_heading_level + 1 and prev_heading_level > 0:
                    issues.append({
                        "type": "heading_level_jump",
                        "severity": "warning",
                        "message": f"第{i}行: 标题层级跳跃（从H{prev_heading_level}到H{heading_level}）"
                    })
                
                prev_heading_level = heading_level
        
        # 检查代码块
        code_blocks = re.findall(r'```', content)
        if len(code_blocks) % 2 != 0:
            issues.append({
                "type": "unclosed_code_block",
                "severity": "error",
                "message": "代码块未正确关闭"
            })
        
        # 检查列表格式
        for i, line in enumerate(lines, 1):
            # 检查无序列表
            if re.match(r'^\s*[\*\-]\s', line):
                if not re.match(r'^\s*[\*\-]\s+\S', line):
                    issues.append({
                        "type": "list_format",
                        "severity": "warning",
                        "message": f"第{i}行: 列表项格式不正确（缺少空格）"
                    })
        
        return issues
    
    def _check_links(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """检查链接"""
        issues = []
        
        # 提取所有链接
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for text, url in links:
            # 检查内部链接
            if url.startswith('./') or url.startswith('../') or url.startswith('/'):
                # 计算目标路径
                if url.startswith('/'):
                    target_path = self.docs_root / url.lstrip('/')
                else:
                    target_path = file_path.parent / url
                
                # 检查文件是否存在
                if not target_path.exists():
                    issues.append({
                        "type": "broken_link",
                        "severity": "warning",
                        "message": f"链接失效: [{text}]({url})"
                    })
        
        return issues
    
    def _print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 文档质量检查报告")
        print("=" * 60)
        print(f"📁 检查文件总数: {self.results['total_files']}")
        print(f"✅ 通过文件数: {self.results['passed_files']}")
        print(f"❌ 失败文件数: {self.results['failed_files']}")
        print(f"⚠️  警告总数: {self.results['warnings']}")
        print(f"❌ 错误总数: {self.results['errors']}")
        
        pass_rate = (self.results['passed_files'] / self.results['total_files'] * 100 
                     if self.results['total_files'] > 0 else 0)
        print(f"\n📈 通过率: {pass_rate:.1f}%")
        
        if self.results['failed_files'] == 0:
            print("\n🎉 所有文档质量检查通过！")
        else:
            print(f"\n⚠️  发现 {self.results['failed_files']} 个文件存在问题，请修复。")
    
    def save_report(self, output_file: str = "docs_quality_report.json"):
        """保存报告到JSON文件"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": self.results["total_files"],
                "passed_files": self.results["passed_files"],
                "failed_files": self.results["failed_files"],
                "warnings": self.results["warnings"],
                "errors": self.results["errors"],
                "pass_rate": (self.results["passed_files"] / self.results["total_files"] * 100 
                             if self.results["total_files"] > 0 else 0)
            },
            "details": self.results["details"]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 质量报告已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档质量检查工具')
    parser.add_argument('--docs-root', default='docs', help='文档根目录')
    parser.add_argument('--output', default='docs_quality_report.json', help='输出报告文件')
    parser.add_argument('--fix', action='store_true', help='自动修复部分问题（暂未实现）')
    
    args = parser.parse_args()
    
    checker = DocumentQualityChecker(args.docs_root)
    checker.check_all_documents()
    checker.save_report(args.output)


if __name__ == '__main__':
    main()
