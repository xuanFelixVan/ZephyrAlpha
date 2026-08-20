# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.adaptation.execution_tuner
# [DOMAIN] D_SHARED
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Execution Tuner — 执行调谐器（token/timeout 自适应）。

依据：
    蓝图 MOD-TASK_SYSTEM §6.7.2 + v0.6.0
    任务卡 TASK-INF-0127

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 任务卡片 task_card 字典
#   fields: task_id + priority(P0/P1/P2) + estimated_tokens + timeout_minutes + assigned_model(可选)
#   code: tune(task_card: dict) / recommend_model(task_card)
# - id: I2
#   name: 默认调谐参数 TuningParams
#   fields: max_tokens=20000 + timeout_minutes=60 + model=deepseek + pipeline=A
#   code: TuningParams L30 / _default_params
# 层: 算法
# - id: A1
#   name_zh: ① 优先级倍率自适应调谐
#   name_en: ExecutionTuner.tune
#   intro: 按任务优先级给token和超时乘倍率，P0放大1.5倍，再封顶防爆，调完记入历史
#   desc: multiplier=PRIORITY_MULTIPLIER(P0=1.5/P1=1.2/P2=1.0) → adjusted=int(估算×multiplier) → tokens封顶max_tokens×2、timeout封顶timeout×3 → 生成ExecutionProfile并append历史
#   inputs: I1 I2
#   outputs: ExecutionProfile(adjusted_tokens/adjusted_timeout/model)
# - id: A2
#   name_zh: ② 模型推荐
#   name_en: ExecutionTuner.recommend_model
#   intro: P0大任推gpt-4，P0小任推gpt-3.5，其余一律deepseek
#   desc: priority==P0且estimated>10000→gpt-4; priority==P0→gpt-3.5-turbo; 否则→deepseek
#   inputs: I1
#   outputs: 模型名字符串
# - id: A3
#   name_zh: ③ 平均调整幅度统计
#   name_en: ExecutionTuner.get_average_adjustment
#   intro: 统计历史上token平均被放大多少倍，没历史就返回1.0
#   desc: mean(adjusted_tokens/max(original_tokens,1)) over _history; 空历史→1.0
#   inputs: A1
#   outputs: 平均调整倍率 float
# 层: 输出
# - id: O1
#   name_zh: 执行画像 ExecutionProfile
#   name_en: ExecutionProfile
#   intro: 含任务ID/优先级/原估算与调整后token和超时/选用模型，供任务系统调度执行
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 模型推荐结果
#   name_en: recommend_model -> str
#   intro: 推荐使用的LLM模型名，供任务分配参考
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> A3
# A1 --> O1
# A2 --> O2
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class TuningParams:
    max_tokens: int = 20000
    timeout_minutes: int = 60
    model: str = "deepseek"
    pipeline: str = "A"


@dataclass
class ExecutionProfile:
    task_id: str
    priority: str
    estimated_tokens: int
    timeout_minutes: int
    adjusted_tokens: int
    adjusted_timeout: int
    model: str


class ExecutionTuner:
    PRIORITY_MULTIPLIER: dict[str, float] = {
        "P0": 1.5,
        "P1": 1.2,
        "P2": 1.0,
    }

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._default_params = TuningParams()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def default_params(self):
        """只读：default_params（Stage 4 公共化）。"""
        return self._default_params

    @default_params.setter
    def default_params(self, value):
        """写入：default_params（Stage 4 公共化）。"""
        self._default_params = value

    @property
    def history(self) -> list[dict[str, Any]]:
        """只读：history（Stage 4 公共化）。"""
        return self._history

    @history.setter
    def history(self, value):
        """写入：history（Stage 4 公共化）。"""
        self._history = value

    def tune(self, task_card: dict[str, Any]) -> ExecutionProfile:
        task_id = task_card.get("task_id", "")
        priority = task_card.get("priority", "P2")
        estimated = task_card.get("estimated_tokens", self._default_params.max_tokens)
        timeout = task_card.get("timeout_minutes", self._default_params.timeout_minutes)

        multiplier = self.PRIORITY_MULTIPLIER.get(priority, 1.0)

        adjusted_tokens = int(estimated * multiplier)
        adjusted_timeout = int(timeout * multiplier)

        adjusted_tokens = min(adjusted_tokens, self._default_params.max_tokens * 2)
        adjusted_timeout = min(adjusted_timeout, self._default_params.timeout_minutes * 3)

        profile = ExecutionProfile(
            task_id=task_id,
            priority=priority,
            estimated_tokens=estimated,
            timeout_minutes=timeout,
            adjusted_tokens=adjusted_tokens,
            adjusted_timeout=adjusted_timeout,
            model=task_card.get("assigned_model", self._default_params.model),
        )

        self._history.append(
            {
                "task_id": task_id,
                "priority": priority,
                "original_tokens": estimated,
                "adjusted_tokens": adjusted_tokens,
            }
        )

        return profile

    def recommend_model(self, task_card: dict[str, Any]) -> str:
        estimated = task_card.get("estimated_tokens", 0)
        priority = task_card.get("priority", "P2")

        if priority == "P0" and estimated > 10000:
            return "gpt-4"
        if priority == "P0":
            return "gpt-3.5-turbo"

        return "deepseek"

    def get_average_adjustment(self) -> float:
        if not self._history:
            return 1.0
        ratios = [h["adjusted_tokens"] / max(h["original_tokens"], 1) for h in self._history]
        return sum(ratios) / len(ratios)
