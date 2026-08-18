# [A_test] module_id: MOD-TEST-276 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-metric_count_drift | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] tests.scripts.governance.d8_doc_sync.test_metric_count_drift_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_metric_count_drift_reconciler.py — dashboard 指标数描述派生校验 reconciler 单测

权威依据：scripts/governance/d8_doc_sync/metric_count_drift_reconciler.py
对标先例：tests/scripts/governance/d8_doc_sync/test_readme_version_sync_reconciler.py（未创建，参考模式）

测试组：
- TestTrigger: 触发条件判断
- TestScanFileForCountDesc: 指标数描述扫描
- TestReconcile: 完整校验流程
- TestFactory: 工厂函数

测试隔离：mock _read_text / _get_metric_count 隔离真实文件系统；
不依赖真实仓库状态。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DOC_SYNC_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d8_doc_sync"
if str(_DOC_SYNC_DIR) not in sys.path:
    sys.path.insert(0, str(_DOC_SYNC_DIR))

import metric_count_drift_reconciler as _mcdr  # noqa: E402
from metric_count_drift_reconciler import (  # noqa: E402
    _COUNT_DESC_RE,
    _scan_file_for_count_desc,
    _should_trigger,
    make_metric_count_drift_reconciler,
)


@pytest.fixture(autouse=True)
def _repin_project_root():
    """重钉模块全局 _project_root：工厂 make_*(project_root) 会 global 改写模块级
    _project_root 及派生常量，同会话早前 GitCommitGateway(tmp_path) 注册（gateway
    L879-880 eager 注册默认 reconciler）已把全局钉到 tmp 根——本文件每个测试前
    重钉真实根，防跨测试全局污染（同族先例 test_algo_flow_translation_reconciler
    TestFactoryPathReassign 2026-08-14 实证）。"""
    _mcdr.make_metric_count_drift_reconciler(_PROJECT_ROOT)
    yield
    _mcdr.make_metric_count_drift_reconciler(_PROJECT_ROOT)


# ============================================================================
# TestTrigger
# ============================================================================


class TestTrigger:
    """触发条件判断——committed_files 含 dashboard.py 或派生文件才触发。"""

    def test_dashboard_py_triggers(self):
        """dashboard.py 变更 → 触发。"""
        files = ["scripts/governance/architecture_health_dashboard.py"]
        assert _should_trigger(files) is True

    def test_reconciliation_registry_py_triggers(self):
        """reconciliation_registry.py 变更 → 触发。"""
        files = ["src/zephyr/governance/audit/reconciliation_registry.py"]
        assert _should_trigger(files) is True

    def test_script_manifest_yaml_triggers(self):
        """script_manifest.yaml 变更 → 触发。"""
        files = ["scripts/governance/script_manifest.yaml"]
        assert _should_trigger(files) is True

    def test_capability_registry_yaml_triggers(self):
        """capability_canonical_file_registry.yaml 变更 → 触发。"""
        files = ["docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"]
        assert _should_trigger(files) is True

    def test_unrelated_file_does_not_trigger(self):
        """无关文件变更 → 不触发。"""
        files = ["src/zephyr/some_other.py", "docs/random.md"]
        assert _should_trigger(files) is False

    def test_empty_files_does_not_trigger(self):
        """空文件列表 → 不触发。"""
        assert _should_trigger([]) is False


# ============================================================================
# TestScanFileForCountDesc
# ============================================================================


class TestScanFileForCountDesc:
    """指标数描述扫描——正则匹配 + 漂移检测。"""

    def test_consistent_description_no_drift(self):
        """描述值与期望一致 → 无漂移。"""
        content = "# 30 项架构健康度指标\n# 30 项指标自动化检测基线\n"
        findings = _scan_file_for_count_desc(content, 30, "dashboard.py")
        assert findings == []

    def test_drift_detected(self):
        """描述值与期望不一致 → 漂移。"""
        content = "# 11 项架构健康度指标\n"
        findings = _scan_file_for_count_desc(content, 30, "dashboard.py")
        assert len(findings) == 1
        assert "11" in findings[0]
        assert "30" in findings[0]

    def test_multiple_drifts_all_reported(self):
        """多处漂移全部报告。"""
        content = "# 11 项架构健康度指标\n# 18 项指标自动化检测基线\n# 19 项架构健康度指标自动化检测基线\n"
        findings = _scan_file_for_count_desc(content, 30, "dashboard.py")
        assert len(findings) == 3

    def test_no_description_no_drift(self):
        """无指标数描述 → 无漂移（可能用不同措辞，不强制）。"""
        content = "# 这是一个仪表盘\n# 检测架构健康度\n# 30 项指标注册表（措辞不匹配，不强制）\n"
        findings = _scan_file_for_count_desc(content, 30, "dashboard.py")
        assert findings == []

    def test_count_desc_regex_matches_variants(self):
        """正则匹配 dashboard 专属 3 种措辞。"""
        # "项架构健康度指标"
        assert _COUNT_DESC_RE.search("30 项架构健康度指标")
        # "项指标自动化检测基线"
        assert _COUNT_DESC_RE.search("30 项指标自动化检测基线")
        # "项架构健康度指标自动化检测基线"（完整版）
        assert _COUNT_DESC_RE.search("30 项架构健康度指标自动化检测基线")

    def test_count_desc_regex_no_false_positive(self):
        """正则不误匹配无关数字或其他模块的"项指标"。"""
        assert not _COUNT_DESC_RE.search("共有 30 个文件")
        assert not _COUNT_DESC_RE.search("priority=300")
        assert not _COUNT_DESC_RE.search("M30 ZEPHYR_ENV")
        # 其他模块的"项指标"不误匹配（如 SLA 模块的"6 项指标从 sla_metrics"）
        assert not _COUNT_DESC_RE.search("6 项指标从 sla_metrics.jsonl 计算")
        # dashboard 专属措辞的"项指标"单独不匹配（需"项指标自动化检测基线"完整）
        assert not _COUNT_DESC_RE.search("30 项指标注册表")


