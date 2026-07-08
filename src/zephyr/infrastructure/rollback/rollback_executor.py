# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_executor
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.governance.audit_trail.writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_executor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackExecutor — 回滚执行器核心封装。

依据：
    蓝图 MOD-INF-021 §2.1 双轨数据模型 + §2.2 回滚流程
    盲点 B2/B4/B5/B9/B48/B51
    决策 D-021-01 (git-native) + D-021-04 (dual-track) + D-021-05 (失败信号三分类)

四级回滚操作：
    - full_revert:      git revert 全部 commit + SQLite dump restore
    - partial_revert:   按 file_globs 选择性 revert
    - discard:          丢弃未提交变更（git checkout -- {files}）
    - hard_reset:       git reset --hard {commit_sha}（token-gated）

两套流程区分 (B2 鸡与蛋悖论解决)：
    - 已 commit 但后验失败 -> git revert（有可 revert 的对象）
    - pre-commit FAIL   -> discard changes（git checkout/restore——代码尚未被 commit）

回滚流程：
    preflight_check -> is_committed? -> revert or discard -> verify -> audit
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from zephyr.infrastructure.runtime.concurrency_guard import (
    check_rollback_conflict,
    classify_uncommitted_files,
)
from zephyr.infrastructure.rollback.rollback_lock import LockPriority, RollbackLock
from zephyr.infrastructure.rollback.sqlite_dumper import SqliteDumper
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_AUDIT_AVAILABLE = False
try:
    from zephyr.governance.audit_trail.writer import AuditWriter as _CoreAuditWriter

    _AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None

__all__ = [
    "DiscardDecision",
    "DiscardResult",
    "PreflightResult",
    "PreviewResult",
    "RollbackExecutor",
    "RollbackOp",
    "RollbackExecutionResult",
]


class RollbackOp(str, Enum):
    FULL_REVERT = "full_revert"
    PARTIAL_REVERT = "partial_revert"
    DISCARD = "discard"
    HARD_RESET = "hard_reset"


class DiscardDecision(str, Enum):
    DISCARD = "discard"
    REVERT = "revert"
    BLOCKED_BY_OWNER = "blocked_by_owner"
    NO_CHANGES = "no_changes"


@dataclass
class PreflightResult:
    passed: bool
    working_tree_clean: bool
    not_detached_head: bool
    remote_not_ahead: bool
    not_in_rebase: bool
    not_in_merge: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class PreviewResult:
    changed_files: list[str] = field(default_factory=list)
    conflict_risk: str = "low"
    estimated_change_bytes: int = 0
    db_tables_affected: int = 0


@dataclass
class RollbackExecutionResult:
    success: bool
    operation: RollbackOp
    commit_sha: str
    files_reverted: int
    db_tables_restored: int
    db_rows_restored: int
    execution_id: str = ""
    errors: list[str] = field(default_factory=list)
    exit_code: int = 0
    exit_code_resolution: dict[str, str] = field(default_factory=dict)


@dataclass
class DiscardResult:
    success: bool
    files_discarded: list[str]
    files_blocked: list[str]
    decision: DiscardDecision
    execution_id: str = ""
    audit_record: dict[str, Any] = field(default_factory=dict)


