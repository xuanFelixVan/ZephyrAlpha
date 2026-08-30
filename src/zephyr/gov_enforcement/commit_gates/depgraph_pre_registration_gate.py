# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.audit.pg_probe (log_db_failopen/pg_probe_shows_offline，#ARCH-119 延迟 import)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged src/zephyr/**/*.py 文件含 [TTL]=permanent 且 depgraph build_status=planned 且文件实质行数 > _IMPL_THRESHOLD(50) 时阻断 commit（planned 表示"计划但未做"，但代码已 >50 行，应转 production）；tests/ 豁免；DB 不可达 fail-open；git diff 不可达 fail-open；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="DEPGRAPH-PRE-REGISTRATION"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——DB/git/文件读取异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_depgraph_pre_registration_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH] ARCH-DEP-PREMERGE-ENFORCE
"""
depgraph_pre_registration_gate.py — depgraph planned→production 流转强制门禁（DEPGRAPH-PRE-REGISTRATION）

落地 #ARCH-DEP-PREMERGE-ENFORCE：L1 铁律"施工完成转 production"从君子协定升级为
技术强制。补强 NEW-FILE-DEPGRAPH-ENFORCEMENT（priority=58）的盲区——
NEW-FILE-DEPGRAPH-ENFORCEMENT 只检测"新建文件完全无记录"，本 gate 检测
"已登记为 planned 但文件已有实质实现（应转 production）"。

病根（第一性原理）
-----------------
L1 铁律要求"施工前 MUST 通过 apply_depgraph.py --add-design-node 登记设计态
（build_status=planned），施工完成转 production"。但实际：
  - NEW-FILE-DEPGRAPH-ENFORCEMENT 只管"新建文件无记录"
  - planned→production 流转无强制（AI 登记后忘记转 production）
  - 结果：depgraph 充斥 planned 节点但代码已施工——状态失真

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged src/zephyr/**/*.py 文件（新增 + 修改）
  2. 过滤 tests/ 豁免
  3. 提取 [TTL] 头部，若 = permanent
  4. 查 depgraph build_status
  5. 若 build_status=planned 且文件实质行数 > _IMPL_THRESHOLD (50) → 硬阻断
     （planned 表示"计划但未做"，但代码已 >50 行，应转 production）

设计权衡
--------
1. **聚焦 planned→production 流转**：NEW-FILE-DEPGRAPH-ENFORCEMENT 管"无记录"，
   本 gate 管"有记录但状态滞后"——互补不重复。
2. **实质行数阈值 50**：区分"骨架/桩代码"（<50 行，planned 合理）vs
   "已施工"（>50 行，应转 production）。50 行覆盖典型模块级实现。
3. **只检测 [TTL]=permanent**：临时文件（task_bound）不强制 depgraph 流转。
4. **fail-open on DB error**：DB 不可达时不阻断（环境异常非违规，对标
   NEW-FILE-DEPGRAPH-ENFORCEMENT 设计）。
5. **priority=113**：在 FOLDER-CAPACITY-HARD-LIMIT(112) 之后。
6. **in-process DB 查询**：复用 NEW-FILE-DEPGRAPH-ENFORCEMENT 的
   get_depgraph_pg_connection 模式（只读，read_only=True）。

Usage::

    from zephyr.gov_enforcement.commit_gates.depgraph_pre_registration_gate import (
        make_depgraph_pre_registration_gate,
    )

    registry.register(make_depgraph_pre_registration_gate())

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: file_path 参数
#   fields: 参数 file_path（无注解）
#   code: depgraph_pre_registration_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① make_depgraph_pre_registration_gate
#   name_en: make_depgraph_pre_registration_gate
#   intro: 构造 depgraph planned→production 流转强制 GateSpec（硬阻断型）。
#   desc: 构造 depgraph planned→production 流转强制 GateSpec（硬阻断型）。 Returns: GateSpec(gate_id="DEPGRAPH-P…；源码 L343-L369
#   inputs: 无参数
#   outputs: GateSpec
# - id: A2
#   name_zh: ② query_build_status
#   name_en: query_build_status
#   intro: 公共接口：query_build_status（Stage 4 公共化）。
#   desc: 公共接口：query_build_status（Stage 4 公共化）。；源码 L373-L375
#   inputs: file_path
#   outputs: str | None
# - id: A3
#   name_zh: ③ extract_ttl
#   name_en: extract_ttl
#   intro: 公共接口：extract_ttl（Stage 4 公共化）。
#   desc: 公共接口：extract_ttl（Stage 4 公共化）。；源码 L379-L381
#   inputs: file_path
#   outputs: str | None
# - id: A4
#   name_zh: ④ count_impl_lines
#   name_en: count_impl_lines
#   intro: 公共接口：count_impl_lines（Stage 4 公共化）。
#   desc: 公共接口：count_impl_lines（Stage 4 公共化）。；源码 L385-L387
#   inputs: file_path
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# - id: O2
#   name_zh: str | None
#   name_en: str | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
import os
import re
import traceback

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    GateSpec,
    is_test_exempt,
)

logger = logging.getLogger(__name__)

__all__ = ["make_depgraph_pre_registration_gate"]

# SQL 集中化（NO-BARE-SQL gate 合规，常量名需匹配 ^_?SQL_\w+$ 豁免正则）
_SQL_GET_BUILD_STATUS = "SELECT build_status FROM nodes WHERE file_path = %s LIMIT 1"

# 范围限定：src/zephyr/ 下（tests/ 由 is_test_exempt 豁免）
_SRC_ZEPHYR_PREFIX = "src/zephyr/"

# 实质实现行数阈值——超过此值视为"已施工"（应转 production）
_IMPL_THRESHOLD = 50

# TTL 提取正则——支持注释锚定格式 # [TTL] permanent
_TTL_COMMENT_RE = re.compile(r"^#\s*\[TTL\]\s*(\w+)", re.MULTILINE)


def _extract_ttl(file_path: str) -> str | None:
    """从文件头部提取 [TTL] 字段值（注释锚定格式）。

    Args:
        file_path: 文件绝对路径。

    Returns:
        ttl 值（permanent/task_bound）或 None（无声明/读取失败）。
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            head = "".join(next(f, "") for _ in range(30))
    except (OSError, UnicodeDecodeError):
        return None
    m = _TTL_COMMENT_RE.search(head)
    return m.group(1).strip() if m else None


