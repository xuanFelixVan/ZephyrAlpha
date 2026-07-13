# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [MODULE] zephyr.governance.ops_governance.auto_runner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
# [CONSUMERS] phase_manager; gate_engine; session_manager
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] auto_runner.run() MUST exit 0 on success; auto_close MUST release all resources
# [MODIFY-GUARD] docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AutoRunnerError on failure; RuntimeError on resource leak
# [TESTS] tests/test_auto_runner.py
# [A_module] module_id=MOD-GOV_auto_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""GovernanceAutoRunner — 治理脚本自动运行/自动关闭调度器.

基于 phase_manager 调度和 event_driven 触发自动执行 7 维度治理 gate。
执行完成后自动释放资源、清理临时文件、记录审计日志、关闭 session。

职责:
- 自动运行: 按 PHASE_SEQUENCE 顺序执行 7 维度 gate_checks
- 自动关闭: 资源释放 + 临时文件清理 + 审计日志 + session 关闭
- 事件驱动: 基于 depgraph 中 event_driven 字段触发对应脚本
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

logger = logging.getLogger(__name__)

__all__: list[str] = ["GovernanceAutoRunner", "AutoRunnerResult"]


class AutoRunnerResult:
    """自动运行结果。"""

    def __init__(self) -> None:
        self.started_at: str = datetime.now(timezone.utc).isoformat()
        self.finished_at: str | None = None
        self.total_gates: int = 0
        self.passed_gates: int = 0
        self.failed_gates: int = 0
        self.skipped_gates: int = 0
        self.errors: list[str] = []
        self.cleanup_done: bool = False
        self.audit_logged: bool = False

    @property
    def success(self) -> bool:
        return self.failed_gates == 0 and self.cleanup_done and self.audit_logged

    def __repr__(self) -> str:
        return (
            f"AutoRunnerResult(success={self.success}, "
            f"total={self.total_gates}, passed={self.passed_gates}, "
            f"failed={self.failed_gates}, cleanup={self.cleanup_done})"
        )


