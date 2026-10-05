---
created: 2026-09-30
ttl: task_bound
title: A8 车道全流通 P0/P1 修复簿（F73 验证让位/F17 崩溃治愈/F20 实证移交/F38 宏观实体重建）
session: st-circ-a8-20260930
parent: 00_skeleton.md（总包）
prescription_source: s5_skeleton.md §5（P0 处方）
---

# A8 · 全流通修复簿（s5 §5 处方执行）

> 纪律：CapabilityLookup 6 关键词（league/sim_pocket/promotion_advisory/lane_g/resource_profile/macro_regime，
> session=st-circ-a8-20260930 审计留痕）；每项改前核现状；claim 后改；测试+ruff 双净；git_commit.py 正门。

## 一、结论速览

- **F73 A/B 联赛执行器**：他队已治（st-circ 系列 3992e4b024，09-30）→ 本车道**验证让位**，零重做。
- **F17 车道C 挖掘停摆**：根因①已治（`lane_c_formula_miner.py` residualize SVD 崩溃修复+回归测试+实弹烟测出分）。
- **F16/F18/F20**：实证核验后**分别定性**——F16=环境面（ollama 已复活）、F18=在流（非断）、F20=触发链全在，上游断点移交 F96 工单域。
- **F38 宏观传感器缺件**：实体两件按 NB1-B5 处方重建落地（映射表+传感器），单测 14 绿+CH 实弹探针出分（weather=46.41）。

## 二、逐项台账

### 1. F73 A/B 联赛（P0-3）——他队已治，验证让位

- 现状核验：`scripts/backtest/league_judge.py`（546 行）在 HEAD，事件挂点
  `pipeline_events.OPTIONAL_DUE_KINDS["league_judge_due"]` + 月度档 `maybe_emit_monthly` 触指（三处接线）全在；
  league_registry.yaml A 席 STR-E-TIMING-001 已回填；配套 archive/restore/monthly_snapshot/registry 四件全在。
- 落地 commit：**3992e4b024**（[st-c9-final] 联赛 13 件一次整投，2026-09-30——msprt e-process+BHY q=0.10 族守门
  +ρ>0.7 相关性闸，三态 promote/eliminate/observe，月度幂等判定书；处方真源=fullflow_mining/03_promotion_ab/02_ab_league.md 堵点2/6）。
- 验证证据：四 league 测试 **76 passed**（tests/backtest/test_league_{judge,registry,archive,restore}.py）；
  实弹探针 `league_judge.py --check-rulers` → RC=0（access_std STD-SIM-ACCESS-002 frozen / switch draft / pair_engine=msprt / rho=0.7）。
- 与处方差异说明：处方"喂 promotion_advisory"——判定书落 `data/backtest_artifacts/league/judgments/`（F74 promotion_advisory
  证据面走 sim governance/偏离台账独立闭环，league 判定书经 review_policy.judge=promotion_combo_gate 在终审窗汇流；
  判定器自述"建议只落判定书不碰注册表 lifecycle"=st-c9 交付设计，非缺件）。让位理由：他队当夜已交付全链，重做=净零违例。

### 2. F17 车道C 公式挖掘（P1-4）——根因①已治（本车道唯一代码修复之一）

- 现状核验（推翻骨架表层的"调度停摆"初判）：Windows 计划任务 `ZephyrAlpha_FactoryLaneC` **在册且在跑**
  （verbose：上次运行 2026-09-26 10:00:01，上次结果 0；下次 10-03）；`.runtime/logs/factory_lane_c.log` 09-19/09-26 两场全链跑完 exit 0。
- **真根因①（本车道治）**：`lane_c_formula_miner.py:457` fitness 评估 `residualize → np.linalg.lstsq` 抛
  `LinAlgError: SVD did not converge`（09-26 10:00 场实弹 Traceback 在 log）——基座掩码 `~isnan` 放行 ±inf 进设计矩阵；
  未捕获 → 整场挖掘崩溃零产出 → 三周零新公式候选（09-16 后 E1C 批断流）。
