# -*- coding: utf-8 -*-
"""生成 TRAE_LINE_TASK_BACKLOG_PARTB_GOVERNANCE_20260409.md（目录普查 + 交接文档拆条）。"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
OUT = REPO / "docs" / "09_AUDIT" / "STATE" / "TRAE_LINE_TASK_BACKLOG_PARTB_GOVERNANCE_20260409.md"


def main() -> None:
    dirs = sorted(p.name for p in DOCS.iterdir() if p.is_dir())

    lines: list[str] = [
        "---",
        "module_id: TRAE_LINE_TASK_BACKLOG_PARTB_GOVERNANCE_20260409",
        "version: 1.0.0",
        "status: Active",
        "created_date: 2026-04-09",
        "last_updated: '2026-04-09'",
        "owner: 仓库 Owner",
        "standard_type: 逐条任务 backlog Part B（目录普查 / 交接拆条）",
        "applicable_scope: 与 HANDOFF、全库审计方案、整改指令、施工门禁对齐；不替代 Part A 的 532+401 文件级任务",
        "parent_document: ./TRAE_LINE_TASK_INDEX_20260409.md",
        "related_documents:",
        "  - ./HANDOFF_ORPHAN_GOVERNANCE_20260408.md",
        "  - ../PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md",
        "  - ../PROCEDURES/DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md",
        "  - ./CONSTRUCTION_GATE_CRITERIA_20260408.md",
        "  - ./TRAE_LINE_TASK_BACKLOG_20260409.md",
        "---",
        "",
        "# Trae 逐条任务 backlog — Part B：目录普查与交接拆条（2026-04-09）",
        "",
        "> **与 Part A 关系**：`TRAE_LINE_TASK_BACKLOG_20260409.md` 含 **532 ORPHAN + 401 NO-MID + DEDUP + 元任务**；本文件含 **按文件夹的治理普查**、**全库审计批次**、**HANDOFF/整改/门禁** 的细条。执行时 **两者都未清空不算「交接任务全部完成」**（除非你明确只跑蓝图文件级 backlog）。",
        "> **单条完成标准（目录型）**：每条目录任务至少产出其一：父级 `INDEX.md`/`README` 增补入站链、归档搬运 + `CANONICAL_POINTERS`、或 `ARCH_MODULE_GAP_REGISTER` / 台账 **defer 一行**（含理由与日期）。每批结束 `L1 Invalid links = 0`。",
        "",
        "## 4. `docs/` 一级目录 — 归档 / 职责 / 导航 普查（每条对应一个文件夹）",
        "",
        "> **你要做的事**：通读该树主要入口；标出「应留在活跃真源 / 应归档 / 重复嫌疑」；**禁止大爆炸**（单批改动 ≤20 文件）；不确定则只登记 gap。",
        "",
    ]
    for name in dirs:
        path = f"docs/{name}/"
        lines.append(
            f"- [ ] **DIR** `{path}` — 归档候选与重复嫌疑扫描；更新或建议更新该树 `INDEX.md`/`README.md`；写 1 段「本目录职责」摘要（可写入该目录 README 或 STATE 报告）"
        )

    lines.extend(
        [
            "",
            "## 5. 仓库内非 `docs/` 文档带（审计方案 H 阶段相关）",
            "",
            "- [ ] **EXT** `review_materials_package/` — 与内部真源区分、路径与豁免登记（见 `CONSTRUCTION_GATE` / `P1C_DEFERRED` 口径）",
            "- [ ] **EXT** `notebooks/**/*.md` — 实验记录与 `docs/` 交叉引用；抽样检查断链",
            "- [ ] **EXT** `data/**/*.md` — 评估类 md 是否与实施文档重复；登记 canonical",
            "- [ ] **EXT** 仓库根 `README.md` — 与 `docs/INDEX.md`、`System_Manifest.md` 链接与叙事一致",
            "",
            "## 6. 全库文档审计方案 — 按批次 ID 逐条（对应 `FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md`）",
            "",
            "> 每条：对该批次路径做 L2 五问汇总 + 批次表 + 目录职责地图片段；报告路径建议 `docs/09_AUDIT/REPORTS/L2_BATCH_<ID>_YYYYMMDD.md`。",
            "",
        ]
    )
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
        lines.append(
            f"- [ ] **AUDIT-BATCH** `{bid}` — 执行 `FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md` 中该批次路径的 L1/L2/L3 检查与汇总输出"
        )

    lines.extend(
        [
            "",
            "## 7. HANDOFF 整册 — 拆成可勾选检查项（证据驱动）",
            "",
            "- [ ] **HO-00** 通读 `HANDOFF_ORPHAN_GOVERNANCE_20260408.md` §0 目录，确认 §15/§16/§17 已读并摘录 3 条硬禁令到 Playbook 或台账",
            "- [ ] **HO-01** 对照 `DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md` §10：补一行当日执行摘要（若本窗口有动作）",
            "- [ ] **HO-02** 对照 `BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md`：当前蓝图卫生阶段与本文 Part A/B 是否一致，冲突则登记 `ARCH_MODULE_GAP_REGISTER`",
            "- [ ] **HO-03** 运行 `scripts/strict_orphan_inbound_scan.py`，保留 REGEN 列表与基线 diff 说明",
            "- [ ] **HO-04** 检查 `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`：无悬空 TBD；新增重复簇已 disposition",
            "- [ ] **HO-05** `docs/09_AUDIT/STATE/INDEX_GROUPED_20260408.md` 与 `docs/09_AUDIT/REPORTS/INDEX_GROUPED_20260408.md`：STATE/REPORTS 长列表入站是否仍足够（不足则补链或登记）",
            "- [ ] **HO-06** `docs/09_AUDIT/INDEX_AUDIT.md`：门户链是否可达当前真源",
            "- [ ] **HO-07** `docs/06_ARCHIVE/OVERLAP_ORPHAN_PARALLEL_REMEDIATION_SCHEDULE_20260408.md`：本窗口 overlap/orphan 是否按节奏推进或登记 defer",
            "- [ ] **HO-08** Git：长时作业前分支 + 基线 tag（见 HANDOFF §15）；本窗口结束 milestone tag 或说明为何跳过",
            "- [ ] **HO-09** 防幻觉：任意「路径存在/已修复」声明须附 Glob/Read 或脚本输出片段（§16）",
            "- [ ] **HO-10** 重复 + Layer 互查：按 HANDOFF §18 对本轮改动涉及簇做 canonical 与互链",
            "",
            "## 8. 文档整改指令 — 阶段条（`DOC_REMEDIATION_TASK_DIRECTIVE_20260408.md`）",
            "",
            "> 若 `REMEDIATION_EXECUTION_CLOSURE_20260408.md` 已宣称闭环：本条目标改为 **复跑验证 + 记录路径**，而非重复施工。",
            "",
            "- [ ] **REM-P0A** 根目录 `temp_*.md` + 蓝图双重路径 + `[模块ID]` 占位 — 按指令 §4 验收",
            "- [ ] **REM-P0B** 双 YAML：50 文件 dry-run 已审 + 分批写回 — 按指令 §5 与 ADR-OC-001",
            "- [ ] **REM-P1A** `module_id` 去重 + 缺省补全 + registry — 按指令 §6",
            "- [ ] **REM-P1B** `audit_state` 权威目录合并 — 按指令 §7 与 ADR-OC-002",
            "- [ ] **REM-P1C** Backlog P1 余项 — 按指令 §8 与 `P1C_DEFERRED_20260408.md`",
            "- [ ] **REM-CLOSURE** EC-1～EC-7 复跑勾选 + `SENTINEL_L1_POST_REMEDIATION` 存档路径更新",
            "",
            "## 9. 施工门禁 §3 — 块级逐条（进入第 3 阶段代码前）",
            "",
            "> 细则见 `CONSTRUCTION_GATE_CRITERIA_20260408.md` §3；每条完成须在 STATE 或 closure 报告中可指向证据。",
            "",
            "- [ ] **CG3-A** 元数据 / L1 / 双 YAML 复跑达标（§2～§3-A）",
            "- [ ] **CG3-B** 架构模块审计与 gap 登记闭合或可豁免（§3-B）",
            "- [ ] **CG3-C** 全库审计关键批次（P0）无未处理 P0 发现或已登记（§3-C）",
            "- [ ] **CG3-D** 重复与孤儿治理达标或书面豁免（§3-D）",
            "- [ ] **CG3-E** API/契约与 TDR 对齐（§3-E）",
            "- [ ] **CG3-F** 施工文档 §0.3 交付物齐套（§3-F）",
            "",
            "## 10. 可选：二级热点子树（`05_IMPLEMENTATION` 内再拆，每批 ≤20 文件）",
            "",
            "- [ ] **SUB-05** `docs/05_IMPLEMENTATION/04_OPERATIONS/` — 与 `09_AUDIT` 重复与 audit_state 边界",
            "- [ ] **SUB-05** `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` — 蓝图与施工文档边界（除 Part A 已列单文件外）",
            "- [ ] **SUB-05** `docs/05_IMPLEMENTATION/07_OPERATIONS/` — 运维手册与监控入口",
            "- [ ] **SUB-06** `docs/06_ARCHIVE/(root)` — 散落 md 归类索引（全库审计 G1）",
            "",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(lines)} lines), docs dirs: {len(dirs)}")


if __name__ == "__main__":
    main()
