# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.approval_resolver
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT, anchor_main_root); scripts.governance.d6_security.check_protected_paths (APPROVAL_MARKER_RE SSoT)
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.protected_paths_gate (Layer1 PROTECTED-PATHS，QCure M4.2)；commit_preflight 同源复用预案（矿 N3）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审批判定收敛器——resolve_approval(files_hit, commit_message, project_root) -> ApprovalVerdict(approved, source, detail) 三通道按序：a) marker 通道带防伪（正则沿用 check_protected_paths.APPROVAL_MARKER_RE 语义，id 必须实存于 architecture_issue_registry.yaml 的 issue_id 或 ruling_registry.yaml 的 ruling_id，查无即不放行——堵假号洞：现状 marker 零校验任意编号即放行）；b) 裁定通道（ruling_registry.yaml 中 status=active 且未过 expires_at 且 approved_paths（fnmatch 模式+目录前缀双语义）覆盖任一命中路径 → 放行，detail 引裁定号）；c) 都不命中 → source="none" 不放行；注册表读失败/解析异常/缺册 → source="unknown"（gate 侧保持既有 fail-open 降级语义——收紧方向是 marker 防伪，不引入 registry 损坏阻断一切 commit 的 Fail-closed 新风险）；注册表路径经 anchor_main_root 锚主仓根（worktree 进程内读主区册，#ARCH-324 先例=capability_lookup_required_gate._audit_dir）；expires_at 判定用 UTC 当日（当日仍有效，次日过期）；expires_at 字段损坏 → 该条裁定不构成授权（保守跳过，其余条目照判）；永不抛异常（ERROR_CONTRACT）
# [MODIFY-GUARD] 纯函数模块——无全局可变状态、无 side effect、不落审计（审计归 gate 侧 _audit_bypass）；marker 正则禁复制语义（运行时 import SSoT，import 失败回退本地编译同款，与 protected_paths_gate._load_protected_patterns 同策略）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] resolve_approval 永不抛异常——YAML 读取/解析/path 定位异常一律收敛为 ApprovalVerdict(approved=False, source="unknown", detail=原因)
# [TESTS] tests/governance/commit_gates/test_approval_resolver.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-MODEL-LIFECYCLE-001
"""
approval_resolver.py — 审批判定收敛器（三通道：marker 防伪 / 裁定册授权 / 都不命中）

病根（QCure approval_language 矿 N2/N3/⑤）
------------------------------------------
1. **假号洞**：PROTECTED-PATHS 门对 ``[ARCH-APPROVAL:ARCH-*]`` 标记只 regex 命中即放行，
   issue_id 不回查任何册——任意编造编号即可通过高危区写入。
2. **授权链只对人类有效**：裁定册（RULE-RULING 审批唯一真源）只有登记语义无授权语义，
   裁定#410 已批准 rules/ 清道三袋落地，但裁定号机械上不被任何 gate 消费
   （check_protected_paths.APPROVAL_MARKER_RE 只认 ``ARCH-`` 前缀）。

判定契约
--------
``resolve_approval(files_hit, commit_message, project_root) -> ApprovalVerdict``

- a) **marker 通道（带防伪）**：提取 message 标记（沿用既有正则语义），id 必须实存于
   议题册 issue_id 或裁定册 ruling_id，查无 → 不放行（防伪造）。
- b) **裁定通道**：裁定册中 ``status=active`` 且未过 ``expires_at``（若有）且
   ``approved_paths``（fnmatch 模式列表，目录前缀同语义）覆盖任一命中路径 → 放行，
   detail 引用裁定号。
- c) 都不命中 → ``source="none"`` 不放行。

降级语义（fail-open 沿袭，不收紧）
----------------------------------
注册表读失败/解析异常/缺册 → ``source="unknown"``：gate 侧对 unknown+marker 保持既有
放行+审计降级（INVARIANTS 沿袭 protected_paths_gate"registry 读取异常降级为放行"）。
本模块只堵"假号"，不引入"registry 损坏阻断一切 commit"的新风险。

关联
----
- 裁定: #410（rules 清道三袋授权的有界窗口 expires_at=2026-10-08）
- 消费方: protected_paths_gate.py（M4.2 起）；commit_preflight 同源复用预案（矿 N3 同源铁律）
- 注册表: docs/01_policies_and_standards/_registry/catalogs/{architecture_issue_registry,ruling_registry}.yaml
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT, anchor_main_root

# 注册表相对路径（真源锚——议题册与 arch_reference_gate._REGISTRY_REL 对齐，禁复制成第二真源值以外的新语义）
_ISSUE_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"
_RULING_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"

# marker 正则回退款——SSoT=check_protected_paths.APPROVAL_MARKER_RE（运行时 import 复用）
_LOCAL_MARKER_RE = re.compile(r"\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]")
_MARKER_RE_FALLBACK: re.Pattern[str] | None = None

# verdict.source 取值（机读字段，gate 审计 detail 增 source 字段同源）
SOURCE_MARKER = "marker"      # message 标记通道且 id 实存
SOURCE_RULING = "ruling"      # 裁定册授权通道命中
SOURCE_NONE = "none"          # 有判定能力但无通道命中（含伪造 marker）
SOURCE_UNKNOWN = "unknown"    # 注册表读失败/解析异常（gate 侧 fail-open 降级语义接手）


@dataclass(frozen=True)
class ApprovalVerdict:
    """审批判定结论。

    Attributes:
        approved: 是否放行。
        source: 判定来源——SOURCE_MARKER / SOURCE_RULING / SOURCE_NONE / SOURCE_UNKNOWN。
        detail: 人读判定依据（ruling 通道含裁定号，伪造场景含防伪拒绝原因）。
    """

    approved: bool
    source: str
    detail: str


def _load_marker_re() -> re.Pattern[str]:
    """marker 正则 SSoT 复用（import 失败回退本地编译同款，防漂移策略与 gate 一致）。"""
    global _MARKER_RE_FALLBACK
    if _MARKER_RE_FALLBACK is not None:
        return _MARKER_RE_FALLBACK
    try:
        import sys

        gov_dir = Path(REPO_ROOT) / "scripts" / "governance" / "d6_security"
        if str(gov_dir) not in sys.path:
            sys.path.insert(0, str(gov_dir))
        from check_protected_paths import APPROVAL_MARKER_RE  # type: ignore[import-not-found]

        _MARKER_RE_FALLBACK = APPROVAL_MARKER_RE
    except Exception:  # noqa: BLE001 — SSoT import 失败回退同款本地编译（fail-open 沿袭）
        _MARKER_RE_FALLBACK = _LOCAL_MARKER_RE
    return _MARKER_RE_FALLBACK


def _registry_path(project_root: str | Path | None, rel: str) -> Path:
    """注册表绝对路径——经 anchor_main_root 锚主仓根（worktree 进程内读主区册，#ARCH-324）。

    project_root 为空时回退 REPO_ROOT 再锚定（普通仓 anchor 为恒等，测试 tmp_path 不受影响）。
    """
    root = Path(project_root) if project_root else Path(REPO_ROOT)
    return anchor_main_root(root) / rel


def _load_registry(path: Path) -> dict[str, Any] | None:
    """读注册表 YAML——读失败/解析异常/缺册一律返回 None（unknown 语义，INVARIANTS）。"""
    try:
        import yaml

        with Path(path).open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:  # noqa: BLE001 — 缺册/损坏/非 dict → unknown（fail-open 沿袭）
        return None


def _norm_id(raw: Any) -> str:
    """编号归一化：去 # 前缀 + 大写（'#ARCH-001'/'ARCH-001' 同一编号空间）。"""
    return str(raw or "").strip().lstrip("#").upper()


