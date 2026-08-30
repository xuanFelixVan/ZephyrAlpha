# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.runbook_generator
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RunbookGenerator — 回滚操作 Runbook 自动生成。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B123

从审计日志中提取回滚操作历史，自动生成下次可用的标准化 Runbook。
格式: 零依赖 Markdown，含触发条件 / 前置检查 / 执行步骤 / 回滚方法。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: runbook_generator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RunbookGenerator
#   name_en: RunbookGenerator
#   intro: class RunbookGenerator 源码 L71-L142
#   desc: 公共方法（定义序）: generate；源码 L71-L142
#   inputs: project_root
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RunbookGenerator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# 模块级工具函数委托给 canonical 实现 zephyr.gov_drift.runbook_generator
# (MOD-INF-023 drift detector 蓝图)。tests/governance/ops/test_runbook_generator.py
# 期望这些函数接受 drift event 对象并返回 Markdown + YAML frontmatter。
# 原本地实现签名错误（接受 kwargs 而非 event），已替换为 canonical 委托。
from zephyr.gov_drift.runbook_generator import (  # noqa: E402
    build_runbook_frontmatter,
    generate_bulk_runbook,
    generate_runbook,
)


class RunbookGenerator:
    RUNBOOK_DIR: str = ".zephyr/runbooks"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._runbook_dir = self._project_root / self.RUNBOOK_DIR
        self._runbook_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, operation_type: str, audit_records: list[dict[str, Any]]) -> Path:
        now = datetime.now(UTC)
        runbook_id = f"RB-{operation_type}-{now.strftime('%Y%m%d-%H%M')}"

        lines: list[str] = []
        lines.append(f"# Runbook: {operation_type}")
        lines.append("")
        lines.append(f"- **Runbook ID**: {runbook_id}")
        lines.append(f"- **Generated At**: {now.isoformat()}")
        lines.append(f"- **Source**: Auto-generated from {len(audit_records)} audit records")
        lines.append("")
        lines.append("## 1. Trigger Conditions")
        lines.append("")
        triggers = self._extract_triggers(audit_records)
        for t in triggers:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("## 2. Pre-flight Checks")
        lines.append("")
        lines.append("- [ ] Verify git working tree is clean")
        lines.append("- [ ] Verify not in detached HEAD state")
        lines.append("- [ ] Verify no rebase/merge in progress")
        lines.append("- [ ] Verify remote is not ahead of local")
        lines.append("")
        lines.append("## 3. Execution Steps")
        lines.append("")
        for i, step in enumerate(self._extract_steps(audit_records), 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append("## 4. Rollback Method (if this operation fails)")
        lines.append("")
        lines.append("```bash")
        lines.append("python src/zephyr/rollback/rollback_bootstrap.py --project-root .")
        lines.append("```")
        lines.append("")
        lines.append("## 5. Audit Summary")
        lines.append("")
        lines.append("| Timestamp | Operation | Success | Details |")
        lines.append("|-----------|-----------|---------|---------|")
        for r in audit_records[-5:]:
            ts = r.get("timestamp_utc", "")[:19]
            op = r.get("operation", "")
            success = "✅" if r.get("success") else "❌"
            details = json.dumps(r.get("details", {}), ensure_ascii=False)[:60]
            lines.append(f"| {ts} | {op} | {success} | {details} |")

        content = "\n".join(lines)
        output_path = self._runbook_dir / f"{runbook_id}.md"
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def _extract_triggers(self, audit_records: list[dict[str, Any]]) -> list[str]:
        triggers: set[str] = set()
        for r in audit_records:
            triggers.add(f"Operation: {r.get('operation', 'unknown')} failed")
        return sorted(triggers) if triggers else ["No trigger data available"]

    def _extract_steps(self, audit_records: list[dict[str, Any]]) -> list[str]:
        steps: set[str] = set()
        for r in audit_records:
            details = r.get("details", {})
            if isinstance(details, dict) and "step" in details:
                steps.add(details["step"])
        return sorted(steps) if steps else ["Verify state -> Execute revert -> Verify result"]


# 模块级工具函数 build_runbook_frontmatter / generate_runbook / generate_bulk_runbook
# 在文件顶部从 zephyr.gov_drift.runbook_generator 导入（canonical 实现）。
