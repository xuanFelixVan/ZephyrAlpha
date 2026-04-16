#!/usr/bin/env python3
"""
文件夹结构分析与修复脚本
策略: 原地修复 + 安全优先 + 可回滚

执行流程:
1. 分析阶段 - 只读扫描，生成完整报告
2. 评估阶段 - 确认哪些目录可以安全清理
3. 修复阶段 - 逐步执行，每次一步

使用:
    python scripts/analyze_and_fix_folder_structure.py --analyze-only
    python scripts/analyze_and_fix_folder_structure.py --dry-run
    python scripts/analyze_and_fix_folder_structure.py --execute
"""

import os
import re
import yaml
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# 项目根目录
PROJECT_ROOT = Path("d:/ZephyrAlpha")
DOCS_ROOT = PROJECT_ROOT / "docs"

# 标准目录结构定义（根据评估文档）
STANDARD_STRUCTURE = {
    "00_OVERVIEW": "系统总览 (Layer 0)",
    "00_RESOURCES": "资源文档 (Layer 0)",
    "01_FRAMEWORK": "框架设计 (Layer 1)",
    "02_FACTOR_LIBRARY": "因子库 (Layer 2)",
    "03_TRADING_TACTICS": "交易策略 (Layer 3, 5)",
    "04_EXECUTION": "执行引擎 (Layer 5, 6)",
    "05_IMPLEMENTATION": "实施指南",
    "06_ARCHIVE": "归档文档",
    "07_GOVERNANCE_COMPLIANCE": "治理与合规层 (Layer 10) - 需要创建",
    "08_AI_GOVERNANCE": "AI治理 (Layer 8子集)",
    "09_AUDIT": "系统治理审计",
    "10_AI_WORKFLOW": "AI工作流",
    "11_STRATEGIC_DECISION": "战略决策层 (Layer 11)",
}

# 已知需要清理的目录模式
INVALID_PATTERNS = [
    r"^- 层级$",           # 特殊字符开头
    r"^- 层级标识$",
    r"^'\[Layer\]'$",      # 引号包裹
    r"^'\[Layer定位\]'$",
    r"^01_'\[Layer\]'$",   # 混合模式
    r"^\d+_-$",            # 仅数字和下划线
    r"^\d+_Layer \d+ \(\)$",  # 空括号
    r"^\d+_layer_\d+_BAK\d+$",  # 备份目录
    r".*_BAK\d+$",         # 备份后缀
    r".*__BACKUP_.*$",      # 备份标记
    r"^\d+_l$",            # 短名称测试目录
    r"^\d+_la$",
    r"^\d+_lay$",
    r"^\d+_laye$",
    r"^\d+_layer_$",
    r"^Layer \d+ \(\)$",   # 无数字前缀的Layer
    r"^Layer \d+ \(.+\)$", # 带描述的Layer
    r"^Layer X.*$",         # Layer X 变体
    r"^layer_\d+$",         # 小写无数字前缀
    r"^layer_$",            # 不完整名称
    r"^舆情分析$",          # 中文孤立目录
    r"^l$",                 # 单字母
]


