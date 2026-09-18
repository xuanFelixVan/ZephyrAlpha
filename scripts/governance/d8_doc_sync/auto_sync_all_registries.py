# [BLUEPRINT] MOD-INF-005 | scripts/governance/auto_sync_all_registries.py | §
# [MODULE] scripts.governance.auto_sync_all_registries
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__；zephyr.shared.utils.time_utils(now_utc, RULE-SCHEMA-TZ)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""全自动注册表同步器
=====================================
扫描变更→更新所有相关注册表→零孤儿

RULE-TWO/RULE-FOUR/RULE-EIGHT 自动化执行器。
一人开发+AI 维护: 每次 session 结束前运行 --all。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 全自动注册表同步器
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import ast
import logging
import os
import re
import sys
from pathlib import Path
from typing import Final

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import (  # noqa: E402  热文件 CAS 写纪律（宪法 §0.2/§0.13）
    StaleWriteRefused,
    WriteVerificationError,
)
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402  RULE-SCHEMA-TZ: 生成器禁 datetime.now()/time.time()

logger = logging.getLogger(__name__)

PROJECT_ROOT = REPO_ROOT

REGISTRIES = {
    "module": PROJECT_ROOT / "docs/03_modules/module-registry.yaml",
    "blueprint": PROJECT_ROOT / "docs/03_modules/blueprint_registry.yaml",
    "gate": PROJECT_ROOT / "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
    "cross_dep": PROJECT_ROOT
    / "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml",
}

# ARCH-036: 路径修正 — 真实物理路径为 src/zephyr/feedback_loop/（下划线，已从 trading/ 迁出至顶层）；
# 旧路径 src/zephyr/feedback-loop/（短横线）从未存在，导致 _discover_fle_gates 静默返回空列表。
FLE_GATES_DIR = PROJECT_ROOT / "src" / "zephyr" / "feedback_loop" / "gates"
FLE_BLUEPRINT = PROJECT_ROOT / "docs" / "03_modules" / "_cross_layer" / "feedback_loop" / "blueprint.md"
FEEDBACK_LOOP_DIR = PROJECT_ROOT / "src" / "zephyr" / "feedback_loop"

FLE_GATE_CATEGORY = "fle_self_defense"
FLE_MODULE_ID = "MOD-FEEDBACK_LOOP"

# WP5/D-4（2026-09-19）第四册派生段总闸：summary/last_updated 一律由 gates 派生，
# 禁手工维护（宪法 §9.5 静态清单禁手工维护）。裁定真源=
# docs/_working/2026-09-18-rule-audit-master-construction-plan.md §1 D-4。
GATE_STATUS_ALIASES: Final[dict[str, str]] = {
    # D-4 归一规则的现场判定：implemented 不在 module_lifecycle_status 词表合法值
    # （docs/01_policies_and_standards/_registry/vocabularies/
    #   module_lifecycle_status_vocabulary.yaml = planned/in_design/in_dev/testing/
    #   active/suspended/deprecated/archived 8 值）⇒ "不在册则归并为 active"。
    # draft 在 status_vocabulary.yaml（文档 3 值词表）在册，D-4 未裁 → 不归并，只报。
    "implemented": "active",
}
# summary 块 = 顶格 `summary:` 起至下一个顶格键（或文件尾）
_GATE_SUMMARY_BLOCK_RE: Final[str] = r"(?ms)^summary:.*?(?=^\S|\Z)"
# volatile 行（P0② 生成器时间戳非幂等治本同款）：仅时戳差异时跳写
_LAST_UPDATED_LINE_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^last_updated: .*$")


def _load_yaml(path: Path) -> dict | None:
    """_load_yaml implementation."""
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load YAML %s: %s", path, e)
        return None


