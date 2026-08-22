# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md
# [MODULE] zephyr.intelligence.reflexion.l1_reflector
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.reflexion.reflection_schema; zephyr.intelligence.reflexion.roles(仅 TYPE_CHECKING 类型引用)
# [CONSUMERS] zephyr.intelligence.reflexion.roles; zephyr.intelligence.reflexion.batch_runner
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] L1 只规则化归因(关键词词表匹配, 不调 LLM); 失败记录归因类别与改进建议恒非空; 每条建议锚定归因类别+轨迹片段
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReflectionSchemaError(ValueError, 由 schema 层上抛); 归因规则表为空 → ValueError
# [TESTS] tests/intelligence/test_reflexion_phase0.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""L1 单轨迹反思器 —— 12号文 §4.2 P0-3(执行层, 触发频率最高/成本最低)。

定位: 单次任务结束后对该次执行轨迹做结构化复盘——输入失败轨迹(+评估报告)
→ 归因分类 + 改进建议 → 产出 L1 反思记录(ReflectionRecord)。

GP0 手动形态 = 规则化归因 MVP: 归因走关键词词表匹配(config 化, 构造可注入),
不做 LLM 自由文本(12号文 §5-8 不做自由文本感想式反思; LLM 增强留 Phase 1)。

归因词表(默认, 可注入覆盖): 数据错误 / 逻辑错误 / 契约违反 / 环境问题 /
需求误解 / 未知(兜底)。匹配顺序 = 规则表插入序(先命中先判), 命中证据=
首个含关键词的轨迹步(evidence_ref=step[i]), 无命中归"未知"并锚定末步。

改进建议: 每类别内置规则化建议模板, 恒非空且每条锚定归因类别+证据片段
(12号文 §4.2 P0-3 验收口径: 非空且可追溯到轨迹片段)。

不做什么: 不做 L2 同类任务归纳(N=5 累积, Phase 2); 不做 L3 跨任务(远期);
不做反思触发裁决(归 Phase 1 ReflCtrl 频率闸门)。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Final

from zephyr.intelligence.reflexion.reflection_schema import (
    ImprovementSuggestion,
    ReflectionRecord,
)

if TYPE_CHECKING:  # 仅类型注解用(运行时鸭子类型读字段, 防 roles↔reflector 循环)
    from zephyr.intelligence.reflexion.roles import EvaluationReport, Trajectory

# ── 归因类别词表(config 化: L1Reflector(rules=...) 可注入覆盖) ──

CATEGORY_DATA_ERROR: Final[str] = "数据错误"
CATEGORY_LOGIC_ERROR: Final[str] = "逻辑错误"
CATEGORY_CONTRACT_VIOLATION: Final[str] = "契约违反"
CATEGORY_ENVIRONMENT_ERROR: Final[str] = "环境问题"
CATEGORY_REQUIREMENT_MISUNDERSTANDING: Final[str] = "需求误解"
CATEGORY_UNKNOWN: Final[str] = "未知"

DEFAULT_ATTRIBUTION_RULES: Final[dict[str, tuple[str, ...]]] = {
    CATEGORY_DATA_ERROR: (
        "数据缺失", "数据错误", "数据口径", "空值", "nan", "缺失值",
        "未来函数", "前视", "lookahead", "脏数据",
    ),
    CATEGORY_LOGIC_ERROR: (
        "逻辑错误", "推导矛盾", "因果倒置", "假设不成立", "自相矛盾", "逻辑漏洞",
    ),
    CATEGORY_CONTRACT_VIOLATION: (
        "契约违反", "契约", "schema", "字段缺失", "格式不符", "类型不符",
        "contract", "接口不符",
    ),
    CATEGORY_ENVIRONMENT_ERROR: (
        "环境问题", "依赖缺失", "连接失败", "超时", "timeout", "network",
        "importerror", "权限不足", "资源不足",
    ),
    CATEGORY_REQUIREMENT_MISUNDERSTANDING: (
        "需求误解", "偏离题意", "答非所问", "理解偏差", "需求偏差",
    ),
}

# ── 规则化建议模板(每类别 ≥1 条, 恒非空; {evidence} 占位替换为轨迹片段引用) ──

DEFAULT_SUGGESTION_TEMPLATES: Final[dict[str, tuple[str, ...]]] = {
    CATEGORY_DATA_ERROR: (
        "复核 {evidence} 处输入数据源与字段口径, 补齐缺失值/剔除脏数据后重跑该步",
        "为 {evidence} 步增加数据契约前置校验(非空/取值域), 失败即中止而非带病续跑",
    ),
    CATEGORY_LOGIC_ERROR: (
        "拆解 {evidence} 处推理链, 逐环核对因果方向与前提假设, 修正矛盾环后重跑",
    ),
    CATEGORY_CONTRACT_VIOLATION: (
        "对照输出契约逐字段核验 {evidence} 处产出(字段/类型/格式), 修齐后重跑该步",
    ),
    CATEGORY_ENVIRONMENT_ERROR: (
        "修复 {evidence} 处环境问题(依赖/连接/资源)后原样重跑, 不改任务逻辑",
    ),
    CATEGORY_REQUIREMENT_MISUNDERSTANDING: (
        "回读任务描述并对照 {evidence} 处产出核对题意, 明确验收口径后重做该步",
    ),
    CATEGORY_UNKNOWN: (
        "人工复核 {evidence} 起全轨迹, 定位根因后将该失败模式补入归因词表",
    ),
}


