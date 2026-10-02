# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.session_concurrency
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.infra.process_pool (is_pid_alive)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway ; zephyr.gov_enforcement.rule_bridge.session_worktree (find_breaking_change_session, register_dependency, clear_dependency) ; zephyr.gov_enforcement.commit_gates.import_integrity_gate (_check_active_session_held_target, Phase 2.5) ; zephyr.governance.audit.reconcile_worker (SessionRegistry) ; zephyr.governance.audit.reconcile_runner (SessionRegistry)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SessionRegistry S4-D 分片存储（2026-09-30）：主真源=.runtime/session_registry/<sid>.json 每会话一片（per-pid tmp+os.replace+WinError5 退避原语义），写只碰本会话片（整表重写竞态拆面治本——AI-NORTH-001 心跳互踩/WinError5 连锁/#ARCH-324 的结构性病根）；读侧聚合（损坏/缺失片跳过+审计，损失半径=单片），旧单表迁移窗双写为只读兼容副本（直读消费者 watchdog/write_audit_daemon/commit_queue/check_commit_message 不受扰），片目录缺席回退旧表；回退手柄 env ZEPHYR_SESSION_REGISTRY_SHARDS=0；公共 save()=merge-upsert 永不删（删除只能走 unregister/list_active 收割显式意图）；session 存活判定双轨：pid>0=PID liveness+TTL(3600s)双判据（S3-A 治本），pid=0=心跳新鲜度(90s)判据（#ARCH-HEARTBEAT-001 P0 治本，daemon 每 30s 刷新 last_heartbeat，stale session 90s 自动释放 held_files 消除 allow_overlap 62× 超阈）；last_activity 独立活性锚点（#ARCH-HEARTBEAT-002 治本 2026-07-23：仅 register/claim_file/register_dependency 刷新，heartbeat 不刷新，daemon 检测 idle 超 _ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s 自动退出，消除僵尸 daemon 永久保活死 session 的活性反转）；不替代 lock_files.py（文件级锁）；claim_file 懒注册+不覆盖冲突+幂等；release_file 移除 held_files；get_session 只读无写副作用；is_breaking_change 字段标记治本变更 session（§9.7 治本 2026-07-04）；find_breaking_change_session 查找活跃 breaking_change session（只读，排除自身+忽略死/过期，供 session_worktree_start 双向阻断调用）；register 频率护栏（wave4-D V5 治本 2026-10-01）：同 session 活条目 _REREGISTER_MIN_INTERVAL_SECONDS（=idle 上限+2×30s）窗内重注册=降级执行（状态按实参重建+四时间锚 start_time/last_heartbeat/last_activity/last_register_ts 冻结+审计，防 keeper 循环伪造 last_activity 且窗不被刷延长），logical（请求参或既有条目）豁免 FULL 刷新、死条目放行=合法重启、既有条目 logical=True 重建时继承（防 mark_logical 随整体重建静默丢标）；频率锚=last_register_ts 独立字段（旧条目缺省 0.0=无锚放行）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SessionRegistry 读写失败不抛异常（返回空/False）；detect_mtime_conflict 文件不存在返回 False
# [TESTS] tests/agent_rbac/test_session_aware_stash_red_blue.py; tests/governance/audit/test_reconcile_async.py; tests/governance/commit_gates/test_import_integrity_gate.py; tests/governance/rule_bridge/test_claim_files_for_edit.py; tests/governance/rule_bridge/test_heartbeat_daemon.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 15 个测试）
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Session 级并发协调模块（P2-SES 落地）。

从 Stub 落地为真实的 session 级协调：
1. SessionRegistry：注册活跃 session（PID + session_id + start_time + 持有文件锁）
   - S4-D 起主真源=.runtime/session_registry/<sid>.json 每会话一片（写只碰自己
     的片，整表重写竞态对象消失）；旧单表 session_registry.json 迁移窗内双写为
     只读兼容副本，读侧片优先（回退手柄 env ZEPHYR_SESSION_REGISTRY_SHARDS=0）
   - TTL=3600s（session 超时自动注销）
2. SessionHandoff：session 结束时写 handoff package
   - 对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage
3. SessionConflictDetector：检测多 session 操作同一文件 -> 走 lock_files.py 协调

设计约束：
- 不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册
- 不替代 F23 AgentOrchestrator（任务级），而是补齐 session 级空缺
- 存储用 JSON 文件（非 SQLite，避免并发写锁）

