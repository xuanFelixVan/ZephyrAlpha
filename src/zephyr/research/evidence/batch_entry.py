# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（18号清单 §6 波4-11 / 11号文 §4.2 Phase 0 / apply_depgraph 设计态登记建议见 .runtime/p3_fragments/w4_11.md）
# [MODULE] zephyr.research.evidence.batch_entry
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE（知识管理——假设/证据=知识资产）
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.file_utils; zephyr.research.evidence.hypothesis_registry; zephyr.research.evidence.evidence_chain; zephyr.research.evidence.iteration_guide
# [CONSUMERS] 手动 CLI 触发（python -m zephyr.research.evidence.batch_entry）+ 计划任务挂点（Windows Task Scheduler / scripts 调度层登记由统筹裁定，本模块仅提供入口）；tests/research/test_evidence_phase0.py
# [STARTUP] manual（仅 CLI/调度手动触发运行——盘中路径零调用）
# [MATURITY] testing
# [INVARIANTS] 盘中零调用——工作日 09:30-15:00 CST（A股交易时段，含午间休市从严）拒绝执行，无例外无旁路；frequency ∈ {daily, weekly} 词表外拒绝；仅评估未归档假设（archived 跳过计数留痕）；批量前证据链完整性自检（篡改即 fail-fast）；建议清单 JSON 原子写落盘；本模块不得被任何盘中/交易路径 import（静态约束——grep 佐证见 .runtime/p3_fragments/w4_11.md）
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BatchEntryError(ZA-RE-0030)——基础错误；IntradayExecutionForbiddenError(ZA-RE-0031)——盘中时段执行尝试；frequency 词表外→ValueError
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""日/周频批量入口（Batch Entry）——研究证据关联组件 P0-4（11号文 §4.2）。

职责：全量（未归档）假设的批量迭代评估——加载假设注册表与证据链 → 证据链
完整性自检 → 迭代引导器逐假设产出建议 → 建议清单 JSON 落盘。

触发方式（11号文 P0-4"手动触发+计划任务挂点"）：
    - 手动：python -m zephyr.research.evidence.batch_entry --frequency daily
    - 计划任务挂点：本 CLI 即挂点（Windows Task Scheduler / 调度层登记由统筹
      裁定接线，本模块只提供入口，不自行注册计划任务）。

盘中零调用声明（11号文 §2.3 频率约束 / §5-3"不做实时盘中证据关联"）：
    证据关联按日频/周频批量处理，盘中无迭代引导需求。本模块内置时段守卫——
    工作日 09:30-15:00 CST（A股交易时段，午间休市 11:30-13:00 从严一并拒绝，
    节假日按交易日从严）任何执行尝试一律 IntradayExecutionForbiddenError。
    本模块亦不 import 任何交易/盘中设施，且不得被盘中路径 import（静态约束）。

落盘：data/research/evidence/guidance/guidance_YYYYMMDD_HHMMSS_{frequency}.json
    （落点选择理由见 hypothesis_registry.py docstring"落点选择"段）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 批量执行请求（CLI 参数/API 关键字）
#   fields: frequency（daily/weekly）/store_dir/rules_path/output_dir/at
#   code: main → run_batch 入口
# 层: 算法
# - id: A1
#   name_zh: ① 盘中零调用守卫
#   name_en: is_intraday 判定
#   desc: 工作日 09:30-15:00 CST（含午间休市从严）执行尝试一律 ZA-RE-0031 拒绝；frequency 词表外 ValueError
#   inputs: I1
#   outputs: 放行时刻
# - id: A2
#   name_zh: ② 加载+完整性自检
#   name_en: registry/chain 加载 + verify_integrity
#   desc: 假设注册表+证据链加载 → 证据链 hash 全量重算自检（篡改即 ZA-RE-0013 fail-fast，防线前移）
#   inputs: A1 放行后
#   outputs: 可评估假设集（未归档）
# - id: A3
#   name_zh: ③ 全量迭代评估
#   name_en: guide.evaluate 循环
#   desc: 未归档假设逐一证据聚合 → 迭代引导器产出建议（带 rule_id+证据计数）
#   inputs: A2
#   outputs: Guidance 清单
# 层: 输出
# - id: O1
#   name_zh: 建议清单落盘 + 执行报告
#   name_en: guidance_*.json（atomic_write）+ BatchReport
#   downstream: 人工/统筹消费清单（后续 Phase 3 闭环回流接线由 11号文 §4.5 裁定）；tests/research/test_evidence_phase0.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1

