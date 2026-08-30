# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.session_concurrency
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.infra.process_pool (is_pid_alive)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway ; zephyr.gov_enforcement.rule_bridge.session_worktree (find_breaking_change_session, register_dependency, clear_dependency) ; zephyr.gov_enforcement.commit_gates.import_integrity_gate (_check_active_session_held_target, Phase 2.5) ; zephyr.governance.audit.reconcile_worker (SessionRegistry) ; zephyr.governance.audit.reconcile_runner (SessionRegistry)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SessionRegistry 原子写入（tmp + os.replace）；session 存活判定双轨：pid>0=PID liveness+TTL(3600s)双判据（S3-A 治本），pid=0=心跳新鲜度(90s)判据（#ARCH-HEARTBEAT-001 P0 治本，daemon 每 30s 刷新 last_heartbeat，stale session 90s 自动释放 held_files 消除 allow_overlap 62× 超阈）；last_activity 独立活性锚点（#ARCH-HEARTBEAT-002 治本 2026-07-23：仅 register/claim_file/register_dependency 刷新，heartbeat 不刷新，daemon 检测 idle 超 _ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s 自动退出，消除僵尸 daemon 永久保活死 session 的活性反转）；不替代 lock_files.py（文件级锁）；claim_file 懒注册+不覆盖冲突+幂等；release_file 移除 held_files；get_session 只读无写副作用；is_breaking_change 字段标记治本变更 session（§9.7 治本 2026-07-04）；find_breaking_change_session 查找活跃 breaking_change session（只读，排除自身+忽略死/过期，供 session_worktree_start 双向阻断调用）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SessionRegistry 读写失败不抛异常（返回空/False）；detect_mtime_conflict 文件不存在返回 False
# [TESTS] tests/test_session_concurrency.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Session 级并发协调模块（P2-SES 落地）。

从 Stub 落地为真实的 session 级协调：
1. SessionRegistry：注册活跃 session（PID + session_id + start_time + 持有文件锁）
   - 存储在 .runtime/session_registry.json（原子写入，对标 lock_files.py）
   - TTL=3600s（session 超时自动注销）
2. SessionHandoff：session 结束时写 handoff package
   - 对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage
3. SessionConflictDetector：检测多 session 操作同一文件 -> 走 lock_files.py 协调

设计约束：
- 不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册
- 不替代 F23 AgentOrchestrator（任务级），而是补齐 session 级空缺
- 存储用 JSON 文件（非 SQLite，避免并发写锁）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 str
#   code: session_concurrency.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: last_read_mtime 参数
#   fields: 参数 last_read_mtime，类型注解 float
#   code: session_concurrency.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ZephyrLock
#   name_en: ZephyrLock
#   intro: class ZephyrLock 源码 L166-L181
#   desc: 公共方法（定义序）: acquire, release, is_active；源码 L166-L181
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ConcurrencyManager
#   name_en: ConcurrencyManager
#   intro: class ConcurrencyManager 源码 L185-L208
#   desc: 公共方法（定义序）: check_conflict, pre_allocate, resolve_conflict；源码 L185-L208
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ detect_mtime_conflict
#   name_en: detect_mtime_conflict
#   intro: detect_mtime_conflict(path, last_read_mtime) 源码 L211-L216
#   desc: 源码 L211-L216
#   inputs: path last_read_mtime
#   outputs: bool
# - id: A4
#   name_zh: ④ SessionInfo
#   name_en: SessionInfo
#   intro: 活跃 session 注册信息。
#   desc: 活跃 session 注册信息。；公共方法（定义序）: to_dict, from_dict；源码 L264-L309
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ SessionRegistry
#   name_en: SessionRegistry
#   intro: Session 级注册表（P2-SES）。
#   desc: Session 级注册表（P2-SES）。 存储在 .runtime/session_registry.json（原子写入：tmp + os.replace）。 TTL=3600…；公共方法（定义序）: save, l…
#   inputs: project_root
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ SessionHandoff
#   name_en: SessionHandoff
#   intro: Session 结束时写 handoff package（P2-SES）。
#   desc: Session 结束时写 handoff package（P2-SES）。 对标 drift_detector/blueprint.md §6.14 Cross-Session…；公共方法（定义序）: write_ha…
#   inputs: project_root
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ SessionConflictDetector
#   name_en: SessionConflictDetector
#   intro: 检测多 session 操作同一文件（P2-SES）。
#   desc: 检测多 session 操作同一文件（P2-SES）。 基于 SessionRegistry + ConcurrencyManager 检测跨 session 文件冲突。 检测到…；公共方法（定义序）: check_f…
#   inputs: registry
#   outputs: 返回值
#   （注：A7 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway ; zephyr.gov_enforcement.…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> O1
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

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from zephyr.shared.infra.process_pool import is_pid_alive

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
_REGISTRY_PATH: str = ".runtime/session_registry.json"
_HANDOFF_DIR: str = ".runtime/handoffs"


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
        )


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


