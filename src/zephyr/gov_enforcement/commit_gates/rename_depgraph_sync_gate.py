# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.rename_depgraph_sync_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py 文件重命名（diff-filter=R）的新路径在 depgraph nodes 表无对应 file_path 记录时阻断 commit；只检测 .py 文件重命名（depgraph 主要追踪 .py 模块）；DB 不可达时 fail-open（logger.warning，不阻断业务）；只读查询（read_only=True）；检测 deprecated 节点豁免（build_status='deprecated' 的旧路径不计为"已同步"）
# [MODIFY-GUARD] gate_id="RENAME-DEPGRAPH-SYNC"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——DB/git 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_rename_depgraph_sync_gate.py
# [A_module] module_id=MOD-GOV-rename_depgraph_sync_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未同步阻断门禁（RENAME-DEPGRAPH-SYNC）

检测 staged .py 文件重命名的新路径在 depgraph (PostgreSQL) nodes 表中无对应
``file_path`` 记录——文件改名后未重建 depgraph，导致生成器读 stale depgraph
产出 stale docs（AI-14 审计 a2a_protocol_security.py → a2a_agent_blocklist.py
重命名遗留 13 处 docs 残留引用的根因）。

病根（第一性原理）
-----------------
100% AI 开发项目中，AI 重命名 .py 文件后容易忘记重建 depgraph：
  1. ``git mv old.py new.py`` 改了文件名
  2. AI 直接 commit（或通过 GitCommitGateway commit）
  3. depgraph (PostgreSQL) nodes 表仍记录旧路径 ``old.py``
  4. 下次 generate_path_tree / generate_domain_dependency_diagram / generate_domain_doc
     读 depgraph → 引用不存在的 ``old.py`` → 产出 stale docs
  5. 后续 AI 读 docs 看到 ``old.py`` → import 失败 → 幻觉温床

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. ``git diff --cached --name-status --diff-filter=R`` 获取 staged 重命名 .py 文件
  2. 对每个新路径查询 ``SELECT 1 FROM nodes WHERE file_path = %s AND build_status != 'deprecated'``
  3. 无记录 → 文件重命名后 depgraph 未重建 → 阻断
  4. 提示 AI 先运行 ``python scripts/governance/generate_project_depgraph.py --force``

设计权衡
--------
1. **只检测 .py 文件**：depgraph 主要追踪 .py 模块，.md/.yaml 等不在 file_path 列。
2. **fail-open on DB error**：DB 不可达时不阻断 commit（环境异常非违规）。
   代价是 DB 宕机时漏检——但 DB 宕机时 depgraph 生成器也无法运行，整体一致。
3. **in-process DB 查询**：不走 subprocess（与 DIRECTORY-CONTRACT 的 subprocess 模式不同），
   因为本 gate 只做简单 SELECT 查询，无需复用 checker 脚本逻辑。
4. **priority=39**：在 CH-VERSION-COL(38) 之后、CLAIM-REQUIRED(40) 之前——
   结构性检查（目录/重命名/depgraph 同步）应尽早拦截，在 claim/overlap 之前。
   原占用 36 与 CH-BATCH-SIZE 冲突，治本（ARCH-TTL-DOC-001 循环修复）迁移到空闲编号 39。
5. **deprecated 节点豁免**：``build_status='deprecated'`` 的旧路径不计为"已同步"，
   防止 AI 将旧节点标记 deprecated 后跳过重建。
6. **只检测 staged rename**：``diff-filter=R`` 只捕获 git 检测到的重命名（R50+）。
   纯 delete+add（不相似）不会被检测为 rename，由 CREATE-GUARD/ORPHAN-MODULE 覆盖。

