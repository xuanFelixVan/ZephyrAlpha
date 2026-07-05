# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.runbook_generator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 手册生成格式不可变
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_runbook_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Runbook Generator — 漂移演练手册自动生成。





module_id: MOD-INF-023


生成 Markdown + YAML frontmatter 格式的漂移演练手册


五大板块：metadata / diagnosis / remediation / rollback / references


对标 blueprint.md §6.9。"""

from __future__ import annotations

import yaml

from .drift_models import DriftEvent


def build_runbook_frontmatter(event: DriftEvent) -> dict[str, object]:
    """构造 YAML frontmatter。"""

    return {
        "drift_id": str(event.event_id),
        "module_id": "MOD-INF-023",
        "detector_id": event.detector_id,
        "timestamp": event.timestamp.isoformat(),
        "severity": event.severity.value,
        "state": event.state.value,
        "scan_level": event.scan_level.value,
        "auto_fixable": event.auto_fixable,
        "roi_score": getattr(event, "roi_score", None),
    }


def _estimate_root_cause(event: DriftEvent) -> str:
    """基于检测器类型估计根因。"""

    cause_map: dict[str, str] = {
        "db_schema_drift": (
            "ORM model definition diverged from actual database schema. "
            "Likely cause: schema migration applied without updating corresponding model, "
            "or model field added without running migration."
        ),
        "dep_version_drift": (
            "Installed package versions differ from requirements.txt constraints. "
            "Likely cause: pip install run without updating requirements.txt, "
            "or dependency updated without pinning."
        ),
        "security_policy_drift": (
            "Security guard gaps detected in endpoint or codebase. "
            "Likely cause: new endpoint added without security review, "
            "or security middleware bypassed."
        ),
        "doc_code_coevolution": (
            "Documentation and code diverged beyond acceptable 7-day window. "
            "Likely cause: code changes committed without corresponding blueprint update."
        ),
        "test_coverage_drift": (
            "Test-to-source ratio dropped below threshold. "
            "Likely cause: new source files added without matching test files."
        ),
        "truth_source_drift": (
            "Multiple truth sources disagree on the same fact. "
            "Likely cause: blueprint updated but YAML SSoT not synchronized."
        ),
    }

    return cause_map.get(
        event.detector_id,
        f"Detector {event.detector_id} flagged a deviation. "
        f"Root cause analysis requires manual triage of event details.",
    )


def _build_remediation_options(event: DriftEvent) -> list[dict[str, str]]:
    """生成 2-3 个修复方案，推荐第一个。"""

    options: list[dict[str, str]] = []

    base_opts: dict[str, list[dict[str, str]]] = {
        "db_schema_drift": [
            {
                "name": "Rebuild migration from ORM",
                "steps": (
                    "1. Audit ORM model fields against sqlite_master\n"
                    "2. Generate new Alembic/peewee migration\n"
                    "3. Apply migration: `python manage.py migrate`\n"
                    "4. Re-run detect_db_schema_drift to verify"
                ),
                "pros": "Declarative, reproducible, tracks in VCS",
                "cons": "Requires migration tooling setup, 5-10 min",
                "recommended": "true",
                "effort": "medium",
            },
            {
                "name": "Manual DDL sync",
                "steps": (
                    "1. Connect to DB: `sqlite3 <db_file>`\n"
                    "2. ALTER TABLE ADD COLUMN for each missing column\n"
                    "3. Verify with PRAGMA table_info\n"
                    "4. Re-run detector"
                ),
                "pros": "Immediate fix, no tooling dependency",
                "cons": "Error-prone, no version tracking",
                "recommended": "false",
                "effort": "low",
            },
        ],
        "dep_version_drift": [
            {
                "name": "Auto-reconcile with pip freeze",
                "steps": (
                    "1. Run `pip freeze > requirements.txt`\n"
                    "2. Post-process: replace == with >= for non-critical deps\n"
                    "3. Commit updated requirements.txt\n"
                    "4. Re-run detect_dep_version_drift"
                ),
                "pros": "Fully automated, preserves semantic versioning",
                "cons": "May upgrade unintended packages",
                "recommended": "true",
                "effort": "low",
            },
            {
                "name": "Manual version audit",
                "steps": (
                    "1. Review each mismatched package changelog\n"
                    "2. Test compatibility in isolated venv\n"
                    "3. Update requirements.txt with tested versions\n"
                    "4. Commit with changelog reference"
                ),
                "pros": "Thorough compatibility verification",
                "cons": "Time-consuming, ~30 min per 10 packages",
                "recommended": "false",
                "effort": "high",
            },
        ],
    }

    opts = base_opts.get(event.detector_id)

    if opts:
        return opts

    return [
        {
            "name": f"Triage drift event {event.event_id}",
            "steps": (
                "1. Review event details and source file\n"
                "2. Compare expected vs actual state\n"
                "3. Apply fix or mark as acknowledged\n"
                "4. Re-run detector to verify resolution"
            ),
            "pros": "Standardized triage workflow",
            "cons": "Requires manual judgment",
            "recommended": "true",
            "effort": "medium",
        }
    ]


def _build_rollback(event: DriftEvent) -> str:
    """生成回滚步骤。"""

    if event.auto_fixable:
        return (
            f"1. Revert the auto-applied fix: check VCS log for '{event.event_id}'\n"
            f"2. `git revert <auto-fix-commit>` to undo\n"
            f"3. Re-run {event.detector_id} to confirm drift reappears\n"
            f"4. If drift was intentional, suppress with suppression_learner"
        )

    return (
        "1. No auto-fix applied — manual rollback unnecessary\n"
        "2. If drift was manually resolved, verify with detector re-run\n"
        "3. Baseline snapshot can be restored via baseline_manager.restore()"
    )


def generate_runbook(event: DriftEvent) -> str:
    """生成 Markdown + YAML frontmatter 完整手册。"""

    frontmatter = build_runbook_frontmatter(event)

    root_cause = _estimate_root_cause(event)

    options = _build_remediation_options(event)

    rollback = _build_rollback(event)

    recommended = next((o for o in options if o.get("recommended") == "true"), options[0] if options else None)

    sections: list[str] = []

    sections.append("---")

    sections.append(yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).strip())

    sections.append("---")

    sections.append("")

    sections.append(f"# Runbook: {event.event_id}")

    sections.append("")

    sections.append("## Diagnosis")

    sections.append("")

    sections.append(f"**Detector**: `{event.detector_id}`")

    sections.append(f"**Severity**: `{event.severity.value}`  |  **State**: `{event.state.value}`")

    sections.append("")

    sections.append("### Expected vs Actual")

    sections.append("")

    sections.append(f"> {event.description}")

    if event.details:
        sections.append("")

        sections.append(f"```\n{event.details}\n```")

    sections.append("")

    sections.append("### Root Cause Analysis")

    sections.append("")

    sections.append(root_cause)

    sections.append("")

    sections.append("## Remediation")

    sections.append("")

    for idx, opt in enumerate(options, 1):
        recommend_tag = " **(RECOMMENDED)**" if opt.get("recommended") == "true" else ""

        sections.append(f"### Option {idx}: {opt['name']}{recommend_tag}")

        sections.append("")

        sections.append(f"**Effort**: {opt.get('effort', 'unknown')}  |  **Pros**: {opt.get('pros', 'N/A')}")

        sections.append(f"**Cons**: {opt.get('cons', 'N/A')}")

        sections.append("")

        sections.append("**Steps**:")

        sections.append("")

        for step in opt["steps"].split("\n"):
            if step.strip():
                sections.append(f"{step.strip()}")

        sections.append("")

    sections.append("## Rollback")

    sections.append("")

    sections.append(rollback)

    sections.append("")

    sections.append("### Verification")

    sections.append("")

    sections.append(f"1. Re-run detector: trigger `{event.detector_id}` scan")

    sections.append("2. Confirm no new drift event for the same artifact")

    sections.append("3. Update baseline via `baseline_manager.capture()` if applicable")

    sections.append("")

    sections.append("## References")

    sections.append("")

    sections.append("- Blueprint: `docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md`")

    sections.append("- Detector Registry: `src/zephyr/behavioral-auditor/_detector-registry.yaml`")

    sections.append("- State Machine: `src/zephyr/behavioral-auditor/state_machine.py`")

    sections.append("- Incident Postmortem: check `src/zephyr/behavioral-auditor/incident_postmortem.py`")

    return "\n".join(sections)


def _write_runbook(path: str, content: str) -> None:
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def generate_bulk_runbook(events: list[DriftEvent], output_dir: str) -> list[str]:
    """批量生成手册，返回文件路径列表。"""

    import os

    os.makedirs(output_dir, exist_ok=True)

    generated: list[str] = []

    for event in events:
        safe_name = str(event.event_id).replace("/", "-").replace(":", "-")

        path = os.path.join(output_dir, f"{safe_name}.md")

        content = generate_runbook(event)

        tmp_path = f"{path}.{os.getpid()}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)

            os.replace(tmp_path, path)

            generated.append(path)

        except PermissionError:
            try:
                os.remove(tmp_path)

            except OSError:
                pass

    return generated
