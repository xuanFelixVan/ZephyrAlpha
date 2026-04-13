---
module_id: CONSTRUCTION_PHASE_TASK_LIST_001
version: 1.0.0
status: Active
created_date: '2026-04-13'
last_updated: '2026-04-13'
owner: 首席文档架构师
layer: layer_05
responsibility: 施工阶段四步 Pipeline 统一任务清单
standard_type: 任务清单
applicable_scope: 本 Git 仓库全量文档与代码资产
---

# 施工阶段统一任务清单

> **定位**：本文件取代已归档的 [蓝图终稿任务清单](./CANON/ARCHIVE/blueprint-phase-closure-task-list.md) 和 [全仓治理总图](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md)，成为施工阶段的**唯一主线任务清单**。
> **核心理念**：全系统扫描 → 修复脚本编排 → 分批原子执行 → 真源融合与索引重建。

## Pipeline 总览

```
Phase 1 ──全系统扫描──┐
                      ▼
Phase 2 ──修复脚本编排──┐
                        ▼
Phase 3 ──分批原子执行──┐
                        ▼
Phase 4 ──真源融合与索引重建──→ 施工门禁验收
```

## 映射表：四步 Pipeline × 旧流程

| Pipeline 阶段 | 对应 REPO_WIDE | 对应蓝图任务 | 对应 README 流程 |
|---------------|----------------|-------------|-----------------|
| Phase 1 全系统扫描 | P0 基线快照 + §0 口径冻结 | 机构阶段 1~2（控制面 + 基线） | §1~§2（蓝图收口 + 孤儿重复） |
| Phase 2 修复脚本编排 | §2.3 并行工作表 + 工具总索引 §2 | 机构阶段 3（清点与映射） | §3（审计区入口） |
| Phase 3 分批原子执行 | P1~P6 波次 + §7 前缀队列 + W0~W4 | 任务 1~6 + 机构阶段 4~5 | §4~§6（分层治理 + 根卫生 + 深度尽治） |
| Phase 4 真源融合与索引重建 | P7 施工门禁 + L1 复跑 | 机构阶段 6~7（质量收口 + 持续保证） | §7（文档地图与放置） |

> **细节追溯**：P0~P7 详细退出标准见 [REPO_WIDE §7](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md)；W0~W4 勾选历史见 [蓝图任务清单](./CANON/ARCHIVE/blueprint-phase-closure-task-list.md)。

---

## Phase 1: 全系统扫描

> 目标：建立仓库资产的完整基线快照，发现所有待修复问题。

- [ ] **1.1** 运行 `git ls-files` 生成全量跟踪文件清单 → `REPO_GIT_TRACKED_FILES_*.txt`
- [ ] **1.2** 运行 `python scripts/governance/export_repo_directory_rollup.py` → rollup 报表（深度 3~6 前缀聚合）
- [ ] **1.3** 运行 `python scripts/audit/sentinel_l1_governance_scan.py` → 全库断链 + module_id 重复报告
- [ ] **1.4** 运行 `python scripts/governance/scan_duplicate_file_content.py --ext md` → 内容哈希重复（C1）
- [ ] **1.5** 运行 `python scripts/governance/scan_basename_collisions.py` → 同名碰撞（C2）
- [ ] **1.6** 运行 `python scripts/governance/scan_index_health.py` → 索引健全性 / 零入链候选
- [ ] **1.7** 运行 `python scripts/governance/scan_blueprint_d_overlap_candidates.py` → D 类重叠候选
- [ ] **1.8** 汇总所有扫描报告至 `docs/09_AUDIT/STATE/`，commit 快照

**退出标准**：全部扫描脚本无异常运行，产出报表已 commit，问题总数已统计记录。

---

## Phase 2: 修复脚本编排

> 目标：根据 Phase 1 扫描结论制定修复策略与执行顺序。

- [ ] **2.1** 按 [治理工具总索引](./governance-tools-index.md) §2 确定脚本执行顺序
- [ ] **2.2** 对每个扫描发现分类处理策略：
  - 自动可修（断链 → 批量路径替换）
  - 需 Owner 裁决（D 类重叠 → Playbook §2.5 置信度分级）
  - 直接归档（衍生物 / `.diff` / `.bak*`）
- [ ] **2.3** 按路径深度 / 前缀拆分执行批次（参考 [REPO_WIDE §7 前缀队列](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md)）
- [ ] **2.4** 如需新修复脚本则编写（放入 `scripts/governance/`，同步更新工具总索引）
- [ ] **2.5** D 类重叠可选二审：`triage_blueprint_d_overlap_pairs.py` → JSONL + [二审提示词模板](./d-class-overlap-second-pass-prompt-template.md)

**退出标准**：每项扫描发现均有指定修复路径（自动/Owner/归档），批次划分表已写入本文件 Phase 3 备忘。

---

## Phase 3: 分批原子执行

> 目标：按依赖关系逐批修复，每批一个 PR/commit，批后回归验证。

### 3A. 波次执行（对应 P1~P6）

