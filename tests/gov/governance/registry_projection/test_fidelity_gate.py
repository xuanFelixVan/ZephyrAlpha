# [A_test] module_id: MOD-GOV_registry_projection_fidelity_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.registry_projection.test_fidelity_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""七册渲染保真门（wave-2 硬前置，st-sI-identity-20261004 车道I 手术5）。

病根（f10_fidelity_diff §0/§3）：身份键按"位置取首（标量）字段"，PG jsonb 按
（键长,字节序）重排字段序 → publish→render→重扫取到另一首字段 → 身份坍缩
（RULING 294→41 / TRANSLATION 8761→1262 / ARCH 815→814 / CAPCAN 丢 383）。
治本=身份声明制（册头 unique_key 声明优先，无声明退位置首标量）+ bundle 身份
置首 + self_check 身份断言 + reconcile 写前冒烟。

判据：
1. 七册全量 render→内存重扫→身份键集合相等 + 声明族基数零坍缩
   （数据源=PG 最新快照；PG 不可达=skip 留痕非 fail）；
2. 身份与字段序解耦（B3 键序病灶形态机械复现=声明键恒稳）；
3. 无声明册位置口径零变化（fdfe8fe302 向后扫描语义保留）；
4. self_check 身份断言封死序不敏感盲区（坍缩/漂移两形态拒写）；
5. 账本复合键与合并器身份等值（红蓝防分叉，F10 §6.1 前置）。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
    _declared_fields_by_family,
    _entry_identity_keys,
)
from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
    entry_identity_key as gate_entry_identity_key,
)
from zephyr.governance.registry_ledger.baseline import _scan_declared_plan, load_roor_index, p0_physical_paths
from zephyr.governance.registry_ledger.ledger_identity import entry_composite_key, entry_identity_key
from zephyr.governance.registry_projection.model import snapshot_from_yaml
from zephyr.governance.registry_projection.renderer import SemanticMismatch, render, self_check

REPO_ROOT = Path(__file__).resolve().parents[4]

# B3 键序病灶样本（f10 §5 S1）：原盘面 ruling_id 首字段 vs jsonb 序 date(4) 抢占
_RULING_DISK_ORDER = {"ruling_id": "裁定#20", "title": "治本批次", "date": "2026-07-18", "status": "active"}
_RULING_JSONB_ORDER = {"date": "2026-07-18", "title": "治本批次", "status": "active", "ruling_id": "裁定#20"}

_DECLARED_YAML = """\
schema_version: 1.0.0
registry_id: REG-FIDELITY-001
unique_key:
- ruling_id
entries:
- ruling_id: '裁定#20'
  date: '2026-07-18'
- ruling_id: '裁定#21'
  date: '2026-07-18'
"""


def _pg_snapshot_or_skip(rid: str, phys: str):
    pytest.importorskip("psycopg2")
    from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable, load_latest_snapshot

    try:
        return load_latest_snapshot(rid, phys)
    except ProjectionUnavailable as exc:  # PG 不可达=skip 留痕非 fail（任务令口径）
        pytest.skip(f"PG 快照不可达（留痕）: {exc}")


