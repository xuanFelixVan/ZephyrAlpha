#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量链接修复脚本 (batch_fix_invalid_links_v2.py)

功能: 读取 CI/CD 链接检查报告，自动修复可修复的无效链接
策略:
  1. 文件存在但路径不对 → 修正路径
  2. 文件不存在但在归档区 → 标记为归档引用
  3. 文件不存在且无替代 → 移除链接（保留文本）
  4. 锚点链接问题 → 保留链接但标记
"""

import json
import re
import sys
import io
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class BatchLinkFixer:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.docs_root = self.workspace_root / "docs"
        self.report_file = self.docs_root / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state" / "CI_CD_LINK_CHECK_20260413.json"
        self.file_index = {}
        self.stats = {
            "total_invalid": 0,
            "path_fixed": 0,
            "link_removed": 0,
            "anchor_stripped": 0,
            "skipped": 0,
            "files_modified": 0,
        }

    def build_file_index(self):
        """构建全文件索引（小写路径 → 实际路径）"""
        print("== 构建文件索引...")
        for md_file in self.docs_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.docs_root)).replace("\\", "/")
            self.file_index[rel_path.lower()] = rel_path
            self.file_index[md_file.name.lower()] = rel_path
        print(f"   索引文件数: {len(self.file_index)}")

    def find_alternative_path(self, url: str) -> str:
        """尝试为无效 URL 找到替代路径"""
        # 去除锚点
        clean_url = url.split("#")[0].rstrip("/")

        # 尝试直接查找文件名
        filename = Path(clean_url).name
        if filename.lower() in self.file_index:
            return self.file_index[filename.lower()]

        # 尝试去除前缀 ./ ../ 等
        stripped = re.sub(r'^(\.\./)+', '', clean_url)
        if stripped.lower() in self.file_index:
            return self.file_index[stripped.lower()]

        # 尝试仅用文件名
        if filename.lower() in self.file_index:
            return self.file_index[filename.lower()]

        return None

    def load_errors(self):
        """加载链接检查报告"""
        if not self.report_file.exists():
            print(f"!! 报告文件不存在: {self.report_file}")
            return []

        with open(self.report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors = data.get("errors", [])
        self.stats["total_invalid"] = len(errors)
        print(f"   无效链接总数: {len(errors)}")
        return errors

    def fix_links(self, dry_run: bool = True):
        """批量修复无效链接"""
        errors = self.load_errors()
        if not errors:
            return

        self.build_file_index()

        # 按源文件分组
        file_errors = {}
        for error in errors:
            source_file = error["file"]
            if source_file not in file_errors:
                file_errors[source_file] = []
            file_errors[source_file].append(error)

        print(f"\n== 需修复文件数: {len(file_errors)}")

        # 分析最常见的无效 URL
        url_counter = Counter(e["url"] for e in errors)
        print(f"\n== Top 10 无效 URL:")
        for url, count in url_counter.most_common(10):
            alt = self.find_alternative_path(url)
            status = f"-> {alt}" if alt else "NO ALT"
            print(f"   {count:4d}x {url[:80]}  [{status}]")

        if dry_run:
            print("\n!! DRY RUN 模式，不实际修改文件")
            # 统计可修复数量
            fixable = 0
            for url, count in url_counter.items():
                if self.find_alternative_path(url):
                    fixable += count
            print(f"   可通过路径修正修复: {fixable} 个链接")
            print(f"   需要其他处理: {self.stats['total_invalid'] - fixable} 个链接")
            return

        # 实际修复
        for source_file, file_error_list in file_errors.items():
            full_path = self.docs_root / source_file
            if not full_path.exists():
                continue

            try:
                with open(full_path, "r", encoding="utf-8-sig") as f:
                    content = f.read()
            except Exception:
                continue

            original_content = content
            source_dir = str(Path(source_file).parent).replace("\\", "/")

            for error in file_error_list:
                url = error["url"]
                text = error["text"]

                # 策略1: 尝试路径修正
                alt_path = self.find_alternative_path(url)
                if alt_path:
                    # 计算从源文件到目标的相对路径
                    try:
                        source_abs = (self.docs_root / source_dir).resolve()
                        target_abs = (self.docs_root / alt_path).resolve()
                        new_rel = str(target_abs.relative_to(source_abs)).replace("\\", "/")
                        if not new_rel.startswith("."):
                            new_rel = "./" + new_rel
                    except (ValueError, OSError):
                        new_rel = alt_path

                    # 替换链接
                    old_link = f"[{text}]({url})"
                    new_link = f"[{text}]({new_rel})"
                    content = content.replace(old_link, new_link)
                    if content != original_content:
                        self.stats["path_fixed"] += 1
                        continue

                # 策略2: 去除锚点后重试
                if "#" in url:
                    base_url = url.split("#")[0]
                    alt_path = self.find_alternative_path(base_url)
                    if alt_path:
                        try:
                            source_abs = (self.docs_root / source_dir).resolve()
                            target_abs = (self.docs_root / alt_path).resolve()
                            new_rel = str(target_abs.relative_to(source_abs)).replace("\\", "/")
                            if not new_rel.startswith("."):
                                new_rel = "./" + new_rel
                            anchor = url.split("#")[1]
                            new_url = f"{new_rel}#{anchor}"
                        except (ValueError, OSError):
                            new_url = alt_path

                        old_link = f"[{text}]({url})"
                        new_link = f"[{text}]({new_url})"
                        content = content.replace(old_link, new_link)
                        if content != original_content:
                            self.stats["anchor_stripped"] += 1
                            continue

                # 策略3: 移除无效链接，保留文本
                old_link = f"[{text}]({url})"
                new_link = text
                content = content.replace(old_link, new_link)
                if content != original_content:
                    self.stats["link_removed"] += 1

            # 写入修改
            if content != original_content:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stats["files_modified"] += 1

        print(f"\n== 修复完成:")
        print(f"   路径修正: {self.stats['path_fixed']}")
        print(f"   锚点修复: {self.stats['anchor_stripped']}")
        print(f"   链接移除: {self.stats['link_removed']}")
        print(f"   修改文件: {self.stats['files_modified']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="批量链接修复脚本")
    parser.add_argument("--dry-run", action="store_true", help="仅分析，不修改文件")
    parser.add_argument("--workspace", default=".", help="工作区根目录")
    args = parser.parse_args()

    fixer = BatchLinkFixer(args.workspace)
    fixer.fix_links(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