- 修复（即写即 add）：`residualize` 掩码改 `np.isfinite(baseline).all(axis=1)` + `LinAlgError` 降级返回原值（单程序坏≠全场崩）；
  `run_mine` 验收循环加单程序 try/except（同事故防御纵深）。
- 测试：`test_lane_c_formula_miner.py` +4 用例（inf 基座回归/病态设计降级/fitness 工厂容坏/原有 22 绿不破）→ 全文件 26 passed。
- 实弹探针：`mine --smoke --population 30 --generations 3 --universe-n 40` → **跑通出分**（5 候选 incr_ic 0.0107~0.0270，
  落 `data/strategy_intake/lane_c_candidates.csv`，birth_source=pop30/gen3 可溯源）。披露：烟测 5 行入生产台账
  （birth_source 可辨，E2/E4 门在下游把关；手工删账违反数据操作纪律，故留痕不删）。
- **真根因②（环境面，已复活）**：09-26 10:29 C3 翻译/lane_b 全 theme 失败=ollama (11434) 连接拒绝；
  本车道 10-01 00:57 实测同样关闭 → 直接启动 `ollama.exe serve`（进程 in reaper keep 册 `ollama.exe serve`）→
  TCP 11434 OPEN + `/api/version` 0.34.1。披露：`ZephyrAlpha_OllamaServe` 计划任务手动触发返回上次结果 267014
  （任务宿主侧终止），守护直启成功；任务宿主侧病理（为何 AtLogOn 进程消亡+计划任务拉起即被终止）移交值班班，非代码域。

### 3. F16 车道B / F18 车道D（P1-4）——实证定性，零代码变更

- **F18 lane_d**：**非断**。09-26 场 intake 报告（factory_lane_c.log:4259）`D_three_high E1D-20260926-102753 candidates=20`
  → three_high_candidates.csv（09-29 仍有更新，29KB）。骨架"无今日产物证据"过时；下游 E2 deferred=5 属 F21 考核面（骨架已判通）。
- **F16 lane_b**：触发链在（周六链 `factory_intake_pipeline run --with-lane_b`），断点=ollama 关闭（09-26 十二 theme 全军覆没
  实录在 log）。ollama 已复活（见上）→ 下个周六窗自动恢复；其消费面（翻译/C3）同步恢复。**零代码变更**。
- F15 车道A（社区 597 条）：骨架 P2 低频定性维持，不在本车道。

### 4. F20 车道G 胃进货（P1-4）——触发链实证全在，上游断点移交 F96

- 处方最小件"intel inbox 事件→lane_g_stomach_intake 触发器"**已由 st-chief4x-gut-20260927 全量建成**，本车道逐环实证：
  ①快路径=`intel_harvester.py:390 trigger_lane_g_intake`（落新班 Popen fire-and-forget，main:441 挂尾）在；
  ②慢路径兜底=DataScheduler `lane_g_intake_sweep` 槽（schedule.yaml:129，22:30 每日）+
  `scheduler._run_special_schedule:544` 分支 + `run_intake_sweep` 执行体全在；**实证 09-30 22:30:00 已跑**
  （scheduler_run.log apscheduler executed successfully，0.3s 空扫=收件箱全消化诚实体）；
  ③台账侧 lane_g_seen_urls.csv 09-17 批消化 7 条在案。
- **剩余断点在上游 F96（胃情报源）**：`intel_harvester.py` 自身无任何调度触发（无计划任务、无 schedule.yaml 槽；
  `ZephyrAlpha_ModelIntelScan` 是 model_intel.scanner 另一件事，与本链无关）→ 收件箱 09-16 后无新班 → 快路径休眠。
  骨架 F96"升级工单在案"即此；**移交 F96 工单域**（本车道不越界重建：净零铁律+跨车道领地）。

### 5. F38 宏观传感器缺件（P1-6）——实体两件重建落地

- 核验：`git show 9ec1ae0f6e` 仅 capability_canonical_file_registry +10 行（token 先行批），实体未随；
  `git log --all`+pickaxe 全史零代码 blob；.aidrafts 仅 schema 类目件无传感器实体 → **按处方重建**（重建依据=NB1-B5 卡
  `docs/_working/night_sweep/b_audit/nb1_b5_cn_macro_family.md` R1/R3 原文，CREATE-GUARD token 复用先行批两枚，零新 token）。
