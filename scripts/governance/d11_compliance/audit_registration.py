# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/audit_registration.py | §
# [MODULE] scripts.governance.d11_compliance.audit_registration
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""audit_registration.py — 孤儿注册检测（RULE-TWO 防线 2）

扫描 src/zephyr/ 和 scripts/ 中所有 .py/.yaml 文件，
对比三个注册表（__init__.py __all__、script_manifest.yaml、_registry.yaml），
检测:
  - 孤儿文件: 存在于磁盘但不在任何注册表中
  - 僵尸引用: 注册表引用的文件已删除
  - __init__.py 缺 __all__: 有模块文件但包级 __init__.py 无 __all__

用法:
    python scripts/governance/d11_compliance/audit_registration.py           # 报告孤儿清单（全量）
    python scripts/governance/d11_compliance/audit_registration.py --full    # 显式全量扫描
    python scripts/governance/d11_compliance/audit_registration.py --incremental  # 仅扫描 git 变更文件
    python scripts/governance/d11_compliance/audit_registration.py --fix     # 交互式修复
    python scripts/governance/d11_compliance/audit_registration.py --full --save-baseline  # 保存当前孤儿为基线
    python scripts/governance/d11_compliance/audit_registration.py --incremental --baseline-aware  # 基线差分：仅 NEW 阻断

返回码:
    0 = CLEAN（无孤儿，或 --baseline-aware 模式下仅有 PERSISTENT 孤儿）
    1 = 发现孤儿（--baseline-aware 模式下仅有 NEW 孤儿时）
    2 = 扫描错误

设计基线:
    RULE-TWO 反孤儿功能
    可被 Pipeline Gate 调用（作为 G6 的一部分或独立门禁）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: audit_registration.py — 孤儿注册检测（RULE-TWO 防线 2）
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
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from _shared.constants import GATES_DIR, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

PROJECT_ROOT = REPO_ROOT
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SCRIPT_MANIFEST = SCRIPTS_DIR / "script_manifest.yaml"
GATE_REGISTRY = GATES_DIR / "_registry.yaml"

EXCLUDE_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "egg-info",
    ".ailocks",
    "session_logs",
    "_backup",
    "_archive",
}

EXCLUDE_SCRIPT_DIRS = {
    "governance",  # 治理脚本本身不注册到 manifest（由 generate_manifest.py 管理）
    "__pycache__",
}

# 这些文件是系统级别文件，不归模块注册表管
EXCLUDE_FROM_MODULE_AUDIT: set[str] = {
    "__init__.py",
    "conftest.py",
    "setup.py",
    "version.py",
    "py.typed",
}


@dataclass
class AuditResult:
    orphan_modules: list[OrphanEntry] = field(default_factory=list)
    orphan_scripts: list[OrphanEntry] = field(default_factory=list)
    orphan_gates: list[OrphanEntry] = field(default_factory=list)
    zombie_references: list[ZombieEntry] = field(default_factory=list)
    missing_all: list[Path] = field(default_factory=list)
    # 消费者地图：{full_module: [consumer_rel_paths]}，供下游消费者（如
    # analyze_orphan_consumers.py）复用，避免重复构建（向内收：单一真源）
    import_map: dict[str, list[str]] = field(default_factory=dict)
    # [MODULE] 头部路径不一致（ARCH-034 P4）
    module_path_mismatches: list[ModulePathMismatch] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """is_clean implementation."""
        return not any(
            [
                self.orphan_modules,
                self.orphan_scripts,
                self.orphan_gates,
                self.zombie_references,
                self.missing_all,
                self.module_path_mismatches,
            ]
        )

    @property
    def total_issues(self) -> int:
        """total_issues implementation."""
        return (
            len(self.orphan_modules)
            + len(self.orphan_scripts)
            + len(self.orphan_gates)
            + len(self.zombie_references)
            + len(self.missing_all)
            + len(self.module_path_mismatches)
        )


@dataclass
class OrphanEntry:
    path: Path
    relative: str
    package: str = ""
    suggestion: str = ""


@dataclass
class ZombieEntry:
    reference: str
    registry: str
    detail: str = ""


@dataclass
class ModulePathMismatch:
    """[MODULE] 头部声明的路径与实际磁盘路径不一致（ARCH-034 P4 防复发）。"""
    path: Path
    relative: str
    declared_module: str
    expected_module: str


# ---------------------------------------------------------------------------
# Finding 转换（接入 manage_baseline.py 基线差分机制）
# ---------------------------------------------------------------------------

# 基线存储路径（与 manage_baseline.py 的 _BASELINE_DIR 一致）
_BASELINE_DIR = PROJECT_ROOT / "scripts" / "governance" / "meta" / "baselines"
_AUDIT_BASELINE = _BASELINE_DIR / "audit_registration_baseline.jsonl"