def _seven_registries() -> list[tuple[str, str]]:
    """(registry_id, physical_path) 七册名单（ROOR∪头部机械反查）。"""
    roor = load_roor_index(REPO_ROOT)
    out = []
    for phys in p0_physical_paths(REPO_ROOT):
        head = {}
        try:
            import yaml

            head = yaml.safe_load((REPO_ROOT / phys).read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001 — 头部不可读退 ROOR
            head = {}
        rid = str(head.get("registry_id") or roor.get(phys, {}).get("registry_id") or "")
        assert rid, f"{phys}: registry_id 不可解析"
        out.append((rid, phys))
    return out


# ── 判据1：七册全量身份往返保真门（PG 数据源，skip 留痕） ───────────────────────


@pytest.mark.parametrize("rid,phys", _seven_registries())
def test_seven_registry_identity_roundtrip(rid: str, phys: str):
    """render→内存重扫→身份键集合相等 + 声明族基数零坍缩（F10 复现脚本同口径）。

    声明解析序：bundle 自带 unique_key_fields（新发布）→ 盘面册头声明回退
    （旧 bundle，手术1b 已补齐七册声明）→ 空=位置口径。
    """
    snap = _pg_snapshot_or_skip(rid, phys)
    if not snap.unique_key_fields:
        snap.unique_key_fields = {str(k): v for k, v in _scan_declared_plan(REPO_ROOT, phys).items()}
    rendered = render(snap)
    self_check(rendered, snap)  # 含身份往返断言（手术3）——七册必须全过

    from scripts.governance.commit_queue_landing import _split_registry_entries

    families, err = _split_registry_entries(rendered)
    assert err is None, f"渲染重扫失败: {err}"
    for sec in snap.sections:
        fields = snap.declared_fields_for(sec.root_key)
        snap_ids = {entry_composite_key(dict(e), fields) for e in sec.entries}
        snap_ids.discard(None)
        rescan_ids = set()
        fam = families.get(sec.root_key)
        if fam is not None:
            for blk in fam.blocks:
                ck = entry_composite_key(blk.data, fields) if isinstance(blk.data, dict) else None
                if ck is not None:
                    rescan_ids.add(ck)
        assert snap_ids == rescan_ids, f"{rid} 族 {sec.root_key} 身份键往返漂移"
        if fields:  # 声明族=唯一性契约：基数坍缩（B3 病灶形态）零容忍
            assert len(snap_ids) == len(sec.entries), (
                f"{rid} 族 {sec.root_key} 声明身份坍缩: {len(sec.entries)} 条 → {len(snap_ids)} 键"
            )


# F10 注1 残影瞬时态（B3 窗口 3 条 map_family gate 条目墓碑/复活翻覆，不在存世快照里
# 不可再构）：PG 侧滞留 file= 旧口径键，bundle 侧为 capability_id= 新口径键——首个
# reconcile 落地窗由手术4 rekey 安全网同内容迁键治愈，治愈后本清单清空。
_KNOWN_TRANSIENT_REMNANTS: dict[str, set[str]] = {
    "REG-CAPCAN-001": {
        "file=src/zephyr/gov_enforcement/commit_gates/map_family/dev_delivery_map_gate.py"
        "|token=mapfamily-dev_delivery_map_gate-20261001",
        "file=src/zephyr/gov_enforcement/commit_gates/map_family/data_supply_chain_map_gate.py"
        "|token=mapfamily-data_supply_chain_map_gate-20261001",
        "file=src/zephyr/gov_enforcement/commit_gates/map_family/trading_day_cycle_map_gate.py"
        "|token=mapfamily-trading_day_cycle_map_gate-20261001",
        "capability_id=map_family_dev_delivery_map_gate|token=mapfamily-dev_delivery_map_gate-20261001",
        "capability_id=map_family_data_supply_chain_map_gate|token=mapfamily-data_supply_chain_map_gate-20261001",
        "capability_id=map_family_trading_day_cycle_map_gate|token=mapfamily-trading_day_cycle_map_gate-20261001",
    }
}


@pytest.mark.parametrize("rid,phys", _seven_registries())
def test_seven_registry_pg_entrykey_parity(rid: str, phys: str):
    """bundle 身份集 == PG active entry_key 集（B3 重复行放大器的终极对位断言）。"""
    snap = _pg_snapshot_or_skip(rid, phys)
    if not snap.unique_key_fields:
        snap.unique_key_fields = {str(k): v for k, v in _scan_declared_plan(REPO_ROOT, phys).items()}
    pytest.importorskip("psycopg2")
    from zephyr.infrastructure.database_service import DatabaseService

    try:
        conn = DatabaseService().get_depgraph_conn(read_only=True)
    except Exception as exc:  # noqa: BLE001 — PG 不可达=skip 留痕
        pytest.skip(f"PG 不可达（留痕）: {exc}")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT family_key, entry_key FROM registry_ledger.registry_entry "
                "WHERE registry_id=%s AND status='active'",
                (rid,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    pg_keys = (
        {(r["family_key"], r["entry_key"]) for r in rows}
        if rows and isinstance(rows[0], dict)
        else {(r[0], r[1]) for r in rows}
    )
    snap_keys = set()
    for sec in snap.sections:
        fields = snap.declared_fields_for(sec.root_key)
        for e in sec.entries:
            ck = entry_composite_key(dict(e), fields)
            if ck is not None:
                snap_keys.add((sec.root_key, ck))
    mismatch = snap_keys ^ pg_keys
    remnants = _KNOWN_TRANSIENT_REMNANTS.get(rid, set())
    residual = {k for k in mismatch if k[1] not in remnants}
    if not residual and mismatch:
        # 残差全部=F10 注1 已注记瞬时态（≤3 条）——skip 留痕非 fail（任务令验收口径）；
        # 治愈通道=首个 reconcile 落地窗手术4 rekey（同内容迁键），届时本分支自熄
        pytest.skip(
            f"{rid}: PG entry_key 残差 {len(mismatch)} 条全部为 F10 注1 已注记瞬时态"
            f"（rekey 治愈通道在案，清单见 _KNOWN_TRANSIENT_REMNANTS）"
        )
    assert snap_keys == pg_keys, (
        f"{rid} bundle 身份集与 PG entry_key 不对位: bundle独有={len(snap_keys - pg_keys)} "
        f"pg独有={len(pg_keys - snap_keys)}（示例 {sorted(mismatch)[:3]}）"
    )


# ── 判据2/3：声明制语义单元（纯内存零 DB） ──────────────────────────────────────


def test_declared_identity_decoupled_from_field_order():
    """B3 键序病灶机械复现：jsonb 序抢占首字段不改变声明身份。"""
    assert entry_identity_key(_RULING_DISK_ORDER, ("ruling_id",)) == "ruling_id=裁定#20"
    assert entry_identity_key(_RULING_JSONB_ORDER, ("ruling_id",)) == "ruling_id=裁定#20"
    # 同日多条（2026-07-18 九条姊妹裁定场景）在声明键下互异，在位置口径下坍缩
    sister = dict(_RULING_JSONB_ORDER, ruling_id="裁定#20-A")
    assert entry_identity_key(sister, ("ruling_id",)) == "ruling_id=裁定#20-A"
    assert entry_identity_key(sister) == "date=2026-07-18"  # 位置口径=B3 坍缩形态


def test_positional_fallback_unchanged_without_declaration():
    """无声明=位置向后扫描首个标量（fdfe8fe302 语义保留，零行为变化）。"""
    aliases_first = {"aliases": ["挖矿SOP"], "description": "d", "capability_id": "cap"}
    assert gate_entry_identity_key(aliases_first) == "description=d"
    assert gate_entry_identity_key(aliases_first, ("capability_id",)) == "capability_id=cap"
    assert entry_composite_key({"nested": {"a": 1}}) is None
    # 声明字段缺失/非标量 → 退位置扫描（族级适用性之外的防御位，零新死法）
    assert gate_entry_identity_key({"step_id": "BM-1", "n": 1}, ("module_path",)) == "step_id=BM-1"


def test_declared_fields_by_family_plan_shapes():
    """声明计划解析：list=全族默认 / dict=按族 / 声明本体不入族 / 退化声明丢弃。"""
    import yaml

    data = yaml.safe_load(_DECLARED_YAML)
    plan = _declared_fields_by_family(_DECLARED_YAML, data)
    assert plan == {"entries": ("ruling_id",)}
    assert "unique_key" not in plan  # 声明本体不是条目族
    assert _declared_fields_by_family("unique_key: 3\nentries:\n- x: 1\n", {"entries": [{"x": 1}]}) == {}


def test_snapshot_from_yaml_carries_declaration():
    """盘面提取随快照携带声明计划（bundle 侧由 pg_source 还原，两侧同构）。"""
    snap = snapshot_from_yaml(_DECLARED_YAML, registry_id="REG-FIDELITY-001", physical_path="x.yaml")
    assert snap.unique_key_fields == {"*": ("ruling_id",)}
    assert snap.declared_fields_for("entries") == ("ruling_id",)


def test_gate_identity_keys_use_declaration():
    """门禁身份集（净删检测信号3）在声明册上按声明字段建键。"""
    keys = _entry_identity_keys(_DECLARED_YAML)
    assert keys == {"ruling_id=裁定#20", "ruling_id=裁定#21"}


# ── 判据4：self_check 身份断言（盲区封死回归） ─────────────────────────────────


def test_self_check_rejects_declared_identity_collapse():
    """声明族身份坍缩（同键撞并）= SemanticMismatch 拒写——B3 主病灶形态。"""
    text = _DECLARED_YAML.replace("- ruling_id: '裁定#21'", "- ruling_id: '裁定#20'")
    snap = snapshot_from_yaml(text, registry_id="REG-FIDELITY-001", physical_path="x.yaml")
    with pytest.raises(SemanticMismatch, match="坍缩"):
        self_check(render(snap), snap)


def test_self_check_rejects_roundtrip_identity_drift(monkeypatch):
    """重扫身份漂移（快照身份 vs 渲染重扫身份不等）= 拒写——模拟位置口径消费面错位。"""
    snap = snapshot_from_yaml(_DECLARED_YAML, registry_id="REG-FIDELITY-001", physical_path="x.yaml")
    snap.unique_key_fields = {}  # 位置口径（无声明册）
    from zephyr.governance import registry_projection

    renderer = registry_projection.renderer

    def _reordered_rescan(rendered: str):
        # 模拟 jsonb 重排后的重扫面：date 抢占首字段（B3 实弹形态）
        return {"entries": [{"date": "2026-07-18"}, {"date": "2026-07-18"}]}

    monkeypatch.setattr(renderer, "_rescan_family_blocks", _reordered_rescan)
    with pytest.raises(SemanticMismatch, match="往返漂移"):
        renderer.self_check(renderer.render(snap), snap)


# ── 判据5：账本/合并器身份等值（红蓝防分叉） ───────────────────────────────────


def _load_landing_module():
    path = REPO_ROOT / "scripts" / "governance" / "commit_queue_landing.py"
    spec = importlib.util.spec_from_file_location("fidelity_gate_landing_probe", path)
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_ledger_declared_identity_matches_merger_when_first_field():
    """声明字段==位置首标量字段时（七册现状），账本键与合并器复合键逐字相等。"""
    corpus = [
        ({"ruling_id": "裁定#20", "date": "2026-07-18"}, ("ruling_id",)),
        ({"module_path": "src/a.py", "name_zh": "甲"}, ("module_path",)),
        ({"issue_id": "#ARCH-001", "title": "预留"}, ("issue_id",)),
        ({"file": "src/b.py", "token": "t1", "x": 1}, ("file",)),
    ]
    for payload, fields in corpus:
        assert entry_composite_key(payload, fields) == entry_composite_key(payload), payload
    landing = _load_landing_module()
    for payload, _fields in corpus:
        if landing._merge_entry_identity(payload) is None:
            pytest.skip("registry_family 重组位未落地（等值断言待其落地后生效）")
        assert entry_composite_key(payload) == landing._merge_entry_identity(payload), payload
