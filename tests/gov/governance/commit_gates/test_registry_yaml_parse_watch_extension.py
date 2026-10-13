# [MODULE] tests.gov.governance.commit_gates.test_registry_yaml_parse_watch_extension
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [CONSUMERS] C 件质量守卫：REGISTRY-YAML-PARSE watch 面 P0 扩面（六册）+投影 tamper 全档案生效
# [INVARIANTS] 全部用例 tmp 状态文件/桩 gateway（零主区；PG 一律桩 conn，零真连）；
#   红蓝双向=手改拦/生成器过；独立成文件避让他会话 staged 的 test_registry_yaml_parse_gate.py WIP（共写禁令）
# [MODIFY-GUARD] 新建 2026-10-09 st-regsolo-20261010（热册单口写战役 C 件随批测试，tests/ 豁免 token）
# [TTL] permanent
"""REGISTRY-YAML-PARSE watch 面扩面守卫（裁定#502 战役 C 件）。

P0 七热册中六册进 watch（module_translation 随翻译轨改道 A2 同批上线）：
hot_registry_basic 档=parse+根键唯一；投影 tamper 判别对全档案生效——
已武装册 staged≠状态文件指纹必拦（手改无效），生成器重打后 staged==指纹必过。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (  # noqa: E402
    _WATCH_FILES,
    make_registry_yaml_parse_gate,
)
from zephyr.shared.io.file_utils import content_sha256  # noqa: E402

_RULE = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"
_CAND = "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml"

_VALID_RULING = """module_id: REG-RULING-001
ttl: permanent
title: 裁定中央登记表
unique_key:
- ruling_id
entries:
- ruling_id: "裁定#502"
  title: t
