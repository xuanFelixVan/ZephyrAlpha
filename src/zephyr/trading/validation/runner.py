# [BLUEPRINT] MOD-TDMVAL-001 | docs/03_modules/_domain_trading/validation/blueprint.md
# [MODULE] zephyr.trading.validation.runner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.decision_map; zephyr.data.ch_writer
# [CONSUMERS] zephyr.frontend.dashboard.api_server(/api/tdm/validation 只读消费台账); P2-1 衰减巡检
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] holdout 排除最近 12 个月; 触发<30 verdict=pending; 台账只追加不删改; 空数据不造假(pending 如实披露)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError
# [TESTS] tests/trading/test_validation_runner.py
# [TTL] permanent
"""验证 runner——节点验证批入口（PB-12 排序：第一批=L4 执行类 14 节点 exec_quality；
第二批=X 流 18 节点 exit_counterfactual，Owner 2026-09-10 X 流验证批指令 T3）。

数据源与真源:
    节点清单   config/trading_decision_map.yaml（layer==L4，排除币圈镜像 TDM-C-*）
    成交流水   data/backtest_artifacts/bt-*.json 的 trade_log（run 级回测产物）
    方法学     docs/.../catalogs/validation_method_registry.yaml（五类方法+土规+holdout 参数）
    台账       c1_backtest.node_verdict（DDL 真源 schemas/categories/backtest_node_verdict.py）

铁律落地（Owner 2026-09-09 裁定 §7.3）:
    1. holdout 窗口排除最近 12 个月——窗口内流水不参与任何指标计算与结论。
    2. 保密考卷只考一次——runner 不改写/不删除既有台账行，每次验证追加新 run 行。
    土规（PB-13 降级）: 触发<30 → verdict=pending + significance=insufficient_samples；
    样本外衰减≥50%（对比同方法首验指标）→ significance=oos_decay_suspect。

已知限制（如实披露，见蓝图 §3）:
    - trade_log 无节点归因字段——exec/exit 指标均以流水全量为统计对象（exit 触发=卖出流水代理）。
    - 决策价自 T1（commit ebc98ac1）起入流水；exec 滑点 v1 仍用 VWAP 代理（真决策价口径变更需另批定稿）。
    - exit_counterfactual 对照数据=信号消融对照器（晨报裁定②随本批施工）；回放受协议备忘录
      §12 约束未放行前对照缺失 → 按方法学保持 pending，不造假。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from zephyr.data import ch_writer
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_MAP_PATH = REPO_ROOT / "config" / "trading_decision_map.yaml"
_ARTIFACTS_DIR = REPO_ROOT / "data" / "backtest_artifacts"
_METHOD_REGISTRY = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "validation_method_registry.yaml"
)
_VERDICT_TABLE = "c1_backtest.node_verdict"
_VERDICT_COLUMNS = (
    "(run_id, snapshot_commit, window_start, window_end, node_id, validation_method,"
    " triggers, hit_ratio, significance, verdict, verdict_at, notes)"
)

# 首批=L4 执行类；币圈镜像节点（TDM-C-*）无 A 股成交流水，排除后正好 14 节点
_L4_EXCLUDE_PREFIX = "TDM-C-"


class ValidationError(Exception):
    """验证数据/配置异常（地图无 L4 节点、方法学登记表缺失等）。"""

    error_code = "ZA-TDMVAL-0001"


@dataclass(frozen=True)
class ValidationConfig:
    """验证批参数（默认值=validation_method_registry.yaml discipline 段的裁定口径）。"""

    holdout_months: int = 12          # PB-08：保密考卷窗口（月）
    min_triggers: int = 30            # PB-13 土规 1：触发<30 不下结论
    oos_decay_threshold: float = 0.50  # PB-13 土规 2：样本外衰减≥50% 判存疑
    lag_recheck: bool = True          # PB-16：lag=1 滞后重算开关（默认开）
    as_of: datetime | None = None     # 验证基准时点（None=now；测试可注入固定时点）


@dataclass
class ValidationReport:
    """一次验证批的结果摘要（对话/晨报可读）。"""

    run_id: str
    snapshot_commit: str
    window_start: str | None
    window_end: str | None
    holdout_cutoff: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    written: bool = False
    decay: dict[str, Any] | None = None   # 衰减巡检尾随结果（run_decay_check 返回值）


# ── 节点与方法推导 ────────────────────────────────────────────────────────

def load_exec_nodes(map_path: Path = _MAP_PATH) -> list[dict[str, Any]]:
    """L4 执行类节点清单（排除币圈镜像）。

    Raises:
        ValidationError: 地图无 L4 节点（空批不可静默通过）。
    """
    import yaml

    raw = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    nodes = [
        {"node_id": n["node_id"], "name_zh": n.get("name_zh", ""), "layer": n.get("layer"), "flow": n.get("flow")}
        for n in raw.get("nodes", [])
        if n.get("layer") == "L4" and not n["node_id"].startswith(_L4_EXCLUDE_PREFIX)
    ]
    if not nodes:
        raise ValidationError(f"地图无 L4 执行类节点（{map_path}）——首批验证批不可为空")
    return nodes


def load_xflow_nodes(map_path: Path = _MAP_PATH) -> list[dict[str, Any]]:
    """X 流离场/风控节点清单（flow==exit_flow，第二批；含 S1/S2/R1 枢纽与子节点）。

    Raises:
        ValidationError: 地图无 exit_flow 节点（空批不可静默通过）。
    """
    import yaml

    raw = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    nodes = [
        {"node_id": n["node_id"], "name_zh": n.get("name_zh", ""), "layer": n.get("layer"), "flow": n.get("flow")}
        for n in raw.get("nodes", [])
        if n.get("flow") == "exit_flow"
    ]
    if not nodes:
        raise ValidationError(f"地图无 X 流（exit_flow）节点（{map_path}）——风控验证批不可为空")
    return nodes


def derive_method(node: dict[str, Any]) -> str:
    """layer+flow+形态推导验证方法（validation_method_registry.derivation_rules 的代码形态）。

    节点不加 YAML 字段（真源裁定）——推导顺序=L4 → X 流 → F 流 → L1 传感器 → 兜底区分度。
    """
    if node.get("layer") == "L4":
        return "exec_quality"
    if node.get("flow") == "exit_flow":
        return "exit_counterfactual"
    if node.get("flow") == "portfolio_flow":
        return "portfolio_attribution"
    if node.get("layer") == "L1" and node["node_id"].split("-")[-1].startswith("S"):
        return "sensor_monotonicity"
    return "agg_discrimination"


# ── 成交流水加载与 holdout 切分 ───────────────────────────────────────────

def load_fills(artifacts_dir: Path = _ARTIFACTS_DIR) -> list[dict[str, Any]]:
    """读全部回测产物 trade_log（fill 级：timestamp/side/price/quantity/commission + run/strategy 溯源）。"""
    fills: list[dict[str, Any]] = []
    if not artifacts_dir.exists():
        return fills
    for f in sorted(artifacts_dir.glob("bt-*.json")):
        try:
            artifact = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("跳过损坏产物 %s: %s", f.name, exc)
            continue
        for t in artifact.get("trade_log") or []:
            fills.append({
                "run_id": artifact.get("run_id", f.stem),
                "strategy_id": artifact.get("strategy_id", ""),
                "timestamp": str(t.get("timestamp", "")),
                "symbol": t.get("symbol", ""),
                "side": t.get("side", ""),
                "price": t.get("price"),
                "quantity": t.get("quantity"),
                "commission": t.get("commission"),
                "decision_price": t.get("decision_price"),  # T1（ebc98ac1）起流水携带；v1 指标未消费，前向就绪
            })
    return fills


def holdout_cutoff(as_of: datetime, holdout_months: int) -> datetime:
    """holdout 截止线：as_of 往前推 holdout_months 个自然月（不够整月按同日截断）。"""
    month = as_of.month - holdout_months
    year = as_of.year
    while month <= 0:
        month += 12
        year -= 1
    day = min(as_of.day, 28)   # 月底安全截断（2 月无 30/31 日）
    return as_of.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)


def partition_by_holdout(
    fills: list[dict[str, Any]], cutoff: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """流水切分为 (在验窗口内, holdout 保密窗口)。窗口内=timestamp <= cutoff。"""
    inside: list[dict[str, Any]] = []
    locked: list[dict[str, Any]] = []
    for f in fills:
        try:
            ts = datetime.strptime(f["timestamp"][:10], "%Y-%m-%d")
        except ValueError:
            locked.append(f)   # 无日期/脏时间戳按保密处理（宁严勿漏）
            continue
        (inside if ts <= cutoff else locked).append(f)
    return inside, locked


# ── 执行质量指标（exec_quality）─────────────────────────────────────────

def _parse_float(v: Any) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def compute_exec_metrics(
    fills: list[dict[str, Any]],
    ref_prices: dict[str, float] | None = None,
) -> dict[str, Any]:
    """执行质量指标（滑点 bp + 成交统计）。

    ref_prices: symbol → 参考价（同日 VWAP 代理；lag_recheck=True 时为 T+1 基准）。
    缺参考价的 fill 跳过滑点统计（不猜）。
    """
    prices = [(f, _parse_float(f.get("price"))) for f in fills]
    priced = [(f, p) for f, p in prices if p and p > 0]
    slips: list[float] = []
    for f, p in priced:
        ref = (ref_prices or {}).get(f.get("symbol", ""))
        if not ref or ref <= 0:
            continue
        direction = 1.0 if f.get("side") == "buy" else -1.0
        slips.append(direction * (p - ref) / ref * 10000.0)   # bp，正=劣于基准
    n = len(fills)
    slip_mean = sum(slips) / len(slips) if slips else None
    return {
        "triggers": n,
        "slip_bp_mean": round(slip_mean, 2) if slip_mean is not None else None,
        "slip_samples": len(slips),
        "fill_rate": None,   # v1 流水只含成交记录，未成交数不可得——如实置空（方法学裁定单轴判）
    }


def apply_soil_rules(
    metrics: dict[str, Any], cfg: ValidationConfig, first_metrics: dict[str, Any] | None = None
) -> tuple[str, str]:
    """两土规 → (significance, verdict)。先样本量闸门，再样本外衰减闸门。

    返回 verdict ∈ valid|noise|pending（数据充分时由滑点容差判定；v1 容差线=20bp）。
    """
    if metrics["triggers"] < cfg.min_triggers:
        return "insufficient_samples", "pending"
    if first_metrics and first_metrics.get("slip_bp_mean") is not None and metrics.get("slip_bp_mean") is not None:
        first, now = first_metrics["slip_bp_mean"], metrics["slip_bp_mean"]
        if first > 0 and (now - first) / first >= cfg.oos_decay_threshold:
            return "oos_decay_suspect", "pending"
    slip = metrics.get("slip_bp_mean")
    if slip is None:
        return "", "pending"   # 无参考价可算——不下结论
    if slip <= 20.0:
        return "ok", "valid"
    if slip <= 40.0:
        return "ok", "pending"
    return "ok", "noise"


# ── 离场反事实指标（exit_counterfactual，第二批 X 流）────────────────────

def compute_exit_counterfactual_metrics(
    fills: list[dict[str, Any]],
    ablation_diff: list[float] | None = None,
) -> dict[str, Any]:
    """离场反事实指标（validation_method_registry.yaml exit_counterfactual 口径）。

    统计口径=触发/不触发两组后续 N 日损失差；对照数据=T2 信号消融对照器的双净值
    差额序列（全量净值-无风控净值，>0=风控救回金额）。对照未提供时如实降级：
    avoided_amount=None（方法学 notes「对照未建保持 pending」的代码形态，不造假）。

    触发计数 v1 口径：流水无节点归因，用在验窗口内卖出流水作 X 流触发代理
    （全量口径+notes 披露，与一期裁定 4 同例）。

    Args:
        fills: 在验窗口内流水（partition_by_holdout 的 inside）。
        ablation_diff: 消融差额序列（T2 ablation 双净值差，逐窗口/逐时点）。
    """
    exits = [f for f in fills if f.get("side") == "sell"]
    diffs = [d for d in (ablation_diff or []) if d is not None]
    return {
        "triggers": len(exits),
        "slip_bp_mean": None,   # 非滑点口径；键保留 None 复用行装配
        "fill_rate": None,
        "avoided_amount": round(sum(diffs), 2) if diffs else None,  # X 流救回金额（对照就绪才有值）
        "ablation_samples": len(diffs),
    }


def apply_exit_soil_rules(
    metrics: dict[str, Any], cfg: ValidationConfig, first_metrics: dict[str, Any] | None = None
) -> tuple[str, str]:
    """exit_counterfactual 土规 → (significance, verdict)。

    判定链（对齐 verdict_mapping「触发组损失显著更小→valid；差异不显著→pending；
    触发组反而更差→noise」）：样本量闸门 → 对照就绪闸门 → 对照样本量闸门 →
    衰减闸门（避损额衰减≥50% 判存疑）→ 避损方向判定。
    """
    if metrics["triggers"] < cfg.min_triggers:
        return "insufficient_samples", "pending"
    if metrics.get("avoided_amount") is None:
        return "", "pending"   # 对照数据未建（消融器未放行/未就绪）——保持 pending
    if metrics.get("ablation_samples", 0) < cfg.min_triggers:
        return "insufficient_samples", "pending"   # 对照样本不足，显著性无从谈起
    if first_metrics and first_metrics.get("avoided_amount") is not None:
        first, now = first_metrics["avoided_amount"], metrics["avoided_amount"]
        if first > 0 and (first - now) / first >= cfg.oos_decay_threshold:
            return "oos_decay_suspect", "pending"
    if metrics["avoided_amount"] <= 0:
        return "ok", "noise"   # 风控救回≤0=触发组反而更差
    return "ok", "valid"


# ── 批入口 ───────────────────────────────────────────────────────────────

def _default_writer(table: str, columns: str, tsv: bytes) -> bool:
    """生产写入通道：ch_writer.write_tsv（HTTP 主路径+本地落盘兜底，CH 已提交才 True）。"""
    return ch_writer.write_tsv(table, columns, tsv)


def run_validation(
    cfg: ValidationConfig | None = None,
    map_path: Path = _MAP_PATH,
    artifacts_dir: Path = _ARTIFACTS_DIR,
    dry_run: bool = False,
    writer: Callable[[str, str, bytes], bool] | None = None,
    decay_check: bool = True,
    batch: str = "L4",
    ablation_diff: list[float] | None = None,
) -> ValidationReport:
    """验证批入口：按 batch 选节点清单逐个出 verdict 行并写台账。

    batch="L4"（默认）=第一批执行类 14 节点 exec_quality（一期行为不变）；
    batch="XFLOW"=第二批 X 流 18 节点 exit_counterfactual（ablation_diff=消融差额
    序列，缺省时对照缺失如实降级 pending）。
    dry_run=True 不写库（验收预演）；writer 参数供测试注入收集器。
    decay_check=True（默认）：台账写入成功后顺带跑衰减巡检（裁定 2026-09-10：衰减判定
    依赖新验证行落地才有意义——巡检=验证批的尾随事件，不挂 cron 不占调度器，真正事件驱动）。
    """
    cfg = cfg or ValidationConfig()
    writer = writer or _default_writer
    as_of = cfg.as_of or datetime.now()
    cutoff = holdout_cutoff(as_of, cfg.holdout_months)

    if batch == "L4":
        nodes = load_exec_nodes(map_path)
    elif batch == "XFLOW":
        nodes = load_xflow_nodes(map_path)
    else:
        raise ValidationError(f"未知验证批: {batch}（合法值: L4 | XFLOW）")
    fills = load_fills(artifacts_dir)
    inside, locked = partition_by_holdout(fills, cutoff)

    from zephyr.backtest.core.engine_base import current_map_snapshot

    run_id = f"VAL-{as_of.strftime('%Y%m%d-%H%M%S')}"
    report = ValidationReport(
        run_id=run_id,
        snapshot_commit=current_map_snapshot(),
        window_start=min((f["timestamp"][:10] for f in inside), default=None),
        window_end=max((f["timestamp"][:10] for f in inside), default=None),
        holdout_cutoff=cutoff.strftime("%Y-%m-%d"),
    )

    if batch == "XFLOW":
        metrics = compute_exit_counterfactual_metrics(inside, ablation_diff=ablation_diff)
        significance, verdict = apply_exit_soil_rules(metrics, cfg)
    else:
        metrics = compute_exec_metrics(inside)   # v1：执行流水全量（归因粒度限制，蓝图 §3）
        significance, verdict = apply_soil_rules(metrics, cfg)
    verdict_at = as_of.strftime("%Y-%m-%d %H:%M:%S")

    for n in nodes:
        notes_parts: list[str] = []
        if not inside and locked:
            notes_parts.append(
                f"在验窗口无成交流水：现有 {len(locked)} 笔全部落 holdout 保密窗口"
                f"（>{report.holdout_cutoff}），按 PB-08 定稿前不可考；窗口前移后重跑出结论"
            )
        elif inside and batch == "L4":
            notes_parts.append(f"滑点均值 {metrics['slip_bp_mean']} bp（VWAP 代理基准，lag_recheck={cfg.lag_recheck}）")
        elif inside:
            notes_parts.append(f"离场触发代理计数 {metrics['triggers']}（卖出流水全量口径）")
        if batch == "L4":
            notes_parts.append("归因粒度限制：流水无节点字段，v1 以执行流水全量统计（蓝图 §3）")
            if metrics["fill_rate"] is None:
                notes_parts.append("成交率不可得（流水只含成交记录）")
        else:
            notes_parts.append("归因粒度限制：流水无节点字段，离场触发以卖出流水代理（蓝图 §3）")
            if metrics.get("avoided_amount") is None:
                notes_parts.append(
                    "exit_counterfactual 对照数据未就绪（信号消融对照器随本批施工；"
                    "消融回放受协议备忘录 §12 约束，参数定稿放行前不出真结论）——按方法学保持 pending"
                )
            else:
                notes_parts.append(
                    f"消融避损 {metrics['avoided_amount']} 元（对照序列 {metrics['ablation_samples']} 样本）"
                )
        row = {
            "run_id": run_id,
            "snapshot_commit": report.snapshot_commit,
            "window_start": report.window_start or report.holdout_cutoff,
            "window_end": report.window_end or report.holdout_cutoff,
            "node_id": n["node_id"],
            "validation_method": derive_method(n),
            "triggers": metrics["triggers"],
            "hit_ratio": metrics["fill_rate"],
            "significance": significance or "na",
            "verdict": verdict,
            "verdict_at": verdict_at,
            "notes": "；".join(notes_parts),
        }
        report.rows.append(row)

    def _tsv_cell(v: Any) -> str:
        if v is None:
            return "\\N"   # CH TSV 的 NULL 转义——空串会被解析成 0（2026-09-09 实测踩坑）
        return str(v).replace("\t", " ")

    tsv = ("\n".join(
        "\t".join(_tsv_cell(row[c]) for c in (
            "run_id", "snapshot_commit", "window_start", "window_end", "node_id", "validation_method",
            "triggers", "hit_ratio", "significance", "verdict", "verdict_at", "notes"))
        for row in report.rows
    ) + "\n").encode("utf-8") if report.rows else b""

    if dry_run:
        logger.info("dry-run: %d 行不落库（run_id=%s）", len(report.rows), run_id)
        return report
    if not report.rows:
        raise ValidationError("验证批产出 0 行——拒绝空写入")
    report.written = writer(_VERDICT_TABLE, _VERDICT_COLUMNS, tsv)
    if not report.written:
        logger.error("台账写入未确认 CH_COMMITTED（run_id=%s）——查 ch_writer 落盘兜底", run_id)
        return report
    if decay_check:
        # 衰减巡检尾随事件（PB-14 事件驱动落地）：函数内导入防循环依赖
        # （decay_watch 复用本模块的表常量）。巡检失败不回滚验证批——只记日志。
        try:
            from zephyr.trading.validation.decay_watch import run_decay_check

            report.decay = run_decay_check(writer=writer)
            if report.decay["decayed"]:
                logger.warning("衰减巡检：%d 个节点判 decaying（已追加台账行，面板徽章即预警）",
                               report.decay["decayed"])
        except Exception as exc:   # noqa: BLE001 — 巡检是尾随增强，不阻断验证批结论
            logger.error("衰减巡检失败（验证批结论不受影响）: %s", exc)
    return report


__all__ = [
    "ValidationConfig",
    "ValidationError",
    "ValidationReport",
    "apply_exit_soil_rules",
    "apply_soil_rules",
    "compute_exec_metrics",
    "compute_exit_counterfactual_metrics",
    "derive_method",
    "holdout_cutoff",
    "load_exec_nodes",
    "load_fills",
    "load_xflow_nodes",
    "partition_by_holdout",
    "run_validation",
]
