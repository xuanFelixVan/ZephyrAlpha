# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
duplicate_detector.py - 重复文档检测器

模块ID: DUPLICATE_DETECTOR_001
版本: v1.0.0
创建日期: 2026-04-03

核心功能:
1. 基于文档内容相似度检测重复文档
2. 基于module_id检测重复标识
3. 基于职责描述检测职责重叠
4. 生成重复文档检测报告

使用方式:
    python scripts/duplicate_detector.py --dir docs/ --threshold 0.8
    python scripts/duplicate_detector.py --doc docs/PATH/TO/DOC.md
    python scripts/duplicate_detector.py --all
"""

import os
import re
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from difflib import SequenceMatcher


class DuplicateDetector:
    """重复文档检测器"""

    def __init__(self, docs_dir: str = "docs", threshold: float = 0.8):
        """
        初始化重复文档检测器

        Args:
            docs_dir: 文档目录路径
            threshold: 相似度阈值（0.0-1.0）
        """
        self.docs_dir = Path(docs_dir)
        self.threshold = threshold
        self.documents: Dict[str, Dict] = {}
        self.duplicates: List[Dict] = []
        self.module_id_map: Dict[str, List[str]] = defaultdict(list)

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
            "06_ARCHIVE",
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
                'content_hash': self._compute_hash(content),
                'module_id': self._extract_module_id(content),
                'title': self._extract_title(content),
                'responsibilities': self._extract_responsibilities(content),
                'size': len(content),
                'lines': content.count('\n') + 1,
            }

            return doc_info

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def _compute_hash(self, content: str) -> str:
        """
        计算内容哈希值

        Args:
            content: 文档内容

        Returns:
            哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _extract_module_id(self, content: str) -> str:
        """
        提取module_id

        Args:
            content: 文档内容

        Returns:
            module_id
        """
        pattern = r'module_id:\s*(\S+)'
        match = re.search(pattern, content)
        return match.group(1) if match else None

    def _extract_title(self, content: str) -> str:
        """
        提取文档标题

        Args:
            content: 文档内容

        Returns:
            文档标题
        """
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def _extract_responsibilities(self, content: str) -> List[str]:
        """
        提取职责描述

        Args:
            content: 文档内容

        Returns:
            职责描述列表
        """
        responsibilities = []

        patterns = [
            r'\*\*本文档职责\*\*:\s*(.+)',
            r'\*\*职责\*\*:\s*(.+)',
            r'核心功能:\s*(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            responsibilities.extend(matches)

        return responsibilities

    def detect_module_id_duplicates(self) -> List[Dict]:
        """
        检测module_id重复

        Returns:
            重复的module_id列表
        """
        duplicates = []

        for doc_path, doc_info in self.documents.items():
            module_id = doc_info.get('module_id')
            if module_id:
                self.module_id_map[module_id].append(doc_path)

        for module_id, doc_paths in self.module_id_map.items():
            if len(doc_paths) > 1:
                duplicates.append({
                    'type': 'module_id_duplicate',
                    'module_id': module_id,
                    'documents': doc_paths,
                    'severity': 'P0',
                    'description': f'发现{len(doc_paths)}个文档使用相同的module_id: {module_id}',
                })

        return duplicates

    def detect_content_duplicates(self) -> List[Dict]:
        """
        检测内容重复

        Returns:
            重复的内容列表
        """
        duplicates = []
        content_map: Dict[str, List[str]] = defaultdict(list)

        for doc_path, doc_info in self.documents.items():
            content_hash = doc_info.get('content_hash')
            if content_hash:
                content_map[content_hash].append(doc_path)

        for content_hash, doc_paths in content_map.items():
            if len(doc_paths) > 1:
                duplicates.append({
                    'type': 'content_duplicate',
                    'content_hash': content_hash,
                    'documents': doc_paths,
                    'severity': 'P0',
                    'description': f'发现{len(doc_paths)}个文档内容完全相同',
                })

        return duplicates

    def detect_similarity_duplicates(self) -> List[Dict]:
        """
        检测相似度重复

        Returns:
            相似度重复列表
        """
        duplicates = []
        doc_paths = list(self.documents.keys())

        for i in range(len(doc_paths)):
            for j in range(i + 1, len(doc_paths)):
                doc1_path = doc_paths[i]
                doc2_path = doc_paths[j]

                doc1_info = self.documents[doc1_path]
                doc2_info = self.documents[doc2_path]

                similarity = self._compute_similarity(
                    doc1_info['content'],
                    doc2_info['content']
                )

                if similarity >= self.threshold:
                    duplicates.append({
                        'type': 'similarity_duplicate',
                        'doc1': doc1_path,
                        'doc2': doc2_path,
                        'similarity': similarity,
                        'severity': 'P1' if similarity >= 0.9 else 'P2',
                        'description': f'文档相似度: {similarity:.2%}',
                    })

        return duplicates

    def _compute_similarity(self, content1: str, content2: str) -> float:
        """
        计算两个文档的相似度

        Args:
            content1: 文档1内容
            content2: 文档2内容

        Returns:
            相似度（0.0-1.0）
        """
        if not content1 or not content2:
            return 0.0

        max_len = max(len(content1), len(content2))
        if max_len == 0:
            return 1.0

        if max_len > 10000:
            content1 = content1[:5000]
            content2 = content2[:5000]

        return SequenceMatcher(None, content1, content2).ratio()

    def detect_responsibility_overlap(self) -> List[Dict]:
        """
        检测职责重叠

        Returns:
            职责重叠列表
        """
        overlaps = []
        doc_paths = list(self.documents.keys())

        for i in range(len(doc_paths)):
            for j in range(i + 1, len(doc_paths)):
                doc1_path = doc_paths[i]
                doc2_path = doc_paths[j]

                doc1_info = self.documents[doc1_path]
                doc2_info = self.documents[doc2_path]

                resp1 = doc1_info.get('responsibilities', [])
                resp2 = doc2_info.get('responsibilities', [])

                if resp1 and resp2:
                    overlap_score = self._compute_responsibility_overlap(resp1, resp2)

                    if overlap_score >= self.threshold:
                        overlaps.append({
                            'type': 'responsibility_overlap',
                            'doc1': doc1_path,
                            'doc2': doc2_path,
                            'overlap_score': overlap_score,
                            'severity': 'P1',
                            'description': f'职责重叠度: {overlap_score:.2%}',
                            'doc1_responsibilities': resp1,
                            'doc2_responsibilities': resp2,
                        })

        return overlaps

    def _compute_responsibility_overlap(self, resp1: List[str], resp2: List[str]) -> float:
        """
        计算职责重叠度

        Args:
            resp1: 职责列表1
            resp2: 职责列表2

        Returns:
            重叠度（0.0-1.0）
        """
        if not resp1 or not resp2:
            return 0.0

        total_overlap = 0.0
        for r1 in resp1:
            max_sim = 0.0
            for r2 in resp2:
                sim = SequenceMatcher(None, r1, r2).ratio()
                max_sim = max(max_sim, sim)
            total_overlap += max_sim

        return total_overlap / len(resp1)

    def run_detection(self) -> Dict:
        """
        运行重复检测

        Returns:
            检测结果
        """
        print("开始扫描文档...")
        doc_count = self.scan_documents()
        print(f"扫描完成，共发现 {doc_count} 个文档")

        print("\n检测module_id重复...")
        module_id_duplicates = self.detect_module_id_duplicates()

        print("检测内容重复...")
        content_duplicates = self.detect_content_duplicates()

        print("检测相似度重复...")
        similarity_duplicates = self.detect_similarity_duplicates()

        print("检测职责重叠...")
        responsibility_overlaps = self.detect_responsibility_overlap()

        results = {
            'scan_info': {
                'docs_dir': str(self.docs_dir),
                'threshold': self.threshold,
                'total_documents': doc_count,
            },
            'module_id_duplicates': module_id_duplicates,
            'content_duplicates': content_duplicates,
            'similarity_duplicates': similarity_duplicates,
            'responsibility_overlaps': responsibility_overlaps,
            'summary': {
                'total_issues': (
                    len(module_id_duplicates) +
                    len(content_duplicates) +
                    len(similarity_duplicates) +
                    len(responsibility_overlaps)
                ),
                'p0_issues': (
                    len(module_id_duplicates) +
                    len(content_duplicates)
                ),
                'p1_issues': (
                    len([d for d in similarity_duplicates if d['severity'] == 'P1']) +
                    len(responsibility_overlaps)
                ),
                'p2_issues': len([d for d in similarity_duplicates if d['severity'] == 'P2']),
            },
        }

        return results

    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """
        生成检测报告

        Args:
            results: 检测结果
            output_file: 输出文件路径

        Returns:
            报告内容
        """
        report_lines = []
        report_lines.append("# 重复文档检测报告")
        report_lines.append("")
        report_lines.append(f"**检测时间**: 2026-04-03")
        report_lines.append(f"**检测范围**: {results['scan_info']['docs_dir']}")
        report_lines.append(f"**相似度阈值**: {results['scan_info']['threshold']}")
        report_lines.append(f"**文档总数**: {results['scan_info']['total_documents']}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        report_lines.append("## 📊 检测结果概览")
        report_lines.append("")
        report_lines.append(f"- **总问题数**: {results['summary']['total_issues']}")
        report_lines.append(f"- **P0级问题**: {results['summary']['p0_issues']}")
        report_lines.append(f"- **P1级问题**: {results['summary']['p1_issues']}")
        report_lines.append(f"- **P2级问题**: {results['summary']['p2_issues']}")
        report_lines.append("")

        if results['module_id_duplicates']:
            report_lines.append("## 🔴 module_id重复")
            report_lines.append("")
            for dup in results['module_id_duplicates']:
                report_lines.append(f"### {dup['module_id']}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {dup['severity']}")
                report_lines.append(f"**问题描述**: {dup['description']}")
                report_lines.append("")
                report_lines.append("**重复文档**:")
                for doc in dup['documents']:
                    report_lines.append(f"- `{doc}`")
                report_lines.append("")

        if results['content_duplicates']:
            report_lines.append("## 🔴 内容完全重复")
            report_lines.append("")
            for dup in results['content_duplicates']:
                report_lines.append(f"### 内容哈希: {dup['content_hash'][:16]}...")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {dup['severity']}")
                report_lines.append(f"**问题描述**: {dup['description']}")
                report_lines.append("")
                report_lines.append("**重复文档**:")
                for doc in dup['documents']:
                    report_lines.append(f"- `{doc}`")
                report_lines.append("")

        if results['similarity_duplicates']:
            report_lines.append("## 🟡 相似度重复")
            report_lines.append("")
            for dup in results['similarity_duplicates']:
                report_lines.append(f"### 相似度: {dup['similarity']:.2%}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {dup['severity']}")
                report_lines.append(f"**问题描述**: {dup['description']}")
                report_lines.append("")
                report_lines.append(f"- 文档1: `{dup['doc1']}`")
                report_lines.append(f"- 文档2: `{dup['doc2']}`")
                report_lines.append("")

        if results['responsibility_overlaps']:
            report_lines.append("## 🟡 职责重叠")
            report_lines.append("")
            for overlap in results['responsibility_overlaps']:
                report_lines.append(f"### 重叠度: {overlap['overlap_score']:.2%}")
                report_lines.append("")
                report_lines.append(f"**问题等级**: {overlap['severity']}")
                report_lines.append(f"**问题描述**: {overlap['description']}")
                report_lines.append("")
                report_lines.append(f"- 文档1: `{overlap['doc1']}`")
                report_lines.append(f"- 文档2: `{overlap['doc2']}`")
                report_lines.append("")

        report_lines.append("---")
        report_lines.append("")
        report_lines.append("**检测工具**: duplicate_detector.py v1.0.0")
        report_lines.append("**检测日期**: 2026-04-03")

        report_content = '\n'.join(report_lines)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n报告已保存到: {output_file}")

        return report_content


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='重复文档检测器')
    parser.add_argument('--dir', default='docs', help='文档目录路径')
    parser.add_argument('--doc', help='检测单个文档')
    parser.add_argument('--all', action='store_true', help='检测全系统')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值')
    parser.add_argument('--output', help='输出报告文件路径')

    args = parser.parse_args()

    if args.doc:
        docs_dir = str(Path(args.doc).parent)
        detector = DuplicateDetector(docs_dir, args.threshold)
        results = detector.run_detection()
    elif args.all:
        detector = DuplicateDetector('docs', args.threshold)
        results = detector.run_detection()
    else:
        detector = DuplicateDetector(args.dir, args.threshold)
        results = detector.run_detection()

    report = detector.generate_report(results, args.output)
    print("\n" + report)


if __name__ == '__main__':
    main()
