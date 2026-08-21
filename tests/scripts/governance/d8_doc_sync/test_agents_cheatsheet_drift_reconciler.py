# [A_test] module_id: MOD-TEST-711 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-agents_cheatsheet_drift | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] tests.scripts.governance.d8_doc_sync.test_agents_cheatsheet_drift_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_agents_cheatsheet_drift_reconciler.py — AGENTS.md 速查区数字漂移检测 reconciler 单测

权威依据：scripts/governance/d8_doc_sync/agents_cheatsheet_drift_reconciler.py（#ARCH-133，CAND-REGSYNC-001）
对标先例：tests/scripts/governance/d8_doc_sync/test_metric_count_drift_reconciler.py（同族模式）

测试组：
- TestTrigger: 触发条件判断（无关 commit 不触发，防风暴）
- TestParseAgentsCheatsheet: AGENTS.md 速查区解析（纯函数）
- TestLoadRoorTruth: ROOR 真值解析（纯函数，BREG 区段口径）
- TestReconcile: 完整校验流程（tmp_path 隔离真实文件）
- TestFactory: 工厂函数

测试隔离：tmp_path 构造临时 AGENTS.md 片段+临时真源文件，不碰真实 AGENTS.md/ROOR/注册表；
不依赖真实仓库状态。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DOC_SYNC_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d8_doc_sync"
if str(_DOC_SYNC_DIR) not in sys.path:
    sys.path.insert(0, str(_DOC_SYNC_DIR))

import agents_cheatsheet_drift_reconciler as _macdr  # noqa: E402
from agents_cheatsheet_drift_reconciler import (  # noqa: E402
    _ROW_MAP,
    _load_roor_truth,
    _parse_agents_cheatsheet,
    _should_trigger,
    make_agents_cheatsheet_drift_reconciler,
)

_CATALOGS_REL = "docs/01_policies_and_standards/_registry/catalogs"


@pytest.fixture(autouse=True)
def _repin_project_root():
    """重钉模块全局 _project_root：工厂 make_*(project_root) 会 global 改写模块级
    _project_root 及派生常量，tmp_path 测试会把全局钉到 tmp 根——本文件每个测试前后
    重钉真实根，防跨测试全局污染（同族先例 test_metric_count_drift_reconciler
    _repin_project_root fixture）。"""
    _macdr.make_agents_cheatsheet_drift_reconciler(_PROJECT_ROOT)
    yield
    _macdr.make_agents_cheatsheet_drift_reconciler(_PROJECT_ROOT)


# ============================================================================
# 夹具：tmp 真源内容构造（18 行映射由 _ROW_MAP 驱动，防硬编码漂移）
# ============================================================================

# 每行明细的计数（key → count）；告警阈值行固定 35；能力计数行固定 347
_ROW_COUNTS: dict[str, int] = {
    "universe": 6,
    "benchmark": 8,
    "cost_model": 5,
    "factor": 140,
    "strategy": 146,
    "risk_limit": 111,
    "technical_indicator": 41,
    "chart_pattern": 256,
    "execution_algo": 7,
    "data_asset": 206,
    "field_dictionary": 259,
    "experiment": 5,
    "seat": 16,
    "regime_cycle": 13,
    "model": 8,
    "event_calendar": 14,
    "macro_indicator": 16,
    "portfolio_model": 11,
    "alert_threshold": 35,
}


def _build_agents_text(
    table_total: int = 18,
    row_counts: dict[str, int] | None = None,
    capability_count: int = 347,
    include_capability_anchor: bool = True,
) -> str:
    """构造 tmp AGENTS.md 速查区片段（锚点措辞对齐真实文件行模式）。"""
    counts = dict(_ROW_COUNTS if row_counts is None else row_counts)
    lines = [
        "> **关键 registry 速查**：",
        "> - 告警阈值：[`alert_threshold_registry.yaml`](file:///d:/x/alert_threshold_registry.yaml)"
        f"（REG-ATH-001，监控/告警/复盘链路阈值 SSoT，{counts['alert_threshold']} 条/11 类；改阈值先改表）",
        ">",
        "> **业务资产 registry 速查**（#ARCH-BREG-001，" + f"{table_total} 表体系，施工总案=design_memos/62）：",
    ]
    for key, _reg_id, filename in _ROW_MAP:
        if key == "alert_threshold":
            continue
        lines.append(
            f"> - ✅ {key}：[`{filename}`](file:///d:/x/{filename})（{counts[key]} 条，测试夹具）"
        )
    lines.append(">")
    if include_capability_anchor:
        lines.append(
            "  - 真源：[`capability_canonical_file_registry.yaml`](file:///d:/x/capability_canonical_file_registry.yaml)"
            f"（已声明能力持续扩充——实时条目数以注册表为准，2026-08-15 时点 {capability_count} 条）"
        )
    return "\n".join(lines) + "\n"


