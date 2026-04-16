#!/usr/bin/env python3
"""
自动索引编译器 (Auto-Index Compiler)
从文件系统自动生成索引，不依赖人工维护
防止AI幻觉导致的索引不一致

版本: 1.1.0
日期: 2026-04-16
变更:
  - 修复去重: 链接使用相对路径(相对目标 INDEX.md)，避免同名文件覆盖/重复错误链接
  - 仅从 YAML frontmatter 提取 layer，避免正文中的 layer: 欺骗路由
  - 修正 LAYER_INDEXES（移除不存在的 06_ARCHIVE 等）
  - 未知 layer 键时按文件所在 docs 一级目录回写 INDEX
"""

import io
import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

# 排除：仅排除文件名/路径段，不用子串匹配（避免误伤）
SKIP_DIR_PARTS = frozenset(
    {
        ".git",
        ".github",
        "__pycache__",
        "node_modules",
    }
)


def _should_skip_path(md_file: Path) -> bool:
    if md_file.name == "INDEX.md":
        return True
    parts = md_file.parts
    if any(p in SKIP_DIR_PARTS for p in parts):
        return True
    return False


# layer 键 → 顶层 INDEX 路径（相对 docs/）
# layer_04 多数 L4 ML 蓝图在 01_FRAMEWORK 下，写入 01_FRAMEWORK/INDEX.md
# layer_06 常见为策略/参数类，与 03_TRADING_TACTICS 对齐（见仓库内 frontmatter 抽样）
LAYER_INDEXES: Dict[str, str] = {
    "layer_00": "00_OVERVIEW/INDEX.md",
    "layer_01": "01_FRAMEWORK/INDEX.md",
    "layer_02": "02_FACTOR_LIBRARY/INDEX.md",
    "layer_03": "03_TRADING_TACTICS/INDEX.md",
    "layer_04": "01_FRAMEWORK/INDEX.md",
    "layer_05": "05_IMPLEMENTATION/INDEX.md",
    "layer_06": "03_TRADING_TACTICS/INDEX.md",
    "layer_07": "07_AI_REPORTING/INDEX.md",
    "layer_08": "08_HUMAN_AI_INTERFACE/INDEX.md",
    "layer_09": "09_AUDIT/INDEX.md",
    "layer_10": "10_GOVERNANCE_COMPLIANCE/INDEX.md",
    "layer_11": "11_STRATEGIC_DECISION/INDEX.md",
}

# 常见非规范 layer 字符串 → 规范键（用于路由）
LAYER_ALIASES: Dict[str, str] = {
    "[layer定位]": "layer_03",
    "layer 3 (策略层)": "layer_03",
    "layer 6 (组合优化层)": "layer_04",
    "layer 8 (人机交互层)": "layer_08",
    "layer x ([layer名称])": "layer_11",
    "舆情分析": "layer_03",
    "l00_data_infrastructure": "layer_00",
}


def _alias_for_layer(key: str) -> str:
    k = key.strip()
    low = k.lower()
    if k in LAYER_ALIASES:
        return LAYER_ALIASES[k]
    if low in LAYER_ALIASES:
        return LAYER_ALIASES[low]
    return k


def _layer_value_acceptable(layer: Optional[str]) -> bool:
    """拒绝 YAML 列表误写成 layer: - xxx 等无效值。"""
    if layer is None:
        return False
    s = layer.strip()
    if len(s) < 2:
        return False
    if s.startswith("-") and not s.startswith("layer_"):
        return False
    return True


