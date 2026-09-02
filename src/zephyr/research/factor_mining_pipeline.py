# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（缺口总账 GAP-F-43 行；research 域假设/证据族扩展）
# [MODULE] zephyr.research.factor_mining_pipeline
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定同族口径：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE
# [DEPENDENCIES] 无硬依赖（论文搜索/PDF 解析/LLM 提取/沙箱验证全部注入位，测试全 mock，禁真连外网/LLM/DB）
# [CONSUMERS] （候选：研究组·因子库页"因子挖掘"入口，GAP-F-43 消费位；产出草稿由治理流程串行合并入 factor_registry）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 五段链固定：搜索→PDF 解析→LLM 提假说→沙箱验证→入因子库草稿；单篇/单假说失败降级留痕不中断整批（fail-open per item）；入因子库仅产片段登记草稿（status/promotion_stage 恒 candidate，禁直改注册表——治理流程串行合并，同 density_quantile_trainer build_registry_entry 口径）；沙箱 passed 且 ic_mean≥min_ic 才出草稿；LLM 输出仅接受 JSON 数组（name/formula 必填，缺字段剔除留痕）；每篇假说数封顶；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-43 行
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（query 空白/注入件缺失/配置非法，fail-closed）；论文/假说级异常→notes 留痕不抛
# [TESTS] tests/research/test_factor_mining_pipeline.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN_mining | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""LLM 因子挖掘流水线（GAP-F-43，research 域骨架）。

缺口总账 GAP-F-43（研究组·因子库页"因子挖掘"入口）：论文搜索→PDF 解析→
LLM 提因子假说→沙箱验证→入因子库五段链骨架。全部外部能力走注入位
（searcher/pdf_parser/llm_gateway/validator），测试全 mock，禁真连外网/LLM。

接口契约（生产侧接线点）：
    - searcher: ``(query, max_results) -> list[PaperRef]``（外部论文源）
    - pdf_parser: ``PaperRef -> str``（PDF 全文解析）
    - llm_gateway: ``prompt -> str``（模型网关；输出须为 JSON 数组，
      元素 {"name","formula","rationale"}）
    - validator: ``FactorHypothesis -> ValidationReport``（回测沙箱）

入因子库纪律：仅产出 factor_registry 片段登记草稿（candidate），由治理流程
串行合并——本模块禁直改注册表（同 density_quantile_trainer 晋升草稿口径）。

红线：产出物 testing 封顶；任何挖掘因子禁止直接生效实盘（宪章 B-007/B-009）。

