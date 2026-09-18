# [A_test] module_id: MOD-GOV_position_reconciler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.rollback.test_rollback_position_reconciler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/rollback/test_rollback_position_reconciler.py -q
# [TTL] task_bound
from zephyr.position.position_reconciler import PositionReconciler


class TestPositionReconcilerInstantiation:
    def test_creates_instance(self):
        reconciler = PositionReconciler()
        assert isinstance(reconciler, PositionReconciler)

    def test_has_reconcile_method(self):
        reconciler = PositionReconciler()
        assert callable(getattr(reconciler, "reconcile", None))

    def test_has_should_escalate_method(self):
        reconciler = PositionReconciler()
        assert callable(getattr(reconciler, "should_escalate", None))


class TestReconcile:
    def test_matching_positions(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50}
        external = {"AAPL": 100, "GOOG": 50}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True
        assert result["diffs"] == {}
        assert result["count"] == 0

    def test_mismatched_positions(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50}
        external = {"AAPL": 90, "GOOG": 50}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert result["count"] == 1
        assert "AAPL" in result["diffs"]
        assert result["diffs"]["AAPL"]["internal"] == 100
        assert result["diffs"]["AAPL"]["external"] == 90
        assert result["diffs"]["AAPL"]["diff"] == 10

    def test_key_only_in_internal(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "MSFT": 30}
        external = {"AAPL": 100}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert "MSFT" in result["diffs"]
        assert result["diffs"]["MSFT"]["internal"] == 30
        assert result["diffs"]["MSFT"]["external"] == 0
        assert result["diffs"]["MSFT"]["diff"] == 30

    def test_key_only_in_external(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100}
        external = {"AAPL": 100, "TSLA": 75}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert "TSLA" in result["diffs"]
        assert result["diffs"]["TSLA"]["internal"] == 0
        assert result["diffs"]["TSLA"]["external"] == 75
        assert result["diffs"]["TSLA"]["diff"] == -75

    def test_both_empty(self):
        reconciler = PositionReconciler()
        result = reconciler.reconcile({}, {})
        assert result["match"] is True
        assert result["diffs"] == {}
        assert result["count"] == 0

    def test_multiple_mismatches(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 100, "GOOG": 50, "MSFT": 30}
        external = {"AAPL": 90, "GOOG": 60, "MSFT": 30}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is False
        assert result["count"] == 2

    def test_diff_value_is_internal_minus_external(self):
        reconciler = PositionReconciler()
        internal = {"X": 200}
        external = {"X": 250}
        result = reconciler.reconcile(internal, external)
        assert result["diffs"]["X"]["diff"] == -50

    def test_result_structure(self):
        reconciler = PositionReconciler()
        result = reconciler.reconcile({}, {})
        assert "match" in result
        assert "diffs" in result
        assert "count" in result


