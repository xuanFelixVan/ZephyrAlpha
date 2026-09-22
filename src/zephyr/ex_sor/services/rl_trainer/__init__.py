# [BLUEPRINT] MOD-EX_SOR | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §rl_trainer
# [MODULE] zephyr.ex_sor.services.rl_trainer
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] torch, zephyr.ex_sor.core.rl_exec_env
# [INVARIANTS] 产物只进模拟盘对拍; H-04 真训练=Owner 门（库层 API 仅供施工验证，生产训练管线触发须 Owner 批）; checkpoint 可恢复
# [MODIFY-GUARD] 签名收口（dataclass config）; 复杂度≤15
# [CONSUMERS] scripts（CLI 训练入口）; tests/ex_sor/test_td3_trainer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 训练面异常 fail-loud（ValueError/RuntimeError）; checkpoint IO 异常 fail-loud
# [TESTS] tests/ex_sor/test_td3_trainer.py
# [TTL] permanent
"""TD3 执行训练器子包（TC-11 件3/st-autolnk 第五棒，2026-09-22）。

TD3 起步实现：actor-critic 双 Q+目标网+延迟策略更新；历史 replay 预热
（RlExecEnv 合成盘口回合）；checkpoint 存取。产物只进模拟盘对拍——
真训练管线触发属 H-04 Owner 门（HANDOFF_20260921_ab_league.md 第 62 行口径）。

# [ALGO_FLOW] external: docs/03_modules/_domain_ex_sor/algo_flow/rl_trainer__init__.yaml
"""


from typing import Final

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

__all__: Final = [
    "TD3Agent",
    "ReplayBuffer",
    "TrainerConfig",
    "decode_action",
    "load_checkpoint",
    "obs_dim_for",
    "run_episode",
    "save_checkpoint",
    "state_to_obs",
    "warmup_from_history",
]
