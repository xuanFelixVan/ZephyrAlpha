# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.drift_infrastructure
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_drift.py (+9 more)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 基础设施不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Detector 基础设施 — drift_infrastructure.py


维护窗口、预算系统、检查点写入器、恢复管理器、环境感知/差分检测、部分部署检测。


从 drift_engine.py 提取，对标 blueprint.md §2.6/§2.9/§2.10/§2.13。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: hours 参数
#   fields: 参数 hours，类型注解 int
#   code: drift_infrastructure.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: triggered_by_auto 参数
#   fields: 参数 triggered_by_auto，类型注解 bool
#   code: drift_infrastructure.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: threshold 参数
#   fields: 参数 threshold，类型注解 int
#   code: drift_infrastructure.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: drift_infrastructure.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MaintenanceWindow
#   name_en: MaintenanceWindow
#   intro: class MaintenanceWindow 源码 L164-L179
#   desc: 公共方法（定义序）: is_active, time_remaining；源码 L164-L179
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_maintenance_window
#   name_en: get_maintenance_window
#   intro: get_maintenance_window() 源码 L191-L192
#   desc: 源码 L191-L192
#   inputs: 无参数
#   outputs: MaintenanceWindow | None
# - id: A3
#   name_zh: ③ declare_maintenance_window
#   name_en: declare_maintenance_window
#   intro: declare_maintenance_window(hours, triggered_by_auto) 源码 L19…
#   desc: 源码 L195-L204
#   inputs: hours triggered_by_auto
#   outputs: MaintenanceWindow
# - id: A4
#   name_zh: ④ check_large_diff
#   name_en: check_large_diff
#   intro: check_large_diff(threshold) 源码 L207-L216
#   desc: 源码 L207-L216
#   inputs: threshold
#   outputs: bool
# - id: A5
#   name_zh: ⑤ get_or_create_budget
#   name_en: get_or_create_budget
#   intro: get_or_create_budget(module_id, tier) 源码 L222-L234
#   desc: 源码 L222-L234
#   inputs: module_id tier
#   outputs: DriftBudget
# - id: A6
#   name_zh: ⑥ consume_budget
#   name_en: consume_budget
#   intro: consume_budget(module_id, tier) 源码 L237-L242
#   desc: 源码 L237-L242
#   inputs: module_id tier
#   outputs: bool
# - id: A7
#   name_zh: ⑦ check_budget_for_gate
#   name_en: check_budget_for_gate
#   intro: check_budget_for_gate(module_id, tier, break_glass) 源码 L245…
#   desc: 源码 L245-L261
#   inputs: module_id tier break_glass
#   outputs: dict[str, object]
# - id: A8
#   name_zh: ⑧ CheckpointWriter
#   name_en: CheckpointWriter
#   intro: class CheckpointWriter 源码 L267-L330
#   desc: 公共方法（定义序）: write, cleanup；源码 L267-L330
#   inputs: 无参数
#   outputs: 返回值
# - id: A9
#   name_zh: ⑨ RecoveryManager
#   name_en: RecoveryManager
#   intro: class RecoveryManager 源码 L333-L384
#   desc: 公共方法（定义序）: check_orphaned, on_startup；源码 L333-L384
#   inputs: 无参数
#   outputs: 返回值
# - id: A10
#   name_zh: ⑩ register_env_tags
#   name_en: register_env_tags
#   intro: register_env_tags(module_id, tags) 源码 L393-L394
#   desc: 源码 L393-L394
#   inputs: module_id tags
#   outputs: 返回值
#   （注：A10 之后另有 4 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: MaintenanceWindow | None
#   name_en: MaintenanceWindow | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_drift.py (+9 more)
# - id: O2
#   name_zh: MaintenanceWindow
#   name_en: MaintenanceWindow
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_drift.py (+9 more)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from zephyr.shared.infra.process_pool import run_subprocess_hidden

from .drift_models import DriftBudget

# ── Maintenance Window ──────────────────────────────────────