def _save_yaml(path: Path, data: dict, dry_run: bool = False) -> bool:
    """_save_yaml implementation."""
    try:
        import yaml

        content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        if dry_run:
            logger.info("[DRY-RUN] Would write %d bytes to %s", len(content), path)
            return True
        if atomic_write_safe(path, content):
            logger.info("Written %s", path)
            return True
        logger.error("Failed to save YAML %s: atomic_write_safe returned False", path)
        return False
    except Exception as e:
        logger.error("Failed to save YAML %s: %s", path, e)
        return False


def _discover_fle_gates() -> list[dict]:
    """_discover_fle_gates implementation."""
    gates = []
    # ARCH-036: 静默失效修正 — 旧代码 if not exists: return 静默吞掉路径错误，
    # 改为打印 stderr 警告（与 audit_registration.py GATES_DIR 处理一致）。
    if not FLE_GATES_DIR.is_dir():
        print(f"[WARN] FLE_GATES_DIR not found: {FLE_GATES_DIR} — FLE gate discovery skipped", file=sys.stderr)
        return gates
    for py_file in sorted(FLE_GATES_DIR.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        stem = py_file.stem
        gate_id = f"FLE-{stem.upper().replace('_', '-')[:28]}"
        title = _read_class_docstring(py_file) or stem.replace("_", " ").title()
        gates.append(
            {
                "gate_id": gate_id,
                "gate_name": stem,
                "title": f"{gate_id} {title}",
                "category": FLE_GATE_CATEGORY,
                # ARCH-036: 相对路径基准为 _registry.yaml 所在的 rule_enforcement/，
                # 到 feedback_loop/gates/ 需上溯两级再进入 feedback_loop/。
                "file": f"../../feedback_loop/gates/{py_file.name}",
                "status": "active",
                "scope": "fle",
                "execution_plane": "warm",
                "note": f"Auto-registered by auto_sync_all_registries.py — FLE self-defense gate (physical: src/zephyr/feedback_loop/gates/{py_file.name})",
            }
        )
    return gates


def _read_class_docstring(py_file: Path) -> str | None:
    """_read_class_docstring implementation."""
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                if doc:
                    return doc.split("\n")[0].strip()
        doc = ast.get_docstring(tree)
        if doc:
            return doc.split("\n")[0].strip()
    except (
        OSError,
        SyntaxError,
        ValueError,
    ):  # 单个 gate 文件读取/AST 解析失败返回 None（docstring 为可选元数据），不阻断同步
        pass
    return None


def _extract_blueprint_version(blueprint_path: Path) -> str | None:
    """_extract_blueprint_version implementation."""
    if not blueprint_path.exists():
        return None
    try:
        with open(blueprint_path, encoding="utf-8") as f:
            content = f.read()
        m = re.search(r'^\s*version\s*:\s*"?([\d.]+)"?\s*$', content, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(r'^\s*-\s*version\s*:\s*"?([\d.]+)"?\s*$', content, re.MULTILINE)
        if m:
            return m.group(1)
    except (OSError, ValueError):  # blueprint 读取/解码失败返回 None（版本号为可选元数据），不阻断同步
        pass
    return None


def _derive_gate_summary(gates: list[dict]) -> dict:
    """由 gates 列表派生第四册 summary（D-4/WP5：total/by_category/by_status 全派生）。

    计数按 gates 出现顺序生成键，保持册内既有排布（不重排=零无意义 diff）。
    """
    by_category: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for gate in gates:
        category = str(gate.get("category") or "uncategorized")
        status = str(gate.get("status") or "unknown")
        by_category[category] = by_category.get(category, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    return {"total": len(gates), "by_category": by_category, "by_status": by_status}


def _render_gate_summary(summary: dict) -> str:
    """渲染 summary 块文本（键序固定 total→by_category→by_status，保证两次运行字节一致）。"""
    lines = ["summary:", f"  total: {summary['total']}"]
    for group in ("by_category", "by_status"):
        lines.append(f"  {group}:")
        lines.extend(f"    {name}: {count}" for name, count in summary[group].items())
    return "\n".join(lines) + "\n"


def _apply_gate_status_aliases(text: str) -> str:
    """按 D-4 归一 gates 块内的非法 status（文本级，只碰 `status: <alias>` 行）。"""
    for illegal, legal in GATE_STATUS_ALIASES.items():
        text = re.sub(rf"(?m)^(\s*status: ){re.escape(illegal)}\s*$", rf"\g<1>{legal}", text)
    return text


def _gate_summary_diff(declared: dict, derived: dict) -> list[str]:
    """册内 summary 与派生 summary 的逐栏差异（用于红证/漂移报告）。"""
    rows = []
    for key in ("total", "by_category", "by_status"):
        if declared.get(key) != derived.get(key):
            rows.append(f"summary.{key}: 册内 {declared.get(key)!r} ≠ 派生 {derived.get(key)!r}")
    return rows


def _derive_gate_registry_text(raw: str, stamp: str) -> tuple[str, dict, dict] | None:
    """归一 status → 派生 summary → 拼接派生段。

    Returns:
        (新文本, 派生 summary, 册内 declared)；gates 面不可用时返回 None
        （拒绝在坏输入面上派生）。
    """
    import yaml

    text = _apply_gate_status_aliases(raw)
    declared = yaml.safe_load(raw) or {}
    gates = (yaml.safe_load(text) or {}).get("gates")
    if not isinstance(gates, list):
        logger.error("gate registry: gates 非列表（type=%s），拒绝派生", type(gates).__name__)
        return None
    summary = _derive_gate_summary(gates)
    text = re.sub(_GATE_SUMMARY_BLOCK_RE, lambda _m: _render_gate_summary(summary), text, count=1)
    if _LAST_UPDATED_LINE_RE.search(text):
        text = _LAST_UPDATED_LINE_RE.sub(f"last_updated: {stamp!r}", text, count=1)
    else:
        text = re.sub(r"(?m)^gates:", f"last_updated: {stamp!r}\ngates:", text, count=1)
    return text, summary, declared


def _gate_drift_rows(declared: dict, summary: dict, stamp: str) -> list[str]:
    """派生前册内值 vs 派生值的逐栏差异（红证/漂移报告用）。"""
    rows = _gate_summary_diff(declared.get("summary") or {}, summary)
    if str(declared.get("last_updated")) != stamp:
        rows.append(f"last_updated: 册内 {declared.get('last_updated')!r} → 派生 {stamp!r}")
    return rows


def _gate_text_matches(text: str, raw: str) -> bool:
    """一致判定：完全相等，或仅 volatile ``last_updated`` 时戳差异（幂等跳写）。"""
    return text == raw or _LAST_UPDATED_LINE_RE.sub("", text) == _LAST_UPDATED_LINE_RE.sub("", raw)


def _write_gate_registry_text(path: Path, text: str, base_text: str) -> int:
    """派生文本写前自校验 + CAS 落盘（损坏/基底陈旧一律不落盘）。"""
    import yaml

    from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: PLC0415

    try:
        yaml.safe_load(text)  # 派生后自校验：损坏即不落盘（防写坏唯一输入面）
    except yaml.YAMLError as exc:
        logger.error("派生文本 YAML 自校验失败，拒绝落盘: %s", exc)
        return EXIT_ERROR
    try:
        safe_write_text(
            path,
            text,
            expected_base_sha256=content_sha256(base_text),
            repo_root=PROJECT_ROOT,
            newline="\n",
        )
    except (StaleWriteRefused, WriteVerificationError) as exc:  # 热文件 CAS/回读校验契约
        logger.error("gate registry 派生段拒写: %s", exc)
        return EXIT_ERROR
    return EXIT_PASS


def sync_gate_registry_derived(dry_run: bool = False) -> int:
    """第四册（rule_enforcement/_registry.yaml）派生段重生——WP5/D-4。

    契约：
    - ``gates`` 是唯一的输入面；``summary``（total/by_category/by_status）与
      ``last_updated`` 一律由它派生，禁手工维护（宪法 §9.5）；
    - status 归一（GATE_STATUS_ALIASES）先于派生，故 by_status 是归一后的现值；
    - 文本级局部替换，gates 块逐字节不动——禁 yaml.dump 整写本册（实测本册
      load→dump round-trip 与磁盘字节不等：12 处折行差异，会造出假 diff）；
    - last_updated 基准=**生成器写盘时刻的 UTC 日期**（现场先例两处：
      scripts/governance/d5_architecture/generators/align_panoramas.py:144
      ``now_utc().strftime("%Y-%m-%d")``；本册旧写入端 scripts/scaffold.py:943 也是
      写盘时刻戳）。时区口径经 now_utc() SSoT（RULE-SCHEMA-TZ 禁 datetime.now()/
      time.time()）。mtime 基准被否：工作区 mtime 是 checkout/他会话触碰时刻
      （实测 gate YAML 全为 2026-08-27 checkout 时刻，admission/ 子目录 2026-09-18），
      不承载内容真值；
    - 写盘走 ``safe_write_text``（热文件 CAS：base 陈旧拒写，防吞并发改）
      + ``newline="\\n"``（.gitattributes 钉 *.yaml eol=lf，行尾字节级约定）
      + volatile ``last_updated`` 行跳写（内容未变即不写 ⇒ 连跑两次零 diff，
      字段语义收敛为"内容最近一次实际再生时间"，P0② 生成器时间戳非幂等治本同款）。
    """
    path = REGISTRIES["gate"]
    if not path.exists():
        logger.error("gate registry 不存在: %s", path)
        return EXIT_FINDINGS
    on_disk = path.read_bytes().decode("utf-8")
    eol_drift = "\r\n" in on_disk
    raw = on_disk.replace("\r\n", "\n")
    stamp = now_utc().strftime("%Y-%m-%d")
    derived = _derive_gate_registry_text(raw, stamp)
    if derived is None:
        return EXIT_FINDINGS
    text, summary, declared = derived
    if _gate_text_matches(text, raw) and not eol_drift:
        logger.info("gate registry 派生段一致（gates=%d, last_updated=%s）— 无需改写", summary["total"], stamp)
        return EXIT_PASS

    for row in _gate_drift_rows(declared, summary, stamp) or ["summary 键序/行尾排布漂移（内容等值）"]:
        logger.warning("DRIFT: %s", row)
    if eol_drift:
        logger.warning("DRIFT: 磁盘行尾为 CRLF，.gitattributes 钉 *.yaml eol=lf → 归一为 LF")
    if dry_run:
        logger.info("[DRY-RUN] 将重生派生段（未写盘）→ %s", path)
        return EXIT_FINDINGS
    rc = _write_gate_registry_text(path, text, raw)
    if rc == EXIT_PASS:
        logger.info("已派生重生 gate registry summary/last_updated（gates=%d）→ %s", summary["total"], path)
    return rc


def sync_fle_gates(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing FLE gates to gate registry ===")
    gate_registry = _load_yaml(REGISTRIES["gate"])
    if not gate_registry:
        return EXIT_FINDINGS

    existing_ids = {g["gate_id"] for g in gate_registry.get("gates", [])}
    fle_gates = _discover_fle_gates()
    new_count = 0

    for fg in fle_gates:
        if fg["gate_id"] in existing_ids:
            logger.debug("Gate %s already registered, skipping", fg["gate_id"])
            continue
        gate_registry.setdefault("gates", []).append(fg)
        existing_ids.add(fg["gate_id"])
        new_count += 1

    if new_count == 0:
        logger.info("No new FLE gates to register")
        return EXIT_PASS

    # WP5/D-4 治本：原此处手工增量累加（cats[FLE_GATE_CATEGORY]=new_count+旧值、
    # stats["active"]+=new_count、last_updated 硬编码 "2026-05-08"）是派生面漂移的
    # 根因之一——改为整体由 gates 派生。
    gate_registry["summary"] = _derive_gate_summary(gate_registry["gates"])
    gate_registry["last_updated"] = now_utc().strftime("%Y-%m-%d")

    if _save_yaml(REGISTRIES["gate"], gate_registry, dry_run):
        logger.info("Registered %d new FLE gates", new_count)
        return EXIT_PASS
    return EXIT_FINDINGS


def sync_versions(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing blueprint/module versions ===")
    bp_version = _extract_blueprint_version(FLE_BLUEPRINT)
    if not bp_version:
        logger.warning("Could not extract version from %s", FLE_BLUEPRINT)
        return EXIT_FINDINGS

    errors = 0

    module_reg = _load_yaml(REGISTRIES["module"])
    if module_reg:
        for mod in module_reg.get("modules", []):
            if mod.get("module_id") == FLE_MODULE_ID:
                old = mod.get("blueprint", {}).get("version", "?")
                if old != bp_version:
                    mod.setdefault("blueprint", {})["version"] = bp_version
                    logger.info("module-registry: %s %s -> %s", FLE_MODULE_ID, old, bp_version)
                break
        module_reg["last_updated"] = "2026-05-08"
        if not _save_yaml(REGISTRIES["module"], module_reg, dry_run):
            errors += 1

    bp_reg = _load_yaml(REGISTRIES["blueprint"])
    if bp_reg:
        for bp in bp_reg.get("blueprints", []):
            if bp.get("module_id") == FLE_MODULE_ID:
                old = bp.get("version", "?")
                if old != bp_version:
                    bp["version"] = bp_version
                    logger.info("blueprint-registry: %s %s -> %s", FLE_MODULE_ID, old, bp_version)
                break
        bp_reg["registry"]["last_updated"] = "2026-05-08"
        if not _save_yaml(REGISTRIES["blueprint"], bp_reg, dry_run):
            errors += 1

    return errors


def _extract_dependencies(py_file: Path) -> list[dict]:
    """_extract_dependencies implementation."""
    deps = []
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return deps

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.append({"module": alias.name, "alias": alias.asname})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                deps.append({"module": node.module, "level": node.level})

    return deps


def sync_dependencies(dry_run: bool = False) -> int:
    """Synchronize target with source of truth."""
    logger.info("=== Syncing cross-module dependencies ===")
    dep_registry = _load_yaml(REGISTRIES["cross_dep"])
    if not dep_registry:
        return EXIT_FINDINGS

    existing_sources = set()
    for d in dep_registry.get("dependencies", []):
        if d.get("source") == FLE_MODULE_ID:
            existing_sources.add(d.get("target", ""))

    scheduler_file = FEEDBACK_LOOP_DIR / "scheduler.py"
    if not scheduler_file.exists():
        logger.warning("scheduler.py not found")
        return EXIT_FINDINGS

    raw_deps = _extract_dependencies(scheduler_file)
    new_count = 0
    max_dep_id = 0
    for d in dep_registry.get("dependencies", []):
        try:
            num = int(d["dep_id"].replace("DEP-", ""))
            if num > max_dep_id:
                max_dep_id = num
        except (ValueError, KeyError):
            pass

    for dep in raw_deps:
        mod_name = dep["module"]
        if not mod_name.startswith("zephyr.feedback_loop"):
            continue
        target = mod_name.replace("zephyr.feedback_loop.", "").split(".")[0]
        target_id = f"fle-{target}"
        if target_id in existing_sources:
            continue

        max_dep_id += 1
        dep_entry = {
            "dep_id": f"DEP-{max_dep_id:03d}",
            "source": FLE_MODULE_ID,
            "source_name": "feedback-loop",
            "target": target_id,
            "target_name": target,
            "type": "runtime",
            "strength": "hard",
            "description": f"FLE scheduler imports from feedback-loop.{target}",
            "direction": "downstream",
            "valid_since": "2026-05-08",
        }
        dep_registry.setdefault("dependencies", []).append(dep_entry)
        existing_sources.add(target_id)
        new_count += 1

    dep_registry["last_updated"] = "2026-05-08"
    dep_registry["total_dependencies"] = len(dep_registry["dependencies"])
    summary = dep_registry.setdefault("summary", {})
    summary["total_dependencies"] = len(dep_registry["dependencies"])

    if new_count == 0:
        logger.info("No new dependencies to register")
        return EXIT_PASS

    if _save_yaml(REGISTRIES["cross_dep"], dep_registry, dry_run):
        logger.info("Registered %d new dependencies", new_count)
        return EXIT_PASS
    return EXIT_FINDINGS


def verify_init_all(dry_run: bool = False) -> int:
    """verify_init_all implementation."""
    logger.info("=== Verifying __init__.py __all__ completeness ===")
    errors = 0
    for pkg_dir in FEEDBACK_LOOP_DIR.iterdir():
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("_") or pkg_dir.name.startswith("."):
            continue
        if pkg_dir.name in ("tests", "docs"):
            continue
        init_file = pkg_dir / "__init__.py"
        if not init_file.exists():
            logger.warning("Missing __init__.py in %s", pkg_dir)
            errors += 1
            continue

        py_files = {f.stem for f in pkg_dir.glob("*.py") if f.name != "__init__.py"}
        try:
            with open(init_file, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except Exception:
            logger.error("Failed to parse %s", init_file)
            errors += 1
            continue

        all_list = None
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            all_list = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                        elif isinstance(node.value, (ast.ListComp, ast.Tuple)):
                            pass

        if all_list is None:
            logger.warning("%s: no __all__ found", init_file)
            errors += 1
            continue

        missing = py_files - set(all_list)
        extra = set(all_list) - py_files
        if missing:
            logger.info("%s: missing from __all__: %s", pkg_dir.name, sorted(missing))
        if extra:
            logger.debug("%s: extra in __all__ (no file): %s", pkg_dir.name, sorted(extra))

    return 1 if errors else 0


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Auto-sync all registries from source files")
    parser.add_argument("--sync-gates", action="store_true", help="Register FLE gates in gate registry")
    parser.add_argument(
        "--sync-gate-summary",
        action="store_true",
        help="派生重生第四册 summary/last_updated（WP5/D-4）；配 --dry-run 只做一致性校验",
    )
    parser.add_argument("--sync-versions", action="store_true", help="Sync blueprint versions across registries")
    parser.add_argument("--sync-deps", action="store_true", help="Sync cross-module dependencies")
    parser.add_argument("--verify-all", action="store_true", help="Verify __init__.py __all__ completeness")
    parser.add_argument("--all", action="store_true", help="Run all sync operations")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even on errors")
    args = parser.parse_args()

    run_all = args.all
    if not any(
        [args.sync_gates, args.sync_gate_summary, args.sync_versions, args.sync_deps, args.verify_all, args.all]
    ):
        parser.print_help()
        sys.exit(EXIT_PASS)

    total_errors = 0

    if run_all or args.sync_gates:
        total_errors += sync_fle_gates(dry_run=args.dry_run)
    if run_all or args.sync_gate_summary:
        total_errors += sync_gate_registry_derived(dry_run=args.dry_run)
    if run_all or args.sync_versions:
        total_errors += sync_versions(dry_run=args.dry_run)
    if run_all or args.sync_deps:
        total_errors += sync_dependencies(dry_run=args.dry_run)
    if run_all or args.verify_all:
        total_errors += verify_init_all(dry_run=args.dry_run)

    if args.dry_run:
        logger.info("[DRY-RUN] Complete — %d errors would occur", total_errors)
    elif total_errors == 0:
        logger.info("All registries synced successfully")
    else:
        logger.warning("Completed with %d errors", total_errors)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
