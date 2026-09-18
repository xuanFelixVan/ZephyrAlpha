---
ttl: task_bound
completes_when: 接力车道把未修项（BRK-083 空壳核销 / ROOR 扫描面真源合一）落地或被总包核销
---

# 注册表一致性车道 · 接力清单（st-ff-registry-20260918）

> 逐 BRK 状态。数字全部 2026-09-18 本机实测（命令见各行），非转抄普查。
> 表述纪律（裁定#325）：本车道只报"检出 N 件通过且已被证明能红"，不用"全绿"这个词。

| BRK | 修前实测 | 修后实测 | 状态 | 落点 |
|---|---|---|---|---|
| BRK-074 | 普查称"文档 5 vs DB 27，漂移 5.4 倍" | **重跑生成器后产物与 HEAD 逐字节相同**（环节 341/边 114/锚点 588/无锚点 5 全一致）→ **该条不成立**，5 与 27 是两套口径 | 已改判 + 已治本（口径显式化） | `generate_battle_map_diagram.py` 双口径行 + 口径映射表 |
| BRK-075 | step 五态 151/157/20/8/5 vs anchor status_snapshot 八值 200/164/147/39/16/11/10/1，两套无映射 | 生成器现算三套口径分布 + step五态→判定输入映射表，锚点合计 588 与总数行互验 | 已修（生成器产，禁手工对齐） | 同上 §状态口径映射表 |
| BRK-079 | policy 引用幻影域 1（D_SIGNAL） | **0 未登记幻影引用**；D_SIGNAL 显式登记为退役引用（不删，净删属 Owner 门位） | 已修 + 可机判（BM-INV-008 8a） | `battle_map_domain_policy.yaml` §retired_domain_references |
| BRK-080 | 34/75 域无任何 flow_stage 允许 | **0 域无环节归属**（flow_stage 并集 43 + 横切兜底 33 = 覆盖 75/75） | 已修 + 可机判（BM-INV-008 8b） | policy §cross_cutting_stage_domain_coverage（FF-13/14/15/16，与骨架 §3.3 同源）+ `align_battle_map.py` |
| BRK-081 | 19 域未被 business/tool 裁定；D_PLAN 出现在 allowed 却未分类 | **0 未分类 / 0 分类↔白名单矛盾**（D_PLAN→business，其余 18→tool） | 已修 + 可机判（BM-INV-008 8c/8d） | policy §domain_classification |
| BRK-082 | FDR 68 域 vs depgraph 75；FDR 缺 11、depgraph 缺 4 | **depgraph→FDR 差集 = 0**（补登 11 条，FDR entries 83→94）；**FDR→depgraph 差集 = 4**（全部登记为 Owner 门位净删项，未删） | 已修 | `functional_domain_registry.yaml` 新条目 + §retirement_pending_owner_gate |
| BRK-083 | D_SIGLEGACY 0 节点 / D_TEST 0 节点 / `docs/03_modules/_domain_red_blue_validator/` 空目录 | D_TEST 已在 FDR 登记为**空壳域**（stability=deprecated，注明 0 节点）；D_SIGLEGACY 同批归 FF-14；空目录仅登记 | **部分**（登记项，未删=Owner 门位；`docs/03_modules/**` 本车道禁写） | FDR D_TEST 条目 note；policy FF-14 domains |
| BRK-084 | summary 手写 73/19/5/1，by_tier 11+28+34=73 但实测列表 12/28/34=74（漂移 1）；19/5/1 三值无任何机械真源 | summary 由 `check_registry_consistency.py --refresh-summary` **现算**：total_registries 75、by_tier 12/29/34=75（**漂移归零**）、broken **0**（旧 broken=1 的机判根因=REG-FUNC-DOMAIN-001 缺 `status` 键，已补 active） | 已修 | ROOR §summary（含 `legacy_manual_claims_replaced` 如实留痕旧手写值） |
| BRK-062 | 索引称"已建"但 3 件产物不存在（PAN-BUILT-17/21/16） | **现役产物存在 18/18**；已退役 4 件（03/16/17/21）单列 🗃已退役，不再计入已建口径；覆盖率口径改为剔除退役项（57.9%→52.9%） | 已修（改生成源，未直接改产物） | `generate_panorama_registry.py` `_build_status_label` + stats 段拆分；PAN-BUILT-16 补 `status: retired` |
| BRK-063 | 5 项高优先全景图未建 | 未硬建（新建类一夜建不完） | **出施工包** | `lanes/registry_BRK-063_construction_pack.md` |
| req_tdchainJ_02 | `family_registry` 不存在 | 生成器 + 派生册落地并挂 ROOR（REG-STD-FAMILY-001）：`total_standards=4` / `total_families=4` / `family_unassigned=4` | 已落地（含诚实缺口） | `scripts/governance/standards_governance/generate_standard_family_registry.py` → `.../catalogs/standard_family_registry.yaml` |
| R-015 | 对账域"六件并存" | 实测**七件**（多出 `trading/settlement_reconciliation.py`，MOD-TRADING-003/production/有测试）；七件全部有测试 | 出对照表 + 权威入口建议 | `lanes/registry_recon_six_implementations.md` |

