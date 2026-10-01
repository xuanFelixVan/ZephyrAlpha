# [MODULE] tests.governance.test_connection_matrix_rulers
# [DOMAIN] D_GOV
# [DEPENDENCIES] pytest; scripts.governance.d5_architecture.generators.generate_connection_matrix; zephyr.trading.decision_map; yaml
# [CONSUMERS] CI / 波 13 包 13.4 红证
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部写 tmp_path（禁写生产 data/ 与 docs/）; 断言只增不减（禁为变绿弱化判据）
# [ERROR_CONTRACT] 断言失败即红——不得 skip/xfail 掩盖
# [TTL] permanent
"""波 13 包 13.4 全连接矩阵的红蓝判据（能红判据模板 R-5）。

四条必备红证 + 两条通道防线：
  1. 抹掉一个 module_ref ⇒ 矩阵必须点名该节点（且不得记成 WIRED）
  2. 塞一条假 data_refs 指向不存在的表 ⇒ 必走 R11 通道落 MISSING_WIRING
  3. 没有声明策略链接的因子 ⇒ 必须 NO_DECLARED_EDGE，且**不得**计入差集
  4. --check 对被人改过的 CSV 必须返回非零
  5. ClickHouse 不可达时不得折算成"表不存在/0 行"（毒通道防线）
  6. 同一状态的非法组合（无声明侧却判差集）必须在构造期硬炸
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.governance.d5_architecture.generators import generate_connection_matrix as gcm  # noqa: E402
from zephyr.trading.decision_map import load_decision_map  # noqa: E402

_REAL_MAP = _REPO_ROOT / "config" / "trading_decision_map.yaml"
_REAL_REG = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_REAL_TASKS = _REPO_ROOT / "src" / "zephyr" / "data" / "config" / "tasks.yaml"


def _make_repo(tmp_path: Path, *, mutate=None, materialize_module_refs: bool = True) -> Path:
    """造一个只含必要输入面的沙盘仓（真注册表 + 可派生改写的 TDM + 最小代码面）。

    materialize_module_refs：把 TDM 在册 module_ref 指到的文件在沙盘里补成空壳——
    否则 E6 全是 MISSING_WIRING（盘上没代码），"抹掉才红"的对照组就立不起来。
    空壳不含任何符号，不会把别的边误判成已连。
    """
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True, exist_ok=True)
    reg_dir = root / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    reg_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("data_asset_registry.yaml", "factor_registry.yaml", "strategy_registry.yaml"):
        (reg_dir / fname).write_text((_REAL_REG / fname).read_text(encoding="utf-8"), encoding="utf-8")
    tasks_dir = root / "src" / "zephyr" / "data" / "config"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (tasks_dir / "tasks.yaml").write_text(_REAL_TASKS.read_text(encoding="utf-8"), encoding="utf-8")

    raw = yaml.safe_load(_REAL_MAP.read_text(encoding="utf-8"))
    if mutate is not None:
        mutate(raw)
    if materialize_module_refs:
        for n in raw["nodes"]:
            ref = n.get("module_ref")
            if isinstance(ref, str) and ref.startswith("src/") and ref.endswith(".py"):
                p = root / ref
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("# sandbox stub (no symbols)\n", encoding="utf-8")
    (root / "config" / "trading_decision_map.yaml").write_text(
        yaml.safe_dump(raw, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return root


def _build(root: Path):
    return gcm.build_matrix(
        root,
        map_path=root / "config" / "trading_decision_map.yaml",
        registry_dir=root / "docs/01_policies_and_standards/_registry/catalogs",
        with_clickhouse=False,
        depgraph_r9=False,
    )


def _rows(out, edge_type: str, ids: set[str]) -> list:
    return [r for r in out.rows if r.edge_type == edge_type and (r.source_id in ids or r.target_id in ids)]


def _node_id_containing(raw_map: dict, predicate) -> str:
    for n in raw_map["nodes"]:
        if predicate(n):
            return str(n["node_id"])
    raise AssertionError("沙盘输入里找不到满足条件的节点（测试前提失效，不是判据红）")


# ===== 红证 1：抹掉 module_ref ⇒ 必点名 =====


def test_blanked_module_ref_is_named(tmp_path: Path) -> None:
    raw = yaml.safe_load(_REAL_MAP.read_text(encoding="utf-8"))
    target = _node_id_containing(
        raw, lambda n: n.get("module_ref") and (n.get("data_refs") or n.get("strategy_mounts"))
    )

    def mutate(m: dict) -> None:
        for n in m["nodes"]:
            if n["node_id"] == target:
                n["module_ref"] = None

    out = _build(_make_repo(tmp_path, mutate=mutate))
    named = _rows(out, gcm.EDGE_TYPES[5], {target})
    assert named, f"抹掉 module_ref 后矩阵没有点名 {target}"
    row = named[0]
    assert row.state == gcm.DIFFERENCE_STATE, f"{target} 该进差集却记成 {row.state}"
    assert row.rule_id == "SB-1"
    assert "module_ref" not in row.declared_by, "差集行的应连性不得来自被抹掉的那个字段本身"
    # 反向自证：不抹时同一节点必须是 WIRED（证明红是"抹"造成的，不是尺一直红）
    base = _build(_make_repo(tmp_path / "baseline"))
    same = _rows(base, gcm.EDGE_TYPES[5], {target})[0]
    assert same.state == gcm.WIRED, f"基线里 {target} 本应 WIRED，实得 {same.state}"


def test_blanked_module_ref_without_consumption_is_declared_side_debt(tmp_path: Path) -> None:
    raw = yaml.safe_load(_REAL_MAP.read_text(encoding="utf-8"))
    target = _node_id_containing(
        raw,
        lambda n: n.get("module_ref") and not (n.get("data_refs") or n.get("strategy_mounts") or n.get("factor_refs")),
    )

    def mutate(m: dict) -> None:
        for n in m["nodes"]:
            if n["node_id"] == target:
                n["module_ref"] = None

    out = _build(_make_repo(tmp_path, mutate=mutate))
    row = _rows(out, gcm.EDGE_TYPES[5], {target})[0]
    assert row.state == gcm.NO_DECLARED_EDGE, "没有任何消费声明的空 module_ref 是声明侧欠账，不是接线缺口"
    assert row.declared_by == "NONE"


# ===== 红证 2：假 data_refs ⇒ R11 通道判 MISSING_WIRING =====


def test_fake_data_ref_lands_missing_wiring_via_r11(tmp_path: Path) -> None:
    raw = yaml.safe_load(_REAL_MAP.read_text(encoding="utf-8"))
    target = _node_id_containing(raw, lambda n: n.get("data_refs"))

    def mutate(m: dict) -> None:
        for n in m["nodes"]:
            if n["node_id"] == target:
                n["data_refs"] = ["DS-NOPE-ZZZ999"]

    out = _build(_make_repo(tmp_path, mutate=mutate))
    hits = [r for r in out.rows if r.state == gcm.MISSING_WIRING and "DS-NOPE-ZZZ999" in r.target_id]
    assert hits, "假 data_refs 必须被 R11 通道判成 MISSING_WIRING（悬空指针）"
    row = hits[0]
    assert "R11" in row.read_channel, f"读数通道未披露 R11: {row.read_channel}"
    assert target in row.source_id
    assert row.declared_by.startswith("config/trading_decision_map.yaml")


def test_unreachable_clickhouse_is_never_read_as_absent_table(tmp_path: Path) -> None:
    """毒通道防线：CH 不可达 ⇒ 不得产出 MISSING_WIRING（更不得写"0 行/表不存在"）。"""

    class _StubProber:
        def __init__(self) -> None:
            self.probes = 0
            self.unreachable = 0

        def probe(self, entity: str) -> gcm.MatrixTableProbe:
            return gcm.MatrixTableProbe("unreachable", None, "CH 不可达（stub）")

    root = _make_repo(tmp_path)
    out = _build(root)
    wired_like = [r for r in out.rows if r.edge_type == "collection_leg__table" and r.state == gcm.MISSING_WIRING]
    assert not wired_like, "无 CH 参与时不得凭空调出表不存在"
    # 同一批边在"不可达"桩下仍走 grep 通道，read_channel 必须显式记降级
    inp = gcm.build_inputs(
        root,
        map_path=root / "config" / "trading_decision_map.yaml",
        registry_dir=root / "docs/01_policies_and_standards/_registry/catalogs",
        with_clickhouse=False,
    )
    inp.prober = _StubProber()  # type: ignore[assignment]
    out2 = gcm.MatrixResult()
    gcm.build_job_to_table(inp, out2)
    for r in out2.rows:
        if r.declared_by != "NONE":
            assert "ch=unreachable" not in r.read_channel or r.state != gcm.MISSING_WIRING, (
                f"CH 不可达被判成表不存在: {r.target_id}"
            )
    assert out2.count(gcm.MISSING_WIRING) == 0


def test_probe_without_dot_never_claims_zero_rows() -> None:
    pr = gcm.ClickHouseProber().probe("not_a_table_ref")
    assert pr.disposition == "absent" and pr.rows is None
    assert "无法拆" in pr.detail


# ===== 红证 3：无声明策略链接的因子 ⇒ NO_DECLARED_EDGE 且不入差集 =====


def test_factor_without_strategy_declaration_is_not_a_wiring_gap(tmp_path: Path) -> None:
    out = _build(_make_repo(tmp_path))
    factors = yaml.safe_load((_REAL_REG / "factor_registry.yaml").read_text(encoding="utf-8"))["factors"]
    edge_rows = [r for r in out.rows if r.edge_type == "factor__strategy"]
    # 声明侧覆盖集：① 因子自己声明了 owner（belongs_to_strategies）
    #              ② 该因子出现在任何有 declared_by 的边行源侧（TDM 同节点代理）
    declared = {str(f["factor_id"]) for f in factors if (f.get("belongs_to_strategies") or [])}
    proxy_factors = {r.source_id for r in edge_rows if r.declared_by != "NONE"}
    candidates = [
        str(f["factor_id"])
        for f in factors
        if f.get("factor_id") and str(f["factor_id"]) not in declared and str(f["factor_id"]) not in proxy_factors
    ]
    assert candidates, "沙盘里所有因子都有声明链接，红证 3 前提失效"
    fid = candidates[0]
    rows = [r for r in edge_rows if fid in (r.source_id, r.target_id)]
    assert rows, f"矩阵没有为 {fid} 出行（漏类比错类更糟）"
    for r in rows:
        assert r.state == gcm.NO_DECLARED_EDGE, f"{fid} 被判成 {r.state}——无声明侧不得进差集"


def test_no_declared_edge_never_enters_difference_set(tmp_path: Path) -> None:
    out = _build(_make_repo(tmp_path))
    assert out.denominators["_all"][gcm.DIFFERENCE_STATE] > 0, "真跑必须数出差集（为 0=尺没接上）"
    assert out.denominators["_all"][gcm.NO_DECLARED_EDGE] > 0, "真跑必须数出声明缺失"
    for r in out.difference_set:
        assert r.declared_by != "NONE"


# ===== 红证 4：--check 对被改过的 CSV 必红 =====


def test_check_returns_nonzero_on_mutated_csv(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    out = _build(root)
    csv_path = tmp_path / "connection_matrix.csv"
    gcm.write_artifacts(out, csv_path, None)
    rc_clean, report = gcm.check(
        csv_path,
        repo_root=root,
        map_path=root / "config" / "trading_decision_map.yaml",
        registry_dir=root / "docs/01_policies_and_standards/_registry/catalogs",
        with_clickhouse=False,
        with_depgraph_r9=False,
    )
    assert rc_clean in (gcm.RC_CLEAN, gcm.RC_DIFFERENCE)
    assert report["artifact_stale"] is False, f"未改动即判陈旧（口径不稳）: {report}"

    text = csv_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines[2] = lines[2].replace(gcm.WIRED, gcm.DIFFERENCE_STATE) if gcm.WIRED in lines[2] else lines[2] + "|TAMPERED"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rc, report2 = gcm.check(
        csv_path,
        repo_root=root,
        map_path=root / "config" / "trading_decision_map.yaml",
        registry_dir=root / "docs/01_policies_and_standards/_registry/catalogs",
        with_clickhouse=False,
        with_depgraph_r9=False,
    )
    assert rc == gcm.RC_DIFFERENCE, f"改过的 CSV 仍判 {rc}（--check 失效）"
    assert report2["artifact_stale"] is True


def test_check_returns_tool_failure_when_artifact_missing(tmp_path: Path) -> None:
    rc, report = gcm.check(tmp_path / "nope.csv")
    assert rc == gcm.RC_TOOL_FAILURE
    assert "不存在" in report["error"]


# ===== 判据构造期防线：非法状态组合必须硬炸 =====


def test_illegal_state_combination_raises() -> None:
    with pytest.raises(ValueError):
        gcm._row(
            "table__factor",
            "A",
            "B",
            declared_by="NONE",
            wired_by="x",
            state=gcm.DIFFERENCE_STATE,
            read_channel="t",
            rule_id="R",
            evidence_cmd="t",
        )
    with pytest.raises(ValueError):
        gcm._row(
            "table__factor",
            "A",
            "B",
            declared_by="x",
            wired_by="y",
            state="MAYBE_WIRED",
            read_channel="t",
            rule_id="R",
            evidence_cmd="t",
        )


def test_matrix_only_reads_declared_inputs(tmp_path: Path) -> None:
    """矩阵只吃 TDM + 三本注册表 + tasks.yaml，不碰生产 data/（测试隔离红线）。"""
    root = _make_repo(tmp_path)
    out = _build(root)
    assert (root / "data").exists() is False, "生成器在沙盘里凭空造出了 data/ 写入面"
    assert out.rows and out.denominators["_all"]["total"] == len(out.rows)
    dm = load_decision_map(root / "config" / "trading_decision_map.yaml")
    assert len(dm.nodes) == len(load_decision_map(_REAL_MAP).nodes)


def test_ruler_imports_come_from_this_checkout() -> None:
    """尺与被测件必须同源：误用另一份 checkout 的 zephyr 会让红证测的是别人的代码。

    本道实测踩过：PYTHONPATH 用 Unix 冒号分隔在 Windows 下失效，`import zephyr`
    静默落到主仓 checkout——所以这条断言本身也是一颗红证。
    """
    import zephyr

    here = _REPO_ROOT.resolve()
    assert Path(zephyr.__file__).resolve().is_relative_to(here), (
        f"zephyr 取自 {zephyr.__file__}，不在本 checkout {here} 内"
    )
    assert Path(gcm.__file__).resolve().is_relative_to(here)
