# [A_test] module_id: MOD-L02-027 | layer=test | stability=volatile | safety=L
# [BLUEPRINT] MOD-L02-027 | docs/03_modules/_domain_factor/casebook/blueprint.md | §D-FACTOR-CASE-01
# [MODULE] tests.factor.test_casebook
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_casebook.py
# [A_module] module_id=MOD-L02-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""因子研究案例库测试——写入/检索/空库/重复边界/非法拒绝/并发写。

覆盖（92 号清单 §5.3 ALG-03 验收口径）：
- record_case 写入 → get_case/query_similar 检索闭环
- 空库查询返回空、不建库文件
- 重复假设允许各存一条（id 自增不同）
- 非法 verdict / NaN·inf 统计量 / 空 hypothesis 一律 CasebookError 拒绝（fail-closed）
- 两线程并发写不崩、行数与 id 唯一性正确
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from zephyr.factor.casebook import (
    CasebookError,
    get_case,
    query_similar,
    record_case,
)


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    """隔离的临时库路径（不碰生产 data/databases/factor_casebook.db）。"""
    return tmp_path / "factor_casebook.db"


class TestRecordAndGet:
    """写入-检索闭环。"""

    def test_record_and_get_roundtrip(self, db: Path) -> None:
        cid = record_case(
            "5 日动量与次周收益正相关",
            verdict="success",
            factor_expr="close / shift(close, 5) - 1",
            factor_json='{"family": "momentum", "window": 5}',
            ic=0.062,
            icir=0.71,
            turnover=0.35,
            tags=["momentum", "daily"],
            db_path=db,
        )
        assert cid == 1
        case = get_case(cid, db_path=db)
        assert case is not None
        assert case["hypothesis"] == "5 日动量与次周收益正相关"
        assert case["verdict"] == "success"
        assert case["ic"] == pytest.approx(0.062)
        assert case["icir"] == pytest.approx(0.71)
        assert case["turnover"] == pytest.approx(0.35)
        assert case["tags"] == ["momentum", "daily"]
        assert case["created_at"]

    def test_record_minimal_fields(self, db: Path) -> None:
        cid = record_case("反转因子在缩量环境失效", verdict="failure", db_path=db)
        case = get_case(cid, db_path=db)
        assert case is not None
        assert case["ic"] is None
        assert case["factor_expr"] is None
        assert case["tags"] == []

    def test_fixed_verdict_with_diag(self, db: Path) -> None:
        cid = record_case(
            "换手率因子 IC 为负",
            verdict="fixed",
            failure_diag="原假设符号取反后 IC 转正，按修复版入库",
            ic=0.041,
            db_path=db,
        )
        assert get_case(cid, db_path=db)["verdict"] == "fixed"


class TestQuerySimilar:
    """标签/verdict 检索。"""

    def test_query_by_family_tag(self, db: Path) -> None:
        record_case("动量假设A", verdict="success", tags=["momentum"], db_path=db)
        record_case("价值假设B", verdict="success", tags=["value"], db_path=db)
        record_case("动量假设C", verdict="failure", tags=["momentum"], db_path=db)
        hits = query_similar(family_tag="momentum", db_path=db)
        assert len(hits) == 2
        assert all("momentum" in h["tags"] for h in hits)
        # 默认按 id 倒序（最新在前）
        assert hits[0]["hypothesis"] == "动量假设C"

    def test_query_tag_exact_element_no_substring(self, db: Path) -> None:
        record_case("长动量", verdict="success", tags=["momentum_long"], db_path=db)
        # mom 是 momentum_long 的子串，元素级精确匹配不应命中
        assert query_similar(family_tag="mom", db_path=db) == []
        assert len(query_similar(family_tag="momentum_long", db_path=db)) == 1

    def test_query_by_verdict(self, db: Path) -> None:
        record_case("案例1", verdict="success", db_path=db)
        record_case("案例2", verdict="failure", db_path=db)
        record_case("案例3", verdict="fixed", db_path=db)
        fixed = query_similar(verdict="fixed", db_path=db)
        assert len(fixed) == 1
        assert fixed[0]["hypothesis"] == "案例3"

    def test_query_limit(self, db: Path) -> None:
        for i in range(5):
            record_case(f"案例{i}", verdict="success", db_path=db)
        assert len(query_similar(limit=2, db_path=db)) == 2

    def test_query_empty_db(self, db: Path) -> None:
        assert query_similar(db_path=db) == []
        assert query_similar(family_tag="momentum", db_path=db) == []
        assert get_case(999, db_path=db) is None
        # 空库查询不得主动创建库文件
        assert not db.exists()

    def test_query_invalid_verdict_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            query_similar(verdict="maybe", db_path=db)

    def test_query_invalid_limit_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            query_similar(limit=0, db_path=db)


class TestDuplicateBoundary:
    """重复边界：同假设可重复登记（不同 id），最小字段组合可写。"""

    def test_duplicate_hypothesis_both_stored(self, db: Path) -> None:
        cid1 = record_case("同一假设重复试验", verdict="failure", db_path=db)
        cid2 = record_case("同一假设重复试验", verdict="fixed", db_path=db)
        assert cid1 != cid2
        assert get_case(cid1, db_path=db)["verdict"] == "failure"
        assert get_case(cid2, db_path=db)["verdict"] == "fixed"
        assert len(query_similar(db_path=db)) == 2


class TestFailClosedValidation:
    """非法输入一律拒绝（fail-closed）。"""

    def test_invalid_verdict_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("假设", verdict="unknown", db_path=db)

    def test_nan_ic_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("假设", verdict="success", ic=float("nan"), db_path=db)

    def test_inf_icir_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("假设", verdict="success", icir=float("inf"), db_path=db)

    def test_nan_turnover_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("假设", verdict="success", turnover=float("nan"), db_path=db)

    def test_empty_hypothesis_rejected(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("", verdict="success", db_path=db)
        with pytest.raises(CasebookError):
            record_case("   ", verdict="success", db_path=db)

    def test_rejected_input_leaves_no_row(self, db: Path) -> None:
        with pytest.raises(CasebookError):
            record_case("假设", verdict="bad", db_path=db)
        assert query_similar(db_path=db) == []


class TestConcurrentWrites:
    """并发写：两线程各写 20 条，不崩、行数正确、id 唯一。"""

    def test_two_threads_concurrent_write(self, db: Path) -> None:
        errors: list[BaseException] = []
        per_thread = 20

        def _worker(prefix: str) -> None:
            try:
                for i in range(per_thread):
                    record_case(
                        f"{prefix} 假设 {i}",
                        verdict="success",
                        ic=0.01 * i,
                        tags=[prefix],
                        db_path=db,
                    )
            except BaseException as exc:  # noqa: BLE001 - 测试需捕获线程内一切异常
                errors.append(exc)

        t1 = threading.Thread(target=_worker, args=("threadA",))
        t2 = threading.Thread(target=_worker, args=("threadB",))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert errors == []
        all_cases = query_similar(limit=100, db_path=db)
        assert len(all_cases) == 2 * per_thread
        ids = [c["id"] for c in all_cases]
        assert len(set(ids)) == 2 * per_thread
        assert len(query_similar(family_tag="threadA", limit=100, db_path=db)) == per_thread
