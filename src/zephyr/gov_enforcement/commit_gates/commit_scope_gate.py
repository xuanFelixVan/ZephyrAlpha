# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.commit_scope_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file); zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] allow_multi_domain=True 时放行（逃生通道）；单域或全 UNKNOWN 时 PASS；跨≥2 域时 BLOCK；域判定异常 fail-open（PASS，不阻断）；reconciler auto-commit 走 _commit_auto 不经本 gate（仅 DIRECTORY-CONTRACT），无需豁免
# [MODIFY-GUARD] gate_id="COMMIT-SCOPE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——域判定/YAML 读取异常降级为 UNKNOWN/fail-open（passed=True）
# [TESTS] tests/governance/commit_gates/test_commit_scope_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""commit_scope_gate.py — 提交边界域一致性门禁（COMMIT-SCOPE）

检测一个 commit 的目标文件是否跨越多个功能域（D_XXX）。跨域时硬阻断，
要求拆分为多个 commit，每个域一个。对标 AGENTS.md「一个任务=1次commit」原则。

病根（13a5e1d512 混合提交事故）
--------------------------------
并发 session 将 D_REGIME 域的 regime 校准器修复 + D_GOVERNANCE 域的 DQ 维度
扩展混合在一个 commit。该 session 显式把跨域文件列入 commit files，但无任何
gate 检测「一个 commit 的 files 是否跨多个责任域」——这是语义层缺口。

三 gate 正交防御
----------------
- HELD-OVERLAP（priority=50）：检测文件被其他 session claim（注册表层）
- FOREIGN-CHANGE-DETECTION（priority=45）：检测 claim 时外来变更（内容层）
- COMMIT-SCOPE（priority=48，本 gate）：检测 commit 跨域（语义层）

reconciler 豁免
----------------
reconciler auto-commit 走 ``_commit_auto``（仅 DIRECTORY-CONTRACT gate，不走完整
gate 链，见 git_commit_gateway._commit_auto docstring），不经本 gate，无需豁免逻辑。
本 gate 只在 AI 主导的 ``commit()`` 完整路径运行。

域判定策略（三级 fallback，复用已验证机制）
--------------------------------------------
1. .py 文件：读 ``# [DOMAIN] D_XXX`` 头部（复用 domain_fk_gate 的正则模式，
   读工作区文件——gate 运行时文件尚未 staged，stage 在 gate 之后的 _commit_locked 内）
2. 非 .py 文件：用 functional_domain_registry.yaml 的 ssot_path 最长前缀匹配
3. 未命中：标记 UNKNOWN（不参与跨域判定，避免误报）

逃生通道
--------
``allow_multi_domain=True`` 放行，commit message 追加 ``[GW:<sid>:multi-domain]``
标记（对标 ``[GW:<sid>:overlap]``）。合理场景：跨域重构 / 域注册表本身变更 /
裁定#NNN 引用 + registry 同 commit（AGENTS.md L198 已有此要求）。

Usage::

    from zephyr.gov_enforcement.commit_gates.commit_scope_gate import make_commit_scope_gate

    registry.register(make_commit_scope_gate())
