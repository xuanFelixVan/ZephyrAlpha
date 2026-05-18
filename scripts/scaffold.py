# [BLUEPRINT] MOD-INF-005 | scripts/scaffold.py | §
"""scaffold.py — ZephyrAlpha 唯一创建入口（RULE-TWO 强制执行器）

所有新文件 MUST 通过本脚本创建，禁止直接用 IDE Write/SearchReplace 写入新文件。
找到重复 → 拒绝创建并告诉已有的是什么。
不注册 → 文件根本不存在（前门守卫）。

创建模式:
    module: src/zephyr/<package>/<name>.py → 更新 <package>/__init__.py
    script: scripts/<path>/<name>.py       → 更新 script_manifest.yaml
    gate:   src/zephyr/gates/<name>.yaml   → 更新 _registry.yaml

用法:
    python scripts/scaffold.py module feedback_loop scheduler --desc "FLE 全链路调度器"
    python scripts/scaffold.py script governance/audit_registration --desc "孤儿注册检测"
    python scripts/scaffold.py gate g6_my_gate --title "My Gate" --category kms

设计基线:
    RULE-TWO: 反孤儿功能——所有新产出必须可被系统发现和调用
    RULE-ONE: temp-file + atomic rename 写入
    对标的: K8s kubectl create / Rails scaffold generator / Angular CLI
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
GATES_DIR = SRC_ZEPHYR / "gates"
SCRIPT_MANIFEST = SCRIPTS_DIR / "script_manifest.yaml"
GATE_REGISTRY = GATES_DIR / "_registry.yaml"

# ---------------------------------------------------------------------------
# 模块空壳模板
# ---------------------------------------------------------------------------
MODULE_TEMPLATE = '''"""{description}"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

__all__: list[str] = []


def main() -> None:
    """入口——待实现。"""
    pass


if __name__ == "__main__":
    main()
'''

SCRIPT_TEMPLATE = '''"""{description}"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def main() -> None:
    """入口——待实现。"""
    pass


if __name__ == "__main__":
    main()
'''

GATE_TEMPLATE = """# {gate_id} — {title}
# category: {category}
# created: {created_at}
# scaffold generated — fill in rules below

schema_version: "1.0"
gate_id: "{gate_id}"
title: "{title}"
category: "{category}"
status: active
scope: global
execution_plane: warm

