# [BLUEPRINT] MOD-DAT-AUTO-BACKFILLER | tests/zephyr/data/test_auto_backfiller.py
# [MODULE] tests.zephyr.data.test_auto_backfiller
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.auto_backfiller
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT-AUTO-BACKFILLER | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AutoBackfiller 单元测试——事件触发式自动回填器（CAND-DAT-014 / B10-01815 / §29.2-7）。

覆盖：
    1. 触发事件校验：未知类型/日期倒挂/空 target → ValueError fail-closed
    2. 分片规划：shard_days 切片 + 可选交易日历过滤
    3. 执行：executor 注入逐片执行，单片异常不中断其余
    4. 抽样验证：10% 确定性抽样（最少 1 片），默认/注入 validator
    5. 血缘+重训：全成功且样本通过才触发；失败不触发（fail-closed）
    6. sink 异常不阻断报告（sink_errors 留痕）
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.data.auto_backfiller import (
    AutoBackfillConfig,
    AutoBackfiller,
    BackfillTrigger,
    ShardResult,
)

D = datetime.date


def _trigger(**kw) -> BackfillTrigger:
    base = {
        "trigger_type": "new_factor",
        "target": "alpha_87",
        "start_date": D(2026, 8, 1),
        "end_date": D(2026, 8, 20),
    }
    base.update(kw)
    return BackfillTrigger(**base)


def _ok_executor(shard):
    return ShardResult(shard_id=shard.shard_id, rows_written=100, success=True, error="")


# ── 1. 触发校验 ──


def test_unknown_trigger_type_fail_closed():
    bf = AutoBackfiller(executor=_ok_executor)
    with pytest.raises(ValueError):
        bf.plan(_trigger(trigger_type="bogus"))


def test_start_after_end_fail_closed():
    bf = AutoBackfiller(executor=_ok_executor)
    with pytest.raises(ValueError):
        bf.plan(_trigger(start_date=D(2026, 8, 20), end_date=D(2026, 8, 1)))


def test_empty_target_fail_closed():
    bf = AutoBackfiller(executor=_ok_executor)
    with pytest.raises(ValueError):
        bf.plan(_trigger(target=""))


def test_all_trigger_types_accepted():
    bf = AutoBackfiller(executor=_ok_executor)
    for t in ("new_factor", "formula_upgrade", "data_source_fix"):
        plan = bf.plan(_trigger(trigger_type=t))
        assert plan.trigger.trigger_type == t


# ── 2. 分片规划 ──


def test_plan_shards_by_shard_days():
    cfg = AutoBackfillConfig(shard_days=7)
    bf = AutoBackfiller(config=cfg, executor=_ok_executor)
    plan = bf.plan(_trigger())  # 8/1~8/20 → 3 片
    assert len(plan.shards) == 3
    assert plan.shards[0].start_date == D(2026, 8, 1)
    assert plan.shards[0].end_date == D(2026, 8, 7)
    assert plan.shards[-1].end_date == D(2026, 8, 20)
    assert plan.sample_ratio == cfg.sample_ratio


def test_plan_trading_days_filter():
    # 仅 8/3(周一)~8/7(周五) 为交易日
    tdays = [D(2026, 8, 3) + datetime.timedelta(days=i) for i in range(5)]
    bf = AutoBackfiller(
        config=AutoBackfillConfig(shard_days=7),
        executor=_ok_executor,
        trading_days_provider=lambda s, e: tdays,
    )
    plan = bf.plan(_trigger(start_date=D(2026, 8, 1), end_date=D(2026, 8, 9)))
    days_covered = set()
    for sh in plan.shards:
        d = sh.start_date
        while d <= sh.end_date:
            days_covered.add(d)
            d += datetime.timedelta(days=1)
    assert days_covered == set(tdays)


# ── 3. 执行 ──


def test_run_all_success_triggers_lineage_and_retrain():
    lineage, retrain = [], []
    bf = AutoBackfiller(
        config=AutoBackfillConfig(shard_days=7),
        executor=_ok_executor,
        lineage_sink=lineage.append,
        retrain_sink=retrain.append,
    )
    rep = bf.run(_trigger())
    assert rep.total_shards == 3
    assert rep.succeeded == 3
    assert rep.failed == 0
    assert rep.sample_passed is True
    assert rep.lineage_updated is True
    assert rep.retrain_triggered is True
    assert len(lineage) == 1 and len(retrain) == 1
    assert retrain[0].target == "alpha_87"


def test_run_shard_failure_blocks_lineage_and_retrain():
    lineage, retrain = [], []

    def flaky(shard):
        if shard.shard_id == 1:
            raise RuntimeError("boom")
        return _ok_executor(shard)

    bf = AutoBackfiller(
        config=AutoBackfillConfig(shard_days=7),
        executor=flaky,
        lineage_sink=lineage.append,
        retrain_sink=retrain.append,
    )
    rep = bf.run(_trigger())
    assert rep.succeeded == 2
    assert rep.failed == 1
    assert rep.lineage_updated is False
    assert rep.retrain_triggered is False
    assert lineage == [] and retrain == []


# ── 4. 抽样验证 ──


def test_sampling_min_one_and_deterministic():
    cfg = AutoBackfillConfig(shard_days=1, sample_ratio=0.10)  # 20 片→2 样本
    seen = []

    def validator(shard, result):
        seen.append(shard.shard_id)
        return True

    bf1 = AutoBackfiller(config=cfg, executor=_ok_executor, sample_validator=validator, rng_seed=42)
    rep1 = bf1.run(_trigger())
    first = list(seen)
    seen.clear()
    bf2 = AutoBackfiller(config=cfg, executor=_ok_executor, sample_validator=validator, rng_seed=42)
    rep2 = bf2.run(_trigger())
    assert rep1.sampled >= 1
    assert first == seen  # 同种子同样本
    assert rep1.sampled == rep2.sampled


def test_sample_validator_failure_blocks_retrain():
    retrain = []
    bf = AutoBackfiller(
        config=AutoBackfillConfig(shard_days=7),
        executor=_ok_executor,
        sample_validator=lambda shard, result: False,
        retrain_sink=retrain.append,
    )
    rep = bf.run(_trigger())
    assert rep.sample_passed is False
    assert rep.retrain_triggered is False
    assert rep.lineage_updated is False
    assert retrain == []


def test_default_validator_requires_rows_written():
    def zero_executor(shard):
        return ShardResult(shard_id=shard.shard_id, rows_written=0, success=True, error="")

    bf = AutoBackfiller(config=AutoBackfillConfig(shard_days=7), executor=zero_executor)
    rep = bf.run(_trigger())
    assert rep.sample_passed is False


# ── 5. sink 异常不阻断 ──


def test_sink_errors_recorded_not_raised():
    def bad_sink(_):
        raise RuntimeError("sink down")

    bf = AutoBackfiller(
        config=AutoBackfillConfig(shard_days=7),
        executor=_ok_executor,
        lineage_sink=bad_sink,
        retrain_sink=bad_sink,
    )
    rep = bf.run(_trigger())
    assert rep.succeeded == 3
    assert len(rep.sink_errors) == 2
    assert rep.lineage_updated is False
    assert rep.retrain_triggered is False