def _to_findings(ar: AuditResult) -> list[dict]:
    """将 AuditResult 转换为 manage_baseline.py 的 Finding 格式。

    Finding schema: {dimension, target: {file_path}, description, severity}
    _finding_key = SHA256(dimension|target.file_path|description) 去重。
    """
    findings: list[dict] = []
    for oe in ar.orphan_modules:
        findings.append({
            "dimension": "D1_module_orphan",
            "target": {"file_path": oe.relative},
            "description": f"未注册模块: {oe.package}" if oe.package else f"未注册模块: {oe.relative}",
            "severity": "P2",
        })
    for oe in ar.orphan_scripts:
        findings.append({
            "dimension": "D2_script_orphan",
            "target": {"file_path": oe.relative},
            "description": f"未注册脚本: {oe.relative}",
            "severity": "P2",
        })
    for oe in ar.orphan_gates:
        findings.append({
            "dimension": "D3_gate_orphan",
            "target": {"file_path": oe.relative},
            "description": f"未注册门禁: {oe.relative}",
            "severity": "P2",
        })
    for ze in ar.zombie_references:
        findings.append({
            "dimension": "D4_zombie_reference",
            "target": {"file_path": ze.reference},
            "description": f"僵尸引用: {ze.registry} → {ze.reference}",
            "severity": "P2",
        })
    for p in ar.missing_all:
        rel = p.relative_to(PROJECT_ROOT).as_posix() if p.is_absolute() else str(p)
        findings.append({
            "dimension": "D5_missing_all",
            "target": {"file_path": rel},
            "description": f"__init__.py 缺 __all__: {rel}",
            "severity": "P2",
        })
    for mpm in ar.module_path_mismatches:
        findings.append({
            "dimension": "D6_module_path_mismatch",
            "target": {"file_path": mpm.relative},
            "description": f"[MODULE] 路径不一致: 声明={mpm.declared_module}, 期望={mpm.expected_module}",
            "severity": "P2",
        })
    return findings


# NOTE: _save_baseline（原 L206-242，manage_baseline.save_baseline 的逐行复制）已于
# 2026-06-26 删除并委托 meta.manage_baseline.write_jsonl_baseline（SSoT helper），
# 消除 save_baseline 三份重复。调用点见 main() 中 args.save_baseline 分支。


def _compare_with_baseline(findings: list[dict]) -> dict | None:
    """对比当前 findings 与基线，返回 NEW/RESOLVED/PERSISTENT 分类。

    返回 None 表示基线不存在（调用方应回退为全量阻断模式）。
    """
    if not _AUDIT_BASELINE.exists():
        return None

    import hashlib
    import json

    def _finding_key(f: dict) -> str:
        raw = f"{f.get('dimension', '')}|{f.get('target', {}).get('file_path', '')}|{f.get('description', '')}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    # 加载基线
    baseline_findings: list[dict] = []
    with open(_AUDIT_BASELINE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                baseline_findings.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    current_index = {_finding_key(f): f for f in findings}
    baseline_index = {_finding_key(f): f for f in baseline_findings}

    new_keys = set(current_index.keys()) - set(baseline_index.keys())
    resolved_keys = set(baseline_index.keys()) - set(current_index.keys())
    persistent_keys = set(current_index.keys()) & set(baseline_index.keys())

    classified: list[dict] = []
    for key in new_keys:
        f = dict(current_index[key])
        f["baseline_status"] = "NEW"
        classified.append(f)
    for key in resolved_keys:
        f = dict(baseline_index[key])
        f["baseline_status"] = "RESOLVED"
        classified.append(f)
    for key in persistent_keys:
        f = dict(current_index[key])
        f["baseline_status"] = "PERSISTENT"
        classified.append(f)

    return {
        "current_total": len(findings),
        "baseline_total": len(baseline_findings),
        "new_count": len(new_keys),
        "resolved_count": len(resolved_keys),
        "persistent_count": len(persistent_keys),
        "classified": classified,
    }


def audit(changed_files: set[Path] | None = None) -> AuditResult:
    """执行完整注册审计扫描。

    Args:
        changed_files: 增量模式下传入的变更文件集合。None 表示全量扫描。
    """
    result = AuditResult()

    # ── 1. 构建已注册集合 ──
    registered_modules = _build_module_registry()
    registered_scripts = _build_script_registry()
    registered_gates = _build_gate_registry()

    # ── 1.5 批量收集所有 import 语句（消费者地图）──
    # RULE-TWO 豁免原则：已有自然发现机制（被其他模块 import）的模块不报为 ORPHAN
    result.import_map = _batch_collect_imports()

    # ── 2. 扫描 src/zephyr/ 模块孤儿 ──
    _scan_module_orphans(registered_modules, result.import_map, result, changed_files)

    # ── 3. 扫描 scripts/ 脚本孤儿 ──
    _scan_script_orphans(registered_scripts, result, changed_files)

    # ── 4. 扫描 gates/ 门禁孤儿 ──
    _scan_gate_orphans(registered_gates, result, changed_files)

    # ── 5. 检测僵尸引用 ──
    _detect_zombie_references(registered_modules, registered_scripts, registered_gates, result)

    # ── 6. 检测缺 __all__ 的 __init__.py ──
    _detect_missing_all(result, changed_files)

    # ── 7. 校验 [MODULE] 头部路径一致性（ARCH-034 P4 防复发）──
    _check_module_path_consistency(result, changed_files)

    return result


# ===================================================================
# 注册表构建
# ===================================================================


def _build_module_registry() -> dict[str, set[str]]:
    """返回 {package_name: {module_name, ...}} 表示 __all__ 中已注册的模块。"""
    registry: dict[str, set[str]] = {}

    for init_py in SRC_ZEPHYR.rglob("__init__.py"):
        if any(ex in init_py.parts for ex in EXCLUDE_PATTERNS):
            continue

        rel = init_py.relative_to(SRC_ZEPHYR)
        pkg_name = rel.parent.as_posix().replace("\\", "/").replace("/", ".")

        content = init_py.read_text(encoding="utf-8")

        all_entries = _extract_all_entries(content)
        registry[pkg_name] = all_entries

    return registry


def _extract_all_entries(source: str) -> set[str]:
    """从 __init__.py 源码中提取 __all__ 列表。"""
    entries: set[str] = set()

    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            # Handle both __all__ = [...] and __all__: list[str] = [...]
            all_value = None
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        all_value = node.value
                        break
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                    all_value = node.value
            if all_value is not None and isinstance(all_value, (ast.List, ast.Tuple)):
                for elt in all_value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        entries.add(elt.value)
    except SyntaxError:
        pattern = r'"([^"]+)"'
        for match in re.finditer(pattern, source):
            entries.add(match.group(1))

    return entries


def _build_script_registry() -> set[str]:
    """从 script_manifest.yaml 中提取已注册的脚本路径集合。"""
    if not SCRIPT_MANIFEST.exists():
        return set()

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])
    return {s.get("path", "") for s in scripts if s.get("path")}


