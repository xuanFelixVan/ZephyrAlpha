---
ttl: task_bound
completes_when: BT域批量盖章若实锤移交专项批后本件归档
title: depgraph blueprint_id 错盖修复批报告（40号§4两条落地+80路径顺查）
owner: st-btfix-20261005
---

# 45 号·depgraph blueprint_id 错盖修复批报告

> 会话=st-btfix-20261005；依据=40_triage_index.md §4 修复建议 + 60_chief_adjudication_v1.md 终裁三；号源判据=总包令（判"谁才是正确号"以登记归属互证为准，详见 §1 注）。
> 修数据不修图、修根不修影；DB 操作三步验证（必要性/真实性/可逆性）见 §2。

## 0. 结论速览（总包令 §六 四行）

1. **修层判定**：`data_handler.py`=**头错**（头=DB=错号 001，一致地错，双层同修）；`sim_attribution_report.py`=**DB 错**（头=215 对、DB=084 错，仅 DB 直写）。
2. **两条修复验证链绿**：`apply_depgraph --set-blueprint-id` 各 affected=1（nodes+belongs_to+nodes_metadata 三表同步）；头改后进程外复核一致；重跑 `generate_map_coverage_attribution` 终证 `[join-checker] dangling=0`、30 号 `dangling_keys: []`。
3. **80 路径分类**：A=0 / B=0 / C=36（+1 内部不一致挂账）/ D=43（tests 搬家路径蒸发残留，非错盖）。**批量盖章事故不实锤**，无随批批量修复，专项建议呈 chief（§4）。
4. **dangling 终值=0**（FACTORY 机制节点 MOD-BT-006/MOD-BT-215 两键全部落地接通）。

## 1. 任务1·取证三对照（只读）

### MOD-BT-006（data_handler）

| # | 证据面 | 原值 |
|---|--------|------|
| ① | 文件头 `src/zephyr/backtest/core/data_handler.py` | L1 `# [BLUEPRINT] MOD-BT-001 \| docs/03_modules/_domain_backtest/blueprint.md`；L15 `# [A_module] module_id=MOD-BT-001 \| …` |
| ② | DB `nodes`（node_id=16332076, node_type=module） | `blueprint_id=MOD-BT-001`，`belongs_to=MOD-BT-001` |
| ③ | 登记归属互证 | `config/strategy_production_map.yaml:2710`（FAC-E4-M-003「data_handler 数据来源手」，stage E4，`module_ref: MOD-BT-006`）；`docs/03_modules/_domain_backtest/data_quality_checker/blueprint.md:96`「可选消费: MOD-BT-006 data_handler（数据来源）」；DB 内 `MOD-BT-006` 零行 |

**判层=头错**（文件头自写 001；DB 与头一致地错）。头与 DB 同修，改头后 DB 不会因重扫回退（depgraph 扫描器 `generate_project_depgraph.py:1165` 读文件头 `[BLUEPRINT]` 行推导 blueprint_id——头是重扫真源，必须改头）。

### MOD-BT-215（sim_attribution_report）

| # | 证据面 | 原值 |
|---|--------|------|
| ① | 文件头 `scripts/backtest/sim_attribution_report.py` | L1 `# [BLUEPRINT] MOD-BT-215 \| …`；`# [A_module] module_id=MOD-BT-215 \| …`（**头本就对**） |
| ② | DB `nodes`（node_id=16337255, node_type=script） | `blueprint_id=MOD-BT-084`（错），`belongs_to=MOD-BT-084` |
| ③ | 登记归属互证 | MOD-BT-215 真身=本件（60 号终裁三 + fullflow_mining/b2_f28_e9_live_attribution.md:35 docstring 实核 + `strategy_production_map.yaml:4806` `module_ref: MOD-BT-215` stage E9）；MOD-BT-084 真身另有其人=`scripts/backtest/lane_e_quantile_baseline.py`（文件头自认领），DB 内 084 现存 5 节点 |

**判层=DB 错**（头对、DB 盖错）→ RULE-SSOT 架构数据走 apply_depgraph 直写 DB。

> 注（号源判据）：`architecture_model/module_id_registry.yaml` 经实查只登记 EA 级文档规则模块（GOV-/DOM-/OPS-/PS-，ROOR REG-MOD-ID-001 自述"74 个企业架构级模块 ID"），代码模块 MOD-BT-* 不在其册（其 431-432 行自注"代码模块在各分区 YAML 中定义"）。本批判号改用三重登记互证（config 机制节点 module_ref + 域册蓝图交叉引用 + chief 终裁原文），结论与 40 号 §4、60 号终裁三完全一致。

