# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md
# [MODULE] zephyr.intelligence.reflexion.roles
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.reflexion.reflection_schema; zephyr.intelligence.reflexion.l1_reflector
# [CONSUMERS] zephyr.intelligence.reflexion.batch_runner
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三角色逻辑分离(Actor 产轨迹/Evaluator 按量规评估/SelfReflection 产反思记录); 评估报告字段完整(score/dimensions/defects); 接口协议化(Protocol 结构化子类型)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EvaluationReport 字段不完整 → ValueError; schema 层 ReflectionSchemaError(ValueError) 上抛
# [TESTS] tests/intelligence/test_reflexion_phase0.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
三角色骨架 —— 12号文 §3.2/§4.2 P0-2(Actor→Evaluator→SelfReflection)。

定位: 三角色是逻辑角色而非三个常驻进程(12号文 §3.2)——同一 LLM 会话内可分步
扮演, 也可经模型路由把 Evaluator 分派给低成本模型。接口协议化(typing.Protocol,
结构化子类型), 任何满足协议的可调用体皆可充当角色。

角色分工:
  - Actor: 执行任务产出执行轨迹(Trajectory, 步序列+最终产出+成败标记);
  - Evaluator: 按结构化量规(rubric)评估轨迹, 产出评估报告(EvaluationReport,
    字段完整=score/dimensions/defects, 格式对齐 13号文 §3.5 接口假设, 12号文 §4.6);
  - SelfReflection: 消费评估报告+执行轨迹, 产出结构化反思记录(ReflectionRecord)。

内置合成实现(SyntheticActor/RubricEvaluator/L1SelfReflection)仅用于骨架跑通与
测试——同一任务分角色跑通全流程(P0-2 验收); 生产实现由后续 Phase 注入。

Why 分离而非单角色自问自答(12号文 §3.2): 生成与评估共用同一上下文会系统性高估
自身产出; Evaluator 独立上下文+结构化量规是廉价的对抗性。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: task 参数
#   fields: 参数 task，类型注解 TaskSpec
#   code: roles.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: actor 参数
#   fields: 参数 actor，类型注解 ActorProtocol
#   code: roles.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: evaluator 参数
#   fields: 参数 evaluator，类型注解 EvaluatorProtocol
#   code: roles.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: reflector 参数
#   fields: 参数 reflector，类型注解 SelfReflectionProtocol
#   code: roles.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ActorProtocol
#   name_en: ActorProtocol
#   intro: Actor: 执行任务产出轨迹。
#   desc: Actor: 执行任务产出轨迹。；公共方法（定义序）: run；源码 L195-L198
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② EvaluatorProtocol
#   name_en: EvaluatorProtocol
#   intro: Evaluator: 按量规评估轨迹产出评估报告。
#   desc: Evaluator: 按量规评估轨迹产出评估报告。；公共方法（定义序）: evaluate；源码 L202-L205
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ SelfReflectionProtocol
#   name_en: SelfReflectionProtocol
#   intro: SelfReflection: 消费轨迹+评估报告产出反思记录。
#   desc: SelfReflection: 消费轨迹+评估报告产出反思记录。；公共方法（定义序）: reflect；源码 L209-L216
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ SyntheticActor
#   name_en: SyntheticActor
#   intro: 合成 Actor: 规则化产出固定三步轨迹;
#   desc: 合成 Actor: 规则化产出固定三步轨迹; params["inject_failure"]=类别关键词 可注入失败(如 "数据缺失" → 末步失败+error 文本), 用于…；公共方法（定义序）: run；源码…
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ RubricEvaluator
#   name_en: RubricEvaluator
#   intro: 量规 Evaluator: 三维量规(完整性/逻辑性/契约符合)打分, 缺陷=失败步+错误文本。
#   desc: 量规 Evaluator: 三维量规(完整性/逻辑性/契约符合)打分, 缺陷=失败步+错误文本。；公共方法（定义序）: evaluate；源码 L267-L297
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ L1SelfReflection
#   name_en: L1SelfReflection
#   intro: SelfReflection 角色: 委托 L1Reflector 产出反思记录(规则化归因 MVP)。
#   desc: SelfReflection 角色: 委托 L1Reflector 产出反思记录(规则化归因 MVP)。；公共方法（定义序）: reflect；源码 L300-L311
#   inputs: reflector
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ run_three_role_flow
#   name_en: run_three_role_flow
#   intro: 三角色全流程: Actor 执行 → Evaluator 评估 → SelfReflection 反思。
#   desc: 三角色全流程: Actor 执行 → Evaluator 评估 → SelfReflection 反思。 同一任务分角色跑通(12号文 §4.2 P0-2 验收口径); 返回三角…；源码 L314-L327
#   inputs: task actor evaluator reflector
#   outputs: tuple[Trajectory, EvaluationReport, Ref…
#   （注：A7 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[Trajectory, EvaluationReport, Ref…
#   name_en: tuple[Trajectory, EvaluationReport, Ref…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.intelligence.reflexion.batch_runner
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from zephyr.intelligence.reflexion.l1_reflector import L1Reflector
from zephyr.intelligence.reflexion.reflection_schema import ReflectionRecord