class FolderAnalyzer:
    """文件夹分析器"""

    def __init__(self):
        self.all_dirs: List[Path] = []
        self.standard_dirs: List[Path] = []
        self.invalid_dirs: List[Path] = []
        self.layer_dirs: List[Path] = []
        self.backup_dirs: List[Path] = []
        self.test_dirs: List[Path] = []
        self.empty_dirs: List[Path] = []
        self.file_stats: Dict[str, any] = {}

    def scan_all_directories(self) -> None:
        """扫描所有目录"""
        print("[SCAN] 扫描 docs/ 目录结构...")

        for item in DOCS_ROOT.iterdir():
            if item.is_dir():
                self.all_dirs.append(item)

        # 分类
        for dir_path in self.all_dirs:
            dir_name = dir_path.name

            # 检查是否为标准目录
            if dir_name in STANDARD_STRUCTURE:
                self.standard_dirs.append(dir_path)
            # 检查是否为备份目录
            elif any(re.match(pattern, dir_name) for pattern in INVALID_PATTERNS):
                if "BAK" in dir_name or "BACKUP" in dir_name:
                    self.backup_dirs.append(dir_path)
                elif re.match(r"^\d+_l[aey]?$", dir_name):
                    self.test_dirs.append(dir_path)
                else:
                    self.invalid_dirs.append(dir_path)
            # 检查是否为Layer相关
            elif "Layer" in dir_name or "layer" in dir_name.lower():
                self.layer_dirs.append(dir_path)
            else:
                self.invalid_dirs.append(dir_path)

        print(f"   [INFO] 总目录数: {len(self.all_dirs)}")
        print(f"   [OK]   标准目录: {len(self.standard_dirs)}")
        print(f"   [WARN] 无效目录: {len(self.invalid_dirs)}")
        print(f"   [INFO] Layer目录: {len(self.layer_dirs)}")
        print(f"   [INFO] 备份目录: {len(self.backup_dirs)}")
        print(f"   [INFO] 测试目录: {len(self.test_dirs)}")

    def analyze_file_content(self) -> Dict:
        """分析文件内容，统计MD5去重"""
        print("\n[ANALYZE] 分析文件内容...")

        md5_map: Dict[str, List[Path]] = defaultdict(list)
        total_files = 0
        total_size = 0

        for dir_path in self.all_dirs:
            for md_file in dir_path.rglob("*.md"):
                try:
                    content = md_file.read_bytes()
                    total_files += 1
                    total_size += len(content)

                    # 计算MD5
                    md5_hash = hashlib.md5(content).hexdigest()
                    md5_map[md5_hash].append(md_file)
                except Exception as e:
                    print(f"   [WARN] 无法读取 {md_file}: {e}")

        # 统计重复
        duplicates = {k: v for k, v in md5_map.items() if len(v) > 1}

        self.file_stats = {
            "total_files": total_files,
            "total_size_mb": total_size / (1024 * 1024),
            "unique_hashes": len(md5_map),
            "duplicate_hashes": len(duplicates),
            "duplicate_files": sum(len(v) - 1 for v in duplicates.values()),
            "duplicates": duplicates,
        }

        print(f"   [INFO] Markdown文件总数: {total_files}")
        print(f"   [INFO] 总大小: {self.file_stats['total_size_mb']:.2f} MB")
        print(f"   [INFO] 唯一内容数: {self.file_stats['unique_hashes']}")
        print(f"   [INFO] 重复组数: {self.file_stats['duplicate_hashes']}")
        print(f"   [WARN] 可去重文件数: {self.file_stats['duplicate_files']}")

        return self.file_stats

    def generate_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 70)
        report.append("文件夹结构分析报告")
        report.append(f"生成时间: {datetime.now().isoformat()}")
        report.append("=" * 70)

        # 目录统计
        report.append("\n## 1. 目录分类统计\n")
        report.append(f"- 标准目录: {len(self.standard_dirs)} 个")
        report.append(f"- 无效/混乱目录: {len(self.invalid_dirs)} 个")
        report.append(f"- Layer相关目录: {len(self.layer_dirs)} 个")
        report.append(f"- 备份目录: {len(self.backup_dirs)} 个")
        report.append(f"- 测试目录: {len(self.test_dirs)} 个")

        # 文件统计
        if self.file_stats:
            report.append("\n## 2. 文件内容统计\n")
            report.append(f"- Markdown文件总数: {self.file_stats['total_files']}")
            report.append(f"- 总大小: {self.file_stats['total_size_mb']:.2f} MB")
            report.append(f"- 唯一内容数: {self.file_stats['unique_hashes']}")
            report.append(f"- 重复组数: {self.file_stats['duplicate_hashes']}")
            report.append(f"- 可去重文件数: {self.file_stats['duplicate_files']}")

        # 问题目录清单
        report.append("\n## 3. 需要清理的目录清单\n")
        report.append("### 3.1 备份目录 (可安全删除)\n")
        for d in sorted(self.backup_dirs, key=lambda x: x.name):
            file_count = len(list(d.rglob("*.md")))
            report.append(f"- `{d.name}` ({file_count} 个文件)")

        report.append("\n### 3.2 测试目录 (可安全删除)\n")
        for d in sorted(self.test_dirs, key=lambda x: x.name):
            file_count = len(list(d.rglob("*.md")))
            report.append(f"- `{d.name}` ({file_count} 个文件)")

        report.append("\n### 3.3 无效命名目录 (需要评估)\n")
        for d in sorted(self.invalid_dirs, key=lambda x: x.name):
            file_count = len(list(d.rglob("*.md")))
            report.append(f"- `{d.name}` ({file_count} 个文件)")

        report.append("\n### 3.4 Layer重复目录 (需要评估)\n")
        for d in sorted(self.layer_dirs, key=lambda x: x.name):
            file_count = len(list(d.rglob("*.md")))
            report.append(f"- `{d.name}` ({file_count} 个文件)")

        # 修复建议
        report.append("\n## 4. 修复建议\n")
        report.append("### 4.1 立即执行 (低风险)\n")
        report.append("1. [OK] 删除所有 `_BAK*` 和 `_BACKUP*` 备份目录")
        report.append("2. [OK] 删除所有测试目录 (`10_l/`, `11_la/` 等)")
        report.append("3. [OK] 清理空目录")

        report.append("\n### 4.2 需要评估 (中风险)\n")
        report.append("4. [WARN] 检查 `Layer 1 ()/` 等带括号的目录内容")
        report.append("5. [WARN] 检查 `舆情分析/` 中文目录是否有唯一内容")
        report.append("6. [WARN] 检查 `layer_1/` 等小写目录是否与标准目录重复")

        report.append("\n### 4.3 谨慎处理 (高风险)\n")
        report.append("7. [CRITICAL] 创建 `07_GOVERNANCE_COMPLIANCE/` 目录")
        report.append("8. [CRITICAL] 迁移治理相关文档到新目录")
        report.append("9. [CRITICAL] 更新所有索引和链接")

        report.append("\n" + "=" * 70)

        return "\n".join(report)


