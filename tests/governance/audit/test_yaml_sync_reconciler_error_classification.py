# [A_test] module_id: SRC-TST-2704 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_YAML_SYNC_ERROR_CLASS | docs/_archive/ruling_guc_trigger_cascading_sync_failure.md | §裁定 C / P2
# [MODULE] tests.governance.audit.test_yaml_sync_reconciler_error_classification
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_YAML_SYNC_ERROR_CLASS | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_yaml_sync_reconciler_error_classification.py — reconciler 错误分类与重试策略测试

#ARCH-GUC-TRIGGER-FIX-001 裁定 C (P2): reconciler 错误分类

测试内容：
  1. _classify_sync_failure 纯函数（reconciliation_registry 模块级）
     - deterministic 模式匹配（GUC 未注册 / schema bug / 约束违规）
     - transient 模式匹配（连接 / 死锁 / 超时）
     - unknown 默认返回
     - 边界条件（空字符串 / None / 大小写）
     - 优先级：deterministic + transient 同时出现时 deterministic 优先
  2. _classify_error 纯函数（sync_yaml_to_depgraph 模块级）
     - 异常类型匹配（UndefinedObject / OperationalError 等）
     - 消息文本匹配（psycopg2 用 OperationalError 包装确定性错误的情况）
     - 优先级：deterministic 消息 > transient 类型（避免误判）
  3. _reconcile() 集成测试（mock subprocess）
     - 成功 → action="clean"，重试队列清空
     - deterministic 错误 → action="error"（立即升级，不重试）
     - transient 错误 → action="warn"（重试，队列 attempt+1）
     - unknown 错误 → action="warn"（重试，队列 attempt+1）
     - transient 错误超过 _MAX_RETRY_ATTEMPTS → action="error"（停止重试）
     - 重试队列含 error_class 字段

测试隔离：用 tmp_path 构造 fake gateway，重试队列写入 tmp_path/data/cache/。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
_SYNC_DIR = str(_PROJECT_ROOT / "scripts" / "governance" / "d8_doc_sync")
if _SYNC_DIR not in sys.path:
    sys.path.insert(0, _SYNC_DIR)

from sync_yaml_to_depgraph import _classify_error  # noqa: E402

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcilerSpec,
    _classify_sync_failure,
    make_yaml_sync_reconciler,
)

# ============================================================================
# 1. _classify_sync_failure 纯函数测试
# ============================================================================


class TestClassifySyncFailure:
    """#ARCH-GUC-TRIGGER-FIX-001 裁定 C (P2): reconciler 错误分类纯函数。"""

    # --- deterministic 模式 ---

    @pytest.mark.parametrize("err_text", [
        "unrecognized configuration parameter app.allow_design_maturity_delete",
        'psycopg2.errors.UndefinedObject: 未认可的配置参数 "app.allow_design_maturity_delete"',
        "UndefinedObject: relation does not exist",
        "UndefinedColumn: column foo does not exist",
        "UndefinedTable: relation does not exist",
        "UndefinedFunction: function does not exist",
        "syntax error at or near SELECT",
        "DuplicateTable: relation already exists",
        "DuplicateColumn: column already exists",
        "DuplicateObject: object already exists",
        "permission denied for table users",
        "not-null constraint failed",
        "foreign key constraint violation",
        "unique constraint violation",
        "check constraint failed",
        "invalid input syntax for type integer",
    ])
    def test_deterministic_patterns(self, err_text):
        """确定性错误模式匹配 → deterministic。"""
        assert _classify_sync_failure(err_text) == "deterministic", f"应识别为 deterministic: {err_text}"

    def test_real_guc_bug_error_message(self):
        """原 #ARCH-GUC-TRIGGER-FIX-001 bug 真实错误文本应分类为 deterministic。"""
        err = (
            'psycopg2.errors.UndefinedObject: 未认可的配置参数 "app.allow_design_maturity_delete"\n'
            'CONTEXT: SQL 语句 "SHOW app.allow_design_maturity_delete"\n'
            "在SQL语句的第5行的PL/pgSQL函数protect_dataflow_design_maturity()"
        )
        assert _classify_sync_failure(err) == "deterministic"

    # --- transient 模式 ---

    @pytest.mark.parametrize("err_text", [
        "OperationalError: connection refused",
        "deadlock detected",
        "could not serialize access due to concurrent update",
        "connection timeout expired",
        "could not connect to server",
        "server closed the connection unexpectedly",
        "terminating connection due to administrator command",
    ])
    def test_transient_patterns(self, err_text):
        """瞬态错误模式匹配 → transient。"""
        assert _classify_sync_failure(err_text) == "transient", f"应识别为 transient: {err_text}"

    # --- unknown ---

    @pytest.mark.parametrize("err_text", [
        "some weird unknown error",
        "KeyError: 'foo'",
        "ValueError: invalid argument",
        "",
        None,
    ])
    def test_unknown_patterns(self, err_text):
        """未知错误/边界条件 → unknown。"""
        assert _classify_sync_failure(err_text) == "unknown"

    # --- 大小写不敏感 ---

    def test_case_insensitive(self):
        """错误文本大小写不影响分类。"""
        assert _classify_sync_failure("SYNTAX ERROR") == "deterministic"
        assert _classify_sync_failure("Syntax Error") == "deterministic"
        assert _classify_sync_failure("syntax error") == "deterministic"
        assert _classify_sync_failure("DEADLOCK DETECTED") == "transient"
        assert _classify_sync_failure("Connection Refused") == "transient"

    # --- 优先级：deterministic > transient ---

    def test_deterministic_takes_priority_over_transient(self):
        """当错误文本同时含 deterministic 和 transient 模式时，deterministic 优先。

        场景：psycopg2 OperationalError 包装 UndefinedObject，stderr 同时含
        "operationalerror" 和 "unrecognized configuration parameter"。
        """
        mixed = "OperationalError: connection refused AND unrecognized configuration parameter"
        assert _classify_sync_failure(mixed) == "deterministic"


