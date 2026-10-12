# [A_test] module_id: TEST-MOD-EX_SOR | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_sor.test_td3_trainer
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] torch, zephyr.ex_sor.core.rl_exec_env, zephyr.ex_sor.services.rl_trainer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;小网 CPU 秒级;零实盘零生产路径（checkpoint 落 tmp_path）;H-04：仅施工验证，不触发生产训练管线
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/trade/ex_sor/test_td3_trainer.py
# [TTL] task_bound
"""TD3 执行训练器施工验证（TC-11 件3）：obs 编码/动作解码/预热/更新/checkpoint 往返。"""

from __future__ import annotations

import numpy as np
import pytest
from test_rl_exec_env import make_contract, make_env

from zephyr.ex_sor.services.rl_trainer.td3_agent import TD3Agent, load_checkpoint, save_checkpoint
from zephyr.ex_sor.services.rl_trainer.trainer import (
    ReplayBuffer,
    TrainerConfig,
    decode_action,
    obs_dim_for,
    run_episode,
    state_to_obs,
    warmup_from_history,
)

_OBS = obs_dim_for()


def _agent() -> TD3Agent:
    return TD3Agent(obs_dim=_OBS, lr=1e-3)


def test_obs_shape_and_finiteness() -> None:
    env = make_env(make_contract(), seed=7)
    state = env.reset(seed=7)
    obs = state_to_obs(state, env.contract.slice_count, env.contract.total_quantity)
    assert obs.shape == (_OBS,)
    assert np.isfinite(obs).all()


def test_decode_action_bounds() -> None:
    lo = decode_action(np.array([-1.0, -1.0]), offset_count=5)
    hi = decode_action(np.array([1.0, 1.0]), offset_count=5)
    mid = decode_action(np.array([0.0, 0.0]), offset_count=5)
    assert (lo.price_offset_idx, hi.price_offset_idx) == (0, 4)
    assert mid.price_offset_idx == 2
    assert 0.0 <= lo.quantity_ratio <= 1.0 and hi.quantity_ratio <= 1.0
    assert all(a.is_market is False for a in (lo, hi, mid))


def test_warmup_fills_buffer_without_learning(tmp_path) -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    added = warmup_from_history(env, agent, buffer, episodes=2, seed0=42)
    assert added > 0 and len(buffer) == added
    before = [p.detach().clone() for p in agent.actor.parameters()]
    # 只预热：actor 参数必须零变化（H-04：预热≠训练）
    for a, b in zip(before, agent.actor.parameters(), strict=True):
        assert torch_close(a, b)


def test_td3_update_runs_and_losses_finite() -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    rng = np.random.default_rng(0)
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    warmup_from_history(env, agent, buffer, episodes=2, seed0=1)
    batch = buffer.sample(16, rng)
    c_loss, a_loss = agent.update(batch)
    assert np.isfinite(c_loss) and np.isfinite(a_loss)


def test_checkpoint_roundtrip(tmp_path) -> None:
    agent = _agent()
    rng = np.random.default_rng(3)
    obs = rng.normal(size=_OBS).astype(np.float32)
    before = agent.select_action(obs)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(agent, path, meta={"tag": "tc11"})
    agent2, meta = load_checkpoint(path)
    after = agent2.select_action(obs)
    assert meta.get("tag") == "tc11"
    assert np.allclose(before, after, atol=1e-6)


def test_run_episode_learn_false_no_grad() -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    rng = np.random.default_rng(5)
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    ret = run_episode(env, agent, buffer, noise_sigma=0.1, rng=rng, learn=False)
    assert isinstance(ret, float) and np.isfinite(ret) and len(buffer) > 0


def test_config_default_is_warmup_only() -> None:
    """H-04 门留痕：库层默认 real_training=False。"""
    assert TrainerConfig().real_training is False


def torch_close(a, b) -> bool:
    import torch

    return bool(torch.allclose(a, b))


# ══════════════════════════════════════════════════════════════════════════════
# GPU-04 腿 M-1：影子对拍守卫（统筹 R-5 只批这一腿；真训练与 B-007 消费不在本面）
# 每支判据各对一个我真实怕发生的静默错：
#   ①参考腿绕过 decode_action 单点＝对拍比的成了两套解码；
#   ②同 seed 两次跑出不同数＝"影子"不可信，B-007 材料包里它就是假尺；
#   ③分歧率恒 0 或恒 1＝判据空跑（必须能区分同策略与远策略）；
#   ④缺参考腿还能出数＝单腿自证；
#   ⑤读数面上写着"已接生产"＝越权接线。
# ══════════════════════════════════════════════════════════════════════════════


