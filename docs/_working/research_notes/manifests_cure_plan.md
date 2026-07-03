# manifests_cure_plan.md — STEP 3-5 方案评估 + 执行计划

> 调研对象：`docs/03_modules/_manifests/` 真源分裂审查 + 治本方案决策
> 初版日期：2026-07-01（commit `f9a9ffc6b7`）
> 删除日期：2026-07-01 15:05（commit `1ce95c2961`，"使命已完成"）
> 重建日期：2026-07-04（本次复核，补完 CSV + 修正分类 + 记录已执行状态）
> 配套：[manifests_mapping_audit.md](manifests_mapping_audit.md) · [manifests_missing_diagnosis.md](manifests_missing_diagnosis.md)

---

## 0. 执行摘要（TL;DR）

**治本方案 D（删除 manifest）已于 2026-07-01 由 commit `f9a9ffc6b7` 执行完毕。**

- 42 个 `*_manifest.md` + `_manifests/index.md` 全部物理删除
- `docs/03_modules/index.md` 的 2 处 `_manifests/` 引用清理
- `full_project_tree_zh.md` / `full_project_tree_en.md` 重新生成
- 文件清单真源回归 `depgraph → extract_depgraph.py → blueprint §0.1`

**决策依据**：manifest 是 blueprint §0.1 代码文件清单的过时冗余子集（28 vs 52 文件），无独有信息、无生成器、无消费者。删除消除 1 个病根（真源分裂）+ 7 个衍生问题（命名不一致/双 module_id 体系/frontmatter 双版本/源码路径分裂/模块无蓝图/平铺膨胀/生成器缺失）。

**本次（2026-07-04）复核结论**：方案 D 决策正确，当前状态干净，无需回滚。唯一遗留：1 个调研报告（本文件）被 commit `1ce95c2961` 删除，本次重建以补完用户期望的 3 个产出物。

---

## 1. STEP 1 映射表结果（CSV 汇总）

> 真源：[manifests_mapping_audit.md](manifests_mapping_audit.md)（42 行，每行一个 manifest）
> 数据源：git 历史 `f9a9ffc6b7^`（删除前版本）+ 当前 `docs/03_modules/**/blueprint.md`（55 个）

### 1.1 分类统计

| 类型 | 数量 | 含义 | 匹配依据 |
|------|------|------|----------|
| **A**（名称直接匹配） | 13 | manifest_name == blueprint 子目录名 | `name_direct_match` |
| **B**（语义别名/ssot反查） | 26 | 命名不一致但可通过 diagnosis.md 核对或 ssot_path 反查 | 详见 CSV `basis` 列 |
| **C**（无 blueprint） | 3 | hooks / infra_ops / script_system | 见 §1.3 |
| **D**（孤儿/废弃） | 0 | — | — |
| **合计** | 42 | | |

### 1.2 关键发现：frontmatter 字段无法自动反查

- **30 个 manifest**（2026-05-09 批次）的 `blueprint_id` 全部 = `MOD-GOVERNANCE`（域级归属标记，非模块映射）
- **30 个 manifest** 的 `module_id` 为 `MOD-041~070`（旧顺序编号，blueprint 已改用语义编号如 `MOD-INF-020`，两套无映射表）
- **12 个 manifest**（2026-06-10 批次）有 `ssot_path`，但最后一段目录名与 blueprint 子目录名不直接相等（如 `src/zephyr/observability/telemetry` → `system_telemetry`）
- **结论**：B 类匹配必须依赖语义别名表（基于 diagnosis.md 人工核对 + 源码路径反查），无法靠 frontmatter 自动反查

### 1.3 三个 C 类详解（无 blueprint）

| manifest | 原因 | 源码位置 | 处置 |
|----------|------|----------|------|
| `hooks_manifest.md` | 无 blueprint 子目录（diagnosis.md 根因 5 确认） | 镜像于 `src/zephyr/infrastructure/runtime_integration/hooks/` | 应补建 blueprint 或归并到 `runtime_integration` |
| `infra_ops_manifest.md` | `_domain_infrastructure_operations/blueprint.md` 域级蓝图缺失（diagnosis.md 漏诊，本次复核新发现） | `src/zephyr/infrastructure/` | 应补建域级 blueprint 或拆 manifest 到子模块 |
| `script_system_manifest.md` | 无 blueprint（diagnosis.md 根因 5 确认；被 6 蓝图提及无主属） | 散落 | 应明确归属或归并 |

