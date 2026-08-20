# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.secret_hardcode_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates._diff_helpers; zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py/.yaml/.yml/.json/.toml 文件 added 行含硬编码密钥/Token/凭证（sk-/AKIA/ghp_/KEY="value" 等）时阻断 commit（passed=False）；tests/ 豁免（真源：commit_gate_registry.is_test_exempt）；.env.example 豁免；密钥扫描脚本自身豁免（含模式字面量）；docstring/注释/import 行豁免（.py via _diff_helpers）；git diff 不可达 fail-open（logger.warning）；检出违规则 fail-closed（passed=False）
# [MODIFY-GUARD] gate_id="NO-SECRET-HARDCODE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_secret_hardcode_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""secret_hardcode_gate.py — 密钥值硬编码阻断门禁（NO-SECRET-HARDCODE，#ARCH-SECRETS-GOV-001 Phase 3）

检测 staged 文件 added 行中的硬编码密钥/Token/凭证——与 NO-BARE-GETENV(81) 互补：
  - NO-BARE-GETENV 检测"读密钥方式违规"（裸 ``os.getenv`` / ``os.environ``）
  - NO-SECRET-HARDCODE 检测"密钥值硬编码"（``sk-``/``AKIA``/``ghp_``/``KEY = "value"``）

病根（第一性原理）
-----------------
scan_secret_leak.py 是周扫描脚本（L3-Audit），AI 硬编码密钥提交后要等到周扫描才发现，
密钥已泄漏到 git 历史。本 gate 把检测前移到 commit 阶段，硬阻断。

治本方案
--------
在 GitCommitGateway pre-commit 阶段（in-process）注册门禁：
  1. 获取 staged added/modified 文件（.py/.yaml/.yml/.json/.toml）
  2. 过滤 tests/ 豁免 + .env.example 豁免 + 扫描脚本自身豁免
  3. 对每个文件解析 diff，检查 added 行是否命中 SECRET_PATTERNS_DEEP
  4. 豁免 docstring（.py via ast）/ 注释 / import 行
  5. 命中 -> 硬阻断

设计权衡
--------
1. **P0+P1 全阻断（非 P0-block/P1-warn）**：100% AI 开发场景下 warn-only 不构成闭环
   （AI 把 warn 当"通过"，见 commit_gate_registry.GateRegistrationError 文档与二元化
   元规则——灰度规则必死）。ruling S-4 原建议"P1 warn"在此场景下升级为 block，
   误报通过豁免（tests/.env.example/扫描脚本/docstring/注释）处理，而非 warn。
2. **只检测 added 行**：存量硬编码由 scan_secret_leak.py 周扫描清理，gate 只防新增。
3. **正则 SSoT**：SECRET_PATTERNS_DEEP verbatim 复制自
   ``scripts/governance/d6_security/scan_secret_leak.py``（audit-level SSoT），
   此处为 commit-time enforcement 副本。两处应保持同步——改一处须改另一处。
4. **多扩展名扫描**：.py（代码）+ .yaml/.yml/.json/.toml（配置），覆盖密钥硬编码
   常见位置。docstring 豁免仅对 .py（ast.parse），其余仅豁免注释行。
5. **priority=128**：SECRET-REGISTRY-CONSISTENCY(127) 之后、CAPABILITY-OVERLAP(200)
   之前。三密钥治理 gate 聚簇：81(读违规)/127(一致性)/128(值硬编码)。

与 bare_getenv_gate 的关系
--------------------------
互补双层防御：
  - bare_getenv_gate：``x = os.getenv("KEY")`` —— 读密钥方式违规（应改用 secrets.py）
  - secret_hardcode_gate：``KEY = "sk-xxx"`` —— 密钥值硬编码（应改用 secrets.py 读取）

Usage::

    from zephyr.gov_enforcement.commit_gates.secret_hardcode_gate import make_secret_hardcode_gate

    registry.register(make_secret_hardcode_gate())
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _extract_docstring_lines,
    _is_exempt_line,
    _parse_diff_with_line_numbers,
    _read_staged_file,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_secret_hardcode_gate"]

# 扫描的文件扩展名（.py 代码 + .yaml/.yml/.json/.toml 配置）
_SCAN_EXTENSIONS: frozenset[str] = frozenset({".py", ".yaml", ".yml", ".json", ".toml"})

# 豁免文件（含密钥检测模式字面量，扫描自身会误报）
# 真源：scripts/governance/d6_security/scan_secret_leak.py / detect_secrets.py 含 SECRET_PATTERNS
_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        ".env.example",
        ".env",
        "scripts/governance/d6_security/scan_secret_leak.py",
        "scripts/governance/d6_security/detect_secrets.py",
        "src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py",
        "src/zephyr/shared/security/secrets.py",  # 密钥读取模块（含 KEY 常量引用，非硬编码值）
        # create_guard.py 的指引模板含 creation_token 格式示例字面量（token: "auto-xxx" 占位符非真实密钥），
        # 与 capability_canonical_file_registry.yaml 豁免同族（2026-08-20 波3 实证补齐）
        "src/zephyr/gov_enforcement/commit_gates/create_guard.py",
        # creation_tokens 注册表——token 字段是创建意图标记（auto-xxx），非密钥
        # CREATE-GUARD 门禁要求新 .py 文件在此登记 token，与 NO-SECRET-HARDCODE 形成冲突
        "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
    }
)

