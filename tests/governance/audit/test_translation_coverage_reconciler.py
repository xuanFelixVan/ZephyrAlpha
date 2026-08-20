# [BLUEPRINT] MOD-TEST-282 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-TEST-282 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_TRANSLATION_COVERAGE_RECONCILER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.audit.test_translation_coverage_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_translation_coverage_reconciler.py — 翻译覆盖率存量对账 reconciler 单测

权威依据：src/zephyr/governance/audit/translation_coverage_reconciler.py

测试组：
- TestReconcilerSpec: gate_id / priority
- TestTrigger: src/scripts/docs 文件触发判断
- TestReconcile: reconcile 主逻辑（monkeypatch DB + loader）
  - 无漂移 → action=clean
  - 有漂移 → action=warn
  - DB 不可达 → action=warn（fail-open）
  - loader 不可达 → action=warn（fail-open）
  - 漂移报告落盘 → drift_report.json 生成

测试隔离：monkeypatch _query_depgraph_nodes / _load_translation_loader / _DRIFT_REPORT_PATH。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.governance.audit.translation_coverage_reconciler import (  # noqa: E402
    _is_in_scope,
    make_translation_coverage_reconciler,
)

# ---------------------------------------------------------------------------
# TestReconcilerSpec
# ---------------------------------------------------------------------------


