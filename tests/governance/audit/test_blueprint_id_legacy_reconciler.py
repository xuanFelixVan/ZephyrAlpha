# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.audit.test_blueprint_id_legacy_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_blueprint_id_legacy_reconciler.py — GATE-BLUEPRINT-ID-LEGACY reconciler 单测

权威依据：reconciliation_registry.py::make_blueprint_id_legacy_reconciler
（#ARCH-DATAQUALITY-V1.8 Task I）

测试组：
- TestReconcilerSpecFields: gate_id / priority / isinstance(ReconcilerSpec)
- TestTrigger: .py 文件触发 / .md 文件不触发 / validate_module_id_naming.py 触发
- TestReconcile: tmp_path 隔离环境 + stub validate_module_id_naming
  - 无文件 → clean
  - 合法 [BLUEPRINT] 头 → clean
  - 非法 MOD- 前缀 → warn
  - 无 MOD-/SH- 前缀 → warn
  - 空 [BLUEPRINT] 头 → warn
  - D- 废弃前缀 → warn
  - 报告文件落盘验证

测试隔离：tmp_path 构造独立 src/zephyr/ 目录；validate_module_id_naming 以
monkeypatch sys.modules 注入 stub 到 reconciler 实际引用的完整包路径槽位
（scripts.governance.d3_metadata.validate_module_id_naming），不落真实项目文件。

历史教训（2026-09-15 复核班治本）：DM-90974 把 reconciler 的裸模块名 import 改为
完整包路径后，旧 stub 靠 sys.path + 裸名注入被静默绕过，真源校验器判定测试假 id
合法 → warn 用例全变 clean 的静默漂移。现 stub 拒绝理由带 "stub-rejected" 哨兵
且用例断言哨兵可见——stub 再被绕过时用例响亮失败，事故类别闭环。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcilerSpec,
    make_blueprint_id_legacy_reconciler,
)

# stub 拒绝理由统一带哨兵前缀：若 reconciler 绕过 stub 用了真源校验器，
# 用例断言 "stub-rejected" 可见性即失败（静默漂移 → 响亮失败，2026-09-15 事故闭环）
_STUB_REJECT = "stub-rejected"

# 与 stub 约定的合法 id 集（三轨各取一个代表：layer-master / derived / shared）
_STUB_VALID_IDS = frozenset({"MOD-INF-001", "MOD-GATE_ENGINE", "SH-DB-001"})

# reconciler 内部 from-import 的完整包路径（DM-90974 后的真源引用槽位）
_RECONCILER_VALIDATOR_PATH = "scripts.governance.d3_metadata.validate_module_id_naming"


def _make_stub_validator_module() -> types.ModuleType:
    """构造内存版 validate_module_id_naming stub 模块。

    合法集固定三个代表 id；其余一律 (False, "stub-rejected: ...")，
    用例通过哨兵断言 stub 确被消费。
    """
    stub = types.ModuleType("validate_module_id_naming_stub")

    def is_valid_module_id(bp_id):
        if bp_id in _STUB_VALID_IDS:
            return True, ""
        return False, f"{_STUB_REJECT}: {bp_id}"

    stub.is_valid_module_id = is_valid_module_id
    return stub


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway：仅暴露 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