"""


def test_watch_table_contains_p0_six():
    """六册在挂（module_translation 显式缓武装=A2 车道随翻译轨改道上线）。"""
    assert _WATCH_FILES[_RULE] == "hot_registry_basic"
    assert _WATCH_FILES[_CAND] == "hot_registry_basic"
    assert (
        _WATCH_FILES["docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"]
        == "hot_registry_basic"
    )
    assert (
        _WATCH_FILES["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"]
        == "hot_registry_basic"
    )
    assert _WATCH_FILES["architecture_model/contracts/error_code_registry.yaml"] == "hot_registry_basic"
    assert "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml" not in _WATCH_FILES


def test_hot_registry_basic_duplicate_root_key_blocks():
    """basic 档结构断言生效：双根键必拦（PyYAML 静默取后者盲区）。"""
    dup = _VALID_RULING + "\nentries2_dup: []\nentries:\n- ruling_id: x\n"

    class GW:
        project_root = "."

        def run_git(self, cmd):
            if cmd[:3] == ["git", "diff", "--cached"]:
                return SimpleNamespace(returncode=0, stdout=_RULE)
            if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
                return SimpleNamespace(returncode=0, stdout=dup)
            raise AssertionError(f"unexpected: {cmd}")

    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(GW(), [], session_id=None)
    assert ok is False and "顶层根键重复" in msg


def _state_gateway(tmp_path: Path, staged_text: str):
    """桩 gateway：project_root=tmp（带状态文件）；staged 内容由调用方定。"""

    class GW:
        pass

    gw = GW()
    gw.project_root = str(tmp_path)

    def run_git(cmd):
        if cmd[:3] == ["git", "diff", "--cached"]:
            return SimpleNamespace(returncode=0, stdout=_RULE)
        if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
            return SimpleNamespace(returncode=0, stdout=staged_text)
        raise AssertionError(f"unexpected: {cmd}")

    gw.run_git = run_git
    state_dir = tmp_path / ".runtime" / "projection"
    state_dir.mkdir(parents=True, exist_ok=True)
    return gw, state_dir


def test_projection_tamper_blocks_hand_edit(tmp_path):
    """红证：已武装册手改一行 → staged≠状态指纹 → 必拦（tamper 对 basic 档生效）。"""
    rendered = _VALID_RULING
    hand_edited = rendered.replace("title: t", "title: 手改")
    gw, state_dir = _state_gateway(tmp_path, hand_edited)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps(
            {"registries": {"REG-RULING-001": {"registry_path": _RULE, "content_sha256": content_sha256(rendered)}}}
        ),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is False, "手改投影册必拦"
    assert "意图 API" in msg or "投影" in msg


def test_generator_rendered_diff_passes(tmp_path):
    """蓝证：生成器重打后 staged==状态指纹 → 必过（合法 render-sync 通道畅通）。"""
    rendered = _VALID_RULING
    gw, state_dir = _state_gateway(tmp_path, rendered)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps(
            {"registries": {"REG-RULING-001": {"registry_path": _RULE, "content_sha256": content_sha256(rendered)}}}
        ),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is True, f"生成器产物必过（got: {msg}）"


def test_unarmed_registry_fail_open(tmp_path):
    """未武装册（状态文件无本册条目）= fail-open 零行为（武装顺序自由，门不误伤）。"""
    gw, state_dir = _state_gateway(tmp_path, _VALID_RULING)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps({"registries": {"REG-OTHER-001": {"registry_path": "docs/x.yaml", "content_sha256": "ab"}}}),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is True, f"未武装册零行为（got: {msg}）"


# ===========================================================================
# P0-2② 真源对齐：HEAD 滞后差集改由 PG 账本判该不该拦（st-maint7-20261014）
# ===========================================================================
# 病根实证（10-13 夜 6 只死信同一条）：拦袋的
# docs/_working/tdm_goal_structure_research_2026_10_13.md 的 token 在 PG 里
# status='retired'，而当时 HEAD 的 YAML 还挂着退役残留——守门拿滞后面当基准，
# 把按真源重打投影的无辜袋连杀多轮。本节验"只加对账、不松门禁"两面。

_CAP_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"


def _cap_yaml(entries: list[tuple[str, str]]) -> str:
    body = "schema_version: 1.1.0\ncapabilities: []\ncreation_tokens:\n"
    for file_v, token_v in entries:
        body += f"  - file: {file_v}\n    token: {token_v}\n"
    return body


class _FakeCursor:
    """按 SQL 形态判命中：entry_key=%s 精确／LIKE %s 前缀（键形漂移保守面）。"""

    def __init__(self, hits):
        self._hits = hits
        self._res = None

    def execute(self, sql, params):
        self._res = self._hits(sql, tuple(params))

    def fetchone(self):
        return self._res

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _FakeConn:
    def __init__(self, hits):
        self._hits = hits

    def cursor(self):
        return _FakeCursor(self._hits)

    def close(self):
        pass


def _patch_pg(monkeypatch, hits):
    """桩掉账本连接（PG 零真连）；calls 计数供"无差集不打扰账本"自证。"""
    from zephyr.infrastructure import database_service as dbs

    calls = {"n": 0}

    def _get(self, read_only=False):
        calls["n"] += 1
        if isinstance(hits, Exception):
            raise hits
        return _FakeConn(hits)

    monkeypatch.setattr(dbs.DatabaseService, "get_depgraph_conn", _get, raising=False)
    return calls


def _lag_gateway(tmp_path, head_text):
    gw = SimpleNamespace(project_root=str(tmp_path))
    gw.run_git = lambda cmd: SimpleNamespace(returncode=0, stdout=head_text)
    return gw


_HEAD_TWO = _cap_yaml([("a.md", "t-a"), ("b.md", "t-b")])
_STAGED_ONE = _cap_yaml([("a.md", "t-a")])
_MISSING_KEY = "file=b.md|token=t-b"


def test_pg_retired_entry_no_longer_kills_innocent_bag(tmp_path, monkeypatch):
    """真源不背书（retired/查无）⇒ HEAD 那份是残留：放行＋落审计（10-13 夜六袋形态）。"""
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    calls = _patch_pg(monkeypatch, lambda sql, params: None)
    issue = _head_token_lag_issue(_lag_gateway(tmp_path, _HEAD_TWO), _CAP_REL, _STAGED_ONE, "")
    assert issue is None, f"PG 已 retire 的残留不该判死: {issue}"
    assert calls["n"] == 1, "对账必须只开一次连接"
    audit = tmp_path / ".runtime" / "gate_audit" / "registry_yaml_parse.jsonl"
    assert audit.exists(), "放行必须留审计痕（可见性不靠沉默）"
    rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
    assert rec["event"] == "head_token_lag_pg_cleared"
    assert rec["cleared_by_pg"] == ["b.md|token=t-b"]
    assert rec["still_blocking"] == []


def test_pg_active_entry_still_blocks(tmp_path, monkeypatch):
    """真源 active 命中该复合键⇒ staged 缺它＝真整档回退，照拦（判据本体不松）。"""
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    def hits(sql, params):
        return {"?column?": 1} if params[2] == _MISSING_KEY and "entry_key=%s" in sql else None

    _patch_pg(monkeypatch, hits)
    issue = _head_token_lag_issue(_lag_gateway(tmp_path, _HEAD_TWO), _CAP_REL, _STAGED_ONE, "")
    assert issue is not None and "相对 HEAD 少 1 条" in issue, issue
    assert "PG 对账：1 条 active 照拦" in issue, issue


def test_pg_key_drift_same_file_active_still_blocks(tmp_path, monkeypatch):
    """精确键未命中、同 file 却有 active 条目（键形漂移）⇒ 保守照拦，宁不误放。"""

    def hits(sql, params):
        return {"?column?": 1} if "LIKE %s" in sql else None

    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    issue = _head_token_lag_issue(_lag_gateway(tmp_path, _HEAD_TWO), _CAP_REL, _STAGED_ONE, "")
    assert issue is not None and "相对 HEAD 少 1 条" in issue, issue


def test_pg_unreachable_keeps_block(tmp_path, monkeypatch):
    """账本不可达＝全照拦——禁止"读不到账本"变成放行（与 create_guard T4 同哲学）。"""
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    _patch_pg(monkeypatch, RuntimeError("pg down"))
    issue = _head_token_lag_issue(_lag_gateway(tmp_path, _HEAD_TWO), _CAP_REL, _STAGED_ONE, "")
    assert issue is not None and "相对 HEAD 少 1 条" in issue, issue
    assert "照拦" in issue, issue


def test_degenerate_identity_cannot_be_reconciled_blocks(tmp_path, monkeypatch):
    """非复合身份（无 file/token 对的退化条目）无法对账⇒照拦。"""
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    calls = _patch_pg(monkeypatch, lambda sql, params: None)
    head = "creation_tokens:\n- path: legacy_entry.md\n"
    issue = _head_token_lag_issue(_lag_gateway(tmp_path, head), _CAP_REL, "creation_tokens: []\n", "")
    assert issue is not None and "相对 HEAD 少 1 条" in issue, issue
    assert calls["n"] == 0, "无复合身份可对账时不该去开账本连接"


def test_no_missing_never_touches_pg(tmp_path, monkeypatch):
    """HEAD==staged（无差集）⇒ 零账本开销（常见路径不加成本）。"""
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _head_token_lag_issue

    calls = _patch_pg(monkeypatch, lambda sql, params: None)
    issue = _head_token_lag_issue(_lag_gateway(tmp_path, _STAGED_ONE), _CAP_REL, _STAGED_ONE, "")
    assert issue is None
    assert calls["n"] == 0