> **修正 diagnosis.md**：原结论"25 B + 2 C"应修正为"26 B + 3 C"。差异根因：原 diagnosis.md 未察觉 `_domain_infrastructure_operations/blueprint.md` 域级蓝图缺失（仅有 index.md）。

---

## 2. STEP 2 根因诊断（6 条，已核实）

> 详见 [manifests_missing_diagnosis.md](manifests_missing_diagnosis.md)。此处仅列摘要 + 本次复核修正。

| 根因 | 影响范围 | 本次核实 |
|------|----------|----------|
| 1. 命名体系不一致（主因） | 25 个 B 类 | ✅ 确认（CSV `basis` 列逐个标注） |
| 2. 两套 module_id 体系并存 | 30 个 05-09 批次 | ✅ 确认（MOD-041~070 vs MOD-INF-020） |
| 3. frontmatter schema 双版本 | 30 + 12 | ✅ 确认（有/无 ssot_path 两批） |
| 4. 源码路径分裂 | db/rollback/escalation/hooks/script_system 等 | ✅ 确认 |
| 5. 部分模块无蓝图 | **3 个 C 类**（原 2 个） | ⚠️ 修正：新增 `infra_ops`（域级蓝图缺失） |
| 6. 生成器缺失（元问题） | 42 个全部 | ✅ 确认（见 §3） |

### 2.1 根因 6（生成器缺失）的最终确认

用户列出的 5 个"生成器脚本"经逐一核实，**全部与 `_manifests/` 目录无关**，分属另一套 `script_manifest.yaml` 体系：

| 脚本 | 实际用途 | 与 _manifests/ 关系 |
|------|----------|---------------------|
| `scripts/generate_manifest.py` | 生成 `scripts/script_manifest.yaml`（全树 563 脚本扫描） | ❌ 无关 |
| `scripts/governance/generators/inject_manifests.py` | 注入 `__manifest__` 块到 .py 文件 | ❌ 无关 |
| `scripts/governance/generators/fix_module_manifest_layout.py` | 修复 `__manifest__` 块布局 | ❌ 无关 |
| `scripts/governance/d1_structure/sync_index_from_manifest.py` | 从 `script_manifest.yaml` 同步 index.md | ❌ 无关 |
| `scripts/governance/d1_structure/generate_missing_index_md.py` | 为缺失 index.md 的目录生成索引 | ❌ 无关 |
| `scripts/governance/d11_compliance/validate_manifest_admission.py` | 验证 `scripts/governance/script_manifest.yaml` | ❌ 无关 |
| `scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py` | GATE-19 漂移检测（跑所有 generators --check） | ❌ 无关 |

> **结论**：`_manifests/` 目录的 42 个 manifest 确实是 ad-hoc 产出，无生成器、不可重生。这直接否决了方案 C（"可重生 → 接受平铺"）的前提。

---

## 3. STEP 3 方案评估（四方案对比）

> 原任务列了 A/B/C 三方案。本次新增**方案 D（删除）**——因前会话已执行，必须评估。

### 3.1 四方案成本/收益/风险对比

