# [BLUEPRINT] MOD-EXE-BIZ-001 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.3
# [MODULE] tests.autonomy.test_business_g04_ops_check
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] pytest ; zephyr.autonomy_core.agents.business_agent_entry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 落盘断言只认 tmp runtime_dir；真源注册表用例只读不污染；注册表夹具经 catalogs 缝注入
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.3 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（测试件）
# [TESTS] 自测
# [A_test] module_id=MOD-EXE-BIZ-001 | layer=test | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""S1.3 业务 Agent U7 深化测试（14号文 §4-S1.3 验收口径）.

被测对象：business_agent_entry 新工单类型 g04_strategy_ops_check——对 20号文首批
三策略（打板 daban/多因子 multifactor/事件驱动 event_driven）做因子-策略-组件
状态核对：注册表侧（strategy_registry 条目状态 + factor_registry 关联因子
evidence 状态）+ 组件在位性（20号文 §2.7 设施盘点清单只读存在性检查）+ 缺口清单
（仅建议语义，ADVICE_ONLY_DISCLAIMER 沿用）。
"""

from __future__ import annotations

import json
from pathlib import Path

from zephyr.autonomy_core.agents import business_agent_entry

REPO_ROOT = Path(__file__).resolve().parents[2]

_FIXTURE_STRATEGIES = [
    {
        "strategy_id": "STR-DABAN-901",
        "strategy_class": "daban",
        "status": "candidate",
        "lifecycle_status": "candidate",
        "algorithm_status": "pending_backtest",
        "evidence": "",
        "code_path": "",
    },
    {
        "strategy_id": "STR-DABAN-902",
        "strategy_class": "daban",
        "status": "active",
        "lifecycle_status": "live",
        "algorithm_status": "quantized",
        "evidence": "exp-123",
        "code_path": "src/zephyr/pf_core/strategies/daban_sleeve_strategy.py",
    },
    {
        "strategy_id": "STR-MULTIFACTOR-901",
        "strategy_class": "multifactor",
        "status": "candidate",
        "lifecycle_status": "candidate",
        "algorithm_status": "pending_backtest",
        "evidence": "",
        "code_path": "",
    },
]
_FIXTURE_FACTORS = [
    {
        "factor_id": "FCT-A",
        "belongs_to_strategies": ["STR-DABAN-901"],
        "evidence": "",
        "algorithm_status": "pending_backtest",
    },
    {
        "factor_id": "FCT-B",
        "belongs_to_strategies": ["STR-DABAN-902"],
        "evidence": "exp-9",
        "algorithm_status": "quantized",
    },
    {"factor_id": "FCT-C", "belongs_to_strategies": [], "evidence": "exp-1", "algorithm_status": "quantized"},
]


def _latest_run_dir(tmp_path: Path) -> Path:
    return next(p for p in (tmp_path / "agent_runs" / "business").iterdir() if p.is_dir())


class TestG04RealRegistry:
    """真源注册表+真仓库文件：三策略核对端到端."""

    def test_three_strategies_registry_and_components(self, tmp_path):
        report = business_agent_entry.run_g04_strategy_ops_check(
            {"ticket_id": "g04-real-001"},
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        assert report["kind"] == "g04_strategy_ops_check"
        assert report["advice_only"] is True
        assert "仅建议" in report["disclaimer"]
        assert report["status"] == "completed"
        assert set(report["strategies"]) == {"daban", "multifactor", "event_driven"}

        daban = report["strategies"]["daban"]
        assert daban["registry"]["status"] == "ok"
        assert daban["registry"]["entry_count"] == 22  # 真源：daban 类 22 条
        assert "STR-DABAN-001" in daban["registry"]["entry_ids"]
        assert report["strategies"]["multifactor"]["registry"]["entry_count"] == 70

        # 事件驱动真源已登记 STR-EVENT-001（CAND-SIG-012 晋升）
        event = report["strategies"]["event_driven"]
        assert event["registry"]["entry_count"] == 1
        assert event["registry"]["entry_ids"] == ["STR-EVENT-001"]
        assert not any("无该策略类条目" in gap for gap in report["gaps"])

        # 组件在位性：20号文 §2.7 设施盘点 + 2026-08-21 sleeve 落码回填，全部应在位
        for strategy in report["strategies"].values():
            assert strategy["components"]["expected"] > 0
            assert strategy["components"]["missing"] == []

        # 缺口清单为仅建议语义：全部为字符串描述，不落任何执行结论
        assert report["gap_count"] == len(report["gaps"])
        assert all(isinstance(gap, str) for gap in report["gaps"])

        landed = json.loads((_latest_run_dir(tmp_path) / "g04_strategy_ops_check.json").read_text(encoding="utf-8"))
        assert landed["ai_autonomy"] == "human_gated"
        assert landed["triggered_by"] == "human_manual"
        assert landed["kind"] == "g04_strategy_ops_check"
        assert "仅建议" in landed["disclaimer"]


class TestG04FixtureCatalogs:
    """注册表夹具注入：关联因子 evidence 状态 + 组件缺位 + 无 code_path 缺口."""

    def test_fixture_gaps_and_linked_factors(self, tmp_path):
        catalogs = {"strategies": _FIXTURE_STRATEGIES, "factors": _FIXTURE_FACTORS}
        empty_root = tmp_path / "empty_repo"  # 无任何 src 文件 → 组件全缺位
        empty_root.mkdir()
        report = business_agent_entry.run_g04_strategy_ops_check(
            {"ticket_id": "g04-fixture-001"},
            runtime_dir=tmp_path / "rt",
            repo_root=empty_root,
            catalogs=catalogs,
        )
        assert report["status"] == "completed"
        daban = report["strategies"]["daban"]
        assert daban["registry"]["entry_count"] == 2
        assert daban["registry"]["status_counts"] == {"candidate": 1, "active": 1}
        assert daban["registry"]["entries_without_code_path"] == ["STR-DABAN-901"]
        assert daban["registry"]["entries_without_evidence"] == ["STR-DABAN-901"]
        # 关联因子=belongs_to_strategies 指向本策略条目者
        assert daban["linked_factors"]["factor_ids"] == ["FCT-A", "FCT-B"]
        assert daban["linked_factors"]["evidence_missing"] == ["FCT-A"]
        assert daban["linked_factors"]["pending_backtest"] == ["FCT-A"]
        # 组件缺位进缺口
        assert any("组件缺位" in gap for gap in daban["gaps"])
        # 事件驱动夹具无条目 → 缺口；FCT-C 未挂接任何策略不进关联
        assert report["strategies"]["event_driven"]["linked_factors"]["count"] == 0
        assert any("无该策略类条目" in gap for gap in report["strategies"]["event_driven"]["gaps"])
        assert any("无关联因子挂接" in gap for gap in report["strategies"]["event_driven"]["gaps"])
        multifactor = report["strategies"]["multifactor"]
        assert multifactor["registry"]["entry_count"] == 1

    def test_missing_registries_mark_evidence_missing(self, tmp_path):
        empty_root = tmp_path / "empty_repo"
        empty_root.mkdir()
        report = business_agent_entry.run_g04_strategy_ops_check(
            {"ticket_id": "g04-missing-001"},
            runtime_dir=tmp_path / "rt",
            repo_root=empty_root,
        )
        assert report["status"] == "evidence_missing"
        for strategy in report["strategies"].values():
            assert strategy["registry"]["status"] == "evidence_missing"
        assert any("注册表不可读" in gap for gap in report["gaps"])
        run_record = json.loads((_latest_run_dir(tmp_path / "rt") / "run.json").read_text(encoding="utf-8"))
        assert run_record["status"] == "evidence_missing"


class TestG04CliDispatch:
    """CLI kind 分发：g04_strategy_ops_check 走新处理器."""

    def test_cli_dispatches_g04_kind(self, tmp_path, capsys):
        ticket_file = tmp_path / "ticket.json"
        ticket_file.write_text(
            json.dumps({"ticket_id": "g04-cli-001", "kind": "g04_strategy_ops_check"}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert business_agent_entry.main(["--ticket", str(ticket_file), "--runtime-dir", str(tmp_path / "rt")]) == 0
        out = json.loads(capsys.readouterr().out)
        assert out["kind"] == "g04_strategy_ops_check"
        assert out["advice_only"] is True
        assert (_latest_run_dir(tmp_path / "rt") / "g04_strategy_ops_check.json").exists()