def _build_gate_registry() -> set[str]:
    """从 _registry.yaml 中提取已注册的 gate 文件名集合。"""
    # ARCH-036 P3-C4: 静默失效修正 — 返回空 set 会让调用方认为"无注册 gate"，
    # 导致 gate 孤儿检测整体失效。改为 stderr 警告（与 GATES_DIR 处理一致）。
    if not GATE_REGISTRY.exists():
        print(f"[WARN] GATE_REGISTRY not found: {GATE_REGISTRY} — gate registry scan skipped", file=sys.stderr)
        return set()

    registry_data = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry_data.get("gates", [])
    return {g.get("file", "") for g in gates if g.get("file")}


def _batch_collect_imports() -> dict[str, list[str]]:
    """批量收集所有 import 语句，构建 {module: [consumer_files]} 映射。

    用于 RULE-TWO 豁免判定：被其他模块 import 的模块视为"已有自然发现机制"，
    不报为 ORPHAN（即使未注册到 __all__）。

    优先使用 rg（快速），rg 不可用时自动回退到 Python ast 解析（零外部依赖，
    消除 rg 不在 PATH 时静默返回空 map → RULE-TWO 豁免失效 → 误报 orphan 的脆弱性）。

    匹配模式:
        from zephyr.X.Y.Z import ...
        import zephyr.X.Y.Z

    Returns:
        {full_module_path: [consumer_file_paths]}
    """
    import re as _re
    from collections import defaultdict

    pattern = r"(?:from\s+(zephyr[\w.]*))\s+import|(?:import\s+(zephyr[\w.]*))"
    consumers: dict[str, list[str]] = defaultdict(list)

    # ── 快速路径：rg ──
    try:
        # 纳入项目根目录的 .py（如 sitecustomize.py）——这些是系统级消费者，
        # 仅扫 src/scripts/tests 会漏掉根级导入，导致 RULE-TWO 豁免误判（治本 Bug 2：
        # 当某模块唯一消费者位于根级时，豁免失效 → 误报 orphan）。
        # 用相对路径（posix）传给 rg：若传绝对路径 D:\...，rg 输出含盘符冒号，
        # 下游 line.split(":", 2) 会把盘符冒号当首分隔符 → consumer_file 被截成 "D"。
        root_py_files = [p.relative_to(PROJECT_ROOT).as_posix() for p in PROJECT_ROOT.glob("*.py")]
        result = subprocess.run(
            ["rg", "--no-heading", "-n", "-e", pattern, "src/", "scripts/", "tests/"]
            + root_py_files,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                consumer_file = parts[0]
                content = parts[2]
                match = _re.search(pattern, content)
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        consumers[module].append(consumer_file)
        return dict(consumers)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"INFO: rg 不可用，回退到 Python ast 解析（零外部依赖）: {e}", file=sys.stderr)

    # ── 回退路径：Python ast 解析 ──
    return _collect_imports_via_ast()


