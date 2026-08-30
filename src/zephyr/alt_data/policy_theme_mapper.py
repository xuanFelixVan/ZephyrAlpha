# [BLUEPRINT] MOD-ALT-005 | docs/03_modules/_domain_alt_data/policy_theme_mapper/blueprint.md
# [MODULE] zephyr.alt_data.policy_theme_mapper
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；llm_classifier 全注入）
# [CONSUMERS] 运行时装配批（政策类新闻接 data 域采集族产物 / llm_classifier 接 api_llm_pool·llm_gateway；主题热度与受益/受损清单入信号）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；单条非法Fail-Closed到条；PIT严格（publish_date>as_of→rejected）；热度恒≥0且age_days=0时weight=1.0；LLM输出结构/值域非法必回落规则并llm_invalid留痕，不出伪LLM结论；classifier字段如实记录rule|llm；frozen dataclass asdict JSON可序列化；同输入必同输出；仅信号输入语义无下单含义
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/policy_theme_mapper/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] news_id/title空白/publish_date非法或晚于as_of→InvalidPolicyNewsError（单条Fail-Closed）；主题库theme_id重复/关键词空/half_life_days非正/llm_classifier非callable→InvalidPolicyThemeConfigError（构造期Fail-Closed）；llm_classifier运行期异常→回落规则留痕不阻断
# [TESTS] tests/alt_data/test_policy_theme_mapper.py
# [A_module] module_id=MOD-ALT-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



PolicyThemeMapper — 政策主题映射器（MOD-ALT-005）

B1-00123（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，D-ALT-19）：政策主题库（货币/
产业/监管/财政/贸易）+ 规则关键词主题归类（可选 llm_classifier 注入升级，
输出非法回落规则留痕）+ 主题→申万行业映射表（受益/受损）+ 影响半衰期
参数 → 主题热度（0.5**(age/half_life) 时间衰减加总）与受益/受损清单，
输出入信号。

查重裁定：news_impact_grader（MOD-NLP-IMPACT-001）=单新闻 A/B/C 影响分级
+热点聚类计数（分级面，无主题→行业映射与半衰期）；sector_fund_flow_collector
（MOD-L00-004）=板块资金流采集；api_llm_pool=LLM 池化治理（本件零密钥零直连，
llm_classifier 注入委托）。本模块为政策主题→行业映射与影响持续度评估判定
核心，口径不重复。仅信号输入语义，无下单含义。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: theme_library 参数
#   fields: 参数 theme_library（无注解）
#   code: policy_theme_mapper.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: llm_classifier 参数
#   fields: 参数 llm_classifier（无注解）
#   code: policy_theme_mapper.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PolicyThemeMapper
#   name_en: PolicyThemeMapper
#   intro: 政策主题映射器（主题归类 + 半衰期热度 + 受益/受损清单判定核心）。
#   desc: 政策主题映射器（主题归类 + 半衰期热度 + 受益/受损清单判定核心）。 Args: theme_library: 主题库（None=DEFAULT_THEME_LIBRARY）…；公共方法（定义序）: theme_l…
#   inputs: theme_library llm_classifier
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: PolicyThemeMapper
#   downstream: 运行时装配批（政策类新闻接 data 域采集族产物 / llm_classifier 接 api_llm_pool·llm_gateway；主题热度与受益/受…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Optional

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "DEFAULT_THEME_LIBRARY",
    "InvalidPolicyNewsError",
    "InvalidPolicyThemeConfigError",
    "PolicyNewsItem",
    "PolicyTheme",
    "PolicyThemeMapper",
    "PolicyThemeReport",
    "ThemeHeat",
]


class InvalidPolicyNewsError(ZephyrBaseError):
    """政策新闻输入行非法（Fail-Closed 到条）。"""


class InvalidPolicyThemeConfigError(ZephyrBaseError):
    """主题库/配置非法（构造期 Fail-Closed）。"""


@dataclass(frozen=True)
class PolicyTheme:
    """政策主题定义（frozen；theme→申万行业映射表条目）。"""

    theme_id: str
    keywords: tuple[str, ...]
    half_life_days: int
    beneficiary_industries: tuple[str, ...]  # 受益行业（申万口径名称）
    damaged_industries: tuple[str, ...]  # 受损行业