class IndexCompiler:
    """自动索引编译器 - 从文件系统生成索引"""

    def __init__(self):
        self.compiled_count = 0
        self.total_files = 0
        self.layer_structure = defaultdict(list)

    def extract_yaml_layer(self, content: str) -> Optional[str]:
        """仅从第一个 YAML frontmatter 块提取 layer 字段。"""
        text = content.lstrip("\ufeff")
        if not text.startswith("---"):
            return None
        # 第一个闭合 ---
        end = text.find("\n---", 3)
        if end == -1:
            return None
        fm = text[3:end]
        match = re.search(r"(?m)^layer:\s*(.+?)\s*$", fm)
        if not match:
            return None
        raw = match.group(1).strip()
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1]
        key = raw.strip()
        return _alias_for_layer(key)

    def normalize_layer_key(self, layer: str) -> str:
        """统一大小写与别名。"""
        if not layer:
            return layer
        s = layer.strip()
        return _alias_for_layer(s)

    def scan_files_by_layer(self) -> Dict[str, List[Path]]:
        """按层级扫描所有文件"""
        files_by_layer: Dict[str, List[Path]] = defaultdict(list)

        for md_file in DOCS_DIR.rglob("*.md"):
            if _should_skip_path(md_file):
                continue

            try:
                with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(8000)

                layer = self.extract_yaml_layer(content)
                if not layer:
                    continue
                layer = self.normalize_layer_key(layer)
                if not _layer_value_acceptable(layer):
                    continue
                files_by_layer[layer].append(md_file)
                self.total_files += 1
            except OSError as e:
                print(f"⚠️  无法读取 {md_file}: {e}")

        return files_by_layer

    def resolve_index_path(self, layer: str, files: List[Path]) -> Path:
        """决定某 layer 分桶对应的 INDEX.md 路径。"""
        if layer in LAYER_INDEXES:
            return DOCS_DIR / LAYER_INDEXES[layer]
        # 按文件物理位置：取首个文件在 docs 下的一级目录
        if files:
            rel = files[0].relative_to(DOCS_DIR)
            parts = rel.parts
            if parts:
                return DOCS_DIR / parts[0] / "INDEX.md"
        # 最后回退：避免生成 docs/layer_09 这类无效目录名
        safe = re.sub(r"[^\w\-\[\]\s()（）]", "_", layer)[:80]
        return DOCS_DIR / safe / "INDEX.md"

    def generate_index_content(self, layer: str, files: List[Path], index_path: Path) -> str:
        """生成标准格式的 INDEX 内容；按相对路径去重，链接相对 index_path 所在目录。"""

        # 按 docs 相对路径去重（同名不同目录）
        seen: Set[str] = set()
        unique_files: List[Path] = []
        for f in sorted(files, key=lambda p: p.as_posix().lower()):
            rel = f.relative_to(DOCS_DIR)
            key = rel.as_posix()
            if key in seen:
                continue
            seen.add(key)
            unique_files.append(f)

        index_dir = index_path.parent

        file_entries: List[Tuple[str, str]] = []
        for f in unique_files:
            rel = f.relative_to(DOCS_DIR)
            try:
                link = Path(os.path.relpath(f, index_dir)).as_posix()
            except ValueError:
                link = rel.as_posix()
            if link == ".":
                continue
            # 展示名：末两级路径 + stem，避免仅 stem 撞名
            parts = rel.parts
            if len(parts) >= 2:
                display_name = f"{parts[-2]}/{rel.stem}"
            else:
                display_name = rel.stem
            file_entries.append((display_name, link))

        file_entries.sort(key=lambda x: x[0].lower())

        content = f"""---
module_id: {layer.upper().replace(' ', '_')[:60]}_INDEX_AUTO
version: 1.1.0
status: Active
created_date: 2026-04-13
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: Auto-Index Compiler
standard_type: 自动索引
applicable_scope: {layer}
compliance_level: 强制标准
priority: P0-CRITICAL
layer: {layer}
responsibility:
  - 自动生成层级索引，保证文件可索引
  - 防止AI幻觉导致的索引不一致
  - 实时维护文件目录完整性
---

# {layer} 自动索引

> ⚠️  本文件由自动索引编译器自动生成，请勿手动修改
> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 文档条目数: {len(file_entries)}（已按相对路径去重）

## 文档列表

"""

        for display_name, link in file_entries:
            content += f"- [{display_name}]({link})\n"

        content += f"""

---

**生成信息**
- 生成时间: {datetime.now().isoformat()}
- 扫描范围: {DOCS_DIR}
- 索引文件: {index_path.relative_to(DOCS_DIR.parent)}
- 自动化工具: Auto-Index Compiler v1.1.0
"""

        return content

    def compile_all_indexes(self, recompile: bool = True) -> Dict[str, bool]:
        """编译所有层级的索引"""

        print("=" * 70)
        print("自动索引编译器 (Auto-Index Compiler)")
        print("=" * 70)
        print(f"工作目录: {DOCS_DIR}")
        print(f"编译时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"重编译模式: {'开启' if recompile else '禁用'}")
        print()

        print("[1/3] 按层级扫描文件系统...")
        files_by_layer = self.scan_files_by_layer()
        print(f"      发现 {self.total_files} 次文件归类，跨越 {len(files_by_layer)} 个 layer 键")
        print()

        print("[2/3] 编译层级索引...")
        results: Dict[str, bool] = {}

        for layer in sorted(files_by_layer.keys(), key=str.lower):
            files = files_by_layer[layer]
            index_path = self.resolve_index_path(layer, files)
            index_path.parent.mkdir(parents=True, exist_ok=True)

            new_content = self.generate_index_content(layer, files, index_path)

            try:
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                self.compiled_count += 1
                results[layer] = True
                status = "✅ 编译成功"
            except OSError as e:
                results[layer] = False
                status = f"❌ 编译失败: {e}"

            print(f"  {status} | {layer} ({len(files)} 个文件) → {index_path.relative_to(DOCS_DIR.parent)}")

        print()

        print("[3/3] 编译完成汇总")
        ok = sum(1 for v in results.values() if v)
        print(f"      成功编译: {ok} / {len(results)} 个层级")
        print()

        return results

    def report_compilation_status(self):
        """生成编译状态报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "compiled_count": self.compiled_count,
            "total_files": self.total_files,
            "status": "SUCCESS" if self.compiled_count > 0 else "FAILED",
        }


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="自动索引编译器")
    parser.add_argument("--recompile-all", action="store_true", help="重新编译所有索引")
    parser.add_argument("--layer", type=str, help="只编译指定层级（未实现：仍全量）")
    parser.add_argument("--output", type=str, help="输出报告文件")

    args = parser.parse_args()

    compiler = IndexCompiler()
    results = compiler.compile_all_indexes(recompile=args.recompile_all or True)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = compiler.report_compilation_status()
        report["results"] = {k: ("SUCCESS" if v else "FAILED") for k, v in results.items()}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ 报告已保存: {output_path}")

    print("\n" + "=" * 70)
    print("自动索引编译完成")
    print("=" * 70)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