checks: []
"""


# ===================================================================
# 核心引擎
# ===================================================================

class ScaffoldError(Exception):
    """脚手架阻断——创建失败（重复/冲突）。"""


class ScaffoldEngine:
    """创建→查重→注册 三步原子引擎。"""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.actions: list[str] = []

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------

    def create_module(
        self,
        package: str,
        name: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在 src/zephyr/<package>/<name>.py 创建模块，注册到 __init__.py。"""
        package_dir = SRC_ZEPHYR / package
        file_path = package_dir / f"{name}.py"
        class_name = _to_class_name(name)
        init_py = package_dir / "__init__.py"

        # ── 检查 1: 目录存在 ──
        if not package_dir.is_dir():
            raise ScaffoldError(
                f"Package '{package}' 不存在: {package_dir}\n"
                f"可用包: {_list_packages()}"
            )

        # ── 检查 2: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(
                f"文件已存在: {file_path}\n"
                f"如果是功能重复，请复用已有文件而非新建。"
            )

        # ── 检查 3: 功能重复 ──
        _check_duplicate_functionality(name, description, domain, subdomain)

        # ── 检查 4: __init__.py 中无重复 ──
        if init_py.exists():
            existing_content = init_py.read_text(encoding="utf-8")
            if class_name in existing_content or name in existing_content:
                raise ScaffoldError(
                    f"'{class_name}' / '{name}' 已在 {init_py} 中被引用。\n"
                    f"确认不是重复创建。"
                )

        # ── 执行创建 ──
        content = MODULE_TEMPLATE.format(description=description or f"{class_name} 模块")
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 __init__.py ──
        _register_to_init(init_py, class_name, name, package, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "module", self.dry_run)

        # ── 同步蓝图 §0.1 文件清单（防漂移）──
        _sync_blueprint_file_list(package, name, self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {init_py}  (export '{class_name}')")
        print(f"  ACTION:  from zephyr.{package} import {class_name}")
        _remind_sys_master_dispatch(package, name, description)
        _remind_path_tree_refresh()
        return file_path

    def create_script(
        self,
        rel_path: str,
        description: str = "",
        domain: str = "",
        subdomain: str = "",
    ) -> Path:
        """在 scripts/<rel_path>.py 创建脚本并注册到 script_manifest.yaml。"""
        file_path = SCRIPTS_DIR / f"{rel_path}.py"

        # ── 检查 1: 父目录存在 ──
        parent = file_path.parent
        if not parent.is_dir():
            os.makedirs(parent, exist_ok=True)

        # ── 检查 2: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(
                f"文件已存在: {file_path}\n"
                f"如果是功能重复，请复用已有文件而非新建。"
            )

        # ── 检查 3: 功能重复 ──
        _check_duplicate_functionality(rel_path, description, domain, subdomain)

        # ── 检查 4: manifest 中无重复 ──
        _check_manifest_duplicate(rel_path)

        # ── 执行创建 ──
        content = SCRIPT_TEMPLATE.format(description=description or f"{rel_path} 脚本")
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 manifest ──
        _register_to_manifest(rel_path, description, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "script", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {SCRIPT_MANIFEST}  (entry '{rel_path}')")
        print(f"  ACTION:  python scripts/{rel_path}.py")
        _remind_sys_master_dispatch("scripts", rel_path, description)
        _remind_path_tree_refresh()
        return file_path

    def create_gate(
        self,
        gate_id: str,
        title: str = "",
        category: str = "kms",
    ) -> Path:
        """创建门禁 YAML 并注册到 _registry.yaml。"""
        file_name = f"{gate_id.lower()}.yaml"
        file_path = GATES_DIR / file_name

        # ── 检查 1: 文件冲突 ──
        if file_path.exists():
            raise ScaffoldError(
                f"Gate 文件已存在: {file_path}"
            )

        # ── 检查 2: registry 中无重复 ──
        _check_gate_registry_duplicate(gate_id)

        # ── 执行创建 ──
        content = GATE_TEMPLATE.format(
            gate_id=gate_id,
            title=title or gate_id,
            category=category,
            created_at=datetime.now().strftime("%Y-%m-%d"),
        )
        _atomic_write(file_path, content, self.dry_run, self.actions)

        # ── 注册到 _registry.yaml ──
        _register_to_gate_registry(gate_id, title, category, file_name, self.dry_run, self.actions)

        # ── 通知资产盘点系统（MOD-INF-026）──
        _notify_asset_inventory(str(file_path), "gate", self.dry_run)

        print(f"\n  CREATED  {file_path}")
        print(f"  REGISTERED  {GATE_REGISTRY}  (gate_id '{gate_id}')")
        _remind_path_tree_refresh()
        return file_path


# ===================================================================
# 注册辅助函数
# ===================================================================

def _register_to_init(
    init_py: Path,
    class_name: str,
    module_name: str,
    package: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 __init__.py 追加 import + __all__ 条目。"""
    if not init_py.exists():
        init_py.write_text(
            f"from zephyr.{package}.{module_name} import {class_name}\n\n"
            f"__all__ = [\n    \"{class_name}\",\n]\n",
            encoding="utf-8",
        )
        return

    content = init_py.read_text(encoding="utf-8")

    import_line = f"from zephyr.{package}.{module_name} import {class_name}"
    if import_line not in content:
        lines = content.split("\n")
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_pos = i + 1
        lines.insert(insert_pos, import_line)
        content = "\n".join(lines)

    if "__all__" in content:
        all_line = f'    "{class_name}",'
        if all_line not in content:
            content = _insert_into_all_list(content, class_name)
    else:
        content += f"\n__all__ = [\n    \"{class_name}\",\n]\n"

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {init_py}")
        return

    _atomic_write(init_py, content, False, actions)


def _insert_into_all_list(text: str, name: str) -> str:
    """在 __all__ 列表中插入条目（字母序）。"""
    pattern = r'(\[ __all__\s*=\s*\[)(.*?)(\])'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        text += f'\n__all__.append("{name}")\n'
        return text

    prefix = match.group(1)
    middle = match.group(2)
    suffix = match.group(3)

    entries = [e.strip().strip('"').strip("'") for e in middle.split(",") if e.strip()]
    entries.append(name)
    entries = sorted(set(entries))

    new_middle = "\n    " + ",\n    ".join(f'"{e}"' for e in entries) + ",\n"
    return text[: match.start(2)] + new_middle + text[match.end(2) :]


def _register_to_manifest(
    rel_path: str,
    description: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 script_manifest.yaml 追加条目。"""
    if not SCRIPT_MANIFEST.exists():
        raise ScaffoldError(f"script_manifest.yaml 不存在: {SCRIPT_MANIFEST}")

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])

    entry = {
        "path": f"{rel_path}.py",
        "description": description or f"{rel_path} 脚本",
        "domain": rel_path.split("/")[0] if "/" in rel_path else "root",
        "execution_plane": "warm-path",
        "status": "registered",
    }
    scripts.append(entry)
    manifest["scripts"] = scripts
    manifest["total_scripts"] = len(scripts)
    manifest["generated_at"] = datetime.now().strftime("%Y-%m-%d")

    new_content = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {SCRIPT_MANIFEST}")
        return

    _atomic_write(SCRIPT_MANIFEST, new_content, False, actions)