依据: 11号文 §3.1/§4.2 P0-4 + 18号清单 §6 波4-11
Version: 0.1.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Any, Final

from zephyr.research.evidence.evidence_chain import EvidenceChain
from zephyr.research.evidence.hypothesis_registry import (
    CST,
    DEFAULT_STORE_DIR,
    HypothesisRegistry,
    HypothesisStatus,
)
from zephyr.research.evidence.iteration_guide import IterationGuide, load_rules
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write

__all__: Final = [
    "BatchEntryError",
    "BatchReport",
    "FREQUENCIES",
    "INTRADAY_END",
    "INTRADAY_START",
    "IntradayExecutionForbiddenError",
    "is_intraday",
    "main",
    "run_batch",
]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约（ZA-RE-0030~0031）
# ============================================================================


class BatchEntryError(ZephyrBaseError):
    """ZA-RE-0030: 批量入口基础错误。"""

    error_code = "ZA-RE-0030"


class IntradayExecutionForbiddenError(BatchEntryError):
    """ZA-RE-0031: 盘中时段（工作日 09:30-15:00 CST）执行尝试——一律拒绝。"""

    error_code = "ZA-RE-0031"


# ============================================================================
# 2. 常量与盘中守卫
# ============================================================================

#: 盘中窗口（A股交易时段；午间休市从严一并覆盖；边界左闭右开）
INTRADAY_START: Final = time(9, 30)
INTRADAY_END: Final = time(15, 0)

#: 批量频率词表（11号文 §2.3：日频/周频批量）
FREQUENCIES: Final = frozenset({"daily", "weekly"})

GUIDANCE_DIRNAME: Final = "guidance"


def _as_cst(at: datetime) -> datetime:
    """naive 时间按 CST 解释（统一口径）；aware 时间原样。"""
    return at if at.tzinfo is not None else at.replace(tzinfo=CST)


def is_intraday(at: datetime) -> bool:
    """盘中时段判定：工作日（周一至周五）09:30（含）-15:00（不含）CST。

    从严口径：午间休市 11:30-13:00 一并拒绝；法定节假日按交易日处理
    （宁严勿宽——非交易时段本就不该有盘中任务）。
    """
    at = _as_cst(at)
    return at.weekday() < 5 and INTRADAY_START <= at.time() < INTRADAY_END


# ============================================================================
# 3. 批量执行
# ============================================================================


@dataclass(frozen=True)
class BatchReport:
    """批量执行报告（返回给调用方；清单本体落盘 JSON）。"""

    run_id: str
    frequency: str
    generated_at: str  # ISO 8601（CST）
    evaluated_count: int
    skipped_archived_count: int
    output_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "frequency": self.frequency,
            "generated_at": self.generated_at,
            "evaluated_count": self.evaluated_count,
            "skipped_archived_count": self.skipped_archived_count,
            "output_path": self.output_path,
        }