def safe_delete_directory(dir_path: Path, dry_run: bool = True) -> bool:
    """安全删除目录（移动到归档目录而非永久删除）"""
    if not dir_path.exists():
        return True

    if dry_run:
        print(f"   [DRY-RUN] 将移动: {dir_path.name}")
        return True

    try:
        # 移动到归档目录
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_name = f"{dir_path.name}_DELETED_{timestamp}"
        archive_dir = DOCS_ROOT / "99_ARCHIVE"
        archive_dir.mkdir(exist_ok=True)
        backup_path = archive_dir / backup_name

        shutil.move(str(dir_path), str(backup_path))
        print(f"   [OK] 已移动到归档: {dir_path.name} -> 99_ARCHIVE/{backup_name}")
        return True
    except Exception as e:
        print(f"   [ERROR] 移动失败: {dir_path.name} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="文件夹结构分析与修复脚本")
    parser.add_argument("--analyze-only", action="store_true", help="仅分析，不执行修复")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行，不实际修改")
    parser.add_argument("--execute", action="store_true", help="实际执行修复")
    parser.add_argument("--clean-backups", action="store_true", help="清理备份目录")
    parser.add_argument("--clean-tests", action="store_true", help="清理测试目录")

    args = parser.parse_args()

    print("=" * 70)
    print("文件夹结构分析与修复工具")
    print("=" * 70)

    # 分析阶段
    analyzer = FolderAnalyzer()
    analyzer.scan_all_directories()
    analyzer.analyze_file_content()

    # 生成报告
    report = analyzer.generate_report()
    report_path = PROJECT_ROOT / "reports" / f"folder_structure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"\n[INFO] 报告已保存: {report_path}")

    if args.analyze_only:
        print("\n[OK] 分析完成，未执行任何修复操作")
        print("   查看报告后，可以运行以下命令执行修复:")
        print("   python scripts/analyze_and_fix_folder_structure.py --dry-run")
        return 0

    # 修复阶段
    mode = "模拟执行" if args.dry_run else "实际执行"
    print(f"\n[EXEC] 开始修复 ({mode})...")

    if args.clean_backups or args.execute:
        print("\n[CLEAN] 清理备份目录...")
        for d in analyzer.backup_dirs:
            safe_delete_directory(d, dry_run=args.dry_run)

    if args.clean_tests or args.execute:
        print("\n[CLEAN] 清理测试目录...")
        for d in analyzer.test_dirs:
            safe_delete_directory(d, dry_run=args.dry_run)

    print("\n" + "=" * 70)
    if args.dry_run:
        print("[OK] 模拟执行完成")
        print("   确认无误后，运行: python scripts/analyze_and_fix_folder_structure.py --execute")
    else:
        print("[OK] 修复完成")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
