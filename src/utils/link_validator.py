#!/usr/bin/env python3
"""
引用链接自动化验证工具 v1.0
验证文档中所有内部链接的有效性
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
import sys

class LinkValidator:
    """链接验证器"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docs_dir = os.path.join(self.project_root, "docs")

        # 链接模式
        self.markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.absolute_url_pattern = re.compile(r'^https?://')
        self.internal_link_pattern = re.compile(r'^[^:]+\.(md|pdf|csv)$')

    def find_all_markdown_files(self) -> List[str]:
        """查找所有Markdown文件"""
        markdown_files = []

        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    markdown_files.append(full_path)

        return markdown_files

    def extract_links_from_file(self, file_path: str) -> List[Tuple[str, str, int]]:
        """从文件中提取所有链接"""
        links = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找所有Markdown链接
            for match in self.markdown_link_pattern.finditer(content):
                link_text = match.group(1)
                link_url = match.group(2)
                # 计算行号（简化版本）
                line_number = content[:match.start()].count('\n') + 1
                links.append((link_text, link_url, line_number))

        except Exception as e:
            print(f"读取文件时出错 {file_path}: {e}")

        return links

    def resolve_relative_path(self, source_file: str, relative_path: str) -> str:
        """解析相对路径为绝对路径"""
        # 获取源文件所在目录
        source_dir = os.path.dirname(source_file)

        # 处理锚点链接（如#section）
        if relative_path.startswith('#'):
            return source_file  # 指向同一文件

        # 处理跨文件锚点链接（如file.md#section）
        if '#' in relative_path:
            relative_path = relative_path.split('#')[0]

        # 解析相对路径
        absolute_path = os.path.normpath(os.path.join(source_dir, relative_path))

        return absolute_path

    def validate_link(self, source_file: str, link_url: str) -> Tuple[bool, str]:
        """验证单个链接"""
        # 检查是否为空链接
        if not link_url or link_url.strip() == '':
            return False, "空链接"

        # 检查是否为外部URL
        if self.absolute_url_pattern.match(link_url):
            # 外部URL - 暂时只检查格式
            return True, "外部URL（格式正确）"

        # 检查是否为邮件链接
        if link_url.startswith('mailto:'):
            return True, "邮件链接"

        # 检查是否为内部锚点链接
        if link_url.startswith('#'):
            # 锚点链接 - 暂时无法验证目标是否存在
            return True, "内部锚点链接"

        # 检查是否为内部文件链接
        resolved_path = self.resolve_relative_path(source_file, link_url)

        # 检查文件是否存在
        if os.path.exists(resolved_path):
            return True, "内部文件链接有效"

        # 检查是否为目录（可能链接到目录）
        if os.path.isdir(resolved_path):
            # 检查目录中是否有README.md
            readme_path = os.path.join(resolved_path, "README.md")
            if os.path.exists(readme_path):
                return True, "目录链接（有README.md）"
            else:
                return False, f"目录链接，但目录中无README.md: {resolved_path}"

        # 尝试添加.md扩展名
        if not resolved_path.endswith('.md'):
            md_path = resolved_path + '.md'
            if os.path.exists(md_path):
                return True, f"内部文件链接有效（自动添加.md扩展名）"

        # 尝试添加.pdf扩展名
        if not resolved_path.endswith('.pdf'):
            pdf_path = resolved_path + '.pdf'
            if os.path.exists(pdf_path):
                return True, f"内部文件链接有效（自动添加.pdf扩展名）"

        return False, f"文件不存在: {resolved_path}"

    def validate_all_links(self) -> Dict[str, List[Tuple[str, str, int, bool, str]]]:
        """验证所有链接"""
        results = {}
        markdown_files = self.find_all_markdown_files()

        for file_path in markdown_files:
            file_results = []
            links = self.extract_links_from_file(file_path)

            for link_text, link_url, line_number in links:
                is_valid, message = self.validate_link(file_path, link_url)
                file_results.append((link_text, link_url, line_number, is_valid, message))

            if file_results:
                rel_path = os.path.relpath(file_path, self.project_root)
                results[rel_path] = file_results

        return results

    def print_report(self, results: Dict[str, List[Tuple[str, str, int, bool, str]]]):
        """打印验证报告"""
        print("=" * 80)
        print("文档引用链接验证报告")
        print("=" * 80)

        total_links = 0
        broken_links = 0

        for file_path, file_results in results.items():
            file_broken = [r for r in file_results if not r[3]]

            if file_broken:
                print(f"\n{file_path}: {len(file_broken)} 个无效链接")
                for link_text, link_url, line_number, is_valid, message in file_broken:
                    print(f"  第{line_number}行: [{link_text}]({link_url})")
                    print(f"     错误: {message}")

                broken_links += len(file_broken)

            total_links += len(file_results)

        print(f"\n" + "=" * 80)
        print(f"链接统计:")
        print(f"  总链接数: {total_links}")
        print(f"  无效链接: {broken_links}")
        print(f"  有效链接: {total_links - broken_links}")
        print(f"  链接有效率: {((total_links - broken_links) / total_links * 100 if total_links > 0 else 100):.1f}%")
        print("=" * 80)

        if broken_links == 0:
            print("✅ 所有链接验证通过！")
        else:
            print("⚠️  发现无效链接，请及时修复。")

def main():
    """主函数"""
    validator = LinkValidator()
    results = validator.validate_all_links()
    validator.print_report(results)

    # 如果有无效链接，返回非零退出码
    broken_links = sum(1 for file_results in results.values()
                      for r in file_results if not r[3])
    sys.exit(1 if broken_links > 0 else 0)

if __name__ == "__main__":
    main()
