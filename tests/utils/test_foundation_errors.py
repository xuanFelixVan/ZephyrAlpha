# [A_test] module_id: MOD-GOV_foundation_errors | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_errors
# [DOMAIN] D_SHARED

# [INVARIANTS] ZephyrBaseError为所有业务异常根;details默认空dict;__str__返回message

# [MODIFY-GUARD] errors.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_foundation_errors.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.foundation.errors import (
    ConfigError,
    ContextError,
    ContractError,
    DataError,
    FeedbackError,
    GateError,
    IOError,
    PipelineError,
    SecurityError,
    TaskError,
    UnimplementedError,
    ValidationError,
    ZephyrBaseError,
)


class TestZephyrBaseError:
    def test_init_with_message_only(self):
        err = ZephyrBaseError("something went wrong")
        assert err.message == "something went wrong"
        assert err.details == {}
        assert str(err) == "something went wrong"

    def test_init_with_details(self):
        err = ZephyrBaseError("fail", details={"key": "val", "num": 42})
        assert err.details == {"key": "val", "num": 42}

    def test_init_with_none_details_yields_empty_dict(self):
        err = ZephyrBaseError("fail", details=None)
        assert err.details == {}

    def test_repr_without_details(self):
        err = ZephyrBaseError("oops")
        assert repr(err) == "ZephyrBaseError(message='oops')"

    def test_repr_with_details(self):
        err = ZephyrBaseError("oops", details={"k": 1})
        assert "details={'k': 1}" in repr(err)

    def test_is_exception(self):
        err = ZephyrBaseError("boom")
        assert isinstance(err, Exception)

    def test_raise_and_catch(self):
        with pytest.raises(ZephyrBaseError) as exc_info:
            raise ZephyrBaseError("caught", details={"a": "b"})
        assert exc_info.value.message == "caught"
        assert exc_info.value.details == {"a": "b"}


class TestErrorSubclasses:
    @pytest.mark.parametrize(
        "cls",
        [
            ConfigError,
            ContractError,
            SecurityError,
            ValidationError,
            TaskError,
            PipelineError,
            GateError,
            ContextError,
            FeedbackError,
            DataError,
            IOError,
            UnimplementedError,
        ],
    )
    def test_subclass_inherits_from_base(self, cls):
        err = cls("sub error")
        assert isinstance(err, ZephyrBaseError)
        assert isinstance(err, Exception)
        assert err.message == "sub error"
        assert err.details == {}

    @pytest.mark.parametrize(
        "cls",
        [
            ConfigError,
            ContractError,
            SecurityError,
            ValidationError,
            TaskError,
            PipelineError,
            GateError,
            ContextError,
            FeedbackError,
            DataError,
            IOError,
            UnimplementedError,
        ],
    )
    def test_subclass_catch_by_base(self, cls):
        with pytest.raises(ZephyrBaseError):
            raise cls("catch via base")

    @pytest.mark.parametrize(
        "cls",
        [
            ConfigError,
            ContractError,
            SecurityError,
            ValidationError,
            TaskError,
            PipelineError,
            GateError,
            ContextError,
            FeedbackError,
            DataError,
            IOError,
            UnimplementedError,
        ],
    )
    def test_subclass_with_details(self, cls):
        err = cls("msg", details={"code": 500})
        assert err.details == {"code": 500}

    def test_catch_specific_before_base(self):
        with pytest.raises(TaskError):
            raise TaskError("task failed", details={"task_id": "T-001"})

    def test_ioerror_not_builtins_ioerror(self):
        err = IOError("zephyr io error")
        assert not isinstance(err, OSError)
        assert isinstance(err, ZephyrBaseError)


class TestErrorCodeRuntimeError:
    """包5 工厂化（st-nightsweep-sw8-20260929）：gateway↔duckdb 同构 __init__ 收编基类。"""

    def test_base_semantics_default_code(self):
        from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

        class _Demo(ErrorCodeRuntimeError):
            error_code = "ZA-XX-0001"

        err = _Demo("boom", 42)
        assert err.error_code == "ZA-XX-0001"
        assert isinstance(err, RuntimeError)
        assert err.args == ("boom", 42)

    def test_base_semantics_kwarg_override(self):
        from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

        class _Demo(ErrorCodeRuntimeError):
            error_code = "ZA-XX-0001"

        err = _Demo("boom", error_code="ZA-XX-9999")
        assert err.error_code == "ZA-XX-9999"

    def test_base_no_default_code(self):
        from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

        err = ErrorCodeRuntimeError("bare")
        assert err.error_code is None

    def test_gateway_error_adopts_base(self):
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GatewayError
        from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

        assert issubclass(GatewayError, ErrorCodeRuntimeError)
        # 工厂化最严格判据：不再持有复制的 __init__（原 extract 级克隆收编基类）
        assert GatewayError.__init__ is ErrorCodeRuntimeError.__init__
        err = GatewayError("lock timeout", error_code="ZA-GV-CUSTOM")
        assert err.error_code == "ZA-GV-CUSTOM"
        assert GatewayError("x").error_code == "ZA-GV-0032"

    def test_duckdb_gate_error_adopts_base(self):
        from zephyr.infrastructure.duckdb_runtime_gate import BareDuckDBConnectError
        from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

        assert issubclass(BareDuckDBConnectError, ErrorCodeRuntimeError)
        assert BareDuckDBConnectError.__init__ is ErrorCodeRuntimeError.__init__
        err = BareDuckDBConnectError("bare connect", error_code="ZA-INF-CUSTOM")
        assert err.error_code == "ZA-INF-CUSTOM"
        assert BareDuckDBConnectError("x").error_code == "ZA-INF-0901"
