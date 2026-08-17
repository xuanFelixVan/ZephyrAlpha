# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.paths
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
paths.py — 项目路径常量 SSoT（Single Source of Truth）

对标 AGENTS.md §6.4（最有利于 AI 施工的选择）
         YAML canonical SSoT 铁律

根因修复：此前 7 个文件各自通过 Path(__file__).parents[N] 独立计算
REPO_ROOT，导致：
  1. 目录层级调整需改 7 处
  2. DB_PATH 大小写冲突（state vs STATE）因无 SSoT 未被发现
  3. 路径常量分散定义，漂移风险极高

本文件是 src/zephyr/ 下所有路径常量的唯一真源。
任何需要 REPO_ROOT / DB_PATH / 路径常量的模块，必须从此处导入。

对标：
  - scripts/governance/_shared/constants.py（治理脚本侧的路径 SSoT）
  - Google Style Guide: "Define constants in one place"（常量只在一处定义）
  - Terraform: provider 配置集中定义，模块引用而非重定义
"""

from typing import Final

import functools
import os
from pathlib import Path


@functools.cache
def find_repo_root() -> Path:
    """从当前文件向上查找项目根目录（包含 src/zephyr/ 的目录）。

    比 parents[N] 或 .parent 链更健壮——不依赖文件深度，
    任何位置的模块都能正确定位项目根。

    S4 治本（2026-08-14，裁定书遗留项 6）：pip editable install 的 .pth 把
    ``import zephyr`` 硬锚主仓 src，本函数从主仓 zephyr.__file__ 向上推，
    REPO_ROOT 恒=主仓——worktree 内网关读错 registry。增加 worktree 感知：
    环境变量 ``ZEPHYR_WORKTREE_ROOT`` 显式注入优先（由 activate_env.ps1 或
    调用方设置），命中且含 src/zephyr/__init__.py 则直接返回。

    Returns:
        Path: 项目根目录的绝对路径。

    Raises:
        FileNotFoundError: 向上遍历到文件系统根仍未找到标记。
    """
    # S4：ZEPHYR_WORKTREE_ROOT 显式注入优先（worktree 感知）
    wt = os.environ.get("ZEPHYR_WORKTREE_ROOT")
    if wt:
        wt_path = Path(wt)
        if (wt_path / "src" / "zephyr" / "__init__.py").exists():
            return wt_path

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root (no src/zephyr/__init__.py found) from {current}")


REPO_ROOT: Final[Path] = find_repo_root()


def strip_session_worktree(root: Path) -> Path:
    """若 root 位于 session worktree（.aidrafts/<session>/ 或 .worktrees/<session>/）内，剥离回主仓库根。

    GATE-DEPGRAPH-OPS 治本 Phase 3（观测库单一定位）：
    worktree 进程内 REPO_ROOT 解析为 worktree 根，观测数据写入 worktree 而分裂。
    观测数据必须锚定主仓库——worktree merge/abort 后即删除。

    #ARCH-WORKTREE-ENV-001（2026-08-14）：扩展识别 .worktrees/<session>/——
    第二代机制（scripts/session_worktree.py，#ARCH-AICOLLAB-001）2026-08-11 落地后
    本函数长期未同步，导致 .worktrees 进程内 MAIN_REPO_ROOT == REPO_ROOT（指向
    worktree 自身），"观测数据锚定主仓库"对新机制完全失效。
    """
    parts = root.parts
    for marker in (".aidrafts", ".worktrees"):
        if marker in parts:
            return Path(*parts[: parts.index(marker)])
    return root


# 主仓库根（观测数据锚定点）：主仓库进程 MAIN_REPO_ROOT == REPO_ROOT；
# worktree 进程剥离 .aidrafts/<session> 或 .worktrees/<session> 前缀回主仓库。
MAIN_REPO_ROOT: Final[Path] = strip_session_worktree(REPO_ROOT)


def is_session_worktree_root(root: Path) -> bool:
    """root 恰为 session worktree 根（.worktrees/<sid>/ 或 .aidrafts/<sess>/）判定。

    父目录结构判定（非段包含匹配）——宿主 worktree 内嵌套的 pytest tmp 路径
    （.../.worktrees/<宿主>/.runtime/tmp/pytest_*/tmp_repo）不会误判宿主为
    worktree（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T2 证1/证3 同型陷阱修复模式）。
    """
    return root.parent.name in (".worktrees", ".aidrafts")


def anchor_main_root(root: Path) -> Path:
    """session worktree 根 → 主仓根；其他路径原样返回（is_session_worktree_root 配套）。

    与 strip_session_worktree 的区别：本函数只做单级父目录结构判定，对
    嵌套 tmp 测试库路径安全（不段匹配）；strip_session_worktree 是深路径段
    剥离（用于任意深度路径）。仓级状态锚定调用方应根据入参形态选择。
    """
    if is_session_worktree_root(root):
        return root.parent.parent
    return root

# 治本(2026-07-19): PROJECT_ROOT 作为 REPO_ROOT 的语义别名（canonical SSoT 定义点）。
# 某些模块（如 immutable_core）的测试契约要求 monkeypatch PROJECT_ROOT 属性，
# 将 canonical 定义放在此处避免 SSOT-REDEFINITION gate 阻断（消除分散重定义）。
# 消费者 MUST from zephyr.shared.io.paths import PROJECT_ROOT，禁止在各自模块重定义。
PROJECT_ROOT: Final[Path] = REPO_ROOT

DB_DIR: Final[Path] = REPO_ROOT / "data"

# DB_PATH — 仓级共享治理库（governance.db），锚定主仓根。
# #ARCH-WORKTREE-DB-SPLIT-001 裁定（2026-08-15）：观测/治理状态归属主仓，
# worktree 进程与主仓进程读写同一份——原 REPO_ROOT 相对路径在 worktree 内
# 解析出第二物理副本（.worktrees/<sid>/data/databases/governance.db），
# 观测数据双副本分裂（worktree abort 即丢失）+ 生成器按 cwd 锚定读不同库
# 致派生统计双源振荡（126 蓝图 tracked 文档反复 dirty 实证）。
# 主仓进程 MAIN_REPO_ROOT == REPO_ROOT，语义不变；worktree 进程锚主仓。
# 测试隔离不受影响：tmp_repo 测试库经显式 db_path 参数/fixture 注入，不经本常量。
# computed locally to avoid circular import from zephyr.governance.persistence
# Previously: from zephyr.governance.persistence.sqlite_schema import DB_PATH
DB_PATH: Final[Path] = MAIN_REPO_ROOT / "data" / "databases" / "governance.db"

# 治本（2026-08-17，AI-AUDIT11）：真源漂移修正——原指向 src/zephyr/governance/rule_enforcement
# （物理不存在，gov_enforcement 迁移遗留），dispatch_fle_gates 静默空转。唯一物理真源=
# src/zephyr/gov_enforcement/rule_enforcement（_registry.yaml 所在）。
GATES_DIR: Final[Path] = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_enforcement"
SNAPSHOTS_DIR: Final[Path] = REPO_ROOT / ".runtime" / "snapshots"
RATIONALE_LOG_PATH: Final[Path] = REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"

VECTOR_INDEX_DIR: Final[Path] = REPO_ROOT / ".audit_cache" / "vector_index"
MODELS_CACHE_DIR: Final[Path] = REPO_ROOT / ".audit_cache" / "models"
VMS_PERSIST_DIR: Final[Path] = REPO_ROOT / "data" / "vector_db"

# 治本（裁定#6 路径SSoT）：审计数据目录真源——所有审计模块（gov_audit.writer/integrity 等）
# 必须从此处导入 AUDIT_DATA_DIR，禁止裸 `Path.cwd()/"data"/"audit-trail"`（违反"禁止相对路径"硬约束）。
AUDIT_DATA_DIR: Final[Path] = REPO_ROOT / "data" / "audit-trail"

# DM-90974 Phase 2 治本（2026-07-19 真源收敛）：depgraph dirty flag 路径真源。
# PG-write 脚本（apply_depgraph.py 等）成功 commit DB 后调用 mark_depgraph_dirty() 落此空文件，
# GATE-REGENERATE reconciler 的 _trigger_domain_doc 检测此 flag 存在即 fire，_reconcile_domain_doc
# 成功后删除。真源仍是 PostgreSQL DB；此 flag 仅作"运行时 DB 写入→下次 commit 触发 reconciler"的桥接信号。
# 历史问题：原在 scripts/governance/_shared/constants.py:49 和
# src/zephyr/governance/audit/reconciliation_registry.py:2864 两处独立重算路径字符串，
# 路径变更只改一处会导致写入端与读取端不一致（reconciler 静默失效）。治本：收敛为单一真源。
# 写入端：scripts/governance/_shared/constants.py re-export 此常量（scripts/ 可 import src/）。
# 读取端：reconciliation_registry.py 直接 import 此常量。
DEPGRAPH_DIRTY_FLAG: Final[Path] = REPO_ROOT / "data" / "databases" / "depgraph_dirty.flag"


def get_tmp_dir() -> Path:
    """返回运行时临时目录 REPO_ROOT / '.runtime' / 'tmp'，并确保目录存在。

    Returns:
        Path: 临时目录的绝对路径（已确保存在）。
    """
    tmp_dir = REPO_ROOT / ".runtime" / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def get_data_dir() -> Path:
    """返回数据目录 REPO_ROOT / 'data'，并确保目录存在。

    Returns:
        Path: 数据目录的绝对路径（已确保存在）。
    """
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """返回配置目录 REPO_ROOT / 'config'，并确保目录存在。

    Returns:
        Path: 配置目录的绝对路径（已确保存在）。
    """
    config_dir = REPO_ROOT / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


__all__ = [
    "AUDIT_DATA_DIR",
    "DB_DIR",
    "DB_PATH",
    "DEPGRAPH_DIRTY_FLAG",
    "GATES_DIR",
    "MAIN_REPO_ROOT",
    "MODELS_CACHE_DIR",
    "PROJECT_ROOT",
    "RATIONALE_LOG_PATH",
    "REPO_ROOT",
    "SNAPSHOTS_DIR",
    "VECTOR_INDEX_DIR",
    "VMS_PERSIST_DIR",
    "find_repo_root",
    "get_config_dir",
    "get_data_dir",
    "get_tmp_dir",
    "strip_session_worktree",
]