class TestReconcilerSpec:
    """gate_id / priority / isinstance(ReconcilerSpec)。"""

    def test_gate_id(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.gate_id == "TRANSLATION-COVERAGE"

    def test_priority(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.priority == 951

    def test_is_reconciler_spec(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert isinstance(spec, ReconcilerSpec)


# ---------------------------------------------------------------------------
# TestIsInScope
# ---------------------------------------------------------------------------


class TestIsInScope:
    """_is_in_scope 范围判断（与 translation_coverage_gate._is_in_scope 同范围铁律）。

    治本 2026-08-02 #ARCH-TRANSLATION-SCOPE-NARROW：reconciler 原漏调 is_test_exempt，
    导致 scripts/tests/* 误报为漂移。本组锁定豁免规则，与 gate 测试同步。
    """

    def test_src_zephyr_in_scope(self) -> None:
        assert _is_in_scope("src/zephyr/governance/audit/foo.py") is True

    def test_scripts_governance_in_scope(self) -> None:
        assert _is_in_scope("scripts/governance/foo.py") is True

    def test_scripts_tests_exempt(self) -> None:
        """scripts/tests/ 下 smoke 测试脚本豁免（治本：原漏调 is_test_exempt 致误报）。"""
        assert _is_in_scope("scripts/tests/smoke_test_ede_e2e.py") is False

    def test_demos_dir_exempt(self) -> None:
        assert _is_in_scope("scripts/demos/demo_e2e_pipeline.py") is False

    def test_test_filename_exempt(self) -> None:
        """test_*.py 文件名豁免（任意层级）。"""
        assert _is_in_scope("scripts/backup/test_get_redis_conn.py") is False
        assert _is_in_scope("scripts/construction/test_deepseek_api.py") is False

    def test_init_exempt(self) -> None:
        assert _is_in_scope("src/zephyr/governance/audit/__init__.py") is False

    def test_archive_exempt(self) -> None:
        assert _is_in_scope("src/zephyr/_archive/old.py") is False

    def test_non_py_exempt(self) -> None:
        """非 .py 文件豁免（depgraph 也登记 .ps1/.sh/.yaml，但翻译注册表面向 Python）。"""
        assert _is_in_scope("src/zephyr/governance/audit/config.yaml") is False
        assert _is_in_scope("scripts/governance/deploy.ps1") is False

    def test_docs_out_of_scope(self) -> None:
        assert _is_in_scope("docs/foo.md") is False

    def test_real_capability_scripts_in_scope(self) -> None:
        """真能力脚本（有 blueprint，无 test_ 前缀）仍需大白话简介。"""
        assert _is_in_scope("scripts/ide_health_service.py") is True
        assert _is_in_scope("scripts/record_session_start_commit.py") is True
        assert _is_in_scope("scripts/backup/ch_vm_ssh.py") is True


# ---------------------------------------------------------------------------
# TestTrigger
# ---------------------------------------------------------------------------


class TestTrigger:
    """trigger 文件触发判断。"""

    def test_src_py_triggers(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.trigger(["src/zephyr/foo.py"]) is True

    def test_scripts_py_triggers(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.trigger(["scripts/governance/bar.py"]) is True

    def test_docs_not_trigger(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.trigger(["docs/baz.md"]) is False

    def test_non_py_not_trigger(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.trigger(["src/zephyr/foo.yaml"]) is False

    def test_empty_not_trigger(self) -> None:
        spec = make_translation_coverage_reconciler(MagicMock())
        assert spec.trigger([]) is False


# ---------------------------------------------------------------------------
# TestReconcile
# ---------------------------------------------------------------------------


class TestReconcile:
    """reconcile 主逻辑（monkeypatch DB + loader）。"""

    def test_no_drift_returns_clean(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """无漂移 → action=clean。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        monkeypatch.setattr(
            rec_mod,
            "_query_depgraph_nodes",
            lambda: [{"path": "src/zephyr/foo.py", "file_path": "src/zephyr/foo.py"}],
        )
        monkeypatch.setattr(
            rec_mod,
            "_load_translation_loader",
            lambda: {
                "get_module_translation": lambda p: {
                    "plain_zh": "这是一个合格的大白话简介用于测试",
                    "name_zh": "测试模块",
                },
                "is_generic_plain_zh": lambda s: False,
                "is_generic_plain_suffix": lambda s, n: False,
            },
        )
        # 重定向报告路径到 tmp_path
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", tmp_path / "drift_report.json")

        spec = make_translation_coverage_reconciler(MagicMock())
        result = spec.reconcile(["src/zephyr/foo.py"], "sess-001")
        assert isinstance(result, ReconcileResult)
        assert result.action == "clean"
        assert result.gate_id == "TRANSLATION-COVERAGE"

    def test_drift_returns_warn(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """有漂移 → action=warn。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        monkeypatch.setattr(
            rec_mod,
            "_query_depgraph_nodes",
            lambda: [{"path": "src/zephyr/missing.py", "file_path": "src/zephyr/missing.py"}],
        )
        monkeypatch.setattr(
            rec_mod,
            "_load_translation_loader",
            lambda: {
                "get_module_translation": lambda p: None,  # 无翻译条目
                "is_generic_plain_zh": lambda s: False,
                "is_generic_plain_suffix": lambda s, n: False,
            },
        )
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", tmp_path / "drift_report.json")

        spec = make_translation_coverage_reconciler(MagicMock())
        result = spec.reconcile(["src/zephyr/missing.py"], "sess-001")
        assert result.action == "warn"
        assert "drift" in result.detail.lower()
        assert result.gate_id == "TRANSLATION-COVERAGE"

    def test_drift_report_written(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """漂移报告落盘 → drift_report.json 生成。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        report_path = tmp_path / "drift_report.json"
        monkeypatch.setattr(
            rec_mod,
            "_query_depgraph_nodes",
            lambda: [{"path": "src/zephyr/missing.py", "file_path": "src/zephyr/missing.py"}],
        )
        monkeypatch.setattr(
            rec_mod,
            "_load_translation_loader",
            lambda: {
                "get_module_translation": lambda p: None,
                "is_generic_plain_zh": lambda s: False,
                "is_generic_plain_suffix": lambda s, n: False,
            },
        )
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", report_path)

        spec = make_translation_coverage_reconciler(MagicMock())
        spec.reconcile(["src/zephyr/missing.py"], "sess-001")
        assert report_path.exists()
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert data["gate_id"] == "TRANSLATION-COVERAGE"
        assert "src/zephyr/missing.py" in data["missing_plain"]
        assert data["summary"]["total_drift"] == 1

    def test_db_unreachable_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """DB 不可达 → action=warn（fail-open）。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        monkeypatch.setattr(rec_mod, "_query_depgraph_nodes", lambda: None)
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", tmp_path / "drift_report.json")

        spec = make_translation_coverage_reconciler(MagicMock())
        result = spec.reconcile(["src/zephyr/foo.py"], "sess-001")
        assert result.action == "warn"
        assert "depgraph" in result.detail.lower() or "不可达" in result.detail

    def test_loader_unreachable_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """loader 不可达 → action=warn（fail-open）。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        monkeypatch.setattr(
            rec_mod,
            "_query_depgraph_nodes",
            lambda: [{"path": "src/zephyr/foo.py", "file_path": "src/zephyr/foo.py"}],
        )
        monkeypatch.setattr(rec_mod, "_load_translation_loader", lambda: None)
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", tmp_path / "drift_report.json")

        spec = make_translation_coverage_reconciler(MagicMock())
        result = spec.reconcile(["src/zephyr/foo.py"], "sess-001")
        assert result.action == "warn"
        assert "loader" in result.detail.lower() or "不可达" in result.detail

    def test_out_of_scope_skipped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """file_path 不在范围（docs/）→ 跳过，无漂移。"""
        import zephyr.governance.audit.translation_coverage_reconciler as rec_mod

        monkeypatch.setattr(
            rec_mod,
            "_query_depgraph_nodes",
            lambda: [{"path": "docs/foo.md", "file_path": "docs/foo.md"}],
        )
        monkeypatch.setattr(
            rec_mod,
            "_load_translation_loader",
            lambda: {
                "get_module_translation": lambda p: None,
                "is_generic_plain_zh": lambda s: False,
                "is_generic_plain_suffix": lambda s, n: False,
            },
        )
        monkeypatch.setattr(rec_mod, "_DRIFT_REPORT_PATH", tmp_path / "drift_report.json")

        spec = make_translation_coverage_reconciler(MagicMock())
        result = spec.reconcile(["docs/foo.md"], "sess-001")
        # docs/ 不在范围 → 跳过 → 无漂移 → clean
        assert result.action == "clean"
