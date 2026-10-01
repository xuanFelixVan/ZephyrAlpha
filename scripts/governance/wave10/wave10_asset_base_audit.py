# [BLUEPRINT] MOD-GOV-WAVE10-ASSET-BASE-AUDIT | docs/_working/total_command_closeout/wave10/wave10_base_audit_and_ga_wiring.md
# [MODULE] scripts.governance.wave10.wave10_asset_base_audit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib(ast/re/subprocess/pathlib/collections); pyyaml(仅输出序列化); git CLI(只读 ls-tree/diff)
# [CONSUMERS] docs/_working/total_command_closeout/wave10/wave10_base_audit_and_ga_wiring.md §1 底数表; 波10 G-A.1 盘点表; 总包排产判据（人工/编排调用，无自动触发）
# [STARTUP] manual
#   （原值 standalone_only——GATE-VOCAB 词表归正 manual）
# [MATURITY] experimental
# [INVARIANTS] 只读全仓扫描；零数据库访问（不 import zephyr 业务包，避车道 PYTHONPATH 假绿源）；唯一写面=案卷目录 wave10_asset_base_audit.yaml；在册判据=装饰性接线（仅 TYPE_CHECKING 边 / 有 import 但不在生产闭包）一律判未接；计数一律机械产出禁手工；PROD_ROOTS 显式声明且带真源指针，改动需同批改案卷；生产闭包=自 PROD_ROOTS 沿 runtime import 边的可达集（TYPE_CHECKING 边不入闭包）；本件不点火任何跑批、不写 config/**、不写 docs/01_policies_and_standards/**
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可得->RuntimeError；仓根缺失->RuntimeError；案卷输出目录不可写->IOError 上抛（禁静默降级）；registry YAML/文本读失败->RuntimeError（禁按缺数出表）
# [TESTS] 无 pytest 件（一次性审计生成器）；出口判据=重跑后 yaml 的 cluster.file_count==实数、candle 目录行数==盘点实数、frozen_files_diff 全 clean
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""波 10 底数复核生成器（W-117 终审版 G-A.1 前置：先数实存，再谈接线）.

三簇 x 三列（实存模块数 / 是否在 HEAD / 是否被生产路径消费）机读表，外加：
  1. 蜡烛目录（PAT-CANDLE-*）在册 x 实现 x 静态可数三面计数；
  2. 冻结 prereg 件 diff 证据（G-A.4 出口判据）；
  3. 波 10 新建件消费面反查（本袋接线件自证）。

生产路径口径（真源=AGENTS.md §7 核心系统速查 + 条件包 [CONSUMERS] 实测）：
  zephyr.trading（AutoRuntime Core）/ zephyr.data（数据集成器）/ zephyr.frontend（仪表盘）/
  zephyr.orchestrator / zephyr.runtime + 具名跑批入口
  scripts.backtest.factory_grid_executor、scripts.backtest.f06_e4_wfa_exam、scripts.compute_signals。
