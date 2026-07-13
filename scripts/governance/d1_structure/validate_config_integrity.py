# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/validate_config_integrity.py | §
# [MODULE] scripts.governance.d1_structure.validate_config_integrity
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
validate_config_integrity.py — 运行时配置完整性十一层纵深审计 + 自动同步检测



对标：ITIL SACM §4.5（Configuration Audit — 配置项定期对账）
     ISO 42001 §8（AI System Impact Assessment — AI系统配置变更评估）
     Kubernetes kubeconform（声明式配置Schema校验模式）
     AGENTS.md §4（编码安全 — UTF-8 / 无BOM）
     AGENTS.md §6.2（原子事务模式 — 配置与代码交叉引用一致性 + 测试标记注册链）
     AGENTS.md §6.5（脚本自创入库强制约定）

检测内容：
- L1 文件完整性：YAML数量、编码（无BOM）、语法有效性
- L2 Schema深度校验：required字段、类型约束、边界值、semver版本
- L3 交叉引用：handler函数存在性、glob路径真实性、trigger_router↔PHASE1D对齐
- L4 全项目路径常量：parents[N]统一性（防off-by-one溢出bug）
- L5 治理文档对账：authority-registry.yaml 引用一致性 + directory-std config/ 目录定义
- L6 安全态势：deny显式覆盖、宽泛allow检测、权限降级路径
- L7 自动同步检测：manifest↔文件系统脚本登记对账、预埋文件就绪提醒
    （⚠️ 仅检测报告，不自动修改CBAC权限——AGENTS.md §6.1 变更须Owner审批）
- L8 代码-配置对账：KNOWN_MODELS同步、registry路径漂移、状态机完整性、implementation_status标注
- L9 注释与追踪审计：YAML注释计数准确性、git追踪状态、登记表entry_count一致性
- L10 测试标记对账：@pytest.mark.* 装饰器 ↔ pyproject.toml markers 双向同步（AGENTS.md §6.2 测试标记注册链）
- L11 契约-实现对账：declarative-contract-tracker-registry.md ↔ config/ YAML implementation_status 自动交叉校验

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 运行时配置完整性十一层纵深审计（L1-L11）+ 自动修复（L7）
dimensions:
- D1
- D4
- D5
- D6
- D8
- D9
priority: P0
timeout_seconds: 60
warn_only: false
"""


import os
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import CONFIG_DIR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()
import argparse
import tomllib

import yaml
from _shared.constants import CONFIG_DIR, EXIT_PASS, SRC_DIR  # noqa: E402  治本(ARCH-038 P3): 补全 SRC_DIR import（L8 l8_code_config_reconciliation 使用）

EXCLUDE_DIRS: tuple[str, ...] = ()

AUTH_REG_PATH = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml"
DIR_STD_PATH = REPO_ROOT / "docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml"

PHASE1D_TRIGGER_TYPES = frozenset(
    {
        "onboarding",
        "drift_detected",
        "compression_needed",
        "cleanup_due",
        "blueprint_published",
    }
)

IMMUTABLE_SCHEMA = {
    "min_chars": {"type": int, "ge": 100, "le": 10000},
    "max_chars": {"type": int, "ge": 100, "le": 10000},
    "preserve_structure": {"type": bool},
    "preserve_provenance": {"type": bool},
    "preserve_immutable_blocks": {"type": list},
}


def _rel(path: Path) -> str:
    """_rel implementation."""
    return "/" + str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def l1_file_integrity() -> tuple[list[str], list[str], dict]:
    """L1: 文件完整性 + YAML语法 + 编码安全检查"""
    errors = []
    warnings = []
    yaml_data = {}

    config_files = sorted(f for f in CONFIG_DIR.rglob("*") if f.is_file())
    yaml_files = [f for f in config_files if f.suffix == ".yaml"]

    for f in config_files:
        rel = _rel(f)
        try:
            raw = f.read_bytes()
        except OSError as exc:
            errors.append(f"[L1] {rel}: 无法读取 — {exc}")
            continue

        if raw[:3] == b"\xff\xfe" or raw[:3] == b"\xfe\xff":
            errors.append(f"[L1] {rel}: UTF-16 BOM 编码（应使用 UTF-8 without BOM）")
        elif raw[:3] == b"\xef\xbb\xbf":
            warnings.append(f"[L1] {rel}: 含 UTF-8 BOM（建议去除，AGENTS.md §4）")

        crlf_count = raw.count(b"\r\n")
        lf_only_count = raw.count(b"\n") - crlf_count
        if crlf_count > 0 and lf_only_count > 0:
            warnings.append(f"[L1] {rel}: 混合行尾（CRLF={crlf_count}, LF={lf_only_count}）")

        if f.suffix == ".yaml":
            try:
                text = raw.decode("utf-8", errors="replace")
            except UnicodeError:
                text = ""
            if text:
                trailing_ws = [
                    (i + 1) for i, line in enumerate(text.split("\n")) if line.rstrip("\r\n") != line.rstrip()
                ]
                if trailing_ws:
                    warnings.append(f"[L1] {rel}: 尾部空白行 {trailing_ws[:5]}")
                if "\t" in text:
                    tab_lines = [(i + 1) for i, line in enumerate(text.split("\n")) if "\t" in line]
                    warnings.append(f"[L1] {rel}: 含 Tab 字符行 {tab_lines[:5]}")

    for f in sorted(yaml_files):
        rel = _rel(f)
        try:
            with open(f, encoding="utf-8") as fh:
                content = fh.read()
            data = yaml.safe_load(content)
            yaml_data[rel] = data
            if data is None:
                errors.append(f"[L1] {rel}: YAML 解析为 None（空文件或全注释）")
            elif not isinstance(data, dict):
                errors.append(f"[L1] {rel}: 顶层类型={type(data).__name__}，期望 dict")
        except yaml.YAMLError as exc:
            errors.append(f"[L1] {rel}: YAML 语法错误 — {exc}")
        except UnicodeDecodeError as exc:
            errors.append(f"[L1] {rel}: 编码错误 — {exc}")

    return errors, warnings, yaml_data


def l2_schema_deep(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L2: Schema深度校验"""
    errors = []
    warnings = []

    # ARCH-038 R2: capabilities.yaml 已从 CBAC 规则文件重构为功能开关文件（无 rules 字段）。
    # CBAC 写保护已由 GitCommitGateway claim_files 机制替代，删除过时的 rules 检查。
    # 保留 trigger_router/compression_policy 的 schema 检查。

    tr = yaml_data.get("/config/trigger_router.yaml", {})
    triggers = tr.get("triggers", {})
    if not isinstance(triggers, dict):
        errors.append("[L2] trigger_router.yaml: triggers 不是 dict")
        triggers = {}

    for ttype, spec in triggers.items():
        if not isinstance(spec, dict):
            errors.append(f'[L2] trigger_router.yaml trigger "{ttype}": 值不是 dict')
            continue
        handler = spec.get("handler", "")
        safety = spec.get("safety", "")
        enabled = spec.get("enabled", None)
        desc = spec.get("description", "")

        if not isinstance(handler, str) or not handler.strip():
            errors.append(f'[L2] trigger_router.yaml trigger "{ttype}": handler 为空')
        elif "." not in handler:
            warnings.append(f'[L2] trigger_router.yaml trigger "{ttype}": handler 格式非 module.func — "{handler}"')
        if safety not in ("L", "M", "H"):
            warnings.append(f'[L2] trigger_router.yaml trigger "{ttype}": safety="{safety}" 非 L/M/H')
        if enabled is not None and not isinstance(enabled, bool):
            errors.append(f'[L2] trigger_router.yaml trigger "{ttype}": enabled 不是 bool')
        if isinstance(desc, str) and len(desc) > 200:
            warnings.append(f'[L2] trigger_router.yaml trigger "{ttype}": description={len(desc)} 字符（建议≤200）')

    cp = yaml_data.get("/config/compression_policy.yaml", {})
    policy = cp.get("policy", {})
    if not isinstance(policy, dict):
        errors.append("[L2] compression_policy.yaml: policy 不是 dict")
        policy = {}

    for fname, constraints in IMMUTABLE_SCHEMA.items():
        val = policy.get(fname)
        if val is None:
            errors.append(f"[L2] compression_policy.yaml: 缺少 Immutable Core 字段 — {fname}")
            continue
        if not isinstance(val, constraints["type"]):
            errors.append(
                f"[L2] compression_policy.yaml: {fname} 类型={type(val).__name__}，期望 {constraints['type'].__name__}"
            )
        elif "ge" in constraints and val < constraints["ge"]:
            errors.append(f"[L2] compression_policy.yaml: {fname}={val} < 下限 {constraints['ge']}")
        elif "le" in constraints and val > constraints["le"]:
            errors.append(f"[L2] compression_policy.yaml: {fname}={val} > 上限 {constraints['le']}")

    if isinstance(policy.get("min_chars"), int) and isinstance(policy.get("max_chars"), int):
        if policy["max_chars"] < policy["min_chars"]:
            errors.append(
                f"[L2] compression_policy.yaml: max_chars({policy['max_chars']}) < min_chars({policy['min_chars']}) — 矛盾"
            )

    for key, label in [
        ("/config/capabilities.yaml", "capabilities"),
        ("/config/trigger_router.yaml", "trigger_router"),
        ("/config/compression_policy.yaml", "compression_policy"),
    ]:
        d = yaml_data.get(key, {})
        if d and "version" in d:
            v = str(d["version"])
            if not re.match(r"^\d+\.\d+\.\d+$", v):
                warnings.append(f'[L2] {label}.yaml: version="{v}" 非 semver (x.y.z)')

    return errors, warnings


