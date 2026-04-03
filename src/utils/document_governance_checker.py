#!/usr/bin/env python3
"""
文档治理自动化检查工具 v1.0
专业量化机构文档治理五大原则检查工具
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
import sys

class DocumentGovernanceChecker:
    """文档治理检查器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docs_dir = os.path.join(self.project_root, "docs")
        self.src_dir = os.path.join(self.project_root, "src")
        
        # 专业量化机构文档治理五大原则
        self.principles = {
            "responsibility_driven": "职责驱动原则 (SoC)",
            "index_completeness": "索引完备性原则",
            "version_isolation": "版本隔离原则",
            "document_code_correspondence": "文档代码对应原则",
            "naming_convention": "命名规范原则"
        }
    
    def check_chinese_filenames(self) -> List[Tuple[str, str]]:
        """检查中文文件名 (原则5: 命名规范原则)"""
        issues = []
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if chinese_pattern.search(file):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_root)
                    issues.append((rel_path, "中文文件名"))
        
        return issues
    
    def check_naming_conventions(self) -> List[Tuple[str, str]]:
        """检查命名规范 (原则5: 命名规范原则)"""
        issues = []
        # 标准: 小写下划线，允许数字和点号
        standard_pattern = re.compile(r'^[a-z0-9_.-]+$')
        # 排除已归档文件
        archive_pattern = re.compile(r'archive', re.IGNORECASE)
        
        for root, dirs, files in os.walk(self.docs_dir):
            # 跳过归档目录
            if archive_pattern.search(root):
                continue
                
            for file in files:
                if not standard_pattern.match(file):
                    # 检查常见例外: PDF文件可能有大写
                    if file.endswith('.pdf'):
                        continue
                    # 检查是否包含版本号 (v1.0, v2.0等)
                    version_pattern = re.compile(r'v\d+\.\d+')
                    if version_pattern.search(file):
                        continue
                        
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_root)
                    issues.append((rel_path, f"命名不规范: {file}"))
        
        return issues
    
    def check_index_completeness(self) -> List[Tuple[str, str]]:
        """检查索引完整性 (原则2: 索引完备性原则)"""
        issues = []
        
        # 查找所有索引文件
        index_files = [
            os.path.join(self.docs_dir, "SITEMAP.md"),
            os.path.join(self.docs_dir, "System_Manifest.md"),
            os.path.join(self.docs_dir, "INDEX.md"),
        ]
        
        # 收集所有文档文件
        all_docs = []
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith('.md') or file.endswith('.csv'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.docs_dir)
                    all_docs.append(rel_path)
        
        # 简化检查: 检查主要索引文件是否存在
        for index_file in index_files:
            if not os.path.exists(index_file):
                issues.append((index_file, "索引文件缺失"))
        
        # TODO: 实现完整的索引检查逻辑
        # 这需要解析索引文件内容，检查是否引用所有活跃文档
        
        return issues
    
    def check_document_code_correspondence(self) -> List[Tuple[str, str]]:
        """检查文档代码对应关系 (原则4: 文档代码对应原则)"""
        issues = []
        
        # 查找API契约文档
        api_contract = os.path.join(self.docs_dir, "API_Contract.md")
        if os.path.exists(api_contract):
            # 读取API契约，检查对应的代码模块是否存在
            with open(api_contract, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单检查: 查找模块引用
            module_pattern = re.compile(r'`(\w+)`.*模块')
            modules_in_docs = set(module_pattern.findall(content))
            
            # 检查src/modules目录下的实际模块
            actual_modules = set()
            if os.path.exists(self.src_dir):
                modules_dir = os.path.join(self.src_dir, "modules")
                if os.path.exists(modules_dir):
                    for file in os.listdir(modules_dir):
                        if file.endswith('.py') and file != '__init__.py':
                            module_name = file[:-3]  # 去掉.py
                            actual_modules.add(module_name)
            
            # 比较差异
            missing_in_code = modules_in_docs - actual_modules
            missing_in_docs = actual_modules - modules_in_docs
            
            for module in missing_in_code:
                issues.append((api_contract, f"文档中提到的模块在代码中缺失: {module}"))
            
            for module in missing_in_docs:
                issues.append((api_contract, f"代码中的模块在文档中未提及: {module}"))
        
        return issues
    
    def run_all_checks(self) -> Dict[str, List[Tuple[str, str]]]:
        """运行所有检查"""
        results = {
            "chinese_filenames": self.check_chinese_filenames(),
            "naming_conventions": self.check_naming_conventions(),
            "index_completeness": self.check_index_completeness(),
            "document_code_correspondence": self.check_document_code_correspondence(),
        }
        
        return results
    
    def print_report(self, results: Dict[str, List[Tuple[str, str]]]):
        """打印检查报告"""
        print("=" * 80)
        print("专业量化机构文档治理审计报告")
        print("=" * 80)
        
        total_issues = 0
        for check_name, issues in results.items():
            print(f"\n{check_name.replace('_', ' ').title()}: {len(issues)} 个问题")
            for file_path, issue in issues:
                print(f"  - {file_path}: {issue}")
                total_issues += 1
        
        print(f"\n" + "=" * 80)
        print(f"总计发现 {total_issues} 个文档治理问题")
        print("=" * 80)
        
        if total_issues == 0:
            print("✅ 所有文档治理检查通过！")
        else:
            print("⚠️  发现文档治理问题，请参考专业量化机构文档治理五大原则进行修复。")

def main():
    """主函数"""
    checker = DocumentGovernanceChecker()
    results = checker.run_all_checks()
    checker.print_report(results)
    
    # 如果有问题，返回非零退出码
    total_issues = sum(len(issues) for issues in results.values())
    sys.exit(1 if total_issues > 0 else 0)

if __name__ == "__main__":
    main()