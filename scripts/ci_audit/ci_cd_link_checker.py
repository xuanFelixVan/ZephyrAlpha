#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
CI/CD 文档链接检查器
用于GitHub Actions工作流中检查文档链接有效性
"""

import re
import json
from pathlib import Path
from datetime import datetime

class CICDLinkChecker:
    def __init__(self):
        self.docs_root = Path('docs')
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'skipped_links': 0,
            'errors': []
        }

    def build_file_index(self):
        """构建文件索引"""
        file_index = {}

        if not self.docs_root.exists():
            print("❌ docs目录不存在")
            return file_index

        for md_file in self.docs_root.rglob('*.md'):
            rel_path = str(md_file.relative_to(self.docs_root)).replace('\\', '/')
            file_index[rel_path.lower()] = rel_path
            file_index[md_file.name.lower()] = rel_path

        return file_index

    def check_all_links(self):
        """检查所有文档链接"""
        print("🔍 开始检查文档链接...")

        file_index = self.build_file_index()

        if not file_index:
            print("❌ 没有找到任何Markdown文件")
            return

        md_files = list(self.docs_root.rglob('*.md'))
        self.results['total_files'] = len(md_files)

        print(f"📄 扫描 {len(md_files)} 个文件...")

        for i, md_file in enumerate(md_files, 1):
            if i % 100 == 0:
                print(f"  进度: {i}/{len(md_files)} ({i/len(md_files)*100:.1f}%)")

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue

            source_file = str(md_file.relative_to(self.docs_root)).replace('\\', '/')
            source_dir = str(md_file.parent.relative_to(self.docs_root)).replace('\\', '/')

            # 匹配markdown链接
            link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

            for match in link_pattern.finditer(content):
                link_text = match.group(1)
                link_url = match.group(2).strip()

                # 跳过非文件链接
                if link_url.startswith(('http://', 'https://', 'mailto:', '#', 'tel:')):
                    self.results['skipped_links'] += 1
                    continue

                self.results['total_links'] += 1

                # 解析链接路径
                if link_url.startswith('./') or link_url.startswith('../'):
                    try:
                        raw_path = Path(source_dir) / link_url
                        # 跳过路径过长的情况（Windows 260字符限制）
                        if len(str(raw_path)) > 240:
                            self.results['skipped_links'] += 1
                            self.results['total_links'] -= 1
                            continue
                        # 使用 resolve() 但确保与 docs_root 同为绝对路径
                        docs_root_resolved = self.docs_root.resolve()
                        target_path = raw_path.resolve()
                        target_rel = str(target_path.relative_to(docs_root_resolved)).replace('\\', '/')
                    except (ValueError, OSError):
                        # resolve 失败时，尝试纯字符串路径规范化
                        try:
                            normalized = str(Path(source_dir) / link_url).replace('\\', '/')
                            # 去除 ./ 和 ../ 的纯字符串规范化
                            parts = normalized.split('/')
                            resolved_parts = []
                            for part in parts:
                                if part == '..':
                                    if resolved_parts:
                                        resolved_parts.pop()
                                elif part and part != '.':
                                    resolved_parts.append(part)
                            target_rel = '/'.join(resolved_parts)
                        except Exception:
                            target_rel = link_url
                else:
                    target_rel = link_url

                # 检查文件是否存在
                target_file = self.docs_root / target_rel

                possible_paths = [
                    target_file,
                    self.docs_root / target_rel.lstrip('./'),
                    self.docs_root / (target_rel + '.md'),
                    self.docs_root / (target_rel.rstrip('/') + '.md'),
                    self.docs_root / (target_rel + '/INDEX.md'),
                    self.docs_root / (target_rel + '/index.md'),
                ]

                exists = any(p.exists() for p in possible_paths)

                if exists:
                    self.results['valid_links'] += 1
                else:
                    self.results['invalid_links'] += 1
                    line_number = content[:match.start()].count('\n') + 1
                    self.results['errors'].append({
                        'file': source_file,
                        'line': line_number,
                        'text': link_text,
                        'url': link_url
                    })

    def generate_report(self):
        """生成检查报告"""
        output_dir = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d')
        report_file = output_dir / f'CI_CD_LINK_CHECK_{timestamp}.md'
        json_file = output_dir / f'CI_CD_LINK_CHECK_{timestamp}.json'

        # 生成Markdown报告
        report_lines = [
            "# CI/CD 文档链接检查报告",
            "",
            f"> **检查时间**: {self.results['scan_time']}",
            "",
            "## 📊 检查统计",
            "",
            f"- **扫描文件数**: {self.results['total_files']}",
            f"- **总链接数**: {self.results['total_links']}",
            f"- **有效链接数**: {self.results['valid_links']}",
            f"- **无效链接数**: {self.results['invalid_links']}",
            f"- **跳过链接数**: {self.results['skipped_links']}",
            f"- **有效率**: {self.results['valid_links'] / max(self.results['total_links'], 1) * 100:.2f}%",
            ""
        ]

        if self.results['errors']:
            report_lines.extend([
                "## ❌ 无效链接详情（前50个）",
                "",
                "| 文件 | 行号 | 链接文本 | 链接URL |",
                "|------|------|---------|---------|"
            ])

            for error in self.results['errors'][:50]:
                report_lines.append(
                    f"| {error['file']} | {error['line']} | {error['text']} | {error['url']} |"
                )

            report_lines.extend([
                "",
                f"**总计**: {len(self.results['errors'])} 个无效链接",
                ""
            ])

        report_lines.extend([
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        # 保存JSON结果
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 报告已生成: {report_file}")
        print(f"✅ JSON已保存: {json_file}")

        return report_file

    def run(self):
        """运行检查"""
        print("=" * 60)
        print("CI/CD 文档链接检查器")
        print("=" * 60)

        self.check_all_links()

        print("\n" + "=" * 60)
        print("检查完成!")
        print("=" * 60)
        print(f"扫描文件数: {self.results['total_files']}")
        print(f"总链接数: {self.results['total_links']}")
        print(f"有效链接数: {self.results['valid_links']}")
        print(f"无效链接数: {self.results['invalid_links']}")
        print(f"有效率: {self.results['valid_links'] / max(self.results['total_links'], 1) * 100:.2f}%")

        self.generate_report()

        # 返回退出码
        if self.results['invalid_links'] > 0:
            print(f"\n⚠️  发现 {self.results['invalid_links']} 个无效链接")
            return 1
        else:
            print("\n✅ 所有链接检查通过!")
            return 0

if __name__ == '__main__':
    import sys
    checker = CICDLinkChecker()
    sys.exit(checker.run())