依据: 缺口总账 GAP-F-43（前置 GAP-F-34 密度头已建）
SSoT: depgraph node 10505571（blueprint MOD-EVIDENCE_CHAIN）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: query + 四注入件 + MiningConfig
# 算法: 搜索 → 逐篇解析/LLM 提假说（JSON 契约+封顶） → 逐假说沙箱验证 → 通过者出登记草稿
# 输出: MiningResult（papers/hypotheses/validations/registry_drafts + stage_notes 计数 + notes 留痕）
"""

from __future__ import annotations

import json
import logging
import re as _re
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "FactorHypothesis",
    "MiningConfig",
    "MiningResult",
    "PaperRef",
    "ValidationReport",
    "build_factor_registry_draft",
    "run_factor_mining",
]

#: 注入件签名（模型网关/搜索/解析/沙箱抽象，测试 mock）
PaperSearcher = Callable[[str, int], "list[PaperRef]"]
PdfParser = Callable[["PaperRef"], str]
HypothesisLlmGateway = Callable[[str], str]
SandboxValidator = Callable[["FactorHypothesis"], "ValidationReport"]

_SLUG_RE: Final = _re.compile(r"[^a-z0-9]+")

_LLM_PROMPT_TEMPLATE: Final = (
    "你是因子挖掘助手。阅读以下论文全文，提炼最多 {max_hyp} 个可量化交易的因子假说，"
    "以 JSON 数组返回，元素形如 "
    '{{"name": "因子名", "formula": "可计算公式", "rationale": "经济学/行为学逻辑"}}，'
    "不要输出任何 JSON 以外内容：\n\n{text}"
)


@dataclass(frozen=True, slots=True)
class MiningConfig:
    """挖掘流水线配置。"""

    max_papers: int = 5
    max_hypotheses_per_paper: int = 3
    min_ic: float = 0.02  # 沙箱通过线（|IC| 均值下限，初拍值待标定）

    def __post_init__(self) -> None:
        if int(self.max_papers) < 1:
            raise ValueError(f"max_papers 非法（须 ≥1）: {self.max_papers!r}")
        if int(self.max_hypotheses_per_paper) < 1:
            raise ValueError(f"max_hypotheses_per_paper 非法（须 ≥1）: {self.max_hypotheses_per_paper!r}")
        if not (0.0 <= float(self.min_ic) < 1.0):
            raise ValueError(f"min_ic 非法（须 ∈ [0,1)）: {self.min_ic!r}")


@dataclass(frozen=True, slots=True)
class PaperRef:
    """论文引用（搜索阶段产出）。"""

    paper_id: str
    title: str
    source: str = ""
    url: str = ""


@dataclass(frozen=True, slots=True)
class FactorHypothesis:
    """因子假说（LLM 提取阶段产出）。"""

    name: str
    formula: str
    rationale: str
    source_paper_id: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """沙箱验证报告（validator 注入件产出契约）。"""

    name: str
    passed: bool
    ic_mean: float = 0.0
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MiningResult:
    """挖掘流水线总产出（JSON 可序列化）。"""

    query: str
    papers_found: int
    hypotheses: tuple[FactorHypothesis, ...]
    validations: tuple[ValidationReport, ...]
    registry_drafts: tuple[dict[str, Any], ...]  # factor_registry 片段登记草稿（恒 candidate）
    stage_notes: dict[str, int]  # 各阶段计数（papers_parsed/hypotheses_extracted/validated/passed/drafted）
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slugify(name: str) -> str:
    slug = _SLUG_RE.sub("-", name.lower()).strip("-")
    return slug or "unnamed"


def build_factor_registry_draft(hypothesis: FactorHypothesis, report: ValidationReport) -> dict[str, Any]:
    """产出 factor_registry 片段登记草稿（恒 candidate，禁直改注册表）。"""
    return {
        "factor_id": f"LLMMINE-{_slugify(hypothesis.name)}",
        "name": hypothesis.name,
        "formula": hypothesis.formula,
        "hypothesis": hypothesis.rationale,
        "source": "llm_factor_mining",
        "source_paper_id": hypothesis.source_paper_id,
        "eval_metrics": {"ic_mean": float(report.ic_mean)},
        "promotion_stage": "candidate",
        "decay_state": "created",
        "serving_mode": "none",
        "status": "candidate",
    }


def _extract_hypotheses(
    paper: PaperRef, text: str, llm_gateway: HypothesisLlmGateway, cfg: MiningConfig, notes: list[str]
) -> list[FactorHypothesis]:
    prompt = _LLM_PROMPT_TEMPLATE.format(max_hyp=cfg.max_hypotheses_per_paper, text=text)
    raw = llm_gateway(prompt)
    try:
        items = json.loads(str(raw))
    except (json.JSONDecodeError, TypeError, ValueError):
        notes.append(f"论文 {paper.paper_id} LLM 输出非法 JSON（剔除该篇假说）")
        return []
    if not isinstance(items, list):
        notes.append(f"论文 {paper.paper_id} LLM 输出非 JSON 数组（剔除）")
        return []
    out: list[FactorHypothesis] = []
    for item in items[: cfg.max_hypotheses_per_paper]:
        if (
            not isinstance(item, dict)
            or not str(item.get("name", "")).strip()
            or not str(item.get("formula", "")).strip()
        ):
            notes.append(f"论文 {paper.paper_id} 假说缺字段（name/formula 必填，剔除）: {str(item)[:80]}")
            continue
        out.append(
            FactorHypothesis(
                name=str(item["name"]).strip(),
                formula=str(item["formula"]).strip(),
                rationale=str(item.get("rationale", "")).strip(),
                source_paper_id=paper.paper_id,
            )
        )
    return out


def run_factor_mining(
    query: str,
    *,
    searcher: PaperSearcher | None,
    pdf_parser: PdfParser | None,
    llm_gateway: HypothesisLlmGateway | None,
    validator: SandboxValidator | None,
    config: MiningConfig | None = None,
) -> MiningResult:
    """LLM 因子挖掘流水线路径编排主入口（五段链骨架，全注入位）。

    Args:
        query: 检索主题（非空）。
        searcher/pdf_parser/llm_gateway/validator: 四注入件（缺一不可，fail-closed）。
        config: 流水线配置（None=默认 5 篇/每篇 3 假说/min_ic 0.02）。

    Returns:
        MiningResult（stage_notes 各阶段计数；registry_drafts 仅含通过者）。

    Raises:
        ValueError: query 空白/注入件缺失（fail-closed）。
    """
    cfg = config or MiningConfig()
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"query 非法（须非空字符串）: {query!r}")
    for name, dep in (
        ("searcher", searcher),
        ("pdf_parser", pdf_parser),
        ("llm_gateway", llm_gateway),
        ("validator", validator),
    ):
        if dep is None:
            raise ValueError(f"{name} 注入件缺失（流水线缺件不跑）")

    notes: list[str] = []
    stage = {"papers_parsed": 0, "hypotheses_extracted": 0, "validated": 0, "passed": 0, "drafted": 0}

    papers = list(searcher(query.strip(), cfg.max_papers))[: cfg.max_papers]  # type: ignore[misc]
    if not papers:
        notes.append("未检索到论文（全链空跑）")

    hypotheses: list[FactorHypothesis] = []
    for paper in papers:
        try:
            text = pdf_parser(paper)  # type: ignore[misc]
        except Exception as exc:  # noqa: BLE001 — 单篇解析失败不中断整批
            logger.warning("PDF 解析失败跳过: %s %s: %s", paper.paper_id, type(exc).__name__, exc)
            notes.append(f"论文 {paper.paper_id} PDF 解析失败（{type(exc).__name__}，跳过）")
            continue
        stage["papers_parsed"] += 1
        extracted = _extract_hypotheses(paper, text, llm_gateway, cfg, notes)  # type: ignore[arg-type]
        stage["hypotheses_extracted"] += len(extracted)
        hypotheses.extend(extracted)

    validations: list[ValidationReport] = []
    drafts: list[dict[str, Any]] = []
    for hy in hypotheses:
        try:
            report = validator(hy)  # type: ignore[misc]
        except Exception as exc:  # noqa: BLE001 — 单假说验证异常不中断整批
            logger.warning("沙箱验证异常跳过: %s %s: %s", hy.name, type(exc).__name__, exc)
            notes.append(f"假说 {hy.name} 验证异常（{type(exc).__name__}，跳过）")
            continue
        validations.append(report)
        stage["validated"] += 1
        if report.passed and float(report.ic_mean) >= cfg.min_ic:
            stage["passed"] += 1
            drafts.append(build_factor_registry_draft(hy, report))
            stage["drafted"] += 1
        elif report.passed:
            notes.append(f"假说 {hy.name} 沙箱通过但 ic_mean={report.ic_mean:.4f}<min_ic={cfg.min_ic}（不出草稿）")

    return MiningResult(
        query=query.strip(),
        papers_found=len(papers),
        hypotheses=tuple(hypotheses),
        validations=tuple(validations),
        registry_drafts=tuple(drafts),
        stage_notes=stage,
        notes=tuple(notes),
    )
