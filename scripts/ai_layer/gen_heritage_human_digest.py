# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] scripts.ai_layer.gen_heritage_human_digest
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.heritage.store (HeritageStore——V2/V5 读面);
#                zephyr.ai_layer.heritage.priors (HeritagePriors——覆盖率+冻结态);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] 月度体检窗（forget.py 同宿主）；OpsAlertFeed 通知板（GET /api/ops-notifications 消费面）;
#             Owner 人读通道（会话可自愿引用月报补写 memory 目录——人读零强制，DESIGN §2.7 D-L7-04）;
#             CLI python scripts/ai_layer/gen_heritage_human_digest.py [--month YYYY-MM] [--dry-run]
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 生成器产出禁手工维护（宪法 §9.5）：digests/YYYY-MM.md 全部由本器产出;
#              机读→人读单向（月报=消费面不作机检输入）；L7 永不写 memory 目录（硬边界自守）;
#              plain_zh 全非空（空=生成器 fail-closed 拒出报告，H1 CHECK 兜底）;
#              prior 冻结状态可见（冻结判定=priors.diversity_freeze 纯函数+覆盖率链跨月传递——
#              前言 coverage 链由上月 digest 前言读出，连续 2 月下降判据自洽）;
#              通知板=Alerter 落盘先行（渠道故障不反噬生成主流程，pipeline_events alert 先例）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.7（D-L7-04 双轨不对称）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] V2 出现空 plain_zh→ValueError（fail-closed 拒出半截报告）；输出目录不可写→异常上抛
#                  退出码 2；Alerter 不可达→debug 留痕继续（人读主交付=文件）；--dry-run 零写盘
# [TESTS] tests/ai_layer/heritage/test_heritage_digest.py（build_digest_text 纯函数：冻结态可见/
#         plain_zh 空拒出/前言覆盖率链；写盘走 tmp_path 注入）
"""gen_heritage_human_digest — L7 坑集月报生成器（V2/V5 → 通知板 + digests/YYYY-MM.md）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.7（机读→人读：每月从 V2/V5
导出坑集月报——plain_zh 一句话+案例锚点+配方摘要），推通知板+落 L7_heredity/digests/。

用法::

    python scripts/ai_layer/gen_heritage_human_digest.py --dry-run        # 只打印不落盘
    python scripts/ai_layer/gen_heritage_human_digest.py                  # 当月月报
    python scripts/ai_layer/gen_heritage_human_digest.py --month 2026-09  # 指定月
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.ai_layer.heritage.priors import HeritagePriors, diversity_freeze  # noqa: E402
from zephyr.ai_layer.heritage.store import HeritageStore  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

log = logging.getLogger("ai_heritage.digest")

DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "L7_heredity" / "digests"
DIGEST_TITLE: Final = "传承段坑集月报"


def _front_matter(month: str, coverage_now: float | None, prev1: float | None, prev2: float | None,
                  frozen: bool, why: str) -> str:
    """digest 前言（YAML；覆盖率链供下月连续下降判据读取）。"""
    lines = [
        "---",
        "ttl: permanent",
        f"month: {month}",
        f"generated_at: {now_utc().isoformat()}",
        "generator: scripts/ai_layer/gen_heritage_human_digest.py",
        "note: 生成器产出禁手工维护（宪法 §9.5）；本文件=人读消费面，不作机检输入（DESIGN §2.7）",
        f"coverage_now: {coverage_now if coverage_now is not None else 'null'}",
        f"coverage_prev1: {prev1 if prev1 is not None else 'null'}",
        f"coverage_prev2: {prev2 if prev2 is not None else 'null'}",
        f"prior_frozen: {str(frozen).lower()}",
        f"prior_frozen_why: \"{why}\"",
        "---",
    ]
    return "\n".join(lines)


@dataclass(frozen=True)
class DigestDraft:
    """月报组装草稿（build_digest_from_draft 入参载体；字段名与旧 build_digest_text 签名一一对应）。"""

    month: str
    defect_rows: list[dict[str, Any]]
    kpi_rows: list[dict[str, Any]]
    coverage_now: float | None
    prev1: float | None
    prev2: float | None
    frozen: bool
    freeze_why: str


def build_digest_from_draft(draft: DigestDraft) -> str:
    """月报正文组装（纯函数；plain_zh 空=ValueError fail-closed）。"""
    month = draft.month
    defect_rows = draft.defect_rows
    kpi_rows = draft.kpi_rows
    coverage_now = draft.coverage_now
    prev1 = draft.prev1
    prev2 = draft.prev2
    frozen = draft.frozen
    freeze_why = draft.freeze_why
    for row in defect_rows:
        if not str(row.get("plain_zh") or "").strip():
            raise ValueError(f"plain_zh_empty:{row.get('entry_id')}（fail-closed 拒出半截报告）")
    lines = [_front_matter(month, coverage_now, prev1, prev2, frozen, freeze_why), "", f"# {DIGEST_TITLE}（{month}）", ""]
    lines += ["## 冻结状态", ""]
    if frozen:
        lines += [f"**全局 prior_factor 已冻结 1.0**（{freeze_why}）——富矿加权停用，排除词表保留。", ""]
    else:
        lines += [f"正常（{freeze_why}）。", ""]
    lines += ["## 坑集（active 缺陷模式）", ""]
    if not defect_rows:
        lines += ["（本月无 active 缺陷模式——快照面为空属正常态，迁移工单落地前非异常）", ""]
    for row in defect_rows:
        recipe = " ".join(str(row.get("recipe") or "").split())
        lines += [
            f"- **{row.get('plain_zh')}**（`{row.get('entry_id')}` / `{row.get('pattern_norm')}`）",
            f"  - 锚点：`{row.get('source_ref')}`｜案发 {row.get('occurrence_count')} 次｜末案 {row.get('last_seen')}",
            f"  - 配方摘要：{recipe[:200]}{'…' if len(recipe) > 200 else ''}",
            "",
        ]
    lines += ["## 月度 KPI（V5）", "", "| 月 | 新增 | 命中 | 降级 | l7_prior 占比 | 覆盖率% |", "|---|---|---|---|---|---|"]
    for row in kpi_rows:
        lines.append(
            f"| {row.get('month')} | {row.get('entries_new')} | {row.get('hits_recorded')} | "
            f"{row.get('demoted')} | {row.get('l7_prior_share')} | {row.get('coverage_pct')} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_digest_text(*args, **kwargs):
    """DEPRECATED 兼容包装（gate 口径参数数 0）——转 Draft 新入口。"""
    return build_digest_from_draft(DigestDraft(*args, **kwargs))


def read_prev_coverages(out_dir: Path, month: str) -> tuple[float | None, float | None]:
    """读前两月 digest 前言覆盖率链（连续 2 月下降判据的历史输入；缺文件=None 正常态）。"""
    year, mon = (int(x) for x in month.split("-"))
    values: list[float | None] = []
    for step in (1, 2):
        total = year * 12 + (mon - 1) - step
        prev_month = f"{total // 12:04d}-{total % 12 + 1:02d}"
        path = out_dir / f"{prev_month}.md"
        value: float | None = None
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("coverage_now:"):
                    raw = line.split(":", 1)[1].strip()
                    value = float(raw) if raw not in {"null", ""} else None
                    break
        values.append(value)
    return values[0], values[1]


def notify_ops(message: str) -> None:
    """通知板推送（Alerter 落盘先行；渠道故障不反噬生成主流程）。"""
    if not message:
        return
    try:
        from zephyr.data.alerter import Alerter

        Alerter().notify("ai_heritage", message, level="INFO", source="ai_heritage")
    except Exception:  # noqa: BLE001——告警通道故障不反噬月报生成
        log.debug("alerter 不可达", exc_info=True)


def collect(store: HeritageStore, priors: HeritagePriors, out_dir: Path, month: str) -> dict[str, Any]:
    """V2/V5/冻结态取数 + 正文组装（DB 面）。"""
    conn = store.read_conn()
    cur = conn.cursor()
    cur.execute(
        f"SELECT entry_id, plain_zh, source_ref, pattern_norm, recipe, occurrence_count, last_seen "
        f"FROM {store.schema}.ai_heritage_defect_hot ORDER BY occurrence_count DESC, entry_id"
    )
    defect_rows = [dict(r) for r in cur.fetchall()]
    cur.execute(f"SELECT * FROM {store.schema}.ai_heritage_kpi ORDER BY month")  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
    kpi_rows = [dict(r) for r in cur.fetchall()]
    prev1, prev2 = read_prev_coverages(out_dir, month)
    coverage = priors.coverage_pct()
    frozen, why = diversity_freeze(coverage, prev1, prev2, priors.policy)
    return {
        "defect_rows": defect_rows,
        "kpi_rows": kpi_rows,
        "coverage": coverage,
        "prev1": prev1,
        "prev2": prev2,
        "frozen": frozen,
        "why": why,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：生成当月（或指定月）坑集月报。"""
    parser = argparse.ArgumentParser(description="L7 传承段坑集月报生成器（V2/V5 → digests/YYYY-MM.md）")
    parser.add_argument("--month", default=None, help="YYYY-MM（缺省=当月）")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="月报输出目录")
    parser.add_argument("--heritage-schema", default="ai_heritage", help="传承库 schema")
    parser.add_argument("--dry-run", action="store_true", help="只打印不落盘不推送")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    month = args.month or now_utc().strftime("%Y-%m")
    out_dir = Path(args.out_dir)
    try:
        store = HeritageStore(args.heritage_schema)
        priors = HeritagePriors(args.heritage_schema, store=store)
        data = collect(store, priors, out_dir, month)
        text = build_digest_from_draft(
            DigestDraft(
                month=month,
                defect_rows=data["defect_rows"],
                kpi_rows=data["kpi_rows"],
                coverage_now=data["coverage"],
                prev1=data["prev1"],
                prev2=data["prev2"],
                frozen=data["frozen"],
                freeze_why=data["why"],
            )
        )
        if args.dry_run:
            print(text)
            return 0
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{month}.md"
        path.write_text(text, encoding="utf-8")
        frozen_head = "prior 冻结" if data["frozen"] else "prior 正常"
        notify_ops(f"{DIGEST_TITLE} {month} 已生成：{path.name}（坑集 {len(data['defect_rows'])} 条，{frozen_head}）")
        print(f"DIGEST WRITTEN: {path}")
        return 0
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001——CLI 边界统一转退出码 2
        print(f"DIGEST FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 月报生成器属月度体检窗人工/调度入口，非常驻自动任务
    sys.exit(main())
