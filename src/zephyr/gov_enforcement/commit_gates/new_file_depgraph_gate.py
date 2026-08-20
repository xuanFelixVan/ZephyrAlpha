# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.audit.pg_probe (log_db_failopen/pg_probe_shows_offline，#ARCH-119 延迟 import)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged 新增 .py 文件在 src/zephyr/ 或 scripts/ 下（排除 tests/）且 depgraph nodes 表完全无记录（generated/planned/stable 任一状态）时阻断 commit；只检测 .py 文件（depgraph 主要追踪 .py 模块）；DB 不可达时 fail-open（环境异常非违规，对标 rename_depgraph_sync_gate 设计）；只读查询（read_only=True）；bootstrap 豁免——gate 只检测本次 commit 新增的文件，现有 3811 个 generated 节点不受影响（gate 触发时 commit 已含新文件，depgraph 自然无历史记录）；tests/ 豁免（测试不是模块依赖链节点，真源：commit_gate_registry.is_test_exempt）
# [MODIFY-GUARD] gate_id="NEW-FILE-DEPGRAPH-ENFORCEMENT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——DB/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_new_file_depgraph_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""new_file_depgraph_gate.py — 新建 .py 文件 depgraph 未登记硬阻断门禁（NEW-FILE-DEPGRAPH-ENFORCEMENT）

检测 staged 新增 .py 文件（src/zephyr/ + scripts/ 下，tests/ 豁免）在 depgraph
(PostgreSQL) nodes 表中完全无记录（build_status 为 generated/planned/stable 任一
即视为"已登记"，完全无记录才阻断）——L1 铁律（依赖关系先行）从君子协定升级为
技术强制（#ARCH-DEP-001 第三期）。

病根（第一性原理）
-----------------
100% AI 开发项目中，L1 铁律要求"施工前 MUST 通过 apply_depgraph.py --add-design-node
登记设计态（build_status=planned）"，但实际为君子协定——整个项目 3811 个 generated
节点 vs 41 个 planned 节点（占比 1.05%），AI 普遍先写代码后由 generate_project_depgraph.py
自动扫描登记为 generated。L1 铁律意图是"depgraph 有依赖信息可供 AI 查询=零幻觉空间
可达"，generated 已满足此意图——但"代码已存在但 depgraph 完全无记录"是真正的 drift
（依赖关系未登记），靠 post-merge reconciler 兜底=发现滞后。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. ``git diff --cached --name-only --diff-filter=A`` 获取 staged 新增 .py 文件
  2. 过滤范围：src/zephyr/ 或 scripts/ 下，tests/ 豁免（对标 rename_depgraph_sync_gate）
  3. 对每个新 .py 查询 ``SELECT 1 FROM nodes WHERE file_path = %s LIMIT 1``
     （放行 generated/planned/stable/deprecated 任一状态——depgraph 有记录即满足 L1 意图）
  4. 完全无记录 → 阻断，提示 AI 先运行 ``apply_depgraph.py --add-design-node``
     或 ``python scripts/governance/generate_project_depgraph.py``

设计权衡
--------
1. **硬阻断而非 warn-only**：L1 铁律原文是"MUST 登记"（强制），warn-only 无效
   （AI 会忽略 warn，3811 差距继续扩大）。硬阻断才能强制 AI 施工前登记。
2. **bootstrap 豁免（不追溯）**：gate 只检测本次 commit 新增的文件，现有 3811 个
   generated 节点不受影响（gate 触发时 commit 已含新文件，depgraph 自然无历史记录）。
   不批量转 planned——保持 generated 是诚实状态（planned 表示"计划要做但还没做"，
   但代码已经存在了，撒谎转 planned 反而失真）。
3. **fail-open on DB error**：DB 不可达时不阻断 commit（环境异常非违规，对标
   rename_depgraph_sync_gate 设计）。代价是 DB 宕机时漏检——但 DB 宕机时 depgraph
   生成器也无法运行，整体一致。
4. **in-process DB 查询**：不走 subprocess（对标 rename_depgraph_sync_gate 模式）。
5. **priority=58**：在 HELD-OVERLAP(50) 之后、CREATE-GUARD(60) 之前——结构性检查
   （depgraph 同步状态）应尽早拦截，在文件登记类检查（creation_token/字段头部）
   之前。
6. **与 RENAME-DEPGRAPH-SYNC(39) 互补**：rename gate 检测重命名后新路径未登记（管 R），
   本 gate 检测新建 .py 文件未登记（管 A），覆盖完整。