class TestShouldEscalate:
    def test_below_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(1, threshold=3) is False

    def test_at_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(3, threshold=3) is True

    def test_above_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(5, threshold=3) is True

    def test_zero_diffs(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(0, threshold=3) is False

    def test_default_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(2) is False
        assert reconciler.should_escalate(3) is True

    def test_custom_threshold(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(4, threshold=5) is False
        assert reconciler.should_escalate(5, threshold=5) is True


class TestBoundaryConditions:
    def test_reconcile_with_zero_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 0}
        external = {"AAPL": 0}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_reconcile_large_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": 999999999}
        external = {"AAPL": 999999999}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_reconcile_negative_values(self):
        reconciler = PositionReconciler()
        internal = {"AAPL": -10}
        external = {"AAPL": -10}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True

    def test_should_escalate_threshold_one(self):
        reconciler = PositionReconciler()
        assert reconciler.should_escalate(0, threshold=1) is False
        assert reconciler.should_escalate(1, threshold=1) is True

    def test_reconcile_many_keys(self):
        reconciler = PositionReconciler()
        internal = {f"K{i}": i for i in range(100)}
        external = {f"K{i}": i for i in range(100)}
        result = reconciler.reconcile(internal, external)
        assert result["match"] is True
        assert result["count"] == 0

    def test_reconcile_single_key_diff(self):
        reconciler = PositionReconciler()
        internal = {"A": 1}
        external = {"A": 2}
        result = reconciler.reconcile(internal, external)
        assert result["count"] == 1
        assert result["diffs"]["A"]["diff"] == -1


class TestHandleExecutionReportFailClosed:
    """BRK-016 加严钉：事件入口禁把"拿不到数据"判成"对平了"。

    旧实现 `execution_report.get("internal_positions", {})` 对缺键静默补空
    → 两侧都缺时返回 match=True（假对账，与 #ARCH-327 同型：防线在
    输入侧空转而测试全绿）。这些用例是**能红证据**：把 fail-closed 改回
    .get(key, {}) 则本类整片转红。
    """

    def test_missing_both_keys_is_not_match(self):
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report({})
        assert result["match"] is False
        assert result["status"] == "input_unavailable"
        assert result["rule_id"] == "POS-RECON-002"
        assert set(result["missing"]) == {"internal_positions", "external_positions"}
        assert result["escalate"] is True

    def test_missing_one_key_is_not_match(self):
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report({"internal_positions": {"A": 1}})
        assert result["match"] is False
        assert result["missing"] == ["external_positions"]

    def test_none_positions_is_not_match(self):
        """键在但值为 None（上游查询失败回填 None）= 不可得，禁当空仓。"""
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report(
            {"internal_positions": None, "external_positions": {"A": 1}}
        )
        assert result["match"] is False
        assert "internal_positions:not_mapping" in result["missing"]

    def test_non_mapping_event_is_not_match(self):
        reconciler = PositionReconciler()
        for bad in (None, [], "", 42):
            result = reconciler.handle_execution_report(bad)  # type: ignore[arg-type]
            assert result["match"] is False
            assert result["missing"] == ["event_not_mapping"]

    def test_unproven_double_empty_is_not_match(self):
        """双空且无出处声明 → 无法区分"真空仓"与"两侧都瞎"→ 判不可得。"""
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report(
            {"internal_positions": {}, "external_positions": {}}
        )
        assert result["match"] is False
        assert result["missing"] == ["unproven_empty_positions"]

    def test_declared_flat_book_is_match(self):
        """显式声明出处（空仓合法态）→ 真判平，且不误升级。"""
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report({
            "internal_positions": {},
            "external_positions": {},
            "positions_provenance": "broker PositionStatics.csv @2026-09-18T15:00+08:00",
        })
        assert result["match"] is True
        assert result["status"] == "ok"
        assert result["escalate"] is False

    def test_event_entry_reconciles_real_diff(self):
        reconciler = PositionReconciler()
        result = reconciler.handle_execution_report({
            "internal_positions": {"510300.SH": 100},
            "external_positions": {"510300.SH": 200},
        })
        assert result["match"] is False
        assert result["status"] == "mismatch"
        assert result["rule_id"] == "POS-RECON-001"
        assert result["diffs"]["510300.SH"]["diff"] == -100

    def test_escalation_sink_invoked_on_input_unavailable(self):
        """P0-FATAL 必须真有人接：输入不可得也要走 sink（旧实现根本无此路径）。"""
        got: list[dict] = []
        reconciler = PositionReconciler(escalation_sink=got.append)
        reconciler.handle_execution_report({})
        assert len(got) == 1
        assert got[0]["rule_id"] == "POS-RECON-002"

    def test_escalation_sink_invoked_on_threshold_breach(self):
        got: list[dict] = []
        reconciler = PositionReconciler(escalation_sink=got.append)
        reconciler.handle_execution_report({
            "internal_positions": {"A": 1, "B": 2, "C": 3},
            "external_positions": {"A": 9, "B": 9, "C": 9},
        })
        assert len(got) == 1
        assert got[0]["rule_id"] == "POS-RECON-001"

    def test_escalation_sink_exception_does_not_break_reconcile(self):
        """sink 抛异常必须被 Fail-Loud 兜住（计数与结果仍出，禁空转）。"""
        def _boom(_payload: dict) -> None:
            raise RuntimeError("sink down")

        reconciler = PositionReconciler(escalation_sink=_boom)
        result = reconciler.handle_execution_report({})
        assert result["status"] == "input_unavailable"
        assert reconciler.unavailable_count == 1

    def test_unavailable_count_accumulates(self):
        reconciler = PositionReconciler()
        for _ in range(3):
            reconciler.handle_execution_report({})
        assert reconciler.unavailable_count == 3
        assert reconciler.mismatch_count == 0

