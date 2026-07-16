# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.io.result_repository
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.io.backtest_result_sink
# [CONSUMERS] zephyr.frontend.dashboard.components.backtest_results; zephyr.frontend.dashboard.components.tick_replay
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] PIT铁律(零前瞻偏差); run_id全局唯一; 检索接口对前端透明
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ArtifactNotFoundError
# [TESTS]
# [A_module] module_id=MOD-BT-001-io-repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

import json
import os
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from zephyr.backtest.io.backtest_result_sink import (
    BacktestSinkData,
    EquityPoint,
    TradeRecord,
    DrawdownPoint,
    BenchmarkPoint,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc


class ArtifactNotFoundError(Exception):
    """回测产物未找到"""

    error_code = "ZA-BT-0011"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# ===== CTR-P1-017 BacktestRunArtifact 数据模型 =====


@dataclass(frozen=True)
class BacktestRunArtifact:
    """回测运行产物（CTR-P1-017, #ARCH-047）

    持久化回测运行产物，包含回测结果时序数据（equity curve/trade log/tick replay data），
    用于前端可视化消费。与 CTR-P1-016 BacktestResult（汇总指标）互补——
    BacktestResult 是标量汇总，BacktestRunArtifact 是时序明细。

    PIT 铁律: equity_curve/trade_log 数据 MUST 遵循零前瞻偏差。
    """
    strategy_id: str
    run_id: str  # 与 BacktestResult.idempotency_key 关联
    equity_curve: list[dict[str, Any]]  # [{timestamp: ISO8601, equity: float}, ...]
    trade_log: list[dict[str, Any]]  # [{timestamp, symbol, side, price, quantity, commission}, ...]
    schema_version: str = "1.0.0"
    tick_replay_data: Optional[list[dict[str, Any]]] = None  # [{timestamp, price, volume}, ...]
    benchmark_curve: Optional[list[dict[str, Any]]] = None  # [{timestamp, value}, ...]
    drawdown_curve: Optional[list[dict[str, Any]]] = None  # [{timestamp, drawdown}, ...]
    created_at: str = ""  # ISO8601, save_artifact 时自动填充
    metrics: Optional[dict[str, Any]] = None  # 汇总指标快照(从 BacktestSinkData 提取)


# ===== 存储后端 =====


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
    storage_path: Optional[Path] = None,
) -> str:
    """持久化 BacktestRunArtifact, 返回 run_id。

    蓝图 §16.7: io/result_repository.py 详细规格

    Args:
        artifact: CTR-P1-017 BacktestRunArtifact(含 BacktestSinkData + 元数据 + 时间戳)
        storage_path: 存储目录（默认 data/backtest_artifacts/）

    Returns:
        run_id(全局唯一, 用于后续检索)

    Raises:
        ArtifactNotFoundError: artifact 为 None 或 run_id 为空

    副作用: 写入存储后端(文件系统 JSON)
    """
    if artifact is None:
        raise ArtifactNotFoundError("BacktestRunArtifact 不能为 None")

    if not artifact.run_id:
        raise ArtifactNotFoundError("BacktestRunArtifact.run_id 不能为空")

    storage = storage_path or _default_storage_path()
    storage.mkdir(parents=True, exist_ok=True)

    # 填充 created_at（如果未设置）
    if not artifact.created_at:
        artifact = replace(artifact, created_at=now_utc().isoformat())

    file_path = storage / f"{artifact.run_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(_artifact_to_dict(artifact), f, ensure_ascii=False, indent=2)

    return artifact.run_id


def get_artifact(
    run_id: str,
    storage_path: Optional[Path] = None,
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
    strategy_id: Optional[str] = None,
    storage_path: Optional[Path] = None,
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
            except Exception:
                continue
        # 读取 created_at 用于排序
        try:
            with open(f, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            created_at = d.get("created_at", "")
        except Exception:
            created_at = ""
        run_ids.append((run_id, created_at))

    # 按 created_at 降序（最新优先）
    run_ids.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in run_ids]


def delete_artifact(
    run_id: str,
    storage_path: Optional[Path] = None,
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


def build_artifact_from_data(
    data: BacktestSinkData,
    tick_replay_data: Optional[list[dict[str, Any]]] = None,
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
    equity_curve = [
        {"timestamp": p.timestamp, "equity": p.equity}
        for p in data.equity_curve
    ]
    trade_log = [
        {
            "timestamp": p.timestamp,
            "symbol": p.symbol,
            "side": p.side,
            "price": p.price,
            "quantity": p.quantity,
            "commission": p.commission,
        }
        for p in data.trade_log
    ]
    drawdown_curve = [
        {"timestamp": p.timestamp, "drawdown": p.drawdown}
        for p in data.drawdown_curve
    ] or None
    benchmark_curve = [
        {"timestamp": p.timestamp, "value": p.value}
        for p in data.benchmark_curve
    ] or None

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
        metrics=data.to_metrics_dict(),
    )


__all__ = [
    "ArtifactNotFoundError",
    "BacktestRunArtifact",
    "save_artifact",
    "get_artifact",
    "list_artifacts",
    "delete_artifact",
    "build_artifact_from_data",
]