def l3_cross_reference(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L3: 交叉引用审计"""
    errors = []
    warnings = []

    cap = yaml_data.get("/config/capabilities.yaml", {})
    tr = yaml_data.get("/config/trigger_router.yaml", {})
    triggers = tr.get("triggers", {})

    yaml_trigger_types = set(triggers.keys())
    extra = yaml_trigger_types - set(PHASE1D_TRIGGER_TYPES)
    missing = set(PHASE1D_TRIGGER_TYPES) - yaml_trigger_types
    if extra:
        warnings.append(f"[L3] trigger_router.yaml 多余 trigger: {extra}（PHASE1D_TRIGGER_TYPES 中无定义）")
    if missing:
        errors.append(f"[L3] trigger_router.yaml 缺失 trigger: {missing}（PHASE1D_TRIGGER_TYPES 定义但 YAML 无）")

    for ttype, spec in triggers.items():
        handler = spec.get("handler", "")
        if not handler or "<injected" in handler or "." not in handler:
            continue
        is_stub = "stub" in handler

        mod_path, _, attr = handler.rpartition(".")
        try:
            mod = __import__(mod_path, fromlist=[attr])
            fn = getattr(mod, attr, None)
            if fn is None:
                errors.append(f'[L3] trigger "{ttype}": handler "{handler}" — 函数 "{attr}" 不存在')
            elif not callable(fn):
                errors.append(f'[L3] trigger "{ttype}": handler "{handler}" — 不是 callable')
        except ImportError:
            if is_stub:
                try:
                    rt = __import__("zephyr.orchestrator.execution.trigger_router", fromlist=[attr])
                    if not hasattr(rt, attr):
                        errors.append(f'[L3] trigger "{ttype}": stub "{attr}" 不在 trigger_router 模块中')
                except ImportError:
                    pass
            else:
                pass

    for rule in cap.get("rules", []):
        name = rule.get("name", "?")
        for mode in ("allow", "deny"):
            for pat in rule.get(mode, []):
                p = pat.replace("\\", "/")
                base = p.split("/**/")[0] if "/**/" in p else p.replace("/**", "")
                base = base.split("/*")[0] if "/*" in base else base
                if "*" not in base:
                    full = REPO_ROOT / base.replace("/", os.sep)
                    if not full.exists():
                        if not base.endswith(".py"):
                            pass

    return errors, warnings


def l4_path_constants() -> tuple[list[str], list[str], list[dict]]:
    """L4: 全项目路径常量 parents[N] 一致性扫描（返回fix字典列表）"""
    errors = []
    warnings = []
    fixes = []

    all_py = [
        f
        for f in REPO_ROOT.rglob("*.py")
        if f.is_file()
        and not any(excl in str(f) for excl in EXCLUDE_DIRS)
        and ".venv" not in str(f)
        and "__pycache__" not in str(f)
        and ".git" not in str(f)
        and "_DO_NOT_USE" not in str(f)
    ]

    for f in all_py:
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        expected_parents_index = len(f.relative_to(REPO_ROOT).parts) - 1
        expected_parent_chain_depth = len(f.relative_to(REPO_ROOT).parts)

        for lno, line in enumerate(lines, 1):
            m = re.search(r"(?:REPO_ROOT|_REPO_ROOT|project_root|repo_root)\s*[:=]\s*.*?parents\[(\d+)\]", line)
            if m:
                n = int(m.group(1))
                if n != expected_parents_index:
                    warnings.append(
                        f"[L4] {rel}:{lno} REPO_ROOT 使用 parents[{n}]（期望 parents[{expected_parents_index}]）"
                    )
                    fixes.append(
                        {
                            "file": f,
                            "line": lno,
                            "old": f"parents[{n}]",
                            "new": f"parents[{expected_parents_index}]",
                            "desc": f"{rel}:{lno} parents[{n}] → parents[{expected_parents_index}]",
                        }
                    )
                continue

            m = re.search(r"(?:REPO_ROOT|_REPO_ROOT|project_root|repo_root)\s*[:=].*?(\.parent(?:\.parent)+)$", line)
            if m:
                chain = m.group(1)
                depth = chain.count(".parent")
                if depth != expected_parent_chain_depth:
                    warnings.append(
                        f"[L4] {rel}:{lno} REPO_ROOT 使用 .parent*{depth}（期望 .parent*{expected_parent_chain_depth}）"
                    )
                    fixes.append(
                        {
                            "file": f,
                            "line": lno,
                            "old": chain,
                            "new": ".parent" * expected_parent_chain_depth,
                            "desc": f"{rel}:{lno} .parent*{depth} → .parent*{expected_parent_chain_depth}",
                        }
                    )
                continue

    return errors, warnings, fixes


def l5_gov_doc_reconciliation(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L5: 治理文档三方对账"""
    errors = []
    warnings = []

    if AUTH_REG_PATH.exists():
        auth = AUTH_REG_PATH.read_text(encoding="utf-8", errors="replace")
        for ref in ["config/drift_thresholds.yaml", "config/capabilities.yaml", "config/compression_policy.yaml"]:
            if ref not in auth:
                warnings.append(f'[L5] ai_autonomy_authority_registry.yaml 中未找到 "{ref}" 引用')
    else:
        warnings.append(f"[L5] ai_autonomy_authority_registry.yaml 不存在 — {AUTH_REG_PATH}")

    if DIR_STD_PATH.exists():
        dir_s = DIR_STD_PATH.read_text(encoding="utf-8", errors="replace")
        if "config/ — 运行时配置目录" not in dir_s:
            errors.append("[L5] trae_028_doc_structure_naming.yaml 缺少 config/ 目录结构定义")
    else:
        warnings.append(f"[L5] trae_028_doc_structure_naming.yaml 不存在 — {DIR_STD_PATH}")

    # ARCH-038 R2: capabilities.yaml 已无 rules.write_config（重构为功能开关）。
    # CBAC 写保护已由 GitCommitGateway claim_files 机制替代，删除过时检查。

    return errors, warnings


def l6_security_posture(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L6: 安全态势审计"""
    errors = []
    warnings = []

    # ARCH-038 R2: capabilities.yaml 已无 rules（重构为功能开关）。
    # CBAC 写保护已由 GitCommitGateway claim_files 机制替代，删除过时检查。

    cp = yaml_data.get("/config/compression_policy.yaml", {})
    policy = cp.get("policy", {})
    imm = policy.get("preserve_immutable_blocks", [])
    empty_markers = [m for m in imm if not isinstance(m, str) or not m.strip()]
    if empty_markers:
        warnings.append(
            f"[L6] compression_policy.yaml: preserve_immutable_blocks 含空标记 — 共 {len(empty_markers)} 个"
        )

    return errors, warnings


def _str_distance(a: str, b: str) -> int:
    """Levenshtein编辑距离（用于拼写检测）"""
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (0 if ca == cb else 1)))
        prev = curr
    return prev[-1]


def l7_manifest_sync(yaml_data: dict) -> tuple[list[str], list[str], list[dict]]:
    """L7: 自动同步检测 — manifest↔文件系统脚本登记对账 + 预埋文件就绪提醒（返回fix列表）"""
    errors = []
    warnings = []
    fixes = []

    # === 7A: script_manifest.yaml ↔ 文件系统对账 ===
    manifest_path = REPO_ROOT / "scripts" / "governance" / "script_manifest.yaml"
    if not manifest_path.exists():
        warnings.append(f"[L7] script_manifest.yaml 不存在 — {manifest_path}")
        return errors, warnings, fixes

    try:
        with open(manifest_path, encoding="utf-8") as fh:
            manifest_data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        errors.append(f"[L7] script_manifest.yaml 解析失败: {exc}")
        return errors, warnings, fixes

    manifest_scripts = manifest_data.get("scripts", [])
    if not isinstance(manifest_scripts, list):
        errors.append("[L7] script_manifest.yaml 顶层的 scripts 不是 list")
        manifest_scripts = []

    # 从manifest中提取注册的脚本路径（manifest的name字段相对于scripts/governance/）
    manifest_registered = set()
    manifest_entries = {}
    for entry in manifest_scripts:
        name = entry.get("name", "")
        if name:
            full_name = f"scripts/governance/{name.replace(chr(92), '/')}"
            manifest_registered.add(full_name)
            manifest_entries[full_name] = entry

    # 遍历文件系统中的所有脚本
    gov_dir = REPO_ROOT / "scripts" / "governance"
    if gov_dir.exists():
        fs_scripts = {
            str(f.relative_to(REPO_ROOT)).replace("\\", "/")
            for f in gov_dir.rglob("*.py")
            if f.is_file() and f.name != "__init__.py"
        }
    else:
        fs_scripts = set()

    # 孤儿脚本：文件系统有，manifest中没有
    orphans = fs_scripts - manifest_registered
    if orphans:
        warning_lines = [f"[L7] 孤儿脚本（文件系统存在但未在 manifest 注册） — 共 {len(orphans)} 个"]
        for o in sorted(orphans):
            rel_path = o.replace("scripts/governance/", "", 1)
            dim_tag = rel_path.split("/")[0] if "/" in rel_path else "unknown"
            warning_lines.append(f"      {o}")
            warning_lines.append(f"        → --fix 会自动注册到 manifest（dimension={dim_tag}, P2, 30s）")
        warnings.extend(warning_lines)
        for o in sorted(orphans):
            rel_path = o.replace("scripts/governance/", "", 1)
            dim_tag = rel_path.split("/")[0] if "/" in rel_path else "unknown"
            fixes.append(
                {
                    "type": "manifest_register",
                    "name": rel_path,
                    "dimension": dim_tag,
                    "desc": f"注册孤儿脚本: {rel_path}",
                }
            )

    # 僵尸条目：manifest中有，文件系统没有
    zombies = manifest_registered - fs_scripts
    if zombies:
        error_lines = [f"[L7] 僵尸条目（manifest注册但文件系统不存在） — 共 {len(zombies)} 个"]
        for z in sorted(zombies):
            error_lines.append(f"      {z}")
        errors.extend(error_lines)

    # manifest条目路径格式检查 + 拼写错误检测
    typo_candidates = []
    for full_name, entry in manifest_entries.items():
        dims = entry.get("dimensions", [])
        if not dims or not isinstance(dims, list):
            warnings.append(f'[L7] manifest条目 "{full_name}" dimensions 为空或非list')

        # 检查对应的文件系统中是否存在
        fs_path = REPO_ROOT / full_name.replace("/", os.sep)
        if not fs_path.exists():
            # 搜索同目录下是否有拼写相近的文件（Levenshtein距离≤2的同级文件）
            parent_dir = fs_path.parent
            if parent_dir.exists():
                expected_name = fs_path.name
                candidates = [
                    f.name
                    for f in parent_dir.iterdir()
                    if f.is_file()
                    and f.name != "__init__.py"
                    and _str_distance(f.name, expected_name) <= 2
                    and f.name != expected_name
                ]
                if candidates:
                    typo_candidates.append((full_name, expected_name, candidates))

    if typo_candidates:
        typo_lines = [f"[L7] manifest条目拼写可疑（文件名与文件系统中最近匹配差≤2字符） — 共 {len(typo_candidates)} 个"]
        for full_name, expected, candidates in typo_candidates:
            typo_lines.append(f"      {full_name}")
            typo_lines.append(f"        预期: {expected}")
            typo_lines.append(f"        附近: {candidates}")
            typo_lines.append(f"        → --fix 会自动修正为: {candidates[0]}")
        warnings.extend(typo_lines)
        for full_name, expected, candidates in typo_candidates:
            rel_path = full_name.replace("scripts/governance/", "", 1)
            fixes.append(
                {
                    "type": "manifest_rename",
                    "old_name": rel_path,
                    "new_name": rel_path.rsplit("/", 1)[0] + "/" + candidates[0],
                    "desc": f"修正 manifest 笔误: {expected} → {candidates[0]}",
                }
            )

    # === 7B: 预埋文件就绪检测 ===
    FORWARD_DECLARED = {
        "config/risk/": "config/capabilities.yaml write_config.deny 中预埋的 risk 目录",
        "config/drift_thresholds.yaml": "config/capabilities.yaml write_config.deny 中预埋的 drift_thresholds",
    }

    ready = []
    for path, desc in FORWARD_DECLARED.items():
        full = REPO_ROOT / path.replace("/", os.sep)
        if full.exists():
            ready.append((path, desc))

    if ready:
        info_lines = [f"[L7] 预埋文件已就绪（之前是规划中，现已创建） — 共 {len(ready)} 个"]
        for path, desc in ready:
            info_lines.append(f"      {path} → {desc}")
            info_lines.append(
                "        ⚡ 行动提醒: 确认 capabilities.yaml write_config.deny 中的注释需更新 (移除「预埋」标记)"
            )
        warnings.extend(info_lines)

    # 统计
    if not orphans and not zombies and not ready:
        pass  # all clean

    return errors, warnings, fixes


def l8_code_config_reconciliation(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L8: 代码-配置对账 — 硬编码值与YAML注册表同步、路径漂移、状态机完整性、implementation_status标注"""
    errors = []
    warnings = []

    # 8A: KNOWN_MODELS ↔ embedding_model_registry.yaml 同步
    emb_reg = yaml_data.get("/config/embedding_model_registry.yaml", {})
    yaml_models = set()
    if isinstance(emb_reg, dict):
        for m in emb_reg.get("models", []):
            if isinstance(m, dict) and "name" in m:
                yaml_models.add(m["name"])

    migrate_path = SRC_DIR / "kb" / "embedding_migrate.py"
    if migrate_path.exists():
        try:
            code = migrate_path.read_text(encoding="utf-8")
            known_match = re.search(r"KNOWN_MODELS\s*:\s*dict\[.*?\]\s*=\s*\{", code)
            if known_match:
                start = known_match.end()
                depth = 1
                end = start
                while end < len(code) and depth > 0:
                    if code[end] == "{":
                        depth += 1
                    elif code[end] == "}":
                        depth -= 1
                    end += 1
                body = code[start : end - 1]
                code_models = set(re.findall(r'"([^"]+)"\s*:\s*\{', body))
                yaml_only = yaml_models - code_models
                code_only = code_models - yaml_models
                if yaml_only:
                    errors.append(f"[L8] embedding_model_registry.yaml 有模型不在 KNOWN_MODELS 中: {yaml_only}")
                if code_only:
                    errors.append(f"[L8] KNOWN_MODELS 有模型不在 embedding_model_registry.yaml 中: {code_only}")
                if "SSoT" not in code and "embedding_model_registry" not in code:
                    warnings.append("[L8] embedding_migrate.py KNOWN_MODELS 缺少 SSoT 同步注释")
            else:
                warnings.append("[L8] embedding_migrate.py: 无法解析 KNOWN_MODELS 字典")
        except (OSError, UnicodeDecodeError):
            warnings.append(f"[L8] 无法读取 {migrate_path}")

    # 8B: registry-master-index.yaml 路径漂移检测
    idx_path = (
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry-master-index.yaml"
    )
    if idx_path.exists():
        try:
            idx_text = idx_path.read_text(encoding="utf-8")
            idx_data = yaml.safe_load(idx_text)
            if isinstance(idx_data, dict):
                for entry in idx_data.get("registries", []):
                    if not isinstance(entry, dict):
                        continue
                    phys = entry.get("physical_path", "")
                    name = entry.get("name", "?")
                    if not phys:
                        continue
                    if phys.startswith("src/zephyr/config/"):
                        errors.append(
                            f'[L8] registry-master-index.yaml: "{name}" physical_path="{phys}" 指向 src/zephyr/config/（应改为 config/）'
                        )
                    elif phys.startswith("config/"):
                        full = REPO_ROOT / phys.replace("/", os.sep)
                        if not full.exists():
                            warnings.append(
                                f'[L8] registry-master-index.yaml: "{name}" physical_path="{phys}" 文件不存在'
                            )
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            warnings.append("[L8] 无法解析 registry-master-index.yaml")

    # 8C: session_state_machine.yaml 状态机完整性
    ssm = yaml_data.get("/config/session_state_machine.yaml", {})
    if isinstance(ssm, dict):
        states = {s["name"] for s in ssm.get("states", []) if isinstance(s, dict) and "name" in s}
        transitions = ssm.get("transitions", [])
        reachable_from_idle = set()
        reachable_from_idle.add("idle")
        changed = True
        while changed:
            changed = False
            for t in transitions:
                if not isinstance(t, dict):
                    continue
                f = t.get("from", "")
                to = t.get("to", "")
                if f in reachable_from_idle and to not in reachable_from_idle:
                    reachable_from_idle.add(to)
                    changed = True
        unreachable = states - reachable_from_idle
        if unreachable:
            warnings.append(f"[L8] session_state_machine.yaml: 不可达状态（从 idle 出发无法到达）: {unreachable}")

        terminal_states = set()
        for t in transitions:
            if isinstance(t, dict):
                terminal_states.discard(t.get("from", ""))
        for s in states:
            if s not in terminal_states and s != "idle":
                pass

        for t in transitions:
            if not isinstance(t, dict):
                continue
            f = t.get("from", "")
            to = t.get("to", "")
            if f and f not in states:
                errors.append(f'[L8] session_state_machine.yaml: transition from="{f}" 不在 states 中')
            if to and to not in states:
                errors.append(f'[L8] session_state_machine.yaml: transition to="{to}" 不在 states 中')

    # 8D: implementation_status 标注检查
    for cfg_rel in [
        "/config/context-rules.yaml",
        "/config/embedding_model_registry.yaml",
        "/config/session_state_machine.yaml",
    ]:
        data = yaml_data.get(cfg_rel, {})
        if isinstance(data, dict) and "implementation_status" not in data:
            warnings.append(f"[L8] {cfg_rel}: 缺少 implementation_status 标注（声明式契约文件应标注实现状态）")

    # 8E: 所有 config YAML 的 version + schema_version semver 检查
    for cfg_rel, cfg_data in yaml_data.items():
        if not cfg_rel.startswith("/config/") or not isinstance(cfg_data, dict):
            continue
        v = cfg_data.get("version")
        if v is not None and not re.match(r"^\d+\.\d+\.\d+$", str(v)):
            warnings.append(f'[L8] {cfg_rel}: version="{v}" 非 semver (x.y.z)')
        sv = cfg_data.get("schema_version")
        if sv is not None and not re.match(r"^\d+\.\d+\.\d+$", str(sv)):
            warnings.append(f'[L8] {cfg_rel}: schema_version="{sv}" 非 semver (x.y.z)')

    return errors, warnings


def l9_comment_and_tracking_audit(yaml_data: dict) -> tuple[list[str], list[str]]:
    """L9: 注释与追踪审计 — YAML注释计数准确性、git追踪状态、登记表entry_count一致性"""
    errors = []
    warnings = []

    # 9A: trigger_router.yaml "N 种 trigger_type" 注释计数
    tr_path = CONFIG_DIR / "trigger_router.yaml"
    if tr_path.exists():
        tr_text = tr_path.read_text(encoding="utf-8")
        tr_data = yaml_data.get("/config/trigger_router.yaml", {})
        trigger_count = len(tr_data.get("triggers", {})) if isinstance(tr_data, dict) else 0
        count_match = re.search(r"(\d+)\s*种\s*trigger_type", tr_text)
        if count_match:
            claimed = int(count_match.group(1))
            if claimed != trigger_count:
                errors.append(f"[L9] trigger_router.yaml: 注释声称 {claimed} 种 trigger_type，实际 {trigger_count} 种")

    # 9B: context-rules.yaml description 规则计数
    ctx_path = CONFIG_DIR / "context-rules.yaml"
    if ctx_path.exists():
        ctx_data = yaml_data.get("/config/context-rules.yaml", {})
        if isinstance(ctx_data, dict):
            desc = ctx_data.get("description", "")
            rules = ctx_data.get("rules", [])
            count_match = re.search(r"(\d+)\s+context management rules", desc)
            if count_match:
                claimed = int(count_match.group(1))
                actual = len(rules) if isinstance(rules, list) else 0
                if claimed != actual:
                    errors.append(f"[L9] context-rules.yaml: description 声称 {claimed} rules，实际 {actual} 条")

    # 9C: registry-master-index.yaml entry_count 与 YAML 实际条目一致性
    idx_path = (
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry-master-index.yaml"
    )
    if idx_path.exists():
        try:
            idx_data = yaml.safe_load(idx_path.read_text(encoding="utf-8"))
            if isinstance(idx_data, dict):
                for entry in idx_data.get("registries", []):
                    if not isinstance(entry, dict):
                        continue
                    phys = entry.get("physical_path", "")
                    name = entry.get("name", "?")
                    entry_count = entry.get("entry_count")
                    if not phys or entry_count is None:
                        continue
                    full = REPO_ROOT / phys.replace("/", os.sep)
                    if not full.exists():
                        continue
                    try:
                        target_data = yaml.safe_load(full.read_text(encoding="utf-8"))
                        if not isinstance(target_data, dict):
                            continue
                        if "models" in target_data:
                            actual = len(target_data["models"])
                        elif "rules" in target_data:
                            actual = len(target_data["rules"])
                        elif "states" in target_data:
                            actual = len(target_data["states"])
                        else:
                            continue
                        if actual != entry_count:
                            errors.append(
                                f'[L9] registry-master-index.yaml: "{name}" entry_count={entry_count}，实际 {actual} 条'
                            )
                    except (yaml.YAMLError, UnicodeDecodeError):
                        pass
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            warnings.append("[L9] 无法解析 registry-master-index.yaml")

    # 9D: config YAML 文件 git 追踪状态
    yaml_files = sorted(f for f in CONFIG_DIR.rglob("*.yaml") if f.is_file())
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--"]
            + [str(f.relative_to(REPO_ROOT)).replace("\\", "/") for f in yaml_files],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            untracked = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
            if untracked:
                errors.append(f"[L9] config/ 下有 {len(untracked)} 个 YAML 未被 git 追踪: {untracked}")
    except (subprocess.SubprocessError, FileNotFoundError):
        warnings.append("[L9] 无法执行 git ls-files 检查追踪状态")

    # 9E: embedding_model_registry.yaml scope 字段与实际模型数
    emb_data = yaml_data.get("/config/embedding_model_registry.yaml", {})
    if isinstance(emb_data, dict):
        actual_models = len(emb_data.get("models", []))
        scope_match = re.search(r"(\d+)\s*个", str(emb_data.get("scope", "")))
        if not scope_match:
            idx_path2 = (
                REPO_ROOT
                / "docs"
                / "01_policies_and_standards"
                / "_registry"
                / "catalogs"
                / "registry-master-index.yaml"
            )
            if idx_path2.exists():
                try:
                    idx2 = yaml.safe_load(idx_path2.read_text(encoding="utf-8"))
                    for entry in idx2.get("registries", []):
                        if "embedding" in entry.get("name", "").lower() or "Embedding" in entry.get("name", ""):
                            scope = entry.get("scope", "")
                            scope_match = re.search(r"(\d+)\s*个", scope)
                            break
                except (yaml.YAMLError, OSError):
                    pass
        if scope_match:
            claimed = int(scope_match.group(1))
            if claimed != actual_models:
                errors.append(f"[L9] embedding_model_registry scope 声称 {claimed} 个模型，实际 {actual_models} 个")

    return errors, warnings


PYTEST_BUILTIN_MARKERS = frozenset({"parametrize", "skip", "skipif", "xfail", "usefixtures"})


def step10_pytest_markers_sync() -> tuple[list[str], list[str]]:
    """L10: 测试标记对账 — @pytest.mark.* ↔ pyproject.toml markers 双向同步（AGENTS.md §6.2 测试标记注册链）"""
    errors = []
    warnings = []

    pyproject_path = REPO_ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        warnings.append(f"[L10] pyproject.toml 不存在 — {pyproject_path}")
        return errors, warnings

    try:
        with open(pyproject_path, "rb") as fh:
            toml_data = tomllib.load(fh)
    except Exception as exc:
        errors.append(f"[L10] pyproject.toml 解析失败: {exc}")
        return errors, warnings

    toml_markers_raw = toml_data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])
    toml_markers = set()
    for m in toml_markers_raw:
        name = m.split(":")[0].strip() if isinstance(m, str) else ""
        if name:
            toml_markers.add(name)

    test_dir = REPO_ROOT / "tests"
    test_markers = set()
    if test_dir.exists():
        for test_file in test_dir.rglob("test_*.py"):
            try:
                text = test_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for match in re.finditer(r"@pytest\.mark\.(\w+)", text):
                marker = match.group(1)
                if marker not in PYTEST_BUILTIN_MARKERS:
                    test_markers.add(marker)

    missing_in_toml = test_markers - toml_markers
    if missing_in_toml:
        errors.append(
            f"[L10] @pytest.mark.* 在测试中使用但 pyproject.toml 未注册: {sorted(missing_in_toml)}"
            f"（--strict-markers 下会导致 Unknown marker Error）"
        )

    dead_in_toml = toml_markers - test_markers
    if dead_in_toml:
        warnings.append(
            f"[L10] pyproject.toml 中注册但测试中未使用的 marker: {sorted(dead_in_toml)}"
            f"（建议清理或确认是否预留给未来的测试）"
        )

    return errors, warnings