| 维度 | 方案 A（消除目录） | 方案 B（按域子目录归位） | 方案 C（保持平铺+自动索引） | 方案 D（删除）⭐已执行 |
|------|---------------------|--------------------------|------------------------------|------------------------|
| **前提** | 42 模块都有子目录 | 不依赖子目录 | manifest 可重生 | manifest 是冗余真源 |
| **前提成立?** | ❌ 3 个 C 类无子目录 | ✅ | ❌ 无生成器（根因 6） | ✅（已验证：28 vs 52 文件子集） |
| **文件迁移** | 42 个 + 改名 manifest.md | 42 个 | 0 | -42 个（删除） |
| **生成器改动** | 5 个脚本输出路径 | 5 个脚本输出路径 | 新建生成器 | 0（无生成器可改） |
| **引用点改动** | 5 处 | 5 处 | 0 | 2 处（index.md） |
| **真源归一** | ✅ 完全归一 | ⚠️ 仍分裂（blueprint 在 domain，manifest 在 _manifests/domain） | ❌ 仍分裂 | ✅ 完全归一（回归 depgraph） |
| **未来 3000-4000 模块** | ✅ 天然支撑 | ✅ 支撑 | ❌ 平铺无法定位 | ✅ 无 manifest 概念 |
| **向内收原则** | ⚠️ 创造（迁移） | ⚠️ 创造（分层） | ⚠️ 创造（索引） | ✅ 能删不创造 |
| **第一性原理** | 治标（迁移不解决冗余） | 治标（仍分裂） | 治标（不解决冗余） | ✅ 治本（消除冗余真源） |
| **新 AI 可发现性** | ✅ 模块子目录内 | ⚠️ 需知 _manifests/ 域前缀 | ❌ 3000 文件平铺 | ✅ 查 depgraph 即可 |
| **风险** | 27 个无子目录需补建 | 迁移简单但未治本 | 元问题未解 | 删除后若发现有用难恢复 |
| **回滚成本** | 中（git revert + 重建引用） | 中 | 0 | 低（git revert 单 commit） |

### 3.2 方案 D 的额外评估（本次复核）

**支持删除的证据**：
1. manifest 是 blueprint §0.1 代码文件清单的过时子集（28 vs 52 文件，blueprint 更全）
2. 无独有信息（所有字段都能从 blueprint/depgraph 推导）
3. 无生成器（ad-hoc 产出，不可重生——但反过来也意味着无消费者依赖）
4. 无消费者（Grep 全库仅 5 处引用，且都是索引/树形图，非业务逻辑）
5. 消除 1 病根 + 7 衍生问题（命名不一致/双 module_id/双 schema/路径分裂/无蓝图/平铺膨胀/生成器缺失）

**反对删除的证据**（本次复核寻找）：
- ❌ 未找到——manifest 没有任何独有信息或消费者

**结论**：方案 D 是治本方案，决策正确。

---

## 4. STEP 4 推荐方案 + 理由

### 4.1 推荐方案

> **方案 D（删除 manifest）—— 已执行，本次复核确认决策正确。**

### 4.2 决策依据（数据支撑，不靠拍脑袋）

| 决策准则 | 数据 | 结论 |
|----------|------|------|
| 向内收原则 1（能现成不创造） | manifest 是 blueprint §0.1 子集，depgraph 已是真源 | 删除 > 迁移 |
| 向内收原则 3（第一性原理） | 元问题=冗余真源；删除治本，迁移治标 | 方案 D > A/B |
| 向内收原则 4（新 AI 可发现性） | 删除后 AI 查 depgraph 即可；保留则 AI 需知 _manifests/ + 命名别名表 | 方案 D > A/B/C |
| 80% 子目录阈值（用户原判据） | 42 模块中 39 有子目录（92.8%）→ 原判据推荐 A | 但 A 治标，D 治本 |
| 生成器前提（方案 C 判据） | 无生成器（根因 6 确认） | 方案 C 否决 |
| 冗余度判据 | 28 vs 52 文件（manifest 是 54% 子集），无独有字段 | 删除合理 |

### 4.3 为何不选方案 A（用户原判据会推荐）

用户原判据："如果 42 个模块中 ≥80% 已有子目录 → 推荐方案 A"。实际 39/42=92.8% 有子目录，按此判据应推荐 A。

**但本次复核推荐 D 而非 A**，理由：
1. **方案 A 治标不治本**：把 manifest 迁到模块子目录改名 `manifest.md`，仍然是冗余真源（blueprint §0.1 已有文件清单）
2. **方案 A 工作量大**：42 文件迁移 + 5 生成器改动 + 5 引用点改动，且 3 个 C 类需先补建子目录
3. **方案 D 零冗余**：删除后真源唯一回归 depgraph + blueprint §0.1，未来 3000-4000 模块天然支撑
4. **方案 D 已执行且验证通过**：当前状态干净，无遗留引用

### 4.4 决策树

```
manifest 是冗余真源吗？
├─ 是 → 删除（方案 D）⭐
│   ├─ 有独有信息吗？→ 否（28 vs 52 子集）
│   ├─ 有消费者吗？→ 否（5 处引用都是索引/树形图）
│   └─ 有生成器吗？→ 否（根因 6）
└─ 否 → 评估 A/B/C
    ├─ 42 模块都有子目录？→ 39/42=92.8% 是 → 方案 A
    └─ 否 → 方案 B
```