- **R1 映射表** `config/macro_indicator_series_map.yaml`：MAC↔series_code 唯一翻译层。series_code 全部经 CH 实弹核验
  （2026-09-30 distinct 2261 序列逐一对照；TDM 已挂 8 条中 7 条映射到活序列，CN-008 MLF 无活源=诚实空挂 available:false）；
  附 groups 四组权重（A货币/B流动性信用/C海外/D增长政策 各 0.25）+direction+pit_lag_days（引 REG-MAC-001 发布纪律）。
- **R3 传感器** `src/zephyr/regime/features/macro_regime_sensor.py`：as_of+pit_lag 取数（禁前视）→滚动分位→四组加权
  →天气分 0-100→L01 月级谨慎度因子 [1.0,1.5]；fail-closed（四组全空 ok=False 不编造）；query_fn 注入（测试零 CH）；
  R2 vintage pub_ts 升级路径注记预留。TDM-E-L1-S0 module_ref 接线（改指本件）属永久图 DB 直写域，**留待图车道**（处方 R3 后半）。
- 测试：`tests/regime/features/test_macro_regime_sensor.py` 14 用例（映射表校验/PIT 裁剪/滚动分位/方向计分/编排注入/fail-closed/
  重加权/转义），全绿。
- 实弹探针：`python -m zephyr.regime.features.macro_regime_sensor --as-of 2026-09-30` → ok=true，
  **weather_score=46.41，caution_factor=1.0359，covered_weight=1.0**（货币组 87.0=利率低位宽松支撑；流动性信用组 4.7=
  社融/M2 窗口低位压制；海外 55.2；增长政策 38.7）——读数与宏观直觉一致，管线全通。

## 三、变更清单与提交

| 件 | 类型 | 说明 |
|---|---|---|
| scripts/backtest/lane_c_formula_miner.py | 修复 | residualize inf 掩码+LinAlgError 降级；run_mine 单程序容错 |
| tests/backtest/test_lane_c_formula_miner.py | 测试 | +4 事故回归用例（26 绿） |
| config/macro_indicator_series_map.yaml | 新建 | R1 翻译层（token 复用 9ec1ae0f6e 先行批） |
| src/zephyr/regime/features/macro_regime_sensor.py | 新建 | R3 消费模块（token 复用先行批） |
| tests/regime/features/test_macro_regime_sensor.py | 新建 | 14 用例（tests/ 豁免） |
| docs/01_.../capability_canonical_file_registry.yaml | 登记 | +1 词条 s5_fix_b 簿（CAS safe_write，12423 词条 safe_load 过） |
| docs/01_.../module_translation_registry.yaml | 登记 | +1 翻译词条 macro_regime_sensor（大白话 plain_zh，7949 条） |
| depgraph（PG 直写） | 登记 | file 节点两枚：src/.../macro_regime_sensor.py=15758387、config/macro_indicator_series_map.yaml=15775268（blueprint 缺席=marked missing 非阻断） |
| docs/_working/total_circulation_night/s5_fix_b.md | 新建 | 本簿 |

## 四、移交与让位清单

1. **F73**：让位（他队 3992e4b024 已治，本车道只验证）。
2. **F20 上游**：intel_harvester 调度缺位 → F96 工单域（升级工单在案）。
3. **TDM-E-L1-S0 module_ref**：改指 macro_regime_sensor.py → 图车道（永久图 DB 直写域，apply_* 正门）。
4. **OllamaServe 计划任务病理**（267014 终止+AtLogOn 进程消亡根因）→ 值班/维护班（环境类）。
5. **REG-MAC-001 册务**（entry_count 15→16 修正+候选转正）→ 随 R3 接线批（NB1-B5 R5，属册务车道）。
6. **E8/C1 alloc_budget_daily 停摆（P0-2）/F82 order_daemon（P0-1）**：本车道未领，留待后续 lane。