def _count_impl_lines(file_path: str) -> int:
    """统计文件实质实现行数（非空、非纯注释）。

    Args:
        file_path: 文件绝对路径。

    Returns:
        实现行数；读取失败返回 0（fail-open）。
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            count = 0
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue  # 空行
                if stripped.startswith("#"):
                    continue  # 注释行
                count += 1
        return count
    except (OSError, UnicodeDecodeError):
        return 0


def _get_staged_py_files(gateway) -> list[str] | None:
    """获取 staged 新增/修改 .py 文件列表（src/zephyr/ 下，tests/ 豁免）。

    Returns:
        相对路径列表；git diff 失败/异常返回 None（fail-open）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "DEPGRAPH-PRE-REGISTRATION gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        result: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            fp = line.strip().replace("\\", "/")
            if not fp.endswith(".py"):
                continue
            if not fp.startswith(_SRC_ZEPHYR_PREFIX):
                continue
            if is_test_exempt(fp):
                continue
            result.append(fp)
        return result
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "DEPGRAPH-PRE-REGISTRATION gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _query_build_status(file_path: str) -> str | None:
    """查询 depgraph nodes 表中指定 file_path 的 build_status。

    Returns:
        build_status 字符串（planned/generated/stable/deprecated）；
        None=DB 查询失败或无记录（fail-open）。
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(_SQL_GET_BUILD_STATUS, (file_path,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — fail-open 不阻断
        logger.warning(
            "DEPGRAPH-PRE-REGISTRATION gate fail-open: depgraph 查询失败(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _log_none_status_failopen(gateway, skipped: list[str], session_id: str = "") -> None:
    """tracker #116 B1（#ARCH-119）：build_status 查询返回 None 的 permanent 文件降级留痕。

    None 语义二义（「depgraph 无记录」正常 vs 「DB 查询失败」降级）：
    - 探针证实 PG 离线 → 全部按 DB 离线降级留痕（当日同签名去重）；
    - 探针在线/未知 → 单发连接测试区分：连接失败=真实错误留痕（不静默）；
      连接成功=None 为「无记录」正常语义（NEW-FILE-DEPGRAPH-ENFORCEMENT 已管
      新建无记录），不留痕。
    """
    from zephyr.governance.audit.pg_probe import (  # noqa: PLC0415 延迟 import 防循环
        log_db_failopen,
        pg_probe_shows_offline,
    )

    project_root = gateway.project_root
    if pg_probe_shows_offline(project_root):
        log_db_failopen(
            project_root,
            "DEPGRAPH-PRE-REGISTRATION",
            db_offline=True,
            reason="探针证实 PG 离线，build_status 查询失败，planned→production 流转检测降级跳过",
            affected_files=skipped,
            session_id=session_id,
        )
        return
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        conn.close()
    except Exception as e:  # noqa: BLE001 — 连接失败=真实错误留痕
        log_db_failopen(
            project_root,
            "DEPGRAPH-PRE-REGISTRATION",
            db_offline=False,
            reason=(
                f"探针未证实离线但 depgraph 连接失败({type(e).__name__}: {e})，build_status 查询降级跳过——真实错误"
            ),
            affected_files=skipped,
            session_id=session_id,
            stack_trace=traceback.format_exc(),
        )


def _scan_violations(gateway, py_files: list[str], session_id: str = "") -> list[str]:
    """扫描 planned 状态但已施工的违规。

    返回违规消息列表。
    """
    project_root = gateway.project_root
    violations: list[str] = []
    skipped_none: list[str] = []  # build_status 查询为 None 的 permanent 文件（#116 B1 留痕候选）

    for rel in py_files:
        abs_path = os.path.join(str(project_root), rel)
        # 治本（2026-08-01）：用 public alias（extract_ttl/query_build_status/
        # count_impl_lines）而非私有引用（_extract_ttl 等），使 monkeypatch 能
        # 拦截——public alias 设计初衷即为测试可注入（Stage 4 公共化）。原代码用
        # 私有引用绕过了 alias，导致测试无法 mock（与 reconciler_health_gate 同病根）。
        ttl = extract_ttl(abs_path)
        if ttl != "permanent":
            continue  # 只检测永久模块

        status = query_build_status(rel)
        if status is None:
            skipped_none.append(rel)  # None 二义：无记录（正常）或 DB 失败（降级）
            continue
        if status != "planned":
            continue  # 非 planned 不检测（generated/stable/deprecated 放行）

        impl_lines = count_impl_lines(abs_path)
        if impl_lines <= _IMPL_THRESHOLD:
            continue  # 骨架/桩代码，planned 合理

        violations.append(
            f"  {rel}: depgraph build_status=planned 但实质实现 {impl_lines} 行"
            f" > {_IMPL_THRESHOLD}（planned 表示'计划但未做'，代码已施工应转 production）"
        )

    # tracker #116 B1：DB 降级跳过的 permanent 文件留痕（仅当真为 DB 失败时）
    if skipped_none:
        _log_none_status_failopen(gateway, skipped_none, session_id=session_id)

    return violations


def make_depgraph_pre_registration_gate() -> GateSpec:
    """构造 depgraph planned→production 流转强制 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="DEPGRAPH-PRE-REGISTRATION", priority=113)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        py_files = _get_staged_py_files(gateway)
        if not py_files:
            return True, ""

        violations = _scan_violations(gateway, py_files, session_id=kwargs.get("session_id", ""))

        if violations:
            detail = (
                "DEPGRAPH-PRE-REGISTRATION：检测到 depgraph 状态滞后，\n"
                "  违反 L1 铁律'施工完成转 production'（#ARCH-DEP-PREMERGE-ENFORCE）。\n"
                + "\n".join(violations)
                + "\n-> 运行 apply_depgraph.py --transition-build-status <node_id> production"
            )
            logger.error("DEPGRAPH-PRE-REGISTRATION gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="DEPGRAPH-PRE-REGISTRATION", check=_check, priority=113)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def query_build_status(file_path) -> str | None:
    """公共接口：query_build_status（Stage 4 公共化）。"""
    return _query_build_status(file_path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def extract_ttl(file_path) -> str | None:
    """公共接口：extract_ttl（Stage 4 公共化）。"""
    return _extract_ttl(file_path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def count_impl_lines(file_path) -> int:
    """公共接口：count_impl_lines（Stage 4 公共化）。"""
    return _count_impl_lines(file_path)