# ── 数据载体(三角色间流转的结构化对象) ──


@dataclass(frozen=True)
class TaskSpec:
    """任务规格: Actor 的输入。"""

    task_id: str
    description: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrajectoryStep:
    """轨迹步: 一次动作及其观测。"""

    step_index: int
    action: str
    observation: str


@dataclass(frozen=True)
class Trajectory:
    """执行轨迹: Actor 的产出(步序列+最终产出+成败标记+错误文本)。"""

    task_id: str
    steps: list[TrajectoryStep]
    final_output: str
    succeeded: bool
    error: str = ""


@dataclass(frozen=True)
class EvaluationReport:
    """结构化评估报告: Evaluator 的产出(字段完整=score/dimensions/defects)。"""

    task_id: str
    score: float  # 总分 [0,1]
    dimensions: dict[str, float]  # 量规维度分(非空, 各 [0,1])
    defects: list[str]  # 缺陷清单(无缺陷=空表)

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("EvaluationReport.task_id 缺失或为空(字段不完整拒收)")
        if not isinstance(self.score, (int, float)) or not 0.0 <= float(self.score) <= 1.0:
            raise ValueError(f"EvaluationReport.score 须为 [0,1] 数值: {self.score!r}")
        if not self.dimensions:
            raise ValueError("EvaluationReport.dimensions 为空(字段不完整拒收)")
        for name, value in self.dimensions.items():
            if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"EvaluationReport.dimensions[{name!r}] 须为 [0,1] 数值: {value!r}")
        if not isinstance(self.defects, list):
            raise ValueError("EvaluationReport.defects 须为 list(字段不完整拒收)")


# ── 角色协议(接口协议化: 结构化子类型, 满足签名即可充当) ──


@runtime_checkable
class ActorProtocol(Protocol):
    """Actor: 执行任务产出轨迹。"""

    def run(self, task: TaskSpec) -> Trajectory: ...


@runtime_checkable
class EvaluatorProtocol(Protocol):
    """Evaluator: 按量规评估轨迹产出评估报告。"""

    def evaluate(self, trajectory: Trajectory) -> EvaluationReport: ...


@runtime_checkable
class SelfReflectionProtocol(Protocol):
    """SelfReflection: 消费轨迹+评估报告产出反思记录。"""

    def reflect(
        self,
        trajectory: Trajectory,
        report: EvaluationReport,
    ) -> ReflectionRecord: ...


# ── 合成实现(骨架跑通/测试用; 生产实现后续 Phase 注入) ──


