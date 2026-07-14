# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.ch_version_col_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——staged .py/.md/.sql 文件新增行含 ReplacingMergeTree(blocked_col) 时阻断 commit; tests/ 豁免; git diff 不可达 fail-open; 检出违规则 fail-closed
# [MODIFY-GUARD] gate_id="CH-VERSION-COL"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——git diff 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 阻断（passed=False）
# [TESTS] tests/governance/commit_gates/test_ch_version_col_gate.py
# [A_module] module_id=MOD-GOV-ch_version_col_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ch_version_col_gate.py — CH version 列语义误用阻断门禁（CH-VERSION-COL，裁定 #ARCH-CH-009）

病根：ReplacingMergeTree(version_col) 的 version 参数决定后台 merge 时保留哪个版本。
quality_flag UInt8 DEFAULT 1（100% 行值为 1）作 version 列时，所有行"版本号"相同，
后台 merge 无法判定哪个版本更新，等同无参数 ReplacingMergeTree，去重失效。

裁定 #ARCH-CH-009 修复方案：所有 ReplacingMergeTree 表统一使用 ingest_ts DateTime
DEFAULT now() 作 version 列，按写入时序去重（后写入覆盖先写入）。

本 gate 在 commit 时检测 staged 新增行中是否含 ReplacingMergeTree(blocked_col) 模式，
blocked_col 为非 DateTime 列名（quality_flag / is_deleted / is_active / status /
version_num / revision），命中则 fail-closed 阻断提交。

扫描范围：staged added/modified 的 .py / .md / .sql / .yaml / .yml 文件（tests/ 豁免）。
检测方式：git diff --unified=0 提取 added 行文本，正则匹配
ReplacingMergeTree(col_name) 后检查 col_name 是否在 blocked 集合中。

错误合约：
- git diff 失败/异常 → fail-open（passed=True，logger.warning）
- 检出违规 → fail-closed（passed=False，阻断 commit）
- 无 staged 文件 → 放行
"""

from __future__ import annotations

import logging
import re

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_ch_version_col_gate"]

# 非 DateTime 列名集合——这些列作 ReplacingMergeTree version 参数会导致去重失效
_BLOCKED_VERSION_COLS = {
    "quality_flag",   # UInt8 质量标记位（1=正常 0=异常），100% 行值为 1
    "is_deleted",     # UInt8 软删除标记
    "is_active",      # UInt8 激活状态
    "status",         # 各种状态码
    "version_num",    # Int32 数值版本号（非时序）
    "revision",       # Int32 修订号（非时序）
}

# 匹配 ReplacingMergeTree(col_name) 提取 col_name
_REPLACING_MT_PATTERN = re.compile(
    r"ReplacingMergeTree\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)",
    re.IGNORECASE,
)

# 扫描的文件扩展名
_SCAN_EXTENSIONS = (".py", ".md", ".sql", ".yaml", ".yml")


def _get_staged_scan_files(gateway) -> list[str]:
    """获取 staged added/modified 文件列表（过滤 tests/ 和非目标扩展名）。

    fail-open：git diff 失败/异常时返回空列表。
    """
    try:
        diff_result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if diff_result.returncode != 0:
            logger.warning("CH-VERSION-COL fail-open: git diff 失败(rc=%d)", diff_result.returncode)
            return []
        staged = diff_result.stdout.strip().splitlines()
    except Exception as e:
        logger.warning("CH-VERSION-COL fail-open: git diff 异常(%s: %s)", type(e).__name__, e)
        return []
    return [
        f.replace("\\", "/") for f in staged
        if f.endswith(_SCAN_EXTENSIONS) and not is_test_exempt(f)
    ]


def _get_added_lines_text(gateway, rel_path: str) -> list[str]:
    """获取文件 staged diff 的 added 行文本列表（去掉 '+' 前缀）。

    fail-open：git diff 失败/异常时返回空列表。
    """
    try:
        diff_content = gateway._run_git(
            ["git", "diff", "--cached", "--unified=0", "--", rel_path]
        )
        if diff_content.returncode != 0:
            return []
        return [
            line[1:] for line in diff_content.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
    except Exception:
        return []


def _check_file(gateway, rel_path: str) -> list[str]:
    """检测单个文件的 added 行中是否含 ReplacingMergeTree(blocked_col)。

    Returns: 违规描述列表（空列表=无违规）。
    """
    added_lines = _get_added_lines_text(gateway, rel_path)
    if not added_lines:
        return []
    violations: list[str] = []
    for line in added_lines:
        for match in _REPLACING_MT_PATTERN.finditer(line):
            col_name = match.group(1)
            if col_name in _BLOCKED_VERSION_COLS:
                violations.append(
                    f"  {rel_path}: ReplacingMergeTree({col_name}) —— "
                    f"'{col_name}' 是非 DateTime 列，不能作 version 列"
                    f"（裁定 #ARCH-CH-009，应改用 ingest_ts DateTime DEFAULT now()）"
                )
    return violations


def make_ch_version_col_gate() -> GateSpec:
    """构造 CH version 列语义误用阻断 GateSpec（硬阻断型）。

    Returns: GateSpec(gate_id="CH-VERSION-COL", priority=38)。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        scan_files = _get_staged_scan_files(gateway)
        if not scan_files:
            return True, ""
        all_violations: list[str] = []
        for rel_path in scan_files:
            all_violations.extend(_check_file(gateway, rel_path))
        if all_violations:
            detail = (
                "CH-VERSION-COL：检测到 ReplacingMergeTree 使用非 DateTime 列作 version 列，\n"
                "  违反裁定 #ARCH-CH-009——version 列必须是 DateTime 类型（如 ingest_ts）。\n"
                "  病根：quality_flag 等非时序列 100% 行值相同，等同无参数 ReplacingMergeTree，去重失效。\n"
                + "\n".join(all_violations)
                + "\n-> 改用 ReplacingMergeTree(ingest_ts)，并新增 ingest_ts DateTime DEFAULT now() 列"
            )
            logger.error("CH-VERSION-COL gate block:\n%s", detail)
            return False, detail
        return True, ""

    return GateSpec(gate_id="CH-VERSION-COL", check=_check, priority=38)
