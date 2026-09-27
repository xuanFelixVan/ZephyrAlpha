# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""查馆 import 面与异常面回归（R4，st-fms-tc-20260927 常驻组②③④）。

组②：惰性化不得改变异常面（PG 不可达仍原样上抛/仍按原语义降级，禁被 except 吞、
      禁退化为 ImportError 假信号）。
组③：门禁消费面（capability_lookup 探针链 + BLOOD-FLESH / TAG-VOCAB 两闸）仍调得到。
组④：`python -X importtime` 累计 import 时间判别力断言。

组④基线读数（2026-09-27 同机实测，`python -X importtime -c "import zephyr.library.lookup"`
的对全部 self 求和 / 模块条数）：
    改前（HEAD 树）= 2343.2 / 2499.6 / 2588.4 ms（max 2588.4），1372 条 import
    改后（工作树）= 128.1 / 169.6 / 196.8 ms（max 196.8），256 条 import
    阈值 = 改后实测 max 196.8ms + 10% 余量 → 220ms；另加"必须 < 改前 max/2"
    的显著性下界，防阈值被漂移到必然通过。
"""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import zephyr.governance as governance_pkg
import zephyr.governance.depgraph_schema as depgraph_schema
from zephyr.library import lookup as lookup_mod

REPO_ROOT = Path(__file__).resolve().parents[2]

#: 组④基线（见模块 docstring 实测记录）
BASELINE_IMPORT_MS = 2588.4  # 改前 max
BASELINE_IMPORT_MODULES = 1372  # 改前条数
IMPORT_BUDGET_MS = 220.0  # 改后实测 max 196.8ms × 1.10
IMPORT_BUDGET_MODULES = 700  # 改后实测 256 条，留 2.7× 余量仍 < 基线一半

#: 与"查馆"无关的写侧/门禁重件：改前被父包急切重导出连坐拉入，改后必须缺席
HEAVY_UNRELATED = (
    "zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine",
    "zephyr.gov_enforcement.behavioral_admission.admission_controller",
    "zephyr.shared.lifecycle.resource_optimization_models",
    "zephyr.infrastructure.rollback",
    "zephyr.governance.escalation.result_types",
    "zephyr.security.adversarial_validation.defense_runner",
    "zephyr.data.pit_query",
)


class _PoolDownError(RuntimeError):
    """语义等同 psycopg2 PoolError/OperationalError（取不到连接）。"""


@pytest.fixture(scope="module")
def import_profile() -> dict:
    """跑一次 `-X importtime` 子进程，返回 {self_sum_ms, modules, names}。"""
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"), PYTHONUNBUFFERED="1")
    proc = subprocess.run(  # noqa: S603 — 受控解释器自调用，非外部输入
        [sys.executable, "-X", "importtime", "-c", "import zephyr.library.lookup"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
        env=env,
        check=True,
    )
    total_us = 0
    names: set[str] = set()
    for line in proc.stderr.splitlines():
        parts = line.rstrip().split("|")
        if len(parts) != 3 or not parts[0].startswith("import time:"):
            continue
        try:  # 表头行 "import time: self [us] | cumulative | imported package" 跳过
            total_us += int(parts[0].split(":")[1].strip())
        except ValueError:
            continue
        names.add(parts[2].strip())
    return {"self_sum_ms": total_us / 1000, "modules": len(names), "names": names}


# ─────────────────────────── 组②：异常面不变宽 ───────────────────────────


def test_pool_unreachable_still_raises_same_error(monkeypatch) -> None:
    """取不到连接时仍原样上抛同一异常类型（改前后一致），不被吞、不变 ImportError。"""

    def _boom():
        raise _PoolDownError("pool exhausted")

    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", _boom, raising=True)
    monkeypatch.setenv("LIBRAM_DIRECT", "1")
    with pytest.raises(_PoolDownError) as got:
        lookup_mod.lookup_assets("kline", limit=3)
    assert type(got.value) is _PoolDownError
    assert not isinstance(got.value, ImportError)


def test_feeds_leg_still_raises_same_error(monkeypatch) -> None:
    """--feeds 腿（恒现读真源）异常口径不变。"""

    def _boom():
        raise _PoolDownError("pool exhausted")

    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", _boom, raising=True)
    with pytest.raises(_PoolDownError):
        lookup_mod._run_feeds_query("kline", 3)


def test_error_after_borrow_still_returns_connection(monkeypatch) -> None:
    """借出后报错仍须归还（finally 语义未因惰性 import 位移）。"""
    released: list[bool] = []

    class _BadConn:
        def cursor(self):
            raise _PoolDownError("cursor dead")

    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", _BadConn, raising=True)
    monkeypatch.setattr(depgraph_schema, "release_depgraph_pg_connection", lambda _c: released.append(True))
    monkeypatch.setenv("LIBRAM_DIRECT", "1")
    with pytest.raises(_PoolDownError):
        lookup_mod.lookup_assets("kline", limit=3)
    assert released == [True]


def test_depgraph_schema_unimportable_surfaces_as_importerror(monkeypatch) -> None:
    """真源不可用时：调用点抛 ImportError（原样上抛），绝不静默退成空结果。

    改前该故障发生在 `import zephyr.library.lookup` 时（ImportError）；改后发生在首次
    取连接的调用点（同 ImportError 类型）。两处都**不被吞**，即异常面未变宽；
    唯一允许的差异是时点，且 capability 探针链的 fail-open 口径改前后一致（见下）。
    """
    saved = sys.modules.get("zephyr.governance.depgraph_schema")
    monkeypatch.setenv("LIBRAM_DIRECT", "1")
    sys.modules["zephyr.governance.depgraph_schema"] = None  # type: ignore[assignment]
    try:
        with pytest.raises(ImportError):
            lookup_mod.lookup_assets("kline", limit=3)
    finally:
        if saved is None:
            del sys.modules["zephyr.governance.depgraph_schema"]
        else:
            sys.modules["zephyr.governance.depgraph_schema"] = saved


@pytest.mark.parametrize("fn_name", ["_lookup_terms_via_sql", "_run_feeds_query"])
def test_lazy_connection_import_is_not_inside_try(fn_name: str) -> None:
    """结构断言：下沉的 import 必须在使用点最前、且不在任何 try 块内（防被 except 吞）。"""
    tree = ast.parse(inspect.getsource(lookup_mod))
    target = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn_name)

    def _imports(node: ast.AST, inside_try: bool) -> list[tuple[str, bool]]:
        found: list[tuple[str, bool]] = []
        for child in ast.iter_child_nodes(node):
            nxt = inside_try or isinstance(child, ast.Try)
            if isinstance(child, ast.ImportFrom) and child.module and child.module.endswith("depgraph_schema"):
                found.append((child.module, nxt))
            found.extend(_imports(child, nxt))
        return found

    hits = _imports(target, False)
    assert hits, f"{fn_name} 应含 depgraph_schema 惰性 import"
    assert all(not in_try for _, in_try in hits), f"{fn_name}: 惰性 import 不得落在 try 内（异常面变宽）"


# ─────────────────────────── 组③：消费面仍调得到 ───────────────────────────


def test_capability_lookup_probe_chain_reaches_library() -> None:
    """capability_lookup 探针链：懒加载点可用、且其 fail-open 口径不因本件改变。"""
    from zephyr.governance import capability_lookup

    assert callable(capability_lookup._library_dedup_probe)
    probe_src = inspect.getsource(capability_lookup._library_dedup_probe)
    assert "from zephyr.library.lookup import lookup_assets" in probe_src
    assert "except Exception" in probe_src, "探针 fail-open 面必须仍是原口径（未新增吞点）"
    from zephyr.library.lookup import lookup_assets  # noqa: F401 — 消费面可达性

    assert callable(lookup_assets)


@pytest.mark.parametrize(
    ("module_name", "factory_name", "expected_gate_id"),
    [
        ("library_blood_flesh_gate", "make_library_blood_flesh_gate", "BLOOD-FLESH"),
        ("tag_vocab_gate", "make_tag_vocab_gate", "TAG-VOCAB"),
    ],
)
def test_gate_consumers_still_constructible(module_name: str, factory_name: str, expected_gate_id: str) -> None:
    """门禁消费面（library 族两闸）照旧调得到——本件未动其门禁语义。"""
    module = importlib.import_module(f"zephyr.gov_enforcement.commit_gates.library.{module_name}")
    spec = getattr(module, factory_name)()
    assert spec.gate_id == expected_gate_id
    assert callable(spec.check)


def test_governance_lazy_reexport_surface_fully_resolvable() -> None:
    """父包惰性重导出面与急切版恒等：__all__ 全可解析 + dir() 不缩。"""
    unresolvable = [name for name in governance_pkg.__all__ if not hasattr(governance_pkg, name)]
    assert unresolvable == []
    listed = set(dir(governance_pkg))
    assert set(governance_pkg.__all__) <= listed


def test_governance_symbol_identity_matches_module_path() -> None:
    """惰性解析取到的必须是同一个对象（与急切版 `from a.b import c` 逐字同物）。"""
    import importlib

    from zephyr.governance import DatabaseService  # 符号重导出
    from zephyr.governance.persistence.database_service import DatabaseService as direct

    assert DatabaseService is direct
    capability_module = importlib.import_module("zephyr.governance.capability_lookup")
    assert governance_pkg.CapabilityLookup is capability_module.CapabilityLookup
    admission_module = importlib.import_module("zephyr.gov_enforcement.behavioral_admission.admission_response")
    assert governance_pkg.admission_response is admission_module


@pytest.mark.parametrize(
    ("alias_path", "canonical_path"),
    [
        ("zephyr.governance.event_hook", "zephyr.governance.ops_governance.event_hook"),
        ("zephyr.governance.drift_fix", "zephyr.infrastructure.rollback.drift_fix"),
        ("zephyr.governance.result_types", "zephyr.governance.escalation.result_types"),
    ],
)
def test_sys_modules_alias_identity_preserved(alias_path: str, canonical_path: str) -> None:
    """ARCH-031 三件套别名（boot_hooks/测试按别名路径 import）身份与急切版恒等。"""
    import importlib

    alias = importlib.import_module(alias_path)
    canonical = importlib.import_module(canonical_path)
    assert alias is canonical
    assert sys.modules[alias_path] is sys.modules[canonical_path]


# ─────────────────────────── 组④：import 计时判别力 ───────────────────────────


def test_importtime_cumulative_significantly_dropped(import_profile: dict) -> None:
    """组④：`-X importtime` 累计 import 时间显著下降（阈值=改后实测+10% 余量）。"""
    ms = import_profile["self_sum_ms"]
    assert ms <= IMPORT_BUDGET_MS, (
        f"查馆 import 面回弹：累计 self={ms:.1f}ms > 预算 {IMPORT_BUDGET_MS}ms"
        f"（基线=改前 {BASELINE_IMPORT_MS}ms / 改后实测 max 196.8ms +10%）"
    )
    assert ms < BASELINE_IMPORT_MS / 2, f"断言须保持判别力：{ms:.1f}ms 未低于改前基线 {BASELINE_IMPORT_MS}ms 的一半"


def test_import_surface_drops_heavy_write_side_modules(import_profile: dict) -> None:
    """组④：写侧/门禁重件不再被"查馆"连坐（结构断言，与计时噪声无关）。"""
    pulled = sorted(name for name in HEAVY_UNRELATED if name in import_profile["names"])
    assert pulled == [], f"以下重件不应出现在 import zephyr.library.lookup 的 import 面里：{pulled}"
    assert import_profile["modules"] < BASELINE_IMPORT_MODULES / 2, json.dumps(
        {"modules": import_profile["modules"], "baseline": BASELINE_IMPORT_MODULES},
        ensure_ascii=False,
    )


def test_process_pool_stats_still_constructed() -> None:
    """process_pool 惰性化的 pydantic 统计模型：调用点仍返回同一类型实例。"""
    from zephyr.shared.infra.process_pool import MCPProcessPool
    from zephyr.shared.lifecycle.resource_optimization_models import ProcessPoolStats

    stats = MCPProcessPool().get_stats()
    assert isinstance(stats, ProcessPoolStats)
    assert stats.active_processes == 0