@dataclass(frozen=True)
class AttributionResult:
    """归因结果: 类别 + 命中证据轨迹步下标(未命中=-1, 锚定末步)。"""

    category: str
    evidence_step_index: int  # 轨迹步下标; -1 表示无关键词命中(锚定末步)


class L1Reflector:
    """L1 单轨迹反思器(规则化归因 MVP, 不调 LLM)。"""

    DEFAULT_RULES: ClassVar[dict[str, tuple[str, ...]]] = DEFAULT_ATTRIBUTION_RULES

    def __init__(
        self,
        rules: dict[str, tuple[str, ...]] | None = None,
        suggestion_templates: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self._rules = rules if rules is not None else dict(DEFAULT_ATTRIBUTION_RULES)
        if not self._rules:
            raise ValueError("归因规则表为空(fail-closed): 至少配置一类归因关键词")
        self._templates = (
            suggestion_templates
            if suggestion_templates is not None
            else dict(DEFAULT_SUGGESTION_TEMPLATES)
        )

    @property
    def categories(self) -> tuple[str, ...]:
        return tuple(self._rules) + (CATEGORY_UNKNOWN,)

    def classify(
        self,
        trajectory: Trajectory,
        report: EvaluationReport | None = None,
    ) -> AttributionResult:
        """归因分类: 关键词词表匹配(error 文本→缺陷清单→轨迹步观测), 先命中先判。"""
        haystacks: list[tuple[int, str]] = []  # (轨迹步下标, 小写文本); -1=非步文本
        error_text = (getattr(trajectory, "error", "") or "").lower()
        if error_text:
            haystacks.append((-1, error_text))
        if report is not None:
            for defect in getattr(report, "defects", []) or []:
                haystacks.append((-1, str(defect).lower()))
        for idx, step in enumerate(getattr(trajectory, "steps", []) or []):
            observation = str(getattr(step, "observation", "") or "").lower()
            if observation:
                haystacks.append((idx, observation))
        # 按规则表插入序逐类别扫描, 首个命中即定类(可审计: 哪条规则触发可答)
        for category, keywords in self._rules.items():
            for step_idx, text in haystacks:
                if any(kw.lower() in text for kw in keywords):
                    return AttributionResult(category=category, evidence_step_index=step_idx)
        return AttributionResult(category=CATEGORY_UNKNOWN, evidence_step_index=-1)

    def suggest(
        self,
        attribution: AttributionResult,
        trajectory: Trajectory,
    ) -> list[ImprovementSuggestion]:
        """按归因类别产出改进建议(恒非空, 每条锚定类别+轨迹片段)。"""
        steps = getattr(trajectory, "steps", []) or []
        anchor_idx = attribution.evidence_step_index
        if anchor_idx < 0:
            # 无命中/非步文本命中 → 锚定末步(空轨迹锚定 step[-1] 占位)
            anchor_idx = len(steps) - 1 if steps else -1
        evidence_ref = f"step[{anchor_idx}]"
        templates = self._templates.get(
            attribution.category, self._templates[CATEGORY_UNKNOWN]
        )
        return [
            ImprovementSuggestion(
                category=attribution.category,
                suggestion=template.format(evidence=evidence_ref),
                evidence_ref=evidence_ref,
            )
            for template in templates
        ]

    def reflect(
        self,
        trajectory: Trajectory,
        report: EvaluationReport | None = None,
        trajectory_ref: str = "",
    ) -> ReflectionRecord:
        """单轨迹复盘主入口: 失败轨迹 → 归因+建议 → L1 反思记录。"""
        succeeded = bool(getattr(trajectory, "succeeded", False))
        task_id = str(getattr(trajectory, "task_id", "") or "")
        if succeeded:
            # 成功轨迹: 仅记录成功事实(决策矩阵"连续优秀→仅记录成功模式"的载体,
            # ReflCtrl 频率闸门归 Phase 1, 本层不做跳过裁决)
            return ReflectionRecord(
                reflection_id=f"rfl-{uuid.uuid4().hex[:12]}",
                task_id=task_id,
                trajectory_ref=trajectory_ref or task_id,
                outcome="success",
            )
        attribution = self.classify(trajectory, report)
        suggestions = self.suggest(attribution, trajectory)
        return ReflectionRecord(
            reflection_id=f"rfl-{uuid.uuid4().hex[:12]}",
            task_id=task_id,
            trajectory_ref=trajectory_ref or task_id,
            outcome="failure",
            failure_category=attribution.category,
            improvement_suggestions=suggestions,
        )