Usage::

    from zephyr.gov_enforcement.commit_gates.rename_depgraph_sync_gate import make_rename_depgraph_sync_gate

    registry.register(make_rename_depgraph_sync_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_rename_depgraph_sync_gate"]

# SQL 集中化（NO-BARE-SQL gate 合规，常量名需匹配 ^_?SQL_\w+$ 豁免正则）
_SQL_CHECK_FILE_PATH = (
    "SELECT 1 FROM nodes WHERE file_path = %s AND build_status != 'deprecated' LIMIT 1"
)


def _get_staged_renamed_py_files(gateway) -> list[tuple[str, str]] | None:
    """获取 staged 重命名 .py 文件列表（old_path, new_path）。

    使用 ``git diff --cached --name-status --diff-filter=R`` 获取重命名记录。
    输出格式: ``R<score>\\t<old_path>\\t<new_path>``

    Args:
        gateway: GitCommitGateway 实例（提供 ``_run_git``）。

    Returns:
        (old_path, new_path) 列表（相对路径，正斜杠归一化）；
        git diff 失败/异常时返回 None（fail-open 检测器失效）。
    """
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=R"]
        )
        if diff_result.returncode != 0:
            logger.warning(
                "RENAME-DEPGRAPH-SYNC gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        renames: list[tuple[str, str]] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            # 格式: R<score>\t<old_path>\t<new_path>
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            old_path = parts[1].replace("\\", "/").strip()
            new_path = parts[2].replace("\\", "/").strip()
            # 只检测 .py 文件（depgraph 主要追踪 .py 模块）
            if not new_path.endswith(".py"):
                continue
            # tests/ 豁免（与 ORPHAN-MODULE 一致：tests/ 文件不强制 depgraph 同步）
            if is_test_exempt(new_path):
                continue
            renames.append((old_path, new_path))
        return renames
    except Exception as e:
        logger.warning(
            "RENAME-DEPGRAPH-SYNC gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__, e, exc_info=True,
        )
        return None


def _check_depgraph_has_file(file_path: str) -> bool | None:
    """查询 depgraph nodes 表是否已记录指定 file_path。

    Args:
        file_path: 相对路径（正斜杠，如 ``src/zephyr/.../module.py``）。

    Returns:
        True=depgraph 已记录该文件；False=未记录（违规）；
        None=DB 查询失败（fail-open，不阻断）。
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(
                _SQL_CHECK_FILE_PATH,
                (file_path,),
            )
            return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception as e:
        logger.warning(
            "RENAME-DEPGRAPH-SYNC gate fail-open: depgraph 查询失败(%s: %s)，"
            "无法验证文件重命名同步状态。",
            type(e).__name__, e, exc_info=True,
        )
        return None


def _format_violation_detail(missing: list[tuple[str, str]]) -> str:
    """格式化违规详情字符串（限制显示数量）。"""
    shown = missing[:5]
    pairs = "; ".join(f"{o} -> {n}" for o, n in shown)
    suffix = f" (还有 {len(missing) - 5} 个)" if len(missing) > 5 else ""
    return f"{pairs}{suffix}"


def make_rename_depgraph_sync_gate() -> GateSpec:
    """构造文件重命名 depgraph 同步阻断门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="RENAME-DEPGRAPH-SYNC", priority=39)。
        priority=39——在 CH-VERSION-COL(38) 之后、CLAIM-REQUIRED(40) 之前
        （结构性检查应尽早拦截；原 36 与 CH-BATCH-SIZE 冲突，迁移到空闲 39）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 获取 staged 重命名 .py 文件（None 表示 fail-open 检测器失效）
        renames = _get_staged_renamed_py_files(gateway)
        if not renames:
            return True, ""

        # 2. 逐个查询 depgraph 是否已记录新路径
        missing: list[tuple[str, str]] = []
        for old_path, new_path in renames:
            result = _check_depgraph_has_file(new_path)
            if result is None:
                # DB 查询失败 → fail-open（不阻断此文件）
                continue
            if not result:
                missing.append((old_path, new_path))

        # 3. 有未同步的重命名 → 阻断
        if missing:
            detail = _format_violation_detail(missing)
            return False, (
                f"RENAME-DEPGRAPH-SYNC: {len(missing)} 个 .py 文件重命名后 depgraph 未同步。"
                f"先运行 'python scripts/governance/generate_project_depgraph.py --force' "
                f"重建 depgraph，再提交。详情: {detail}"
            )
        return True, ""

    return GateSpec(gate_id="RENAME-DEPGRAPH-SYNC", check=_check, priority=39)