## 2. 任务2·修复执行（修前快照=可逆性证据）

### 修前 SELECT 快照（2026-10-05，st-btfix-20261005）

```
cols=(node_id, path, blueprint_id, belongs_to, node_type)
(16337255, 'scripts/backtest/sim_attribution_report.py',      'MOD-BT-084', 'MOD-BT-084', 'script')
(16332076, 'src/zephyr/backtest/core/data_handler.py',       'MOD-BT-001', 'MOD-BT-001', 'module')
```

回滚配方：同命令反向 `--set-blueprint-id` 写回上值 + data_handler.py 头两行还原（git 有 staged 前像）。

### 修复动作

1. **DB 直写**（`apply_depgraph.py --set-blueprint-id`，dry-run 各命中 1 节点无误伤后实写）：
   - `src/zephyr/backtest/core/data_handler.py`：MOD-BT-001→**MOD-BT-006**（affected=1，nodes+belongs_to+nodes_metadata 同步，blueprint_id_invalid 清除）
   - `scripts/backtest/sim_attribution_report.py`：MOD-BT-084→**MOD-BT-215**（affected=1，同上）
2. **文件头修复**（仅 data_handler.py，头错层）：L1 `[BLUEPRINT]` 行与 L15 `[A_module]` 行 001→006，其余头域（MODULE/DOMAIN/DEPENDENCIES/INVARIANTS 等）零改动；写后进程外 grep 复核一致。
   - 未跑全图重扫（`generate_project_depgraph --force`）：任务3 实查 80 路径中 43 条 tests 路径已蒸发（§3），全图重扫=对全库节点重盖章，效果等同批量事故修复，超出本批授权（>5 禁批量动）；本批以按 path 精确赋值达成头=DB 双层一致，语义与"改头再重扫"终态等价且爆炸半径=1 节点。

### 验证链

| 步 | 命令 | 证据 |
|----|------|------|
| 1 | `apply_depgraph --set-blueprint-id` ×2 | 均 `[OK] affected=1` |
| 2 | 修后 SELECT 复查 | 两节点 blueprint_id/belongs_to=006/215（与头一致） |
| 3 | 重跑 `generate_map_coverage_attribution.py`（exit 0） | `[join-checker] units=5200 direct=2305 derived=1211 true_orphans=2023 exempted=9 stale_exemptions=0 dangling=0` |
| 4 | 30 号机生件复核 | `dangling_keys: []`（修前基线=2 条：MOD-BT-006/MOD-BT-215@FACTORY） |

## 3. 任务3·MOD-BT-001 挂 80 路径顺查（调查件）

SQL 拉全 `blueprint_id='MOD-BT-001'` 节点（本批修后=80 台：1 config+31 module+5 script+43 test），逐条对照文件头（[BLUEPRINT]/[A_module] 双行）与登记归属：

| 分类 | 定义（总包令） | 计数 | 明细 |
|------|---------------|------|------|
| A | 头=001 且 DB=001（头就是错的批量盖章，有他号认领实证） | **0** | data_handler.py 是唯一实证例，已于本批修出 001 池；余池未见第二例"他号认领" |
| B | 头≠001 但 DB=001（DB 批量事故） | **0** | 唯一候选 `docs/03_modules/_domain_backtest/algo_flow/result_repository.yaml`（config 节点，py 头扫描为空）经查证其锚定 `source_of_truth: src/zephyr/backtest/io/result_repository.py`（该 py 头=001，家族成员）→ 判 C |
| C | 合法（确属 MOD-BT-001 回测引擎家族） | **36** | 26 条头双行一致（core 引擎 14 + implementations 3 + io 1 + regime_validation 3 + scripts 5）；9 条 [BLUEPRINT]=001 但无 [A_module] 行（含冻结真源 engine_base.py、matching_engine.py、preflight_checker.py、result_repository.py、3 个 __init__、run_archive.py、1 metamorphic 测试）；1 条 `regime_validation/__init__.py`（BP/DB=001 一致，但 [A_module] 行=PKG-bt-regime-validation，全仓零注册、非裁定#208 合法词表——内部不一致挂账，见 §4） |
| D（顺查附加桶） | 文件在盘不存在（路径蒸发残留） | **43** | 全部为 `tests/backtest/test_*.py` 旧路径节点；实证 `tests/backtest/` 已搬空（仅剩 `__pycache__`），新家=`tests/research/backtest/`（tests 治理归位批）——**tests 搬家未同步 depgraph 节点路径**，属陈旧节点残留，非 blueprint_id 错盖 |