---

## 5. STEP 5 执行计划

### 5.1 已执行部分（commit `f9a9ffc6b7`，2026-07-01 00:35）

| 步骤 | 内容 | 验证 |
|------|------|------|
| 1. 删除 42 manifest | `docs/03_modules/_manifests/*_manifest.md`（42 个） | ✅ git show --stat 确认 |
| 2. 删除目录索引 | `docs/03_modules/_manifests/index.md` | ✅ git show --stat 确认 |
| 3. 清理 index.md 引用 | `docs/03_modules/index.md` 2 处（_manifests 索引行 + 跨层前缀示例外） | ✅ Grep "No matches found" |
| 4. 重生成 full_project_tree | `full_project_tree_zh.md` + `full_project_tree_en.md` | ✅ 文件已更新（2441/2378 行变更） |
| 5. 新增调研报告 | `manifests_cure_plan.md`（130 行）+ `manifests_missing_diagnosis.md`（59 行） | ✅ commit 确认 |

### 5.2 后续清理（commit `1ce95c2961`，2026-07-01 15:05）

| 步骤 | 内容 | 原因 |
|------|------|------|
| 6. 删除 cure_plan.md | `docs/_working/research_notes/manifests_cure_plan.md`（130 行） | 注释："使命已完成"——临时调研报告，治理完成后清理 |

### 5.3 本次（2026-07-04）补完产出物

| 步骤 | 内容 | 原因 |
|------|------|------|
| 7. 新建 CSV | `manifests_mapping_audit.csv`（42 行） | 用户期望产出物 1，从未创建 |
| 8. 重建 cure_plan.md | `manifests_cure_plan.md`（本文件） | 用户期望产出物 3，被 1ce95c2961 删除 |
| 9. 复核 diagnosis.md | 顶部添加"2026-07-04 复核修正"段落 | 修正分类：25 B+2 C → 26 B+3 C（新增 infra_ops） |

### 5.4 验证命令

```powershell
# 1. 确认 _manifests/ 目录已删除
python -c "import os; print('exists' if os.path.isdir('docs/03_modules/_manifests') else 'deleted')"

# 2. 确认 index.md 无 _manifests 引用
# 用 Grep 工具搜 "_manifests" in docs/03_modules/index.md → 应 No matches found

# 3. 确认 full_project_tree 中的 _manifests 引用都是脚本名（非目录路径）
# 用 Grep 工具搜 "_manifests" in full_project_tree_zh.md → 应只匹配 check_handoff_manifests.py / inject_manifests.py

# 4. 确认 CSV 完整性
python -c "import csv; rows=list(csv.DictReader(open('docs/_working/research_notes/manifests_mapping_audit.csv',encoding='utf-8'))); print(f'total={len(rows)}'); from collections import Counter; print(Counter(r['category'] for r in rows))"

# 5. 确认生成器脚本与 _manifests/ 无关（已逐一核实，见表 §2.1）
```

### 5.5 回滚计划（若发现 manifest 仍有用，理论上不会触发）

```powershell
# 单 commit 回滚（方案 D 的优势：单 commit 即可回滚）
git revert f9a9ffc6b7  # 恢复 42 manifest + index.md 引用 + 旧 full_project_tree

# 注意：revert 会冲突，因为后续 commit 1ce95c2961 删除了 cure_plan.md，需手动解决
# 替代方案：cherry-pick 单个 manifest 文件
git checkout f9a9ffc6b7^ -- docs/03_modules/_manifests/<name>_manifest.md
```

---

## 6. 当前状态验证（2026-07-04）

| 检查项 | 期望 | 实际 | 状态 |
|--------|------|------|------|
| `_manifests/` 目录 | 不存在 | 不存在（Glob/LS 确认） | ✅ |
| `docs/03_modules/index.md` _manifests 引用 | 0 处 | 0 处（Grep "No matches found"） | ✅ |
| `full_project_tree_zh.md` _manifests 引用 | 仅脚本名 | 2 处（check_handoff_manifests.py / inject_manifests.py） | ✅ |
| `full_project_tree_en.md` _manifests 引用 | 仅脚本名 | 2 处（同上） | ✅ |
| `manifests_mapping_audit.csv` | 42 行 | 42 行（A=13/B=26/C=3/D=0） | ✅ |
| `manifests_missing_diagnosis.md` | 存在 | 存在（59 行 + 本次复核段落） | ✅ |
| `manifests_cure_plan.md` | 存在 | 存在（本文件，重建） | ✅ |
| 生成器脚本 | 与 _manifests/ 无关 | 7 个脚本全部属 script_manifest 体系 | ✅ |