def _register_to_gate_registry(
    gate_id: str,
    title: str,
    category: str,
    file_name: str,
    dry_run: bool,
    actions: list[str],
) -> None:
    """向 _registry.yaml 追加门禁条目。"""
    if not GATE_REGISTRY.exists():
        raise ScaffoldError(f"_registry.yaml 不存在: {GATE_REGISTRY}")

    registry = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry.get("gates", [])

    entry = {
        "gate_id": gate_id,
        "gate_name": gate_id.lower(),
        "title": title or gate_id,
        "category": category,
        "file": file_name,
        "status": "active",
        "scope": "global",
        "execution_plane": "warm",
    }
    gates.append(entry)
    registry["gates"] = gates
    registry["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    new_content = yaml.dump(registry, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if dry_run:
        actions.append(f"[DRY-RUN] Would update {GATE_REGISTRY}")
        return

    _atomic_write(GATE_REGISTRY, new_content, False, actions)


# ===================================================================
# 重复检查
# ===================================================================

def _check_duplicate_functionality(name: str, description: str, domain: str = "", subdomain: str = "") -> None:
    """SSoT门禁：检查功能域重叠。硬阻断——重叠时禁止创建。"""
    try:
        from zephyr.l01_infrastructure.registry_governance import FunctionalDomainRegistry
        registry = FunctionalDomainRegistry()
        overlap = registry.check_overlap(
            domain=domain,
            subdomain=subdomain,
            name=name,
            description=description,
        )
        if overlap.has_overlap:
            details = "; ".join(overlap.overlap_details)
            raise ScaffoldError(
                f"SSoT门禁阻断：功能域重叠检测到\n"
                f"  {details}\n"
                f"  复用决策（RULE-EIGHT）：\n"
                f"    完全覆盖 → 直接用已有模块\n"
                f"    80%覆盖 → 扩展已有模块\n"
                f"    50%覆盖 → 重构已有+扩展\n"
                f"    0%覆盖 → 确认domain/subdomain后重新创建\n"
                f"  如确需新建，请指定 --domain 和 --subdomain 参数声明新功能域"
            )
    except ScaffoldError:
        raise
    except ImportError:
        pass
    except Exception as exc:
        print(f"  WARNING: 功能域注册表检查失败: {exc}")

    try:
        from zephyr.mcp import BlueprintSearchServer
    except ImportError:
        return

    query = f"{name} {description}".strip()
    if not query or len(query) < 3:
        return

    try:
        server = BlueprintSearchServer()
        result = server._find_relevant_blueprint(query, num_results=5)
        matches = result.get("results", [])
        for m in matches[:3]:
            score = m.get("relevance_score", 0)
            if score >= 20:
                raise ScaffoldError(
                    f"SSoT门禁阻断：蓝图关键词匹配检测到类似功能\n"
                    f"  已有蓝图: {m.get('blueprint_id', '?')} (score={score})\n"
                    f"  description: {m.get('hint', 'N/A')}\n"
                    f"  level={m.get('blueprint_level')} priority={m.get('priority')}\n"
                    f"  复用决策（RULE-EIGHT）：\n"
                    f"    完全覆盖 → 直接用已有蓝图\n"
                    f"    80%覆盖 → 扩展已有蓝图\n"
                    f"    50%覆盖 → 重构已有+扩展\n"
                    f"    0%覆盖 → 确认后使用 --force-override 强制创建"
                )
    except ScaffoldError:
        raise
    except Exception:
        pass


def _check_manifest_duplicate(rel_path: str) -> None:
    """检查 script_manifest.yaml 中是否已有同路径条目。"""
    if not SCRIPT_MANIFEST.exists():
        return

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])

    target = f"{rel_path}.py"
    for entry in scripts:
        if entry.get("path") == target:
            raise ScaffoldError(
                f"script_manifest.yaml 中已存在: {target}\n"
                f"description: {entry.get('description', 'N/A')}"
            )