# ── SECRET_PATTERNS_DEEP —— SSoT: scripts/governance/d6_security/scan_secret_leak.py ──
# verbatim 复制（audit-level SSoT），此处为 commit-time enforcement 副本。
# 改一处须改另一处。P0=高置信度格式/显式 KEY=value；P1=private_key/access_key/db_url。
# 全阻断（见上文设计权衡1）——severity 仅用于消息分级，不区分 block/warn。
_SECRET_PATTERNS_DEEP: list[tuple[re.Pattern, str, str]] = [
    (
        re.compile(r"(?:api[_-]?key|apikey|API_KEY)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
        "API Key 硬编码",
        "P0",
    ),
    (re.compile(r"(?:secret|SECRET)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Secret 硬编码", "P0"),
    (re.compile(r"(?:token|TOKEN)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Token 硬编码", "P0"),
    (re.compile(r"(?:password|PASSWORD|passwd)\s*[:=]\s*['\"][^'\"]{3,}['\"]", re.IGNORECASE), "Password 硬编码", "P0"),
    (re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE), "OpenAI API Key", "P0"),
    (re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE), "AWS Access Key ID", "P0"),
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}", re.IGNORECASE), "GitHub Token", "P0"),
    (
        re.compile(r"(?:private[_-]?key|PRIVATE_KEY)['\"]?\s*[:=]\s*['\"][^'\"]{16,}['\"]", re.IGNORECASE),
        "Private Key",
        "P1",
    ),
    (re.compile(r"(?:access[_-]?key|ACCESS_KEY)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Access Key", "P1"),
    (
        re.compile(
            r"(?:database[_-]?url|DATABASE_URL|DB_URL)\s*[:=]\s*['\"][^'\"]*:[^'\"]*@[^'\"]*['\"]",
            re.IGNORECASE,
        ),
        "数据库连接串含密码",
        "P1",
    ),
]


def _collect_staged_files(gateway):
    """获取 staged added/modified 待扫描文件（fail-open）。

    Returns:
        None=fail-open（git 失败，调用方应放行）；空列表=无文件待检；
        非空列表=待检相对路径（正斜杠）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=AM"])
        if diff_result.returncode != 0:
            logger.warning(
                "NO-SECRET-HARDCODE gate fail-open: git diff 失败(rc=%d)。",
                diff_result.returncode,
            )
            return None
        staged = [f.replace("\\", "/") for f in diff_result.stdout.strip().splitlines() if f]
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "NO-SECRET-HARDCODE gate fail-open: git diff 异常(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None

    result = []
    for f in staged:
        if is_test_exempt(f):
            continue
        if f in _EXEMPT_FILES:
            continue
        # 扩展名匹配（大小写不敏感）
        dot = f.rfind(".")
        if dot < 0:
            continue
        ext = f[dot:].lower()
        if ext not in _SCAN_EXTENSIONS:
            continue
        result.append(f)
    return result


def _scan_file_violations(gateway, rel_file: str) -> list[str]:
    """扫描单个 staged 文件的 added 行，返回违规描述列表。

    对 .py 文件额外豁免 docstring 行（ast 精确识别）；所有文件豁免注释/import 行。
    """
    # 读取 staged 完整内容（用于 docstring 行号提取）
    file_content = _read_staged_file(gateway, rel_file)
    is_py = rel_file.endswith(".py")
    docstring_lines = _extract_docstring_lines(file_content) if (is_py and file_content) else set()

    # 解析 diff，获取 added 行及行号
    try:
        file_diff = gateway.run_git(["git", "diff", "--cached", "--unified=0", "--ignore-cr-at-eol", "--", rel_file])
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("NO-SECRET-HARDCODE gate: git diff 失败 file=%s, %s", rel_file, e)
        return []
    if file_diff.returncode != 0:
        return []

    added_lines = _parse_diff_with_line_numbers(file_diff.stdout)
    violations: list[str] = []
    for line_no, content in added_lines:
        # 豁免：docstring 内的行（仅 .py）
        if line_no in docstring_lines:
            continue
        # 豁免：注释 / import 行
        if _is_exempt_line(content):
            continue
        for compiled_re, label, severity in _SECRET_PATTERNS_DEEP:
            m = compiled_re.search(content)
            if m:
                violations.append(f"  {rel_file}:{line_no} [{severity}] {label}: {m.group(0)[:80]}")
                break  # 同一行只报一个模式，避免噪音
    return violations


def make_secret_hardcode_gate() -> GateSpec:
    """构造密钥值硬编码阻断 GateSpec（硬阻断型）。

    Returns:
        GateSpec(gate_id="NO-SECRET-HARDCODE", priority=128)。
        priority=128——SECRET-REGISTRY-CONSISTENCY(127) 之后、CAPABILITY-OVERLAP(200)
        之前。三密钥治理 gate 聚簇：81(读违规)/127(一致性)/128(值硬编码)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        staged_files = _collect_staged_files(gateway)
        if not staged_files:
            return True, ""

        violations: list[str] = []
        for rel_file in staged_files:
            violations.extend(_scan_file_violations(gateway, rel_file))

        if violations:
            detail = (
                "NO-SECRET-HARDCODE：检测到硬编码密钥/Token/凭证，\n"
                "  密钥值禁止硬编码到代码/配置——改用 zephyr.shared.security.secrets 读取\n"
                "  （get_required_secret / get_service_secret / get_secret_or_default）。\n"
                + "\n".join(violations)
                + "\n-> 参考 SECRETS.md 与 config/secret_registry.yaml"
            )
            logger.error("NO-SECRET-HARDCODE gate block:\n%s", detail)
            return False, detail

        return True, ""

    return GateSpec(gate_id="NO-SECRET-HARDCODE", check=_check, priority=128)