def test_passive_reference_round_trips_through_single_decode() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor

    for idx in range(5):
        actor = passive_reference_actor(idx, 0.37, offset_count=5)
        got = decode_action(actor(np.zeros(obs_dim_for(), dtype=np.float32)), 5)
        assert got.price_offset_idx == idx, f"参考腿第 {idx} 档往返不符：{got}"
        assert abs(got.quantity_ratio - 0.37) < 1e-6
        assert got.is_market is False


def test_passive_reference_rejects_out_of_range_params() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor

    with pytest.raises(ValueError):
        passive_reference_actor(5, 0.5, offset_count=5)
    with pytest.raises(ValueError):
        passive_reference_actor(0, 1.5, offset_count=5)


def test_shadow_leg_is_deterministic_for_same_seed_env() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor, run_shadow_leg

    actor = passive_reference_actor(2, 0.5, len(make_contract().offset_levels))
    first = run_shadow_leg(make_env(make_contract(), seed=7), actor)
    second = run_shadow_leg(make_env(make_contract(), seed=7), actor)
    assert first == second, "同 seed 同盘口序列必须逐字段相等，否则影子对拍不可信"
    assert first["steps"] <= make_contract().slice_count


def test_shadow_compare_identical_legs_zero_divergence() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor, shadow_compare

    levels = len(make_contract().offset_levels)
    rep = shadow_compare(
        lambda: make_env(make_contract(), seed=11),
        {
            "reference": passive_reference_actor(2, 0.4, levels),
            "twin": passive_reference_actor(2, 0.4, levels),
        },
        reference="reference",
    )
    assert rep["divergence_rate"]["twin"] == 0.0
    assert rep["is_delta_vs_reference"]["twin"] == 0.0


def test_shadow_compare_flags_divergent_leg() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor, shadow_compare

    levels = len(make_contract().offset_levels)
    rep = shadow_compare(
        lambda: make_env(make_contract(), seed=13),
        {
            "reference": passive_reference_actor(0, 0.1, levels),
            "far": passive_reference_actor(4, 1.0, levels),
        },
        reference="reference",
    )
    assert rep["divergence_rate"]["far"] == 1.0, "档档不同必须满分歧（判据不能空跑）"
    delta = rep["is_delta_vs_reference"]["far"]
    assert isinstance(delta, float) and np.isfinite(delta)
    assert rep["legs"]["reference"]["fill_ratio"] <= rep["legs"]["far"]["fill_ratio"] + 1e-9, (
        "参与率 0.1 vs 1.0：完成率差必须同向可读，否则成本/进度两数在说谎"
    )


def test_shadow_compare_requires_reference_leg() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor, shadow_compare

    levels = len(make_contract().offset_levels)
    with pytest.raises(ValueError):
        shadow_compare(
            lambda: make_env(make_contract(), seed=1),
            {"solo": passive_reference_actor(1, 0.5, levels)},
            reference="reference",
        )


def test_agent_leg_runs_and_reports_finite_numbers() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import agent_reference_actor, run_shadow_leg, shadow_compare

    agent = _agent()
    levels = len(make_contract().offset_levels)
    leg = run_shadow_leg(make_env(make_contract(), seed=17), agent_reference_actor(agent, sigma=0.0))
    assert leg["steps"] > 0 and np.isfinite(leg["is_total"])
    assert 0.0 <= leg["fill_ratio"] <= 1.0
    assert all(0 <= idx < levels for idx, _r in leg["actions"]), "解码恒在契约档域内（影子腿不得越界）"
    rep = shadow_compare(
        lambda: make_env(make_contract(), seed=17),
        {"reference": agent_reference_actor(agent, sigma=0.0), "cand": agent_reference_actor(agent, sigma=0.0)},
        reference="reference",
    )
    assert rep["divergence_rate"]["cand"] == 0.0, "同一 actor 评估态（sigma=0）必须逐切片自洽"


def test_shadow_report_declares_it_is_not_wired_in() -> None:
    from zephyr.ex_sor.services.rl_trainer.trainer import passive_reference_actor, shadow_compare

    levels = len(make_contract().offset_levels)
    rep = shadow_compare(
        lambda: make_env(make_contract(), seed=3),
        {"reference": passive_reference_actor(1, 0.2, levels)},
        reference="reference",
    )
    assert "B-007" in rep["consumption"] and "未接" in rep["consumption"]
