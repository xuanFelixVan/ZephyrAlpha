# [BLUEPRINT] MOD-INF-021 | 03_modules/l01_infrastructure/rollback-system/blueprint.md | §

# [MODULE] zephyr.rollback.runbook_generator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
RunbookGenerator — 回滚操作 Runbook 自动生成。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B123

从审计日志中提取回滚操作历史，自动生成下次可用的标准化 Runbook。
格式: 零依赖 Markdown，含触发条件 / 前置检查 / 执行步骤 / 回滚方法。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RunbookGenerator:

    RUNBOOK_DIR: str = ".zephyr/runbooks"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._runbook_dir = self._project_root / self.RUNBOOK_DIR
        self._runbook_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, operation_type: str, audit_records: list[dict[str, Any]]) -> Path:
        now = datetime.now(timezone.utc)
        runbook_id = f"RB-{operation_type}-{now.strftime('%Y%m%d-%H%M')}"

        lines: list[str] = []
        lines.append(f"# Runbook: {operation_type}")
        lines.append(f"")
        lines.append(f"- **Runbook ID**: {runbook_id}")
        lines.append(f"- **Generated At**: {now.isoformat()}")
        lines.append(f"- **Source**: Auto-generated from {len(audit_records)} audit records")
        lines.append(f"")
        lines.append(f"## 1. Trigger Conditions")
        lines.append(f"")
        triggers = self._extract_triggers(audit_records)
        for t in triggers:
            lines.append(f"- {t}")
        lines.append(f"")
        lines.append(f"## 2. Pre-flight Checks")
        lines.append(f"")
        lines.append(f"- [ ] Verify git working tree is clean")
        lines.append(f"- [ ] Verify not in detached HEAD state")
        lines.append(f"- [ ] Verify no rebase/merge in progress")
        lines.append(f"- [ ] Verify remote is not ahead of local")
        lines.append(f"")
        lines.append(f"## 3. Execution Steps")
        lines.append(f"")
        for i, step in enumerate(self._extract_steps(audit_records), 1):
            lines.append(f"{i}. {step}")
        lines.append(f"")
        lines.append(f"## 4. Rollback Method (if this operation fails)")
        lines.append(f"")
        lines.append(f"```bash")
        lines.append(f"python src/zephyr/rollback/rollback_bootstrap.py --project-root .")
        lines.append(f"```")
        lines.append(f"")
        lines.append(f"## 5. Audit Summary")
        lines.append(f"")
        lines.append(f"| Timestamp | Operation | Success | Details |")
        lines.append(f"|-----------|-----------|---------|---------|")
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
        return sorted(steps) if steps else ["Verify state → Execute revert → Verify result"]
