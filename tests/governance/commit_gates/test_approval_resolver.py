# [A_test] module_id: MOD-GOV_approval_resolver | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_approval_resolver
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_approval_resolver.py — 审批判定收敛器三通道单测（QCure M4.1，st-qcure-20260925 施工线C）

权威依据：approval_resolver.py（resolve_approval / ApprovalVerdict）

测试组：
- TestRulingChannel: 裁定通道——真裁定+路径命中 PASS；fnmatch/目录前缀双语义；
  非 active 不认；过期不认；无 approved_paths 不认；路径未覆盖不认
- TestMarkerChannel: marker 防伪——实存 id 放行；伪造 id 拒绝（堵假号洞）；
  缺册 unknown；# 前缀归一化；注册表路径为目录（读异常）不抛异常收敛 unknown
- TestVerdictContract: 永不抛异常 + source 取值封闭
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from zephyr.gov_enforcement.commit_gates.approval_resolver import (
    SOURCE_MARKER,
    SOURCE_NONE,
    SOURCE_RULING,
    SOURCE_UNKNOWN,
    resolve_approval,
)

_CATALOGS = "docs/01_policies_and_standards/_registry/catalogs"
_RULES_HIT = "docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml"


def _make_issue_registry(root: Path, issue_ids: list[str]) -> Path:
    """tmp_path 造议题册 fixture（entries[].issue_id 最小形）。"""
    path = root / _CATALOGS / "architecture_issue_registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"entries": [{"issue_id": i} for i in issue_ids]}
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


def _make_ruling_registry(root: Path, rulings: list[dict]) -> Path:
    """tmp_path 造裁定册 fixture。"""
    path = root / _CATALOGS / "ruling_registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"entries": rulings}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def _ruling(**overrides) -> dict:
    """裁定条目基模（对齐 ruling_registry entry_schema + M4 新字段）。"""
    entry = {
        "ruling_id": "裁定#410",
        "title": "终局班两件收口批准",
        "date": "2026-09-24",
        "category": "架构",
        "status": "active",
        "summary": "rules 清道三袋落地",
        "affected_files": [],
        "related_arch": [],
        "related_rulings": [],
        "superseded_by": None,
        "approved_paths": ["docs/01_policies_and_standards/rules/"],
        "expires_at": "2099-01-01",
    }
    entry.update(overrides)
    return entry


class TestRulingChannel:
    """裁定通道：active + 未过期 + approved_paths 覆盖。"""

    def test_active_ruling_covers_hit_passes(self, tmp_path):
        """真裁定 + 目录前缀覆盖命中路径 → PASS，detail 引裁定号。"""
        _make_ruling_registry(tmp_path, [_ruling()])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is True
        assert v.source == SOURCE_RULING
        assert "裁定#410" in v.detail

    def test_fnmatch_pattern_coverage(self, tmp_path):
        """approved_paths 用 fnmatch glob 模式 → 逐文件匹配覆盖。"""
        _make_ruling_registry(tmp_path, [_ruling(approved_paths=["docs/01_policies_and_standards/rules/*.yaml"])])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is True
        assert v.source == SOURCE_RULING

    def test_non_active_status_rejected(self, tmp_path):
        """status=decided（越四值枚举）不构成授权 → 不放行。"""
        _make_ruling_registry(tmp_path, [_ruling(status="decided")])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False

    def test_expired_ruling_rejected(self, tmp_path):
        """expires_at 已过 → 不放行。"""
        _make_ruling_registry(tmp_path, [_ruling(expires_at="2020-01-01")])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_NONE

    def test_expiry_today_boundary_still_valid(self, tmp_path):
        """expires_at=当日（UTC）仍有效，昨日过期（有界窗口边界语义）。"""
        today = datetime.now(timezone.utc).date()
        _make_ruling_registry(tmp_path, [_ruling(expires_at=today.isoformat())])
        assert resolve_approval([_RULES_HIT], None, tmp_path).approved is True
        _make_ruling_registry(tmp_path, [_ruling(expires_at=(today - timedelta(days=1)).isoformat())])
        assert resolve_approval([_RULES_HIT], None, tmp_path).approved is False

    def test_corrupted_expires_at_not_authorized(self, tmp_path):
        """expires_at 字段损坏 → 该条不构成授权（保守）。"""
        _make_ruling_registry(tmp_path, [_ruling(expires_at="not-a-date")])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False

    def test_no_approved_paths_not_authorized(self, tmp_path):
        """无 approved_paths（纯登记语义）→ 不放行。"""
        _make_ruling_registry(tmp_path, [_ruling(approved_paths=None)])
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False

    def test_path_not_covered_rejected(self, tmp_path):
        """命中路径不在 approved_paths 覆盖内 → 不放行。"""
        _make_ruling_registry(tmp_path, [_ruling()])
        v = resolve_approval(["AGENTS.md"], None, tmp_path)
        assert v.approved is False

    def test_missing_ruling_registry_unknown(self, tmp_path):
        """裁定册缺册 → unknown（fail-open 语义信号，gate 侧接手降级）。"""
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_UNKNOWN


