#!/usr/bin/env python3
"""目录迁移脚本

用途: 迁移违规目录到合规命名，并自动更新所有引用
功能:
  - 复制目录内容到新位置
  - 批量更新所有.md文件中的链接
  - 更新SITEMAP映射
  - 生成迁移报告

使用:
  python scripts/migrate_directory.py \
    --from docs/module_designs \
    --to docs/12_MODULE_DESIGNS \
    --update-links

作者: 文档治理委员会
日期: 2026-04-13
"""

from __future__ import annotations

import io
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"
PROJECT_ROOT = DOCS_ROOT.parent


class DirectoryMigrator:
    """目录迁移器"""

    def __init__(self, from_dir: Path, to_dir: Path, dry_run: bool = False):
        self.from_dir = Path(from_dir)
        self.to_dir = Path(to_dir)
        self.dry_run = dry_run
        self.updated_files: List[Path] = []
        self.errors: List[str] = []

    def migrate(self, links_only: bool = False) -> bool:
        """执行迁移，返回是否成功
        
        Args:
            links_only: 如果为True，仅更新链接，不复制目录
        """
        print("=" * 70)
        print("目录迁移")
        print("=" * 70)
        print(f"从: {self.from_dir}")
        print(f"到: {self.to_dir}")
        print(f"模式: {'预览' if self.dry_run else '执行'}")
        if links_only:
            print("仅更新链接（目录已手动移动）")
        print("-" * 70)

        # 1. 验证源目录存在（仅非links_only模式）
        if not links_only and not self.from_dir.exists():
            print(f"❌ 源目录不存在: {self.from_dir}")
            return False

        # 2. 验证目标目录不存在（或为空）- 仅非links_only模式
        if not links_only:
            if self.to_dir.exists() and any(self.to_dir.iterdir()):
                print(f"❌ 目标目录已存在且非空: {self.to_dir}")
                return False
        else:
            if not self.to_dir.exists():
                print(f"❌ 目标目录不存在（links_only模式）: {self.to_dir}")
                return False

        # 3. 检查命名合规性
        new_name = self.to_dir.name
        if not self._check_naming_compliance(new_name):
            return False

        try:
            # 4. 复制目录（如非links_only）
            if not links_only:
                if not self.dry_run:
                    self._copy_directory()
                print(f"✅ 目录复制: {self.from_dir.name} -> {self.to_dir.name}")

            # 5. 更新链接
            old_rel = self.from_dir.relative_to(DOCS_ROOT)
            new_rel = self.to_dir.relative_to(DOCS_ROOT)
            self._update_all_links(str(old_rel).replace("\\", "/"),
                                   str(new_rel).replace("\\", "/"))

            # 6. 更新SITEMAP
            if not self.dry_run:
                self._update_sitemap()

            # 7. 生成报告
            self._generate_report()

            print("\n" + "=" * 70)
            print(f"迁移{'预览' if self.dry_run else '完成'}")
            print(f"更新文件数: {len(self.updated_files)}")
            if self.errors:
                print(f"错误数: {len(self.errors)}")
            print("=" * 70)

            return len(self.errors) == 0

        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            return False

    def _check_naming_compliance(self, dir_name: str) -> bool:
        """检查目录命名合规性"""
        import re

        # Layer主目录规则
        layer_pattern = re.compile(r"^\d{2}_[A-Z_]+$")
        # 子目录规则
        sub_pattern = re.compile(r"^[a-z0-9_]+|[A-Z0-9_]+$")
        # 禁止词
        prohibited = {"temp", "tmp", "backup", "old", "test", "new"}

        if dir_name.lower() in prohibited:
            print(f"❌ 目录名包含禁止词: {dir_name}")
            return False

        depth = len(self.to_dir.relative_to(DOCS_ROOT).parts)
        if depth == 1:
            if not layer_pattern.match(dir_name):
                print(f"❌ Layer主目录命名违规: {dir_name}")
                print("   应使用格式: 数字_大写下划线 (如 12_MODULE_DESIGNS)")
                return False
        else:
            if not sub_pattern.match(dir_name):
                print(f"⚠️ 子目录命名建议检查: {dir_name}")

        return True

    def _copy_directory(self) -> None:
        """复制目录内容"""
        self.to_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.from_dir, self.to_dir)

    def _update_all_links(self, old_rel: str, new_rel: str) -> None:
        """更新所有.md文件中的链接"""
        print(f"\n🔍 更新链接: {old_rel} -> {new_rel}")

        for md_file in DOCS_ROOT.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8-sig")
                original = content

                # 更新各种格式的链接
                patterns = [
                    (rf"\({re.escape(old_rel)}", f"({new_rel}"),
                    (rf"\[{re.escape(old_rel)}\]", f"[{new_rel}]"),
                    (rf'"{re.escape(old_rel)}"', f'"{new_rel}"'),
                ]

                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)

                if content != original:
                    if not self.dry_run:
                        md_file.write_text(content, encoding="utf-8")
                    self.updated_files.append(md_file)
                    print(f"  更新: {md_file.relative_to(DOCS_ROOT)}")

            except Exception as e:
                self.errors.append(f"{md_file}: {e}")

    def _update_sitemap(self) -> None:
        """更新SITEMAP.md"""
        sitemap_path = DOCS_ROOT / "SITEMAP.md"
        if not sitemap_path.exists():
            return

        try:
            content = sitemap_path.read_text(encoding="utf-8-sig")
            old_rel = str(self.from_dir.relative_to(DOCS_ROOT)).replace("\\", "/")
            new_rel = str(self.to_dir.relative_to(DOCS_ROOT)).replace("\\", "/")

            if old_rel in content:
                content = content.replace(old_rel, new_rel)
                sitemap_path.write_text(content, encoding="utf-8")
                print(f"\n✅ 更新 SITEMAP.md")
        except Exception as e:
            self.errors.append(f"SITEMAP update: {e}")

    def _generate_report(self) -> None:
        """生成迁移报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = PROJECT_ROOT / f"reports/migration_{timestamp}.md"

        report = f"""# 目录迁移报告

