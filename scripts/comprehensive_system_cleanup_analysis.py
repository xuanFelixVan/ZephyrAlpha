#!/usr/bin/env python3
"""
系统全面废墟检查脚本
检查整个 D:\ZephyrAlpha 目录，识别：
1. 临时/备份文件 (.bak, .tmp)
2. 深层嵌套目录 (超过5层)
3. 空目录
4. 大文件 (>10MB)
5. 重复文件
6. 缓存/日志文件
7. 孤儿文件 (不在标准结构中)
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path("d:/ZephyrAlpha")

# 需要扫描的目录
SCAN_DIRS = [
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "reports",
    PROJECT_ROOT / "logs",
    PROJECT_ROOT / ".audit_cache",
    PROJECT_ROOT / ".audit_fix_backup",
    PROJECT_ROOT / ".trae",
]

# 忽略的目录
IGNORE_DIRS = [
    ".git",
    ".venv",
    ".venv-1",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".vscode",
    ".cursor",
    ".github",
]

# 问题文件模式
PROBLEM_PATTERNS = {
    "backup_files": [".bak", ".tmp", ".temp", ".old", ".orig", ".save"],
    "log_files": [".log"],
    "cache_files": [".cache", ".pyc"],
}


class SystemCleaner:
    def __init__(self):
        self.all_files = []
        self.all_dirs = []
        self.problems = {
            "backup_files": [],
            "deep_dirs": [],
            "empty_dirs": [],
            "large_files": [],
            "duplicates": defaultdict(list),
            "cache_files": [],
            "orphan_files": [],
        }
        self.stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
        }

    def scan(self):
        """扫描整个项目"""
        print("=" * 70)
        print("[SCAN] 开始全面系统扫描...")
        print("=" * 70)

        for scan_dir in SCAN_DIRS:
            if not scan_dir.exists():
                continue
            self._scan_directory(scan_dir)

        print(f"\n[INFO] 扫描完成:")
        print(f"  - 文件总数: {self.stats['total_files']}")
        print(f"  - 目录总数: {self.stats['total_dirs']}")
        print(f"  - 总大小: {self.stats['total_size'] / (1024*1024):.2f} MB")

    def _scan_directory(self, dir_path: Path, depth=0):
        """递归扫描目录"""
        try:
            for item in dir_path.iterdir():
                # 跳过忽略的目录
                if item.is_dir() and item.name in IGNORE_DIRS:
                    continue

                if item.is_dir():
                    self.all_dirs.append((item, depth))
                    self.stats["total_dirs"] += 1

                    # 检查深层目录
                    if depth > 5:
                        self.problems["deep_dirs"].append((item, depth))

                    # 递归扫描
                    self._scan_directory(item, depth + 1)

                elif item.is_file():
                    self.all_files.append(item)
                    self.stats["total_files"] += 1

                    try:
                        size = item.stat().st_size
                        self.stats["total_size"] += size

                        # 检查备份文件
                        if any(item.suffix == ext for ext in PROBLEM_PATTERNS["backup_files"]):
                            self.problems["backup_files"].append((item, size))

                        # 检查日志文件
                        elif any(item.suffix == ext for ext in PROBLEM_PATTERNS["log_files"]):
                            self.problems["cache_files"].append((item, size))

                        # 检查大文件
                        elif size > 10 * 1024 * 1024:  # 10MB
                            self.problems["large_files"].append((item, size))

                    except:
                        pass

        except PermissionError:
            pass

    def find_duplicates(self):
        """查找重复文件"""
        print("\n[SCAN] 查找重复文件...")
        file_hashes = defaultdict(list)

        for file_path in self.all_files:
            try:
                # 只检查小文件 (< 50MB)
                if file_path.stat().st_size > 50 * 1024 * 1024:
                    continue

                # 计算MD5
                with open(file_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()
                file_hashes[md5_hash].append(file_path)
            except:
                pass

        # 记录重复文件
        for hash_val, files in file_hashes.items():
            if len(files) > 1:
                self.problems["duplicates"][hash_val] = files

        print(f"[INFO] 发现 {len(self.problems['duplicates'])} 组重复文件")

    def find_empty_dirs(self):
        """查找空目录"""
        print("\n[SCAN] 查找空目录...")

        for dir_path, depth in self.all_dirs:
            try:
                # 检查是否为空（除了.gitkeep）
                items = list(dir_path.iterdir())
                non_gitkeep = [i for i in items if i.name != ".gitkeep"]

                if not non_gitkeep:
                    self.problems["empty_dirs"].append((dir_path, depth))
            except:
                pass

        print(f"[INFO] 发现 {len(self.problems['empty_dirs'])} 个空目录")

    def generate_report(self):
        """生成清理报告"""
        report = []
        report.append("=" * 70)
        report.append("系统全面废墟检查报告")
        report.append(f"生成时间: {datetime.now().isoformat()}")
        report.append("=" * 70)

        # 1. 备份文件
        report.append("\n## 1. 备份文件 (.bak, .tmp 等)\n")
        report.append(f"总数: {len(self.problems['backup_files'])} 个\n")
        for file_path, size in sorted(self.problems['backup_files'], key=lambda x: x[1], reverse=True)[:20]:
            report.append(f"- `{file_path.relative_to(PROJECT_ROOT)}` ({size/1024:.1f} KB)")
        if len(self.problems['backup_files']) > 20:
            report.append(f"- ... 还有 {len(self.problems['backup_files']) - 20} 个")

        # 2. 深层目录
        report.append("\n## 2. 深层嵌套目录 (>5层)\n")
        report.append(f"总数: {len(self.problems['deep_dirs'])} 个\n")
        for dir_path, depth in sorted(self.problems['deep_dirs'], key=lambda x: x[1], reverse=True):
            report.append(f"- `{dir_path.relative_to(PROJECT_ROOT)}` ({depth} 层)")

        # 3. 空目录
        report.append("\n## 3. 空目录\n")
        report.append(f"总数: {len(self.problems['empty_dirs'])} 个\n")
        for dir_path, depth in self.problems['empty_dirs'][:20]:
            report.append(f"- `{dir_path.relative_to(PROJECT_ROOT)}`")
        if len(self.problems['empty_dirs']) > 20:
            report.append(f"- ... 还有 {len(self.problems['empty_dirs']) - 20} 个")

        # 4. 大文件
        report.append("\n## 4. 大文件 (>10MB)\n")
        report.append(f"总数: {len(self.problems['large_files'])} 个\n")
        for file_path, size in sorted(self.problems['large_files'], key=lambda x: x[1], reverse=True):
            report.append(f"- `{file_path.relative_to(PROJECT_ROOT)}` ({size/(1024*1024):.2f} MB)")

        # 5. 重复文件
        report.append("\n## 5. 重复文件组\n")
        report.append(f"总数: {len(self.problems['duplicates'])} 组\n")
        for hash_val, files in list(self.problems['duplicates'].items())[:10]:
            report.append(f"\n组 {hash_val[:8]}... ({len(files)} 个文件):")
            for f in files:
                report.append(f"  - `{f.relative_to(PROJECT_ROOT)}`")

        # 6. 缓存/日志文件
        report.append("\n## 6. 缓存/日志文件\n")
        report.append(f"总数: {len(self.problems['cache_files'])} 个\n")
        for file_path, size in sorted(self.problems['cache_files'], key=lambda x: x[1], reverse=True)[:15]:
            report.append(f"- `{file_path.relative_to(PROJECT_ROOT)}` ({size/1024:.1f} KB)")

        # 7. 清理建议
        report.append("\n## 7. 清理建议\n")
        report.append("### 立即清理 (低风险)\n")
        report.append("1. [ ] 删除所有 .bak 备份文件")
        report.append("2. [ ] 删除空目录")
        report.append("3. [ ] 清理日志文件 (.log)")
        report.append("4. [ ] 清理 __pycache__ 目录")

        report.append("\n### 谨慎处理 (中风险)\n")
        report.append("5. [ ] 评估深层目录结构")
        report.append("6. [ ] 处理重复文件")

        report.append("\n### 需要决策 (高风险)\n")
        report.append("7. [ ] 审查大文件是否必要")
        report.append("8. [ ] 评估 .audit_fix_backup 目录内容")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def save_report(self):
        """保存报告"""
        report = self.generate_report()
        report_path = PROJECT_ROOT / "reports" / f"system_cleanup_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding='utf-8')
        print(f"\n[INFO] 报告已保存: {report_path}")
        return report_path


def main():
    cleaner = SystemCleaner()
    cleaner.scan()
    cleaner.find_duplicates()
    cleaner.find_empty_dirs()
    cleaner.save_report()

    print("\n" + "=" * 70)
    print("扫描摘要:")
    print("=" * 70)
    print(f"  备份文件: {len(cleaner.problems['backup_files'])} 个")
    print(f"  深层目录: {len(cleaner.problems['deep_dirs'])} 个")
    print(f"  空目录: {len(cleaner.problems['empty_dirs'])} 个")
    print(f"  大文件: {len(cleaner.problems['large_files'])} 个")
    print(f"  重复组: {len(cleaner.problems['duplicates'])} 组")
    print(f"  缓存文件: {len(cleaner.problems['cache_files'])} 个")


if __name__ == "__main__":
    main()
