# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] tests.gov.governance.test_apply_depgraph_dry_run
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.apply_depgraph
# [CONSUMERS] depgraph dry-run 语义回归防线（st-maint2 2026-10-11）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] dry-run == 零 PG 写 + 零工作树写 + 零后台再生（审计留痕除外）
# [MODIFY-GUARD] scripts/governance/apply_depgraph.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败 = dry-run 语义违约（带 --dry-run 仍真写 PG / 触发后台再生）
# [TESTS] 本文件即测试
# [A_test] module_id=MOD-TEST-DRYRUN | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_apply_depgraph_dry_run.py — apply_depgraph.py --dry-run 语义违约红证 + 回归

病根（st-maint2 治本 2026-10-11）：12+ 个写子命令带 --dry-run 仍真写 PostgreSQL——处理器不收
dry_run 形参、调度点不传，函数体内 conn.commit() 无条件执行；且 __main__ finally 用 argv 逐字
匹配 "--dry-run"，argparse 缩写 --dry 可绕过后台重生成抑制。

判据口径：dry-run == 零 PG 写 + 零工作树写 + 零后台再生；审计留痕可写但记录带 dry_run 字段。

覆盖：
1. 每个漏腿函数 dry_run=True → commit==0 且 rollback 被调用、返回成功值；dry_run=False → commit 被调
   （正向腿不能被改坏，防"把写腿整段禁掉"的放松式修法）。
2. 机判 15 个写子命令目标函数签名全部含 dry_run 形参（inspect.signature）。
3. 反向钉桩：--add-design-node 的 sync_module_panorama 在 dry-run 下不被调用。
4. 反向钉桩：argv 用 --dry 缩写时 finally 后台再生判据必须为假（reconcile_async 不被调用）。
5. 审计 jsonl 记录含 dry_run 字段。
6. 跨侧对账：真跑路径 commit 前写的语句 == dry-run plan 摘要（防"预览一半、真跑多做一件事"）。
7. 红证（原始字节）：加载未修 pristine 副本，断言它确实"dry_run 下仍 commit"。

测试隔离：全程 monkeypatch PG 连接工厂为假连接，审计目录重定向到 tmp_path，不碰生产 DB/工作树。
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import subprocess
import sys
import types
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_GOV_DIR = _PROJECT_ROOT / "scripts" / "governance"
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src"), str(_GOV_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_FIXED_PATH = _GOV_DIR / "apply_depgraph.py"
# 红证基线字节＝施工基线 commit 的内容寻址 blob（不落 .orig 副本：docs/_working 目录
# 契约只允 .md/.csv/.yaml/.html/.json，且根宪法 §4 全资产净零禁上 MB 级重复件）。
# sha256 实测与当初落盘的 .orig 副本同值＝等价性已证。
_BASELINE_SHA = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"
_PRISTINE_REL = "scripts/governance/apply_depgraph.py"
_PRISTINE_SHA256 = "d80386669336d20bd3faf1d3bca55df1945829664d9eb0046d138c4ea690173f"


