# [BLUEPRINT] MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §P1-b 跨层契约签名漂移检测

# [MODULE] zephyr.governance.audit.cross_layer_contract_signature_reconciler

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec, SQL_CREATE_DRIFT_AUDIT_FINDINGS, SQL_INSERT_DRIFT_AUDIT_FINDING); zephyr.governance.audit._git_helpers (git_show_file); stdlib (ast, logging, os, sqlite3, uuid, yaml)

# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] post-commit 事件触发（仅当 staged .py 文件命中 cross_layer_contracts.yaml 中任一 physical_path，或 YAML 自身被修改时触发）；reconciler 永不抛异常（异常降级为 warn）；只读 git show HEAD~1:path 获取旧版本（不修改工作区）；签名漂移持久化到 governance.db drift_audit_findings 表（severity=HIGH）；AST 解析失败降级为 warn（不阻断）

# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _CONTRACTS_YAML_REL

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] reconcile 永不抛异常——git/AST/DB 异常降级为 ReconcileResult(action="warn")

# [TESTS] tests/governance/audit/test_cross_layer_contract_signature_reconciler.py

# [A_module] module_id=MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable  # noqa: blueprint-amodule-cross-check [BLUEPRINT]==[A_module] same module

# [TTL] permanent

# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)

"""

cross_layer_contract_signature_reconciler.py — 跨层契约签名漂移检测 reconciler（P1-b，2026-07-21）。



post-commit 事件触发，当 staged .py 文件命中 ``cross_layer_contracts.yaml`` 中任一

``physical_path``（即跨层契约 codegen 目标文件被修改），或 YAML 自身被修改时，AST 提取

旧版本（HEAD~1）与新版本的 ``@dataclass`` 类签名（类名+字段名+字段类型），比对差异，

若签名变化（字段增删/类型改/类名改）则 warn 并持久化到 ``governance.db`` 的

``drift_audit_findings`` 表（severity=HIGH）。



治本动机（第一性原理）

--------------------

12 维度审计 P1-b 维度："跨层契约签名漂移检测"——原属 uncovered-but-gatable。

SSoT 是 ``cross_layer_contracts.yaml``，codegen 生成 ``src/zephyr/shared/contracts/*.py``。

契约文件被手工修改（绕过 codegen）是核心漂移源——AI 可能直接编辑 codegen 产物而非改 YAML。

post-commit reconciler 检测此类漂移，warn + 持久化，AI 可查 ``drift_audit_findings`` 表

发现历史漂移。



设计权衡

--------

1. **post-commit warn-only（非 block）**：签名变化可能是合法 codegen 重生成（YAML 改了

   再 codegen），reconciler 无法区分"手工改 codegen 产物"vs"合法 codegen"。warn+持久化

   让 AI 后续可查，不阻断合法 codegen 流程。

2. **AST 提取 @dataclass 签名**：跨层契约均为 ``@dataclass(frozen=True)`` 类

   （cross_layer_contracts.yaml codegen 约定）。提取类名+字段名+字段类型注解。

3. **git show HEAD~1:path 获取旧版本**：post-commit 时 HEAD 已是新 commit，HEAD~1 是

   旧版本。新增文件（无 HEAD~1）不检测（首次创建无漂移可言）。

4. **fail-open**：git/AST/DB 任一异常降级为 warn（不阻断，不丢日志）。

5. **priority=215**：早于 drift_scan(140) 已过，晚于 blueprint_frontmatter(135)，

   在 depgraph_ops(130) → blueprint_frontmatter(135) → drift_scan(140) 之后，

   独立检测契约签名漂移（与 drift_scan 互补：drift_scan 检测蓝图↔代码↔depgraph 三方

   对齐，本 reconciler 检测契约 codegen 产物签名稳定性）。



Usage

-----

::



    from zephyr.governance.audit.cross_layer_contract_signature_reconciler import (

        make_cross_layer_contract_signature_reconciler,

    )



    registry.register(make_cross_layer_contract_signature_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 跨层契约真源 YAML
#   fields: contracts[].physical_path 集合
#   code: _CONTRACTS_YAML_REL L169（architecture_model/contracts/cross_layer_contracts.yaml）
# - id: I2
#   name: post-commit 提交文件列表 committed_files
#   fields: 本次 commit 的 staged 文件路径列表
#   code: _reconcile(committed_files) L647
# - id: I3
#   name: 契约文件新旧源码
#   fields: 工作区新版全文 + git show HEAD~1 旧版全文
#   code: open(new_abs) L601 / git_show_file L615
# 层: 算法
# - id: A1
#   name_zh: ① 契约路径集合加载
#   name_en: _load_contract_physical_paths
#   intro: 从契约 YAML 读出所有 codegen 产物的物理路径集合
#   desc: yaml.safe_load 提取 contracts[].physical_path 归一化为 POSIX 风格；缺失/解析失败返回空集 fail-open
#   inputs: I1
#   outputs: physical_path 集合
# - id: A2
#   name_zh: ② 触发与变更收集
#   name_en: _trigger + _collect_changed_contracts
#   intro: YAML 自身被改就全量重检，否则只检命中路径的 .py 文件
#   desc: committed 命中 YAML → 检测全部 physical_path；命中单个契约 .py → 单文件检测
#   inputs: A1 I2
#   outputs: changed_contracts 文件列表
# - id: A3
#   name_zh: ③ dataclass 签名 AST 提取
#   name_en: _extract_dataclass_signatures
#   intro: AST 找出所有 @dataclass 类并提取字段名与类型注解
#   desc: 识别 @dataclass 与 @dataclass(frozen=True)；AnnAssign 字段 unparse 注解；SyntaxError 返回空 dict
#   inputs: A2 I3
#   outputs: {类名: [(字段名, 类型注解)]} 新旧两份签名
# - id: A4
#   name_zh: ④ 签名差异比对
#   name_en: _diff_signatures
#   intro: 比对新旧签名，类删除/字段删除/类型变更算漂移
#   desc: 删除类、删除字段、字段类型变化 → 差异；新增类/新增字段属兼容变更不报
#   inputs: A3
#   outputs: 差异描述列表
# - id: A5
#   name_zh: ⑤ 漂移持久化与编排
#   name_en: _persist_drift_finding + _reconcile
#   intro: 命中漂移写库并汇总 warn，全程异常降级不抛出
#   desc: finding_id=cs-+uuid12，类型 CONTRACT_SIGNATURE_DRIFT severity=HIGH；detail 截断前 5 项；无路径→skip，无变更→clean
#   inputs: A4
#   outputs: ReconcileResult(warn/clean/skip) + drift_audit_findings 记录
#   invariant: reconciler 永不抛异常；post-commit warn-only
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: warn=契约签名漂移（gate_id=GATE-CROSS-LAYER-CONTRACT-SIGNATURE），clean/skip=无漂移
#   downstream: GitCommitGateway MOD-INF-035
# - id: O2
#   name_zh: 签名漂移数据库记录
#   name_en: drift_audit_findings 记录
#   intro: 契约签名漂移历史落库，供 AI 事后追溯手工改 codegen 产物事件
#   downstream: governance.db drift_audit_findings 表（AI 查询）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> A3
# I3 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
# A5 --> O2
"""



