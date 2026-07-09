# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.system_snapshot
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_system_snapshot | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SystemSnapshotter — M1 系统状态镜像（CL-017 RI 扩展模式）
==========================================================
任务编号 : T-V2-006（experimental）
权限层级 : AI-Modifiable（快照输出）/ Human-Gated（门禁通过率阈值）
真源声明 : ai_autonomy_authority_registry.yaml §2.11 (CL-017)
关联决策 : rationale-log R83（CL-017 升级为 RI 扩展模式）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
SystemSnapshot 是 M1 build() pipeline 末尾生成的系统状态镜像，记录：

  1. 模块版本（module_versions）— 关键子模块版本字符串
  2. Provenance 指纹（provenance_fingerprint）— architecture-rationale-log.md 的 SHA-256
  3. 门禁注册表哈希（registry_hashes）— G1~G4 各 YAML 文件的 SHA-256
  4. 蓝图 V-12 通过率（blueprint_v12_pass_rate）— 从 SQLite gates 表统计

输出路径：.runtime/snapshots/<timestamp>Z.json（UTC ISO 8601，符号 ":"->"T"）

设计原则
--------
- SystemSnapshot：Pydantic v2 frozen（不可变快照）
- SystemSnapshotter.capture()：M1 backward 兼容（现有调用方无需改动）
- 快照写入失败时仅 warn，不抛出异常（不阻断 M1 主流程）
- TTL 30 天归档由 T-V2-013（V-16 归档脚本）负责
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import warnings
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from zephyr.shared.io.paths import (
    DB_PATH as DB_PATH_DEFAULT,
)
from zephyr.shared.io.paths import (
    GATES_DIR,
    REPO_ROOT,
    SNAPSHOTS_DIR,
)

_logger = logging.getLogger(__name__)
_UTC = UTC

# 已知关键子模块（用于版本收集）
_MODULE_MANIFESTS: dict[str, str] = {
    "zephyr.governance.rule_enforcement.gate_engine": "v1.0.0",
    "zephyr.governance.rule_enforcement.circuit_breaker": "v1.0.0",
    "zephyr.autonomy_core.system_snapshot": "v1.0.0",
    "zephyr.autonomy_core.doc_compressor": "v1.0.0",
    "zephyr.autonomy_core.context.context_budget_tracker": "v1.0.0",
    "zephyr.shared.capability": "v1.0.0",
    "zephyr.security.llm_defense.llm_security.process_sandbox": "v1.0.0",
    "zephyr.governance.persistence.sqlite_schema": "v1.0.0",
}

_GATE_FILES: dict[str, str] = {
    "G1": "g1-ingest.yaml",
    "G2": "g2-triage.yaml",
    "G3": "g3-evaluate.yaml",
    "G4": "g4-activate.yaml",
    "G5": "g5-extract.yaml",
}

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class SystemSnapshot(BaseModel):
    """M1 系统状态镜像（Pydantic v2 frozen）。

    字段
    ----
    timestamp
        快照生成时间（UTC ISO 8601）。
    module_versions
        关键子模块版本字典；键为 "zephyr.<module>" 格式。
    provenance_fingerprint
        architecture-rationale-log.md 的 SHA-256 哈希（前 16 字节十六进制）。
        日志不存在时为 "unavailable"。
    registry_hashes
        G1~G4 门禁 YAML 文件的 SHA-256 哈希字典。
    blueprint_v12_pass_rate
        V-12 蓝图门禁（G4 gate）通过率 [0, 1]；数据库不可用时为 -1.0（哨兵值）。
    """

    model_config = ConfigDict(frozen=True)

    timestamp: str
    module_versions: dict[str, str]
    provenance_fingerprint: str
    registry_hashes: dict[str, str]
    blueprint_v12_pass_rate: float = Field(ge=-1.0, le=1.0)


# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class SnapshotBuildError(RuntimeError):
    """系统快照构建失败（不抛出到 M1 主流程，仅内部记录）。"""

    error_code = "ZA-IF-0003"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


# ---------------------------------------------------------------------------
# SystemSnapshotter
# ---------------------------------------------------------------------------


