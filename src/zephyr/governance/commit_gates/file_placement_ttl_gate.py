# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.file_placement_ttl_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml (真源：directory_zones); docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml (真源：decision_tree Q1)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——真源 YAML 缺失/解析失败时阻断 commit；动态加载 directory_contract.yaml + ttl_vocabulary.yaml，禁止硬编码路径列表
# [MODIFY-GUARD] gate_id="FILE-PLACEMENT-TTL"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通过；exit 1=有违规（阻断 commit，PROMOTION_BLOCKED 或 FILE-PLACEMENT-TTL 冲突）
# [TESTS] tests/governance/commit_gates/test_file_placement_ttl_gate.py
# [A_module] module_id=MOD-GOV-file_placement_ttl_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# [ARCH] ARCH-049
"""file_placement_ttl_gate.py — 文件放置与 TTL 一致性门禁（治本 #ARCH-049：防止临时文件乱放根目录）

落地 ttl_vocabulary.yaml §146-152 "永久区准入机制"（原标注"后续实现"）+
directory_contract.yaml directory_zones.permanent.gate=allow_promote_required。

病根（幻觉/漂移物理证据，#ARCH-049）
---------------------------------
AI 创建临时文件（ttl=task_bound）时无路径约束，乱放根目录或永久区：
- 案例 2026-07-05：audit_assignment/ 放根目录（应在 docs/_working/）
- 根因：ttl_vocabulary.yaml §146-152 设计了永久区准入机制但标注"后续实现"未施工
- GitCommitGateway 预留 allow_promote 参数 + PROMOTION_BLOCKED 常量但无检查逻辑
- AI 不被强制走 decision_tree 判定，路径与 TTL 不一致无门禁阻断

治本方案（#ARCH-049）
--------
新建 in-process gate FILE-PLACEMENT-TTL（priority=33），三重校验：
1. 永久区准入（PROMOTION_BLOCKED）：permanent.paths 新文件需 allow_promote=True
   （exempt_subdirs 生成器输出豁免）
2. TTL↔zone 一致性：frontmatter.ttl 与路径 zone 冲突 → 阻断
3. 根目录子目录准入：第一级目录不在 directory_zones 所有 paths → 阻断
   （防止 audit_assignment/ 这类乱建子目录，临时文件应落 docs/_working/）

真源动态加载（不硬编码）：
- 永久区/临时区/中性区路径：directory_contract.yaml directory_zones.*.paths
- 生成器豁免：directory_contract.yaml directory_zones.permanent.exempt_subdirs
- 过程性子目录：ttl_vocabulary.yaml decision_tree.Q1.criteria

设计决策
--------
1. **in-process 而非 subprocess**：TTL↔路径一致性是新逻辑，check_directory_contract.py /
   check_frontmatter_metadata.py 均未覆盖。gate 内动态加载 YAML 真源（派生读取，非多真源）。
2. **fail-closed**：YAML 真源缺失/解析失败阻断 commit（路径约束是核心约束）。
3. **priority=33**：在 TTL-METADATA(32) 之后、R5-DIGIT-SUFFIX(35) 之前——
   先校验 ttl 字段合法（TTL-METADATA），再校验 ttl↔路径一致（本 gate）。
4. **allow_promote 透传**：commit() 的 allow_promote 参数通过 check_all kwargs 传入。
5. **隐藏目录豁免**：以 . 开头的目录（.git/.aidrafts/.github 等）豁免规则3。

Usage::

    from zephyr.governance.commit_gates.file_placement_ttl_gate import make_file_placement_ttl_gate

    registry.register(make_file_placement_ttl_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, allow_promote=..., allow_overlap=...)
"""

from __future__ import annotations

import logging
import os
import re

import yaml

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_file_placement_ttl_gate"]

# 真源路径（相对 project_root）
_DC_PATH = "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml"
_TTL_VOCAB_PATH = "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml"

# TTL 提取正则——支持 YAML frontmatter + 注释锚定两种格式
_TTL_FRONTMATTER_RE = re.compile(r"^ttl:\s*(\w+)\s*$", re.MULTILINE)
_TTL_COMMENT_RE = re.compile(r"^#\s*\[TTL\]\s*(\w+)", re.MULTILINE)