def run_batch(
    *,
    frequency: str = "daily",
    store_dir: Path | str | None = None,
    rules_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    at: datetime | None = None,
) -> BatchReport:
    """跑一轮全量（未归档）假设迭代评估，建议清单落盘。

    Args:
        frequency: 批量频率——daily / weekly（词表外 ValueError）。
        store_dir: 假设/证据落盘目录；None → data/research/evidence/。
        rules_path: 迭代引导规则表；None → config/iteration_guide_rules.yaml。
        output_dir: 建议清单输出目录；None → {store_dir}/guidance/。
        at: 执行时刻（测试注入）；None → 当前 CST。

    Raises:
        ValueError: frequency 越出词表。
        IntradayExecutionForbiddenError: 盘中时段（工作日 09:30-15:00 CST）。
        EvidenceIntegrityError: 批量前完整性自检检出篡改。
    """
    if frequency not in FREQUENCIES:
        raise ValueError(f"批量频率越出词表: {frequency!r}（词表：daily/weekly）")
    now = _as_cst(at) if at is not None else datetime.now(CST)
    # 盘中零调用守卫（11号文 §5-3：不做实时盘中证据关联）——无例外无旁路
    if is_intraday(now):
        raise IntradayExecutionForbiddenError(
            f"盘中时段拒绝执行证据批量评估: {now.isoformat()}"
            "（工作日 09:30-15:00 CST；11号文 §2.3/§5-3 频率约束——日/周频批量，盘中零调用）",
            details={"at": now.isoformat(), "frequency": frequency},
        )

    store = Path(store_dir) if store_dir is not None else DEFAULT_STORE_DIR
    registry = HypothesisRegistry(store_dir=store)
    chain = EvidenceChain(store_dir=store, registry=registry)
    chain.verify_integrity()  # 批量前完整性自检——篡改即 fail-fast（P0-2 防线前移）
    guide = IterationGuide(rules=load_rules(rules_path) if rules_path is not None else None)

    hypotheses = registry.list_all()
    targets = [h for h in hypotheses if h.status is not HypothesisStatus.ARCHIVED]
    skipped = len(hypotheses) - len(targets)
    items = [guide.evaluate(chain.summary_for(h.hypothesis_id), at=now) for h in targets]

    out_dir = Path(output_dir) if output_dir is not None else store / GUIDANCE_DIRNAME
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"BATCH-{now:%Y%m%dT%H%M%S}-{frequency}"
    out_path = out_dir / f"guidance_{now:%Y%m%d_%H%M%S}_{frequency}.json"
    payload = {
        "run_id": run_id,
        "frequency": frequency,
        "generated_at": now.isoformat(),
        "evaluated_count": len(items),
        "skipped_archived_count": skipped,
        "items": [g.to_dict() for g in items],
    }
    atomic_write(out_path, json.dumps(payload, ensure_ascii=False, indent=2))
    log.info(
        "证据批量评估完成 %s：评估 %d 假设（跳过归档 %d）→ %s",
        run_id,
        len(items),
        skipped,
        out_path,
    )
    return BatchReport(
        run_id=run_id,
        frequency=frequency,
        generated_at=now.isoformat(),
        evaluated_count=len(items),
        skipped_archived_count=skipped,
        output_path=str(out_path),
    )


# ============================================================================
# 4. CLI（手动触发 + 计划任务挂点）
# ============================================================================


def main(argv: list[str] | None = None, *, at: datetime | None = None) -> int:
    """CLI 入口。返回码：0 成功；3 盘中时段拒绝执行。"""
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.research.evidence.batch_entry",
        description="研究证据关联——日/周频批量迭代评估（盘中 09:30-15:00 拒绝执行）",
    )
    parser.add_argument("--frequency", choices=sorted(FREQUENCIES), default="daily", help="批量频率（默认 daily）")
    parser.add_argument("--store-dir", default=None, help="假设/证据落盘目录（默认 data/research/evidence/）")
    parser.add_argument("--rules", default=None, help="迭代引导规则表 YAML（默认 config/iteration_guide_rules.yaml）")
    parser.add_argument("--output-dir", default=None, help="建议清单输出目录（默认 {store}/guidance/）")
    args = parser.parse_args(argv)
    try:
        report = run_batch(
            frequency=args.frequency,
            store_dir=args.store_dir,
            rules_path=args.rules,
            output_dir=args.output_dir,
            at=at,
        )
    except IntradayExecutionForbiddenError as exc:
        print(f"[盘中禁跑] {exc}", file=sys.stderr)
        return 3
    print(f"[batch] {report.run_id}：评估 {report.evaluated_count} 假设 → {report.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
