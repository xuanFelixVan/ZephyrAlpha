#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
自动化INDEX.md生成脚本

功能:
1. 扫描缺失INDEX.md的目录
2. 分析目录内容
3. 生成标准化的INDEX.md文件

使用方法:
    python scripts/auto_generate_index.py [--dry-run] [--priority-threshold 3]
"""

import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class IndexGenerator:
    """INDEX.md自动生成器"""

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.stats = {
            "total_scanned": 0,
            "missing_index": 0,
            "generated": 0,
            "skipped": 0
        }

    def scan_missing_index_directories(self, min_files: int = 1) -> List[Dict]:
        """扫描缺失INDEX.md的目录"""
        missing_dirs = []

        for root, dirs, files in os.walk(self.docs_root):
            # 排除特定目录
            if any(exclude in root for exclude in ["audit_state", "archive", "__pycache__", ".git"]):
                continue

            # 检查是否有INDEX.md
            index_path = Path(root) / "INDEX.md"
            if index_path.exists():
                continue

            # 统计.md文件数量
            md_files = [f for f in files if f.endswith(".md")]
            if len(md_files) >= min_files:
                missing_dirs.append({
                    "path": root,
                    "relative_path": Path(root).relative_to(self.docs_root.parent),
                    "md_count": len(md_files),
                    "md_files": md_files
                })

        self.stats["total_scanned"] = len(missing_dirs)
        return missing_dirs

    def analyze_directory_content(self, dir_path: str) -> Dict:
        """分析目录内容"""
        path = Path(dir_path)
        md_files = list(path.glob("*.md"))

        # 提取module_id
        modules = []
        for md_file in md_files:
            if md_file.name == "INDEX.md":
                continue

            module_id = self.extract_module_id(md_file)
            if module_id:
                modules.append({
                    "file": md_file.name,
                    "module_id": module_id
                })

        # 推断目录职责
        responsibility = self.infer_responsibility(path, modules)

        return {
            "path": path,
            "md_files": [f.name for f in md_files if f.name != "INDEX.md"],
            "modules": modules,
            "responsibility": responsibility
        }

    def extract_module_id(self, md_file: Path) -> Optional[str]:
        """从文件中提取module_id"""
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("module_id:"):
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return None

    def infer_responsibility(self, dir_path: Path, modules: List[Dict]) -> str:
        """推断目录职责"""
        dir_name = dir_path.name.lower()

        # 基于目录名称推断
        responsibility_map = {
            "blueprints": "蓝图文档管理",
            "standards": "标准规范管理",
            "templates": "模板文档管理",
            "reports": "报告文档管理",
            "audit": "审计文档管理",
            "data_source": "数据源管理",
            "factor_library": "因子库管理",
            "trading_tactics": "交易策略管理",
            "execution": "执行层管理",
            "risk": "风险管理",
            "monitoring": "监控管理",
            "ui_design": "UI设计管理",
            "operations": "运营管理"
        }

        for key, value in responsibility_map.items():
            if key in dir_name:
                return value

        return "文档索引导航"

    def generate_index_content(self, dir_info: Dict) -> str:
        """生成INDEX.md内容"""
        path = dir_info["path"]
        relative_path = dir_info["relative_path"]

        # 生成标题
        title = path.name.replace("_", " ").title()

        # 生成内容
        content = f"""---
module_id: INDEX_{path.name.upper()}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档治理系统
standard_type: 索引文档
applicable_scope: {dir_info['responsibility']}
compliance_level: 专业标准
---

# {title}索引

> **版本**: v1.0.0
> **创建日期**: {datetime.now().strftime('%Y-%m-%d')}
> **核心定位**: {dir_info['responsibility']}
> **索引**: `INDEX_{path.name.upper()}_001`

---

## 📋 目录概览

### 统计信息

| 指标 | 数值 |
|------|------|
| **文档总数** | {len(dir_info['md_files'])} |
| **活跃模块** | {len(dir_info['modules'])} |
| **更新频率** | 按需更新 |

---

## 📚 文档列表