from __future__ import annotations

import ast
import logging
import os
import sqlite3
import uuid
from pathlib import Path

from zephyr.governance.audit._git_helpers import git_show_file
from zephyr.governance.audit.reconciliation_registry import (
    SQL_CREATE_DRIFT_AUDIT_FINDINGS,
    SQL_INSERT_DRIFT_AUDIT_FINDING,
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)



_GATE_ID = "GATE-CROSS-LAYER-CONTRACT-SIGNATURE"

# priority=215: 独立检测契约签名漂移，在 drift_scan(140) 之后

_PRIORITY = 215



# 跨层契约 YAML 真源路径（SSoT，AGENTS.md §11.0.2 规则数据真源）

_CONTRACTS_YAML_REL = "architecture_model/contracts/cross_layer_contracts.yaml"





def _load_contract_physical_paths(yaml_abs: str) -> set[str]:

    """从 cross_layer_contracts.yaml 加载所有 physical_path 集合。



    fail-open：YAML 解析失败返回空集（无法检测，降级 skip）。



    Args:

        yaml_abs: YAML 文件绝对路径。



    Returns:

        physical_path 集合（POSIX 风格相对路径）；YAML 不存在/解析失败返回空集。

    """

    try:

        import yaml

    except ImportError:

        logger.warning("cross_layer_contract_signature: PyYAML not installed, skip")

        return set()

    if not os.path.isfile(yaml_abs):

        return set()

    try:

        with open(yaml_abs, "r", encoding="utf-8") as f:

            data = yaml.safe_load(f)

        if not isinstance(data, dict):

            return set()

        contracts = data.get("contracts", [])

        paths: set[str] = set()

        for c in contracts:

            if isinstance(c, dict):

                p = c.get("physical_path")

                if isinstance(p, str) and p:

                    paths.add(p.replace("\\", "/"))

        return paths

    except Exception as e:  # noqa: BLE001 — fail-open 不阻断

        logger.warning("cross_layer_contract_signature: YAML load failed: %s", e)

        return set()





