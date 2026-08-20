# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.strategy_archive
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (MAIN_REPO_ROOT); zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.governance.lifecycle_governance.retirement_workflow (archive 端口); 调用方（退役评审执行）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 归档只增不改（同 strategy_id 重复归档→StrategyArchiveError 防覆盖）; manifest.json 为归档唯一清单真源; strategy_id 防路径穿越（仅 [A-Za-z0-9_-]）; 取回只读不写
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategyArchiveError(ZA-GV-0049)
# [TESTS] tests/governance/lifecycle/test_strategy_archive.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: strategy_id + StrategyArchiveArtifacts(training_run_id/decay_knight/reason/params_snapshot/pnl_curve) + archive_root(默认 MAIN_REPO_ROOT/strategy_archive)
# F1: archive_strategy(建 strategy_archive/<sid>/ → manifest.json + params_snapshot.json + pnl_curve.csv；重复归档拒)
# F2: retrieve_strategy_archive(读 manifest.json + 产物文件清单；不存在→StrategyArchiveError)
# F3: list_archived_strategies(扫描 archive_root 下含 manifest.json 的子目录)
# O1: archive_strategy→归档目录 Path；retrieve→{manifest, files}
# [/ALGO_FLOW]
"""D_GOVERNANCE — 退役策略归档区读写（61 号 §3.9 归档四件套第 ④ 条，函数级）。

物理终点 ``strategy_archive/<strategy_id>/``：PnL 曲线 + 参数快照 + training_run_id +
退役原因五骑士归因，落 manifest.json 清单。归档四件套其余三件（design_memo deprecated /
depgraph retired / 模型注册 alias）由调用方另行承载，本模块仅承载第 ④ 条产物读写。

依据: 61_lifecycle_multi_ai §3.9（策略归档机制）
Version: 0.1.0
"""
from __future__ import annotations

import csv
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import MAIN_REPO_ROOT

logger = logging.getLogger(__name__)

#: strategy_id 合法字符（防路径穿越）
_STRATEGY_ID_PATTERN: Final = re.compile(r"^[A-Za-z0-9_\-]+$")
MANIFEST_FILENAME: Final[str] = "manifest.json"
PARAMS_FILENAME: Final[str] = "params_snapshot.json"
PNL_FILENAME: Final[str] = "pnl_curve.csv"
DEFAULT_ARCHIVE_ROOT: Final[Path] = MAIN_REPO_ROOT / "strategy_archive"


class StrategyArchiveError(ZephyrBaseError):
    """归档读写错误（id 非法 / 重复归档 / 归档不存在 / manifest 畸形）。"""

    error_code = "ZA-GV-0049"


@dataclass(frozen=True)
class StrategyArchiveArtifacts:
    """归档产物（61 号 §3.9 第 ④ 条四要素）。

    Attributes:
        training_run_id: 训练运行 ID（实验跟踪 run_id 或登记引用）。
        decay_knight: 退役原因五骑士归因（crowding/regime_change/overfitting/
            technology_evolution/regulatory_change）。
        reason: 退役原因人类可读说明。
        params_snapshot: 退役时参数快照（可选）。
        pnl_curve: 历史 PnL 曲线 [(date_iso, pnl), ...]（可选）。
        extra: 额外清单字段（可选）。
    """

    training_run_id: str
    decay_knight: str
    reason: str
    params_snapshot: dict | None = None
    pnl_curve: Sequence[tuple[str, float]] | None = None
    extra: dict = field(default_factory=dict)


def _validate_strategy_id(strategy_id: str) -> str:
    if not strategy_id or not _STRATEGY_ID_PATTERN.match(strategy_id):
        raise StrategyArchiveError(
            f"strategy_id 非法（仅允许 [A-Za-z0-9_-]，防路径穿越）: {strategy_id!r}"
        )
    return strategy_id


def archive_strategy(
    strategy_id: str,
    artifacts: StrategyArchiveArtifacts,
    *,
    archive_root: Path | None = None,
    archived_at: datetime | None = None,
) -> Path:
    """把退役策略产物归档到 ``<archive_root>/<strategy_id>/``。

    幂等纪律：归档只增不改——目录已存在（含 manifest.json）→ StrategyArchiveError，
    防并发/重试覆盖历史归档（重新归档须人工先移除旧目录，显式审计动作）。

    Returns:
        归档目录 Path。
    """
    _validate_strategy_id(strategy_id)
    if not artifacts.training_run_id or not artifacts.training_run_id.strip():
        raise StrategyArchiveError("training_run_id 不能为空（61 号 §3.9 四要素）")
    if not artifacts.decay_knight or not artifacts.decay_knight.strip():
        raise StrategyArchiveError("decay_knight 不能为空（五骑士归因必填）")

    root = archive_root if archive_root is not None else DEFAULT_ARCHIVE_ROOT
    target = root / strategy_id
    if (target / MANIFEST_FILENAME).exists():
        raise StrategyArchiveError(
            f"归档已存在（只增不改，防覆盖）: {target}",
            details={"strategy_id": strategy_id},
        )
    target.mkdir(parents=True, exist_ok=False)

    manifest = {
        "strategy_id": strategy_id,
        "archived_at": (archived_at or datetime.now(UTC)).isoformat(),
        "training_run_id": artifacts.training_run_id,
        "decay_knight": artifacts.decay_knight,
        "reason": artifacts.reason,
        "files": [MANIFEST_FILENAME],
        **artifacts.extra,
    }
    if artifacts.params_snapshot is not None:
        (target / PARAMS_FILENAME).write_text(
            json.dumps(artifacts.params_snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest["files"].append(PARAMS_FILENAME)
    if artifacts.pnl_curve is not None:
        with (target / PNL_FILENAME).open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "pnl"])
            for date_iso, pnl in artifacts.pnl_curve:
                writer.writerow([date_iso, float(pnl)])
        manifest["files"].append(PNL_FILENAME)

    (target / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.warning("策略 %s 已归档到 %s（%s）", strategy_id, target, artifacts.decay_knight)
    return target


def retrieve_strategy_archive(
    strategy_id: str,
    *,
    archive_root: Path | None = None,
) -> dict:
    """取回退役策略归档（只读）：``{"manifest": dict, "files": {name: Path}}``。"""
    _validate_strategy_id(strategy_id)
    root = archive_root if archive_root is not None else DEFAULT_ARCHIVE_ROOT
    target = root / strategy_id
    manifest_path = target / MANIFEST_FILENAME
    if not manifest_path.exists():
        raise StrategyArchiveError(
            f"归档不存在: {target}", details={"strategy_id": strategy_id}
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise StrategyArchiveError(f"manifest 畸形: {manifest_path}: {exc}") from exc
    files = {p.name: p for p in sorted(target.iterdir()) if p.is_file()}
    return {"manifest": manifest, "files": files}


def list_archived_strategies(*, archive_root: Path | None = None) -> list[str]:
    """列出全部已归档策略 ID（含 manifest.json 的子目录；根目录不存在 → 空列表）。"""
    root = archive_root if archive_root is not None else DEFAULT_ARCHIVE_ROOT
    if not root.exists():
        return []
    return sorted(
        d.name for d in root.iterdir() if d.is_dir() and (d / MANIFEST_FILENAME).exists()
    )


__all__: Final = [
    "DEFAULT_ARCHIVE_ROOT",
    "MANIFEST_FILENAME",
    "PARAMS_FILENAME",
    "PNL_FILENAME",
    "StrategyArchiveArtifacts",
    "StrategyArchiveError",
    "archive_strategy",
    "list_archived_strategies",
    "retrieve_strategy_archive",
]