class TestMarkerChannel:
    """marker 通道防伪：id 必须实存。"""

    def test_registered_marker_passes(self, tmp_path):
        """id 实存于议题册 → PASS（source=marker）。"""
        _make_issue_registry(tmp_path, ["ARCH-MODEL-LIFECYCLE-001"])
        v = resolve_approval([".gitignore"], "fix: [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]", tmp_path)
        assert v.approved is True
        assert v.source == SOURCE_MARKER

    def test_forged_marker_rejected(self, tmp_path):
        """id 查无（册可读但无此号）→ 防伪拒绝（堵假号洞）。"""
        _make_issue_registry(tmp_path, ["ARCH-OTHER-999"])
        v = resolve_approval([".gitignore"], "fix: [ARCH-APPROVAL:ARCH-FAKE-123]", tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_NONE
        assert "not registered" in v.detail

    def test_marker_missing_issue_registry_unknown(self, tmp_path):
        """议题册缺册（无法判真伪）→ unknown，gate 侧保持 fail-open。"""
        v = resolve_approval([".gitignore"], "fix: [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]", tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_UNKNOWN

    def test_marker_hash_prefix_normalized(self, tmp_path):
        """'#ARCH-007' 与 'ARCH-007' 同一编号空间（去 # 归一化比对）。"""
        _make_issue_registry(tmp_path, ["#ARCH-007"])
        v = resolve_approval([".gitattributes"], "x [ARCH-APPROVAL:#ARCH-007]", tmp_path)
        assert v.approved is True

    def test_unreadable_registry_never_raises(self, tmp_path):
        """议题册路径为目录（读异常）→ 收敛 unknown，不抛异常。"""
        bad = tmp_path / _CATALOGS / "architecture_issue_registry.yaml"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.mkdir()  # 目录替代文件 → open 抛 IsADirectoryError
        v = resolve_approval([".gitignore"], "fix: [ARCH-APPROVAL:ARCH-X-1]", tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_UNKNOWN


class TestVerdictContract:
    """verdict 契约：永不抛异常 + source 取值封闭。"""

    def test_never_raises_with_none_inputs(self):
        """全空输入 → 返回 verdict 不抛异常。"""
        v = resolve_approval([], None, None)
        assert v.approved is False
        assert v.source in (SOURCE_NONE, SOURCE_UNKNOWN)

    def test_ruling_registry_invalid_yaml_unknown(self, tmp_path):
        """裁定册 YAML 语法损坏 → unknown（读失败降级，不 fail-closed）。"""
        path = tmp_path / _CATALOGS / "ruling_registry.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("entries: [unclosed", encoding="utf-8")
        v = resolve_approval([_RULES_HIT], None, tmp_path)
        assert v.approved is False
        assert v.source == SOURCE_UNKNOWN

    def test_forged_marker_still_allows_independent_ruling(self, tmp_path):
        """伪造 marker 自身不放行，但独立有效裁定仍可授权（通道独立）。"""
        _make_issue_registry(tmp_path, ["ARCH-OTHER-999"])
        _make_ruling_registry(tmp_path, [_ruling()])
        v = resolve_approval([_RULES_HIT], "x [ARCH-APPROVAL:ARCH-FAKE-1]", tmp_path)
        assert v.approved is True
        assert v.source == SOURCE_RULING
