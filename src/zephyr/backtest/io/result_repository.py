# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.io.result_repository
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.io.backtest_result_sink; zephyr.shared.io.paths; zephyr.shared.utils.time_utils; zephyr.backtest.core.cost_attribution（成本归因注入，lazy import）; zephyr.backtest.core.cost_model_calibration; zephyr.backtest.core.matching_logic（费率真源注入，零字面量）; zephyr.backtest.core.engine_base（合理性倍数带真源，H5-F）
# [CONSUMERS] zephyr.frontend.dashboard.components.backtest_results; zephyr.frontend.dashboard.components.tick_replay
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] PIT铁律(零前瞻偏差); run_id全局唯一; 检索接口对前端透明;
#              成本归因费率只从 matching_logic 注入（本件零费率字面量）;
#              合理性护栏倍数带只从 engine_base.plausible_equity_multiple_bounds 取
#              （H5-F 治本 2026-09-17：本件曾自写 11.0x/0.05x 第二套字面量，与引擎层
#              10.0/-0.95 两条线互不知情，改一处漏一处）;
#              归因不可算时 MUST 写 status=error + ERROR 日志而非省略字段（沉默禁令）
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ArtifactNotFoundError
# [TESTS]
# [TTL] permanent
"""result_repository · 回测产物持久化/检索模块（v1.3.0 新增，#ARCH-047）

蓝图规格: docs/03_modules/_domain_backtest/blueprint.md §16.7
契约: CTR-P1-017 BacktestRunArtifact(source=D_BACKTEST, target=[D_FRONTEND])

职责:
  - 持久化 BacktestRunArtifact(CTR-P1-017), 返回 run_id
  - 提供 get_artifact(run_id) 检索接口, 供 D_FRONTEND backtest_results/tick_replay 组件消费
  - 封装存储细节(文件系统 JSON), 对前端透明

约束:
  - 仅持久化/检索, 不做可视化转换(转换由 sink 完成)
  - run_id 必须全局唯一(BacktestResult.idempotency_key 关联)
  - PIT 铁律: equity_curve/trade_log 数据零前瞻偏差
  - 检索接口对 D_FRONTEND 同步暴露, 大对象延迟由调用方处理
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ArtifactNotFoundError(Exception):
    """回测产物未找到"""

    error_code = "ZA-BT-0011"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class ArtifactQuarantinedError(Exception):
    """回测产物被合理性护栏隔离（P0-4，2026-09-14 外部审查整改）。

    失真产物（极端收益/零成交空跑）已写入 quarantine/ 子目录留证，
    不进正库——"30x 收益自动隔离而非存盘"。确需落盘（复盘取证）用
    save_artifact(..., allow_implausible=True)。
    """

    error_code = "ZA-BT-0042"

    def __init__(self, *args, quarantine_path: str | None = None, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code
        self.quarantine_path = quarantine_path


def _artifact_plausibility_violations(artifact: "BacktestRunArtifact") -> list[str]:
    """产物级合理性检查（P0-4）：净值曲线倍数 + 零成交空跑。

    与引擎层护栏（engine_base.enforce_result_plausibility）互补：引擎层在
    结果产出时拦截，本函数在落盘时兜底——覆盖绕过引擎直写产物的管线
    （如 tick 回放/历史管线），口径用净值曲线首尾倍数（对 fraction/multiple
    两种 metrics 口径都稳健）。
    """
    violations: list[str] = []
    curve = artifact.equity_curve or []
    if len(curve) >= 2:
        try:
            first = float(curve[0].get("equity", 0.0))
            last = float(curve[-1].get("equity", 0.0))
        except (AttributeError, TypeError, ValueError):
            first = last = 0.0
        if first > 0 and last > 0:
            multiple = last / first
            max_multiple, min_multiple = plausible_equity_multiple_bounds()
            if multiple > max_multiple:  # 倍数带由 engine_base 收益带推出，禁在此复述数值
                violations.append(
                    f"equity {first:.0f}->{last:.0f} = {multiple:.1f}x（>合理上限 {max_multiple:.1f}x，"
                    "失真嫌疑；口径真源=engine_base.MAX_PLAUSIBLE_TOTAL_RETURN）"
                )
            elif multiple < min_multiple:  # 无杠杆 long-only 不可能亏穿
                violations.append(
                    f"equity {first:.0f}->{last:.0f} = {multiple:.3f}x（<合理下限 {min_multiple:.2f}x）"
                )
    metrics = artifact.metrics or {}
    if metrics.get("trades_count") == 0:
        violations.append("metrics.trades_count=0 空跑")
    return violations


# ===== CTR-P1-017 BacktestRunArtifact 数据模型 =====


def _default_storage_path() -> Path:
    """默认存储路径: REPO_ROOT/data/backtest_artifacts/ (绝对路径, SSoT: zephyr.shared.io.paths)"""
    return REPO_ROOT / "data" / "backtest_artifacts"


def _artifact_to_dict(artifact: BacktestRunArtifact) -> dict[str, Any]:
    """转换 artifact 为可 JSON 序列化 dict"""
    return asdict(artifact)


def _dict_to_artifact(d: dict[str, Any]) -> BacktestRunArtifact:
    """从 dict 重建 artifact（忽略未知字段，兼容 schema 演进）"""
    # 只取 BacktestRunArtifact 已知字段（前向兼容）
    known_fields = {f for f in BacktestRunArtifact.__dataclass_fields__}
    filtered = {k: v for k, v in d.items() if k in known_fields}
    return BacktestRunArtifact(**filtered)


# ===== 核心接口 =====


def save_artifact(
    artifact: BacktestRunArtifact,
    storage_path: Path | None = None,
    allow_implausible: bool = False,
) -> str:
    """持久化 BacktestRunArtifact, 返回 run_id。

    蓝图 §16.7: io/result_repository.py 详细规格

    P0-4（2026-09-14 外部审查整改）：落盘前合理性护栏默认开启——极端收益
    （净值首尾倍数越出 engine_base 收益带推出的倍数带，现=4.0x/0.05x）与零成交空跑
    产物自动隔离至 ``<storage>/quarantine/`` 留证并抛 ArtifactQuarantinedError，不进正库。
    allow_implausible=True 显式放行（复盘取证用）。

    Args:
        artifact: CTR-P1-017 BacktestRunArtifact(含 BacktestSinkData + 元数据 + 时间戳)
        storage_path: 存储目录（默认 data/backtest_artifacts/）
        allow_implausible: 显式放行失真产物落正库（默认 False=隔离）

    Returns:
        run_id(全局唯一, 用于后续检索)

    Raises:
        ArtifactNotFoundError: artifact 为 None 或 run_id 为空
        ArtifactQuarantinedError: 产物未通过合理性护栏（已隔离至 quarantine/）

    副作用: 写入存储后端(文件系统 JSON)
    """
    if artifact is None:
        raise ArtifactNotFoundError("BacktestRunArtifact 不能为 None")

    if not artifact.run_id:
        raise ArtifactNotFoundError("BacktestRunArtifact.run_id 不能为空")

    storage = storage_path or _default_storage_path()
    storage.mkdir(parents=True, exist_ok=True)

    # P0-4 合理性护栏（默认开）：失真产物隔离留证，不进正库
    violations = _artifact_plausibility_violations(artifact)
    if violations and not allow_implausible:
        quarantine_dir = storage / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        quarantine_file = quarantine_dir / f"{artifact.run_id}.json"
        payload = _artifact_to_dict(artifact)
        payload["quarantine_reasons"] = violations
        with open(quarantine_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        raise ArtifactQuarantinedError(
            f"回测产物合理性护栏拦截 (run_id={artifact.run_id}): " + "; ".join(violations)
            + f"——已隔离至 {quarantine_file}（确需落正库用 allow_implausible=True）",
            quarantine_path=str(quarantine_file),
        )

    # 填充 created_at（如果未设置）——用 now_utc_str()（空格分隔，SSoT 存储契约，AGENTS.md §11.1.1 / time_utils.now_utc_str）
    if not artifact.created_at:
        artifact = replace(artifact, created_at=now_utc_str())

    file_path = storage / f"{artifact.run_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(_artifact_to_dict(artifact), f, ensure_ascii=False, indent=2)

    return artifact.run_id


def get_artifact(
    run_id: str,
    storage_path: Path | None = None,
) -> BacktestRunArtifact:
    """按 run_id 检索 BacktestRunArtifact, 供 D_FRONTEND 消费。

    蓝图 §16.7: io/result_repository.py 详细规格

    Args:
        run_id: save_artifact 返回值
        storage_path: 存储目录（默认 data/backtest_artifacts/）

    Returns:
        BacktestRunArtifact(完整回测运行产物)

    Raises:
        ArtifactNotFoundError: run_id 不存在或文件损坏
    """
    if not run_id:
        raise ArtifactNotFoundError("run_id 不能为空")

    storage = storage_path or _default_storage_path()
    file_path = storage / f"{run_id}.json"

    if not file_path.exists():
        raise ArtifactNotFoundError("run_id 未找到", details={"run_id": run_id, "file_path": str(file_path)})

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise ArtifactNotFoundError(f"run_id={run_id} 文件损坏: {e}") from e

    return _dict_to_artifact(d)


def list_artifacts(
    strategy_id: str | None = None,
    storage_path: Path | None = None,
) -> list[str]:
    """列出所有 run_id（可按 strategy_id 过滤）。

    Args:
        strategy_id: 策略 ID 过滤（None = 全部）
        storage_path: 存储目录（默认 data/backtest_artifacts/）

    Returns:
        run_id 列表（按 created_at 降序, 最新优先）
    """
    storage = storage_path or _default_storage_path()
    if not storage.exists():
        return []

    run_ids: list[tuple[str, str]] = []
    for f in storage.glob("*.json"):
        run_id = f.stem
        if strategy_id is not None:
            try:
                artifact = get_artifact(run_id, storage_path=storage)
                if artifact.strategy_id != strategy_id:
                    continue
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                continue
        # 读取 created_at 用于排序
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            created_at = d.get("created_at", "")
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            created_at = ""
        run_ids.append((run_id, created_at))

    # 按 created_at 降序（最新优先）
    run_ids.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in run_ids]


def delete_artifact(
    run_id: str,
    storage_path: Path | None = None,
) -> bool:
    """删除指定 run_id 的产物文件。

    Args:
        run_id: 要删除的 run_id
        storage_path: 存储目录（默认 data/backtest_artifacts/）

    Returns:
        True=删除成功, False=文件不存在
    """
    if not run_id:
        return False
    storage = storage_path or _default_storage_path()
    file_path = storage / f"{run_id}.json"
    if not file_path.exists():
        return False
    file_path.unlink()
    return True


# ===== 便捷构建函数 =====


def _cost_attribution_snapshot(
    data: "BacktestSinkData",
    trade_log: list[dict[str, Any]],
) -> dict[str, Any]:
    """成交成本归因快照（台账 #23 H2 收口：把"一半亏损是佣金"写成产物里的显式事实）。

    为什么注入点是本函数而不是各调用方：``build_artifact_from_data`` 是所有持久化
    路径的唯一收口（scripts/run_backtest 与 framework_composer 的 S11 整装回测都经
    此处）——引擎侧标定得再准，artifact 里没有这一节就等于报告看不见。

    口径纪律：
      - 费率一律从 ``matching_logic`` 真源注入（本件零费率字面量，RULE-SSOT）；
      - ``consumed_slippage_bps`` 取**逐笔名义的标定档名义加权**，不取旧 1bp：
        artifact 不携带引擎实际消费的 bps，而缺 ``decision_price`` 的笔需要补计口径；
        宁取有出处的实证档（分层 2.34~7.24bp，无流动性信息时 3.79bp），
        不取无出处的旧一口价，provenance 随盘披露；
      - 归因失败不阻断落盘（取证通道坏 ≠ 样本坏），但 MUST 留痕 + ERROR 日志——
        静默省略字段是本仓禁令（沉默禁令）。
    """
    from zephyr.backtest.core import cost_model_calibration as cost_cal
    from zephyr.backtest.core.cost_attribution import attribute_trade_costs
    from zephyr.backtest.core.matching_logic import (
        COMMISSION_RATE,
        MIN_COMMISSION,
        STAMP_TAX_RATE,
        TRANSFER_FEE_RATE,
    )

    schema = "cost_attribution/1.0"
    if not trade_log:
        return {"schema": schema, "status": "no_trades"}

    curve = data.equity_curve or ()
    initial_capital = float(curve[0].equity) if curve and float(curve[0].equity) > 0 else None
    net_result = initial_capital * float(data.total_return) if initial_capital is not None else None

    notional_sum = 0.0
    slip_weighted = 0.0
    for rec in trade_log:
        try:
            notional = float(rec["price"]) * float(rec["quantity"])
        except (KeyError, TypeError, ValueError):
            continue
        if notional <= 0:
            continue
        notional_sum += notional
        slip_weighted += float(cost_cal.resolve_slippage_bps(notional)) * notional
    consumed_bps = slip_weighted / notional_sum if notional_sum > 0 else None

    try:
        attr = attribute_trade_costs(
            trade_log,
            commission_rate=COMMISSION_RATE,
            stamp_tax_rate=STAMP_TAX_RATE,
            transfer_fee_rate=TRANSFER_FEE_RATE,
            min_commission=MIN_COMMISSION,
            consumed_slippage_bps=consumed_bps,
            initial_capital=initial_capital,
            n_trading_days=len(curve) or None,
            net_result=net_result,
        )
    except Exception as exc:  # noqa: BLE001 —— 归因是旁路取证，坏在这里不该拖垮落盘
        logger.error("成本归因快照失败（artifact 仍落盘，禁静默）: %s: %s", type(exc).__name__, exc)
        return {"schema": schema, "status": "error", "error": f"{type(exc).__name__}: {exc}"}

    snapshot = attr.to_metrics_dict()
    snapshot["status"] = "ok"
    snapshot["consumed_slippage_provenance"] = (
        "calibrated_per_fill_notional_weighted" if consumed_bps is not None else "calibrated_universal"
    )
    for alert in attr.alerts:
        if alert.severity in ("P0", "P1"):
            logger.warning("[cost_attribution] %s(%s): %s", alert.code, alert.severity, alert.message)
    return snapshot


def build_artifact_from_data(
    data: BacktestSinkData,
    tick_replay_data: list[dict[str, Any]] | None = None,
) -> BacktestRunArtifact:
    """从 BacktestSinkData 构建 BacktestRunArtifact。

    便捷方法：将 sink 的输出转化为可持久化的 artifact。
    自动提取时序数据 + 汇总指标快照。

    Args:
        data: sink_backtest_result 的输出
        tick_replay_data: tick 回放数据 [{timestamp, price, volume}, ...]（可选）

    Returns:
        BacktestRunArtifact(可传给 save_artifact 持久化)
    """
    # 提取时序数据为 list[dict]
    equity_curve = [{"timestamp": p.timestamp, "equity": p.equity} for p in data.equity_curve]
    trade_log = [
        {
            "timestamp": p.timestamp,
            "symbol": p.symbol,
            "side": p.side,
            "price": p.price,
            "quantity": p.quantity,
            "commission": p.commission,
            "decision_price": p.decision_price,
            "order_type": p.order_type,
        }
        for p in data.trade_log
    ]
    drawdown_curve = [{"timestamp": p.timestamp, "drawdown": p.drawdown} for p in data.drawdown_curve] or None
    benchmark_curve = [{"timestamp": p.timestamp, "value": p.value} for p in data.benchmark_curve] or None

    metrics = data.to_metrics_dict()
    metrics["cost_attribution"] = _cost_attribution_snapshot(data, trade_log)

    return BacktestRunArtifact(
        strategy_id=data.strategy_id,
        run_id=data.run_id,
        equity_curve=equity_curve,
        trade_log=trade_log,
        schema_version="1.0.0",
        tick_replay_data=tick_replay_data,
        benchmark_curve=benchmark_curve,
        drawdown_curve=drawdown_curve,
        created_at="",  # save_artifact 时自动填充
        metrics=metrics,
    )


__all__ = [
    "ArtifactNotFoundError",
    "ArtifactQuarantinedError",
    "BacktestRunArtifact",
    "save_artifact",
    "get_artifact",
    "list_artifacts",
    "delete_artifact",
    "build_artifact_from_data",
]

# ==== BEGIN CODGEN:CTR-P1-017 ====
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.backtest.io.result_repository
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] frozen dataclass; SSoT=cross_layer_contracts.yaml; DO NOT EDIT (codegen)
# [MODIFY-GUARD] cross_layer_contracts.yaml; generate_contracts.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
import json
import os
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from zephyr.backtest.core.engine_base import plausible_equity_multiple_bounds
from zephyr.backtest.io.backtest_result_sink import (
    BacktestSinkData,
    BenchmarkPoint,
    DrawdownPoint,
    EquityPoint,
    TradeRecord,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc, now_utc_str

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-08-06"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/result_repository.py

CTR-P1-017: BacktestRunArtifact / 回测运行产物

回测运行产物契约，包含回测结果时序数据（equity curve/trade log/tick replay data），用于前端可视化消费。与 CTR-P1-016 BacktestResult（汇总指标）互补——BacktestResult 是标量汇总，BacktestRunArtifact 是时序明细。

SSoT: cross_layer_contracts.yaml -> CTR-P1-017
Version: 1.0.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当回测引擎完成一次运行后,MUST 产出 BacktestRunArtifact 以支撑前端可视化。 strategy_id 必须对应策略注册表中已注册的策略 key。 run_id 必须与 BacktestResult.idempotency_key 关联,保证汇总指标与时序明细可对齐。 equity_curve 与 trade_log 数据 MUST 遵循 PIT 铁律(零前瞻偏差)——任何时序点不得引用其之后时刻才能获得的信息。 tick_replay_data 为可选项,仅当回测配置启用 tick 级回放时填充。 benchmark_curve 与 drawdown_curve 为可选,用于前端叠加渲染基准对比与回撤分析。 Frontend 通过 result_repository.py (D_BACKTEST io/) 拉取本产物,使用 Panel+HoloViz 组件渲染可视化。
"""


@dataclass(frozen=True)
class BacktestRunArtifact:
    run_id: str
    strategy_id: str
    benchmark_curve: list[dict[str, Any]] | None = None
    created_at: str = ""
    drawdown_curve: list[dict[str, Any]] | None = None
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] | None = None
    schema_version: str = "1.0.0"
    tick_replay_data: list[dict[str, Any]] | None = None
    trade_log: list[dict[str, Any]] = field(default_factory=list)


# ==== END CODGEN:CTR-P1-017 ====
