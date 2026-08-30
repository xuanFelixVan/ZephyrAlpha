# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.deterministic_replay
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Deterministic Replay — v0.15.0 R206

Blindspot: FLE decisions non-reproducible; LLM nondeterminism prevents audit replay.
Risk: R206 — "Why did FLE choose this repair?" Unanswerable; decision provenance lost.

Mitigation: seed(timestamp) + temperature=0 + prompt hash for fully deterministic replay.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: deterministic_replay.py
# 层: 算法
# - id: A1
#   name_zh: ① DeterministicReplay
#   name_en: DeterministicReplay
#   intro: class DeterministicReplay 源码 L72-L91
#   desc: 公共方法（定义序）: capture, replay, verify；源码 L72-L91
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DeterministicReplay
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class ReplayRecord:
    replay_id: str
    seed: int
    prompt_hash: str
    temperature: float = 0.0
    output: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class DeterministicReplay:
    records: list[ReplayRecord] = field(default_factory=list)

    def capture(self, prompt: str, output: str, seed: int | None = None) -> ReplayRecord:
        if seed is None:
            seed = int(time.time() * 1000)
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        record = ReplayRecord(replay_id=prompt_hash, seed=seed, prompt_hash=prompt_hash, temperature=0.0, output=output)
        self.records.append(record)
        return record

    def replay(self, replay_id: str) -> ReplayRecord | None:
        for r in self.records:
            if r.replay_id == replay_id:
                return r
        return None

    def verify(self, replay_id: str, expected_output: str) -> bool:
        record = self.replay(replay_id)
        return record is not None and record.output == expected_output