def _collect_imports_via_ast() -> dict[str, list[str]]:
    """使用 Python ast 解析 .py 文件的 import 语句，构建消费者地图。

    rg 不可用时的零外部依赖回退方案。扫描范围与 rg 路径一致：
    src/、scripts/、tests/ 目录及根级 *.py 文件。

    匹配模式（与 rg 正则一致）:
        from zephyr.X.Y.Z import ...
        import zephyr.X.Y.Z

    Returns:
        {full_module_path: [consumer_file_relative_paths]}
    """
    from collections import defaultdict

    consumers: dict[str, list[str]] = defaultdict(list)

    # 收集要扫描的 .py 文件（与 rg 扫描范围一致）
    py_files: list[Path] = []
    for dir_name in ("src", "scripts", "tests"):
        d = PROJECT_ROOT / dir_name
        if d.is_dir():
            for py_file in d.rglob("*.py"):
                if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
                    continue
                py_files.append(py_file)
    # 根级 .py 文件（如 sitecustomize.py）
    for py_file in PROJECT_ROOT.glob("*.py"):
        py_files.append(py_file)

    for py_file in py_files:
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

        try:
            rel_path = py_file.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            rel_path = str(py_file)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("zephyr."):
                        consumers[alias.name].append(rel_path)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("zephyr."):
                    consumers[node.module].append(rel_path)

    return dict(consumers)


# ===================================================================
# 孤儿扫描
# ===================================================================


def _scan_module_orphans(
    registered: dict[str, set[str]],
    import_map: dict[str, list[str]],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 src/zephyr/ 下所有 .py 文件，找出不在 __all__ 中且无消费者的。

    RULE-TWO 豁免原则：被其他模块 import 的模块视为"已有自然发现机制"，
    不报为 ORPHAN（即使未注册到 __all__）。

    Args:
        registered: {package: {module_names}} 来自 __all__
        import_map: {full_module: [consumer_files]} 来自批量 Grep
        result: 审计结果
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    for py_file in SRC_ZEPHYR.rglob("*.py"):
        if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
            continue
        if py_file.name in EXCLUDE_FROM_MODULE_AUDIT:
            continue
        if py_file.name.startswith("_"):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and py_file not in changed_files:
            continue

        rel = py_file.relative_to(SRC_ZEPHYR)
        rel_str = rel.as_posix()
        parts = rel.parts

        pkg = ".".join(parts[:-1]) if len(parts) > 1 else ""
        module_name = py_file.stem

        if pkg not in registered:
            result.orphan_modules.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    package=pkg,
                    suggestion=f"Package '{pkg}' 的 __init__.py 不包含任何 __all__ 条目",
                )
            )
            continue

        class_name = "".join(p.capitalize() for p in module_name.split("_"))
        if module_name not in registered[pkg] and class_name not in registered[pkg]:
            # RULE-TWO 豁免：检查是否有消费者（被其他模块 import）
            full_module = "zephyr." + ".".join(parts[:-1] + (module_name,)) if parts[:-1] else "zephyr." + module_name
            consumer_files = import_map.get(full_module, [])
            # 排除自身
            consumer_files = [c for c in consumer_files if not c.endswith(rel_str)]
            if consumer_files:
                # 有消费者 = 已有自然发现机制 = 豁免
                continue

            pkg_dotted = pkg.replace('/', '.').replace('\\', '.')
            result.orphan_modules.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    package=pkg,
                    suggestion=(
                        f"from zephyr.{pkg_dotted}.{module_name} import {class_name}"
                    ),
                )
            )


def _scan_script_orphans(
    registered: set[str],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 scripts/ 下所有 .py 文件，找出不在 script_manifest.yaml 中的。

    Args:
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    for py_file in SCRIPTS_DIR.rglob("*.py"):
        if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and py_file not in changed_files:
            continue

        rel = py_file.relative_to(SCRIPTS_DIR)
        rel_str = rel.as_posix()

        parts = rel.parts
        if parts and parts[0] in EXCLUDE_SCRIPT_DIRS:
            continue

        if rel_str not in registered:
            result.orphan_scripts.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    suggestion=f"python scripts/scaffold.py script {rel.with_suffix('').as_posix()}",
                )
            )