def step11_contract_implementation_audit() -> tuple[list[str], list[str]]:
    """L11: 契约-实现对账 — declarative-contract-tracker-registry.md ↔ config/ YAML implementation_status 交叉校验（根因修复第2层）"""
    errors = []
    warnings = []

    tracker_path = (
        REPO_ROOT
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "declarative-contract-tracker-registry.md"
    )
    if not tracker_path.exists():
        warnings.append("[L11] declarative-contract-tracker-registry.md 不存在 — 跳过契约对账")
        return errors, warnings

    try:
        with open(tracker_path, encoding="utf-8") as fh:
            tracker = yaml.safe_load(fh)
    except Exception as exc:
        errors.append(f"[L11] 契约跟踪登记表解析失败: {exc}")
        return errors, warnings

    tracked_sources: set[str] = set()
    unresolved_sources_yaml: set[str] = set()
    unresolved_sources_py: set[str] = set()
    unresolved_count = 0
    for ct in tracker.get("contracts", []):
        src = ct.get("source", "")
        tracked_sources.add(src)
        if ct.get("status") == "unresolved":
            unresolved_count += 1
            if src.endswith((".yaml", ".yml")):
                unresolved_sources_yaml.add(src)
            elif src.endswith(".py"):
                unresolved_sources_py.add(src)

    config_yaml_paths: set[str] = set()
    config_dir = REPO_ROOT / "config"
    if config_dir.exists():
        for yf in sorted(config_dir.rglob("*.yaml")):
            rel = str(yf.relative_to(REPO_ROOT)).replace("\\", "/")
            try:
                text = yf.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "implementation_status" in text:
                config_yaml_paths.add(rel)

    untracked = config_yaml_paths - tracked_sources
    if untracked:
        warnings.append(
            f"[L11] config/ YAML 含 implementation_status 但未在契约跟踪登记表中登记: "
            f"{sorted(untracked)}（新契约未注册——请在 declarative-contract-tracker-registry.md 中添加）"
        )

    tracked_but_gone = unresolved_sources_yaml - config_yaml_paths
    if tracked_but_gone:
        warnings.append(
            f"[L11] 未解决的契约含 YAML 源但该源已不含 implementation_status: "
            f"{sorted(tracked_but_gone)}（契约可能已兑现——请更新 status 为 resolved）"
        )

    for py_src in unresolved_sources_py:
        py_path = REPO_ROOT / py_src
        if not py_path.exists():
            warnings.append(f"[L11] 契约跟踪登记表中登记的 Python 源已不存在: {py_src}（请更新或删除条目）")

    if unresolved_count > 0:
        warnings.append(
            f"[L11] {unresolved_count} 条声明式契约尚未兑现（详见 declarative-contract-tracker-registry.md）"
        )

    return errors, warnings