**迁移时间**: {datetime.now().isoformat()}
**源目录**: {self.from_dir}
**目标目录**: {self.to_dir}
**模式**: {'预览' if self.dry_run else '执行'}

## 统计

- 更新文件数: {len(self.updated_files)}
- 错误数: {len(self.errors)}

## 更新的文件

"""
        for f in self.updated_files:
            report += f"- {f.relative_to(DOCS_ROOT)}\n"

        if self.errors:
            report += "\n## 错误\n\n"
            for e in self.errors:
                report += f"- {e}\n"

        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"\n📄 报告已保存: {report_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="目录迁移工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览迁移
  python migrate_directory.py --from docs/module_designs --to docs/12_MODULE_DESIGNS --dry-run

  # 执行迁移
  python migrate_directory.py --from docs/module_designs --to docs/12_MODULE_DESIGNS

  # 仅更新链接（目录已手动移动）
  python migrate_directory.py --from docs/old_name --to docs/new_name --links-only
        """,
    )

    parser.add_argument("--from", "-f", dest="from_dir", required=True,
                        help="源目录路径")
    parser.add_argument("--to", "-t", dest="to_dir", required=True,
                        help="目标目录路径")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="预览模式（不实际修改）")
    parser.add_argument("--links-only", "-l", action="store_true",
                        help="仅更新链接，不复制目录")

    args = parser.parse_args()

    from_path = PROJECT_ROOT / args.from_dir
    to_path = PROJECT_ROOT / args.to_dir

    migrator = DirectoryMigrator(from_path, to_path, dry_run=args.dry_run)
    success = migrator.migrate(links_only=args.links_only)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