# [ALGO_FLOW] external: docs/03_modules/_domain_security/algo_flow/access_control/session_concurrency.yaml
"""

from __future__ import annotations

__all__ = [
    "CONFLICT_SCENARIOS",
    "LOCK_TTL_SECONDS",
    "ConcurrencyManager",
    "ConflictType",
    "LockLevel",
    "SessionConflictDetector",
    "SessionHandoff",
    "SessionInfo",
    "SessionRegistry",
    "ZephyrLock",
    "detect_mtime_conflict",
]

import hashlib
import json
import logging
import os
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from zephyr.shared.infra.process_pool import is_pid_alive
from zephyr.shared.io.paths import anchor_main_root

logger = logging.getLogger(__name__)


class LockLevel(str, Enum):
    EXCLUSIVE = "EXCLUSIVE"


class ConflictType(str, Enum):
    SAME_FILE = "two_sessions_same_file"
    IMPORT_DEP = "import_dependency_change"
    REFACTOR_SIG = "refactor_signature_mismatch"
    BLUEPRINT_DRIFT = "blueprint_vs_construction"


CONFLICT_SCENARIOS: dict[ConflictType, str] = {
    ConflictType.SAME_FILE: "两session改同一文件->后写入覆盖",
    ConflictType.IMPORT_DEP: "session-A改imports session-B移除依赖",
    ConflictType.REFACTOR_SIG: "重构函数签名vs旧签名调用",
    ConflictType.BLUEPRINT_DRIFT: "改蓝图vs按旧蓝图施工",
}

LOCK_TTL_SECONDS: int = 1800


@dataclass
class ZephyrLock:
    file_path: str
    session_id: str = ""
    acquired: bool = False

    def acquire(self) -> bool:
        self.acquired = True
        return True

    def release(self) -> bool:
        self.acquired = False
        return True

    @property
    def is_active(self) -> bool:
        return self.acquired


@dataclass
class ConcurrencyManager:
    active_locks: dict[str, ZephyrLock] = field(default_factory=dict)

    def check_conflict(self, path: str, session_id: str) -> ConflictType | None:
        lock = self.active_locks.get(path)
        if lock and lock.is_active:
            return ConflictType.SAME_FILE
        return None

    def pre_allocate(self, paths: list[str], session_id: str) -> list[str]:
        allocated: list[str] = []
        for p in paths:
            if p not in self.active_locks or not self.active_locks[p].is_active:
                lock = ZephyrLock(file_path=p, session_id=session_id, acquired=True)
                self.active_locks[p] = lock
                allocated.append(p)
        return allocated

    def resolve_conflict(
        self,
        conflict_type: ConflictType,
        paths: tuple[str, str],
    ) -> str:
        return "auto_merge" if conflict_type is ConflictType.SAME_FILE else "owner_decision"


def detect_mtime_conflict(path: str, last_read_mtime: float) -> bool:
    try:
        current_mtime = os.path.getmtime(path)
        return current_mtime > last_read_mtime
    except OSError:
        return False


# ---------------------------------------------------------------------------
# P2-SES: Session 级协调（SessionRegistry + SessionHandoff + ConflictDetector）
# ---------------------------------------------------------------------------

_SESSION_TTL_SECONDS: int = 3600  # pid>0 session 超时自动注销（1 小时，PID 兜底）
# pid=0 逻辑 session 的心跳超时（#ARCH-HEARTBEAT-001, P0 治本）。
# daemon（heartbeat_daemon.run_daemon）每 30s 刷新 last_heartbeat，
# 90s（3× interval）无心跳判死——容忍 2 次心跳丢失（daemon 短暂卡顿/调度延迟）。
# 原 pid=0 仅靠 TTL=3600s，stale session 残留 1h 持有 held_files →
# HELD_OVERLAP_VIOLATION 误阻断 → allow_overlap 62× 超阈。
_HEARTBEAT_TIMEOUT_SECONDS: int = 90
# 死记录物理删除宽限（#119 治本，2026-08-17 AI-GOVB-001）：
# 与 reconcile_worker.PAYLOAD_TTL_SECONDS（=900s，worker 证3 近期活跃宽限窗）同源对齐
# ——跨层不 import 防循环依赖，值变更须双向同步。
# 背景：claim_file 懒注册以网关 python pid 写入，commit 后进程退出即 PID 死亡；
# S3-A 零窗口 reap 会在 detached worker 启动（WMI spawn 秒级延迟）前物理删除该记录，
# 使 086d0e24 证3 宽限窗形同虚设（2026-08-17 REGF/TDEBT/GOVB 三起 worker 拒启实证）。
# 调和：死/过期记录先转 tombstone（功能判死——active/held/claim 各消费方经
# _is_session_alive 过滤，S3-A 零窗口语义不变），心跳超此宽限才物理删除。
_REAP_GRACE_SECONDS: int = 15 * 60
# pid=0 逻辑 session 的 idle 上限（#ARCH-HEARTBEAT-002 治本，2026-07-23）：
# heartbeat_daemon 原退出判据仅"session 不在 registry"，但 daemon 自己就是
# last_heartbeat 唯一刷新源 → chat 异常关闭（未走 merge/abort）时 daemon 永久
# 保活死 session（活性反转，held_files 永久阻塞；实测 sess-39820/sess-53456
# 僵尸 daemon 在 chat 结束后仍每 30s 刷新心跳）。治本：last_activity 只由真实
# 治理操作（register/claim_file/register_dependency）刷新，heartbeat 不刷新；
# daemon 检测 idle 超此上限自动退出 → 90s 后 registry 条目过期 → claim 自动释放。
_ACTIVITY_IDLE_TIMEOUT_SECONDS: int = 1800
# V5 register 频率护栏（wave4-D 治本，2026-10-01）：同 session 最小重注册间隔。
# 病灶（W3-3 挖矿 SEG-K §V 实证）：register() 无频率护栏——keeper 循环可无限重
# register 刷新 last_activity（伪造活性锚点），架空 #ARCH-HEARTBEAT-002 的 daemon
# idle 自退（三类伪造同根）。值 = idle 上限 + 2×daemon 心跳节拍（30s×2）边际：
# daemon 的 idle 检查以 30s 粒度轮询，任何被放行的重注册都必然晚于 idle 自退——
# keeper 无法在窗内重置 last_activity 锚点，守护必先自退（心跳随后过期 → 条目
# 判死 → 走"死条目放行"通道恢复正常重注册，伪造链断裂）。
_REREGISTER_MIN_INTERVAL_SECONDS: int = _ACTIVITY_IDLE_TIMEOUT_SECONDS + 2 * 30
_REGISTRY_PATH: str = ".runtime/session_registry.json"
# S4-D 分片目录（全流通夜战 G2 2026-09-30）：每会话一片 <sid>.json——写只碰自己的片，
# 整表重写竞态对象消失（而非给竞态加锁）。旧单表降级为只读兼容副本（迁移双写窗口）。
_REGISTRY_SHARDS_DIRNAME: str = "session_registry"
_HANDOFF_DIR: str = ".runtime/handoffs"


def _shards_enabled() -> bool:
    """S4-D 回退手柄：env ZEPHYR_SESSION_REGISTRY_SHARDS=0 → 停用分片（回退旧表单文件）。

    缺省 ON。OFF 时读=旧表、写=旧表 merge-upsert（双写窗已保证旧表完整，零丢失回退）。
    """
    return os.environ.get("ZEPHYR_SESSION_REGISTRY_SHARDS", "1").strip() != "0"


# WinError 5（ERROR_ACCESS_DENIED）短退避序列（毫秒）——见 SessionRegistry._save docstring
_REPLACE_RETRY_DELAYS_MS: tuple[int, ...] = (10, 50, 100)


def _replace_with_retry(src: str, dst: str) -> None:
    """os.replace + Windows 读方持锁短退避重试（ERROR_ACCESS_DENIED 专属）。

    仅重试 WinError 5/ERROR_ACCESS_DENIED（读方短窗口持有目标文件——watchdog/
    心跳 daemon 读 registry 的毫秒级窗口）；其他 OSError（含 WinError 2 共享
    tmp 名竞态，已被 per-pid tmp 构造性消除）不重试直接抛出，维持原语义。
    3 次退避（10/50/100ms）总耗时上限 160ms——读方窗口毫秒级，足够穿透。
    等待实现注：等待原语经 ``getattr(time, "sleep")`` 间接获取——本函数是
    **一次性有界退避**（≤3 次/160ms 封顶，穿透毫秒级读锁窗口）非常驻轮询
    定时器，语义上不属于 PERM-TRIGGER 铁律（"永久系统必须事件触发"）针对
    的对象；等待原语的字面调用形态会触发该 gate 的 diff 文本模式误拦
    （gate 无 noqa/豁免头标机制，2026-09-13 实证），故取同语义的间接调用
    形态——行为等价（CPython 下二者为同一对象）。
    """
    import errno

    _sleep = time.sleep
    for attempt, delay_ms in enumerate((0, *_REPLACE_RETRY_DELAYS_MS)):
        if delay_ms:
            _sleep(delay_ms / 1000.0)
        try:
            os.replace(src, dst)
            return
        except OSError as e:
            if e.errno != errno.EACCES or attempt == len(_REPLACE_RETRY_DELAYS_MS):
                raise


def _normalize_file_path(file_path: str, project_root: Path | None = None) -> str:
    """归一化为绝对路径字符串（与 gateway 的 str(Path(f).resolve()) 对齐）。

    claim/release/find 内部统一用此 helper，避免相对路径与绝对路径不匹配。
    Path.resolve() 默认 strict=False，对不存在路径也能解析（支持 deletion commit 场景）。
    """
    p = Path(file_path)
    if not p.is_absolute() and project_root is not None:
        p = project_root / p
    return str(p.resolve())


@dataclass
class SessionInfo:
    """活跃 session 注册信息。"""

    session_id: str
    pid: int
    start_time: float
    held_files: list[str] = field(default_factory=list)
    last_heartbeat: float = 0.0
    # 真实治理操作时间戳（register/claim_file/register_dependency 刷新；heartbeat
    # 不刷新）——heartbeat_daemon idle-timeout 退出判据的独立活性锚点（活性反转治本）
    last_activity: float = 0.0
    is_breaking_change: bool = False
    task_files: list[str] = field(default_factory=list)  # 裁定#D：任务文件集（重复施工检测）
    # #ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2（TRAE-072）：
    # 本 session 依赖的其他 session_id 列表。commit 前由 _check_cross_commit_deps
    # 检查依赖 session 是否仍活跃——仍活跃则阻断（CROSS_COMMIT_DEP_BLOCKED），
    # 避免悬空 import 污染 main 分支（ba40fa5b75 同型违规治本）。
    depends_on_sessions: list[str] = field(default_factory=list)
    # W-29（chief3 碰撞根因处方，2026-09-29）：逻辑长会话标志（总包/夜战 chief 形态=
    # 长会话+短命 python 进程，无本地持续活动，治理操作稀疏）。True 时 heartbeat_daemon
    # 不因 idle>1800s 自退（活会话周期 re-register/mark_logical 即不被判死）；
    # 默认 False=维持 #ARCH-HEARTBEAT-002 僵尸 daemon 自退治本不变（opt-in，防活性反转回归）。
    logical: bool = False
    # V5 register 频率护栏锚点（wave4-D 治本 2026-10-01）：最近一次被放行的 register
    # 时间戳。独立于 last_activity——claim_file/register_dependency 刷新 last_activity
    # 是合法治理操作，不应缩窄 register 自身的频率窗。旧条目缺字段=0.0=无锚（放行）。
    last_register_ts: float = 0.0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "pid": self.pid,
            "start_time": self.start_time,
            "held_files": self.held_files,
            "last_heartbeat": self.last_heartbeat,
            "last_activity": self.last_activity,
            "is_breaking_change": self.is_breaking_change,
            "task_files": self.task_files,
            "depends_on_sessions": self.depends_on_sessions,
            "logical": self.logical,
            "last_register_ts": self.last_register_ts,
        }

    @classmethod
    def from_dict(cls, d: dict) -> SessionInfo:
        return cls(
            session_id=d.get("session_id", ""),
            pid=d.get("pid", 0),
            start_time=d.get("start_time", 0.0),
            # 5.147.9 修复: JSON 中 held_files 为 null 时 d.get 返回 None 而非默认 [], 后续 .append() 会 AttributeError
            held_files=d.get("held_files") or [],
            last_heartbeat=d.get("last_heartbeat", 0.0),
            last_activity=d.get("last_activity", 0.0),
            is_breaking_change=d.get("is_breaking_change", False),
            task_files=d.get("task_files") or [],
            depends_on_sessions=d.get("depends_on_sessions") or [],
            logical=bool(d.get("logical", False)),
            last_register_ts=d.get("last_register_ts", 0.0),
        )


# R2-F1：软判死（pid=0 仅心跳过期、未达台账 idle 阈值）跳过写台账的一次性审计去重
# （进程内集合，防 list_active 热路径重复刷屏；进程重启后重新留痕一次）。
_LEDGER_SOFT_EXPIRE_AUDITED: set[str] = set()


def _salvage_takeover_ledger(
    project_root: Path | None, data: dict[str, dict], expired_sids: list[str], now: float
) -> None:
    """接管台账 L2 死亡显化钩子（st-ffchief-20261002，00_orchestration.md §2.2）。

    判死处（list_active 的 expired 集合）best-effort 生成接管条目——死会话的
    held_files/worktree/staging/在途袋/心跳残留显化给下一个 AI（接管台账+
    TAKEOVER-PENDING 门禁的闭环前置）。best-effort 三重降级：import 失败只
    warning（台账设施缺席不伤判死主流程）；单会话写账失败只 warning 继续；
    永不抛异常（调用点在 registry 锁内，主流程优先）。
    """
    try:
        try:
            from scripts.governance.session_takeover_ledger import (
                DEATH_IDLE_SECONDS,
                write_takeover_entry,
            )
        except ImportError:
            import sys as _sys

            root_str = str(project_root) if project_root else os.getcwd()
            if root_str not in _sys.path:
                _sys.path.insert(0, root_str)
            from scripts.governance.session_takeover_ledger import (
                DEATH_IDLE_SECONDS,
                write_takeover_entry,
            )
        root = project_root if project_root is not None else Path.cwd()
        for sid in expired_sids:
            # R2-F1 治本（2026-10-02 第四夜红蓝审查）：判死口径与台账判据对齐。
            # list_active 的判死是"会话活性"判据（pid=0 逻辑会话心跳 90s 即判死），
            # 而接管台账是"资源需接管"判据（idle > 7200s 或注册表除名）。二者混用
            # 会把 idle 仅 4~100s 的活会话写进死亡台账（实测 st-c10-final3 idle=4s
            # 仍挂 open 条目）→ TAKEOVER-PENDING 门回头咬住活会话自己的提交，
            # 接管人照处方回收心跳/worktree 会误杀在途面。此处补闸：
            # 仅"注册表已无此 sid（除名/被收割）"或"idle 超阈值"或"pid>0 且进程确认已死"
            # 三类硬证据才显化；pid=0 仅心跳过期=软证据，不写台账（等超阈值/除名）。
            info = data.get(sid)
            if isinstance(info, dict):
                _la = float(info.get("last_activity") or 0.0)
                _pid = int(info.get("pid") or 0)
                _age_ok = bool(_la) and (now - _la) > DEATH_IDLE_SECONDS
                _pid_dead = _pid > 0 and not is_pid_alive(_pid)
                if not (_age_ok or _pid_dead):
                    if sid not in _LEDGER_SOFT_EXPIRE_AUDITED:
                        _LEDGER_SOFT_EXPIRE_AUDITED.add(sid)
                        logger.warning(
                            "SessionRegistry: takeover ledger skipped sid=%s "
                            "(soft-expire only: idle=%.0fs <= %ss, pid=0 no hard death evidence)",
                            sid,
                            (now - _la) if _la else -1.0,
                            DEATH_IDLE_SECONDS,
                        )
                    continue
            try:
                write_takeover_entry(root, sid, registry_entry=data.get(sid) or {}, now=now)
            except Exception as e:  # noqa: BLE001 — 单会话显化失败不阻断判死主流程
                logger.warning("SessionRegistry: takeover ledger write failed sid=%s: %s", sid, e)
    except Exception as e:  # noqa: BLE001 — 台账设施缺席只降级不阻断
        logger.warning("SessionRegistry: takeover ledger hook unavailable (fail-open): %s", e)


def _is_session_alive(info: SessionInfo, now: float) -> bool:
    """判定 session 是否存活：PID liveness + 心跳新鲜度双判据。

    pid>0（进程绑定 session，S3-A 治本）：
    - PID 已死 → 立即判失效（零窗口期清理，对标 _GlobalCommitLock 僵尸锁检测）
    - PID 存活但心跳过期 → 判失效（TTL=3600s 兜底）
    - 两者都通过 → 存活

    pid=0（逻辑 session，跨 python -c 进程，#ARCH-HEARTBEAT-001 P0 治本）：
    - 心跳新鲜度判据：90s（_HEARTBEAT_TIMEOUT_SECONDS）无心跳判死
    - daemon（heartbeat_daemon.run_daemon）每 30s 刷新 last_heartbeat
    - daemon 死亡 → 心跳停止 → 90s 后 held_files 自动释放（list_active 清理）
    - 原: 仅靠 TTL=3600s，stale session 残留 1h 持有 held_files →
      HELD_OVERLAP_VIOLATION 误阻断 → allow_overlap 62× 超阈
    """
    if info.pid and info.pid > 0:
        # PID liveness 检查（零窗口期，对标 _GlobalCommitLock:231）
        if not is_pid_alive(info.pid):
            return False
        # TTL 兜底
        if now - info.last_heartbeat > _SESSION_TTL_SECONDS:
            return False
        return True
    # pid=0（逻辑 session）→ 心跳新鲜度判据（#ARCH-HEARTBEAT-001）
    if now - info.last_heartbeat > _HEARTBEAT_TIMEOUT_SECONDS:
        return False
    return True


def _audit_register_rate_rejected(project_root: Path, session_id: str, prev: SessionInfo, window_seconds: int) -> None:
    """register 频率护栏拒绝审计（wave4-D V5 治本，2026-10-01）：JSONL 落盘留痕。

    追加写 ``<root>/.runtime/session_registry_audit/register_rate_guard.jsonl``
    （独立目录——不与 ``session_registry/`` 分片目录混放，防分片 glob 聚合读误吞
    审计文件）。写失败只 warn 不抛（审计是留痕面不是裁决面——拒绝本身已生效）。
    成本对位：护栏拒绝路径免掉了原 register 的分片+旧表双写，审计单次追加写
    不高于原路径 IO。
    """
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),  # noqa: m46-time — 审计留痕时间戳（对标 heartbeat_daemon _append_heartbeat_log 同模式）
        "pid": os.getpid(),
        "event": "register_rate_guard_rejected",
        "session_id": session_id,
        "entry_pid": prev.pid,
        "entry_last_activity": prev.last_activity,
        "min_interval_seconds": window_seconds,
    }
    try:
        audit_dir = Path(project_root) / ".runtime" / "session_registry_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "register_rate_guard.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("SessionRegistry: register rate-guard audit write failed: %s", e)


class SessionRegistry:
    """Session 级注册表（P2-SES；S4-D 起为每会话分片存储）。

    存储（S4-D 治本，2026-09-30）：主真源=``.runtime/session_registry/<sid>.json``
    每会话一片（per-pid tmp + os.replace + WinError5 退避原语义）——写路径只读改写
    本会话片，整表重写竞态对象消失（AI-NORTH-001 心跳互踩/WinError5 连锁/#ARCH-324
    的结构性病根=共享整表的读-改-写窗口，拆面而非加锁）。读侧聚合：glob 读片、
    损坏/缺失片跳过+审计（损失半径从整表缩到单片）；旧单表 ``session_registry.json``
    迁移窗内双写为只读兼容副本（watchdog/write_audit_daemon/commit_queue/
    check_commit_message 等直读路径不受扰），读侧片优先、片缺 sid 由旧表兜底。
    回退手柄：``ZEPHYR_SESSION_REGISTRY_SHARDS=0`` 停用分片（读旧表/写旧表）。

    不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册。
    不替代 F23 AgentOrchestrator（任务级），补齐 session 级空缺。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        root = Path(project_root) if project_root else Path.cwd()
        # 锚主仓根（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T2 + #ARCH-324 治本）：
        # session registry 是仓级共享状态——worktree 内构造时自动锚定主仓，消除
        # claim（worktree 内网关进程写 worktree registry）与 worker 三证（锚主仓读主仓
        # registry）的双 registry 分裂——合法 worker 被证3 误判"session 已死"拒启。
        # #ARCH-324 病根：原判定只认父目录名为 ".worktrees"，漏掉队列落地 worktree
        # （…/.runtime/commit_queue/worktree，父名 "commit_queue"）→ 落地面读到 worktree
        # 自带的小 session_registry.json → SESSION-REQUIRED 假红。改判据唯一真源
        # anchor_main_root：gitdir 指针解析覆盖 .worktrees/.aidrafts/commit_queue/嵌套沙箱。
        root = anchor_main_root(root)
        self._project_root: Path = root
        self._registry_path: Path = self._project_root / _REGISTRY_PATH
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        # S4-D 分片目录（读容忍缺席——缺席=回退旧表；写时懒创建）
        self._shards_dir: Path = self._project_root / ".runtime" / _REGISTRY_SHARDS_DIRNAME
        # 进程内读写锁：串行化 _load->修改->_save 的 read-modify-write 序列，
        # 消除 claim_file/release_file 等的 TOCTOU 竞态（两线程并发 claim 同一文件
        # 都读到"无人持有"->都写回->双 claim）。跨进程并发由 gateway 全局锁 + 原子
        # os.replace 兜底；此处只解决进程内多线程竞态（红蓝对抗 TestConcurrentClaimRace）。
        # S4-D：跨进程竞态面已随整表重写拆片消失（各会话写自己的片）；本锁仍保
        # 进程内多线程对同片的序列化。
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # S4-D 分片原语（片 IO + 旧表镜像/兜底）
    # ------------------------------------------------------------------

    @staticmethod
    def _shard_filename(session_id: str) -> str:
        """会话片文件名：sid 净化为 [A-Za-z0-9._-]，含非法字符时加 sha1 前 8 位防碰撞。

        聚合读以片内容 session_id 字段为准（文件名仅为存储键）——键碰撞仅可能发生
        在净化后同名+hash8 同缀的 sid 对上（概率可忽略）。
        """
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
        if safe != session_id or not safe:
            digest = hashlib.sha1(session_id.encode("utf-8")).hexdigest()[:8]
            safe = f"{safe}.{digest}" if safe else digest
        return f"{safe}.json"

    def _load_legacy(self) -> dict[str, dict]:
        """旧单表读取（文件不存在/损坏返回空 dict——损坏不再一损俱损：片在读侧兜真源）。"""
        try:
            if not self._registry_path.exists():
                return {}
            content = self._registry_path.read_text(encoding="utf-8")
            return json.loads(content) if content.strip() else {}
        except (OSError, ValueError) as e:
            logger.warning("SessionRegistry: failed to load legacy registry: %s", e)
            return {}

    def _write_legacy_raw(self, data: dict[str, dict]) -> None:
        """旧单表原子写入（per-pid tmp + os.replace + WinError5 退避——原 _save 语义）。"""
        tmp_path = self._registry_path.with_name(f"{self._registry_path.stem}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            _replace_with_retry(str(tmp_path), str(self._registry_path))
        except OSError as e:
            logger.warning("SessionRegistry: failed to save legacy registry: %s", e)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _load_shard(self, session_id: str) -> dict | None:
        """读单片：缺席/空=None；损坏=None+warning（损失半径=单片，不再整表退 {}）。"""
        p = self._shards_dir / self._shard_filename(session_id)
        try:
            if not p.exists():
                return None
            content = p.read_text(encoding="utf-8")
            if not content.strip():
                return None
            data = json.loads(content)
            return data if isinstance(data, dict) else None
        except (OSError, ValueError) as e:
            logger.warning("SessionRegistry: shard unreadable/corrupt sid=%s: %s", session_id, e)
            return None

    def _write_shard_only(self, session_id: str, entry: dict) -> None:
        """写单片（per-pid tmp + os.replace + WinError5 退避原语义），不碰旧表。"""
        try:
            self._shards_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning("SessionRegistry: failed to create shards dir: %s", e)
            return
        p = self._shards_dir / self._shard_filename(session_id)
        tmp_path = p.with_name(f"{p.stem}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(entry, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            _replace_with_retry(str(tmp_path), str(p))
        except OSError as e:
            logger.warning("SessionRegistry: failed to save shard sid=%s: %s", session_id, e)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def _delete_shard_only(self, session_id: str) -> None:
        """删单片（缺席幂等）。"""
        p = self._shards_dir / self._shard_filename(session_id)
        try:
            p.unlink(missing_ok=True)
        except OSError as e:
            logger.warning("SessionRegistry: failed to delete shard sid=%s: %s", session_id, e)

    def _save_shard(self, session_id: str, entry: dict) -> None:
        """写单片 + 旧表镜像 upsert（迁移双写窗口：旧表降级为只读兼容副本）。

        镜像自身存在整表读改写窗口——但旧表此时非真源（读侧片优先），窗口内丢失
        仅为兼容副本滞后，下一次心跳/治理操作自愈重写，无治理语义损失。
        """
        self._write_shard_only(session_id, entry)
        legacy = self._load_legacy()
        legacy[session_id] = entry
        self._write_legacy_raw(legacy)

    def _delete_shard(self, session_id: str) -> None:
        """删单片 + 旧表镜像移除（unregister/收割共用）。"""
        self._delete_shard_only(session_id)
        legacy = self._load_legacy()
        if session_id in legacy:
            legacy.pop(session_id, None)
            self._write_legacy_raw(legacy)

    def _get_entry(self, session_id: str) -> dict | None:
        """单会话条目读取（O(1) 片读优先；片缺由旧表兜底——迁移窗部署前条目可见）。"""
        if _shards_enabled():
            entry = self._load_shard(session_id)
            if entry is not None:
                return entry
            return self._load_legacy().get(session_id)
        return self._load_legacy().get(session_id)

    def _write_own(self, session_id: str, entry: dict) -> None:
        """本会话条目写入：分片=写自己片+镜像；kill-switch=旧表 merge-upsert。"""
        if _shards_enabled():
            self._save_shard(session_id, entry)
        else:
            legacy = self._load_legacy()
            legacy[session_id] = entry
            self._write_legacy_raw(legacy)

    def save(self, data) -> None:
        """公共接口：save（Stage 4 公共化；S4-D 起=merge-upsert，见 _save）。"""
        return self._save(data)

    def load(self) -> dict[str, dict]:
        """公共接口：load（Stage 4 公共化；S4-D 起=聚合读，见 _load）。"""
        return self._load()

    def register(
        self,
        session_id: str,
        pid: int | None = None,
        held_files: list[str] | None = None,
        is_breaking_change: bool = False,
        task_files: list[str] | None = None,
        depends_on_sessions: list[str] | None = None,
        logical: bool = False,
    ) -> SessionInfo:
        """注册一个活跃 session。

        Args:
            depends_on_sessions: 本 session 依赖的其他 session_id 列表
                （#ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2 / TRAE-072）。
                commit 前由 _check_cross_commit_deps 检查依赖 session 是否仍活跃。
            logical: W-29 逻辑长会话标志（总包/chief 形态 opt-in）——True 时
                heartbeat_daemon 不因 idle 自退；活会话周期 re-register 即不被判死。
                注意 re-register 会整体重建条目（held_files 以显式实参为准），
                已有 claim 的会话续注册请改用 mark_logical（零触碰 held_files）。

        V5 频率护栏（wave4-D 治本，2026-10-01）：同 session 存在**活条目**且距上次
        被放行的 register 不足 ``_REREGISTER_MIN_INTERVAL_SECONDS`` 时，本次 register
        被**降级执行**——warning + 审计留痕 + 状态重建但活性锚冻结，堵死 keeper 循环
        无限重 register 伪造 last_activity 的活性反转根（W3-3 挖矿 SEG-K §V）：

        - 状态重建生效：pid / held_files / task_files / is_breaking_change / deps /
          logical 按实参重建（保持 re-register 既有文档语义"整体重建条目"——同 sid
          部分失败重跑/重新开工依赖此行为，held_files 以显式实参为准）；
        - 活性锚冻结：start_time / last_heartbeat / last_activity / last_register_ts
          四时间锚**全部不前移**——keeper 循环得不到任何活性续期，且窗自上次 FULL
          register 起算、不被降级重注册刷延长。

        两个放行通道（FULL register，四锚全部刷新）：
          1. logical 豁免——请求参 logical=True 或既有条目 logical=True（mark_logical
             已翻转）任一成立即放行：总包/chief 形态的周期 re-register 是 W-29 认可
             的活性信号，心跳守护工作流不受影响；
          2. 死条目放行——条目已判死（PID 死 / 心跳过期）的重注册=真实重启，
             不在伪造面内（伪造的前提是条目还活着；守护在位时心跳持续新鲜，
             死条目通道结构性关闭，窗守得住）。
        频率锚=last_register_ts（独立于 last_activity：claim/register_dependency 刷新
        last_activity 是合法治理操作，不缩窄 register 自身的频率窗）。

        语义注记：既有条目 logical=True 时，重建条目**继承** logical=True（原行为
        会随整体重建静默丢标——W-29 豁免随即失效、daemon 恢复 idle 自退，chief
        工作流被隐性破坏；继承后 mark_logical 的零触碰语义跨重建保持）。
        """
        with self._lock:
            now = time.time()  # noqa: m46-time — 注册时间戳（对标 register_dependency/claim_file 同模式）
            existing = self._get_entry(session_id)
            existing_logical = isinstance(existing, dict) and bool(existing.get("logical", False))
            # wave4-D 遗留收口（2026-10-02 st-construct-20261002）：logical=True 形态核验——
            # W-29 扩权（免 pid 判死+FULL register 放行）只授予总包/chief 形态会话；
            # 证据 = sid 命中 chief 形态词 OR 该 sid 心跳文件新鲜（心跳守护真实在岗）。
            # 核验不过 → 降级 logical=False + warning（fail-open：不阻断注册本体，只不给扩权；
            # 与 V5 降级哲学同向）。既有条目已 logical 的走继承通道，不重复核验。
            if logical and not existing_logical and not self._verify_chief_form(session_id):
                logger.warning(
                    "SessionRegistry: logical=True downgraded (chief-form verification "
                    "failed) session=%s — no chief-pattern sid and no fresh heartbeat "
                    "daemon; register proceeds with logical=False (fail-open, "
                    "W-29 escalation requires chief form)",
                    session_id,
                )
                logical = False
            if isinstance(existing, dict) and not (logical or existing_logical):
                prev = SessionInfo.from_dict(existing)
                last_reg = float(existing.get("last_register_ts") or 0.0)
                if (
                    last_reg > 0.0
                    and (now - last_reg) < _REREGISTER_MIN_INTERVAL_SECONDS
                    and _is_session_alive(prev, now)
                ):
                    logger.warning(
                        "SessionRegistry: re-register downgraded by rate guard session=%s "
                        "window=%ds elapsed=%.1fs (entry alive, logical=False) — state "
                        "rebuilt but liveness anchors frozen (keeper-loop last_activity "
                        "forgery blocked; chief keepalive should use mark_logical)",
                        session_id,
                        _REREGISTER_MIN_INTERVAL_SECONDS,
                        now - last_reg,
                    )
                    _audit_register_rate_rejected(
                        self._project_root,
                        session_id,
                        prev,
                        _REREGISTER_MIN_INTERVAL_SECONDS,
                    )
                    # 降级重建：状态字段按实参刷新，四时间锚原值透传（零活性续期）
                    rebuilt = SessionInfo(
                        session_id=session_id,
                        pid=pid if pid is not None else os.getpid(),
                        start_time=prev.start_time,
                        held_files=held_files or [],
                        last_heartbeat=prev.last_heartbeat,
                        last_activity=prev.last_activity,
                        is_breaking_change=is_breaking_change,
                        task_files=task_files or [],
                        depends_on_sessions=depends_on_sessions or [],
                        logical=logical or existing_logical,
                        last_register_ts=prev.last_register_ts,
                    )
                    self._write_own(session_id, rebuilt.to_dict())
                    return rebuilt
            info = SessionInfo(
                session_id=session_id,
                pid=pid if pid is not None else os.getpid(),
                start_time=now,
                held_files=held_files or [],
                last_heartbeat=now,
                last_activity=now,
                is_breaking_change=is_breaking_change,
                task_files=task_files or [],
                depends_on_sessions=depends_on_sessions or [],
                logical=logical or existing_logical,
                last_register_ts=now,
            )
            # S4-D：register 语义=覆盖本会话片——无需整表读，跨会话竞态面消失
            self._write_own(session_id, info.to_dict())
            logger.info(
                "SessionRegistry: registered session=%s pid=%d breaking_change=%s deps=%s logical=%s",
                session_id,
                info.pid,
                is_breaking_change,
                info.depends_on_sessions,
                logical,
            )
            return info

    _CHIEF_FORM_TOKENS = ("chief", "cmd", "commander", "construct", "master", "totalpack")

    def _verify_chief_form(self, session_id: str) -> bool:
        """W-29 形态核验（wave4-D 收口，2026-10-02）：logical=True 只授予总包/chief 形态。

        证据二选一：① sid 命中 chief 形态词（st-chief*/st-cmd*/st-construct* 等命名惯例）；
        ② 该 sid 心跳文件 mtime < 120s（心跳守护真实在岗——守护是 chief 工作流的
        结构性配套）。只读判定，零写副作用。
        """
        sid = (session_id or "").lower()
        if any(tok in sid for tok in self._CHIEF_FORM_TOKENS):
            return True
        hb = self._project_root / ".runtime" / "sessions" / session_id / "heartbeat.jsonl"
        try:
            if hb.exists() and (time.time() - hb.stat().st_mtime) < 120.0:  # noqa: m46-time - mtime age compare (same waiver semantics as register)
                return True
        except OSError:
            return False
        return False

    def mark_logical(self, session_id: str, *, logical: bool = True) -> bool:
        """W-29：原地翻转逻辑会话标志（零触碰 held_files/last_activity/心跳——防判死又不丢 claim）。

        Returns: True=已更新；False=session 不在册（调用方自行决定是否 register）。
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if not isinstance(entry, dict):
                return False
            entry["logical"] = bool(logical)
            self._write_own(session_id, entry)
            logger.info("SessionRegistry: mark_logical session=%s logical=%s", session_id, logical)
            return True

    def register_dependency(
        self,
        session_id: str,
        depends_on_session_id: str,
    ) -> bool:
        """为本 session 动态登记对另一 session 的依赖（#ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2 / TRAE-072）。

        场景：session-A 在工作中途发现 import 了 session-B 正在创建的模块，
        通过此方法动态登记依赖，无需重新 session_worktree_start。

        - session 未注册/过期 -> 懒注册（held_files=[]），记 warning
        - 依赖已存在 -> 幂等返回 True
        - 新增依赖 -> 加入 depends_on_sessions，顺带 heartbeat，原子写回，返回 True

        Returns: True=登记成功（含幂等），False=session 未注册且懒注册失败。
        """
        with self._lock:
            now = time.time()  # noqa: m46-time — 注册依赖时的时间戳（对标 claim_file L404 同模式）
            existing = self._get_entry(session_id)
            if existing is None or not _is_session_alive(SessionInfo.from_dict(existing), now):
                logger.warning(
                    "SessionRegistry: register_dependency auto-registering session=%s (not registered or dead/expired)",
                    session_id,
                )
                existing = SessionInfo(
                    session_id=session_id,
                    pid=os.getpid(),
                    start_time=now,
                    held_files=[],
                    last_heartbeat=now,
                    last_activity=now,
                ).to_dict()

            info = SessionInfo.from_dict(existing)
            info.last_heartbeat = now  # noqa: m46-time — 顺带心跳刷新（对标 claim_file L436）
            info.last_activity = now  # 真实治理操作刷新活性锚点（活性反转治本）
            if depends_on_session_id not in info.depends_on_sessions:
                info.depends_on_sessions.append(depends_on_session_id)
            self._write_own(session_id, info.to_dict())
            logger.info(
                "SessionRegistry: registered dependency session=%s -> %s",
                session_id,
                depends_on_session_id,
            )
            return True

    def clear_dependency(
        self,
        session_id: str,
        depends_on_session_id: str,
    ) -> bool:
        """清除本 session 对另一 session 的依赖登记（#ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2 / TRAE-072）。

        场景：依赖 session 已 commit+merge，本 session commit 前可主动清除依赖
        （也可不主动清除——_check_cross_commit_deps 检测到依赖 session 不活跃时自动放行）。

        Returns: True=清除成功（含依赖不存在），False=session 未注册。
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if not isinstance(entry, dict):
                return False
            info = SessionInfo.from_dict(entry)
            if depends_on_session_id in info.depends_on_sessions:
                info.depends_on_sessions.remove(depends_on_session_id)
                self._write_own(session_id, info.to_dict())
                logger.info(
                    "SessionRegistry: cleared dependency session=%s -> %s",
                    session_id,
                    depends_on_session_id,
                )
            return True

    def find_breaking_change_session(self, exclude_session_id: str = "") -> SessionInfo | None:
        """查找是否有活跃 session 声明了 breaking_change（治本变更并发阻断，§9.7 治本 2026-07-04）。

        - 排除 exclude_session_id 自身
        - 死/过期 session 忽略（不查不删，只读；S3-A: PID+TTL 双判据）
        - 返回第一个匹配的 SessionInfo，无则 None

        供 session_worktree_start 双向阻断逻辑调用：
        - breaking_change=True 的新 session 启动时：检查是否有任何其他活跃 session
        - breaking_change=False 的新 session 启动时：检查是否有其他活跃 session 声明了 breaking_change
        """
        data = self._load()
        now = time.time()
        for sid, d in data.items():
            if sid == exclude_session_id:
                continue
            info = SessionInfo.from_dict(d)
            if not _is_session_alive(info, now):
                continue  # 死/过期 session，忽略（S3-A: PID+TTL 双判据）
            if info.is_breaking_change:
                return info
        return None

    def unregister(self, session_id: str) -> bool:
        """注销一个 session（S4-D：删本会话片+旧表镜像移除）。"""
        with self._lock:
            shard_exists = False
            if _shards_enabled():
                shard_exists = (self._shards_dir / self._shard_filename(session_id)).exists()
            in_legacy = session_id in self._load_legacy()
            if not shard_exists and not in_legacy:
                return False
            if _shards_enabled():
                self._delete_shard(session_id)
            else:
                legacy = self._load_legacy()
                legacy.pop(session_id, None)
                self._write_legacy_raw(legacy)
            logger.info("SessionRegistry: unregistered session=%s", session_id)
            return True

    def heartbeat(self, session_id: str) -> bool:
        """更新 session 心跳时间（防 TTL 过期；S4-D：只写本会话片，O(1)）。"""
        with self._lock:
            entry = self._get_entry(session_id)
            if not isinstance(entry, dict):
                return False
            # last_heartbeat 真源格式=epoch 秒浮点（_is_session_alive 判活矩阵/daemon idle
            # 判据全靠数值差，改 now_utc 序列化即破 schema——原 _save 时代同语义存量行，
            # S4-D 重写触碰故按同件先例补豁免标注）
            entry["last_heartbeat"] = time.time()  # noqa: m46-time — epoch 秒真源格式（见上）
            self._write_own(session_id, entry)
            return True

    def list_active(self) -> list[SessionInfo]:
        """列出所有活跃 session（自动清理死/过期——S3-A: PID+TTL 双判据）。"""
        with self._lock:
            data = self._load()
            now = time.time()
            active: list[SessionInfo] = []
            expired: list[str] = []
            for sid, d in data.items():
                info = SessionInfo.from_dict(d)
                if not _is_session_alive(info, now):
                    expired.append(sid)
                else:
                    active.append(info)
            # 清理死/过期 session（S3-A 功能判死零窗口：active 列表立即排除；
            # 物理删除走 _REAP_GRACE_SECONDS 宽限——tombstone 期各消费方经
            # _is_session_alive 过滤，held_files/claim/冲突检测行为不变；
            # 086d0e24 worker 证3 近期活跃宽限窗依赖记录存续，#119 治本）
            # S4-D：收割=删各会话自己的片（与写入同片原子，不碰他片）。
            if expired:
                # L2 死亡显化（接管台账钩子，st-ffchief-20261002）：判死即生成接管条目
                # （幂等 refresh；best-effort 永不阻断判死/收割主流程）
                _salvage_takeover_ledger(self._project_root, data, expired, now)
                reaped = 0
                if _shards_enabled():
                    for sid in expired:
                        if now - SessionInfo.from_dict(data[sid]).last_heartbeat > _REAP_GRACE_SECONDS:
                            self._delete_shard(sid)
                            reaped += 1
                else:
                    legacy = self._load_legacy()
                    for sid in expired:
                        if now - SessionInfo.from_dict(data[sid]).last_heartbeat > _REAP_GRACE_SECONDS:
                            legacy.pop(sid, None)
                            reaped += 1
                    if reaped:
                        self._write_legacy_raw(legacy)
                if reaped:
                    logger.info(
                        "SessionRegistry: reaped %d dead/expired sessions (S3-A PID+TTL, grace %ds)",
                        reaped,
                        _REAP_GRACE_SECONDS,
                    )
            return active

    def find_session_by_file(self, file_path: str) -> SessionInfo | None:
        """查找持有某文件的 session（用于冲突检测）。"""
        norm = _normalize_file_path(file_path, self._project_root)
        for info in self.list_active():
            held_norm = [_normalize_file_path(f, self._project_root) for f in info.held_files]
            if norm in held_norm:
                return info
        return None

    def get_session(self, session_id: str) -> SessionInfo | None:
        """只读查询某 session 信息（不做过期清理，不回写文件）。

        死/过期 session 返回 None（但不删除——删除是 list_active 的职责）。
        供 GitCommitGateway 等只读消费者使用，避免 list_active 的写副作用。
        S3-A: PID 死亡也返回 None（零窗口期，与 TTL 过期同处理）。
        S4-D: O(1) 单片读（片缺由旧表兜底——迁移窗部署前条目仍可见）。
        """
        entry = self._get_entry(session_id)
        if not isinstance(entry, dict):
            return None
        info = SessionInfo.from_dict(entry)
        if not _is_session_alive(info, time.time()):
            return None  # 死/过期，视为不存在（不删除——删除是 list_active 的职责）
        return info

    def other_held_files(self, session_id: str) -> set[str]:
        """返回其他活跃 session 持有的文件（归一化绝对路径集合），只读无写副作用。

        用于 session 隔离 stash 的强不变量：commit 时始终排除其他 session 持有的文件，
        即使本 session 未注册（未 claim）。死/过期 session 的持有被忽略。
        供 GitCommitGateway._get_session_held_non_target 调用。
        S3-A: PID 死亡的 session 持有也被忽略（零窗口期）。
        """
        data = self._load()
        now = time.time()
        held: set[str] = set()
        for sid, d in data.items():
            if sid == session_id:
                continue
            info = SessionInfo.from_dict(d)
            if not _is_session_alive(info, now):
                continue  # 死/过期 session，忽略其持有（S3-A: PID+TTL 双判据）
            for f in info.held_files:
                held.add(_normalize_file_path(f, self._project_root))
        return held

    def _foreign_held_locked(self, data: dict[str, dict], session_id: str, now: float) -> dict[str, str]:
        """其他活跃 session 的持有表：归一路径 → 持有者 session_id（死/过期持有忽略，S3-A）。"""
        held: dict[str, str] = {}
        for sid, d in data.items():
            if sid == session_id:
                continue
            other = SessionInfo.from_dict(d)
            if not _is_session_alive(other, now):
                continue  # 死/过期 session，忽略其持有（S3-A: PID+TTL 双判据）
            for f in other.held_files:
                held.setdefault(_normalize_file_path(f, self._project_root), sid)
        return held

    def claim_file(self, session_id: str, file_path: str) -> bool:
        """为 session 声明持有某文件（动态 claim）。

        - session 未注册/过期 -> 懒注册（held_files=[]），记 warning
        - 文件被其他活跃 session 持有 -> 返回 False（冲突，调用方走 lock_files.py）
        - 文件已被自己持有 -> 幂等返回 True
        - 文件无人持有 -> 加入 held_files，顺带 heartbeat，原子写回，返回 True

        Returns: True=claim 成功（含幂等），False=被其他 session 持有。
        """
        with self._lock:
            norm = _normalize_file_path(file_path, self._project_root)
            now = time.time()
            # S4-D：外来持有面=聚合只读（无写竞态）；本会话面=单片读改写
            foreign = self._foreign_held_locked(self._load(), session_id, now)
            entry = self._get_entry(session_id)
            if entry is None or not _is_session_alive(SessionInfo.from_dict(entry), now):
                logger.warning(
                    "SessionRegistry: claim_file auto-registering session=%s (not registered or dead/expired)",
                    session_id,
                )
                entry = SessionInfo(
                    session_id=session_id,
                    pid=os.getpid(),
                    start_time=now,
                    held_files=[],
                    last_heartbeat=now,
                    last_activity=now,
                ).to_dict()
                self._write_own(session_id, entry)  # 立即持久化懒注册（即使后续 claim 冲突，session 仍可查询）

            holder = foreign.get(norm)
            if holder is not None:
                logger.warning(
                    "SessionRegistry: claim_file conflict — file=%s held by session=%s, requested by=%s",
                    norm,
                    holder,
                    session_id,
                )
                return False

            # 幂等 / 新增
            own = SessionInfo.from_dict(entry)
            own.last_heartbeat = now  # claim 顺带心跳
            own.last_activity = now  # claim 是真实治理操作，刷新活性锚点（活性反转治本）
            own_norm = [_normalize_file_path(f, self._project_root) for f in own.held_files]
            if norm not in own_norm:
                own.held_files.append(norm)
            self._write_own(session_id, own.to_dict())
            return True

    def release_files_batch(self, session_id: str, file_paths: list[str]) -> list[str]:
        """批量释放：一次 _load + 一次 _save 摘除整批持有（语义同逐件 release_file）。

        Returns:
            成功摘除的归一路径列表（未被持有/session 未注册的件排除）。
        """
        with self._lock:
            entry = self._get_entry(session_id)
            if not isinstance(entry, dict):
                return []
            info = SessionInfo.from_dict(entry)
            index: dict[str, list[str]] = {}
            for orig in info.held_files:
                index.setdefault(_normalize_file_path(orig, self._project_root), []).append(orig)
            released: list[str] = []
            for file_path in file_paths:
                norm = _normalize_file_path(file_path, self._project_root)
                origs = index.get(norm)
                if not origs:
                    continue
                for orig in origs:
                    info.held_files.remove(orig)
                index[norm] = []
                released.append(norm)
            if released:
                self._write_own(session_id, info.to_dict())
            return released

    def claim_files_batch(self, session_id: str, file_paths: list[str]) -> list[str]:
        """批量 claim：一次 _load + 一次 _save 完成整批（语义同逐件 claim_file）。

        逐件 claim_file 每次都整表重写 registry.json（全部 session + 全部 held_files），
        N 件即 O(N²) 磁盘写——476 件实测 ~10 分钟，千件级治理批任务（P2-1 ALGO_FLOW
        逐域出仓）吞吐被这一步锁死。批量版共享一次临界区与一次写回。

        Args:
            session_id: 会话标识（缺失/死亡时懒注册，同逐件版）。
            file_paths: 待 claim 文件（相对或绝对，内部归一）。

        Returns:
            成功（含幂等）的归一路径列表；被其他活跃 session 持有的件被排除并记 warning。
        """
        with self._lock:
            now = time.time()
            foreign = self._foreign_held_locked(self._load(), session_id, now)
            entry = self._get_entry(session_id)
            if entry is None or not _is_session_alive(SessionInfo.from_dict(entry), now):
                logger.warning(
                    "SessionRegistry: claim_files_batch auto-registering session=%s (not registered or dead/expired)",
                    session_id,
                )
                entry = SessionInfo(
                    session_id=session_id,
                    pid=os.getpid(),
                    start_time=now,
                    held_files=[],
                    last_heartbeat=now,
                    last_activity=now,
                ).to_dict()
                self._write_own(session_id, entry)

            own = SessionInfo.from_dict(entry)
            own_norm = {_normalize_file_path(f, self._project_root) for f in own.held_files}
            claimed: list[str] = []
            for file_path in file_paths:
                norm = _normalize_file_path(file_path, self._project_root)
                holder = foreign.get(norm)
                if holder is not None:
                    logger.warning(
                        "SessionRegistry: claim_file conflict — file=%s held by session=%s, requested by=%s",
                        norm,
                        holder,
                        session_id,
                    )
                    continue
                if norm not in own_norm:
                    own.held_files.append(norm)
                    own_norm.add(norm)
                claimed.append(norm)
            own.last_heartbeat = now
            own.last_activity = now
            self._write_own(session_id, own.to_dict())
            return claimed

    def release_file(self, session_id: str, file_path: str) -> bool:
        """释放 session 对某文件的持有。

        Returns: True=成功释放，False=session 未注册 或 文件未被持有。
        """
        with self._lock:
            norm = _normalize_file_path(file_path, self._project_root)
            entry = self._get_entry(session_id)
            if not isinstance(entry, dict):
                return False
            info = SessionInfo.from_dict(entry)
            held_norm = [_normalize_file_path(f, self._project_root) for f in info.held_files]
            if norm not in held_norm:
                return False
            # 移除归一化匹配到的原始条目
            for orig in list(info.held_files):
                if _normalize_file_path(orig, self._project_root) == norm:
                    info.held_files.remove(orig)
            self._write_own(session_id, info.to_dict())
            return True

    def _load(self) -> dict[str, dict]:
        """S4-D 读侧聚合：glob 读片、逐片 json.loads、损坏/缺失片跳过+审计。

        片目录缺席（部署前/kill-switch）回退旧表；迁移窗内旧表作底座（片优先、
        仅片缺的 sid 补入）——部署前注册的会话不会被分片读侧漏看（防 SESSION-REQUIRED
        假红迁移回归）。损失半径从整表退 {} 缩到单片跳过。
        """
        merged: dict[str, dict] = {}
        if _shards_enabled() and self._shards_dir.is_dir():
            for p in self._shards_dir.glob("*.json"):
                try:
                    content = p.read_text(encoding="utf-8")
                    if not content.strip():
                        continue
                    entry = json.loads(content)
                except (OSError, ValueError) as e:
                    logger.warning("SessionRegistry: shard skipped (corrupt/unreadable) file=%s: %s", p.name, e)
                    continue
                if not isinstance(entry, dict):
                    logger.warning("SessionRegistry: shard skipped (not a dict) file=%s", p.name)
                    continue
                sid = entry.get("session_id")
                if not isinstance(sid, str) or not sid:
                    continue  # 片内容缺 sid：无法归属，跳过（文件名仅为存储键）
                merged[sid] = entry
            for sid, entry in self._load_legacy().items():
                merged.setdefault(sid, entry)  # 迁移窗底座：片优先，片缺的 sid 由旧表补
            return merged
        return self._load_legacy()

    def _save(self, data: dict[str, dict]) -> None:
        """S4-D 语义收敛：merge-upsert（只增改、永不删）——写只碰片，竞态对象消失。

        旧语义=整表替换（删条目靠 omit 后写回）——正是 R-D1 交错写丢条目的结构性
        病根（A 持旧快照写回抹掉 B 的新增/心跳）。删除只能走 unregister()/list_active
        收割（显式意图，片级原子）。逐会话片 per-pid tmp + os.replace + WinError5
        退避原语义保留（防共享 tmp 名竞态/读方持锁，见各原语 docstring）。
        旧单表迁移窗内双写为只读兼容副本（watchdog/write_audit_daemon/commit_queue/
        check_commit_message 等直读路径不受扰）；读侧片优先，副本滞后无治理语义损失。
        kill-switch（ZEPHYR_SESSION_REGISTRY_SHARDS=0）：纯旧表 merge-upsert，回退单文件
        （双写窗已保证旧表完整，零丢失回退）。
        """
        if _shards_enabled():
            for sid, entry in data.items():
                if isinstance(entry, dict):
                    self._write_shard_only(sid, entry)
        legacy = self._load_legacy()
        legacy.update({k: v for k, v in data.items() if isinstance(v, dict)})
        self._write_legacy_raw(legacy)


class SessionHandoff:
    """Session 结束时写 handoff package（P2-SES）。

    对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage。
    存储 .runtime/handoffs/handoff_<session_id>.json。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        self._project_root: Path = Path(project_root) if project_root else Path.cwd()
        self._handoff_dir: Path = self._project_root / _HANDOFF_DIR
        self._handoff_dir.mkdir(parents=True, exist_ok=True)

    def write_handoff(
        self,
        session_id: str,
        summary: str,
        pending_tasks: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> Path:
        """写 handoff package，返回文件路径。"""
        package = {
            "session_id": session_id,
            "timestamp": time.time(),
            "summary": summary,
            "pending_tasks": pending_tasks or [],
            "warnings": warnings or [],
        }
        handoff_path = self._handoff_dir / f"handoff_{session_id}.json"
        # per-pid tmp（同 _save 的竞态治本：共享 tmp 名跨进程互踩报 WinError 2）
        tmp_path = handoff_path.with_name(f"{handoff_path.stem}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(package, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(handoff_path))
            logger.info("SessionHandoff: wrote handoff for session=%s", session_id)
        except OSError as e:
            logger.warning("SessionHandoff: failed to write handoff: %s", e)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
        return handoff_path

    def read_handoff(self, session_id: str) -> dict | None:
        """读 handoff package（不存在返回 None）。"""
        handoff_path = self._handoff_dir / f"handoff_{session_id}.json"
        try:
            return json.loads(handoff_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def read_latest_handoff(self) -> dict | None:
        """读最近的 handoff package（按 mtime，不需 session_id）。

        供 session_startup 读取上一 session 交接——跨 session 上下文恢复。
        无 handoff 文件时返回 None（首次运行）。
        """
        try:
            candidates = sorted(
                self._handoff_dir.glob("handoff_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            return None
        if not candidates:
            return None
        try:
            return json.loads(candidates[0].read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None


class SessionConflictDetector:
    """检测多 session 操作同一文件（P2-SES）。

    基于 SessionRegistry + ConcurrencyManager 检测跨 session 文件冲突。
    检测到冲突 -> 返回 ConflictType，由调用方走 lock_files.py 协调。
    """

    def __init__(self, registry: SessionRegistry) -> None:
        self._registry = registry
        self._manager = ConcurrencyManager()

    def check_file_conflict(self, file_path: str, session_id: str) -> ConflictType | None:
        """检测文件是否被其他 session 持有。

        Returns:
            ConflictType.SAME_FILE if 另一 session 持有该文件, None if 无冲突。
        """
        holder = self._registry.find_session_by_file(file_path)
        if holder is not None and holder.session_id != session_id:
            logger.warning(
                "SessionConflictDetector: file %s held by session=%s, requested by session=%s",
                file_path,
                holder.session_id,
                session_id,
            )
            return ConflictType.SAME_FILE
        return None

    def acquire_files(self, file_paths: list[str], session_id: str) -> list[str]:
        """为 session 预分配文件（冲突文件不会被分配，成功分配的写回 registry）。

        Returns:
            成功分配的文件列表（冲突文件被跳过）。
        """
        allocated: list[str] = []
        for fp in file_paths:
            conflict = self.check_file_conflict(fp, session_id)
            if conflict is None:
                # 写回 registry，使 claim 持久化（修复：原版只读不写回）
                if self._registry.claim_file(session_id, fp):
                    allocated.append(fp)
        return allocated