7. **放行 deprecated 状态**：deprecated 表示"已废弃但历史存在"，仍属 depgraph 已登记。
   若废弃文件被重新加入 commit，由 ORPHAN-MODULE 等其他 gate 检测，本 gate 不重复。

L1 铁律分层裁定（#ARCH-L1-RULE-ENFORCEMENT-GAP，2026-08-04 二元化）：
  L1 铁律文本（trae_080）要求"施工前 MUST 登记 planned"，但 99% 节点为 generated
  （先施工后登记），灰度规则已形同虚设。裁定拆为两层——
  - **铁律（gate-enforced，本 gate）**：commit 前在 depgraph 有记录（any status）。
    二元判定：registered before commit = yes/no。gate 硬阻断 unregistered。
  - **建议（best practice，非铁律）**：施工前先登记 planned 设计态，供 AI 查询依赖。
    非技术强制，文档引导。不适用"规则二元化元规则"（非铁律）。
  理由：100% AI 项目中，当前 AI session 有对话上下文（不严格依赖 depgraph 查询），
  未来 AI session 依赖 depgraph（satisfied by "generated before commit"）。
  "planned before code"的增量价值可通过 capability lookup / rule discovery 补偿。

bootstrap 证据（depgraph DB 查询，2026-07-21）：
  - 整个项目：planned=41, generated=3811, stable=1584, deprecated=2
  - d8_doc_sync 目录：planned=0, generated=12, stable=0
  - scripts/ 下 reconciler：planned=0, generated=3, stable=1
  说明：现有节点已自动登记为 generated，gate 放行 generated/planned/stable/deprecated
  任一状态，不影响现有节点。新 gate 只阻断"完全无记录"的新文件。