# ============================================================================
# 2. _classify_error 纯函数测试（sync_yaml_to_depgraph 侧）
# ============================================================================


class TestClassifyError:
    """#ARCH-GUC-TRIGGER-FIX-001 裁定 C (P2): sync 函数异常分类纯函数。"""

    # --- 异常类型匹配 ---

    @pytest.mark.parametrize("exc_type,exc_msg", [
        ("UndefinedObject", "GUC not registered"),
        ("UndefinedColumn", "column missing"),
        ("UndefinedTable", "table missing"),
        ("UndefinedFunction", "function missing"),
        ("SyntaxError", "syntax error"),
        ("DuplicateTable", "table exists"),
        ("DuplicateColumn", "column exists"),
        ("DuplicateObject", "object exists"),
        ("PermissionDenied", "no access"),
        ("NotNullViolation", "null not allowed"),
        ("ForeignKeyViolation", "fk failed"),
        ("UniqueViolation", "dup value"),
        ("CheckViolation", "check failed"),
        ("InvalidTextRepresentation", "bad format"),
        ("InvalidParameterValue", "bad param"),
        ("UndefinedParameter", "param missing"),
        ("DuplicateAlias", "alias exists"),
        ("InvalidColumnReference", "bad col ref"),
        ("GroupingError", "group error"),
        ("WrongObjectType", "wrong type"),
    ])
    def test_deterministic_exception_types(self, exc_type, exc_msg):
        """确定性异常类型匹配 → deterministic。"""
        assert _classify_error(exc_type, exc_msg) == "deterministic"

    @pytest.mark.parametrize("exc_type,exc_msg", [
        ("OperationalError", "connection refused"),
        ("DeadlockDetected", "deadlock"),
        ("SerializationFailure", "could not serialize"),
        ("InternalError", "internal"),
    ])
    def test_transient_exception_types(self, exc_type, exc_msg):
        """瞬态异常类型匹配 → transient。"""
        assert _classify_error(exc_type, exc_msg) == "transient"

    def test_unknown_exception_type(self):
        """未知异常类型 + 无模式匹配 → unknown。"""
        assert _classify_error("ValueError", "something weird") == "unknown"
        assert _classify_error("KeyError", "key not found") == "unknown"

    # --- 消息文本匹配（异常类型未命中时）---

    def test_message_pattern_deterministic(self):
        """异常类型未命中但消息含 deterministic 模式 → deterministic。"""
        assert _classify_error("Exception", "unrecognized configuration parameter") == "deterministic"
        assert _classify_error("Exception", "does not exist") == "deterministic"
        assert _classify_error("Exception", "already exists") == "deterministic"
        assert _classify_error("Exception", "permission denied") == "deterministic"

    def test_message_pattern_transient(self):
        """异常类型未命中但消息含 transient 模式 → transient。"""
        assert _classify_error("Exception", "deadlock detected") == "transient"
        assert _classify_error("Exception", "connection refused") == "transient"

    # --- 优先级：deterministic 消息 > transient 类型 ---

    def test_deterministic_message_overrides_transient_type(self):
        """OperationalError 类型 + deterministic 消息 → deterministic（优先级）。

        关键场景：psycopg2 可能用 OperationalError 包装 UndefinedObject，
        导致 type(e).__name__ == 'OperationalError' 但消息含 GUC 错误。
        此时必须识别为 deterministic，否则 reconciler 会盲重试。
        """
        assert _classify_error("OperationalError", "unrecognized configuration parameter") == "deterministic"
        assert _classify_error("OperationalError", "relation does not exist") == "deterministic"

    # --- 边界条件 ---

    def test_empty_and_none(self):
        """空字符串 / None 参数 → unknown。"""
        assert _classify_error("", "") == "unknown"
        assert _classify_error(None, None) == "unknown"
        assert _classify_error("", "some error") == "unknown"
        assert _classify_error("ValueError", "") == "unknown"

    def test_case_insensitive(self):
        """异常类型和消息大小写不影响分类。"""
        assert _classify_error("undefinedobject", "msg") == "deterministic"
        assert _classify_error("UNDEFINEDOBJECT", "msg") == "deterministic"
        assert _classify_error("Exception", "SYNTAX ERROR") == "deterministic"
        assert _classify_error("Exception", "DEADLOCK DETECTED") == "transient"