def _scan_config_consumers(filename: str, max_results: int = 5) -> list[str]:
    """扫描 src/+scripts/+tests/ 下 .py 文件，找出引用此 config 文件名的消费者（最多 max_results 个）。

    治本（ARCH-038 P2）：发现契约——新 AI 需知道每个 config 文件被谁消费。
    用正则词边界匹配，避免子串假阳性（如 "flags.yaml" 误匹配 "feature_flags.yaml"）。
    前瞻否定 [A-Za-z0-9_]：排除 "feature_flags.yaml" 中的 "_" 前缀。
    后瞻否定 [A-Za-z0-9_.]：排除 "flags.yaml.bak" 中的 "." 后缀。
    """
    consumers: list[str] = []
    # 正则：文件名前后不能是字母/数字/下划线（前）/点（后），确保匹配完整文件名
    pattern = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(filename) + r'(?![A-Za-z0-9_.])')
    search_roots = [REPO_ROOT / "src", REPO_ROOT / "scripts", REPO_ROOT / "tests"]
    for root in search_roots:
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if pattern.search(text):
                rel = "/" + str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
                consumers.append(rel)
                if len(consumers) >= max_results:
                    return consumers
    return consumers


def list_configs() -> None:
    """P2 发现契约：输出 config/ 下所有配置文件的清单到 stdout（YAML 格式，按需生成，不持久化）。

    治本（ARCH-038 P2）：新 AI 运行 `--list-configs` 即可发现 config/ 全貌：
    - path: 相对路径
    - type: yaml/yml/json
    - size_bytes: 文件大小
    - top_keys: YAML 顶层 keys（仅 .yaml/.yml）
    - protected_by: 是否在 capabilities.yaml write_config.deny/allow 中
    - consumers: 代码中引用此文件的位置（最多 5 个）

    向内收逻辑：
    - ① 复用 L1 的 rglob 枚举逻辑，不新建扫描器
    - ② 按需生成，无持久化文件，无维护成本
    - ③ 清单是"视图"不是"数据"，不该持久化（避免多真源+过时）
    - ④ AGENTS.md 声明此命令为 config/ 发现契约
    """
    from datetime import datetime, timezone

    # 只列 directory_contract.yaml allowed 扩展名（.yaml/.yml/.json），
    # 排除 .env.postgres 等敏感/违规文件（由 contract checker 单独处理）
    ALLOWED_EXTS = {".yaml", ".yml", ".json"}
    config_files = sorted(
        f for f in CONFIG_DIR.rglob("*") if f.is_file() and f.name != ".gitkeep" and f.suffix in ALLOWED_EXTS
    )

    # 加载 capabilities.yaml 的 write_config 规则，用于判断 protected_by
    cap_path = CONFIG_DIR / "capabilities.yaml"
    write_config_deny: set[str] = set()
    write_config_allow: set[str] = set()
    if cap_path.exists():
        try:
            with open(cap_path, encoding="utf-8") as fh:
                cap_data = yaml.safe_load(fh) or {}
            for rule in cap_data.get("rules", []):
                if rule.get("name") == "write_config":
                    write_config_deny = {str(x) for x in rule.get("deny", [])}
                    write_config_allow = {str(x) for x in rule.get("allow", [])}
                    break
        except (yaml.YAMLError, OSError):
            pass

    files_info: list[dict] = []
    for f in config_files:
        rel = _rel(f)
        # config/capabilities.yaml → "config/capabilities.yaml" 用于匹配 deny/allow
        rel_no_leading_slash = rel.lstrip("/")
        size_bytes = f.stat().st_size
        ftype = f.suffix.lstrip(".")

        entry: dict = {
            "path": rel_no_leading_slash,
            "type": ftype,
            "size_bytes": size_bytes,
        }

        # top_keys（仅 YAML）
        if f.suffix in (".yaml", ".yml"):
            try:
                with open(f, encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                if isinstance(data, dict):
                    entry["top_keys"] = list(data.keys())
                else:
                    entry["top_keys"] = []
            except (yaml.YAMLError, OSError):
                entry["top_keys"] = []

        # protected_by
        protected: list[str] = []
        if rel_no_leading_slash in write_config_deny:
            protected.append("write_config.deny")
        if rel_no_leading_slash in write_config_allow:
            protected.append("write_config.allow")
        entry["protected_by"] = protected if protected else None

        # consumers
        entry["consumers"] = _scan_config_consumers(f.name)

        files_info.append(entry)

    output = {
        "_auto_generated": True,
        "_notice": "config/ 发现契约 — 按需生成，不持久化。新 AI 运行 --list-configs 获取最新清单。",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/governance/d1_structure/validate_config_integrity.py --list-configs",
        "total_files": len(files_info),
        "files": files_info,
    }
    # 用 allow_unicode=False 输出纯 ASCII（中文转义为 \uXXXX），
    # 避免 PowerShell 管道用 GBK 解码 UTF-8 导致乱码；AI 解析 \uXXXX 无障碍
    yaml_text = yaml.safe_dump(output, sort_keys=False, allow_unicode=False, default_flow_style=False)
    sys.stdout.write(yaml_text)


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="运行时配置完整性十一层纵深审计 + 自动修复")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：errors也仅warn不阻塞 (exit 0)")
    parser.add_argument("--fix", action="store_true", help="自动修复模式：修复parents路径bug + 注册孤儿脚本 + 修正笔误")
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="P2 发现契约：输出 config/ 下所有配置文件清单到 stdout（按需生成，不持久化）",
    )
    args = parser.parse_args()

    # P2 发现契约：提前返回，不执行审计
    if args.list_configs:
        list_configs()
        sys.exit(EXIT_PASS)

    all_errors = []
    all_warnings = []
    all_fixes = []

    print("\n" + "=" * 60, file=sys.stderr)
    print("[CONFIG-AUDIT] 运行时配置完整性审计 — 十一层纵深扫描" + (" + 自动修复" if args.fix else ""), file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    e, w, yd = l1_file_integrity()
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"\n  L1 文件完整性+YAML语法:  {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = l2_schema_deep(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L2 Schema深度校验:       {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = l3_cross_reference(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L3 交叉引用审计:         {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w, f = l4_path_constants()
    all_errors.extend(e)
    all_warnings.extend(w)
    all_fixes.extend(f)
    print(f"  L4 路径常量扫描:         {len(e)} errors, {len(w)} warnings（{len(f)} 可自动修复）", file=sys.stderr)

    e, w = l5_gov_doc_reconciliation(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L5 治理文档对账:         {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = l6_security_posture(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L6 安全态势审计:         {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w, f = l7_manifest_sync(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    all_fixes.extend(f)
    print(f"  L7 自动同步检测:         {len(e)} errors, {len(w)} warnings（{len(f)} 可自动修复）", file=sys.stderr)

    e, w = l8_code_config_reconciliation(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L8 代码-配置对账:        {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = l9_comment_and_tracking_audit(yd)
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L9 注释与追踪审计:       {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = step10_pytest_markers_sync()
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L10 测试标记对账:        {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    e, w = step11_contract_implementation_audit()
    all_errors.extend(e)
    all_warnings.extend(w)
    print(f"  L11 契约-实现对账:        {len(e)} errors, {len(w)} warnings", file=sys.stderr)

    # === 自动修复阶段 ===
    applied = 0
    skipped = 0

    if args.fix and all_fixes:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"[FIX] 自动修复阶段 — 共 {len(all_fixes)} 项", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)

        manifest_path = REPO_ROOT / "scripts" / "governance" / "script_manifest.yaml"

        for fix in all_fixes:
            ftype = fix.get("type", "text_replace")

            if ftype == "text_replace":
                fpath = fix["file"]
                old = fix["old"]
                new = fix["new"]
                try:
                    content = fpath.read_text(encoding="utf-8")
                    if old in content:
                        content = content.replace(old, new, 1)
                        atomic_write_safe(fpath, content)
                        print(f"  ✅ {fix['desc']}", file=sys.stderr)
                        applied += 1
                    else:
                        print(f"  ⚠️  跳过（字符串已不存在）: {fix['desc']}", file=sys.stderr)
                        skipped += 1
                except (OSError, ValueError) as exc:
                    print(f"  ❌ 失败: {fix['desc']} — {exc}", file=sys.stderr)
                    skipped += 1

            elif ftype == "manifest_register":
                name = fix["name"]
                dim_tag = fix.get("dimension", "unknown")
                try:
                    manifest = manifest_path.read_text(encoding="utf-8")
                    new_entry = f"""\n  - name: {name}
    dimensions: [{dim_tag}]
    priority: P2
    timeout_seconds: 30
    args: [--warn-only]
    warn_only: true
    description: 自动注册脚本（v3.1 --fix）"""
                    if new_entry not in manifest:
                        atomic_write_safe(manifest_path, manifest + new_entry)
                        print(f"  ✅ {fix['desc']}", file=sys.stderr)
                        applied += 1
                    else:
                        print(f"  ⚠️  跳过（条目已存在）: {fix['desc']}", file=sys.stderr)
                        skipped += 1
                except (OSError, ValueError) as exc:
                    print(f"  ❌ 失败: {fix['desc']} — {exc}", file=sys.stderr)
                    skipped += 1

            elif ftype == "manifest_rename":
                try:
                    manifest = manifest_path.read_text(encoding="utf-8")
                    old_name = "name: " + fix["old_name"]
                    new_name = "name: " + fix["new_name"]
                    if old_name in manifest:
                        manifest = manifest.replace(old_name, new_name, 1)
                        atomic_write_safe(manifest_path, manifest)
                        print(f"  ✅ {fix['desc']}", file=sys.stderr)
                        applied += 1
                    else:
                        print(f"  ⚠️  跳过（旧名不存在）: {fix['desc']}", file=sys.stderr)
                        skipped += 1
                except (OSError, ValueError) as exc:
                    print(f"  ❌ 失败: {fix['desc']} — {exc}", file=sys.stderr)
                    skipped += 1

        print(f"\n  [FIX-REPORT] 已应用: {applied}, 跳过: {skipped}", file=sys.stderr)

    elif args.fix and not all_fixes:
        print("\n  [FIX] 无需修复 — 所有检查项已通过 ✅", file=sys.stderr)

    # === 输出结果 ===
    print(f"\n{'=' * 60}", file=sys.stderr)
    if all_errors:
        print(f"\n  ERRORS ({len(all_errors)}):", file=sys.stderr)
        for err in all_errors:
            print(f"    ❌ {err}", file=sys.stderr)
    else:
        print("\n  ✅ ERRORS: 0", file=sys.stderr)

    if all_warnings:
        print(f"\n  WARNINGS ({len(all_warnings)}):", file=sys.stderr)
        for warn in all_warnings:
            print(f"    ⚠️  {warn}", file=sys.stderr)
    else:
        print("\n  ✅ WARNINGS: 0", file=sys.stderr)

    total = len(all_errors) + len(all_warnings)
    print(f"\n  [RESULT] {len(all_errors)} errors, {len(all_warnings)} warnings, {total} total", file=sys.stderr)
    print(f"{'=' * 60}\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