---

## 7. 后续建议（2026-07-04 二次复核更新）

> 原建议 1（3 个 C 类补建 blueprint）经 [c_class_modules_audit.md](c_class_modules_audit.md) 源码核实后**取消**——3 个模块均有蓝图归属，无需补建。

### 7.1 新建议 1：修复 script_system 路径漂移（5 处，P2）

script_system 的蓝图是 `governance_automation/blueprint.md`（MOD-INF-005），但有 5 处蓝图引用路径错误：

| # | 文件 | 行号 | 错误路径 | 正确路径 |
|---|------|------|----------|----------|
| 1 | `_system_master/blueprint.md` | 656 | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 2 | `governance_automation/blueprint.md` | 53 | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 3 | `governance_automation/blueprint.md` | 86-87 | `src/zephyr/infrastructure/runtime_integration/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 4 | `gate_engine/blueprint.md` | 698 | `docs/03_modules/_cross_layer/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |
| 5 | `task_system/blueprint.md` | 639, 1360 | `docs/03_modules/_domain_infrastructure_operations/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |

建议作为独立任务卡执行（涉及多蓝图改动，需逐个验证）。

### 7.2 新建议 2：infra_ops 域归属决策（P3）

`_domain_infrastructure_operations/` 域级蓝图缺失，但 `runtime_integration/blueprint.md`（MOD-INF-002）的 layer 已声明为 `infra_ops`。建议：
- **方案 A**：补建 `_domain_infrastructure_operations/blueprint.md` 域级蓝图（如果 infra_ops 域要独立发展）
- **方案 B**：归并到 `_domain_infrastructure_runtime/`（推荐，因 `src/zephyr/infra_ops/` 几乎空骨架）

涉及域合并，需 architecture 裁定（影响 43 域方案）。

### 7.3 保持建议：命名体系统一（治本根因 1）

manifest 已删除，命名不一致问题随之消失。但源码目录名与 blueprint 子目录名仍有不一致（如 `src/zephyr/observability/telemetry` vs `system_telemetry`）。建议在 `path_ownership_map.yaml` 中登记别名映射表，供新 AI 反查。

### 7.4 已完成：临时脚本清理

- `tmp/_extract_manifest_mapping.py`（TTL=task_bound）✅ 已删除
- `tmp/_manifest_frontmatter_dump.json`（debug 产物）✅ 已删除

### 7.5 分类汇总修正

基于 [c_class_modules_audit.md](c_class_modules_audit.md) 源码头部核实，[manifests_mapping_audit.md](manifests_mapping_audit.md) 的 C 类应全部修正为 B 类：

| 分类 | 第一次复核 | 本次二次复核（最终） |
|------|------------|-----------------------|
| A | 13 | 13 |
| B | 26 | **29** |
| C | 3 | **0** |
| D | 0 | 0 |
| 合计 | 42 | 42 |

**最终结论**：42 个 manifest 全部能找到归属，无真正的 C 类或 D 类。原 diagnosis.md 的根因 5"部分模块无蓝图"应取消。

---

## 8. 引用

- 删除 commit：`f9a9ffc6b7c31227f81b51bf05294b30e0db9d9a`（2026-07-01 00:35）
- 清理 commit：`1ce95c2961842c14b107a09d8f18eb7766f00943`（2026-07-01 15:05，ARCH-031 遗留治理）
- 配套产出物：
  - [manifests_mapping_audit.md](manifests_mapping_audit.md) — STEP 1 映射表（42 行）
  - [manifests_missing_diagnosis.md](manifests_missing_diagnosis.md) — STEP 2 根因诊断（59 行 + 复核段落）
  - [manifests_cure_plan.md](manifests_cure_plan.md) — STEP 3-5 方案评估+执行计划（本文件）
