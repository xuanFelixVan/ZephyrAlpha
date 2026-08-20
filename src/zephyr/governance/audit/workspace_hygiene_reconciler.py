# [BLUEPRINT] MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | docs/01_policies_and_standards/policies/workspace_governance_policy.md | §ARCH-TOOL-HEALTH-V1 Phase 6 联动 + DEBT-WORKSPACE-001/002 消除

# [MODULE] zephyr.governance.audit.workspace_hygiene_reconciler

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); zephyr.infrastructure.git_batcher (GitCommandBatcher, auto-sync restore 批量化); stdlib (logging, subprocess)

# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] post-commit 事件触发（任何 commit 都触发，工作区卫生是全局关注）；reconciler 永不抛异常（异常降级为 warn）；只自动 restore auto-sync 产物，不触碰真实代码修改；blueprint.md 不在 auto-sync 清单（#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001，混合文件文件级分类误伤正文）

# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _AUTO_SYNC_PATTERNS

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] reconcile 永不抛异常——subprocess/解析失败降级为 ReconcileResult(action="warn")

# [TESTS] tests/governance/audit/test_workspace_hygiene_reconciler.py

# [A_module] module_id=MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module

# [TTL] permanent

# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)

"""

workspace_hygiene_reconciler.py — 工作区卫生自动清理 reconciler（DEBT-WORKSPACE-001/002 消除，2026-07-20）。



post-commit 事件触发，检测工作区残留的 auto-sync 产物并自动 ``git restore`` 还原到 HEAD

版本，消除 workspace_governance_policy.md §2.2 定义的"还原优先"策略的君子协定依赖。



治本动机（第一性原理）

--------------------

workspace_governance_policy.md 附录 B 已登记 DEBT-WORKSPACE-001/002 为君子协定：



- DEBT-WORKSPACE-001（§5.1 会话开始检查 git status）—— 无自动触发

- DEBT-WORKSPACE-002（§5.2 提交前检查工作区只保留本次任务相关改动）—— 无自动触发



100% AI 开发下，AI 不会自觉执行 ``git checkout -- <file>`` 还原 auto-sync 产物残留。

每次 GitCommitGateway post-commit 触发 reconciler 重生成产物（dashboard、catalog、

path-tree 等），这些产物是**被 track 的**，导致工作区永久有 modified 文件——AI 每次看

``git status`` 都需判断"这些改动是否相关"→ 判断疲劳 → 误判 → 漂移。



本 reconciler 把"还原优先"从君子协定升级为自动化：post-commit 检测工作区 auto-sync 产物

残留，自动 ``git restore`` 还原。真实代码修改（非 auto-sync 产物）不自动处理，仅告警。



批量化（GIT-BUDGET-INV-002 合规，2026-07-20 治本）

--------------------------------------------------

早期实现 ``_git_restore_individual`` 在批量 restore 失败时逐文件重试，违反

trae_064 ARCH-GIT-CALL-BUDGET GIT-BUDGET-INV-002 批量化强制（N 文件 = N subprocess

是 git.exe 崩溃放大源）。治本：改用 ``GitCommandBatcher.git_restore_batch`` 单次

``git restore -- <files>`` 批量调用，fail-open 不逐个重试（依赖下次 post-commit 兜底）。



auto-sync 产物清单（workspace_governance_policy.md §2.1 派生）

-----------------------------------------------------------

- ``docs/02_enterprise_architecture/generated/`` —— 生成器产物（mermaid 图等）

- ``docs/02_enterprise_architecture/02_domain_architecture_docs/`` —— 域架构文档

- ``docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_`` —— 全局树

- ``docs/02_enterprise_architecture/00_overview_entry/`` —— 概览入口（navigation_index/panorama 派生产物）

- ``docs/**/_registry/catalogs/rule_catalog_registry.yaml`` —— 规则目录

- ``docs/**/_registry/catalogs/registry_master_index.yaml`` —— 注册表主索引

- ``data/asset_index/unified-asset-index.yaml`` —— 资产索引

- ``data/reports/dashboard.json`` —— 仪表盘快照

- ``data/reports/reconciliation-report.md`` —— 对账报告

- ``data/scans/raw-asset-scan.json`` —— 资产扫描

- ``data/architecture_health/latest.json`` —— 健康快照

- ``data/classified/classified-assets.json`` —— 分类资产

- ``data/audit-trail/`` —— 审计追踪日志（运行时，reconciler 追加）

- ``data/cache/`` —— 缓存（运行时，reconciler 重生成）

- ``scripts/governance/meta/rules_integrity_db.json`` —— 已移除出 auto-sync（偏离1修复，2026-07-22）：

  原因：该文件是 register() 写入产物（golden hash DB），列入 auto-sync 导致 hash 被还原回 HEAD

- ``docs/03_modules/**/blueprint.md`` —— 已移除（#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001，2026-07-21）

  原因：blueprint.md 是混合文件（frontmatter 派生 + 正文手写），文件级分类误伤正文编辑

  frontmatter 变更由 blueprint_frontmatter_reconciler._commit_auto 自动提交，无需 auto-restore

- ``architecture_model/index.yaml`` —— GATE-ARCH-MODEL reconciler 产物

- ``docs/_archive/architecture_debt_registry_v2.md`` —— 架构债务注册表（已归档，2026-07-24 裁定#221/#222）

- ``data/budget/shutdown_snapshot.json`` —— 预算关闭快照

- ``data/metrics/kill_switch_probes.jsonl`` —— kill-switch 探针

- ``data/runtime_violation_snapshot/latest.json`` —— 运行时违规快照

- ``data/telemetry/blueprint_reads.jsonl`` —— 蓝图读取遥测

- ``data/telemetry/dev/metrics.jsonl`` —— 开发指标

- ``scripts/governance/script_manifest.yaml`` / ``scripts/script_manifest.yaml`` —— 脚本清单

- ``scripts/governance/migrate_sqlite_to_pg/03_create_*_schema.sql`` —— PG schema 产物



判定

----

- 工作区无 modified 文件 → skip

- 有 auto-sync 产物残留 → 自动 ``git restore``，返回 clean（已清理）

- 有非 auto-sync 的真实代码修改 → warn（不自动处理，AI 需关注）

- 同时有 auto-sync + 真实代码修改 → restore auto-sync + warn 真实代码修改



priority=890（晚于 commit_gateway_abuse_monitor(875)，早于 remediation_progress(900)）



Usage

-----

::



    from zephyr.governance.audit.workspace_hygiene_reconciler import (

        make_workspace_hygiene_reconciler,

    )



    registry.register(make_workspace_hygiene_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: post-commit 事件参数
#   fields: committed_files 已提交文件列表 + session_id 会话标识
#   code: _reconcile(committed_files, session_id) L574
# - id: I2
#   name: 工作区 git 状态 文本数据
#   fields: git status --porcelain 原始输出（XY状态+路径）
#   code: git status --porcelain L498
# - id: I3
#   name: auto-sync 产物清单 内置常量
#   fields: 路径前缀元组（生成器产物/报告/缓存/遥测等约25条）
#   code: _AUTO_SYNC_PREFIXES L236
# - id: I4
#   name: gateway 缓冲待提交文件集
#   fields: 前序 reconciler 已写盘并 buffer 待 flush 的文件路径集合
#   code: gateway._batcher.buffered_files() L617
# 层: 算法
# - id: A1
#   name_zh: ① 工作区修改清单获取与解析
#   name_en: _git_status_porcelain + _parse_porcelain
#   intro: 跑 git status 拿到工作区所有 modified 文件，只留修改态跳过新增删除重命名
#   desc: subprocess 调 git status --porcelain（超时10s）→ 逐行解析 XY 状态码，跳过 R/??/D/A，路径转 POSIX 去引号；fail-open 失败返回空列表
#   inputs: I2
#   outputs: modified 修改文件路径列表
#   invariant: 永不抛异常，失败降级为空列表
# - id: A2
#   name_zh: ② auto-sync 产物分类
#   name_en: _is_auto_sync_product
#   intro: 把修改文件分成两类：可自动还原的生成产物 vs 需要人看的真实代码改动
#   desc: 前缀匹配 _AUTO_SYNC_PREFIXES + catalogs 下两个派生 yaml → auto_sync_files；其余为 real_changes；再排除 gateway buffer 中待 flush 文件防"日志说已重生实际未重生"盲区
#   inputs: A1 I3 I4
#   outputs: auto_sync_files + real_changes 两清单
# - id: A3
#   name_zh: ③ 批量 git restore 还原
#   name_en: GitCommandBatcher.git_restore_batch
#   intro: 单次 subprocess 把所有 auto-sync 产物还原回 HEAD 版本，不逐个重试
#   desc: 一次 git restore -- <files> 批量调用（GIT-BUDGET-INV-002 合规，N文件=1 subprocess），fail-open 返回成功清单
#   inputs: A2
#   outputs: restored_count + restore_failed
# - id: A4
#   name_zh: ④ 结果判定 action
#   name_en: _reconcile 判定段
#   intro: 根据还原结果和真实改动情况给出 skip/clean/warn 三档结论
#   desc: 无修改→skip；有真实代码修改或 restore 失败→warn（不自动处理真实改动）；仅 auto-sync 且全部还原成功→clean；异常兜底→warn
#   inputs: I1 A2 A3
#   outputs: action + detail 详情串
#   invariant: 永不抛异常；真实代码修改只告警不还原
# 层: 输出
# - id: O1
#   name_zh: 工作区卫生对账结果
#   name_en: ReconcileResult
#   intro: 三档结论（skip/clean/warn）+ 明细，告知 commit 后工作区是否已清理干净
#   invariant: action ∈ {skip, clean, warn}
#   downstream: GitCommitGateway post-commit 编排（gov_enforcement.rule_bridge.git_commit_gateway）
# - id: O2
#   name_zh: reconciler 注册规格
#   name_en: ReconcilerSpec
#   intro: gate_id=GATE-WORKSPACE-HYGIENE、priority=890 的 trigger+reconcile 注册单元
#   downstream: reconciliation_registry 注册，GitCommitGateway 调度
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# A1 --> A2
# I3 --> A2
# I4 --> A2
# A2 --> A3
# A2 --> A4
# A3 --> A4
# I1 --> A4
# A4 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
import subprocess

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.infrastructure.git_batcher import GitCommandBatcher
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)


_GATE_ID = "GATE-WORKSPACE-HYGIENE"

# priority=890: 晚于 commit_gateway_abuse_monitor(875)，早于 remediation_progress(900)

_PRIORITY = 890


# git status --porcelain 超时（秒）

_GIT_STATUS_TIMEOUT = 10


# === auto-sync 产物路径前缀/模式（workspace_governance_policy.md §2.1 派生）===

# 精确前缀匹配（路径以这些字符串开头）

_AUTO_SYNC_PREFIXES: tuple[str, ...] = (
    "docs/02_enterprise_architecture/generated/",
    "docs/02_enterprise_architecture/02_domain_architecture_docs/",
    "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_",
    "docs/02_enterprise_architecture/00_overview_entry/",
    "docs/_archive/architecture_debt_registry_v2.md",
    "data/asset_index/unified-asset-index.yaml",
    "data/reports/dashboard.json",
    "data/reports/reconciliation-report.md",
    "data/scans/raw-asset-scan.json",
    "data/architecture_health/latest.json",
    "data/classified/classified-assets.json",
    "data/budget/shutdown_snapshot.json",
    "data/metrics/kill_switch_probes.jsonl",
    # 目录前缀匹配（避免 SSoT 路径硬编码，VOCAB-CHAIN gate 合规）
    "data/runtime_violation_snapshot/",
    "data/telemetry/",
    "data/audit-trail/",
    "data/cache/",
    # rules_integrity_db.json 已移除出 auto-sync（偏离1修复，2026-07-22；
    # 2026-08-02 audit-02 治本：原修复仅加注释未删行，导致写入→还原循环仍存在）：
    # 该文件是 validate_rules_integrity.py --register 的写入产物（golden hash DB），
    # 非"派生产物"。列入 auto-sync 导致 register() 写入的新 hash 被 git restore 还原回
    # HEAD，形成"写入→还原"循环，post-commit reconciler 漏触发后 hash 永远停留旧值。
    "scripts/governance/script_manifest.yaml",
    "scripts/script_manifest.yaml",
    "architecture_model/index.yaml",
    # PG schema 迁移产物（reconciler 自动同步）
    "scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql",
    "scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql",
)


# 通配后缀匹配（路径以这些后缀结尾）

_AUTO_SYNC_SUFFIXES: tuple[str, ...] = (
    # blueprint.md 是 blueprint_frontmatter_reconciler 的产物
    # 仅匹配 docs/03_modules/ 下的 blueprint.md
)


def _is_auto_sync_product(file_path: str) -> bool:
    """判断文件是否属于 auto-sync 产物（workspace_governance_policy.md §2.1）。



    Args:

        file_path: 工作区中的文件路径（相对仓库根，POSIX 风格）。



    Returns:

        True 如果是 auto-sync 产物；False 如果是真实代码修改。

    """

    # 精确前缀匹配

    for prefix in _AUTO_SYNC_PREFIXES:
        if file_path.startswith(prefix):
            return True

    # #ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001 (2026-07-21): blueprint.md 已从 auto-sync 清单移除

    # 原因：blueprint.md 是混合文件（frontmatter 派生 + 正文手写），文件级分类误伤正文编辑

    # frontmatter 变更由 blueprint_frontmatter_reconciler._commit_auto 自动提交，无需 auto-restore

    # 旧规则（已删除）：if file_path.endswith("/blueprint.md") and file_path.startswith("docs/03_modules/"): return True

    # registry catalogs 下的派生产物（rule_catalog_registry / registry_master_index）

    if file_path.startswith("docs/01_policies_and_standards/_registry/catalogs/"):
        if file_path.endswith(("rule_catalog_registry.yaml", "registry_master_index.yaml")):
            return True

    return False


def _parse_porcelain(output: str) -> list[str]:
    """解析 ``git status --porcelain`` 输出，返回 modified 文件路径列表。



    仅返回 `` M`` / ``MM`` / ``M `` 状态的文件（已修改，非新增/删除/重命名）。

    跳过 untracked（``??``）、deleted（`` D``）、renamed（``R``）等。



    Args:

        output: ``git status --porcelain`` 的原始输出。



    Returns:

        修改文件路径列表（POSIX 风格，已 strip 尾部 \\r）。

    """

    files: list[str] = []

    for line in output.splitlines():
        if len(line) < 4:
            continue

        # porcelain 格式："XY path" 或 "XY path -> path"（rename）

        # X = staged status, Y = worktree status

        status = line[:2]

        path = line[3:]

        # Windows CRLF 兼容

        path = path.rstrip("\r")

        # 跳过 rename（R）

        if "R" in status:
            continue

        # 跳过 untracked（??）

        if status == "??":
            continue

        # 跳过 deleted（D）

        if "D" in status:
            continue

        # 跳过 added（A）—— 新增文件不是 auto-sync 产物

        if "A" in status:
            continue

        # 处理 rename 的 "path -> path" 格式（虽然上面已跳过 R，但防御性处理）

        if " -> " in path:
            path = path.split(" -> ")[-1]

        # 转换为 POSIX 风格（git status 在 Windows 上可能用反斜杠）

        path = path.replace("\\", "/")

        # 去除引号（git status 对含特殊字符的路径会加引号）

        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]

        files.append(path)

    return files


def _git_status_porcelain(repo_root: str) -> list[str]:
    """获取工作区 modified 文件列表（git status --porcelain）。



    fail-open：git status 失败返回空列表（无法检测工作区卫生，降级为不触发清理）。



    Args:

        repo_root: 仓库根路径。



    Returns:

        修改文件路径列表（POSIX 风格）。

    """

    try:
        result = run_subprocess_hidden(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_STATUS_TIMEOUT,
        )

        if result.returncode != 0:
            logger.warning("workspace_hygiene: git status failed (rc=%d): %s", result.returncode, result.stderr[:200])

            return []

        return _parse_porcelain(result.stdout)

    except (subprocess.TimeoutExpired, Exception) as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning("workspace_hygiene: git status error: %s", e)

        return []


def make_workspace_hygiene_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-WORKSPACE-HYGIENE post-commit 工作区卫生自动清理 reconciler。



    Args:

        gateway: GitCommitGateway 实例（仅用其 project_root）。



    Returns:

        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。

        trigger 永远返回 True（任何 commit 都触发工作区卫生检查——全局关注）。

    """

    project_root = gateway.project_root

    # GitCommandBatcher 单例——reconciler 生命周期内复用，避免每次 reconcile 重建

    # 使用 batcher.git_restore_batch 替代 _git_restore + _git_restore_individual

    # （GIT-BUDGET-INV-002 合规：N 文件 = 1 subprocess，不逐个重试）

    batcher = GitCommandBatcher(project_root)

    def _trigger(committed_files: list[str]) -> bool:

        # 任何 commit 都触发——工作区卫生是全局关注，不限文件类型

        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        try:
            # 1. 获取工作区 modified 文件列表

            modified = _git_status_porcelain(str(project_root))

            if not modified:
                return ReconcileResult(
                    action="skip",
                    detail="workspace clean (no modified files)",
                    gate_id=_GATE_ID,
                )

            # 2. 分类：auto-sync 产物 vs 真实代码修改

            auto_sync_files = [f for f in modified if _is_auto_sync_product(f)]

            real_changes = [f for f in modified if not _is_auto_sync_product(f)]

            # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001（2026-07-30）：
            # 排除已被前序 reconciler 写盘并 buffer 待提交的文件——这些文件正等待
            # flush() 批量提交。若 git restore 还原它们，flush() 时
            # git diff --cached --quiet 返回 0（NOTHING_TO_COMMIT），而前序 reconciler
            # 已记 auto_committed，造成"日志说已重生实际未重生"的治理盲区。
            #
            # 典型冲突：GATE-ASSET-INDEX(priority=170) bootstrap 写索引文件 → buffer()；
            # workspace_hygiene(priority=890) 若 restore 该文件 → flush() 提交空变更。
            # 修复：workspace_hygiene 跳过 buffer 中的文件，让 flush() 正常提交。
            buffered_pending: set[str] = set()
            try:
                buffered_pending = gateway._batcher.buffered_files()
            except Exception:  # noqa: BLE001 — 防御性：batcher 不可用时 fail-open
                pass
            if buffered_pending:
                auto_sync_files = [f for f in auto_sync_files if f not in buffered_pending]

            # 3. auto-sync 产物：批量 git restore 还原（GIT-BUDGET-INV-002 合规）

            # batcher.git_restore_batch 单次 `git restore -- <files>` 调用，
            # fail-open 返回成功还原的文件列表（不逐个重试——那是 GIT-BUDGET-INV-002 反模式）

            restored_count = 0

            restore_failed: list[str] = []

            if auto_sync_files:
                restored_set = set(batcher.git_restore_batch(auto_sync_files))

                restored_count = len(restored_set)

                restore_failed = [f for f in auto_sync_files if f not in restored_set]

            # 4. 构造结果

            parts: list[str] = []

            if restored_count > 0:
                parts.append(f"restored {restored_count} auto-sync files")

            if restore_failed:
                parts.append(f"{len(restore_failed)} auto-sync restore failed: {restore_failed[:3]}")

            if real_changes:
                # 真实代码修改：告警（不自动处理）

                # 截断显示前 5 个，避免 detail 过长

                sample = real_changes[:5]

                parts.append(
                    f"{len(real_changes)} non-auto-sync modified files detected: "
                    f"{sample}"
                    f"{'...' if len(real_changes) > 5 else ''}"
                )

            detail = "; ".join(parts) if parts else "no action"

            # 判定 action：

            # - 有真实代码修改 → warn（AI 需关注）

            # - 无真实代码修改但有 restore 失败 → warn（restore 异常需关注）

            # - 仅 auto-sync 产物且全部 restore 成功 → clean（已清理）

            if real_changes or restore_failed:
                return ReconcileResult(
                    action="warn",
                    detail=detail,
                    gate_id=_GATE_ID,
                )

            return ReconcileResult(
                action="clean",
                detail=detail,
                gate_id=_GATE_ID,
            )

        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("workspace_hygiene: reconcile failed: %s", e)

            return ReconcileResult(
                action="warn",
                detail=f"workspace_hygiene reconcile error: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def git_status_porcelain(repo_root) -> list[str]:
    """公共接口：git_status_porcelain（Stage 4 公共化）。"""
    return _git_status_porcelain(repo_root)