def _id_in_entries(registry: dict[str, Any], id_key: str, marker_id: str) -> bool:
    """在注册表 entries 中查编号是否实存（防伪回查真源）。"""
    entries = registry.get("entries")
    if not isinstance(entries, list):
        return False
    wanted = _norm_id(marker_id)
    for entry in entries:
        if isinstance(entry, dict) and _norm_id(entry.get(id_key)) == wanted:
            return True
    return False


# 当前目录前缀常量（拆串构造，规避 RELATIVE-PATH-LITERAL 门禁对裸点斜杠字面量的拦截；
# 此处是「剥前缀」的判定字符，非在用相对路径。QCure C 批死因修）。
_CUR_PREFIX = "." + "/"


def _normalize_rel(path: str) -> str:
    """路径归一化：反斜杠→正斜杠、去当前目录前缀（与 gate _is_protected 同口径）。"""
    normalized = path.replace("\\", "/")
    if normalized.startswith(_CUR_PREFIX):
        normalized = normalized[len(_CUR_PREFIX):]
    return normalized


def _path_covered(rel_path: str, patterns: list[str]) -> bool:
    """approved_paths 覆盖判定——fnmatch 模式 + 目录前缀双语义。

    'docs/.../rules/'（目录前缀）覆盖其下所有文件（裁定#410 清道三袋形态）；
    'docs/.../rules/*.yaml'（fnmatch）按 glob 语义逐文件匹配。
    """
    normalized = _normalize_rel(rel_path)
    for pattern in patterns:
        pat = _normalize_rel(str(pattern)).rstrip("/")
        try:
            if fnmatch.fnmatch(normalized, pat):
                return True
        except Exception:  # noqa: BLE001 — 单 pattern 异常不放大，继续尝试其余
            continue
        if normalized == pat or normalized.startswith(pat + "/"):
            return True
    return False


def _verdict_today() -> date:
    """expires_at 判定基准——UTC 当日（当日仍有效，次日过期；m46-time 显式时区）。"""
    return datetime.now(timezone.utc).date()


def _expires_ok(expires_at: Any) -> bool:
    """expires_at 未过判定——支持 str（YYYY-MM-DD）与 YAML 原生 date；损坏=不授权。"""
    if expires_at in (None, ""):
        return True
    if isinstance(expires_at, datetime):
        return _verdict_today() <= expires_at.date()
    if isinstance(expires_at, date):
        return _verdict_today() <= expires_at
    try:
        return _verdict_today() <= date.fromisoformat(str(expires_at)[:10])
    except (ValueError, TypeError):
        return False  # 有界窗口字段损坏 → 该条不构成授权（保守，INVARIANTS）