DEFAULT_THEME_LIBRARY: Final[tuple[PolicyTheme, ...]] = (
    PolicyTheme(
        theme_id="货币政策",
        keywords=("降准", "降息", "LPR", "MLF", "逆回购", "存款利率", "流动性投放"),
        half_life_days=20,
        beneficiary_industries=("银行", "非银金融", "房地产"),
        damaged_industries=(),
    ),
    PolicyTheme(
        theme_id="产业政策",
        keywords=("产业规划", "补贴", "专精特新", "首台套", "产业链政策", "扶持"),
        half_life_days=40,
        beneficiary_industries=("半导体", "新能源", "高端装备"),
        damaged_industries=(),
    ),
    PolicyTheme(
        theme_id="监管政策",
        keywords=("监管", "处罚", "立案", "规范", "反垄断", "退市"),
        half_life_days=30,
        beneficiary_industries=(),
        damaged_industries=("非银金融", "房地产", "互联网"),
    ),
    PolicyTheme(
        theme_id="财政政策",
        keywords=("专项债", "减税", "基建", "财政刺激", "以旧换新"),
        half_life_days=35,
        beneficiary_industries=("建筑", "建材", "工程机械"),
        damaged_industries=(),
    ),
    PolicyTheme(
        theme_id="贸易政策",
        keywords=("关税", "出口管制", "反倾销", "贸易摩擦", "出口退税"),
        half_life_days=25,
        beneficiary_industries=("国产替代", "农业"),
        damaged_industries=("出口链", "航运"),
    ),
)