@dataclass
class MaintenanceWindow:
    start_time: datetime

    end_time: datetime

    is_shadow_mode: bool = True

    triggered_by_auto: bool = False

    def is_active(self) -> bool:
        now = datetime.now(UTC)

        return self.start_time <= now <= self.end_time

    def time_remaining(self) -> timedelta:
        return max(self.end_time - datetime.now(UTC), timedelta(0))


_last_window: MaintenanceWindow | None = None


_budgets: dict[str, DriftBudget] = {}


_checkpoints_dir: str = ""


def get_maintenance_window() -> MaintenanceWindow | None:
    return _last_window


def declare_maintenance_window(hours: int = 2, triggered_by_auto: bool = False) -> MaintenanceWindow:
    global _last_window

    now = datetime.now(UTC)

    _last_window = MaintenanceWindow(
        start_time=now, end_time=now + timedelta(hours=hours), triggered_by_auto=triggered_by_auto
    )

    return _last_window


def check_large_diff(threshold: int = 50) -> bool:
    try:
        result = run_subprocess_hidden(["git", "diff", "--stat", "HEAD~1"], capture_output=True, text=True, timeout=10)

        lines = result.stdout.strip().split("\n")

        return (len(lines) - 1) > threshold

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# ── Budget ─────────────────────────────────────────────────


def get_or_create_budget(module_id: str, tier: str = "P0") -> DriftBudget:
    key = f"{module_id}:{tier}"

    if key not in _budgets:
        _budgets[key] = DriftBudget(
            module_id=module_id,
            tier=tier,
            monthly_budget=DriftBudget.tier_budget(tier),
            remaining=DriftBudget.tier_budget(tier),
            reset_date=date.today().replace(day=1),
        )

    return _budgets[key]


def consume_budget(module_id: str, tier: str = "P0") -> bool:
    budget = get_or_create_budget(module_id, tier)

    budget.consume(1)

    return budget.is_exhausted()


def check_budget_for_gate(module_id: str, tier: str = "P0", break_glass: bool = False) -> dict[str, object]:
    if break_glass:
        return {"allowed": True, "reason": "BREAK_GLASS", "requires": "Owner approval + audit chain"}

    budget = get_or_create_budget(module_id, tier)

    if budget.is_exhausted():
        if tier == "P0":
            return {"allowed": False, "reason": "HARD_LIMIT_P0"}

        elif tier == "P1":
            return {"allowed": False, "reason": "DOWNGRADED_P3"}

        else:
            return {"allowed": True, "reason": "WARNING_P2"}

    return {"allowed": True, "reason": "OK"}


# ── Checkpoint + Recovery ───────────────────────────────────


class CheckpointWriter:
    @staticmethod
    def write(
        scan_id: uuid.UUID, completed_detectors: list[str], scan_start_time: str, project_root: str | None = None
    ) -> None:
        # NOTE: _ENGINE_ROOT is set in drift_engine.py via _resolve_paths().

        # We use a heuristic fallback if project_root is not provided.

        root = project_root

        if not root:
            # 5.155.11 修复：原回退os.getcwd()可能指向任意目录，改用REPO_ROOT SSoT
            from zephyr.shared.io.paths import REPO_ROOT

            root = os.environ.get("ZEPHYR_PROJECT_ROOT") or str(REPO_ROOT)

        ckpt_dir = (
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(root))), "data", "drift_checkpoints")
            if "drift-detector" in root
            else os.path.join(root, "data", "drift_checkpoints")
        )

        os.makedirs(ckpt_dir, exist_ok=True)

        global _checkpoints_dir

        _checkpoints_dir = ckpt_dir

        ckpt_path = os.path.join(ckpt_dir, f"{scan_id}.json")

        data = {
            "scan_id": str(scan_id),
            "completed_detectors": completed_detectors,
            "last_checkpoint_time": datetime.now(UTC).isoformat(),
            "scan_start_time": scan_start_time,
        }

        tmp_path = f"{ckpt_path}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)

                fh.flush()

                os.fsync(fh.fileno())

            os.replace(tmp_path, ckpt_path)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass

    @staticmethod
    def cleanup(scan_id: uuid.UUID) -> None:
        if _checkpoints_dir:
            ckpt_path = os.path.join(_checkpoints_dir, f"{scan_id}.json")

            if os.path.exists(ckpt_path):
                os.remove(ckpt_path)