def _check_gate_registry_duplicate(gate_id: str) -> None:
    """检查 _registry.yaml 中是否已有同 ID 门禁。"""
    if not GATE_REGISTRY.exists():
        return

    registry = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry.get("gates", [])

    for entry in gates:
        if entry.get("gate_id", "").upper() == gate_id.upper():
            raise ScaffoldError(
                f"_registry.yaml 中已存在 gate_id='{gate_id}'\n"
                f"title: {entry.get('title', 'N/A')}\n"
                f"file: {entry.get('file', 'N/A')}"
            )


# ===================================================================
# 通用工具
# ===================================================================

def _notify_asset_inventory(file_path: str, asset_type: str, dry_run: bool) -> None:
    """post-creation hook: 通知资产盘点系统新文件已创建。

    MOD-INF-026 蓝图 §38 自资产注册 —— scaffold.py 是唯一创建入口，
    所有新文件通过此 hook 自动通知盘点系统。

    失败不阻塞 scaffold —— 盘点系统不可用也允许创建文件。
    """
    if dry_run:
        return

    try:
        from zephyr.asset_inventory.telemetry import get_telemetry
        telemetry = get_telemetry()
        telemetry.inc(f"scaffold_{asset_type}_created")
    except Exception:
        pass


def _remind_sys_master_dispatch(package: str, name: str, description: str) -> None:
    """post-creation hook: 提醒更新 SYS-MASTER-001 §0.2 分派表。

    RULE-TWO 反孤儿功能——新模块/脚本创建后，下一个 AI session
    需要通过 §0 分派表发现它。如果分派表没有对应条目，新功能就是孤儿。
    """
    sys_master = PROJECT_ROOT / "docs" / "03_modules" / "_sys-master" / "blueprint.md"
    if not sys_master.exists():
        return

    try:
        text = sys_master.read_text(encoding="utf-8")
        search_key = name.replace("-", "_").replace("/", "_")
        if search_key not in text and name not in text:
            print(f"  ⚠️  REMINDER: '{name}' not found in SYS-MASTER-001 §0.2 dispatch table.")
            print(f"  ⚠️  If this module serves a new task domain, add a row to §0.2:")
            print(f"  ⚠️    | {description or name} | 本蓝图 §N | <module blueprint> | ~400 |")
    except Exception:
        pass


def _sync_blueprint_file_list(package: str, name: str, dry_run: bool) -> None:
    """post-creation hook: 自动更新蓝图 §0.1 代码文件清单。

    RULE-TWO 反孤儿 + 防漂移——scaffold 创建新模块后，自动将新文件
    添加到对应蓝图的 §0.1 文件清单中，防止蓝图-代码漂移。

    查找逻辑：从 src/zephyr/<package>/ 定位到 docs/03_modules/ 下对应蓝图。
    """
    if dry_run:
        return

    code_dir = SRC_ZEPHYR / package
    if not code_dir.exists():
        return

    blueprint_dir = PROJECT_ROOT / "docs" / "03_modules"
    blueprint_candidates = list(blueprint_dir.rglob("blueprint.md"))
    target_blueprint = None
    for bp in blueprint_candidates:
        try:
            text = bp.read_text(encoding="utf-8")
            if f"actual_disk_path: \"src/zephyr/{package}/\"" in text or f"actual_disk_path: 'src/zephyr/{package}/'" in text:
                target_blueprint = bp
                break
        except Exception:
            continue

    if target_blueprint is None:
        return

    try:
        content = target_blueprint.read_text(encoding="utf-8")
        actual_files = sorted([f.name for f in code_dir.iterdir() if f.suffix == ".py"])
        actual_count = len(actual_files)

        import re
        section_match = re.search(r'###\s*§0\.1\s+代码文件清单', content)
        if not section_match:
            return

        listed_match = re.findall(r'^\|\s*\d+\s*\|\s*`([^`]+)`', content[section_match.start():], re.MULTILINE)
        listed_files = set(listed_match)
        actual_set = set(actual_files)
        missing_in_blueprint = actual_set - listed_files

        if not missing_in_blueprint:
            return

        last_row_match = None
        for m in re.finditer(r'^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|', content[section_match.start():], re.MULTILINE):
            last_row_match = m
        if last_row_match is None:
            return

        last_num = int(last_row_match.group(1))
        insert_pos = section_match.start() + last_row_match.end()

        new_rows = ""
        for i, fname in enumerate(sorted(missing_in_blueprint), last_num + 1):
            new_rows += f"\n| {i} | `{fname}` | §3.1 | {fname.replace('.py', '').replace('_', ' ')} | 已实现 | — |"

        content = content[:insert_pos] + new_rows + content[insert_pos:]

        for old_count in range(1, 200):
            for pattern in [
                f"{old_count} .py files",
                f"{old_count} 个 .py 文件",
                f"{old_count} 个 .py",
                f"{old_count}代码文件",
            ]:
                if pattern in content and old_count != actual_count:
                    content = content.replace(pattern, pattern.replace(str(old_count), str(actual_count)))

        tmp_path = str(target_blueprint) + f".{os.getpid()}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(target_blueprint))

        print(f"  📋 SYNCED: Added {len(missing_in_blueprint)} file(s) to blueprint §0.1: {sorted(missing_in_blueprint)}")
    except Exception as e:
        print(f"  ⚠️  SYNC-FAILED: Could not update blueprint §0.1: {e}")


