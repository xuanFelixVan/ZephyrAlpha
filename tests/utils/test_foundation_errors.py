# [A_test] module_id: MOD-GOV_foundation_errors | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_errors

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