def _scan_gate_orphans(
    registered: set[str],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 gates/ 下所有 .yaml 文件，找出不在 _registry.yaml 中的。

    Args:
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    if not GATES_DIR.is_dir():
        return

    for yaml_file in GATES_DIR.glob("*.yaml"):
        if yaml_file.name.startswith("_"):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and yaml_file not in changed_files:
            continue

        if yaml_file.name not in registered:
            result.orphan_gates.append(
                OrphanEntry(
                    path=yaml_file,
                    relative=yaml_file.name,
                    suggestion=f"python scripts/scaffold.py gate {yaml_file.stem.upper()}",
                )
            )


# ===================================================================
# 僵尸引用检测
# ===================================================================


def _detect_zombie_references(
    module_registry: dict[str, set[str]],
    script_registry: set[str],
    gate_registry: set[str],
    result: AuditResult,
) -> None:
    """检测注册表中引用了已删除文件的条目。"""
    # Script manifest
    if SCRIPT_MANIFEST.exists():
        manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
        for entry in manifest.get("scripts", []):
            path_str = entry.get("path", "")
            if path_str and not (SCRIPTS_DIR / path_str).exists():
                result.zombie_references.append(
                    ZombieEntry(
                        reference=path_str,
                        registry="script_manifest.yaml",
                        detail=entry.get("description", ""),
                    )
                )

    # Gate registry
    if GATE_REGISTRY.exists():
        registry_data = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
        for entry in registry_data.get("gates", []):
            file_name = entry.get("file", "")
            if file_name and not (GATES_DIR / file_name).exists():
                result.zombie_references.append(
                    ZombieEntry(
                        reference=f"gate_id={entry.get('gate_id', '?')}",
                        registry="_registry.yaml",
                        detail=f"file={file_name}, title={entry.get('title', '')}",
                    )
                )


# ===================================================================
# __init__.py 缺 __all__
# ===================================================================


def _detect_missing_all(result: AuditResult, changed_files: set[Path] | None = None) -> None:
    """检测有 .py 模块但包级 __init__.py 无 __all__ 的包。

    Args:
        changed_files: 增量模式下仅扫描此集合中文件所属的 __init__.py。None 表示全量扫描。
    """
    for init_py in SRC_ZEPHYR.rglob("__init__.py"):
        if any(ex in init_py.parts for ex in EXCLUDE_PATTERNS):
            continue
        # 增量模式：仅检查变更文件所在目录的 __init__.py，或 __init__.py 自身变更
        if changed_files is not None:
            parent_dir = init_py.parent
            relevant = any(cf == init_py or cf.parent == parent_dir for cf in changed_files)
            if not relevant:
                continue

        pkg_dir = init_py.parent
        py_files = [
            f for f in pkg_dir.glob("*.py") if f.name not in EXCLUDE_FROM_MODULE_AUDIT and not f.name.startswith("_")
        ]

        if not py_files:
            continue

        content = init_py.read_text(encoding="utf-8")
        if "__all__" not in content:
            result.missing_all.append(init_py)


# ===================================================================
# [MODULE] 头部路径一致性校验（ARCH-034 P4）
# ===================================================================


# [MODULE] 头部解析正则（与 check_ssot_gate.py GATE-SSOT 第1层一致）
_RE_MODULE_HEADER = re.compile(r"^#\s*\[MODULE\]\s*(.+)$", re.MULTILINE)


def _check_module_path_consistency(
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """校验 .py 文件头部 [MODULE] 声明的路径与实际磁盘路径一致。

    防止迁移后 [MODULE] 头部残留旧路径（如 ARCH-034 BA→GDD 迁移后
    brain_integration.py 仍声明 behavioral_auditor 路径）。

    Args:
        changed_files: 增量模式下仅扫描此集合。None 表示全量扫描。
    """
    for py_file in SRC_ZEPHYR.rglob("*.py"):
        if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and py_file not in changed_files:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        match = _RE_MODULE_HEADER.search(content)
        if not match:
            continue  # 无 [MODULE] 头部，跳过

        declared_module = match.group(1).strip()

        # 从实际磁盘路径推导 expected module path
        rel = py_file.relative_to(SRC_ZEPHYR)
        parts = rel.parts
        if py_file.name == "__init__.py":
            expected = "zephyr." + ".".join(parts[:-1]) if len(parts) > 1 else "zephyr"
        else:
            stem = py_file.stem
            expected = (
                "zephyr." + ".".join(parts[:-1] + (stem,))
                if len(parts) > 1
                else f"zephyr.{stem}"
            )

        if declared_module != expected:
            result.module_path_mismatches.append(
                ModulePathMismatch(
                    path=py_file,
                    relative=py_file.relative_to(PROJECT_ROOT).as_posix(),
                    declared_module=declared_module,
                    expected_module=expected,
                )
            )


# ===================================================================
# 格式化输出
# ===================================================================


def print_report(ar: AuditResult, compact: bool = False) -> str:
    """格式化审计报告。"""
    lines: list[str] = []

    total = ar.total_issues
    status = "CLEAN" if ar.is_clean else f"ISSUES ({total})"
    lines.append(f"\n{'=' * 60}")
    lines.append(f"  RULE-TWO 注册审计: {status}")
    lines.append(f"{'=' * 60}")

    if ar.is_clean:
        lines.append("\n  No orphan files detected — all modules registered.")
        return "\n".join(lines)

    if ar.orphan_modules:
        lines.append(f"\n  ORPHAN MODULES ({len(ar.orphan_modules)}):")
        for oe in ar.orphan_modules:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.orphan_scripts:
        lines.append(f"\n  ORPHAN SCRIPTS ({len(ar.orphan_scripts)}):")
        for oe in ar.orphan_scripts:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.orphan_gates:
        lines.append(f"\n  ORPHAN GATES ({len(ar.orphan_gates)}):")
        for oe in ar.orphan_gates:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.missing_all:
        lines.append(f"\n  MISSING __all__  ({len(ar.missing_all)}):")
        for p in ar.missing_all:
            rel = p.relative_to(PROJECT_ROOT).as_posix()
            lines.append(f"    {rel}")

    if ar.zombie_references:
        lines.append(f"\n  ZOMBIE REFERENCES ({len(ar.zombie_references)}):")
        for ze in ar.zombie_references:
            lines.append(f"    {ze.reference} → [{ze.registry}] {ze.detail}")

    if ar.module_path_mismatches:
        lines.append(f"\n  MODULE PATH MISMATCH ({len(ar.module_path_mismatches)}):")
        for mpm in ar.module_path_mismatches:
            lines.append(f"    {mpm.relative}")
            if not compact:
                lines.append(f"      → declared: {mpm.declared_module}")
                lines.append(f"      → expected: {mpm.expected_module}")

    lines.append(f"\n  TOTAL: {total} issues")
    return "\n".join(lines)


# ===================================================================
# 增量扫描支持
# ===================================================================


def _in_audit_scope(rel_str: str) -> bool:
    """判断相对路径是否在审计范围内（单一真源，勿重复实现）。

    审计范围：仅 ``src/zephyr/`` 与 ``scripts/`` 下文件。
    ``tests/``、``docs/``、根级等其他目录不扫。

    ``--incremental``、``--files``、post-commit reconciler 三处 scope 过滤
    统一委托本函数，避免分散实现导致漂移。
    """
    return rel_str.startswith("src/zephyr/") or rel_str.startswith("scripts/")


def _get_changed_files_from_git() -> set[Path]:
    """通过 git diff 获取相对于 HEAD 的变更文件集合。

    包含已暂存和未暂存的变更，以及未跟踪的新文件。
    scope 过滤委托 ``_in_audit_scope()`` 单一真源。
    """
    changed: set[Path] = set()
    try:
        # 已跟踪文件的变更（已暂存 + 未暂存）
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    p = PROJECT_ROOT / line
                    if p.exists():
                        changed.add(p)

        # 未跟踪的新文件
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    p = PROJECT_ROOT / line
                    if p.exists():
                        changed.add(p)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARNING: git diff 失败，回退到全量扫描: {e}", file=sys.stderr)
        return set()

    # scope 过滤委托 _in_audit_scope() 单一真源
    filtered: set[Path] = set()
    for p in changed:
        try:
            rel_str = p.relative_to(PROJECT_ROOT).as_posix()
            if _in_audit_scope(rel_str):
                filtered.add(p)
        except ValueError:
            continue

    return filtered


def _build_changed_files_from_paths(paths: list[str]) -> set[Path]:
    """从显式路径列表构建变更文件集合（供 post-commit reconciler 传入 committed_files）。

    治本 Bug 1：``--incremental`` 用 ``git diff HEAD`` + ``git ls-files --others`` 推导
    changed_files，会扫到**工作树全部 WIP**而非本次 commit 的文件。post-commit
    reconciler 应改用本函数接收精确的 committed_files，避免对无关 WIP 误报 NEW orphan。

    过滤规则委托 ``_in_audit_scope()`` 单一真源。
    接受绝对或相对路径（相对路径相对于 PROJECT_ROOT）。

    Args:
        paths: 文件路径列表（绝对或相对）。

    Returns:
        绝对路径集合，仅含 src/zephyr/ 和 scripts/ 下且磁盘存在的文件。
    """
    changed: set[Path] = set()
    for p in paths:
        path = Path(p)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if not path.exists():
            continue
        try:
            rel_str = path.relative_to(PROJECT_ROOT).as_posix()
            if _in_audit_scope(rel_str):
                changed.add(path)
        except ValueError:
            continue
    return changed


# ===================================================================
# CLI
# ===================================================================


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="RULE-TWO 注册审计——检测孤儿模块/脚本/门禁",
    )
    scan_mode = parser.add_mutually_exclusive_group()
    scan_mode.add_argument("--full", action="store_true", help="全量扫描（默认）")
    scan_mode.add_argument("--incremental", action="store_true", help="增量扫描：仅扫描 git 变更文件（git diff HEAD + 未跟踪）")
    scan_mode.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="显式指定变更文件集合（绝对或相对路径），替代 --incremental 的 git diff 推导。"
        "供 post-commit reconciler 传入精确 committed_files，避免扫描无关 WIP（治本："
        "--incremental 会扫到工作树全部 WIP 而非本次 commit 的文件）。",
    )
    parser.add_argument("--compact", action="store_true", help="紧凑输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出（供 AI/MCP 消费）")
    parser.add_argument("--fix", action="store_true", help="交互式修复孤儿")
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="将当前 findings 保存为基线（用于初始化存量孤儿快照）",
    )
    parser.add_argument(
        "--baseline-aware",
        action="store_true",
        help="差分模式（--incremental 或 --files）下对比基线：仅 NEW 孤儿阻断(exit 1)，"
        "PERSISTENT 孤儿降级为告警(exit 0)",
    )
    args = parser.parse_args()

    # 确定扫描模式
    changed_files: set[Path] | None = None
    differential = False  # 差分模式：--incremental 或 --files（用于 --baseline-aware 判定）
    try:
        if args.files:
            # 显式文件列表（供 post-commit reconciler 传入精确 committed_files，
            # 避免 --incremental 的 git diff 扫到无关 WIP——治本 Bug 1）
            changed_files = _build_changed_files_from_paths(args.files)
            differential = True
            if not changed_files:
                print("[FILES] 传入文件均不在 src/zephyr/ 或 scripts/ 下，扫描结果为空（CLEAN）", file=sys.stderr)
                ar = AuditResult()
            else:
                print(f"[FILES] 显式指定 {len(changed_files)} 个变更文件，仅扫描这些文件", file=sys.stderr)
                ar = audit(changed_files=changed_files)
        elif args.incremental:
            changed_files = _get_changed_files_from_git()
            differential = True
            if not changed_files:
                print("[INCREMENTAL] 无变更文件或 git 不可用，扫描结果为空（CLEAN）", file=sys.stderr)
                # 无变更文件 = 无新增孤儿 = CLEAN
                ar = AuditResult()
            else:
                print(f"[INCREMENTAL] 检测到 {len(changed_files)} 个变更文件，仅扫描这些文件", file=sys.stderr)
                ar = audit(changed_files=changed_files)
        else:
            ar = audit()
    except Exception as e:
        print(f"ERROR: 审计失败: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # ── --save-baseline 模式：保存基线后 exit 0 ──
    # DRY：委托 meta.manage_baseline.write_jsonl_baseline（SSoT helper，原 _save_baseline 复制已删除）
    if args.save_baseline:
        from datetime import UTC, datetime

        from meta.manage_baseline import write_jsonl_baseline

        findings = _to_findings(ar)
        ts_str = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        meta = write_jsonl_baseline(
            findings,
            baseline_dir=_BASELINE_DIR,
            versioned_prefix="audit_registration",
            current_path=_AUDIT_BASELINE,
            meta_path=None,
            source_label="audit_registration.py --save-baseline",
            label=f"audit_registration-{ts_str}",
            ts_str=ts_str,
        )
        print(f"[BASELINE] 已保存 {meta['finding_count']} 条 findings 为基线")
        print(f"  文件: {meta['file']}")
        print(f"  时间: {meta['saved_at']}")
        sys.exit(EXIT_PASS)

    # ── --baseline-aware 模式：差分扫描对比基线 ──
    if args.baseline_aware and differential:
        findings = _to_findings(ar)
        comparison = _compare_with_baseline(findings)

        if comparison is None:
            # 基线不存在 → 回退为全量阻断 + 提示
            if not ar.is_clean:
                print(
                    f"[WARN] 基线不存在，无法区分 NEW/PERSISTENT。"
                    f"当前 {ar.total_issues} 条 findings 全部按阻断处理。"
                    f"请运行 --save-baseline 初始化基线。",
                    file=sys.stderr,
                )
            # 回退为当前行为（exit 1 if any findings）
            print(print_report(ar, compact=args.compact))
            sys.exit(EXIT_PASS if ar.is_clean else EXIT_FINDINGS)

        # 基线存在 → 分类输出
        new_findings = [f for f in comparison["classified"] if f["baseline_status"] == "NEW"]
        persistent_findings = [f for f in comparison["classified"] if f["baseline_status"] == "PERSISTENT"]
        resolved_findings = [f for f in comparison["classified"] if f["baseline_status"] == "RESOLVED"]

        print(f"\n{'=' * 60}")
        print(f"  RULE-TWO 注册审计（基线差分模式）")
        print(f"{'=' * 60}")
        print(f"  当前: {comparison['current_total']}, 基线: {comparison['baseline_total']}")
        print(f"  🆕 NEW: {comparison['new_count']}（阻断）")
        print(f"  ✅ RESOLVED: {comparison['resolved_count']}（已解决）")
        print(f"  🔄 PERSISTENT: {comparison['persistent_count']}（存量，不阻断）")

        if new_findings:
            print(f"\n  [NEW] 本次变更新引入的孤儿（必须修复）:")
            for f in new_findings:
                fp = f.get("target", {}).get("file_path", "?")
                desc = f.get("description", "")[:100]
                print(f"    {fp}: {desc}")

        if persistent_findings:
            print(f"\n  [PERSISTENT] 存量孤儿（不阻断，需后续专项治理）:")
            for f in persistent_findings[:20]:
                fp = f.get("target", {}).get("file_path", "?")
                print(f"    {fp}")
            if len(persistent_findings) > 20:
                print(f"    ...（共 {len(persistent_findings)} 个）")

        if resolved_findings:
            print(f"\n  [RESOLVED] 本次变更解决的存量孤儿:")
            for f in resolved_findings[:10]:
                fp = f.get("target", {}).get("file_path", "?")
                print(f"    {fp}")
            if len(resolved_findings) > 10:
                print(f"    ...（共 {len(resolved_findings)} 个）")

        print(f"\n{'=' * 60}")
        # 仅 NEW > 0 时 exit 1；PERSISTENT only → exit 0
        sys.exit(EXIT_FINDINGS if comparison["new_count"] > 0 else EXIT_PASS)

    # ── 默认输出模式（无 baseline-aware）──
    if args.json:
        import json

        output = {
            "orphan_modules": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_modules],
            "orphan_scripts": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_scripts],
            "orphan_gates": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_gates],
            "missing_all": [p.relative_to(PROJECT_ROOT).as_posix() for p in ar.missing_all],
            "zombie_references": [
                {"reference": ze.reference, "registry": ze.registry, "detail": ze.detail} for ze in ar.zombie_references
            ],
            "module_path_mismatches": [
                {"relative": mpm.relative, "declared": mpm.declared_module, "expected": mpm.expected_module}
                for mpm in ar.module_path_mismatches
            ],
            "total_issues": ar.total_issues,
            # 消费者地图：供下游复用，避免重复构建（analyze_orphan_consumers.py 等）
            "import_map": ar.import_map,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(print_report(ar, compact=args.compact))

    if args.fix and not ar.is_clean:
        _interactive_fix(ar)

    sys.exit(EXIT_PASS if ar.is_clean else EXIT_FINDINGS)