class SyntheticActor:
    """合成 Actor: 规则化产出固定三步轨迹; params["inject_failure"]=类别关键词
    可注入失败(如 "数据缺失" → 末步失败+error 文本), 用于构造失败轨迹样例。
    """

    def run(self, task: TaskSpec) -> Trajectory:
        steps = [
            TrajectoryStep(
                step_index=0,
                action="检索资料",
                observation=f"围绕「{task.description}」完成资料检索, 证据齐备",
            ),
            TrajectoryStep(
                step_index=1,
                action="形成假设",
                observation="形成候选假设: 盈利质量因子与次季收益正相关",
            ),
            TrajectoryStep(
                step_index=2,
                action="撰写产出",
                observation="完成产出撰写并通过自检",
            ),
        ]
        inject_failure = str(task.params.get("inject_failure", "") or "")
        if inject_failure:
            steps[2] = TrajectoryStep(
                step_index=2,
                action="撰写产出",
                observation=f"产出撰写中止: {inject_failure}",
            )
            return Trajectory(
                task_id=task.task_id,
                steps=steps,
                final_output="",
                succeeded=False,
                error=f"任务执行失败: {inject_failure}",
            )
        return Trajectory(
            task_id=task.task_id,
            steps=steps,
            final_output=f"「{task.description}」假设初稿: 盈利质量因子(应计利润率为代理)与次季收益正相关, 待回测验证",
            succeeded=True,
        )


class RubricEvaluator:
    """量规 Evaluator: 三维量规(完整性/逻辑性/契约符合)打分, 缺陷=失败步+错误文本。"""

    DIMENSIONS: tuple[str, ...] = ("完整性", "逻辑性", "契约符合")

    def evaluate(self, trajectory: Trajectory) -> EvaluationReport:
        failed_steps = [s for s in trajectory.steps if "中止" in s.observation]
        if trajectory.succeeded and not failed_steps:
            dimensions = {name: 0.9 for name in self.DIMENSIONS}
            return EvaluationReport(
                task_id=trajectory.task_id,
                score=round(sum(dimensions.values()) / len(dimensions), 4),
                dimensions=dimensions,
                defects=[],
            )
        # 失败轨迹: 完整性按完成步比例, 逻辑性/契约符合降档
        completed = len(trajectory.steps) - len(failed_steps)
        dimensions = {
            "完整性": round(completed / max(len(trajectory.steps), 1), 4),
            "逻辑性": 0.3,
            "契约符合": 0.0 if not trajectory.final_output else 0.5,
        }
        defects = [f"step[{s.step_index}] {s.observation}" for s in failed_steps]
        if trajectory.error:
            defects.append(trajectory.error)
        return EvaluationReport(
            task_id=trajectory.task_id,
            score=round(sum(dimensions.values()) / len(dimensions), 4),
            dimensions=dimensions,
            defects=defects,
        )


class L1SelfReflection:
    """SelfReflection 角色: 委托 L1Reflector 产出反思记录(规则化归因 MVP)。"""

    def __init__(self, reflector: L1Reflector | None = None) -> None:
        self._reflector = reflector or L1Reflector()

    def reflect(
        self,
        trajectory: Trajectory,
        report: EvaluationReport,
    ) -> ReflectionRecord:
        return self._reflector.reflect(trajectory, report)


def run_three_role_flow(
    task: TaskSpec,
    actor: ActorProtocol,
    evaluator: EvaluatorProtocol,
    reflector: SelfReflectionProtocol,
) -> tuple[Trajectory, EvaluationReport, ReflectionRecord]:
    """三角色全流程: Actor 执行 → Evaluator 评估 → SelfReflection 反思。

    同一任务分角色跑通(12号文 §4.2 P0-2 验收口径); 返回三角色各自产出。
    """
    trajectory = actor.run(task)
    report = evaluator.evaluate(trajectory)
    record = reflector.reflect(trajectory, report)
    return trajectory, report, record