class GovernanceAutoRunner:
    """治理脚本自动运行/自动关闭调度器。

    使用方法:
        runner = GovernanceAutoRunner()
        result = runner.run()
        if result.success:
            print("ok")
    """

    def __init__(self) -> None:
        self._result = AutoRunnerResult()
        self._resources: list[Any] = []
        self._temp_files: list[Path] = []

    def run(self) -> AutoRunnerResult:
        """执行自动运行 + 自动关闭的完整流程。

        步骤:
        1. 加载 phase_manager 的 PHASE_SEQUENCE
        2. 按阶段顺序执行 gate_checks
        3. 自动关闭: 清理资源 + 临时文件 + 审计日志
        """
        logger.info("GovernanceAutoRunner.run() started")

        try:
            self._run_gates()
        except Exception as e:
            self._result.errors.append(f"gate execution error: {e}")
            logger.error("Gate execution error: %s", e, exc_info=True)
        finally:
            self._auto_close()

        self._result.finished_at = datetime.now(timezone.utc).isoformat()
        logger.info("GovernanceAutoRunner.run() finished: %s", self._result)
        return self._result

    def _run_gates(self) -> None:
        """按阶段顺序执行 gate_checks。"""
        from zephyr.governance.ops_governance.phase_manager import (
            PHASE_SEQUENCE,
            ConstructionPhase,
        )

        # 收集所有治理 gate
        # ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，从 PHASE_SEQUENCE 派生
        all_gov_gates: list[str] = []
        for phase_gate in PHASE_SEQUENCE.values():
            all_gov_gates.extend(phase_gate.gate_checks)

        self._result.total_gates = len(all_gov_gates)

        # 按阶段顺序执行
        for phase in ConstructionPhase:
            phase_gate = PHASE_SEQUENCE.get(phase)
            if phase_gate is None:
                continue

            for check_name in phase_gate.gate_checks:
                if check_name not in all_gov_gates:
                    continue

                try:
                    result = self._execute_gate(check_name)
                    if result:
                        self._result.passed_gates += 1
                    else:
                        self._result.failed_gates += 1
                        self._result.errors.append(f"gate {check_name} failed")
                except Exception as e:
                    self._result.failed_gates += 1
                    self._result.errors.append(f"gate {check_name} error: {e}")
                    logger.warning("Gate %s error: %s", check_name, e, exc_info=True)

        # 未执行的 gate 标记为 skipped
        executed = self._result.passed_gates + self._result.failed_gates
        self._result.skipped_gates = self._result.total_gates - executed

    def _execute_gate(self, gate_name: str) -> bool:
        """执行单个 gate check。fail-closed: gate 异常时返回 False（不视为通过）。"""
        try:
            from zephyr.governance.ops_governance.phase_check_registry import run_check
            from zephyr.governance.ops_governance.phase_manager import GateResult

            result = run_check(gate_name)
            return result == GateResult.GREEN
        except Exception as e:
            # fail-closed: gate 不存在或执行失败时，视为未通过（不静默放行）
            logger.warning("Gate %s execution failed: %s", gate_name, e, exc_info=True)
            return False

    def _auto_close(self) -> None:
        """自动关闭: 资源释放 + 临时文件清理 + 审计日志。"""
        logger.info("Auto-close started")

        # 1. 释放资源
        for resource in self._resources:
            try:
                if hasattr(resource, "close"):
                    resource.close()
            except Exception as e:
                logger.warning("Resource close error: %s", e, exc_info=True)
        self._resources.clear()

        # 2. 清理临时文件
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                logger.warning("Temp file cleanup error: %s", e, exc_info=True)
        self._temp_files.clear()

        # 3. 记录审计日志
        try:
            self._write_audit_log()
            self._result.audit_logged = True
        except Exception as e:
            logger.error("Audit log error: %s", e, exc_info=True)
            self._result.errors.append(f"audit log error: {e}")

        # 4. 标记清理完成
        self._result.cleanup_done = True
        logger.info("Auto-close finished")

    def _write_audit_log(self) -> None:
        """写入审计日志到 PostgreSQL governance_audit_logs 表.

        表结构由 02_create_pg_schema.sql 创建（8列含 skipped_gates）。
        P2迁移后：从 SQLite 切换到 PostgreSQL，使用 psycopg2 cursor 模式。
        """
        try:
            conn = get_depgraph_pg_connection(autocommit=False)
        except (psycopg2.Error, FileNotFoundError, ValueError) as e:
            # 5.170.1 修复: 审计日志 PG 连接失败属于系统级故障, 应为 error 而非 warning
            logger.error("_write_audit_log: PG 连接失败: %s", e)
            return

        try:
            with conn.cursor() as cur:
                # 表已由 02_create_pg_schema.sql 创建，无需兜底建表
                cur.execute(
                    "INSERT INTO governance_audit_logs "
                    "(timestamp, total_gates, passed_gates, failed_gates, skipped_gates, success, errors) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        self._result.started_at,
                        self._result.total_gates,
                        self._result.passed_gates,
                        self._result.failed_gates,
                        self._result.skipped_gates,
                        1 if self._result.success else 0,
                        "; ".join(self._result.errors[:10]),
                    ),
                )
            conn.commit()
        except psycopg2.Error as e:
            # 5.170.2 修复: 审计日志 INSERT 失败属于系统级故障, 应为 error 而非 warning
            logger.error("_write_audit_log: 写入审计日志失败: %s", e)
            conn.rollback()
        finally:
            conn.close()

    def register_resource(self, resource: Any) -> None:
        """注册需要在关闭时释放的资源。"""
        self._resources.append(resource)

    def register_temp_file(self, path: Path) -> None:
        """注册需要在关闭时清理的临时文件。"""
        self._temp_files.append(path)

    @staticmethod
    def get_gates_by_event(event_type: str) -> list[str]:
        """从 depgraph (PostgreSQL) 查询指定 event_driven 触发器的 gate 列表.

        全景图是项目真源——event_driven 配置存储在 gates 表 event_driven 列。
        P2迁移后：从 SQLite 切换到 PostgreSQL，使用 psycopg2 cursor 模式。

        Args:
            event_type: 事件类型（always/on_commit/on_file_change/on_session_start/
                        on_session_end/on_rule_change）

        Returns:
            list[str]: 匹配的 gate_id 列表；DB不可用时返回空列表
        """
        try:
            conn = get_depgraph_pg_connection(autocommit=True)
        except (psycopg2.Error, FileNotFoundError, ValueError) as e:
            logger.warning("get_gates_by_event(%s) PG 连接失败: %s", event_type, e)
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT gate_id FROM gates "
                    "WHERE event_driven=%s AND status='active' AND auto_start=1 "
                    "ORDER BY gate_id",
                    (event_type,),
                )
                rows = cur.fetchall()
            return [r[0] for r in rows]
        except psycopg2.Error as e:
            logger.warning("get_gates_by_event(%s) failed: %s", event_type, e)
            return []
        finally:
            conn.close()

    @staticmethod
    def get_all_event_types() -> list[str]:
        """从 depgraph (PostgreSQL) 查询所有非空的 event_driven 类型。"""
        try:
            conn = get_depgraph_pg_connection(autocommit=True)
        except (psycopg2.Error, FileNotFoundError, ValueError) as e:
            logger.warning("get_all_event_types PG 连接失败: %s", e)
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT event_driven FROM gates "
                    "WHERE status='active' AND event_driven != '' "
                    "ORDER BY event_driven"
                )
                rows = cur.fetchall()
            return [r[0] for r in rows]
        except psycopg2.Error as e:
            logger.warning("get_all_event_types failed: %s", e)
            return []
        finally:
            conn.close()


def main() -> None:
    """CLI 入口。"""
    runner = GovernanceAutoRunner()
    result = runner.run()
    if result.success:
        print("ok")
    else:
        print(f"failed: {result.errors}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()