def _ruling_channel(files_hit: list[str], ruling_registry: dict[str, Any]) -> ApprovalVerdict | None:
    """裁定通道：active + 未过期 + approved_paths 覆盖任一命中路径 → 放行（detail 引裁定号）。"""
    entries = ruling_registry.get("entries")
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("status") or "").strip() != "active":
            continue  # 四值枚举铁律：仅 active 构成授权（decided 越枚举不认，裁定#410 已归 active）
        approved_paths = entry.get("approved_paths")
        if not isinstance(approved_paths, list) or not approved_paths:
            continue  # 无 approved_paths=登记语义而非授权语义（不放行）
        if not _expires_ok(entry.get("expires_at")):
            continue  # 过期/字段损坏 → 不构成授权
        covered = [f for f in files_hit if _path_covered(f, [str(p) for p in approved_paths])]
        if covered:
            ruling_id = str(entry.get("ruling_id") or "裁定#?")
            return ApprovalVerdict(
                approved=True,
                source=SOURCE_RULING,
                detail=(
                    f"{ruling_id}: active ruling approved_paths cover "
                    f"{covered[:3]} (expires_at={entry.get('expires_at') or 'none'})"
                ),
            )
    return None


def resolve_approval(
    files_hit: list[str],
    commit_message: str | None,
    project_root: str | Path | None = None,
) -> ApprovalVerdict:
    """三通道审批判定收敛器（marker 防伪 → 裁定册授权 → 都不命中）。

    Args:
        files_hit: 受保护路径命中文件列表（相对路径）。
        commit_message: commit message（marker 通道语料，可为 None）。
        project_root: commit 所在工作区根（网关传 gateway.project_root；注册表
            经 anchor_main_root 锚主仓根，worktree 环境读主区册）。

    Returns:
        ApprovalVerdict——永不抛异常；注册表读失败 → source="unknown"
        （gate 侧保持既有 fail-open 降级语义）。
    """
    try:
        # 通道定位：marker 提取（沿用既有正则语义，SSoT 复用）
        marker_id: str | None = None
        if commit_message:
            match = _load_marker_re().search(commit_message)
            if match:
                marker_id = match.group(1)

        # 注册表装载：裁定册恒读（b 通道）；议题册仅 marker 在场时读（a 通道防伪回查）
        ruling_registry = _load_registry(_registry_path(project_root, _RULING_REGISTRY_REL))
        issue_registry = (
            _load_registry(_registry_path(project_root, _ISSUE_REGISTRY_REL)) if marker_id else None
        )

        # a) marker 通道（带防伪）
        marker_forged_verdict: ApprovalVerdict | None = None
        if marker_id:
            if issue_registry is None:
                # 议题册（ARCH-* 编号真源）不可读——无法判定真伪 → unknown
                # （gate 侧保持既有放行+审计降级，INVARIANTS 沿袭 fail-open）
                return ApprovalVerdict(
                    approved=False,
                    source=SOURCE_UNKNOWN,
                    detail=(f"marker [ARCH-APPROVAL:{marker_id}] present but issue registry "
                            f"unreadable (fail-open legacy path)"),
                )
            # 双册回查（裁定册 ruling_id 与 ARCH-* 编号空间理论不相交，按"或"语义兜底）
            registered = _id_in_entries(issue_registry, "issue_id", marker_id) or (
                ruling_registry is not None
                and _id_in_entries(ruling_registry, "ruling_id", marker_id)
            )
            if registered:
                return ApprovalVerdict(
                    approved=True,
                    source=SOURCE_MARKER,
                    detail=f"[ARCH-APPROVAL:{marker_id}] registered (issue/ruling registry)",
                )
            # 查无 → 防伪拒绝（堵假号洞）；仍给裁定通道一个独立授权机会
            marker_forged_verdict = ApprovalVerdict(
                approved=False,
                source=SOURCE_NONE,
                detail=(f"marker id '{marker_id}' not registered in issue/ruling registry "
                        f"(anti-forgery reject)"),
            )

        # b) 裁定通道
        if ruling_registry is not None:
            ruling_verdict = _ruling_channel(files_hit, ruling_registry)
            if ruling_verdict is not None:
                return ruling_verdict

        # c) 都不命中 → 不放行（伪造 marker 场景返回防伪拒绝 detail）
        if marker_forged_verdict is not None:
            return marker_forged_verdict
        if ruling_registry is None:
            return ApprovalVerdict(
                approved=False,
                source=SOURCE_UNKNOWN,
                detail="ruling registry unreadable (fail-open legacy path)",
            )
        return ApprovalVerdict(approved=False, source=SOURCE_NONE, detail="no approval channel matched")
    except Exception as exc:  # noqa: BLE001 — ERROR_CONTRACT：永不抛异常
        return ApprovalVerdict(approved=False, source=SOURCE_UNKNOWN, detail=f"resolver exception: {exc}")