"""

        # 添加文档列表
        if dir_info["md_files"]:
            content += "### 核心文档\n\n"
            for md_file in sorted(dir_info["md_files"]):
                # 查找对应的module_id
                module_id = None
                for module in dir_info["modules"]:
                    if module["file"] == md_file:
                        module_id = module["module_id"]
                        break

                # 生成文档标题（从文件名推断）
                doc_title = md_file.replace(".md", "").replace("_", " ").title()

                if module_id:
                    content += f"- [{doc_title}]({md_file}) - `{module_id}`\n"
                else:
                    content += f"- [{doc_title}]({md_file})\n"
        else:
            content += "暂无文档\n"

        # 添加维护指南
        content += f"""
---

## 🔍 维护指南

### 更新规则

1. **新增文档**: 在此目录添加新文档后，更新本文档列表
2. **删除文档**: 删除文档后，从列表中移除对应条目
3. **重命名文档**: 更新文档名称后，同步更新索引

### 质量标准

- ✅ 所有文档必须有明确的module_id
- ✅ 文档命名遵循专业量化机构标准
- ✅ 保持索引与实际文件一致

---

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本创建 | 文档治理系统 |

---

## 🔗 相关文档

- [Module ID注册表](../../09_AUDIT/STATE/MODULE_ID_REGISTRY.md)
- [职责边界地图](../../09_AUDIT/STATE/RESPONSIBILITY_BOUNDARY_MAP.md)
- [专业文档治理审计指南](../../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)

---

**索引状态**: ✅ 活跃
**维护频率**: 按需更新
**下次更新**: 按需
"""

        return content

    def generate_index_file(self, dir_info: Dict, dry_run: bool = False) -> bool:
        """生成INDEX.md文件"""
        index_path = dir_info["path"] / "INDEX.md"

        if dry_run:
            print(f"[DRY-RUN] 将创建: {index_path}")
            return True

        try:
            content = self.generate_index_content(dir_info)
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] 已创建: {index_path.relative_to(self.docs_root.parent)}")
            self.stats["generated"] += 1
            return True
        except Exception as e:
            print(f"[ERROR] 创建失败: {index_path} - {e}")
            self.stats["skipped"] += 1
            return False

    def run(self, dry_run: bool = False, min_files: int = 1, priority_threshold: int = 3):
        """执行自动生成"""
        print("=" * 80)
        print("INDEX.md自动生成工具")
        print("=" * 80)
        print()

        # 扫描缺失INDEX.md的目录
        print("第一阶段: 扫描缺失INDEX.md的目录")
        print("-" * 80)
        missing_dirs = self.scan_missing_index_directories(min_files)

        if not missing_dirs:
            print("[OK] 所有目录都有INDEX.md")
            return

        print(f"发现 {len(missing_dirs)} 个目录缺失INDEX.md")
        print()

        # 按文件数量排序（优先处理文件多的目录）
        missing_dirs.sort(key=lambda x: x["md_count"], reverse=True)

        # 显示前10个优先级最高的目录
        print("优先级最高的目录:")
        for i, dir_info in enumerate(missing_dirs[:10], 1):
            print(f"{i}. {dir_info['relative_path']} - {dir_info['md_count']}个文件")

        print()
        print("-" * 80)
        print()

        # 生成INDEX.md文件
        print("第二阶段: 生成INDEX.md文件")
        print("-" * 80)

        for dir_info in missing_dirs:
            # 分析目录内容
            analyzed = self.analyze_directory_content(dir_info["path"])
            # 添加relative_path字段
            analyzed["relative_path"] = dir_info["relative_path"]

            # 生成INDEX.md
            self.generate_index_file(analyzed, dry_run)

        # 统计信息
        print()
        print("=" * 80)
        print("生成统计")
        print("=" * 80)
        print(f"扫描目录数: {self.stats['total_scanned']}")
        print(f"生成文件数: {self.stats['generated']}")
        print(f"跳过文件数: {self.stats['skipped']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="INDEX.md自动生成工具")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟运行，不实际创建文件")
    parser.add_argument("--min-files", type=int, default=1, help="最小文件数量阈值")
    parser.add_argument("--priority-threshold", type=int, default=3, help="优先级阈值")

    args = parser.parse_args()

    generator = IndexGenerator()
    generator.run(
        dry_run=args.dry_run,
        min_files=args.min_files,
        priority_threshold=args.priority_threshold
    )


if __name__ == "__main__":
    main()