def _interactive_fix(ar: AuditResult) -> None:
    """交互式修复孤儿文件——将 orphan 注册到对应注册表。"""
    print("\n--- 交互式修复 ---")
    print("输入 'y' 自动注册, 'n' 跳过, 'd' 删除孤儿文件, 'q' 退出\n")

    for oe in ar.orphan_modules:
        choice = input(f"  注册模块 {oe.relative}? [y/n/d/q] ").strip().lower()
        if choice == "q":
            break
        elif choice == "d":
            oe.path.unlink()
            print(f"    DELETED {oe.relative}")
        elif choice == "y":
            _auto_register_module(oe)
        else:
            print("    SKIPPED")

    for oe in ar.orphan_scripts:
        choice = input(f"  注册脚本 {oe.relative}? [y/n/d/q] ").strip().lower()
        if choice == "q":
            break
        elif choice == "d":
            oe.path.unlink()
            print(f"    DELETED {oe.relative}")
        elif choice == "y":
            _auto_register_script(oe)
        else:
            print("    SKIPPED")


def _auto_register_module(oe: OrphanEntry) -> None:
    """自动将模块注册到 __init__.py（DM-367 约定：注册 module_name 而非 class_name）。

    治本（OPS-A3）：
      - 不再臆造 PascalCase class_name（原 L961 假设模块导出同名类，对纯模块注册错误）
      - 注册 module_name 到 __all__（与 shared/contracts/__init__.py DM-367 段一致）
      - 修复 regex（原 L971 `\\[__all__` 匹配字面量 `[__all__`，永远失败）
      - __all__ 无法机械定位时降级为提示，不写坏文件
    """
    pkg_path = SRC_ZEPHYR / oe.package.replace(".", "/")
    init_py = pkg_path / "__init__.py"
    module_name = oe.path.stem

    if not init_py.exists():
        print(f'    HINT: {init_py} 不存在，需手动创建并声明 __all__ 含 "{module_name}"')
        return

    content = init_py.read_text(encoding="utf-8")
    changed = False

    # 1. 确保 `from . import <module_name>` 存在（DM-367 re-export 约定）
    import_line = f"from . import {module_name}"
    if import_line not in content:
        if "__all__" in content:
            idx = content.index("__all__")
            content = content[:idx] + import_line + "\n" + content[idx:]
        else:
            content += f"\n{import_line}\n"
        changed = True

    # 2. 注册 module_name 到 __all__
    if f'"{module_name}"' in content or f"'{module_name}'" in content:
        pass  # 已注册
    elif "__all__" in content:
        # 修复后的 regex：匹配 __all__ = [...]（原 `\[__all__` 误匹配字面量 `[__all__`）
        pattern = r"(__all__\s*=\s*\[)(.*?)(\])"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            mid = match.group(2)
            entries = [e.strip().strip('"').strip("'") for e in mid.split(",") if e.strip()]
            entries.append(module_name)
            new_mid = "\n    " + ",\n    ".join(f'"{e}"' for e in entries) + ",\n"
            content = content[: match.start(2)] + new_mid + content[match.end(2) :]
            changed = True
        else:
            # __all__ 存在但无法机械定位（如 __all__.append 模式），追加 append
            content += f'\n__all__.append("{module_name}")\n'
            changed = True
    else:
        content += f'\n__all__ = [\n    "{module_name}",\n]\n'
        changed = True

    if not changed:
        print(f"    SKIP {module_name}（已注册于 {init_py}）")
        return

    atomic_write(init_py, content)
    print(f"    REGISTERED {module_name} → {init_py}")


def _auto_register_script(oe: OrphanEntry) -> None:
    """自动将脚本注册到 script_manifest.yaml——委托 canonical generator。

    治本（OPS-A3）：不再手动 yaml.dump（会丢弃 # Auto-generated 头注释并重排格式，
    与 generate_manifest.py 输出不一致），改为调用 generate_manifest.py 全量重生成，
    保证 SSoT 一致性。
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_manifest.py")],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    if result.returncode == 0:
        print(f"    REGISTERED {oe.relative} → script_manifest.yaml (via generate_manifest.py)")
    else:
        print(f"    ERROR: generate_manifest.py 失败: {result.stderr}", file=sys.stderr)


if __name__ == "__main__":
    main()
