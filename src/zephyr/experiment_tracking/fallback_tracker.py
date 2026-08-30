# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.fallback_tracker
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.experiment_tracking.experiment_tracker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 与 ExperimentTracker 同接口；数据写 logs/experiment_tracking_fallback/{component}/{run_id}/run_meta.json
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写文件失败→stderr 不抛
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""
L_INFRA_TELEMETRY — JSON 实验跟踪器（单一后端实现）。

与 ExperimentTracker 同接口，数据写本地 JSON 文件，供 query.py 扫描查询。
依据: 51_panel_experiment_history_mlflow_retirement.md 工作流 A（单一 JSON 后端）
Version: 0.2.0（MLflow 退役）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fallback_dir 参数
#   fields: 参数 fallback_dir（无注解）
#   code: fallback_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FallbackBackend
#   name_en: FallbackBackend
#   intro: 单一 JSON 实验跟踪后端（MLflow 已退役，本后端即唯一生产后端）。
#   desc: 单一 JSON 实验跟踪后端（MLflow 已退役，本后端即唯一生产后端）。 每次 run 写一个 JSON 文件到 {fallback_dir}/{component}/{ru…；公共方法（定义序）: start_r…
#   inputs: fallback_dir
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FallbackBackend
#   downstream: zephyr.experiment_tracking.experiment_tracker
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional


class FallbackBackend:
    """单一 JSON 实验跟踪后端（MLflow 已退役，本后端即唯一生产后端）。

    每次 run 写一个 JSON 文件到 {fallback_dir}/{component}/{run_id}/run_meta.json，
    含 params/metrics/tags/status/start_time/end_time + artifacts 目录引用。
    """

    def __init__(self, fallback_dir: Path) -> None:
        self._base = Path(fallback_dir)
        self._current: dict[str, Any] | None = None
        self._current_dir: Path | None = None

    def start_run(self, component: str, run_name: str | None, tags: dict | None) -> str:
        run_id = uuid.uuid4().hex[:12]
        run_dir = self._base / component
        run_dir.mkdir(parents=True, exist_ok=True)
        self._current_dir = run_dir / run_id
        self._current_dir.mkdir(parents=True, exist_ok=True)
        self._current = {
            "run_id": run_id,
            "component": component,
            "run_name": run_name or f"{component}_{datetime.now(UTC):%Y%m%d_%H%M%S}",
            "tags": tags or {},
            "params": {},
            "metrics": {},
            "status": "RUNNING",
            "start_time": datetime.now(UTC).isoformat(),
            "end_time": None,
            "artifacts": [],
        }
        return run_id

    def log_params(self, params: dict[str, Any]) -> None:
        current = getattr(self, "_current", None)
        if current is not None:
            current["params"].update({k: str(v) for k, v in params.items()})

    def log_metrics(self, metrics: dict[str, float], step: int | None) -> None:
        current = getattr(self, "_current", None)
        if current is not None:
            for k, v in metrics.items():
                current["metrics"][k] = float(v)

    def log_artifact(self, local_path: str, artifact_path: str | None) -> None:
        current = getattr(self, "_current", None)
        if current is None:
            return
        # 只记录路径引用，不复制（fallback query 层按 local_path 解析）
        current["artifacts"].append(
            {
                "local_path": str(local_path),
                "artifact_path": artifact_path,
            }
        )

    def log_artifact_bytes(self, data: bytes, filename: str, artifact_path: str | None) -> None:
        current = getattr(self, "_current", None)
        current_dir = getattr(self, "_current_dir", None)
        if current is None or current_dir is None:
            return
        target_dir = current_dir if artifact_path is None else current_dir / artifact_path
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / filename).write_bytes(data)
        current["artifacts"].append(
            {
                "filename": filename,
                "artifact_path": artifact_path,
            }
        )

    def end_run(self, status: str) -> None:
        current = getattr(self, "_current", None)
        current_dir = getattr(self, "_current_dir", None)
        if current is None or current_dir is None:
            return
        current["status"] = status
        current["end_time"] = datetime.now(UTC).isoformat()
        meta_path = current_dir / "run_meta.json"
        meta_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        del self._current
        del self._current_dir