## 未修 / 卡在哪（如实）

1. **`family` 归属未填**：`config/standards.yaml` 4 条 STD-* **全无 family 字段**（实测），生成器不臆造 →
   `family_unassigned=4`。补齐输入需在 standards.yaml 每条加 `family: A|B|C|D`（合法域来自
   `governance_family_vocabulary.yaml` 的 4 值），再加 `--check` 即可归零。属**语义裁定**，非本车道可代裁。
2. **BM-INV-008 未接进提交门禁**：本轮只落 `align_battle_map.py`（对齐检测器，`severity: warn` 君子协定沿用）。
   要不要升成硬阻断门禁 = 门禁语义变更，按 R-010① 归总包。
3. **`fully_scanned/pending_scan` 的扫描面真源合一**：本车道已停止在 ROOR 手写这两个数，
   并把"扫描覆盖以 `registry_consistency_contract.yaml` 为准"写进 note；但**该 contract 仍只覆盖 15 册**
   （实测 `len(contract['registries'])=15` vs ROOR 75 册）→ 扫描面缺口 60 册未闭合，属 FF-14 工作量。
4. **测试**：`standard_family_registry` 生成器的测试文件在头注释 TESTS 字段已声明路径
   （`tests/governance/standards_governance/test_generate_standard_family_registry.py`），
   本轮**未落该测试文件**（预算让位于七件对账表与 BM-INV-008 三组能红探针）→ 接力第一优先补。
5. **RULING-REFERENCE**：本车道全程只写 `R-0NN`/`req_tdchainJ_NN`/`#ARCH-*` 已登记号，
   未自取新裁定号（§4 取号权归总包）。

## 能红证据（三组，均 2026-09-18 实测）

对 `align_battle_map._check_domain_registry_consistency` 做输入扰动：

| 探针 | 扰动 | 期望 | 实测 |
|---|---|---|---|
| RED-1 | 摘掉 `cross_cutting_stage_domain_coverage` 的域并集 | 无归属域数暴涨 | uncovered = **33**（基线 0） |
| RED-2 | 从 `domain_classification` 摘掉 `D_PLAN` | 未分类 + 白名单矛盾同时报 | unclassified=1，conflict=**['D_PLAN']** |
| RED-3 | 引用一个不存在的域 `D_NOT_A_REAL_DOMAIN` | 幻影引用立即报 | phantom = **['D_NOT_A_REAL_DOMAIN']** |

基线（扰动前）四类差集全为 0，即 BM-INV-008 **既能红也能白**，不是恒真门禁。
另：`generate_standard_family_registry.py` 的真源缺失路径为**抛错 exit 1**（不静默产出空册冒充"已建"）。
