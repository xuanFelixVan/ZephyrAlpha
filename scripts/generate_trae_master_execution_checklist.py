# -*- coding: utf-8 -*-
"""生成单一主执行清单：TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md（全局编号 T0001+）。"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "docs" / "09_AUDIT" / "STATE"
OUT = STATE / "TRAE_MASTER_EXECUTION_CHECKLIST_20260409.md"
ORPHAN_LIST = STATE / "STRICT_ORPHAN_FILES_LIST_REGEN_20260408.txt"
NO_MID_LIST = STATE / "MODULE_ID_MISSING_FILES_LIST_20260409.txt"
DOCS = REPO / "docs"


def main() -> None:
    lines: list[str] = []
    n = 0

    def task(desc: str) -> None:
        nonlocal n
        n += 1
        tid = f"T{n:04d}"
        lines.append(f"- [ ] **{tid}** {desc}")

    lines.extend(
        [
            "---",
            "module_id: TRAE_MASTER_EXECUTION_CHECKLIST_20260409",
            "version: 1.0.0",
            "status: Active",
            "created_date: 2026-04-09",
            "last_updated: '2026-04-09'",
            "owner: 仓库 Owner",
            "standard_type: 单一主执行清单（全量编号）",
            "applicable_scope: Trae/Cursor 自主执行；合并 Directive、HANDOFF、PartA、PartB、门禁与整改要点",
            "parent_document: ./TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md",
            "related_documents:",
            "  - ./HANDOFF_ORPHAN_GOVERNANCE_20260408.md",
            "  - ./TRAE_BLUEPRINT_TASK_LEDGER_20260408.md",
            "  - ../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md",
            "  - ../STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md",
            "  - ../STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md",
            "  - ../STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md",
            "  - ./GOVERNANCE_DECISIONS_LOCKED_20260408.md",
            "  - ../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md",
            "  - ../PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md",
            "  - ../PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md",
            "  - ../PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md",
            "  - ../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md",
            "  - ../../03_TRADING_TACTICS/API_Contract.md",
            "  - ./STRICT_ORPHAN_FILES_LIST_REGEN_20260408.txt",
            "  - ./MODULE_ID_MISSING_FILES_LIST_20260409.txt",
            "---",
            "",
            "# Trae / 文档治理 — 主执行清单（单一文档 · 全量编号）",
            "",
            "> **用途**：本文件为**唯一勾选真源**；`TRAE_LINE_TASK_BACKLOG_20260409.md`（Part A）与 `TRAE_LINE_TASK_BACKLOG_PARTB_GOVERNANCE_20260409.md`（Part B）为分卷，**任务内容与编号以本文件为准**。再生成：`python scripts/generate_trae_master_execution_checklist.py`。",
            "> **执行规则**：从 **最小未勾选编号** 继续；每批 ≤20～50 文件（视类型）；每批结束 `python scripts/sentinel_l1_governance_scan.py` 且 **Invalid links = 0** 后 `git commit`；禁止向 Owner 提问（见下方框架任务）。",
            "",
            "## 编号索引（按段）",
            "",
            "| 段 | 内容 | 编号前缀说明 |",
            "|----|------|----------------|",
            "| A | 框架：Directive/HANDOFF/真源阅读与硬规则 | 自 T0001 起连续 |",
            "| B | 元任务 + module_id 去重 | META / DEDUP |",
            "| C | 严格 inbound 孤儿（逐文件） | ORPHAN + 路径 |",
            "| D | 首道 YAML 缺 module_id（逐文件） | NO-MID + 路径 |",
            "| E | docs 一级目录普查 | DIR |",
            "| F | 仓库非 docs 带 | EXT |",
            "| G | 全库审计批次 A1～I3 | AUDIT |",
            "| H | HANDOFF 拆条 | HO |",
            "| I | 文档整改阶段 | REM |",
            "| J | 施工门禁 §3 块 | CG3 |",
            "| K | 二级热点子树 | SUB |",
            "",
            "---",
            "",
            "## A. 执行框架与真源（`TRAE_AUTONOMOUS_WORK_DIRECTIVE` + `HANDOFF` + 关联标准）",
            "",
        ]
    )

    # --- Section A: framework (merged from directive + handoff pointers)
    fw = [
        "（框架）通读并之后遵守 `docs/09_AUDIT/STATE/TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md` 全文：§3 禁止、§4 工作循环、§5 DoD、§6 遇阻、§7 时长、§8 收工",
        "（框架）通读 `docs/09_AUDIT/STATE/HANDOFF_ORPHAN_GOVERNANCE_20260408.md` 全文；至少精读 §0 目录、§15 Git、§16 防幻觉、§17 长时作业、§18 重复互查",
        "（框架）打开 `docs/09_AUDIT/STATE/TRAE_BLUEPRINT_TASK_LEDGER_20260408.md`；**仅**能修改台账指派给自己的 `01_BLUEPRINTS` 文件；未指派的不打开不保存",
        "（框架）打开 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md`：确认 §0 三阶段、§0.1 蓝图终稿五条、§0.3 与 §3 与当前窗口目标一致",
        "（框架）打开 `docs/03_TRADING_TACTICS/API_Contract.md`；蓝图「接口与契约」段须可指到此真源",
        "（框架）打开 `docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md`（全部 ADR；双 YAML、module_id、audit_state、重复正文等）",
        "（框架）打开 `docs/09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`",
        "（框架）打开 `docs/09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`",
        "（框架）打开 `docs/09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md`（含 §10 执行记录义务）",
        "（框架）打开 `docs/09_AUDIT/PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md` 与 `docs/09_AUDIT/STATE/ARCH_MODULE_GAP_REGISTER_20260408.md`（矛盾时加 G3 草案，不擅自改总纲）",
        "（框架）打开 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md` 并对照当前阶段",
        "（框架）打开 `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`；动重复前必须先更新 disposition，禁止无记录删除",
        "（硬规则）执行全程禁止向 Owner/用户提问、禁止等待确认（工具完全不可用且 §6 用尽除外）",
        "（硬规则）禁止编造 `docs/` 下路径；任何「文件存在」须 Glob/Read 验证",
        "（硬规则）禁止手估孤儿数；须运行 `python scripts/strict_orphan_inbound_scan.py` 并在收工/批次说明中引用 REGEN 输出路径",
        "（硬规则）每批文件编辑后运行 `python scripts/sentinel_l1_governance_scan.py`；**Invalid links 必须为 0** 才能开始下一批扩 scope",
        "（硬规则）未按 `DUPLICATE_DOCUMENT_HANDLING_STANDARD` 更新 `CANONICAL_POINTERS.md` 前，不得删除疑似重复文档",
        "（硬规则）默认不得擅自扩大范围到 `docs/01_FRAMEWORK/*BLUEPRINT*`（除非台账或 Owner 书面指派）",
        "（硬规则）蓝图「终稿」= `CONSTRUCTION_GATE` §0.1 五条同时满足；做不到则登记 gap/defer，禁止伪完成",
        "（工作循环）按 HANDOFF §15 建立长时作业分支 + 基线 tag（若尚未存在）",
        "（工作循环）每 60～90 分钟：选批 → 修改 → L1=0 → `git commit`（message 含范围与 L1=0）→ 更新台账 §6 / 本清单勾选",
        "（工作循环）约每 2 轮可选复跑 `strict_orphan_inbound_scan.py` 记录趋势",
        "（DoD）本窗口须有至少一次 L1 报告说明 **Invalid links = 0**（提交或 restore 须在 Playbook §10 说明）",
        "（DoD）已承诺台账批次内文件：已处理或 **defer**（理由写入台账或 gap register）",
        "（DoD）本窗口若动过重复簇：`CANONICAL_POINTERS` 无新增悬空 TBD（或含 Owner/日期指派）",
        "（DoD）收工：`DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md` §10 增加一行；必要时 milestone tag（HANDOFF §15.3）",
        "（遇阻）断链：按 L1 明细修真实相对路径，禁止假目标",
        "（遇阻）不知是否删除：**不删**；仅 Superseded/说明/按 LAYOUT 迁至 STATE|REPORTS",
        "（遇阻）不知 canonical：在 `CANONICAL_POINTERS.md` 增加 TBD 行 + 两路径对比摘要 + UTC 日期",
        "（遇阻）与总纲矛盾：`ARCH_MODULE_GAP_REGISTER_20260408.md` 加 G3，不静默改 `ARCHITECTURE.md`",
        "（遇阻）脚本失败：重试 3 次 → `git restore` 可疑文件 → 台账记 blocked（脚本名+首行错误）→ 停止扩 scope",
        "（门禁/整改）进入第 3 阶段写代码前须满足 `CONSTRUCTION_GATE` §3 与 §2 复跑要求；本窗口若只做蓝图/治理则在本清单 J 段登记进度或豁免",
        "（整改）遵循 `docs/09_AUDIT/PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md` 与 `OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md` 阶段顺序；P0-B 禁止跳过 50 文件 dry-run",
        "（审计）全库分批方法见 `docs/09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md`（本清单 G 段为批次勾选）",
        "（可选）附录英文规范块：同 `TRAE_AUTONOMOUS_WORK_DIRECTIVE_20260408.md` §10 Appendix A，贴 Trae 首条可增稳",
    ]
    for s in fw:
        task(s)

    lines.extend(["", "---", "", "## B. 元任务与 module_id 去重", ""])

    meta = [
        "（META）将 9 篇曾未入台账的 `01_BLUEPRINTS` 蓝图补入 `TRAE_BLUEPRINT_TASK_LEDGER_20260408.md` §3.1（新批次号自洽，每篇一行）",
        "（META）复跑 `python scripts/strict_orphan_inbound_scan.py`，更新 REGEN 列表与报告；与基线 tag `doc-baseline-20260409`（若存在）对比记录严格孤儿数变化",
        "（META）复跑 `python scripts/sentinel_l1_governance_scan.py`，确认 Invalid links = 0；将 module_id 重复数与 no_id_total 写入台账或 Playbook §10",
        "（META）对 DEDUP 两簇按 `GOVERNANCE_DECISIONS_LOCKED_20260408.md` ADR-OC-003 处理（canonical、后缀、互链）",
        "（META）401 篇缺首道 module_id 按目录分批（每批 ≤50）补最小 front matter 或登记豁免（路径见本清单 D 段）",
    ]
    for s in meta:
        task(s)

    task(
        "（DEDUP）解决 `module_id: FACTOR_GUIDE_001` 重复：canonical `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md`；`docs/06_ARCHIVE/overlap_FACTOR_MANAGEMENT_STANDARD_20260407_190203.md` 按 ADR 改后缀并互链"
    )
    task(
        "（DEDUP）解决 `module_id: 09_AUDIT_STATE_STRICT_ORPHAN_FILES_REPORT_20260408` 重复：`STRICT_ORPHAN_FILES_REPORT_20260408.md` 与 `STRICT_ORPHAN_FILES_REPORT_REGEN_20260408.md` 择一 canonical，另一改 module_id（如 `_REGEN`）并互链"
    )

    lines.extend(["", "---", "", "## C. 严格 inbound 孤儿（逐文件 · REGEN）", ""])
    orphan_lines = [ln.strip() for ln in ORPHAN_LIST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for p in orphan_lines:
        task(f"（ORPHAN）`{p}` — 自权威 INDEX/SITEMAP/父 README 增加入站链，或按 HANDOFF 归档/豁免登记")

    lines.extend(["", "---", "", "## D. 首道 YAML 缺少 module_id（逐文件）", ""])
    mid_lines = [ln.strip() for ln in NO_MID_LIST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for p in mid_lines:
        task(f"（NO-MID）`{p}` — 补首道 front matter 之 `module_id`（及 status/version）或登记豁免")

    lines.extend(["", "---", "", "## E. `docs/` 一级目录 — 归档 / 职责 / 导航 普查", ""])
    dirs = sorted(p.name for p in DOCS.iterdir() if p.is_dir())
    for name in dirs:
        task(
            f"（DIR）`docs/{name}/` — 归档候选与重复扫描；补/建议 INDEX 或 README；写 1 段目录职责摘要或 defer"
        )

    lines.extend(["", "---", "", "## F. 仓库非 `docs/` 文档带", ""])
    ext = [
        "（EXT）`review_materials_package/` — 与内部真源区分、豁免登记（CONSTRUCTION_GATE / P1C_DEFERRED 口径）",
        "（EXT）`notebooks/**/*.md` — 与 docs 交叉引用；抽样断链检查",
        "（EXT）`data/**/*.md` — 与实施文档去重；登记 canonical",
        "（EXT）仓库根 `README.md` — 与 `docs/INDEX.md`、`System_Manifest.md` 一致",
    ]
    for s in ext:
        task(s)

    lines.extend(["", "---", "", "## G. 全库文档审计方案 — 批次（FULL_SYSTEM_DOCUMENT_AUDIT_PLAN）", ""])
    batch_ids = [
        "A1",
        "A2",
        "A3",
        "A4",
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "C1",
        "C2",
        "C3",
        "C4",
        "D1",
        "D2",
        "D3",
        "E1",
        "E2",
        "E3",
        "E4",
        "F1",
        "F2",
        "F3",
        "G1",
        "G2",
        "G3",
        "G4",
        "H1",
        "H2",
        "H3",
        "H4",
        "I1",
        "I2",
        "I3",
    ]
    for bid in batch_ids:
        task(f"（AUDIT）批次 `{bid}` — 按 FULL_SYSTEM_DOCUMENT_AUDIT_PLAN 执行该路径 L1/L2/L3 与汇总报告")

    lines.extend(["", "---", "", "## H. HANDOFF 拆条（证据驱动）", ""])
    ho = [
        "（HO）通读 HANDOFF §0 目录；确认 §15/§16/§17 已读并摘录 3 条硬禁令到 Playbook 或台账",
        "（HO）`DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md` §10：本窗口有动作则补一行摘要",
        "（HO）对照 `BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md`；与当前 backlog 冲突则登记 ARCH gap",
        "（HO）运行 `strict_orphan_inbound_scan.py`；保留 REGEN 与基线 diff 说明",
        "（HO）`CANONICAL_POINTERS.md`：无悬空 TBD；新簇已 disposition",
        "（HO）`INDEX_GROUPED_20260408.md`（STATE 与 REPORTS）：长列表入站是否足够",
        "（HO）`docs/09_AUDIT/INDEX_AUDIT.md`：门户链可达真源",
        "（HO）`OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`：节奏或 defer",
        "（HO）Git：长时作业前基线 tag；窗口结束 milestone tag 或书面说明跳过",
        "（HO）防幻觉：声称须附 Glob/Read 或脚本片段",
        "（HO）HANDOFF §18：本轮涉及重复簇 canonical 与互链",
    ]
    for s in ho:
        task(s)

    lines.extend(["", "---", "", "## I. 文档整改指令（DOC_REMEDIATION）", ""])
    rem = [
        "（REM）P0-A：`temp_*.md` + 蓝图双重路径 + `[模块ID]` 占位 — 指令 §4",
        "（REM）P0-B：双 YAML 50 文件 dry-run 审阅后再分批写回 — 指令 §5 / ADR-OC-001",
        "（REM）P1-A：module_id 去重 + 缺省 + registry — 指令 §6",
        "（REM）P1-B：audit_state 权威目录合并 — 指令 §7 / ADR-OC-002",
        "（REM）P1-C：P1 余项 — 指令 §8 与 P1C_DEFERRED",
        "（REM）闭环：EC-1～EC-7 复跑勾选 + POST_REMEDIATION L1 存档路径",
    ]
    for s in rem:
        task(s)

    lines.extend(["", "---", "", "## J. 施工门禁 §3（进入第 3 阶段代码前）", ""])
    cg = [
        "（CG3-A）元数据 / L1 / 双 YAML 复跑达标 — CONSTRUCTION_GATE §2～§3-A",
        "（CG3-B）架构模块审计与 gap — §3-B",
        "（CG3-C）全库审计 P0 批次 — §3-C",
        "（CG3-D）重复与孤儿治理 — §3-D",
        "（CG3-E）API/契约与 TDR — §3-E",
        "（CG3-F）施工文档 §0.3 交付物 — §3-F",
    ]
    for s in cg:
        task(s)

    lines.extend(["", "---", "", "## K. 二级热点子树（可选加深）", ""])
    sub = [
        "（SUB）`docs/05_IMPLEMENTATION/04_OPERATIONS/` — 与 09_AUDIT / audit_state 边界",
        "（SUB）`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` — 蓝图与施工文档边界",
        "（SUB）`docs/05_IMPLEMENTATION/07_OPERATIONS/` — 运维与监控入口",
        "（SUB）`docs/06_ARCHIVE/` 根散落 — G1 归类索引",
    ]
    for s in sub:
        task(s)

    lines.extend(
        [
            "",
            "---",
            "",
            f"**清单结束**：共 **{n}** 条编号任务（T0001～T{n:04d}）。",
            "",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} tasks={n}")


if __name__ == "__main__":
    main()