class RollbackExecutor:
    def __init__(
        self,
        project_root: Path | None = None,
        sqlite_dumper: SqliteDumper | None = None,
        rollback_lock: RollbackLock | None = None,
        owner_session_id: str | None = None,
    ) -> None:
        self._project_root = project_root or Path.cwd()
        self._dumper = sqlite_dumper or SqliteDumper()
        self._lock = rollback_lock or RollbackLock(project_root=self._project_root)
        self._owner_session_id = owner_session_id or self._resolve_env_owner()
        self._in_flight_dir = self._project_root / ".zephyr" / "rollback_in_flight"
        self._audit_writer: _CoreAuditWriter | None = None
        if _AUDIT_AVAILABLE:
            try:
                self._audit_writer = _CoreAuditWriter()
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞审计写入器初始化失败（审计链断链不可见）
                logger.warning("AuditWriter init failed; audit trail will fall back to jsonl", exc_info=True)

    def _generate_execution_id(self) -> str:
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"RBEXEC-{ts}-{short_uuid}"

    def _in_flight_path(self, execution_id: str) -> Path:
        return self._in_flight_dir / f"{execution_id}.json"

    def _write_in_flight(self, execution_id: str, step: str, status: str, data: dict[str, Any] | None = None) -> None:
        self._in_flight_dir.mkdir(parents=True, exist_ok=True)
        record: dict[str, Any] = {
            "execution_id": execution_id,
            "updated_at": datetime.now(UTC).isoformat(),
            "step": step,
            "status": status,
        }
        if data:
            record["data"] = data
        path = self._in_flight_path(execution_id)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_in_flight(self, execution_id: str) -> dict[str, Any] | None:
        path = self._in_flight_path(execution_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _delete_in_flight(self, execution_id: str) -> None:
        path = self._in_flight_path(execution_id)
        try:
            path.unlink(missing_ok=True)
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 in-flight 标记清理失败（残留标记会导致下次回滚误判）
            logger.debug("in-flight marker unlink failed for execution_id=%s", execution_id, exc_info=True)

    def _recover_stale_in_flight(self) -> list[str]:
        recovered: list[str] = []
        if not self._in_flight_dir.exists():
            return recovered
        for f in self._in_flight_dir.glob("*.json"):
            try:
                record = json.loads(f.read_text(encoding="utf-8"))
                status = record.get("status", "")
                step = record.get("step", "")
                if status == "FAILED":
                    execution_id = record.get("execution_id", f.stem)
                    self._write_in_flight(execution_id, step, "RECOVERING", {"recovered_from": f.stem})
                    recovered.append(execution_id)
            except (json.JSONDecodeError, KeyError):
                pass
        return recovered

    def _get_in_flight_status(self, execution_id: str) -> str | None:
        record = self._read_in_flight(execution_id)
        if record:
            return record.get("status")
        return None

    def preflight_check(self) -> PreflightResult:
        errors: list[str] = []
        working_tree_clean = True
        not_detached_head = True
        remote_not_ahead = True
        not_in_rebase = True
        not_in_merge = True

        git_status = self._run_git(["status", "--porcelain"])
        if git_status.strip():
            working_tree_clean = False
            errors.append("Working tree is dirty")

        head_ref = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if head_ref.strip() == "HEAD":
            not_detached_head = False
            errors.append("Detached HEAD state")

        rebase_merge_dir = self._project_root / ".git" / "rebase-merge"
        rebase_apply_dir = self._project_root / ".git" / "rebase-apply"
        if rebase_merge_dir.exists() or rebase_apply_dir.exists():
            not_in_rebase = False
            errors.append("Rebase in progress")

        merge_head = self._project_root / ".git" / "MERGE_HEAD"
        if merge_head.exists():
            not_in_merge = False
            errors.append("Merge in progress")

        cherry_pick_head = self._project_root / ".git" / "CHERRY_PICK_HEAD"
        if cherry_pick_head.exists():
            errors.append("Cherry-pick in progress")

        try:
            merge_base = self._run_git(["merge-base", "HEAD", "origin/main"])
            remote_head = self._run_git(["rev-parse", "origin/main"])
            if merge_base.strip() != remote_head.strip():
                remote_not_ahead = False
                errors.append("Remote may be ahead of local")
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 git merge-base 检查失败（无 remote 时属预期，但仍需可观测）
            logger.debug("preflight merge-base check failed (expected if no remote)", exc_info=True)

        passed = len(errors) == 0
        return PreflightResult(
            passed=passed,
            working_tree_clean=working_tree_clean,
            not_detached_head=not_detached_head,
            remote_not_ahead=remote_not_ahead,
            not_in_rebase=not_in_rebase,
            not_in_merge=not_in_merge,
            errors=errors,
        )

    def preview(self, commit_sha: str) -> PreviewResult:
        changed = self._run_git(["diff", "--name-only", f"{commit_sha}..HEAD"])
        changed_files = [f for f in changed.strip().split("\n") if f]

        conflict_risk = "low"
        diff_stat = self._run_git(["diff", "--stat", f"{commit_sha}..HEAD"])
        estimated_bytes = len(diff_stat.encode("utf-8"))

        if len(changed_files) > 10:
            conflict_risk = "high"
        elif len(changed_files) > 5:
            conflict_risk = "medium"

        existing_merges = self._run_git(["log", "--oneline", "--merges", f"{commit_sha}..HEAD"])
        if existing_merges.strip():
            conflict_risk = "high"

        return PreviewResult(
            changed_files=changed_files,
            conflict_risk=conflict_risk,
            estimated_change_bytes=estimated_bytes,
        )

    def is_committed(self, files: list[str]) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for f in files:
            try:
                tracked = self._run_git(["ls-files", "--error-unmatch", f])
                result[f] = True
            except Exception:
                result[f] = False
        return result

    def get_uncommitted_files(self) -> list[str]:
        output = self._run_git(["diff", "--name-only", "HEAD"])
        unstaged = [f for f in output.strip().split("\n") if f]
        return unstaged

    def get_staged_uncommitted_files(self) -> list[str]:
        output = self._run_git(["diff", "--cached", "--name-only"])
        staged = [f for f in output.strip().split("\n") if f]
        return staged

    def _detect_owner_session_in_files(self, files: list[str]) -> list[str]:
        blocked: list[str] = []
        for f in files:
            try:
                log_output = self._run_git(["log", "-1", "--format=%an %ae %s", "--", f])
                if self._owner_session_id and self._owner_session_id in log_output:
                    blocked.append(f)
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞 git log 查询失败（owner 检测漏判不可见）
                logger.debug("git log owner detection failed for file=%s", f, exc_info=True)
        return blocked

    def discard_changes(
        self,
        file_list: list[str],
        force: bool = False,
        audit_session: str = "",
    ) -> DiscardResult:
        files_blocked: list[str] = []

        if not force:
            owner_files = self._detect_owner_session_in_files(file_list)
            if owner_files:
                files_blocked = owner_files
                audit_record = self._build_discard_audit(
                    decision=DiscardDecision.BLOCKED_BY_OWNER,
                    files=file_list,
                    blocked=owner_files,
                    reason=f"Owner session {self._owner_session_id} detected in: {owner_files}",
                    audit_session=audit_session,
                )
                return DiscardResult(
                    success=False,
                    files_discarded=[],
                    files_blocked=files_blocked,
                    decision=DiscardDecision.BLOCKED_BY_OWNER,
                    audit_record=audit_record,
                )

        uncommitted_files = self.get_uncommitted_files()
        staged_files = self.get_staged_uncommitted_files()
        all_uncommitted = set(uncommitted_files + staged_files)

        discardable = [f for f in file_list if f in all_uncommitted and f not in files_blocked]
        already_committed = [f for f in file_list if f not in all_uncommitted]

        if not discardable:
            audit_record = self._build_discard_audit(
                decision=DiscardDecision.NO_CHANGES,
                files=file_list,
                blocked=[],
                reason="No uncommitted changes to discard",
                audit_session=audit_session,
            )
            return DiscardResult(
                success=False,
                files_discarded=[],
                files_blocked=[],
                decision=DiscardDecision.NO_CHANGES,
                audit_record=audit_record,
            )

        files_discarded: list[str] = []
        for f in discardable:
            try:
                self._run_git(["checkout", "--", f])
                files_discarded.append(f)
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞 discard 失败（回滚失败不可见——最危险）
                logger.warning("git checkout discard failed for file=%s (rollback incomplete)", f, exc_info=True)

        for f in staged_files:
            if f in discardable:
                try:
                    self._run_git(["reset", "HEAD", "--", f])
                except Exception:
                    # 5.12.1 修复：原 except: pass 静默吞 staged reset 失败（staged 变更残留）
                    logger.warning("git reset HEAD failed for staged file=%s", f, exc_info=True)

        audit_record = self._build_discard_audit(
            decision=DiscardDecision.DISCARD,
            files=discardable,
            blocked=files_blocked,
            reason=f"Discarded {len(discardable)} uncommitted file(s)",
            audit_session=audit_session,
        )

        self._write_audit_log(audit_record)

        return DiscardResult(
            success=True,
            files_discarded=files_discarded,
            files_blocked=files_blocked,
            decision=DiscardDecision.DISCARD,
            audit_record=audit_record,
        )

    def rollback_or_discard(
        self,
        files: list[str],
        commit_sha: str = "",
        audit_session: str = "",
    ) -> DiscardResult:
        committal_status = self.is_committed(files)
        all_committed = all(committal_status.values())
        all_uncommitted = not any(committal_status.values())

        if all_uncommitted:
            return self.discard_changes(files, audit_session=audit_session)

        if all_committed:
            if not commit_sha:
                commit_sha = self._run_git(["rev-parse", "--short", "HEAD"]).strip()

            result = self.full_revert(commit_sha)

            audit_record = self._build_discard_audit(
                decision=DiscardDecision.REVERT,
                files=files,
                blocked=[],
                reason=f"Reverted to commit {commit_sha}: {result.files_reverted} files",
                audit_session=audit_session,
            )
            self._write_audit_log(audit_record)

            return DiscardResult(
                success=result.success,
                files_discarded=files,
                files_blocked=[],
                decision=DiscardDecision.REVERT,
                audit_record=audit_record,
            )

        committed = [f for f in files if committal_status.get(f, False)]
        uncommitted = [f for f in files if not committal_status.get(f, True)]

        result = self.discard_changes(uncommitted, audit_session=audit_session)

        if committed and commit_sha:
            revert_result = self.full_revert(commit_sha)

        audit_record = self._build_discard_audit(
            decision=DiscardDecision.DISCARD if uncommitted else DiscardDecision.REVERT,
            files=files,
            blocked=result.files_blocked,
            reason=f"Mixed: discarded {len(uncommitted)} uncommitted, reverted {len(committed)} committed",
            audit_session=audit_session,
        )
        self._write_audit_log(audit_record)

        return DiscardResult(
            success=result.success,
            files_discarded=result.files_discarded + uncommitted,
            files_blocked=result.files_blocked,
            decision=result.decision,
            audit_record=audit_record,
        )

    def full_revert(self, commit_sha: str, dry_run: bool = False, audit_session: str = "") -> RollbackExecutionResult:
        return self._execute(RollbackOp.FULL_REVERT, commit_sha, dry_run=dry_run, audit_session=audit_session)

    def partial_revert(
        self, commit_sha: str, file_globs: list[str], dry_run: bool = False, audit_session: str = ""
    ) -> RollbackExecutionResult:
        return self._execute(
            RollbackOp.PARTIAL_REVERT, commit_sha, file_globs=file_globs, dry_run=dry_run, audit_session=audit_session
        )

    def discard(self, files: list[str], audit_session: str = "") -> RollbackExecutionResult:
        return self._execute(RollbackOp.DISCARD, "", file_list=files, audit_session=audit_session)

    def hard_reset(self, commit_sha: str, token: str = "", audit_session: str = "") -> RollbackExecutionResult:
        if not token:
            raise ValueError("hard_reset requires a valid BREAK_GLASS token")
        self._lsg_verify_critical_operation("hard_reset", commit_sha)
        return self._execute(RollbackOp.HARD_RESET, commit_sha, token=token, audit_session=audit_session)

    def _lsg_verify_critical_operation(self, operation: str, target: str) -> None:
        try:
            _lsg_mod = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway")
            LSGSecurityGateway = _lsg_mod.LSGSecurityGateway

            gateway = LSGSecurityGateway()
            content = f"rollback:{operation} target:{target}"
            result = run_sync(gateway.scan_agent_action(content, tool_name=f"rollback_{operation}"))
            if result.decision.value not in ("allow", "ALLOW"):
                raise PermissionError(f"LSG blocked rollback operation: {operation}")
        except ImportError:
            pass

    def forward_fix_evaluate(self, commit_sha: str) -> bool:
        preview_result = self.preview(commit_sha)
        if preview_result.conflict_risk == "high":
            return False
        if len(preview_result.changed_files) <= 3:
            return True
        return False

    def dependency_impact_analysis(self, commit_sha: str) -> dict[str, Any]:
        changed = self._run_git(["diff", "--name-only", f"{commit_sha}..HEAD"])
        changed_files = [f for f in changed.strip().split("\n") if f]
        impacted_modules: set[str] = set()
        for f in changed_files:
            if "src/zephyr/" in f:
                parts = Path(f).parts
                for i, part in enumerate(parts):
                    if part == "zephyr" and i + 1 < len(parts):
                        impacted_modules.add(parts[i + 1])
                        break

        return {
            "changed_files": changed_files,
            "impacted_modules": sorted(impacted_modules),
            "impact_breadth": len(impacted_modules),
        }

    def _build_discard_audit(
        self,
        decision: DiscardDecision,
        files: list[str],
        blocked: list[str],
        reason: str,
        audit_session: str,
    ) -> dict[str, Any]:
        return {
            "audit_id": f"ROLLBACK-DISCARD-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "operation": "discard_routing",
            "decision": decision.value,
            "files_in_scope": files,
            "files_blocked": blocked,
            "reason": reason,
            "session_id": audit_session,
            "executor_version": "0.10.0",
        }

    def _write_audit_log(self, record: dict[str, Any]) -> None:
        if self._audit_writer is not None:
            try:
                event = dict(record)
                event["event_type"] = event.get("event_type", "rollback_discard")
                event["agent_id"] = event.get("agent_id", record.get("session_id", "rollback_executor"))
                self._audit_writer.write(event)
                return
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞审计写入失败（审计链断链不可见）
                logger.warning("AuditWriter.write failed for discard audit; falling back to jsonl", exc_info=True)
        try:
            audit_dir = REPO_ROOT / ".zephyr" / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_file = audit_dir / "rollback_discard_audit.jsonl"
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 jsonl 兜底写入失败（审计记录彻底丢失）
            logger.error("jsonl audit fallback write failed for discard audit (audit record LOST)", exc_info=True)

    def cancel_pending_rollback(self, task_id: str, reason: str, token: str = "") -> dict[str, Any]:
        if not token:
            return {"canceled": False, "task_id": task_id, "reason": "BREAK_GLASS token required"}
        canceled = False
        if self._in_flight_dir.exists():
            for f_path in self._in_flight_dir.glob("*.json"):
                try:
                    record = json.loads(f_path.read_text(encoding="utf-8"))
                    if record.get("status") in ("PENDING", "RETRYING"):
                        f_path.unlink(missing_ok=True)
                        canceled = True
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
        if canceled:
            self._write_op_audit(
                operation="BREAK_GLASS_CANCEL",
                commit_sha="",
                success=True,
                details={"task_id": task_id, "reason": reason},
                audit_session="BREAK_GLASS",
            )
        return {"canceled": canceled, "task_id": task_id, "reason": reason}

    def _resolve_env_owner(self) -> str | None:
        return os.environ.get("ZEPHYR_OWNER_SESSION_ID") or os.environ.get("OWNER_SESSION_ID")

    def _execute(
        self,
        operation: RollbackOp,
        commit_sha: str,
        file_globs: list[str] | None = None,
        file_list: list[str] | None = None,
        token: str = "",
        dry_run: bool = False,
        audit_session: str = "",
    ) -> RollbackExecutionResult:
        errors: list[str] = []
        files_reverted = 0
        db_tables_restored = 0
        db_rows_restored = 0
        g0_passed = False
        execution_id = self._generate_execution_id()
        stashed = False

        # === 并发安全守卫（方案C）：检测回滚文件是否与活跃文件锁冲突 ===
        files_to_check = self._resolve_conflict_files(operation, commit_sha, file_globs, file_list)
        if files_to_check:
            conflict = check_rollback_conflict(
                files_to_check,
                self._owner_session_id or audit_session or "auto",
                self._project_root,
            )
            if conflict.has_conflict:
                self._write_in_flight(execution_id, "concurrency_check", "BLOCKED", conflict.locked_by)
                self._write_op_audit(
                    operation=operation.value,
                    commit_sha=commit_sha,
                    success=False,
                    details={"error": "concurrency_conflict", "blocked_files": conflict.blocked_files, "execution_id": execution_id},
                    audit_session=audit_session,
                )
                return RollbackExecutionResult(
                    success=False,
                    operation=operation,
                    commit_sha=commit_sha,
                    files_reverted=0,
                    db_tables_restored=0,
                    db_rows_restored=0,
                    execution_id=execution_id,
                    errors=[f"Blocked by concurrency conflict: {conflict.locked_by}"],
                )

        self._write_in_flight(execution_id, "preflight", "PENDING")

        preflight = self.preflight_check()
        if not preflight.passed and operation is not RollbackOp.HARD_RESET:
            if preflight.errors and "Working tree is dirty" in str(preflight.errors):
                # === stash 安全化（方案C）：只 stash 本 session 的文件，其他 session 文件阻断 ===
                uncommitted = self.get_uncommitted_files() + self.get_staged_uncommitted_files()
                stash_plan = classify_uncommitted_files(
                    uncommitted,
                    self._owner_session_id or audit_session or "auto",
                    self._project_root,
                )
                if stash_plan.other_files:
                    self._write_in_flight(execution_id, "stash_check", "BLOCKED", {"other_files": stash_plan.other_files})
                    self._write_op_audit(
                        operation=operation.value,
                        commit_sha=commit_sha,
                        success=False,
                        details={"error": "other_session_uncommitted", "other_files": stash_plan.other_files, "execution_id": execution_id},
                        audit_session=audit_session,
                    )
                    return RollbackExecutionResult(
                        success=False,
                        operation=operation,
                        commit_sha=commit_sha,
                        files_reverted=0,
                        db_tables_restored=0,
                        db_rows_restored=0,
                        execution_id=execution_id,
                        errors=[f"Other session uncommitted files blocked stash: {stash_plan.other_files}"],
                    )
                self._run_git(["stash"])
                stashed = True
                self._write_in_flight(execution_id, "preflight", "SUCCESS", {"stashed": True})
            else:
                self._write_in_flight(execution_id, "preflight", "FAILED", {"errors": preflight.errors})
                self._write_op_audit(
                    operation=operation.value,
                    commit_sha=commit_sha,
                    success=False,
                    details={"error": str(preflight.errors), "execution_id": execution_id},
                    audit_session=audit_session,
                )
                return RollbackExecutionResult(
                    success=False,
                    operation=operation,
                    commit_sha=commit_sha,
                    files_reverted=0,
                    db_tables_restored=0,
                    db_rows_restored=0,
                    execution_id=execution_id,
                    errors=preflight.errors,
                )
        else:
            self._write_in_flight(execution_id, "preflight", "SUCCESS")

        lock_result = self._lock.acquire(
            owner=audit_session or self._owner_session_id or "auto",
            priority=LockPriority.NORMAL,
            task=operation.value,
        )

        if not lock_result.acquired:
            self._write_in_flight(execution_id, "acquire_lock", "FAILED", {"reason": lock_result.reason})
            return RollbackExecutionResult(
                success=False,
                operation=operation,
                commit_sha=commit_sha,
                files_reverted=0,
                db_tables_restored=0,
                db_rows_restored=0,
                execution_id=execution_id,
                errors=[f"Could not acquire rollback lock: {lock_result.reason}"],
            )

        self._write_in_flight(execution_id, "acquire_lock", "SUCCESS")

        try:
            if dry_run:
                preview = self.preview(commit_sha)
                result = RollbackExecutionResult(
                    success=True,
                    operation=operation,
                    commit_sha=commit_sha,
                    files_reverted=len(preview.changed_files),
                    db_tables_restored=0,
                    db_rows_restored=0,
                    execution_id=execution_id,
                )
            elif operation is RollbackOp.FULL_REVERT:
                self._write_in_flight(execution_id, "git_revert", "PENDING")
                git_result = self._git_revert(commit_sha)
                files_reverted = git_result.get("files_changed", 0)
                self._write_in_flight(execution_id, "git_revert", "SUCCESS", {"files_changed": files_reverted})
                self._write_in_flight(execution_id, "g0_verify", "PENDING")
                g0_passed = self._g0_verify()
                self._write_in_flight(execution_id, "g0_verify", "SUCCESS" if g0_passed else "FAILED")
            elif operation is RollbackOp.PARTIAL_REVERT:
                if not file_globs:
                    raise ValueError("partial_revert requires file_globs")
                self._write_in_flight(execution_id, "partial_revert", "PENDING")
                git_result = self._git_partial_revert(commit_sha, file_globs)
                files_reverted = git_result.get("files_changed", 0)
                self._write_in_flight(execution_id, "partial_revert", "SUCCESS", {"files_changed": files_reverted})
                g0_passed = self._g0_verify(files=file_globs)
                self._write_in_flight(execution_id, "g0_verify", "SUCCESS" if g0_passed else "FAILED")
            elif operation is RollbackOp.DISCARD:
                if not file_list:
                    raise ValueError("discard requires file_list")
                self._write_in_flight(execution_id, "discard", "PENDING")
                uncommitted = self.get_uncommitted_files()
                staged = self.get_staged_uncommitted_files()
                all_uncommitted = set(uncommitted + staged)
                discardable = [f for f in file_list if f in all_uncommitted]
                for f in discardable:
                    self._run_git(["checkout", "--", f])
                for f in staged:
                    if f in discardable:
                        self._run_git(["reset", "HEAD", "--", f])
                files_reverted = len(discardable)
                self._write_in_flight(execution_id, "discard", "SUCCESS", {"files_discarded": discardable})
            elif operation is RollbackOp.HARD_RESET:
                self._write_in_flight(execution_id, "hard_reset", "PENDING")
                self._run_git(["reset", "--hard", commit_sha])
                files_reverted = 0
                g0_passed = True
                self._write_in_flight(execution_id, "hard_reset", "SUCCESS")

            jsonl_path = Path(f"data/rollback/db_snapshots/{commit_sha}.jsonl")
            if jsonl_path.exists() and not dry_run:
                self._write_in_flight(execution_id, "db_restore", "PENDING")
                restore_result = self._dumper.restore(jsonl_path)
                db_tables_restored = restore_result.tables_restored
                db_rows_restored = restore_result.rows_restored
                self._write_in_flight(
                    execution_id, "db_restore", "SUCCESS", {"tables": db_tables_restored, "rows": db_rows_restored}
                )

            result = RollbackExecutionResult(
                success=True,
                operation=operation,
                commit_sha=commit_sha,
                files_reverted=files_reverted,
                db_tables_restored=db_tables_restored,
                db_rows_restored=db_rows_restored,
                execution_id=execution_id,
            )

            try:
                from zephyr.infrastructure.rollback.contract import resolve_exit_code

                _exit = resolve_exit_code(result.exit_code)
                object.__setattr__(result, "exit_code_resolution", _exit)
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞 exit_code 解析失败（门禁决策信号丢失）
                logger.debug("exit_code resolution failed for execution_id=%s", execution_id, exc_info=True)

            self._write_in_flight(execution_id, "complete", "SUCCESS")

            self._write_op_audit(
                operation=operation.value,
                commit_sha=commit_sha,
                success=True,
                details={
                    "files_reverted": files_reverted,
                    "db_tables_restored": db_tables_restored,
                    "g0_verified": g0_passed,
                    "execution_id": execution_id,
                },
                audit_session=audit_session,
            )

            return result
        except Exception as e:
            errors.append("internal error")
            self._write_in_flight(execution_id, "error", "FAILED", {"error": "internal error"})
            self._write_op_audit(
                operation=operation.value,
                commit_sha=commit_sha,
                success=False,
                details={"error": "internal error", "execution_id": execution_id},
                audit_session=audit_session,
            )
            return RollbackExecutionResult(
                success=False,
                operation=operation,
                commit_sha=commit_sha,
                files_reverted=files_reverted,
                db_tables_restored=db_tables_restored,
                db_rows_restored=db_rows_restored,
                execution_id=execution_id,
                errors=errors,
            )
        finally:
            self._lock.release(lock_result.lock_id)
            if stashed:
                try:
                    self._run_git(["stash", "pop"])
                    self._write_in_flight(execution_id, "stash_pop", "SUCCESS")
                except Exception as e:
                    self._write_in_flight(execution_id, "stash_pop", "FAILED", {"error": "internal error"})
            self._delete_in_flight(execution_id)

    def _resolve_conflict_files(
        self,
        operation: RollbackOp,
        commit_sha: str,
        file_globs: list[str] | None = None,
        file_list: list[str] | None = None,
    ) -> list[str]:
        """根据 operation 类型确定冲突检查的文件范围。"""
        if operation is RollbackOp.DISCARD:
            return list(file_list or [])
        if operation is RollbackOp.PARTIAL_REVERT:
            return list(file_globs or [])
        if operation is RollbackOp.FULL_REVERT:
            try:
                preview = self.preview(commit_sha)
                return list(preview.changed_files)
            except Exception:
                return []
        if operation is RollbackOp.HARD_RESET:
            try:
                output = self._run_git(["ls-files"])
                return [f for f in output.strip().split("\n") if f]
            except Exception:
                return []
        return []

    def _git_revert(self, commit_sha: str) -> dict[str, Any]:
        output = self._run_git(["revert", "--no-edit", commit_sha])
        diff_files = self._run_git(["diff-tree", "--no-commit-id", "-r", "HEAD"])
        files_changed = len([f for f in diff_files.strip().split("\n") if f])
        return {"output": output, "files_changed": files_changed}

    def _git_partial_revert(self, commit_sha: str, file_globs: list[str]) -> dict[str, Any]:
        self._run_git(["revert", "--no-commit", commit_sha])
        all_files = self._run_git(["diff", "--name-only", "HEAD~1..HEAD"])
        keep_files = [f for f in all_files.strip().split("\n") if f and f not in file_globs]
        for f in keep_files:
            self._run_git(["reset", "HEAD", "--", f])
            self._run_git(["checkout", "--", f])
        self._run_git(["commit", "-m", f"Partial revert: {commit_sha} [selected files]"])
        return {"files_changed": len(file_globs)}

    def _run_git(self, args: list[str], timeout: int = 10) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""

    def _g0_verify(self, files: list[str] | None = None) -> bool:
        try:
            import ast

            target_files = files or []
            if not target_files:
                output = self._run_git(["diff", "--name-only", "HEAD~1..HEAD"])
                target_files = [f for f in output.strip().split("\n") if f]

            py_files = [f for f in target_files if f.endswith(".py")]
            if not py_files:
                return True

            for py_file in py_files:
                full_path = self._project_root / py_file
                if not full_path.exists():
                    continue

                source = full_path.read_text(encoding="utf-8")
                try:
                    ast.parse(source)
                except SyntaxError:
                    return False

                if "def " not in source and "class " not in source:
                    continue

            cache_dirs = list(self._project_root.glob("**/__pycache__"))
            for cache_dir in cache_dirs:
                try:
                    shutil.rmtree(cache_dir)
                except Exception:
                    # 5.12.1 修复：原 except: pass 静默吞 pycache 清理失败（残留缓存可能导致后续导入幽灵模块）
                    logger.debug("pycache rmtree failed for %s", cache_dir, exc_info=True)

            return True
        except Exception:
            return False

    def _write_op_audit(
        self,
        operation: str,
        commit_sha: str,
        success: bool,
        details: dict[str, Any],
        audit_session: str,
    ) -> None:
        record = {
            "audit_id": f"ROLLBACK-OP-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "operation": operation,
            "commit_sha": commit_sha,
            "success": success,
            "details": details,
            "session_id": audit_session,
            "executor_version": "0.10.0",
        }
        if self._audit_writer is not None:
            try:
                event = dict(record)
                event["event_type"] = "rollback_operation"
                event["agent_id"] = audit_session or "rollback_executor"
                event["target_path"] = commit_sha
                event["status"] = "success" if success else "failed"
                self._audit_writer.write(event)
                return
            except Exception:
                # 5.12.1 修复：原 except: pass 静默吞操作审计写入失败（审计链断链不可见）
                logger.warning("AuditWriter.write failed for op audit; falling back to jsonl", exc_info=True)
        try:
            audit_dir = REPO_ROOT / ".zephyr" / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_file = audit_dir / "rollback_operations_audit.jsonl"
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # 5.12.1 修复：原 except: pass 静默吞 jsonl 兜底写入失败（操作审计记录彻底丢失）
            logger.error("jsonl audit fallback write failed for op audit (audit record LOST)", exc_info=True)