class SessionRegistry:
    """Session 级注册表（P2-SES）。

    存储在 .runtime/session_registry.json（原子写入：tmp + os.replace）。
    TTL=3600s（session 超时自动注销）。

    不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册。
    不替代 F23 AgentOrchestrator（任务级），补齐 session 级空缺。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        root = Path(project_root) if project_root else Path.cwd()
        # 锚主仓根（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T2 实证治本）：
        # session registry 是仓级共享状态——worktree（.worktrees/<sid>/ 结构）内
        # 构造时自动锚定主仓，消除 claim（worktree 内网关进程写 worktree registry）
        # 与 worker 三证（锚主仓读主仓 registry）的双 registry 分裂——合法 worker
        # 被证3 误判"session 已死"拒启（2026-08-14 两例实证）。
        # 嵌套 fake worktree（测试 tmp_repo/.worktrees/<sid>）同样锚宿主根，语义一致。
        if root.parent.name == ".worktrees":
            root = root.parent.parent
        self._project_root: Path = root
        self._registry_path: Path = self._project_root / _REGISTRY_PATH
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        # 进程内读写锁：串行化 _load->修改->_save 的 read-modify-write 序列，
        # 消除 claim_file/release_file 等的 TOCTOU 竞态（两线程并发 claim 同一文件
        # 都读到"无人持有"->都写回->双 claim）。跨进程并发由 gateway 全局锁 + 原子
        # os.replace 兜底；此处只解决进程内多线程竞态（红蓝对抗 TestConcurrentClaimRace）。
        self._lock = threading.RLock()

    def save(self, data) -> None:
        """公共接口：save（Stage 4 公共化）。"""
        return self._save(data)

    def load(self) -> dict[str, dict]:
        """公共接口：load（Stage 4 公共化）。"""
        return self._load()

    def register(
        self,
        session_id: str,
        pid: int | None = None,
        held_files: list[str] | None = None,
        is_breaking_change: bool = False,
        task_files: list[str] | None = None,
        depends_on_sessions: list[str] | None = None,
    ) -> SessionInfo:
        """注册一个活跃 session。

        Args:
            depends_on_sessions: 本 session 依赖的其他 session_id 列表
                （#ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2 / TRAE-072）。
                commit 前由 _check_cross_commit_deps 检查依赖 session 是否仍活跃。
        """
        with self._lock:
            info = SessionInfo(
                session_id=session_id,
                pid=pid if pid is not None else os.getpid(),
                start_time=time.time(),
                held_files=held_files or [],
                last_heartbeat=time.time(),
                last_activity=time.time(),
                is_breaking_change=is_breaking_change,
                task_files=task_files or [],
                depends_on_sessions=depends_on_sessions or [],
            )
            data = self._load()
            data[session_id] = info.to_dict()
            self._save(data)
            logger.info(
                "SessionRegistry: registered session=%s pid=%d breaking_change=%s deps=%s",
                session_id,
                info.pid,
                is_breaking_change,
                info.depends_on_sessions,
            )
            return info

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
            data = self._load()
            now = time.time()  # noqa: m46-time — 注册依赖时的时间戳（对标 claim_file L404 同模式）
            existing = data.get(session_id)
            if existing is None or not _is_session_alive(SessionInfo.from_dict(existing), now):
                logger.warning(
                    "SessionRegistry: register_dependency auto-registering session=%s (not registered or dead/expired)",
                    session_id,
                )
                data[session_id] = SessionInfo(
                    session_id=session_id,
                    pid=os.getpid(),
                    start_time=now,
                    held_files=[],
                    last_heartbeat=now,
                    last_activity=now,
                ).to_dict()
                self._save(data)

            info = SessionInfo.from_dict(data[session_id])
            info.last_heartbeat = now  # noqa: m46-time — 顺带心跳刷新（对标 claim_file L436）
            info.last_activity = now  # 真实治理操作刷新活性锚点（活性反转治本）
            if depends_on_session_id not in info.depends_on_sessions:
                info.depends_on_sessions.append(depends_on_session_id)
            data[session_id] = info.to_dict()
            self._save(data)
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
            data = self._load()
            if session_id not in data:
                return False
            info = SessionInfo.from_dict(data[session_id])
            if depends_on_session_id in info.depends_on_sessions:
                info.depends_on_sessions.remove(depends_on_session_id)
                data[session_id] = info.to_dict()
                self._save(data)
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
        """注销一个 session。"""
        with self._lock:
            data = self._load()
            if session_id not in data:
                return False
            del data[session_id]
            self._save(data)
            logger.info("SessionRegistry: unregistered session=%s", session_id)
            return True

    def heartbeat(self, session_id: str) -> bool:
        """更新 session 心跳时间（防 TTL 过期）。"""
        with self._lock:
            data = self._load()
            if session_id not in data:
                return False
            data[session_id]["last_heartbeat"] = time.time()
            self._save(data)
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
            if expired:
                reaped = 0
                for sid in expired:
                    if now - SessionInfo.from_dict(data[sid]).last_heartbeat > _REAP_GRACE_SECONDS:
                        del data[sid]
                        reaped += 1
                if reaped:
                    self._save(data)
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
        """
        data = self._load()
        if session_id not in data:
            return None
        info = SessionInfo.from_dict(data[session_id])
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
            data = self._load()
            now = time.time()

            # 懒注册：session 不存在或死/过期（S3-A: PID 死亡也触发懒注册，用当前 PID 覆盖）
            existing = data.get(session_id)
            if existing is None or not _is_session_alive(SessionInfo.from_dict(existing), now):
                logger.warning(
                    "SessionRegistry: claim_file auto-registering session=%s (not registered or dead/expired)",
                    session_id,
                )
                data[session_id] = SessionInfo(
                    session_id=session_id,
                    pid=os.getpid(),
                    start_time=now,
                    held_files=[],
                    last_heartbeat=now,
                    last_activity=now,
                ).to_dict()
                self._save(data)  # 立即持久化懒注册（即使后续 claim 冲突，session 仍可查询）

            # 检查是否被其他活跃 session 持有
            for sid, d in data.items():
                if sid == session_id:
                    continue
                other = SessionInfo.from_dict(d)
                if not _is_session_alive(other, now):
                    continue  # 死/过期 session，忽略其 claim（S3-A: PID+TTL 双判据）
                other_held_norm = [_normalize_file_path(f, self._project_root) for f in other.held_files]
                if norm in other_held_norm:
                    logger.warning(
                        "SessionRegistry: claim_file conflict — file=%s held by session=%s, requested by=%s",
                        norm,
                        sid,
                        session_id,
                    )
                    return False

            # 幂等 / 新增
            own = SessionInfo.from_dict(data[session_id])
            own.last_heartbeat = now  # claim 顺带心跳
            own.last_activity = now  # claim 是真实治理操作，刷新活性锚点（活性反转治本）
            own_norm = [_normalize_file_path(f, self._project_root) for f in own.held_files]
            if norm not in own_norm:
                own.held_files.append(norm)
            data[session_id] = own.to_dict()
            self._save(data)
            return True

    def release_file(self, session_id: str, file_path: str) -> bool:
        """释放 session 对某文件的持有。

        Returns: True=成功释放，False=session 未注册 或 文件未被持有。
        """
        with self._lock:
            norm = _normalize_file_path(file_path, self._project_root)
            data = self._load()
            if session_id not in data:
                return False
            info = SessionInfo.from_dict(data[session_id])
            held_norm = [_normalize_file_path(f, self._project_root) for f in info.held_files]
            if norm not in held_norm:
                return False
            # 移除归一化匹配到的原始条目
            for orig in list(info.held_files):
                if _normalize_file_path(orig, self._project_root) == norm:
                    info.held_files.remove(orig)
            data[session_id] = info.to_dict()
            self._save(data)
            return True

    def _load(self) -> dict[str, dict]:
        """原子读取 registry（文件不存在/损坏返回空 dict）。"""
        try:
            if not self._registry_path.exists():
                return {}
            content = self._registry_path.read_text(encoding="utf-8")
            return json.loads(content) if content.strip() else {}
        except (OSError, ValueError) as e:
            logger.warning("SessionRegistry: failed to load registry: %s", e)
            return {}

    def _save(self, data: dict[str, dict]) -> None:
        """原子写入 registry（per-pid tmp + os.replace，防并发写损坏）。

        tmp 文件名带 PID（session_registry.<pid>.tmp）——共享单 tmp 名存在跨进程
        竞态：A 进程 os.replace 把 tmp 移走后，B 进程 os.replace 报 WinError 2
        （系统找不到指定的文件），该次写静默丢失（仅 warning）。2026-08-15
        AI-NORTH-001 实证：心跳 daemon 与 commit 进程并发写互踩，心跳丢失致
        session 假性过期反复自动重注册。per-pid tmp 从构造上消除共享名竞态；
        os.replace（MoveFileEx REPLACE_EXISTING）本身原子，JSON 不会撕裂。
        """
        tmp_path = self._registry_path.with_name(f"{self._registry_path.stem}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(self._registry_path))
        except OSError as e:
            logger.warning("SessionRegistry: failed to save registry: %s", e)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


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