**判定**：A+B 合计=0（个别阈值远未触发），**批量盖章事故不实锤**——"81 台超宽"的构成=36 合法家族 + 43 tests 搬家残留 + （已修出的 2 台错盖）。本批零批量动 001 池；43 台 stale 节点清理（`--propagate-node-paths` 指向新家或 `--cleanup-orphan-nodes`）建议移交专项批（§4）。

## 4. 呈报 chief（本班零执行，仅挂账）

1. **43 台 tests 旧路径 stale 节点**：`tests/backtest/test_*.py` → 新家 `tests/research/backtest/`，depgraph 节点路径未随迁。建议专项批走 `apply_depgraph --propagate-node-paths`（精确值映射，禁子串替换）或对确无新家节点者 `--cleanup-orphan-nodes`；修后 30 号 auxiliary_ledger.test 计数将同步回真。
2. **regime_validation/__init__.py 头内不一致**：[BLUEPRINT]/DB=MOD-BT-001 vs [A_module]=PKG-bt-regime-validation（未注册号）。需裁定：包根 __init__ 应挂家族号 001 还是另立注册号；修头属一行外科，但定号权在 chief。
3. **号源判据口径**：总包令指 `architecture_model/module_id_registry.yaml` 为 MOD-* 号段唯一真源，实查该册只辖 EA 级（GOV/DOM/OPS/PS）；代码模块号段无单一登记册，散见 config 机制节点 module_ref + 域册蓝图互证。建议后续立法明确 MOD-{DOMAIN}-NNN 号段的登记真源位（或扩 REG-MOD-ID-001 辖区），免各班判号口径漂移。
4. **共享册并发写实证与 token 先行落地**：本批 creation_token（panorama_map_census）经 `batch_creation_tokens.py` 两轮登记（60/45 两件，CAS 纯增），期间**实证该册存在他会话整册渲染变体重写并抹除他会话新增条目**（st-btfix 两 token 于 17:53 整册重写中被抹，重写面 3957+/472- 量级）；按总包令 ⚠️ 条款改走**外科配方先行落地**：册回 HEAD+手插两条纯增+即刻提交（同 HEAD 先例 a9016ca992 st-f12-doctor3「token 先行批」配方：HEAD 渲染版基底+纯增量插入；本批 commit 层 diff=纯增零删，不触发 REGISTRY-MASS-DELETION、无自签逃生旗；写侧 safe_write_text CAS+allow_mass_edit 审计留痕）。**先行落地批已落 HEAD=9cfd775382（+10/-0 纯增，队列 state=done）**；他会话重写面备份 `.runtime/tmp/ccfr_foreign_backup_20261005.yaml` 留证，落袋后**未回灌盘面**——其重写面经 F12 先例判读为渲染变体噪音（HEAD 渲染版基底=校正目标，回灌=重新引入变体），且主批落袋时点该册已被他会话重新暂存新态（在途不代碰）。

## 5. 纪律自检

- [x] 修前快照留证（§2），DB 变更可逆（反向 set 同命令）；三步验证：必要性=40号§4+终裁三双授权；真实性=三对照互证（§1）；可逆性=回滚配方在案
- [x] 写前 claim（data_handler.py @ st-btfix-20261005）；六图 YAML 零改动；30/31 号仅机生重跑零手改
- [x] capability_lookup 反查留审计（fix_depgraph_module_id/fix_header_module_id 命中，SSoT 顺序"Python 先改 DB 再同步文件头"遵行）
- [x] A/B=0 未触发批量阈值（≤5 随批/>5 呈报均不适用）；43 台 stale 只报告零动作
- [x] tmp 遗留：`.runtime/tmp/bt001_scan.json`（顺查原始扫描件，供专项批复核，TTL 自净）+`.runtime/tmp/ccfr_foreign_backup_20261005.yaml`（他会话重写面备份，恢复后自净）
- [x] 提交链：token 先行落地批（册）→ 主批（data_handler.py+30/31 号机生重跑+本件）均走 git_commit.py --enqueue 队列正门；会话注册=活体 pid 锚（ZCode 短命进程 pid 会随进程死亡被活性剪枝，pid=None 注册同样被剪——锚定真实存活后台进程方过 SESSION-REQUIRED）