def _extract_ttl(file_path: str) -> str | None:
    """从文件头部提取 ttl 字段值（支持 YAML frontmatter + 注释锚定）。

    Args:
        file_path: 文件绝对路径。

    Returns:
        ttl 值（permanent/task_bound）或 None（无声明）。
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            # 只读前 50 行（ttl 字段在头部）
            head = "".join(next(f, "") for _ in range(50))
    except (OSError, UnicodeDecodeError):
        return None

    # 优先匹配 YAML frontmatter: ttl: xxx
    m = _TTL_FRONTMATTER_RE.search(head)
    if m:
        return m.group(1).strip()
    # 兜底匹配注释锚定: # [TTL] xxx
    m = _TTL_COMMENT_RE.search(head)
    if m:
        return m.group(1).strip()
    return None


def _load_placement_ssot(project_root):
    """动态加载文件放置真源（directory_contract.yaml + ttl_vocabulary.yaml）。

    Returns:
        (permanent_paths, temporary_paths, neutral_paths, exempt_subdirs,
         process_subdir_segments, allowed_root_subdirs)
    """
    dc_path = project_root / _DC_PATH
    if not dc_path.is_file():
        raise FileNotFoundError(f"directory_contract.yaml not found: {dc_path}")
    with open(dc_path, encoding="utf-8") as f:
        dc = yaml.safe_load(f)

    zones = dc.get("directory_zones", {})
    permanent_paths = zones.get("permanent", {}).get("paths", [])
    temporary_paths = zones.get("temporary", {}).get("paths", [])
    neutral_paths = zones.get("neutral", {}).get("paths", [])
    exempt_subdirs = zones.get("permanent", {}).get("exempt_subdirs", [])

    # 从 ttl_vocabulary.yaml 加载 Q1 过程性子目录（contains 判定）
    tv_path = project_root / _TTL_VOCAB_PATH
    process_subdir_segments: list[str] = []
    if tv_path.is_file():
        with open(tv_path, encoding="utf-8") as f:
            tv = yaml.safe_load(f)
        q1_criteria = (
            tv.get("decision_tree", {}).get("nodes", {}).get("Q1", {}).get("criteria", [])
        )
        for c in q1_criteria:
            if c.get("signal") == "path" and c.get("operator") == "contains":
                process_subdir_segments.append(c["value"])  # 如 "/changes/"

    # 提取允许的根目录第一级子目录（从所有 zone paths）
    allowed_root_subdirs: set[str] = set()
    for paths in (permanent_paths, temporary_paths, neutral_paths):
        for p in paths:
            first_seg = p.split("/")[0]
            if first_seg:
                allowed_root_subdirs.add(first_seg + "/")

    return (
        permanent_paths,
        temporary_paths,
        neutral_paths,
        exempt_subdirs,
        process_subdir_segments,
        allowed_root_subdirs,
    )


def make_file_placement_ttl_gate() -> GateSpec:
    """构造 FILE-PLACEMENT-TTL 门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="FILE-PLACEMENT-TTL", priority=33)。
        priority=33——在 TTL-METADATA(32) 之后、R5-DIGIT-SUFFIX(35) 之前
        （先校验 ttl 字段合法，再校验 ttl↔路径一致）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        allow_promote = kwargs.get("allow_promote", False)
        project_root = gateway.project_root

        # 1. 动态加载真源（fail-closed：加载失败阻断）
        try:
            (
                permanent_paths,
                temporary_paths,
                neutral_paths,
                exempt_subdirs,
                process_subdir_segments,
                allowed_root_subdirs,
            ) = _load_placement_ssot(project_root)
        except (FileNotFoundError, OSError, yaml.YAMLError) as e:
            return False, f"FILE-PLACEMENT-TTL 真源加载失败（fail-closed）: {e}"

        # 2. 逐文件校验
        violations: list[str] = []
        for f in files:
            if not os.path.isfile(f):
                continue  # deletion commit：跳过
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")

            # tests/ 豁免
            if is_test_exempt(rel):
                continue

            # 判定 zone 归属
            in_permanent = any(rel.startswith(p) for p in permanent_paths)
            in_temporary = any(rel.startswith(p) for p in temporary_paths)
            # 过程性子目录（Q1 contains 判定，如 /changes/ /reports/ /delivery/）
            in_process = any(seg in rel for seg in process_subdir_segments)

            # 提取 frontmatter.ttl
            ttl = _extract_ttl(f)

            # 判断是否新增文件（未 git tracked = 新增；tracked = 修改）
            # 规则1/3 只对新增文件检查（永久区准入和根目录子目录准入是"新文件进入"约束）
            # 规则2 对所有文件检查（TTL↔zone 一致性是持续约束）
            is_new_file = not gateway._is_git_tracked(rel)

            # 规则1：永久区新文件准入（PROMOTION_BLOCKED）——只对新增文件
            if is_new_file and in_permanent and not any(rel.startswith(ex) for ex in exempt_subdirs):
                if not allow_promote:
                    violations.append(
                        f"PROMOTION_BLOCKED: {rel} 位于永久区，需 allow_promote=True 准入"
                        f"（或落入 exempt_subdirs 生成器豁免）"
                    )

            # 规则2：TTL↔zone 一致性（对所有文件）
            if ttl == "permanent" and in_temporary:
                violations.append(
                    f"FILE-PLACEMENT-TTL: {rel} frontmatter.ttl=permanent 但在临时区，"
                    f"应迁移到永久区或改 ttl=task_bound"
                )
            elif ttl == "task_bound" and in_permanent:
                violations.append(
                    f"FILE-PLACEMENT-TTL: {rel} frontmatter.ttl=task_bound 但在永久区，"
                    f"应改 ttl=permanent 或迁移到临时区（docs/_working/）"
                )

            # 规则3：根目录子目录准入（防止 audit_assignment/ 这类乱建子目录）——只对新增文件
            if is_new_file and "/" in rel:
                first_seg = rel.split("/")[0] + "/"
                # 豁免：以 . 开头的目录（.git/.aidrafts/.github/.trae 等工具内部目录）
                if not first_seg.startswith("."):
                    if first_seg not in allowed_root_subdirs:
                        violations.append(
                            f"FILE-PLACEMENT-TTL: {rel} 位于未登记的根目录子目录 '{first_seg}'，"
                            f"允许的子目录: {sorted(allowed_root_subdirs)}。"
                            f"临时文件请落 docs/_working/，永久文件需裁定归属域"
                        )

        if violations:
            return False, "\n".join(violations)
        return True, "file placement ttl check passed"

    return GateSpec(gate_id="FILE-PLACEMENT-TTL", check=_check, priority=33)