def _atomic_write(path: Path, content: str, dry_run: bool, actions: list[str]) -> None:
    """RULE-ONE 合规: temp-file + atomic rename。"""
    if dry_run:
        actions.append(f"[DRY-RUN] Would write {path}")
        return

    tmp_path = Path(f"{path}.{os.getpid()}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(str(tmp_path), str(path))
    except PermissionError:
        try:
            os.remove(str(tmp_path))
        except OSError:
            pass
        raise


def _to_class_name(name: str) -> str:
    """snake_case → PascalCase。"""
    return "".join(part.capitalize() for part in name.split("_"))


def _list_packages() -> str:
    """列出 src/zephyr/ 下所有子包。"""
    pkgs = [
        d.name
        for d in sorted(SRC_ZEPHYR.iterdir())
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")
        and (d / "__init__.py").exists()
    ]
    return ", ".join(pkgs[:20])


# ===================================================================
# CLI
# ===================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ZephyrAlpha Scaffold — 唯一创建入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # module
    p_mod = sub.add_parser("module", help="创建 src/zephyr/<package>/<name>.py")
    p_mod.add_argument("package", help="目标包名 (e.g. feedback_loop)")
    p_mod.add_argument("name", help="模块名 (e.g. scheduler)")
    p_mod.add_argument("--desc", default="", help="功能描述")
    p_mod.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_mod.add_argument("--subdomain", default="", help="子功能域 (e.g. gate_engine)")
    p_mod.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # script
    p_scr = sub.add_parser("script", help="创建 scripts/<path>/<name>.py")
    p_scr.add_argument("path", help="scripts 下的相对路径 (e.g. governance/my_tool)")
    p_scr.add_argument("--desc", default="", help="功能描述")
    p_scr.add_argument("--domain", default="", help="功能域 (e.g. governance)")
    p_scr.add_argument("--subdomain", default="", help="子功能域 (e.g. gate_engine)")
    p_scr.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    # gate
    p_gate = sub.add_parser("gate", help="创建 src/zephyr/gates/<id>.yaml")
    p_gate.add_argument("gate_id", help="Gate 标识 (e.g. G7)")
    p_gate.add_argument("--title", default="", help="门禁标题")
    p_gate.add_argument("--category", default="kms", help="门禁分类")
    p_gate.add_argument("--dry-run", action="store_true", help="仅检查，不写入")

    args = parser.parse_args()
    engine = ScaffoldEngine(dry_run=args.dry_run)

    try:
        if args.mode == "module":
            engine.create_module(args.package, args.name, args.desc, domain=getattr(args, 'domain', ''), subdomain=getattr(args, 'subdomain', ''))
        elif args.mode == "script":
            engine.create_script(args.path, args.desc, domain=getattr(args, 'domain', ''), subdomain=getattr(args, 'subdomain', ''))
        elif args.mode == "gate":
            engine.create_gate(args.gate_id, args.title, args.category)
        else:
            parser.print_help()
            sys.exit(1)
    except ScaffoldError as e:
        print(f"\n  BLOCKED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