"""

from __future__ import annotations

import ast
import re
import subprocess
from collections import deque
from pathlib import Path

import yaml

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # TRAE-067 无窗口统一入口
from zephyr.shared.io.paths import REPO_ROOT  # SSoT canonical（SSOT-REDEFINITION 门：禁本地重定义）

SRC = REPO_ROOT / "src"
SCRIPTS = REPO_ROOT / "scripts"
TESTS = REPO_ROOT / "tests"
OUT_DIR = REPO_ROOT / "docs" / "_working" / "total_command_closeout" / "wave10"
OUT_YAML = OUT_DIR / "wave10_asset_base_audit.yaml"
PATTERN_REGISTRY = REPO_ROOT / str(
    Path("docs" / "01_policies_and_standards" / "_registry" / "catalogs") / "chart_pattern_registry.yaml"
)
SCANNER = SRC / "zephyr/signal_ashare/strategy_signal/candlestick_scanner.py"

PROD_ROOTS: tuple[str, ...] = (
    "zephyr.trading",
    "zephyr.data",
    "zephyr.frontend",
    "zephyr.orchestrator",
    "zephyr.runtime",
)
PROD_ROOT_MODULES_EXPLICIT: tuple[str, ...] = (
    "scripts.backtest.factory_grid_executor",
    "scripts.backtest.f06_e4_wfa_exam",
    "scripts.compute_signals",
)
FROZEN_FILES: tuple[str, ...] = (
    "config/search_space_prereg.yaml",
    "config/exam_scale_cost_gate.yaml",
    "config/flags.yaml",
)


def _git(*args: str) -> str:
    proc = run_subprocess_hidden(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败: {proc.stderr[:400]}")
    return proc.stdout


def _py_files(base: Path) -> list[Path]:
    return sorted(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)


def _dotted(path: Path) -> str | None:
    try:
        rel = path.relative_to(SRC)
        parts = list(rel.with_suffix("").parts)
    except ValueError:
        try:
            rel = path.relative_to(SCRIPTS)
            parts = ["scripts", *rel.with_suffix("").parts]
        except ValueError:
            return None
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else None


def _is_type_checking_guard(test: ast.expr) -> bool:
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def _absolute_targets(node: ast.Import | ast.ImportFrom) -> set[str]:
    if isinstance(node, ast.Import):
        return {a.name for a in node.names}
    if node.level:
        return set()
    base = node.module or ""
    out = {base} if base else set()
    out.update(f"{base}.{a.name}" for a in node.names if a.name != "*" and base)
    return out


def _relative_targets(node: ast.ImportFrom, mod_name: str, path: Path) -> set[str]:
    pkg_parts = mod_name.split(".")
    if path.name != "__init__.py":
        pkg_parts = pkg_parts[:-1]
    up = node.level - 1
    if up:
        pkg_parts = pkg_parts[: len(pkg_parts) - up] if len(pkg_parts) >= up else []
    prefix = ".".join(pkg_parts)
    if node.module and prefix:
        base = f"{prefix}.{node.module}"
    else:
        base = node.module or prefix
    out = {base} if base else set()
    out.update(f"{base}.{a.name}" for a in node.names if a.name != "*" and base)
    return out


def _imports_of(path: Path, mod_name: str) -> tuple[set[str], set[str]]:
    """(运行时目标前缀集, 仅 TYPE_CHECKING 目标前缀集)。"""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    tc_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking_guard(node.test):
            tc_ids.update(id(s) for s in ast.walk(node) if isinstance(s, (ast.Import, ast.ImportFrom)))
    runtime: set[str] = set()
    tc_only: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.ImportFrom) and node.level:
            targets = _relative_targets(node, mod_name, path)
        else:
            targets = _absolute_targets(node)
        bucket = tc_only if id(node) in tc_ids else runtime
        bucket.update(targets)
    return runtime, tc_only - runtime


def _resolve(target: str, names: set[str]) -> str | None:
    parts = target.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in names:
            return cand
    return None


def _build_graph() -> tuple[dict[str, Path], dict[str, dict[str, str]], dict[str, set[str]]]:
    parsed: list[tuple[str, Path]] = []
    files: dict[str, Path] = {}
    for base in (SRC, SCRIPTS, TESTS):
        for path in _py_files(base):
            name = _dotted(path)
            if name is None or name in files:
                continue
            files[name] = path
            parsed.append((name, path))
    names = set(files)
    edges: dict[str, set[str]] = {m: set() for m in names}
    incoming: dict[str, dict[str, str]] = {}
    for name, path in parsed:
        runtime, _tc = _imports_of(path, name)
        out: set[str] = set()
        for target in runtime:
            hit = _resolve(target, names)
            if hit and hit != name:
                out.add(hit)
        edges[name] = out
        for m in out:
            incoming.setdefault(m, {})[name] = "runtime"
    return files, incoming, edges


def _prod_closure(edges: dict[str, set[str]], files: dict[str, Path]) -> set[str]:
    roots = {m for m in files if m.startswith(PROD_ROOTS)}
    roots |= {m for m in files if m in PROD_ROOT_MODULES_EXPLICIT}
    seen = set(roots)
    dq = deque(roots)
    while dq:
        for nxt in edges.get(dq.popleft(), ()):
            if nxt not in seen:
                seen.add(nxt)
                dq.append(nxt)
    return seen


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _classify(module: str, incoming: dict[str, dict[str, str]], closure: set[str], files: dict[str, Path]) -> dict:
    consumers = [c for c in incoming.get(module, {}) if c != module]
    prod: list[str] = []
    script: list[str] = []
    src_other: list[str] = []
    test: list[str] = []
    for c in consumers:
        rp = _rel(files[c])
        if rp.startswith("tests/"):
            test.append(c)
        elif c in closure:
            prod.append(c)
        elif rp.startswith("scripts/"):
            script.append(c)
        else:
            src_other.append(c)
    if prod:
        verdict = "CONNECTED_PROD"
    elif script:
        verdict = "NOT_CONSUMED_script_only"
    elif src_other:
        verdict = "NOT_CONSUMED_off_prod_path"
    elif test:
        verdict = "NOT_CONSUMED_test_only"
    else:
        verdict = "NOT_CONSUMED_orphan"
    return {
        "module": module,
        "path": _rel(files[module]),
        "verdict": verdict,
        "runtime_consumer_count": len(prod) + len(script) + len(src_other),
        "prod_consumers": sorted(prod)[:8],
        "src_consumers_off_prod_path": sorted(src_other)[:8],
        "script_consumers": sorted(script)[:8],
        "test_consumers": sorted(test)[:4],
    }


def _candle_catalog() -> dict:
    if not PATTERN_REGISTRY.exists():
        raise RuntimeError(f"形态册缺失: {PATTERN_REGISTRY}")
    raw = PATTERN_REGISTRY.read_text(encoding="utf-8", errors="replace")
    ids = sorted(set(re.findall(r"PAT-CANDLE-\d{3}", raw)))
    reg_rows = len(re.findall(r'-\s+pattern_id:\s*"PAT-CANDLE-\d{3}"', raw))
    scanner_text = SCANNER.read_text(encoding="utf-8", errors="replace")
    static_ids = set(re.findall(r"PAT-CANDLE-\d{3}", scanner_text))
    extra_rules = len(re.findall(r'"PAT-CANDLE-\d{3}"', scanner_text))
    talib_cdl: int | str
    try:
        import talib  # noqa: PLC0415

        talib_cdl = len([f for f in dir(talib) if f.startswith("CDL") and callable(getattr(talib, f))])
    except Exception as exc:  # noqa: BLE001 — talib 轮子不可得=如实标注（不可选依赖探测，异常类型入账禁假计数）
        talib_cdl = f"unavailable:{type(exc).__name__}"
    manifest = SCRIPTS / "script-manifest.yaml"
    manifest_lines: list[str] = []
    if manifest.exists():
        for line in manifest.read_text(encoding="utf-8", errors="replace").splitlines():
            if "candlestick_scanner" in line or "PAT-CANDLE" in line:
                manifest_lines.append(line.strip()[:220])
    return {
        "registry_rows_by_pattern_id": reg_rows,
        "registry_distinct_ids": len(ids),
        "scanner_static_id_literals": len(static_ids),
        "registry_ids_with_static_literal": len([i for i in ids if i in static_ids]),
        "static_literal_occurrences": extra_rules,
        "talib_cdl_functions": talib_cdl,
        "hook_missing_note": "TA-Lib CDL 类 id 由运行时 dir(talib) 枚举生成，源码无常驻字面量属预期非缺陷",
        "script_manifest_candle_lines": manifest_lines[:6],
    }


def _frozen_diff() -> dict[str, str]:
    out: dict[str, str] = {}
    for f in FROZEN_FILES:
        d = _git("diff", "HEAD", "--name-only", "--", f).strip()
        out[f] = "clean_diff_zero" if d == "" else f"DIRTY:{d}"
    return out


def main() -> int:
    files, incoming, edges = _build_graph()
    closure = _prod_closure(edges, files)
    head = {l.strip() for l in _git("ls-tree", "-r", "HEAD", "--name-only").splitlines() if l.strip()}

    clusters = {
        "signal_ashare_graph_core_excl_strategy_signal": sorted(
            m
            for m in files
            if m.startswith("zephyr.signal_ashare") and not m.startswith("zephyr.signal_ashare.strategy_signal")
        ),
        "strategy_signal_pattern_chain": sorted(
            m for m in files if m.startswith("zephyr.signal_ashare.strategy_signal")
        ),
        "wave10_new_parts": sorted(
            m for m in files if m.startswith("scripts.signals.") or m.startswith("scripts.governance.wave10.")
        ),
    }

    report: dict = {
        "generated_by": "scripts/governance/wave10/wave10_asset_base_audit.py",
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD").strip(),
        "prod_roots": list(PROD_ROOTS),
        "prod_root_scripts": list(PROD_ROOT_MODULES_EXPLICIT),
        "prod_closure_module_count": len(closure),
        "scanned_module_count": len(files),
        "judgment_rule": "装饰性接线（仅 TYPE_CHECKING / 仅脚本 / 仅非生产 src / 仅测试）一律判未接；CONNECTED_PROD 才算接",
        "clusters": {},
        "candle_catalog": _candle_catalog(),
        "frozen_files_diff": _frozen_diff(),
    }
    for cname, mods in clusters.items():
        rows = [_classify(m, incoming, closure, files) for m in mods]
        for r in rows:
            r["in_head"] = r["path"] in head
        report["clusters"][cname] = {
            "file_count": len(rows),
            "in_head_count": sum(1 for r in rows if r["in_head"]),
            "connected_prod_count": sum(1 for r in rows if r["verdict"] == "CONNECTED_PROD"),
            "verdict_tally": {
                v: sum(1 for r in rows if r["verdict"] == v) for v in sorted({r["verdict"] for r in rows})
            },
            "modules": rows,
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_YAML.write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True, width=200),
        encoding="utf-8",
        newline="\n",
    )
    for cname, blk in report["clusters"].items():
        print(
            f"{cname}: files={blk['file_count']} in_head={blk['in_head_count']} "
            f"connected_prod={blk['connected_prod_count']} tally={blk['verdict_tally']}"
        )
    print(
        "candle_catalog:",
        report["candle_catalog"]["registry_distinct_ids"],
        "ids /",
        report["candle_catalog"]["talib_cdl_functions"],
        "talib CDL",
    )
    print("frozen_diff:", report["frozen_files_diff"])
    print("written:", _rel(OUT_YAML))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
