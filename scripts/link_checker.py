"""
link_checker.py - 链接检查器

模块ID: LINK_CHECKER_001
版本: v1.0.0
创建日期: 2026-04-03

核心功能:
1. 检查内部链接有效性
2. 检查外部链接可访问性
3. 检查路径层级是否符合规范
4. 生成链接检查报告

使用方式:
    python scripts/link_checker.py --dir docs/
    python scripts/link_checker.py --doc docs/PATH/TO/DOC.md
    python scripts/link_checker.py --all
"""

import os
import re
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Set
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed


class LinkChecker:
    """链接检查器"""
    
    def __init__(self, docs_dir: str = "docs", max_depth: int = 3, timeout: int = 5):
        """
        初始化链接检查器
        
        Args:
            docs_dir: 文档目录路径
            max_depth: 最大允许的路径层级
            timeout: 外部链接超时时间（秒）
        """
        self.docs_dir = Path(docs_dir)
        self.max_depth = max_depth
        self.timeout = timeout
        self.documents: Dict[str, Dict] = {}
        self.links: List[Dict] = []
        self.broken_links: List[Dict] = []
        self.depth_violations: List[Dict] = []
        self.insecure_links: List[Dict] = []
        
    def scan_documents(self) -> int:
        """
        扫描所有Markdown文档
        
        Returns:
            扫描到的文档数量
        """
        count = 0
        for md_file in self.docs_dir.rglob("*.md"):
            if self._should_skip(md_file):
                continue
                
            doc_info = self._extract_doc_info(md_file)
            if doc_info:
                self.documents[str(md_file)] = doc_info
                count += 1
                
        return count
    
    def _should_skip(self, file_path: Path) -> bool:
        """
        判断是否应该跳过该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否跳过
        """
        skip_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
        ]
        
        for pattern in skip_patterns:
            if pattern in str(file_path):
                return True
                
        return False
    
    def _extract_doc_info(self, file_path: Path) -> Dict:
        """
        提取文档信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档信息字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            doc_info = {
                'path': str(file_path),
                'content': content,
                'links': self._extract_links(content, file_path),
            }
            
            return doc_info
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def _extract_links(self, content: str, file_path: Path) -> List[Dict]:
        """
        提取文档中的所有链接
        
        Args:
            content: 文档内容
            file_path: 文件路径
            
        Returns:
            链接列表
        """
        links = []
        
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            link_text = match[0]
            link_url = match[1]
            
            link_info = {
                'text': link_text,
                'url': link_url,
                'source_file': str(file_path),
                'type': self._classify_link(link_url),
                'depth': self._calculate_depth(link_url),
            }
            
            links.append(link_info)
        
        return links
    
    def _classify_link(self, url: str) -> str:
        """
        分类链接类型
        
        Args:
            url: 链接URL
            
        Returns:
            链接类型（internal/external）
        """
        if url.startswith('http://') or url.startswith('https://'):
            return 'external'
        else:
            return 'internal'
    
    def _calculate_depth(self, url: str) -> int:
        """
        计算路径层级
        
        Args:
            url: 链接URL
            
        Returns:
            路径层级（../的数量）
        """
        if url.startswith('http://') or url.startswith('https://'):
            return 0
        
        depth = 0
        parts = url.split('/')
        
        for part in parts:
            if part == '..':
                depth += 1
        
        return depth
    
    def check_internal_links(self) -> List[Dict]:
        """
        检查内部链接有效性
        
        Returns:
            失效的内部链接列表
        """
        broken_links = []
        
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                if link['type'] == 'internal':
                    target_path = self._resolve_link(link['url'], doc_path)
                    
                    if not target_path or not target_path.exists():
                        broken_links.append({
                            'source_file': doc_path,
                            'link_text': link['text'],
                            'link_url': link['url'],
                            'type': 'broken_internal',
                            'severity': 'P0',
                            'description': f'内部链接失效: {link["url"]}',
                        })
        
        return broken_links
    
    def _resolve_link(self, url: str, source_file: str) -> Path:
        """
        解析链接路径
        
        Args:
            url: 链接URL
            source_file: 源文件路径
            
        Returns:
            目标文件路径
        """
        if url.startswith('http://') or url.startswith('https://'):
            return None
        
        if '#' in url:
            url = url.split('#')[0]
        
        if not url:
            return None
        
        source_dir = Path(source_file).parent
        target_path = (source_dir / url).resolve()
        
        return target_path
    
    def check_external_links(self, max_workers: int = 10) -> List[Dict]:
        """
        检查外部链接可访问性
        
        Args:
            max_workers: 最大并发数
            
        Returns:
            失效的外部链接列表
        """
        broken_links = []
        external_links = []
        
        seen_urls = set()  # Track already checked URLs
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                if link['type'] == 'external':
                    # Skip special URL schemes that don't need HTTP checking
                    if link['url'].startswith(('mailto:', 'tel:', 'ftp:')):
                        continue
                    # Skip duplicate URLs to avoid redundant checks
                    if link['url'] in seen_urls:
                        continue
                    seen_urls.add(link['url'])
                    external_links.append({
                        'source_file': doc_path,
                        'link_text': link['text'],
                        'link_url': link['url'],
                    })
        
        print(f"检查 {len(external_links)} 个外部链接...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {
                executor.submit(self._check_url, link['link_url']): link
                for link in external_links
            }
            
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    is_accessible = future.result()
                    if not is_accessible:
                        broken_links.append({
                            'source_file': link['source_file'],
                            'link_text': link['text'],
                            'link_url': link['link_url'],
                            'type': 'broken_external',
                            'severity': 'P1',
                            'description': f'外部链接不可访问: {link["link_url"]}',
                        })
                except Exception as e:
                    broken_links.append({
                        'source_file': link['source_file'],
                        'link_text': link['text'],
                        'link_url': link['link_url'],
                        'type': 'broken_external',
                        'severity': 'P1',
                        'description': f'外部链接检查失败: {link["link_url"]} - {str(e)}',
                    })
        
        return broken_links
    
    def _check_url(self, url: str) -> bool:
        """
        检查URL是否可访问
        
        Args:
            url: URL
            
        Returns:
            是否可访问
        """
        try:
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False
    
    def check_depth_violations(self) -> List[Dict]:
        """
        检查路径层级违规
        
        Returns:
            路径层级违规列表
        """
        violations = []
        
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                if link['type'] == 'internal' and link['depth'] > self.max_depth:
                    violations.append({
                        'source_file': doc_path,
                        'link_text': link['text'],
                        'link_url': link['url'],
                        'depth': link['depth'],
                        'type': 'depth_violation',
                        'severity': 'P2',
                        'description': f'路径层级超限: {link["depth"]}层 (最大允许{self.max_depth}层)',
                    })
        
        return violations
    
    def check_insecure_links(self) -> List[Dict]:
        """
        检查不安全链接
        
        Returns:
            不安全链接列表
        """
        insecure_links = []
        
        for doc_path, doc_info in self.documents.items():
            for link in doc_info['links']:
                if link['url'].startswith('http://'):
                    insecure_links.append({
                        'source_file': doc_path,
                        'link_text': link['text'],
                        'link_url': link['url'],
                        'type': 'insecure_link',
                        'severity': 'P1',
                        'description': f'使用不安全的HTTP链接: {link["url"]}',
                    })
        
        return insecure_links
    
    def run_checks(self) -> Dict:
        """
        运行所有检查
        
        Returns:
            检查结果
        """
        print("开始扫描文档...")
        doc_count = self.scan_documents()
        print(f"扫描完成，共发现 {doc_count} 个文档")
        
        print("\n检查内部链接...")
        broken_internal = self.check_internal_links()
        
        print("检查外部链接...")
        broken_external = self.check_external_links()
        
        print("检查路径层级...")
        depth_violations = self.check_depth_violations()
        
        print("检查安全链接...")
        insecure_links = self.check_insecure_links()
        
        results = {
            'scan_info': {
                'docs_dir': str(self.docs_dir),
                'max_depth': self.max_depth,
                'total_documents': doc_count,
            },
            'broken_internal_links': broken_internal,
            'broken_external_links': broken_external,
            'depth_violations': depth_violations,
            'insecure_links': insecure_links,
            'summary': {
                'total_issues': (
                    len(broken_internal) +
                    len(broken_external) +
                    len(depth_violations) +
                    len(insecure_links)
                ),
                'p0_issues': len(broken_internal),
                'p1_issues': len(broken_external) + len(insecure_links),
                'p2_issues': len(depth_violations),
            },
        }
        
        return results
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """
        生成检查报告
        
        Args:
            results: 检查结果
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        report_lines = []
        report_lines.append("# 链接检查报告")
        report_lines.append("")
        report_lines.append(f"**检查时间**: 2026-04-03")
        report_lines.append(f"**检查范围**: {results['scan_info']['docs_dir']}")
        report_lines.append(f"**最大路径层级**: {results['scan_info']['max_depth']}")
        report_lines.append(f"**文档总数**: {results['scan_info']['total_documents']}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        report_lines.append("## 📊 检查结果概览")
        report_lines.append("")
        report_lines.append(f"- **总问题数**: {results['summary']['total_issues']}")
        report_lines.append(f"- **P0级问题**: {results['summary']['p0_issues']}")
        report_lines.append(f"- **P1级问题**: {results['summary']['p1_issues']}")
        report_lines.append(f"- **P2级问题**: {results['summary']['p2_issues']}")
        report_lines.append("")
        
        if results['broken_internal_links']:
            report_lines.append("## 🔴 内部链接失效")
            report_lines.append("")
            for link in results['broken_internal_links']:
                report_lines.append(f"### {link['link_text']}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {link['severity']}")
                report_lines.append(f"**问题描述**: {link['description']}")
                report_lines.append(f"**源文件**: `{link['source_file']}`")
                report_lines.append(f"**链接URL**: `{link['link_url']}`")
                report_lines.append("")
        
        if results['broken_external_links']:
            report_lines.append("## 🟡 外部链接失效")
            report_lines.append("")
            for link in results['broken_external_links']:
                report_lines.append(f"### {link['link_text']}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {link['severity']}")
                report_lines.append(f"**问题描述**: {link['description']}")
                report_lines.append(f"**源文件**: `{link['source_file']}`")
                report_lines.append(f"**链接URL**: `{link['link_url']}`")
                report_lines.append("")
        
        if results['depth_violations']:
            report_lines.append("## 🟢 路径层级超限")
            report_lines.append("")
            for link in results['depth_violations']:
                report_lines.append(f"### {link['link_text']}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {link['severity']}")
                report_lines.append(f"**问题描述**: {link['description']}")
                report_lines.append(f"**源文件**: `{link['source_file']}`")
                report_lines.append(f"**链接URL**: `{link['link_url']}`")
                report_lines.append("")
        
        if results['insecure_links']:
            report_lines.append("## 🟡 不安全链接")
            report_lines.append("")
            for link in results['insecure_links']:
                report_lines.append(f"### {link['link_text']}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {link['severity']}")
                report_lines.append(f"**问题描述**: {link['description']}")
                report_lines.append(f"**源文件**: `{link['source_file']}`")
                report_lines.append(f"**链接URL**: `{link['link_url']}`")
                report_lines.append("")
        
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("**检查工具**: link_checker.py v1.0.0")
        report_lines.append("**检查日期**: 2026-04-03")
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n报告已保存到: {output_file}")
        
        return report_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='链接检查器')
    parser.add_argument('--dir', default='docs', help='文档目录路径')
    parser.add_argument('--doc', help='检查单个文档')
    parser.add_argument('--all', action='store_true', help='检查全系统')
    parser.add_argument('--max-depth', type=int, default=3, help='最大允许的路径层级')
    parser.add_argument('--timeout', type=int, default=5, help='外部链接超时时间（秒）')
    parser.add_argument('--output', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    if args.doc:
        docs_dir = str(Path(args.doc).parent)
        checker = LinkChecker(docs_dir, args.max_depth, args.timeout)
        results = checker.run_checks()
    elif args.all:
        checker = LinkChecker('docs', args.max_depth, args.timeout)
        results = checker.run_checks()
    else:
        checker = LinkChecker(args.dir, args.max_depth, args.timeout)
        results = checker.run_checks()
    
    report = checker.generate_report(results, args.output)
    print("\n" + report)


if __name__ == '__main__':
    main()