- [ ] **3.1** 重复与冗余（P1）：C1 哈希重复合并 / C2 同名裁决 + Playbook 闭环
- [ ] **3.2** 衍生物清理（P2）：`.diff` / `.bak*` / `review_materials_package` 等归档或删除
- [ ] **3.3** 索引可达（P3）：主导航抽样 + `scripts/` / `src/` 入口补链
- [ ] **3.4** 门禁矩阵衔接（P4）：L1 / verify 脚本 + 架构目录 + `backfill_missing_module_id.py`
- [ ] **3.5** 深度前缀队列（P5 = §7）：逐前缀满足退出标准（重复/摆放/导航/内链/衍生物/路径/证据）
- [ ] **3.6** 结构命名合规（P6）：目录命名 / PATH_STANDARD / LAYOUT 对齐

### 3B. 扩展轨（对应 W0~W4，与 3A 可并行）

- [ ] **3.7** W0 控制面落地：办公室 + 仓库根 Playbook + Owner R0~R4 确认
- [ ] **3.8** W1 R0 文档层验收：孤儿/断链 + 大门口索引 + L1=0
- [ ] **3.9** W2 R1 仓库门面与配置：`.gitignore` / 根 README / 密钥抽查
- [ ] **3.10** W3 R2~R3 脚本与工程：`scripts/README` 互指 + 源码根约定
- [ ] **3.11** W4 R4 排除层：依赖/缓存不进库 + pre-commit/CI 配置

### 3C. 回归验证（每批必做）

- [ ] **3.12** 每批完成后复跑 `export_repo_directory_rollup.py` + `sentinel_l1_governance_scan.py`
- [ ] **3.13** 确认新引入断链数 = 0，module_id 重复数不增

**退出标准**：P1~P6 + W0~W4 全部勾完；每批回归 L1 无新增断链。

---

## Phase 4: 真源融合与索引重建

> 目标：完成 canonical 裁决、重生成全部索引、通过施工门禁。

### 4A. Canonical 裁决

- [ ] **4.1** D 类重叠终审：高置信合并 + 低置信登记 [D 类合稿待审登记](./d-class-consolidation-pending-review-register.md)
- [ ] **4.2** 更新 CANONICAL_POINTERS.md 重复簇台账（待创建于 `docs/09_AUDIT/STATE/`）
- [ ] **4.3** 受控文档登记表 [controlled-documents-register.md](./controlled-documents-register.md) 补行

### 4B. 索引重建

- [ ] **4.4** 重生成 `01_BLUEPRINTS/INDEX.md`：`python scripts/governance/generate_01_blueprints_index.py`
- [ ] **4.5** 重生成架构服务目录：`python scripts/governance/generate_architecture_service_catalog.py`
- [ ] **4.6** 运行 `scan_index_health.py` → 目标：零入链候选 = 0（或已书面豁免）
- [ ] **4.7** 更新办公室 [INDEX.md](./INDEX.md) / [CANON/INDEX.md](./CANON/INDEX.md) 与磁盘对齐

### 4C. 最终门禁

- [ ] **4.8** L1 最终全量扫描：`sentinel_l1_governance_scan.py` → 断链 = 0 / module_id 重复 = 0
- [ ] **4.9** P7 施工门禁验收：对照 [施工门禁标准](./CANON/construction-gate-criteria-20260408.md) 三阶段 + 五条
- [ ] **4.10** [蓝图卫生总案](./CANON/blueprint-phase-document-hygiene-master-plan-20260408.md) 退出标准确认
- [ ] **4.11** 更新办公室 [README.md](./README.md) / [AI 交接说明](./project-office-ai-handoff.md) / [全库治理文档导航](./governance-documents-navigation.md)

**退出标准**：L1 断链 = 0；module_id 重复 = 0；施工门禁三阶段全通过；INDEX 与磁盘完全对齐。

---

## 执行备忘（滚动记录）

| 日期 | 批次 | 动作摘要 | commit/PR |
|------|------|----------|-----------|
| 2026-04-13 | Phase 0 | 修复 L1 脚本 SyntaxError；归档旧任务清单至 CANON/ARCHIVE | — |

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-13 | 首版：四步 Pipeline 统一主线，整合 P0~P7 / W0~W4 / README 7 步 |

## 相关文档

- [项目办公室 README](./README.md) — Pipeline 总览入口
- [治理工具总索引](./governance-tools-index.md) — 脚本命令与复跑顺序
- [施工门禁标准](./CANON/construction-gate-criteria-20260408.md) — Phase 4 验收依据
- [蓝图卫生总案](./CANON/blueprint-phase-document-hygiene-master-plan-20260408.md) — 清洁退出标准
- [REPO_WIDE 全仓治理总图（已归档）](./CANON/ARCHIVE/repo-wide-file-governance-task-list.md) — P0~P7 / §7 退出标准详情
- [蓝图终稿任务清单（已归档）](./CANON/ARCHIVE/blueprint-phase-closure-task-list.md) — 任务 1~7 + W0~W4 历史勾选