# ============================================================================
# TestReconcile
# ============================================================================


class TestReconcile:
    """完整校验流程——_reconcile 函数。"""

    def test_clean_when_all_consistent(self):
        """所有文件描述一致 → clean。"""
        spec = make_metric_count_drift_reconciler()
        with patch("metric_count_drift_reconciler._get_metric_count", return_value=30):
            with patch("metric_count_drift_reconciler._read_text", return_value="# 30 项架构健康度指标\n"):
                result = spec.reconcile(
                    ["scripts/governance/architecture_health_dashboard.py"],
                    "test-session",
                )
        assert result.action == "clean"
        assert "30" in result.detail

    def test_warn_when_drift_detected(self):
        """检测到漂移 → warn。"""
        spec = make_metric_count_drift_reconciler()

        # 模拟 4 个文件都返回漂移描述
        def mock_read_text(path):
            return "# 11 项架构健康度指标\n"

        with patch("metric_count_drift_reconciler._get_metric_count", return_value=30):
            with patch("metric_count_drift_reconciler._read_text", side_effect=mock_read_text):
                result = spec.reconcile(
                    ["scripts/governance/architecture_health_dashboard.py"],
                    "test-session",
                )
        assert result.action == "warn"
        assert "漂移" in result.detail

    def test_warn_when_metric_import_fails(self):
        """METRICS 导入失败 → warn（不阻断）。"""
        spec = make_metric_count_drift_reconciler()
        with patch("metric_count_drift_reconciler._get_metric_count", return_value=None):
            result = spec.reconcile(
                ["scripts/governance/architecture_health_dashboard.py"],
                "test-session",
            )
        assert result.action == "warn"
        assert "METRICS 导入失败" in result.detail

    def test_warn_when_file_read_fails(self):
        """文件读取失败 → warn（不阻断）。"""
        spec = make_metric_count_drift_reconciler()
        with patch("metric_count_drift_reconciler._get_metric_count", return_value=30):
            with patch("metric_count_drift_reconciler._read_text", return_value=None):
                result = spec.reconcile(
                    ["scripts/governance/architecture_health_dashboard.py"],
                    "test-session",
                )
        # 4 文件都 None → 无 findings → clean（文件读取失败不视为漂移）
        # 但 _read_text 返回 None 时 _scan_file_for_count_desc 不被调用
        assert result.action == "clean"

    def test_partial_drift_only_reports_inconsistent(self):
        """部分文件漂移，只报告不一致的文件。"""
        spec = make_metric_count_drift_reconciler()

        # dashboard.py 一致，reconciliation_registry.py 漂移
        def mock_read_text(path):
            path_str = str(path)
            if "architecture_health_dashboard" in path_str:
                return "# 30 项架构健康度指标\n"
            return "# 11 项架构健康度指标\n"

        with patch("metric_count_drift_reconciler._get_metric_count", return_value=30):
            with patch("metric_count_drift_reconciler._read_text", side_effect=mock_read_text):
                result = spec.reconcile(
                    ["scripts/governance/architecture_health_dashboard.py"],
                    "test-session",
                )
        assert result.action == "warn"
        # dashboard.py 一致不计入，其他 3 文件漂移
        assert "3 处" in result.detail


# ============================================================================
# TestFactory
# ============================================================================


class TestFactory:
    """工厂函数——make_metric_count_drift_reconciler。"""

    def test_factory_returns_spec_with_correct_gate_id(self):
        """工厂返回 ReconcilerSpec，gate_id 正确。"""
        spec = make_metric_count_drift_reconciler()
        assert spec.gate_id == "GATE-METRIC-COUNT-DRIFT"

    def test_factory_returns_spec_with_correct_priority(self):
        """priority=220（晚于 readme_version_sync 210）。"""
        spec = make_metric_count_drift_reconciler()
        assert spec.priority == 220

    def test_factory_trigger_callable(self):
        """trigger 是可调用对象。"""
        spec = make_metric_count_drift_reconciler()
        assert callable(spec.trigger)
        assert spec.trigger(["scripts/governance/architecture_health_dashboard.py"]) is True

    def test_factory_reconcile_callable(self):
        """reconcile 是可调用对象。"""
        spec = make_metric_count_drift_reconciler()
        assert callable(spec.reconcile)

    def test_factory_with_custom_project_root(self, tmp_path):
        """工厂接受自定义 project_root。"""
        # 创建必要的子目录结构
        (tmp_path / "scripts" / "governance").mkdir(parents=True)
        (tmp_path / "src" / "zephyr" / "governance" / "audit").mkdir(parents=True)
        (tmp_path / "docs" / "01_policies_and_standards" / "_registry" / "catalogs").mkdir(parents=True)
        spec = make_metric_count_drift_reconciler(tmp_path)
        assert spec.gate_id == "GATE-METRIC-COUNT-DRIFT"