@dataclass(frozen=True)
class PolicyNewsItem:
    """政策类新闻输入（frozen）。"""

    news_id: str
    title: str
    text: str
    publish_date: datetime.date
    source: str

    def __post_init__(self) -> None:
        for name in ("news_id", "title"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise InvalidPolicyNewsError(f"{name} 不能为空: {v!r}")
        if not isinstance(self.publish_date, datetime.date) or isinstance(self.publish_date, datetime.datetime):
            raise InvalidPolicyNewsError(f"publish_date 必须为 date: {type(self.publish_date).__name__}")
        object.__setattr__(self, "news_id", self.news_id.strip())
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(self, "text", self.text if isinstance(self.text, str) else "")
        object.__setattr__(self, "source", self.source if isinstance(self.source, str) else "")


@dataclass(frozen=True)
class ThemeHeat:
    """主题热度输出（frozen）。"""

    theme_id: str
    heat: float
    news_count: int
    beneficiary_industries: tuple[str, ...]
    damaged_industries: tuple[str, ...]


@dataclass(frozen=True)
class PolicyThemeReport:
    """批量映射报告（frozen；beneficiary/damaged_list 为 (行业, heat) 降序）。"""

    items_in: int
    accepted: int
    rejected: int
    unmatched: int
    themes: tuple[ThemeHeat, ...]
    beneficiary_list: tuple[tuple[str, float], ...]
    damaged_list: tuple[tuple[str, float], ...]
    llm_invalid: int
    errors: tuple[tuple[int, str], ...]


def _validate_library(library: Sequence[PolicyTheme]) -> tuple[PolicyTheme, ...]:
    if not library:
        raise InvalidPolicyThemeConfigError("theme_library 不能为空")
    seen: set[str] = set()
    for theme in library:
        if not isinstance(theme, PolicyTheme):
            raise InvalidPolicyThemeConfigError(f"主题条目类型非法: {type(theme).__name__}")
        if not theme.theme_id or not theme.theme_id.strip():
            raise InvalidPolicyThemeConfigError("theme_id 不能为空")
        if theme.theme_id in seen:
            raise InvalidPolicyThemeConfigError(f"theme_id 重复: {theme.theme_id}")
        seen.add(theme.theme_id)
        if not theme.keywords or any(not k.strip() for k in theme.keywords):
            raise InvalidPolicyThemeConfigError(f"{theme.theme_id} keywords 必须非空且无空白项")
        if (
            isinstance(theme.half_life_days, bool)
            or not isinstance(theme.half_life_days, int)
            or theme.half_life_days <= 0
        ):
            raise InvalidPolicyThemeConfigError(f"{theme.theme_id} half_life_days 必须为正 int: {theme.half_life_days}")
    return tuple(library)


class PolicyThemeMapper:
    """政策主题映射器（主题归类 + 半衰期热度 + 受益/受损清单判定核心）。

    Args:
        theme_library: 主题库（None=DEFAULT_THEME_LIBRARY）
        llm_classifier: item -> Mapping{"theme_id": str|None} 注入升级；
            输出结构非法/未知主题 → 回落规则并 llm_invalid 留痕；运行期异常
            同回落不阻断。
    """

    def __init__(
        self,
        theme_library: Sequence[PolicyTheme] | None = None,
        llm_classifier: Callable[[PolicyNewsItem], Mapping[str, object]] | None = None,
    ) -> None:
        self._library = _validate_library(DEFAULT_THEME_LIBRARY if theme_library is None else theme_library)
        if llm_classifier is not None and not callable(llm_classifier):
            raise InvalidPolicyThemeConfigError(
                f"llm_classifier 必须为 callable 或 None: {type(llm_classifier).__name__}"
            )
        self._llm_classifier = llm_classifier
        self._by_id: dict[str, PolicyTheme] = {t.theme_id: t for t in self._library}

    @property
    def theme_library(self) -> tuple[PolicyTheme, ...]:
        return self._library

    def _rule_classify(self, item: PolicyNewsItem) -> str | None:
        haystack = f"{item.title}\n{item.text}"
        for theme in self._library:  # 库定义优先序，首中即定
            if any(k in haystack for k in theme.keywords):
                return theme.theme_id
        return None

    def classify_one(self, item: PolicyNewsItem) -> tuple[str | None, str, bool]:
        """单条归类 → (theme_id|None, classifier=rule|llm, llm_invalid)。"""
        if not isinstance(item, PolicyNewsItem):
            raise InvalidPolicyNewsError(f"item 类型非法: {type(item).__name__}")
        if self._llm_classifier is not None:
            try:
                out = self._llm_classifier(item)
                if not isinstance(out, Mapping):
                    # 结构非法 → 回落规则留痕
                    return self._rule_classify(item), "rule", True
                theme_id = out.get("theme_id")
                if theme_id is None:
                    return None, "llm", False
                if isinstance(theme_id, str) and theme_id in self._by_id:
                    return theme_id, "llm", False
                # 未知主题/结构非法 → 回落规则留痕
                return self._rule_classify(item), "rule", True
            except Exception:  # noqa: BLE001 —— 回落规则不阻断
                return self._rule_classify(item), "rule", True
        return self._rule_classify(item), "rule", False

    def map_theme(
        self,
        items: Sequence[PolicyNewsItem | Mapping[str, object]],
        as_of: datetime.date,
    ) -> PolicyThemeReport:
        """批量映射：主题热度（半衰期衰减加总）+ 受益/受损清单（确定性排序）。"""
        if not isinstance(as_of, datetime.date) or isinstance(as_of, datetime.datetime):
            raise InvalidPolicyNewsError(f"as_of 必须为 date: {type(as_of).__name__}")
        heat_by_theme: dict[str, float] = {}
        count_by_theme: dict[str, int] = {}
        errors: list[tuple[int, str]] = []
        accepted = 0
        unmatched = 0
        llm_invalid = 0
        for idx, raw in enumerate(items or []):
            try:
                item = (
                    raw if isinstance(raw, PolicyNewsItem) else PolicyNewsItem(**raw)  # type: ignore[arg-type]
                )
                if item.publish_date > as_of:  # PIT 严格
                    raise InvalidPolicyNewsError(f"publish_date {item.publish_date} 晚于 as_of {as_of}（未来新闻拒绝）")
                theme_id, _classifier, invalid = self.classify_one(item)
                llm_invalid += int(invalid)
                accepted += 1
                if theme_id is None:
                    unmatched += 1
                    continue
                theme = self._by_id[theme_id]
                age_days = (as_of - item.publish_date).days
                weight = 0.5 ** (age_days / theme.half_life_days)
                heat_by_theme[theme_id] = heat_by_theme.get(theme_id, 0.0) + weight
                count_by_theme[theme_id] = count_by_theme.get(theme_id, 0) + 1
            except Exception as exc:  # noqa: BLE001 —— 单条 Fail-Closed 到条
                errors.append((idx, f"{type(exc).__name__}: {exc}"))
        themes = tuple(
            sorted(
                (
                    ThemeHeat(
                        theme_id=tid,
                        heat=heat_by_theme[tid],
                        news_count=count_by_theme[tid],
                        beneficiary_industries=self._by_id[tid].beneficiary_industries,
                        damaged_industries=self._by_id[tid].damaged_industries,
                    )
                    for tid in heat_by_theme
                ),
                key=lambda t: (-t.heat, t.theme_id),
            )
        )
        beneficiary: dict[str, float] = {}
        damaged: dict[str, float] = {}
        for th in themes:
            for ind in th.beneficiary_industries:
                beneficiary[ind] = beneficiary.get(ind, 0.0) + th.heat
            for ind in th.damaged_industries:
                damaged[ind] = damaged.get(ind, 0.0) + th.heat
        return PolicyThemeReport(
            items_in=len(items or []),
            accepted=accepted,
            rejected=len(errors),
            unmatched=unmatched,
            themes=themes,
            beneficiary_list=tuple(sorted(beneficiary.items(), key=lambda kv: (-kv[1], kv[0]))),
            damaged_list=tuple(sorted(damaged.items(), key=lambda kv: (-kv[1], kv[0]))),
            llm_invalid=llm_invalid,
            errors=tuple(errors),
        )
