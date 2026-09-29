# [BLUEPRINT] MOD-RPT-038 | docs/03_modules/_domain_reporting/review_trigger/blueprint.md | §
# [MODULE] tests.reporting.test_review_trigger
# [DOMAIN] D_REPORTING
# [TTL] permanent
"""F115 R1 触发链薄刀测试——review_trigger 事件触发入口。

覆盖：
- trigger_daily_review 真实全链（DailyAuditor+RiskReportEngine+Publisher+Sink→tmp_path）
- 上游缺口最小输入语义（空持仓/零值契约快照，audit PASS、归档落盘）
- 注入编排器面（publish=False 不归档；自定义 portfolio_id 双契约一致）
- 非法 trading_date → ValueError；CLI main() 0/1 退出码
- morning_digest 边界回归：不触 data/reports/morning_digest.md（在途袋领地零交集）

测试隔离：tmp_path 落点；worktree 解析走 ZEPHYR_ALPHA_ROOT 环境变量
（usercustomize 官方开关，禁 sys.modules 级清洗——模块级清洗毒化同进程兄弟测试）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.reporting.report_archive_sink import DEFAULT_ARCHIVE_FILENAME, load_report_records  # noqa: E402
from zephyr.reporting.review_orchestrator import ReviewOrchestrator  # noqa: E402
from zephyr.reporting.review_trigger import (  # noqa: E402
    build_default_orchestrator,
    main,
    trigger_daily_review,
)
from zephyr.risk.core.daily_auditor import AuditStatus  # noqa: E402


class TestTriggerDailyReview:
    def test_real_chain_produces_and_persists(self, tmp_path: Path) -> None:
        archive = tmp_path / DEFAULT_ARCHIVE_FILENAME
        orch = build_default_orchestrator(archive_path=archive)
        result = trigger_daily_review("2026-09-28", orchestrator=orch, portfolio_id="P-T1")
        assert result.audit_report.overall_status is AuditStatus.PASS  # 空输入五件套全绿
        assert result.human_attention == ()
        assert result.archived_report is not None
        assert result.archived_report.report_type == "daily_risk_review"
        records = load_report_records(archive)
        assert len(records) == 1 and records[0]["report_id"].startswith("DAILY-REVIEW-P-T1")

    def test_no_publish_skips_archive(self, tmp_path: Path) -> None:
        archive = tmp_path / DEFAULT_ARCHIVE_FILENAME
        orch = build_default_orchestrator(archive_path=archive)
        result = trigger_daily_review("2026-09-28", orchestrator=orch, publish=False)
        assert result.archived_report is None
        assert not archive.exists() and orch._publisher.archive_count == 0

    def test_default_orchestrator_wiring(self) -> None:
        orch = build_default_orchestrator()
        assert isinstance(orch, ReviewOrchestrator)

    def test_bad_trading_date_raises(self, tmp_path: Path) -> None:
        orch = build_default_orchestrator(archive_path=tmp_path / "a.jsonl")
        with pytest.raises(ValueError):
            trigger_daily_review("2026/09/28", orchestrator=orch)

    def test_morning_digest_boundary_untouched(self, tmp_path: Path) -> None:
        """晨报面零交集：触发链只写归档 JSONL，不产 morning_digest.md。"""
        archive = tmp_path / DEFAULT_ARCHIVE_FILENAME
        trigger_daily_review("2026-09-28", orchestrator=build_default_orchestrator(archive_path=archive))
        assert not (tmp_path / "morning_digest.md").exists()
        assert archive.exists()


class TestCliMain:
    def test_cli_ok_exit_zero(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        archive = tmp_path / "cli.jsonl"
        code = main(["--trading-date", "2026-09-27", "--archive-path", str(archive), "--portfolio-id", "P-CLI"])
        assert code == 0
        out = capsys.readouterr().out
        assert "[review_trigger] OK" in out and "audit=PASS" in out
        assert len(load_report_records(archive)) == 1

    def test_cli_bad_date_exit_one(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--trading-date", "not-a-date"]) == 1
        assert "FAIL" in capsys.readouterr().out

    def test_cli_no_publish(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["--trading-date", "2026-09-26", "--no-publish"])
        assert code == 0
        assert "(未归档)" in capsys.readouterr().out


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-q"])