def _pristine_apply_depgraph(dst_dir: Path) -> Path:
    """现取基线原始字节并落成可导入的 .py（二进制读，防行尾折叠改字节）。"""
    proc = subprocess.run(
        ["git", "-C", _PROJECT_ROOT.as_posix(), "show", f"{_BASELINE_SHA}:{_PRISTINE_REL}"],
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, f"基线 blob 取回失败: {proc.stderr[:200]}"
    raw = proc.stdout
    if hashlib.sha256(raw).hexdigest() != _PRISTINE_SHA256:
        raise AssertionError(f"pristine 字节与钉死基线不符（红证失真）：sha={hashlib.sha256(raw).hexdigest()[:16]}")
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "apply_depgraph_pristine.py"
    dst.write_bytes(raw)
    return dst


def _load(name: str, path: Path):
    # 显式 SourceFileLoader：pristine 副本以 .orig 后缀存原始字节，spec_from_file_location
    # 无法为未知后缀推断 loader；SourceFileLoader 按源码编译，绕过后缀限制。
    loader = SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── 假连接：记录 execute/commit/rollback 调用序列 ──
EVENTS: list[tuple] = []


class _AutoRow(dict):
    """万能行：对任意列名返回可推进到 commit 点的合法值（含 .get/keys）；恒真。"""

    D = {
        "count": 0,
        "node_id": 999,
        "edge_id": 888,
        "mapping_id": 1,
        "design_maturity": "design",
        "build_status": "planned",
        "dep_type": "import_depends",
        "dep_maturity": "design",
        "path": "",
        "file_path": "",
        "blueprint_id": "",
        "name": "n",
        "constraint_type": "c",
        "constraint_id": "c1",
        "domain_id": "D",
        "from_node_id": 2,
        "to_node_id": 3,
        "entry_point": 0,
        "granularity": "file",
        "node_type": "module",
    }

    def __bool__(self):
        return True

    def __getitem__(self, k):
        if dict.__contains__(self, k):
            return dict.__getitem__(self, k)
        return self.D.get(k, "design")

    def get(self, k, default=None):
        if dict.__contains__(self, k) or k in self.D:
            return self[k]
        return default

    def keys(self):
        return self.D.keys()


# fetchone 返回 None（让函数走"新建/插入"腿而非提前 return 的已存在腿）
_NONE_SUBSTR = (
    "AND design_maturity='design'",
    "AND design_maturity='production'",
    "AND dep_type=%s",
)
_EMPTY_ALL = ("SELECT to_node_id FROM edges", "node_id = ANY(")
_LIST_ALL = {"SELECT node_id, path FROM nodes WHERE blueprint_id": [(123, "p")]}


class _Cursor:
    def __init__(self, sql):
        EVENTS.append(("execute", sql))
        self._sql = sql

    def fetchone(self):
        if any(s in self._sql for s in _NONE_SUBSTR):
            return None
        return _AutoRow()

    def fetchall(self):
        for key, val in _LIST_ALL.items():
            if key in self._sql:
                return val
        if any(s in self._sql for s in _EMPTY_ALL):
            return []
        return []


class _Conn:
    def execute(self, sql, params=None):
        return _Cursor(sql)

    def commit(self):
        EVENTS.append(("commit",))

    def rollback(self):
        EVENTS.append(("rollback",))

    def close(self):
        EVENTS.append(("close",))


def _fake_factory(autocommit=False, allow_edge_delete=False, *a, **k):
    return _Conn()


def _reset():
    EVENTS.clear()


def _commits():
    return sum(1 for e in EVENTS if e[0] == "commit")


def _rollbacks():
    return sum(1 for e in EVENTS if e[0] == "rollback")


def _last_execute_before_commit():
    for i, e in enumerate(EVENTS):
        if e[0] == "commit":
            for j in range(i - 1, -1, -1):
                if EVENTS[j][0] == "execute":
                    return EVENTS[j][1]
    return None


# 漏腿函数调用适配 + 期望"成功"返回
_INT_RESULT = {"add_design_node", "add_file_node", "add_design_edge", "add_edge"}


def _call_fn(adg, name, dry):
    kw = {"dry_run": dry}
    if name == "add_design_node":
        return adg.add_design_node("docs/x/", "", "DDOM", **kw)
    if name == "add_file_node":
        return adg.add_file_node(str(_REL_EXISTING), "", "DDOM", force=True, **kw)
    if name == "add_design_edge":
        return adg.add_design_edge(2, 3, **kw)
    if name == "add_edge":
        return adg.add_edge(2, 3, dep_type="import_depends", dep_maturity="active", **kw)
    if name == "transition_build_status":
        return adg.transition_build_status(5, "generated", **kw)
    if name == "transition_design_maturity":
        return adg.transition_design_maturity(5, "production", **kw)
    if name == "remove_design_node":
        return adg.remove_design_node(5, design_evidence="11-D-RISK §1", **kw)
    if name == "deprecate_node":
        return adg.deprecate_node(5, force=True, **kw)
    if name == "mark_blueprint_invalid":
        return adg.mark_blueprint_invalid("BP", "reason", **kw)
    if name == "delete_design_edge":
        return adg.delete_design_edge(7, **kw)
    if name == "delete_edge":
        return adg.delete_edge(7, **kw)
    if name == "delete_blueprint_link":
        return adg.delete_blueprint_link("BP", **kw)
    if name == "delete_constraint":
        return adg.delete_constraint("C", **kw)
    if name == "update_edge_type":
        return adg.update_edge_type(7, "import_depends", **kw)
    if name == "update_module_metadata":
        return adg.update_module_metadata("scripts/x.py", {"module_name_cn": "x"}, **kw)
    raise KeyError(name)


# 相对仓库根真实存在的文件（add_file_node 需要磁盘文件存在）
_REL_EXISTING = "scripts/governance/apply_depgraph.py"

ALL_LEAKY = [
    "add_design_node",
    "add_file_node",
    "add_design_edge",
    "add_edge",
    "transition_build_status",
    "transition_design_maturity",
    "remove_design_node",
    "deprecate_node",
    "mark_blueprint_invalid",
    "delete_design_edge",
    "delete_edge",
    "delete_blueprint_link",
    "delete_constraint",
    "update_edge_type",
    "update_module_metadata",
]


@pytest.fixture()
def adg(tmp_path, monkeypatch):
    """加载修后模块并把外部效应（PG 连接、审计目录、词表加载、计划累加器）隔离到假件。"""
    mod = _load("adg_fixed", _FIXED_PATH)
    _reset()
    monkeypatch.setattr(mod, "get_depgraph_pg_connection", _fake_factory)
    monkeypatch.setattr(mod, "_DESIGN_NODE_DELETE_AUDIT_DIR", tmp_path)
    monkeypatch.setattr(mod, "_DRY_RUN_PLAN", [])
    monkeypatch.setattr(mod, "load_vocabulary_values", lambda *a, **k: {"directory", "file", "module", "aggregated"})
    mod._AUDIT_TMP = tmp_path
    return mod


# ── 1. 每个漏腿函数：dry 零 commit + rollback；真跑 commit 有被调 ──
@pytest.mark.parametrize("name", ALL_LEAKY)
def test_dry_run_no_commit_real_does(adg, name):
    expected = (
        999
        if name in ("add_design_node", "add_file_node")
        else (888 if name in ("add_design_edge", "add_edge") else True)
    )

    # dry-run 腿
    _reset()
    del adg._DRY_RUN_PLAN[:]
    ret = _call_fn(adg, name, True)
    assert _commits() == 0, f"{name}: dry-run 仍 commit（违约）"
    assert _rollbacks() >= 1, f"{name}: dry-run 未显式 rollback"
    assert ret == expected, f"{name}: dry-run 返回值应为成功值（证明推进到 commit 点而非报错绕过）"
    assert len(adg._DRY_RUN_PLAN) == 1, f"{name}: dry-run 应记录 1 条 plan"

    # 真跑腿（正向不能被放松成"整段禁掉"）
    _reset()
    ret2 = _call_fn(adg, name, False)
    assert _commits() >= 1, f"{name}: 真跑 dry_run=False 必须 commit（正向腿被改坏）"
    assert _rollbacks() == 0, f"{name}: 真跑不应触发 gate rollback"
    assert ret2 == expected, f"{name}: 真跑返回值应一致"


# ── 2. 机判：写子命令目标函数签名全部含 dry_run 形参 ──
@pytest.mark.parametrize("name", ALL_LEAKY)
def test_signature_has_dry_run_param(adg, name):
    fn = getattr(adg, name)
    assert "dry_run" in inspect.signature(fn).parameters, f"{name} 缺 dry_run 形参"


# ── 3. 反向钉桩：dry-run 下 sync_module_panorama 不被调用 ──
def _run_add_design_node_dispatch(adg, argv, sync_calls, monkeypatch):
    fake_sync_mod = types.ModuleType("sync_panorama_module")

    def _sync(bp):
        sync_calls.append(bp)

    fake_sync_mod.sync_module_panorama = _sync
    monkeypatch.setitem(sys.modules, "sync_panorama_module", fake_sync_mod)

    def _stub(path, bp, dom, bs, granularity="directory", dry_run=False):
        _run_add_design_node_dispatch.last_dry = dry_run
        return 5

    monkeypatch.setattr(adg, "add_design_node", _stub)
    monkeypatch.setattr(sys, "argv", ["apply_depgraph.py", *argv])
    adg.main()


def test_sync_panorama_skipped_in_dry_run(adg, monkeypatch):
    calls = []
    _run_add_design_node_dispatch(
        adg, ["--add-design-node", "docs/x/", "BPID", "DDOM", "--dry-run"], calls, monkeypatch
    )
    assert calls == [], "dry-run 下 sync_module_panorama 不得被调用（会写 PG + 落盘 blueprint.md）"

    calls2 = []
    _run_add_design_node_dispatch(adg, ["--add-design-node", "docs/x/", "BPID", "DDOM"], calls2, monkeypatch)
    assert calls2 == ["BPID"], "非 dry-run 下 sync_module_panorama 应被调用（正向腿不被改坏）"


# ── 4. 反向钉桩：--dry 缩写时后台再生判据必须为假 ──
def _install_side_effect_stubs(monkeypatch, registry):
    for name in ("scripts.governance.meta.backup_runtime_state", "meta.backup_runtime_state"):
        m = types.ModuleType(name)
        m.backup_pg_architecture = lambda *a, **k: registry.setdefault("backup", []).append(a)
        monkeypatch.setitem(sys.modules, name, m)
    for name in ("scripts.governance.reconcile_generators", "reconcile_generators"):
        m = types.ModuleType(name)

        def _recon(topic):
            registry.setdefault("reconcile", []).append(topic)
            return {"status": "no-op"}

        m.reconcile_async = _recon
        monkeypatch.setitem(sys.modules, name, m)
    import _shared.constants as _const

    monkeypatch.setattr(_const, "mark_depgraph_dirty", lambda *a, **k: registry.setdefault("dirty", []).append(1))


def test_dry_abbreviation_suppresses_regenerate(adg, monkeypatch):
    # 判据函数层：parsed=True（--dry 被 argparse 解析为 True）→ 非写运行
    assert adg._is_write_run(["x", "--add-design-node", "--dry"], True) is False
    # 反证：若沿用旧 argv 字面匹配，parsed 缺失时 --dry 会被判为"真写"（这正是被根除的绕过）
    assert adg._is_write_run(["x", "--add-design-node", "--dry"], None) is True

    reg = {}
    _install_side_effect_stubs(monkeypatch, reg)
    monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
    ret = adg._post_write_finalize(["x", "--add-design-node", "--dry"], True)
    assert ret is False
    assert reg.get("reconcile", []) == [], "--dry 缩写绝不能触发后台再生"

    # 正向腿：真跑（parsed=False）须触发后台再生
    reg2 = {}
    _install_side_effect_stubs(monkeypatch, reg2)
    ret2 = adg._post_write_finalize(["x", "--add-design-node"], False)
    assert ret2 is True
    assert reg2.get("reconcile", []) == ["depgraph_db"], "真跑必须触发后台再生（正向腿不被放松）"


# ── 5. 审计 jsonl 记录含 dry_run 字段 ──
def test_audit_jsonl_has_dry_run_field(adg):
    _reset()
    del adg._DRY_RUN_PLAN[:]
    adg.remove_design_node(5, design_evidence="11-D-RISK §1", dry_run=True)
    audit_file = adg._AUDIT_TMP / "design_node_delete.jsonl"
    assert audit_file.exists(), "dry-run 下审计留痕仍应写（可反查预览动作）"
    rec = json.loads(audit_file.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert "dry_run" in rec, "审计记录必须含 dry_run 字段"
    assert rec["dry_run"] is True


# ── 6. 跨侧对账：真跑 commit 前语句 == dry-run plan 摘要 ──
@pytest.mark.parametrize(
    "name,sql_attr",
    [
        ("transition_build_status", "SQL_UPDATE_BUILD_STATUS"),
        ("delete_edge", "SQL_DELETE_EDGE_BY_ID"),
        ("remove_design_node", "SQL_DEPRECATE_NODE"),
    ],
)
def test_real_sql_matches_dry_plan(adg, name, sql_attr):
    const = getattr(adg, sql_attr)
    _reset()
    del adg._DRY_RUN_PLAN[:]
    _call_fn(adg, name, True)
    assert adg._DRY_RUN_PLAN and adg._DRY_RUN_PLAN[0]["sql"] == const

    _reset()
    _call_fn(adg, name, False)
    assert _last_execute_before_commit() == const, "真跑 commit 前写的语句与 dry-run 预览不一致"


# ── 7. 红证：未修 pristine 副本确实"dry_run 下仍 commit"（缺陷源自原始字节）──
def test_pristine_still_commits_under_dry_run(tmp_path: Path):
    pri = _load("adg_pristine", _pristine_apply_depgraph(tmp_path))
    # 结构证据：原函数根本没有 dry_run 形参 → 无法遵守 dry-run
    assert "dry_run" not in inspect.signature(pri.add_design_node).parameters, "pristine 应无 dry_run 形参"
    # 行为证据：按旧 --dry-run 调度形态调用（旧调度不传 dry_run），连接工厂记录到 commit = 真写 PG
    _reset()
    pri.get_depgraph_pg_connection = _fake_factory
    pri.load_vocabulary_values = lambda *a, **k: {"directory", "file", "module", "aggregated"}
    pri._DESIGN_NODE_DELETE_AUDIT_DIR = Path(__file__).parent  # 不触发（add_design_node 无审计）
    pri.add_design_node("docs/x/", "", "DDOM")
    assert _commits() >= 1, "红证失败：pristine 竟未 commit——说明 pristine 副本不是原始有缺陷字节（sha 须核对）"