Usage::

    from zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate import make_new_file_depgraph_gate

    registry.register(make_new_file_depgraph_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_new_file_depgraph_gate"]

# SQL 集中化（NO-BARE-SQL gate 合规，常量名需匹配 ^_?SQL_\w+$ 豁免正则）
_SQL_CHECK_FILE_PATH = "SELECT 1 FROM nodes WHERE file_path = %s LIMIT 1"

# 范围限定：src/zephyr/ + scripts/ 下（tests/ 由 is_test_exempt 豁免）
# 排除 tests/ 的原因：测试不是模块依赖链节点，depgraph 不强制登记
_SRC_ZEPHYR_PREFIX = "src/zephyr/"
_SCRIPTS_PREFIX = "scripts/"


def _is_in_scope(file_path: str) -> bool:
    """判断文件路径是否在 gate 检测范围内（src/zephyr/ 或 scripts/ 下，tests/ 豁免）。

    Args:
        file_path: 相对路径（正斜杠归一化）。

    Returns:
        True=在范围内（需检测）；False=不在范围内（跳过）。
    """
    # tests/ 豁免（真源：commit_gate_registry.is_test_exempt）
    if is_test_exempt(file_path):
        return False
    # 范围限定：src/zephyr/ 或 scripts/ 下
    return file_path.startswith(_SRC_ZEPHYR_PREFIX) or file_path.startswith(_SCRIPTS_PREFIX)


def _get_staged_new_py_files(gateway) -> list[str] | None:
    """获取 staged 新增 .py 文件列表（--diff-filter=A）。

    使用 ``git diff --cached --name-only --diff-filter=A`` 获取新增文件。
    过滤范围：src/zephyr/ 或 scripts/ 下，tests/ 豁免。

    Args:
        gateway: GitCommitGateway 实例（提供 ``_run_git``）。

    Returns:
        相对路径列表（正斜杠归一化）；
        git diff 失败/异常时返回 None（fail-open 检测器失效）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning(
                "NEW-FILE-DEPGRAPH-ENFORCEMENT gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        new_files: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            file_path = line.strip().replace("\\", "/")
            # 只检测 .py 文件（depgraph 主要追踪 .py 模块）
            if not file_path.endswith(".py"):
                continue
            # 范围限定 + tests/ 豁免
            if not _is_in_scope(file_path):
                continue
            new_files.append(file_path)
        return new_files
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NEW-FILE-DEPGRAPH-ENFORCEMENT gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _check_depgraph_has_file(file_path: str) -> bool | None:
    """查询 depgraph nodes 表是否已记录指定 file_path。

    Args:
        file_path: 相对路径（正斜杠，如 ``src/zephyr/.../module.py``）。

    Returns:
        True=depgraph 已记录该文件（generated/planned/stable/deprecated 任一状态）；
        False=未记录（违规）；None=DB 查询失败（fail-open，不阻断）。
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(_SQL_CHECK_FILE_PATH, (file_path,))
            return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NEW-FILE-DEPGRAPH-ENFORCEMENT gate fail-open: depgraph 查询失败(%s: %s)，无法验证新文件登记状态。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _format_violation_detail(missing: list[str]) -> str:
    """格式化违规详情字符串（限制显示数量）。"""
    shown = missing[:5]
    suffix = f" (还有 {len(missing) - 5} 个)" if len(missing) > 5 else ""
    return f"{', '.join(shown)}{suffix}"


def make_new_file_depgraph_gate() -> GateSpec:
    """构造新建 .py 文件 depgraph 未登记硬阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NEW-FILE-DEPGRAPH-ENFORCEMENT", priority=58)。
        priority=58——在 HELD-OVERLAP(50) 之后、CREATE-GUARD(60) 之前
        （结构性检查应尽早拦截，在文件登记类检查之前）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 非 Zephyr 项目（tmp_path 测试仓库等）skip
        # 对标 CREATE-GUARD 的 non-Zephyr project skip 设计
        _governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return (
                True,
                "non-Zephyr project (no scripts/governance/d1_structure), skipping NEW-FILE-DEPGRAPH-ENFORCEMENT",
            )

        # 2. 获取 staged 新增 .py 文件（None 表示 fail-open 检测器失效）
        new_py_files = _get_staged_new_py_files(gateway)
        if not new_py_files:
            return True, ""

        # 3. 治本 2026-06-30（对标 CREATE-GUARD）：只检测 commit 文件中的新增 .py
        # （gateway 选择性提交时，staged 区可能含未在 commit files 中的文件）
        commit_files_rel: set[str] = set()
        for f in files:
            try:
                rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
                commit_files_rel.add(rel)
            except (ValueError, OSError):
                continue
        new_py_files = [f for f in new_py_files if f in commit_files_rel]
        if not new_py_files:
            return True, ""

        # 4. 逐个查询 depgraph 是否已记录
        missing: list[str] = []
        degraded: list[str] = []  # DB 查询失败被降级放行的新文件（#116 B1 留痕）
        for file_path in new_py_files:
            result = _check_depgraph_has_file(file_path)
            if result is None:
                # DB 查询失败 → fail-open（不阻断此文件）
                degraded.append(file_path)
                continue
            if not result:
                missing.append(file_path)

        # 4b. tracker #116 B1（#ARCH-119）：fail-open 放行统一接 log_gate_failure
        # 持久化（critical_warn，下次 commit 网关 banner 浮现）；探针状态区分
        # 「DB 离线降级」（当日同签名去重）vs「真实错误」（逐次留痕不静默）。
        # 放行语义不变——只加留痕。
        if degraded:
            from zephyr.governance.audit.pg_probe import (  # noqa: PLC0415 延迟 import 防循环
                log_db_failopen,
                pg_probe_shows_offline,
            )

            _offline = pg_probe_shows_offline(gateway.project_root)
            log_db_failopen(
                gateway.project_root,
                "NEW-FILE-DEPGRAPH-ENFORCEMENT",
                db_offline=_offline,
                reason=(
                    "depgraph 查询失败，新文件登记状态无法验证，降级放行"
                    + ("（探针证实 PG 离线）" if _offline else "（探针未证实离线——真实连接错误）")
                ),
                affected_files=degraded,
                session_id=kwargs.get("session_id", ""),
            )

        # 5. 有未登记的新文件 → 阻断
        if missing:
            detail = _format_violation_detail(missing)
            return False, (
                f"NEW-FILE-DEPGRAPH-ENFORCEMENT: {len(missing)} 个新建 .py 文件"
                f"在 depgraph (PostgreSQL) nodes 表无记录。L1 铁律（依赖关系先行）"
                f"从君子协定升级为技术强制（#ARCH-DEP-001 第三期）。"
                f"修复（二选一）："
                f"① 先登记设计态再施工——python scripts/governance/apply_depgraph.py "
                f"--add-design-node <file_path> <module_id> <domain_id> --granularity file；"
                f"② 施工完毕直接全量重扫登记运营态——python scripts/governance/"
                f"generate_project_depgraph.py --output-db depgraph --force"
                f"（#ARCH-70 起：同 path design 预登记节点由重扫自动同身份 UPDATE 转 production，"
                f"无需手工 transition）。"
                f"详情: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="NEW-FILE-DEPGRAPH-ENFORCEMENT", check=_check, priority=58)