@pytest.fixture
def stub_validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Fixture: stub 注入 reconciler 实际引用的完整包路径槽位，返回 tmp_path 工程根。"""
    monkeypatch.setitem(sys.modules, _RECONCILER_VALIDATOR_PATH, _make_stub_validator_module())
    # 旧裸模块名缓存一并清除（DM-90974 之前的历史残留，防御性）
    monkeypatch.delitem(sys.modules, "validate_module_id_naming", raising=False)
    return tmp_path


def _write_py_file(project_root: Path, rel_path: str, blueprint_header: str | None) -> Path:
    """在 project_root 下写一个 .py 文件，可指定 [BLUEPRINT] 头部行。

    Args:
        rel_path: 相对路径（如 "src/zephyr/foo.py"）
        blueprint_header: [BLUEPRINT] 头部的 module_id 部分；
            None 表示不写 [BLUEPRINT] 行；
            空字符串表示写空头 "# [BLUEPRINT]"。

    Returns:
        文件绝对路径。
    """
    file_path = project_root / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if blueprint_header is not None:
        if blueprint_header == "":
            lines.append("# [BLUEPRINT]")
        else:
            lines.append(f"# [BLUEPRINT] {blueprint_header} | docs/03_modules/foo/blueprint.md | section-0.1")
    lines.append('"""docstring."""')
    lines.append("")
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return file_path


class TestReconcilerSpecFields:
    """ReconcilerSpec 字段校验。"""

    def test_gate_id(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.gate_id == "GATE-BLUEPRINT-ID-LEGACY"

    def test_priority(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.priority == 145

    def test_is_reconciler_spec(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)

    def test_trigger_callable(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert callable(spec.trigger)

    def test_reconcile_callable(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert callable(spec.reconcile)


class TestTrigger:
    """trigger 函数行为。"""

    def test_py_file_triggers(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.trigger(["src/zephyr/foo.py"]) is True

    def test_md_file_does_not_trigger(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.trigger(["docs/03_modules/foo/blueprint.md"]) is False

    def test_validate_module_id_naming_triggers(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.trigger(["scripts/governance/d3_metadata/validate_module_id_naming.py"]) is True

    def test_empty_list_does_not_trigger(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.trigger([]) is False

    def test_mixed_md_files_do_not_trigger(self, tmp_path: Path) -> None:
        gw = _make_gateway(tmp_path)
        spec = make_blueprint_id_legacy_reconciler(gw)
        assert spec.trigger(["README.md", "docs/foo.md"]) is False


class TestReconcile:
    """reconcile 函数行为（tmp_path 隔离环境 + stub validator）。"""

    def test_clean_when_no_files(self, stub_validator: Path) -> None:
        """无 src/zephyr/ 等目录 -> scanned=0, clean。"""
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/foo.py"], "test-session")
        assert result.action == "clean"
        assert "0 violations" in result.detail

    def test_clean_when_valid_header(self, stub_validator: Path) -> None:
        """合法 MOD-INF-001 头 -> clean。"""
        _write_py_file(stub_validator, "src/zephyr/valid.py", "MOD-INF-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/valid.py"], "test-session")
        assert result.action == "clean"
        assert "0 violations" in result.detail

    def test_clean_when_valid_derived_track(self, stub_validator: Path) -> None:
        """合法派生轨 MOD-GATE_ENGINE -> clean。"""
        _write_py_file(stub_validator, "src/zephyr/derived.py", "MOD-GATE_ENGINE")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/derived.py"], "test-session")
        assert result.action == "clean"

    def test_clean_when_valid_shared_track(self, stub_validator: Path) -> None:
        """合法共享轨 SH-DB-001 -> clean。"""
        _write_py_file(stub_validator, "src/zephyr/shared.py", "SH-DB-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/shared.py"], "test-session")
        assert result.action == "clean"

    def test_warn_when_invalid_mod_prefix(self, stub_validator: Path) -> None:
        """非法 MOD-GOV-SCRIPTS（layer-master 轨不匹配） -> warn。"""
        _write_py_file(stub_validator, "src/zephyr/invalid.py", "MOD-GOV-SCRIPTS")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/invalid.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        # 哨兵：证明 stub 确被消费（防 stub 被真源校验器绕过的静默漂移复发）
        assert _STUB_REJECT in result.detail

    def test_warn_when_no_prefix(self, stub_validator: Path) -> None:
        """无 MOD-/SH- 前缀（ARCHITECTURE-DIAGRAM-PLAN） -> warn。"""
        _write_py_file(stub_validator, "src/zephyr/no_prefix.py", "ARCHITECTURE-DIAGRAM-PLAN")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/no_prefix.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert _STUB_REJECT in result.detail

    def test_warn_when_empty_header(self, stub_validator: Path) -> None:
        """空 [BLUEPRINT] 头（无 module_id） -> warn。"""
        _write_py_file(stub_validator, "src/zephyr/empty.py", "")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/empty.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert "empty" in result.detail.lower()

    def test_warn_when_d_prefix_deprecated(self, stub_validator: Path) -> None:
        """D-FOO-001 废弃前缀 -> warn。"""
        _write_py_file(stub_validator, "src/zephyr/deprecated.py", "D-FOO-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/deprecated.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert _STUB_REJECT in result.detail

    def test_warn_when_src_legacy(self, stub_validator: Path) -> None:
        """SRC-XXX 残留 -> warn。"""
        _write_py_file(stub_validator, "src/zephyr/src_legacy.py", "SRC-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/src_legacy.py"], "test-session")
        assert result.action == "warn"
        assert "1 violation" in result.detail
        assert _STUB_REJECT in result.detail

    def test_report_file_written(self, stub_validator: Path) -> None:
        """违规时报告文件落盘到 .runtime/reconcile_reports/。"""
        _write_py_file(stub_validator, "src/zephyr/invalid.py", "MOD-GOV-SCRIPTS")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/invalid.py"], "test-session-report")
        assert result.action == "warn"
        reports_dir = stub_validator / ".runtime" / "reconcile_reports"
        assert reports_dir.is_dir()
        report_files = list(reports_dir.glob("blueprint_id_legacy_*.json"))
        assert len(report_files) == 1
        import json

        report = json.loads(report_files[0].read_text(encoding="utf-8"))
        assert report["gate_id"] == "GATE-BLUEPRINT-ID-LEGACY"
        assert report["session_id"] == "test-session-report"
        assert report["violation_count"] == 1
        assert len(report["violations"]) == 1
        assert report["violations"][0]["module_id"] == "MOD-GOV-SCRIPTS"
        # 哨兵：报告里的拒绝理由必须来自 stub
        assert report["violations"][0]["reason"].startswith(_STUB_REJECT)

    def test_report_file_written_clean(self, stub_validator: Path) -> None:
        """clean 时报告文件也落盘。"""
        _write_py_file(stub_validator, "src/zephyr/valid.py", "MOD-INF-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/valid.py"], "test-session-clean")
        assert result.action == "clean"
        reports_dir = stub_validator / ".runtime" / "reconcile_reports"
        report_files = list(reports_dir.glob("blueprint_id_legacy_*.json"))
        assert len(report_files) == 1
        import json

        report = json.loads(report_files[0].read_text(encoding="utf-8"))
        assert report["violation_count"] == 0

    def test_multiple_violations_counted(self, stub_validator: Path) -> None:
        """多个违规文件都被检测。"""
        _write_py_file(stub_validator, "src/zephyr/a.py", "MOD-GOV-SCRIPTS")
        _write_py_file(stub_validator, "src/zephyr/b.py", "ARCHITECTURE-PLAN")
        _write_py_file(stub_validator, "src/zephyr/c.py", "SRC-001")
        _write_py_file(stub_validator, "src/zephyr/valid.py", "MOD-INF-001")
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/"], "test-multi")
        assert result.action == "warn"
        assert "3 violation" in result.detail
        assert _STUB_REJECT in result.detail

    def test_files_without_blueprint_header_skipped(self, stub_validator: Path) -> None:
        """无 [BLUEPRINT] 头的文件不计入违规。"""
        _write_py_file(stub_validator, "src/zephyr/no_header.py", None)
        gw = _make_gateway(stub_validator)
        spec = make_blueprint_id_legacy_reconciler(gw)
        result = spec.reconcile(["src/zephyr/no_header.py"], "test-no-header")
        assert result.action == "clean"
        assert "0 violations" in result.detail
        import json

        reports_dir = stub_validator / ".runtime" / "reconcile_reports"
        report = json.loads(list(reports_dir.glob("*.json"))[0].read_text(encoding="utf-8"))
        assert report["files_with_blueprint_header"] == 0