class SystemSnapshotter:
    """M1 内部组件：在 build() pipeline 末尾生成系统状态镜像。

    参数
    ----
    repo_root
        仓库根目录；默认自动推断。
    snapshots_dir
        快照输出目录；默认 .runtime/snapshots/。
    db_path
        SQLite 数据库路径（用于查询 G4 通过率）；默认 DB_PATH_DEFAULT。
    gates_dir
        门禁 YAML 所在目录；默认 src/zephyr/governance/rule_enforcement/。
    module_manifests
        模块版本字典；默认 _MODULE_MANIFESTS（运行时可覆盖以注入真实版本）。

    M1 backward 兼容
    ----------------
    capture() 调用失败时仅发出 UserWarning，不抛出异常，
    确保现有 M1 build() 调用方不受影响。
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        snapshots_dir: Path | None = None,
        db_path: Path | None = None,
        gates_dir: Path | None = None,
        module_manifests: dict[str, str] | None = None,
    ) -> None:
        self._repo_root = repo_root or REPO_ROOT
        self._snapshots_dir = snapshots_dir or SNAPSHOTS_DIR
        self._db_path = db_path or DB_PATH_DEFAULT
        self._gates_dir = gates_dir or GATES_DIR
        self._module_manifests = dict(module_manifests) if module_manifests is not None else dict(_MODULE_MANIFESTS)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def capture(self) -> tuple[SystemSnapshot, Path | None]:
        """构建 SystemSnapshot 并持久化到 .runtime/snapshots/。

        返回
        ----
        (snapshot, path)
            path 为实际写入路径；写入失败时为 None（快照对象仍返回）。

        M1 backward 兼容保证
        --------------------
        任何内部错误仅发出 UserWarning，不向上层传播异常。
        """
        try:
            snapshot = self._build_snapshot()
        except Exception as exc:
            warnings.warn(
                f"[SystemSnapshotter] 快照构建失败（非致命）：{exc}",
                stacklevel=2,
            )
            _logger.warning("SystemSnapshotter.capture 失败: %s", exc, exc_info=True)
            return self._empty_snapshot(), None

        path = self._persist(snapshot)
        return snapshot, path

    # ------------------------------------------------------------------
    # 内部：构建
    # ------------------------------------------------------------------

    def _build_snapshot(self) -> SystemSnapshot:
        """聚合各来源数据，构建 SystemSnapshot 对象。"""
        return SystemSnapshot(
            timestamp=datetime.now(_UTC).isoformat(),
            module_versions=self._collect_module_versions(),
            provenance_fingerprint=self._compute_provenance_fingerprint(),
            registry_hashes=self._compute_registry_hashes(),
            blueprint_v12_pass_rate=self._compute_blueprint_pass_rate(),
        )

    def _collect_module_versions(self) -> dict[str, str]:
        """收集关键子模块版本。

        使用静态 manifests 字典（真实版本由 Owner 更新）。
        升级为读取 pyproject.toml 或 importlib.metadata。
        """
        versions: dict[str, str] = {}
        for module_name, version in self._module_manifests.items():
            versions[module_name] = version
        return versions

    def _compute_provenance_fingerprint(self) -> str:
        """计算 architecture-rationale-log.md 的 SHA-256 指纹（前 16 字节）。

        文件不存在时返回 "unavailable"。
        """
        log_path = self._repo_root / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"
        if not log_path.exists():
            return "unavailable"
        try:
            raw = log_path.read_bytes()
            return hashlib.sha256(raw).hexdigest()[:32]
        except OSError:
            return "read_error"

    def _compute_registry_hashes(self) -> dict[str, str]:
        """计算 G1~G5 门禁 YAML 文件的 SHA-256 哈希。

        YAML 文件不存在时对应哈希值为 "missing"。
        """
        hashes: dict[str, str] = {}
        for gate_id, filename in _GATE_FILES.items():
            yaml_path = self._gates_dir / filename
            if not yaml_path.exists():
                hashes[gate_id] = "missing"
                continue
            try:
                raw = yaml_path.read_bytes()
                hashes[gate_id] = hashlib.sha256(raw).hexdigest()[:16]
            except OSError:
                hashes[gate_id] = "read_error"
        return hashes

    def _compute_blueprint_pass_rate(self) -> float:
        """从 SQLite gate_runs 表查询 G4 门禁通过率。

        - 数据库不存在或无数据时返回 -1.0（哨兵值，表示"不可用"）
        - 有数据时返回 [0.0, 1.0]
        """
        if not self._db_path.exists():
            return -1.0
        try:
            conn = get_db_connection(str(self._db_path), timeout=5.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS passed "
                "FROM gate_runs WHERE gate_id LIKE 'G4%'"
            )
            row = cursor.fetchone()
            conn.close()
            if row is None or row["total"] == 0:
                return -1.0
            return round(row["passed"] / row["total"], 4)
        except Exception:
            return -1.0

    # ------------------------------------------------------------------
    # 内部：持久化
    # ------------------------------------------------------------------

    def _persist(self, snapshot: SystemSnapshot) -> Path | None:
        """将 SystemSnapshot 写入 JSON 文件。

        文件名：<timestamp_safe>Z.json（":"->"-"，适合文件名）
        写入失败时发出 UserWarning 并返回 None。
        """
        try:
            self._snapshots_dir.mkdir(parents=True, exist_ok=True)
            ts_safe = snapshot.timestamp.replace(":", "-").replace("+", "Z").split("Z")[0]
            filename = f"{ts_safe}Z.json"
            output_path = self._snapshots_dir / filename
            output_path.write_text(
                json.dumps(snapshot.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )
            _logger.info("SystemSnapshot 已写入：%s", output_path)
            return output_path
        except Exception as exc:
            warnings.warn(
                f"[SystemSnapshotter] 快照写入失败（非致命）：{exc}",
                stacklevel=3,
            )
            return None

    def _empty_snapshot(self) -> SystemSnapshot:
        """构建失败时返回的空快照（哨兵对象，不写磁盘）。"""
        return SystemSnapshot(
            timestamp=datetime.now(_UTC).isoformat(),
            module_versions={},
            provenance_fingerprint="unavailable",
            registry_hashes={},
            blueprint_v12_pass_rate=-1.0,
        )

    # ------------------------------------------------------------------
    # 便捷类方法：供 M1.build() 一行调用
    # ------------------------------------------------------------------

    @classmethod
    def run_in_build(
        cls,
        *,
        repo_root: Path | None = None,
        snapshots_dir: Path | None = None,
        db_path: Path | None = None,
    ) -> tuple[SystemSnapshot, Path | None]:
        """M1 build() pipeline 末尾的一行调用接口。

        示例（在 M1.build() 倒数第二步追加）：
            snapshot, path = SystemSnapshotter.run_in_build()
            logger.info("snapshot: %s", path)

        参数全部可选，保持 M1 backward 兼容。
        """
        snapshotter = cls(
            repo_root=repo_root,
            snapshots_dir=snapshots_dir,
            db_path=db_path,
        )
        return snapshotter.capture()


class CESnapshot(BaseModel):
    """CE 系统状态快照——轻量级运行时状态采集。

    用于 Inject 阶段参考系统当前状况。
    """

    model_config = ConfigDict(frozen=True)

    active_sessions: int = Field(default=0, ge=0, description="当前活跃 Agent session 数")
    vms_connected: bool = Field(default=False, description="VMS 连接状态")
    ce_pipeline_stats: dict[str, float] = Field(
        default_factory=dict,
        description="CE pipeline 各阶段耗时 (ms): build/compress/validate/inject",
    )
    memory_usage_mb: float = Field(default=0.0, ge=0.0, description="内存使用 (MB)")
    timestamp: str = Field(default="", description="快照时间戳 (ISO 8601)")


def take_snapshot() -> CESnapshot:
    """采集系统运行状态快照。

    零外部依赖——可独立调用。

    Returns
    -------
    CESnapshot
        不可变快照对象
    """
    memory_mb = _get_memory_usage_mb()
    timestamp = datetime.now(UTC).isoformat()

    return CESnapshot(
        active_sessions=_count_active_sessions(),
        vms_connected=_check_vms_connection(),
        ce_pipeline_stats=_get_pipeline_stats(),
        memory_usage_mb=memory_mb,
        timestamp=timestamp,
    )


def _get_memory_usage_mb() -> float:
    try:
        import psutil

        return round(psutil.Process().memory_info().rss / (1024 * 1024), 2)
    except ImportError:
        pass
    try:
        import os

        if hasattr(os, "sysconf") and hasattr(os, "confstr"):
            return 0.0
    except Exception as e:
        _logger.warning("suppressed error in system_snapshot", exc_info=True)
    return 0.0


def _count_active_sessions() -> int:
    try:
        from pathlib import Path

        runtime_dir = Path(".runtime/sessions")
        if runtime_dir.exists():
            return len(list(runtime_dir.glob("*.json")))
    except Exception as e:
        _logger.warning("suppressed error in system_snapshot", exc_info=True)
    return 0


def _check_vms_connection() -> bool:
    try:
        from pathlib import Path

        vms_dir = Path(".runtime/vms")
        return vms_dir.exists()
    except Exception as e:
        _logger.warning("suppressed error in system_snapshot", exc_info=True)
    return False


def _get_pipeline_stats() -> dict[str, float]:
    try:
        from pathlib import Path

        stats_file = Path(".runtime/ce_pipeline_stats.json")
        if stats_file.exists():
            import json

            data = json.loads(stats_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {k: float(v) for k, v in data.items()}
    except Exception as e:
        _logger.warning("suppressed error in system_snapshot", exc_info=True)
    return {"build_ms": 0.0, "compress_ms": 0.0, "validate_ms": 0.0, "inject_ms": 0.0}