def _extract_dataclass_signatures(source: str) -> dict[str, list[tuple[str, str]]]:

    """AST 提取源码中所有 @dataclass 类的签名（类名 → [(字段名, 类型注解字符串), ...]）。



    Args:

        source: Python 源码字符串。



    Returns:

        dict[类名, [(字段名, 类型注解), ...]]；AST 解析失败返回空 dict。

    """

    try:

        tree = ast.parse(source)

    except SyntaxError:

        return {}

    sigs: dict[str, list[tuple[str, str]]] = {}

    for node in ast.walk(tree):

        if not isinstance(node, ast.ClassDef):

            continue

        # 检测 @dataclass 装饰器（含 @dataclass(frozen=True) 等带参形式）

        is_dataclass = False

        for dec in node.decorator_list:

            d_name = ""

            if isinstance(dec, ast.Name):

                d_name = dec.id

            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):

                d_name = dec.func.id

            if d_name == "dataclass":

                is_dataclass = True

                break

        if not is_dataclass:

            continue

        fields: list[tuple[str, str]] = []

        for stmt in node.body:

            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):

                fname = stmt.target.id

                ftype = ast.unparse(stmt.annotation) if stmt.annotation else "Any"

                fields.append((fname, ftype))

        sigs[node.name] = fields

    return sigs





def _diff_signatures(

    old: dict[str, list[tuple[str, str]]],

    new: dict[str, list[tuple[str, str]]],

) -> list[str]:

    """比对两份 @dataclass 签名，返回差异描述列表。



    Args:

        old: 旧版本签名。

        new: 新版本签名。



    Returns:

        差异描述字符串列表（如 "类 NormalizedMarketData 字段 'symbol' 类型 str→int"）；

        无差异返回空列表。

    """

    diffs: list[str] = []

    old_classes = set(old.keys())

    new_classes = set(new.keys())

    # 删除的类

    for cls in sorted(old_classes - new_classes):

        diffs.append(f"类 {cls} 被删除")

    # 新增的类（不报漂移——新增是兼容变更）

    # 修改的类（字段集变化）

    for cls in sorted(old_classes & new_classes):

        old_fields = dict(old[cls])

        new_fields = dict(new[cls])

        old_names = set(old_fields.keys())

        new_names = set(new_fields.keys())

        # 删除的字段（破坏性变更）

        for fname in sorted(old_names - new_names):

            diffs.append(f"类 {cls} 字段 '{fname}' 被删除")

        # 类型变化

        for fname in sorted(old_names & new_names):

            if old_fields[fname] != new_fields[fname]:

                diffs.append(

                    f"类 {cls} 字段 '{fname}' 类型 "

                    f"{old_fields[fname]}→{new_fields[fname]}"

                )

    return diffs





def _persist_drift_finding(project_root: Path, file_path: str, detail: str) -> None:

    """持久化契约签名漂移到 governance.db drift_audit_findings 表。



    fail-open：DB 异常只记日志不抛出（reconciler 永不抛异常）。



    Args:

        project_root: 仓库根路径。

        file_path: 漂移文件相对路径。

        detail: 漂移详情。

    """

    db_path = os.path.join(str(project_root), "data", "databases", "governance.db")

    try:

        conn = sqlite3.connect(db_path, timeout=30.0)

        try:

            conn.execute(SQL_CREATE_DRIFT_AUDIT_FINDINGS)

            finding_id = f"cs-{uuid.uuid4().hex[:12]}"

            conn.execute(

                SQL_INSERT_DRIFT_AUDIT_FINDING,

                (finding_id, now_utc(),

                 "CONTRACT_SIGNATURE_DRIFT", "HIGH",

                 file_path, detail),

            )

            conn.commit()

        finally:

            conn.close()

    except Exception as e:  # noqa: BLE001 — fail-open

        logger.warning("cross_layer_contract_signature: persist finding failed: %s", e)