# ============================================================================
# 3. _reconcile() 集成测试（mock subprocess）
# ============================================================================


class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root（指向 tmp_path）。"""

    def __init__(self, project_root: Path):
        self.project_root = project_root


def _make_subprocess_result(returncode: int, stdout: str = "", stderr: str = ""):
    """构造模拟的 subprocess.CompletedProcess。"""
    r = MagicMock()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


def _read_retry_queue(tmp_path: Path) -> dict | None:
    """读取 tmp_path 下的重试队列文件。"""
    qpath = tmp_path / "data" / "cache" / "yaml_sync_retry_queue.json"
    if not qpath.exists():
        return None
    return json.loads(qpath.read_text(encoding="utf-8"))


class TestReconcileErrorClassification:
    """#ARCH-GUC-TRIGGER-FIX-001 裁定 C (P2): _reconcile() 错误分类与重试策略。"""

    def test_reconcile_success_clears_retry_queue(self, tmp_path):
        """sync 成功 → action="clean"，重试队列清空。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        # 预置一个重试队列
        qpath = tmp_path / "data" / "cache" / "yaml_sync_retry_queue.json"
        qpath.parent.mkdir(parents=True, exist_ok=True)
        qpath.write_text(json.dumps({"attempt": 2, "error": "prev"}), encoding="utf-8")

        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(0, stdout="synced ok", stderr=""),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "clean"
        assert "synced" in r.detail.lower() or "clean" in r.detail.lower()
        assert not qpath.exists(), "重试队列应被清空"

    def test_reconcile_deterministic_failure_immediate_error(self, tmp_path):
        """deterministic 错误 → action="error"（立即升级，不重试）。

        关键验证：#ARCH-GUC-TRIGGER-FIX-001 根因——GUC 未注册错误重试 23 次全失败。
        修复后此类错误第一次出现即升级为 error，不再盲重试。
        """
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        guc_err = 'psycopg2.errors.UndefinedObject: 未认可的配置参数 "app.allow_design_maturity_delete"'

        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(1, stdout="", stderr=guc_err),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "error", f"deterministic 错误应立即 error，实际: {r.action}"
        assert "DETERMINISTIC" in r.detail or "deterministic" in r.detail.lower()
        assert "NOT retryable" in r.detail or "not retryable" in r.detail.lower()
        assert "schema bug" in r.detail.lower() or "GUC" in r.detail or "constraint" in r.detail.lower()
        # 重试队列应记录 error_class=deterministic + escalated=True，attempt=1（不累加）
        queue = _read_retry_queue(tmp_path)
        assert queue is not None, "deterministic 失败应写入重试队列（标记 escalated）"
        assert queue.get("error_class") == "deterministic"
        assert queue.get("escalated") is True
        assert queue.get("attempt") == 1, "deterministic 错误 attempt 固定为 1（不重试）"

    def test_reconcile_transient_failure_warn_and_retry(self, tmp_path):
        """transient 错误 → action="warn"，attempt+1，队列含 error_class=transient。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        transient_err = "psycopg2.OperationalError: connection refused"

        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(1, stdout="", stderr=transient_err),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "warn", f"transient 错误应 warn（重试），实际: {r.action}"
        assert "error_class=transient" in r.detail
        assert "will retry" in r.detail.lower()
        queue = _read_retry_queue(tmp_path)
        assert queue is not None
        assert queue.get("error_class") == "transient"
        assert queue.get("attempt") == 1
        assert "escalated" not in queue or queue.get("escalated") is not True

    def test_reconcile_unknown_failure_warn_and_retry(self, tmp_path):
        """unknown 错误 → action="warn"，attempt+1，队列含 error_class=unknown。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        unknown_err = "KeyError: 'something weird'"

        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(1, stdout="", stderr=unknown_err),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "warn", f"unknown 错误应 warn（保守重试），实际: {r.action}"
        assert "error_class=unknown" in r.detail
        queue = _read_retry_queue(tmp_path)
        assert queue is not None
        assert queue.get("error_class") == "unknown"
        assert queue.get("attempt") == 1

    def test_reconcile_transient_max_retry_escalates_to_error(self, tmp_path):
        """transient 错误超过 _MAX_RETRY_ATTEMPTS → action="error"（停止重试）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        # 预置已达 max-1 次的队列（下次是第 max 次）
        qpath = tmp_path / "data" / "cache" / "yaml_sync_retry_queue.json"
        qpath.parent.mkdir(parents=True, exist_ok=True)
        qpath.write_text(json.dumps({
            "attempt": 2,  # _MAX_RETRY_ATTEMPTS=3，下次是第 3 次
            "error": "prev transient",
            "error_class": "transient",
        }), encoding="utf-8")

        transient_err = "OperationalError: connection timeout"
        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(1, stdout="", stderr=transient_err),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "error", f"超过 max retry 应 error，实际: {r.action}"
        assert "STOPPED retry" in r.detail or "max=3" in r.detail
        assert "error_class=transient" in r.detail
        queue = _read_retry_queue(tmp_path)
        assert queue.get("attempt") == 3

    def test_reconcile_deterministic_does_not_accumulate_retry(self, tmp_path):
        """deterministic 错误连续出现 2 次，attempt 始终为 1（不重试不累加）。

        对比原 bug：sync_dataflow_registry retry 23 次——如果当时有此分类，
        第 1 次失败即升级为 error，不会有 23 次重试。
        """
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        guc_err = 'UndefinedObject: unrecognized configuration parameter app.x'

        for _ in range(2):
            with patch(
                "zephyr.governance.audit.reconciliation_registry._run_subprocess",
                return_value=_make_subprocess_result(1, stdout="", stderr=guc_err),
            ):
                r = spec.reconcile([], "sess-test")

            assert r.action == "error", "deterministic 错误每次都应 error"
            queue = _read_retry_queue(tmp_path)
            assert queue.get("attempt") == 1, f"deterministic attempt 应始终为 1，实际: {queue.get('attempt')}"
            assert queue.get("error_class") == "deterministic"
            assert queue.get("escalated") is True

    def test_reconcile_detail_includes_error_snippet(self, tmp_path):
        """error/warn detail 包含错误文本片段（便于 AI 诊断）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        err = "syntax error at or near SELECT FROM WHERE"

        with patch(
            "zephyr.governance.audit.reconciliation_registry._run_subprocess",
            return_value=_make_subprocess_result(1, stdout="", stderr=err),
        ):
            r = spec.reconcile([], "sess-test")

        assert r.action == "error"
        assert "syntax error" in r.detail, f"detail 应包含错误片段，实际: {r.detail}"


# ============================================================================
# 4. 工厂函数测试
# ============================================================================


class TestMakeYamlSyncReconcilerFactory:
    """make_yaml_sync_reconciler 工厂返回值测试。"""

    def test_factory_returns_spec(self, tmp_path):
        """工厂返回正确 ReconcilerSpec（gate_id / priority / callables）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_yaml_sync_reconciler(gw)
        assert isinstance(spec, ReconcilerSpec)
        assert spec.gate_id == "GATE-YAML-SYNC"
        assert spec.priority == 160
        assert callable(spec.trigger)
        assert callable(spec.reconcile)