class RecoveryManager:
    @staticmethod
    def check_orphaned(_project_root: str | None = None) -> list[str]:
        ckpt_dir = _checkpoints_dir

        if not ckpt_dir or not os.path.isdir(ckpt_dir):
            return []

        orphaned: list[str] = []

        cutoff = datetime.now(UTC) - timedelta(hours=24)

        for fname in os.listdir(ckpt_dir):
            if not fname.endswith(".json"):
                continue

            full = os.path.join(ckpt_dir, fname)

            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=UTC)

                if mtime < cutoff:
                    orphaned.append(fname.replace(".json", ""))

            except OSError:
                pass

        return orphaned

    @staticmethod
    def on_startup(_project_root: str | None = None) -> dict[str, object] | None:
        ckpt_dir = _checkpoints_dir

        if not ckpt_dir or not os.path.isdir(ckpt_dir):
            return None

        try:
            file_paths = [os.path.join(ckpt_dir, f) for f in sorted(os.listdir(ckpt_dir)) if f.endswith(".json")]
            cached: list[tuple[object, datetime]] = []
            for full in file_paths:
                with open(full, encoding="utf-8") as fh:
                    data = json.load(fh)
                mtime = datetime.fromtimestamp(os.path.getmtime(full), tz=UTC)
                cached.append((data, mtime))
            for data, mtime in cached:
                if (datetime.now(UTC) - mtime) > timedelta(hours=24):
                    continue
                return data
        except (json.JSONDecodeError, OSError):
            pass

        return None


# ── Environment Awareness ──────────────────────────────────


_module_env_tags: dict[str, dict[str, str]] = {}


def register_env_tags(module_id: str, tags: dict[str, str]) -> None:
    _module_env_tags[module_id] = tags


@dataclass
class EnvDiffReport:
    module_id: str

    diff_type: str

    env_tags: dict[str, str] = field(default_factory=dict)

    is_true_drift: bool = True


def differential_detection(
    module_id: str, diffs: list[dict[str, object]], env_tags: dict[str, str] | None = None
) -> EnvDiffReport:
    tags = env_tags or _module_env_tags.get(module_id, {})

    env_diff_count = 0

    drift_count = 0

    for d in diffs:
        dim = str(d.get("drift_dimension", ""))

        if "env" in dim.lower() or "config_profile" in dim or "python_version" in dim:
            env_diff_count += 1

        else:
            drift_count += 1

    is_drift = drift_count > 0 or (env_diff_count > 0 and not tags)

    return EnvDiffReport(
        module_id=module_id,
        diff_type="ENV_DIFF" if not is_drift else "DRIFT",
        env_tags=tags,
        is_true_drift=is_drift,
    )


# ── Partial Deployment Detection ────────────────────────────


@dataclass
class PartialDeploymentRecord:
    module_a: str

    module_b: str

    started_at: datetime

    is_stalled: bool = False


_partial_deployments: dict[str, PartialDeploymentRecord] = {}


def detect_partial_deployment(module_ids: list[str]) -> PartialDeploymentRecord | None:
    if len(module_ids) < 2:
        return None

    key = "_".join(sorted(module_ids[:2]))

    now = datetime.now(UTC)

    if key not in _partial_deployments:
        rec = PartialDeploymentRecord(module_a=module_ids[0], module_b=module_ids[1], started_at=now)

        _partial_deployments[key] = rec

        return rec

    rec = _partial_deployments[key]

    if (now - rec.started_at).total_seconds() > 86400:
        rec.is_stalled = True

    return rec
