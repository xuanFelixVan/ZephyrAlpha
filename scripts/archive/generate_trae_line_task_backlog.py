# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""一次性生成 TRAE_LINE_TASK_BACKLOG_20260409.md（孤儿 + 缺 module_id 逐条任务）。"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    regen_path = REPO / "docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_LIST_REGEN_20260408.txt"
    missing_path = REPO / "docs/09_AUDIT/STATE/MODULE_ID_MISSING_FILES_LIST_20260409.txt"
    out_path = REPO / "docs/09_AUDIT/STATE/TRAE_LINE_TASK_BACKLOG_20260409.md"

    regen = [ln.strip() for ln in regen_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    missing = [ln.strip() for ln in missing_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    lines: list[str] = [
        "---",
        "module_id: TRAE_LINE_TASK_BACKLOG_20260409",
        "version: 1.0.0",
        "status: Active",
        "created_date: 2026-04-09",
        "last_updated: '2026-04-09'",
        "owner: 仓库 Owner",
        "standard_type: 逐条任务 backlog（Trae / Cursor 执行）",
        "applicable_scope: 孤儿治理、module_id 补齐、台账补录；与 CONSTRUCTION_GATE §3 对齐",
        "parent_document: ./TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md",
        "related_documents:",
        "  - ./STRICT_ORPHAN_FILES_LIST_REGEN_20260408.txt",
        "  - ./STRICT_ORPHAN_FILES_REPORT_REGEN_20260408.md",
        "  - ./MODULE_ID_MISSING_FILES_LIST_20260409.txt",
        "  - ./TRAE_BLUEPRINT_TASK_LEDGER_20260408.md",
        "---",
        "",
        "# Trae 逐条任务 backlog（2026-04-09）",
        "",
        "> **生成说明**：根据 Trae 自主窗口完成报告与仓库扫描产物整理；**每一行 `- [ ]` 为独立任务**。",
        "> **Trae 连续执行**：对话中断后，**下一窗口从本文件第一条未勾选任务继续**，先对齐 Git 分支再改。",
        "> **完成方式**：入站链接挂载 / 补 YAML `module_id` / 台账一行 / `CANONICAL_POINTERS` 一行 / defer 登记到 gap 或台账（禁止无记录跳过）。",
        "",
        "## 0. 元任务（先于大批量逐文件任务）",
        "",
        "- [ ] **META-01** 将 9 篇曾未入台账的 `01_BLUEPRINTS` 蓝图补入 `TRAE_BLUEPRINT_TASK_LEDGER_20260408.md` §3.1（新批次号自洽，每篇一行）。",
        "- [ ] **META-02** 复跑 `python scripts/strict_orphan_inbound_scan.py`，更新 REGEN 列表与报告；与基线 tag `doc-baseline-20260409` 对比记录「严格孤儿数」变化。",
        "- [ ] **META-03** 复跑 `python scripts/sentinel_l1_governance_scan.py`，确认 `Invalid links = 0`；将 `module_id` 重复数与 `no_id_total` 写入台账或 Playbook §10。",
        "- [ ] **META-04** 对 **DEDUP** 两簇按 `GOVERNANCE_DECISIONS_LOCKED_20260408.md` ADR-OC-003 选 canonical、改后缀或归档互链。",
        "- [ ] **META-05** 401 篇「首道 YAML 无 module_id」按目录分批（每批 ≤50）补最小 front matter 或登记豁免（路径见 §3）。",
        "",
        "## 1. module_id 重复（2 簇）",
        "",
        "- [ ] **DEDUP-01** 解决 `module_id: FACTOR_GUIDE_001` 重复：canonical `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md`；对 `docs/06_ARCHIVE/overlap_FACTOR_MANAGEMENT_STANDARD_20260407_190203.md` 按 ADR-OC-003 改后缀并加互链/篇首说明。",
        "- [ ] **DEDUP-02** 解决 `module_id: 09_AUDIT_STATE_STRICT_ORPHAN_FILES_REPORT_20260408` 重复：在 `STRICT_ORPHAN_FILES_REPORT_20260408.md` 与 `STRICT_ORPHAN_FILES_REPORT_REGEN_20260408.md` 择一 canonical，另一篇改 `module_id`（如 `_REGEN` 后缀）并互链。",
        "",
        f"## 2. 严格 inbound 孤儿（REGEN 清单，共 **{len(regen)}** 条）",
        "",
        "> 每条任务：从权威 `INDEX.md` / `SITEMAP.md` / 父目录 README 增加**入站**链接，或按 `HANDOFF_ORPHAN_GOVERNANCE_20260408.md` 归档/豁免登记。",
        "",
    ]
    for p in regen:
        lines.append(f"- [ ] **ORPHAN** `{p}`")

    lines.extend(
        [
            "",
            f"## 3. 首道 YAML 缺少 module_id（共 **{len(missing)}** 条）",
            "",
            "> 机器路径清单：`docs/09_AUDIT/STATE/MODULE_ID_MISSING_FILES_LIST_20260409.txt`（与本节一一对应）。",
            "",
        ]
    )
    for p in missing:
        lines.append(f"- [ ] **NO-MID** `{p}`")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