"""

from __future__ import annotations

import logging
import os
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_commit_scope_gate"]

# 域注册表真源（SSoT TRAE-062：与 domain_fk_gate 同源，规则数据真源=YAML）
_DOMAIN_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"

# 匹配 [DOMAIN] D_XXX 头部（与 domain_fk_gate._DOMAIN_HEADER_RE 同模式，列 0 起始）
_DOMAIN_HEADER_RE = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)")

# 匹配 YAML entries 段中的 "- domain: D_XXX" 条目（与 domain_fk_gate 同模式）
_YAML_DOMAIN_ENTRY_RE = re.compile(r"^-\s*domain:\s*(\S+)")
# 匹配条目内的 "  ssot_path: xxx" 行
_YAML_SSOT_PATH_RE = re.compile(r"^\s*ssot_path:\s*(\S+)")

# [DOMAIN] 头部扫描行数上限（头部 frontmatter 区）
_HEADER_SCAN_LINES = 20


def _load_path_domain_map(gateway) -> dict[str, str] | None:
    """从 functional_domain_registry.yaml 加载 ssot_path→domain 映射。

    读取顺序：staged 版本（``git show :path``，与 domain_fk_gate 一致）→ 工作区文件。
    解析 entries 段，逐条目关联 ``- domain: D_XXX`` 与后续 ``  ssot_path: xxx``。

    Args:
        gateway: GitCommitGateway 实例（提供 run_git / project_root）。

    Returns:
        {ssot_path: domain} 字典，用于非 .py 文件的路径推断（最长前缀匹配）；
        YAML 不可读或无条目时返回 None（调用方 fail-open）。
    """
    content = _read_staged_file(gateway, _DOMAIN_REGISTRY_REL)
    if content is None:
        # fallback：读工作区版本（YAML 未 staged 但已 tracked 时 staged 版本 == HEAD，
        # _read_staged_file 已能读到；此处兜底新建/异常场景）
        try:
            abs_path = str(gateway.project_root / _DOMAIN_REGISTRY_REL)
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:  # noqa: BLE001 — fail-open
            content = None
    if content is None:
        logger.warning("COMMIT-SCOPE fail-open: 无法读取 functional_domain_registry.yaml")
        return None

    path_map: dict[str, str] = {}
    current_domain: str | None = None
    for line in content.splitlines():
        m_domain = _YAML_DOMAIN_ENTRY_RE.match(line)
        if m_domain:
            current_domain = m_domain.group(1)
            continue
        m_path = _YAML_SSOT_PATH_RE.match(line)
        if m_path and current_domain:
            path_map[m_path.group(1)] = current_domain
    if not path_map:
        logger.warning("COMMIT-SCOPE fail-open: functional_domain_registry.yaml 未解析出 ssot_path 条目（格式异常？）")
        return None
    return path_map


def _infer_domain_by_path(rel_path: str, path_map: dict[str, str]) -> str:
    """用 ssot_path 最长前缀匹配推断文件域。

    Args:
        rel_path: 文件相对路径（正斜杠归一化）。
        path_map: {ssot_path: domain} 字典。

    Returns:
        匹配的域 ID，或 "UNKNOWN"。
    """
    normalized = rel_path.replace("\\", "/")
    best_match: str | None = None
    best_len = 0
    for ssot_path, domain in path_map.items():
        sp = ssot_path.rstrip("/")
        if normalized.startswith(sp + "/") and len(sp) > best_len:
            best_match = domain
            best_len = len(sp)
    return best_match or "UNKNOWN"


def _get_file_domain(gateway, abs_file: str, path_map: dict[str, str] | None) -> str:
    """获取单个文件的域归属（三级 fallback）。

    1. .py 文件：读工作区文件 [DOMAIN] 头部（gate 运行时文件未 staged，
       直接 open 工作区版本——[DOMAIN] 头部是文件固有属性）
    2. 路径推断：functional_domain_registry.yaml 的 ssot_path 最长前缀匹配
    3. UNKNOWN

    fail-open：任何异常降级为 UNKNOWN（不阻断）。
    """
    try:
        rel = os.path.relpath(abs_file, str(gateway.project_root)).replace("\\", "/")
    except (ValueError, AttributeError):
        return "UNKNOWN"

    # 1. .py 文件读 [DOMAIN] 头部
    if rel.endswith(".py"):
        try:
            with open(abs_file, "r", encoding="utf-8", errors="replace") as f:
                for _ in range(_HEADER_SCAN_LINES):
                    line = f.readline()
                    if not line:
                        break
                    m = _DOMAIN_HEADER_RE.match(line)
                    if m:
                        return m.group(1)
        except Exception:  # noqa: BLE001 — fail-open
            pass  # 文件不存在（staged delete）或读取失败 → 落到路径推断

    # 2. 路径推断
    if path_map:
        return _infer_domain_by_path(rel, path_map)

    # 3. UNKNOWN
    return "UNKNOWN"


def make_commit_scope_gate() -> GateSpec:
    """构造提交边界域一致性门禁 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="COMMIT-SCOPE", priority=48)。
        priority=48 在 DERIVED-FILE-DELETION(46) 之后、HELD-OVERLAP(50) 之前
        ——文件级安全检查（40-46）之后、搭便车检查（50）之前，语义层检查。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 逃生通道：显式声明放行，调用方负责追加 [GW:<sid>:multi-domain] 标记
        if kwargs.get("allow_multi_domain"):
            return True, ""

        # 加载路径→域映射（fail-open）
        try:
            path_map = _load_path_domain_map(gateway)
        except Exception:  # noqa: BLE001 — fail-open
            path_map = None

        # 收集每个文件的域（排除 UNKNOWN——无域信息不参与跨域判定，避免误报）
        file_domains: dict[str, str] = {}  # {rel_path: domain}
        try:
            for abs_f in files:
                domain = _get_file_domain(gateway, abs_f, path_map)
                if domain != "UNKNOWN":
                    try:
                        rel = os.path.relpath(abs_f, str(gateway.project_root))
                    except (ValueError, AttributeError):
                        rel = abs_f
                    file_domains[rel.replace("\\", "/")] = domain
        except Exception:  # noqa: BLE001 — fail-open
            return True, ""

        # 单域或无域信息 → PASS
        domains = set(file_domains.values())
        if len(domains) <= 1:
            return True, ""

        # 跨域 → BLOCK
        domain_files: dict[str, list[str]] = {}
        for f, d in file_domains.items():
            domain_files.setdefault(d, []).append(f)

        detail_lines = [f"  {d}: {sorted(fs)}" for d, fs in sorted(domain_files.items())]
        return False, (
            f"commit 跨越多个功能域（COMMIT_SCOPE_VIOLATION）: "
            f"检测到 {len(domains)} 个域。"
            f"一个 commit 应只包含单一责任域的改动"
            f"（AGENTS.md「一个任务=1次commit」原则）。"
            f"请拆分为多个 commit，每个域一个。\n"
            + "\n".join(detail_lines)
            + "\n如确认需跨域提交（如跨域重构/域注册表变更），"
            "用 commit(allow_multi_domain=True) 逃生通道。"
        )

    return GateSpec(gate_id="COMMIT-SCOPE", check=_check, priority=48)
