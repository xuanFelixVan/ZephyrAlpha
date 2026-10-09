# [MODULE] tests.gov.governance.test_commit_queue_landing_pg_render
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.commit_queue_landing
# [CONSUMERS] B 件质量守卫：已入账本册物化=PG 现读 render（袋字节退役）+袋删禁令+纪元探针
# [INVARIANTS] 全部用例 monkeypatch ROOR/账本/渲染注入点，零 PG 零 git 零盘面写（tmp_path 外零触碰）；
#   红证判据=返回字节必须来自 render 替身而非袋字节（蒸发通道退役的本质断言）
# [MODIFY-GUARD] 新建 2026-10-09 st-regsolo-20261010（热册单口写战役 B 件随批测试，tests/ 豁免 token）
# [TTL] permanent
"""commit_queue_landing B 件单测：已入账本册物化从袋内旧快照切 PG 现读 render。

历史病根（10-09 三起 token 蒸发/-271 回滚险情机制面）：注册表族物化从袋内旧快照
派生字节（快进短路整档覆写/条目级合并皆以袋字节为 theirs 真源）。B 件后已入账本册
物化唯一真源=PG registry_snapshot 现读 render——本件守三不变量：
①返回字节来自 render 而非袋字节；②render==dev 时 noop 且留审计注；
③PG 不可达=环境类瞬态退 pending（禁静默退袋字节）；④账本册禁袋删。
"""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.governance.commit_queue_landing as cql
from scripts.governance.commit_queue_landing import PgRenderUnavailable, WorktreeLanding

_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_PG_SRC = "zephyr.governance.registry_projection.pg_source"
_RENDERER = "zephyr.governance.registry_projection.renderer"
_BASELINE = "zephyr.governance.registry_ledger.baseline"


def _lander(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, rid: str | None, *, ours_text: str | None = "SAME_AS_DEV\n"
) -> WorktreeLanding:
    """最小 Lander 替身（绕过 __init__ 的 worktree/gateway 重装备；仅挂本件被测面）。

    ours_text=None 模拟 dev 侧无此文件（cat-file rc!=0）。
    """
    lander = object.__new__(WorktreeLanding)
    lander.repo_root = tmp_path
    lander.worktree_path = tmp_path / "wt"

    class _R:
        returncode = 0 if ours_text is not None else 1
        stdout = ours_text or ""

    lander._git_repo = lambda *a, **k: _R()
    monkeypatch.setattr(
        f"{_BASELINE}.load_roor_index",
        lambda root: {_REL: {"registry_id": rid}} if rid else {},
    )
    return lander


def test_epoch_probe_present():
    """装载验证探针在册（守护重启后启动日志打印本值=新码在岗四证之一）。"""
    assert cql.LANDING_MATERIALIZATION_EPOCH.startswith("regsolo-b-20261009")


def test_ledger_backed_materializes_from_pg_render(tmp_path, monkeypatch):
    """不变量①：账本册返回字节=PG render 产物，袋内旧快照字节整体不进入物化。"""
    lander = _lander(tmp_path, monkeypatch, "REG-CAPCAN-001")
    monkeypatch.setattr(f"{_PG_SRC}.load_latest_snapshot", lambda rid, phys: object())
    monkeypatch.setattr(f"{_RENDERER}.render", lambda snap: "PG_RENDER_TEXT\n")

    class _Item(dict):
        pass

    out = lander._merge_registry_file(_Item(), _REL, b"STALE_BAG_BYTES\n", "olddev")
    assert out == b"PG_RENDER_TEXT\n"  # 袋字节被无视——蒸发通道退役的本质断言


def test_ledger_backed_render_equals_dev_noop_with_audit(tmp_path, monkeypatch):
    """不变量②：render==dev → None（noop）+ noop_audit 注（确定性投影吸收）。"""
    lander = _lander(tmp_path, monkeypatch, "REG-CAPCAN-001")
    monkeypatch.setattr(f"{_PG_SRC}.load_latest_snapshot", lambda rid, phys: object())
    monkeypatch.setattr(f"{_RENDERER}.render", lambda snap: "SAME_AS_DEV\n")
    item = {"meta": {}}
    out = lander._merge_registry_file(item, _REL, b"STALE_BAG_BYTES\n", "olddev")
    assert out is None
    assert "确定性投影吸收" in item["meta"]["noop_audit"]


def test_not_in_roor_returns_none_falls_back_to_legacy(tmp_path, monkeypatch):
    """未入账本册（ROOR 无 registry_id）→ None → 调用方落回既有三向合并（cutover 安全）。"""
    lander = _lander(tmp_path, monkeypatch, None)
    assert lander._pg_render_registry_text(_REL) is None
    assert lander._ledger_registry_id(_REL) is None


def test_no_published_snapshot_is_not_enrolled(tmp_path, monkeypatch):
    """ROOR 有 id 但 PG 无已发布快照=未入账本册 → None（不误判 PG 宕机）。"""
    lander = _lander(tmp_path, monkeypatch, "REG-NOTYET-001")
    from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable

    def _load(rid, phys):
        raise ProjectionUnavailable(f"registry_id={rid} 无已发布快照")

    monkeypatch.setattr(f"{_PG_SRC}.load_latest_snapshot", _load)
    assert lander._pg_render_registry_text(_REL) is None


def test_pg_down_raises_transient_never_falls_back_to_bag(tmp_path, monkeypatch):
    """不变量③：PG 不可达=PgRenderUnavailable（环境类瞬态退 pending），禁静默退袋字节。"""
    lander = _lander(tmp_path, monkeypatch, "REG-CAPCAN-001")
    from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable

    def _load(rid, phys):
        raise ProjectionUnavailable("registry_snapshot 不可读: OperationalError: connection refused")

    monkeypatch.setattr(f"{_PG_SRC}.load_latest_snapshot", _load)
    with pytest.raises(PgRenderUnavailable, match="退 pending"):
        lander._pg_render_registry_text(_REL)
    assert issubclass(PgRenderUnavailable, cql.SnapshotVerifyError)


def test_delete_of_ledger_backed_registry_blocked(tmp_path, monkeypatch):
    """不变量④：账本册禁袋删——退役唯一通道=api.retire（袋 delete 死信带处方）。"""
    lander = _lander(tmp_path, monkeypatch, "REG-CAPCAN-001")
    item = {"files": [{"path": _REL, "action": "delete"}]}
    with pytest.raises(RuntimeError, match="api.retire"):
        lander._apply_snapshot(item, tmp_path / "q", "olddev")


def test_delete_of_non_ledger_path_still_allowed(tmp_path, monkeypatch):
    """非账本册路径 delete 行为零变更（守卫不扩面）。"""
    lander = _lander(tmp_path, monkeypatch, None)
    f = tmp_path / "wt" / "docs" / "x" / "a.md"
    f.parent.mkdir(parents=True)
    f.write_text("x", encoding="utf-8")
    item = {"files": [{"path": "docs/x/a.md", "action": "delete"}]}
    out = lander._apply_snapshot(item, tmp_path / "q", "olddev")
    assert not f.exists() and len(out) == 1