def make_cross_layer_contract_signature_reconciler(gateway: "object") -> ReconcilerSpec:

    """构造 GATE-CROSS-LAYER-CONTRACT-SIGNATURE post-commit 契约签名漂移检测 reconciler。



    Args:

        gateway: GitCommitGateway 实例（用其 project_root + _run_git）。



    Returns:

        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。

        trigger 仅当 staged .py 文件命中 contracts YAML 的 physical_path，

        或 YAML 自身被修改时返回 True。

    """

    project_root = gateway.project_root

    yaml_abs = str(project_root / _CONTRACTS_YAML_REL)



    def _safe_relpath(f: str) -> str:

        try:

            return os.path.relpath(f, str(project_root)).replace("\\", "/")

        except (ValueError, OSError):

            return f.replace("\\", "/")



    def _trigger(committed_files: list[str]) -> bool:

        # 1. YAML 自身被修改 → 触发（需重检所有契约）

        for f in committed_files:

            if _safe_relpath(f) == _CONTRACTS_YAML_REL:

                return True

        # 2. .py 文件命中 physical_path → 触发

        physical_paths = _load_contract_physical_paths(yaml_abs)

        if not physical_paths:

            return False

        for f in committed_files:

            rel = _safe_relpath(f)

            if rel in physical_paths:

                return True

        return False



    def _collect_changed_contracts(

        committed_files: list[str],

        physical_paths: set[str],

    ) -> tuple[bool, list[str]]:

        """收集本次 commit 涉及的契约文件列表。



        Returns:

            (yaml_changed, changed_contracts)：yaml_changed=True 表示

            cross_layer_contracts.yaml 自身被修改（changed_contracts 含所有

            physical_path）；否则 changed_contracts 仅含本次 commit 命中的。

        """

        yaml_changed = False

        changed_contracts: list[str] = []

        for f in committed_files:

            rel = _safe_relpath(f)

            if rel == _CONTRACTS_YAML_REL:

                yaml_changed = True

                continue

            if rel in physical_paths and rel.endswith(".py"):

                changed_contracts.append(rel)

        # YAML 自身被修改 → 检测所有 physical_path（无法确定哪个变了）

        if yaml_changed:

            changed_contracts = sorted(physical_paths)

        return yaml_changed, changed_contracts



    def _check_single_contract(rel_path: str) -> str | None:

        """检查单个契约文件的签名漂移。



        Returns:

            漂移详情字符串（命中漂移时）；None=无漂移或跳过（新增文件/无 @dataclass）。

            读取失败时返回 "{rel_path}: 读取失败 {e}" 字符串。

        """

        # 读取新版本（工作区已是 commit 后状态）

        new_abs = str(project_root / rel_path)

        try:

            with open(new_abs, "r", encoding="utf-8", errors="replace") as fh:

                new_source = fh.read()

        except OSError as e:

            return f"{rel_path}: 读取失败 {e}"

        # 读取旧版本（HEAD~1）

        old_source = git_show_file(str(project_root), rel_path, "HEAD~1")

        if old_source is None:

            return None  # 新增文件，无旧版本可比对

        old_sigs = _extract_dataclass_signatures(old_source)

        new_sigs = _extract_dataclass_signatures(new_source)

        if not old_sigs and not new_sigs:

            return None  # 两边都无 @dataclass（非契约文件误匹配）

        diffs = _diff_signatures(old_sigs, new_sigs)

        if not diffs:

            return None

        detail_str = "; ".join(diffs[:5])

        if len(diffs) > 5:

            detail_str += f" (还有 {len(diffs) - 5} 项)"

        _persist_drift_finding(project_root, rel_path, detail_str)

        return f"{rel_path}: {detail_str}"



    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        try:

            physical_paths = _load_contract_physical_paths(yaml_abs)

            if not physical_paths:

                return ReconcileResult(

                    action="skip",

                    detail="cross_layer_contracts.yaml 无 physical_path 或加载失败",

                    gate_id=_GATE_ID,

                )

            _yaml_changed, changed_contracts = _collect_changed_contracts(

                committed_files, physical_paths

            )

            if not changed_contracts:

                return ReconcileResult(

                    action="skip",

                    detail="无契约文件被修改",

                    gate_id=_GATE_ID,

                )

            drift_details: list[str] = []

            for rel_path in changed_contracts:

                detail = _check_single_contract(rel_path)

                if detail:

                    drift_details.append(detail)

            if drift_details:

                summary = "; ".join(drift_details[:3])

                if len(drift_details) > 3:

                    summary += f" (还有 {len(drift_details) - 3} 个文件)"

                return ReconcileResult(

                    action="warn",

                    detail=f"跨层契约签名漂移 {len(drift_details)} 个文件: {summary}",

                    gate_id=_GATE_ID,

                )

            return ReconcileResult(

                action="clean",

                detail=f"检查 {len(changed_contracts)} 个契约文件，无签名漂移",

                gate_id=_GATE_ID,

            )



        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常

            logger.warning("cross_layer_contract_signature: reconcile failed: %s", e)

            return ReconcileResult(

                action="warn",

                detail=f"cross_layer_contract_signature reconcile error: {e}",

                gate_id=_GATE_ID,

            )



    return ReconcilerSpec(

        gate_id=_GATE_ID,

        trigger=_trigger,

        reconcile=_reconcile,

        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),

    )