def _build_roor_text(entry_counts: dict[str, int] | None = None) -> str:
    """构造 tmp ROOR 片段：#ARCH-BREG-001 区段 18 条 + 区外 COMP 条目 + ATH 条目。"""
    counts = dict(_ROW_COUNTS if entry_counts is None else entry_counts)
    lines = [
        "registries:",
        "      # ── 业务资产注册表（#ARCH-BREG-001，2026-08-12 补登记）──",
    ]
    for key, reg_id, filename in _ROW_MAP:
        if key == "alert_threshold":
            continue  # ATH 在 BREG 区段外（#ARCH-MON-001 标签）
        lines.extend(
            [
                f"      - registry_id: {reg_id}",
                "        name: 测试注册表",
                f"        physical_path: {_CATALOGS_REL}/{filename}",
                "        format: yaml",
                f"        entry_count: {counts[key]}",
                "        status: active",
                f"        description: 测试夹具 {counts[key]} 条。#ARCH-BREG-001 P0",
            ]
        )
    # 区段结束标志：首个无 #ARCH-BREG-001 标签的条目（#ARCH-COMP-001）
    lines.extend(
        [
            "      - registry_id: REG-FEATURE-ADJ-001",
            "        entry_count: 19",
            "        description: 功能二元裁定。#ARCH-COMP-001（2026-08-15）",
            "      - registry_id: REG-ATH-001",
            "        entry_count: " + str(counts["alert_threshold"]),
            "        description: 告警阈值。#ARCH-MON-001（2026-08-15）",
            "ai_usage:",
            "  discover_all_registries: []",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_capability_text(count: int = 359) -> str:
    """构造 tmp capability 注册表片段（count 条 `- capability_id:` 行）。"""
    lines = ["capabilities:"]
    for i in range(count):
        lines.append(f"- capability_id: cap_{i:04d}")
    return "\n".join(lines) + "\n"


def _make_tmp_spec(
    tmp_path: Path,
    agents_text: str,
    roor_text: str,
    capability_text: str | None,
):
    """把 tmp 片段写到工厂期望的相对路径，返回 make_*(tmp_path) 的 spec。"""
    (tmp_path / "docs").mkdir()
    (tmp_path / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (tmp_path / "docs" / "registry_of_registries.yaml").write_text(roor_text, encoding="utf-8")
    if capability_text is not None:
        cap_path = tmp_path / Path(_macdr._CAPABILITY_REL)
        cap_path.parent.mkdir(parents=True, exist_ok=True)
        cap_path.write_text(capability_text, encoding="utf-8")
    return make_agents_cheatsheet_drift_reconciler(tmp_path)


# ============================================================================
# TestTrigger
# ============================================================================


class TestTrigger:
    """触发条件判断——committed_files 含 AGENTS.md 或任一真源文件才触发。"""

    def test_agents_md_triggers(self):
        """AGENTS.md 变更 → 触发。"""
        assert _should_trigger(["AGENTS.md"]) is True

    def test_roor_triggers(self):
        """ROOR 变更 → 触发。"""
        assert _should_trigger(["docs/registry_of_registries.yaml"]) is True

    def test_capability_registry_triggers(self):
        """capability 注册表变更 → 触发。"""
        assert _should_trigger([f"{_CATALOGS_REL}/capability_canonical_file_registry.yaml"]) is True

    def test_business_registry_triggers(self):
        """业务注册表 yaml 变更 → 触发（含无 _registry 后缀的 field_dictionary.yaml）。"""
        assert _should_trigger([f"{_CATALOGS_REL}/factor_registry.yaml"]) is True
        assert _should_trigger([f"{_CATALOGS_REL}/field_dictionary.yaml"]) is True

    def test_alert_threshold_registry_triggers(self):
        """alert_threshold_registry.yaml 变更 → 触发。"""
        assert _should_trigger([f"{_CATALOGS_REL}/alert_threshold_registry.yaml"]) is True

    def test_absolute_path_triggers(self):
        """绝对路径（项目根下）→ 归一化后触发。"""
        assert _should_trigger([str(_PROJECT_ROOT / "AGENTS.md")]) is True

    def test_unrelated_file_does_not_trigger(self):
        """无关文件变更 → 不触发（防风暴）。"""
        assert _should_trigger(["src/zephyr/some_other.py", "docs/random.md"]) is False

    def test_empty_files_does_not_trigger(self):
        """空文件列表 → 不触发。"""
        assert _should_trigger([]) is False


# ============================================================================
# TestParseAgentsCheatsheet
# ============================================================================


class TestParseAgentsCheatsheet:
    """AGENTS.md 速查区解析——正则锚定 + fail-visible。"""

    def test_full_snippet_parses_all_anchors(self):
        """完整片段：总数+18 行明细+告警阈值+能力计数全部解析出。"""
        parsed = _parse_agents_cheatsheet(_build_agents_text())
        assert parsed["parse_failures"] == []
        assert parsed["table_total"] == (4, 18)
        assert len(parsed["rows"]) == 19  # 18 业务明细 + 1 告警阈值
        assert parsed["rows"]["universe"][1] == 6
        assert parsed["rows"]["alert_threshold"][1] == 35
        assert parsed["capability"][1] == 347

    def test_missing_capability_anchor_fail_visible(self):
        """能力计数锚点缺失 → parse_failures 非空（fail-visible 不静默）。"""
        parsed = _parse_agents_cheatsheet(_build_agents_text(include_capability_anchor=False))
        assert parsed["capability"] is None
        assert any("能力计数行" in f for f in parsed["parse_failures"])

    def test_missing_section_header_fail_visible(self):
        """业务资产速查区标题缺失 → parse_failures 非空。"""
        parsed = _parse_agents_cheatsheet("# 无关内容\n无锚点\n")
        assert parsed["table_total"] is None
        assert len(parsed["parse_failures"]) >= 2  # 标题 + 各明细行

    def test_row_count_units_compatible(self):
        """明细行单位差异兼容（条/席位/事件类型 均为'（N 单位'形态）。"""
        text = _build_agents_text()
        # 把 seat 行单位换成"席位"、event_calendar 换成"事件类型"（对齐真实 AGENTS.md）
        text = text.replace("（16 条，测试夹具）", "（16 席位，测试夹具）", 1)
        text = text.replace("（14 条，测试夹具）", "（14 事件类型全量 PIT 规则，测试夹具）", 1)
        parsed = _parse_agents_cheatsheet(text)
        assert parsed["parse_failures"] == []
        assert parsed["rows"]["seat"][1] == 16
        assert parsed["rows"]["event_calendar"][1] == 14


# ============================================================================
# TestLoadRoorTruth
# ============================================================================


class TestLoadRoorTruth:
    """ROOR 真值解析——BREG 区段口径（标签圈定，抗行号漂移）。"""

    def test_breg_zone_counts_18_excludes_comp_tagged(self):
        """区段计数=18：#ARCH-COMP-001 标签条目（FEATURE-ADJ）不入区。"""
        truth = _load_roor_truth(_build_roor_text())
        assert truth["parse_failures"] == []
        assert truth["breg_total"] == 18

    def test_entry_counts_extracted(self):
        """各条目 entry_count 提取（含区外 ATH）。"""
        truth = _load_roor_truth(_build_roor_text())
        assert truth["entry_counts"]["REG-UNI-001"] == 6
        assert truth["entry_counts"]["REG-PFM-001"] == 11
        assert truth["entry_counts"]["REG-ATH-001"] == 35

    def test_missing_section_fail_visible(self):
        """区段标题缺失 → parse_failures 非空。"""
        truth = _load_roor_truth("registries:\n      - registry_id: REG-X-001\n        entry_count: 1\n")
        assert truth["breg_total"] is None
        assert any("区段标题" in f for f in truth["parse_failures"])

    def test_missing_entry_count_fail_visible(self):
        """映射内条目缺 entry_count → parse_failures 非空。"""
        roor_text = _build_roor_text().replace("        entry_count: 140\n", "", 1)
        truth = _load_roor_truth(roor_text)
        assert any("REG-FCT-001" in f for f in truth["parse_failures"])


# ============================================================================
# TestReconcile
# ============================================================================


class TestReconcile:
    """完整校验流程——spec.reconcile 对 tmp 文件集。"""

    def test_clean_when_consistent(self, tmp_path):
        """数字全部一致 → clean。"""
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(capability_count=359),
            _build_roor_text(),
            _build_capability_text(359),
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "clean"
        assert "零漂移" in result.detail

    def test_warn_when_capability_count_drifts(self, tmp_path):
        """能力计数漂移 → warn 且 message 含行号/两值/真源路径。"""
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(capability_count=347),
            _build_roor_text(),
            _build_capability_text(359),
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "warn"
        assert "AGENTS.md L" in result.detail
        assert "347" in result.detail
        assert "359" in result.detail
        assert "capability_canonical_file_registry.yaml" in result.detail

    def test_warn_when_row_count_drifts(self, tmp_path):
        """明细行漂移（factor 140 vs 真值 111）→ warn 含两值与 registry_id。"""
        row_counts = dict(_ROW_COUNTS)
        row_counts["factor"] = 111
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(row_counts=row_counts),
            _build_roor_text(),
            _build_capability_text(347),
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "warn"
        assert "写 111" in result.detail
        assert "实测 140" in result.detail
        assert "REG-FCT-001" in result.detail

    def test_warn_when_table_total_drifts(self, tmp_path):
        """表体系总数漂移 → warn。"""
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(table_total=17),
            _build_roor_text(),
            _build_capability_text(347),
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "warn"
        assert "17 表体系" in result.detail
        assert "实测 18" in result.detail

    def test_warn_fail_visible_when_format_changed(self, tmp_path):
        """AGENTS.md 格式变化（能力计数锚点失配）→ warn fail-visible，不静默。"""
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(include_capability_anchor=False),
            _build_roor_text(),
            _build_capability_text(359),
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "warn"
        assert "速查区格式已变" in result.detail
        assert "检测器需跟进" in result.detail

    def test_warn_when_truth_file_unreadable(self, tmp_path):
        """真源文件缺失（capability 注册表未建）→ warn 不阻断。"""
        spec = _make_tmp_spec(
            tmp_path,
            _build_agents_text(),
            _build_roor_text(),
            None,
        )
        result = spec.reconcile(["AGENTS.md"], "test-session")
        assert result.action == "warn"
        assert "读取失败" in result.detail


# ============================================================================
# TestFactory
# ============================================================================


class TestFactory:
    """工厂函数——make_agents_cheatsheet_drift_reconciler。"""

    def test_factory_gate_id(self):
        """gate_id=GATE-AGENTS-CHEATSHEET-SYNC。"""
        spec = make_agents_cheatsheet_drift_reconciler()
        assert spec.gate_id == "GATE-AGENTS-CHEATSHEET-SYNC"

    def test_factory_priority(self):
        """priority=250（晚于 algo_flow_translation 240）。"""
        spec = make_agents_cheatsheet_drift_reconciler()
        assert spec.priority == 250

    def test_factory_file_ops_read_only(self):
        """file_ops={'read'}——warn-only MVP 只读不写（AGENTS.md 属 PROTECTED-PATHS）。"""
        spec = make_agents_cheatsheet_drift_reconciler()
        assert spec.file_ops == frozenset({"read"})

    def test_factory_trigger_and_reconcile_callable(self):
        """trigger/reconcile 均为可调用对象。"""
        spec = make_agents_cheatsheet_drift_reconciler()
        assert callable(spec.trigger)
        assert callable(spec.reconcile)
        assert spec.trigger(["AGENTS.md"]) is True
        assert spec.trigger(["src/zephyr/unrelated.py"]) is False

    def test_factory_with_custom_project_root(self, tmp_path):
        """工厂接受自定义 project_root 并重钉派生路径。"""
        (tmp_path / "docs").mkdir()
        spec = make_agents_cheatsheet_drift_reconciler(tmp_path)
        assert spec.gate_id == "GATE-AGENTS-CHEATSHEET-SYNC"
        assert _macdr._AGENTS_FILE == tmp_path / "AGENTS.md"
