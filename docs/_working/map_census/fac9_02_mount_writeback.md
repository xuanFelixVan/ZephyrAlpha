---
ttl: task_bound
completes_when: 总筹消化本回填报告（锚修复核/11 行总筹清单/第二刀测试脱钩随批落地）后，本件转归档
title: 图9 策略工厂 挂图升级 车道F2 挂载回填报告
owner: ZephyrAlpha-Owner
session: st-map9-f2-20261003
---

# 图9 策略工厂 车道F2 挂载回填报告

> 会话 `st-map9-f2-20261003`｜2026-10-03｜真源=`fac9_01_mount_candidates.yaml`（449 行，db394dfb23）。
> 交付：`config/strategy_production_map.yaml` mechanism 挂载层机生落图（CAS 写回，幂等对拍过）+ 本报告。
> 前置门三查全过：候选表在 HEAD（db394dfb23）｜图头 purpose_legend 12 条 + schema '0.3'（62b59093d0）｜校验器 exit 0。

## 一、新增节点计数（字段化）

- mechanism 节点 **323**（=census 可挂 333 − 呈总筹 11 + 任务单 4-b 明令附加件 1）；全图 nodes **339**（主干 16 + 机制 323），edges 16 不变。
- 挂载判定：census 可挂 333 行中 **322 行入图**（verdict 1×181｜2×61｜3×77｜4×3），**11 行呈总筹**（§四），**反面 116 行不上图**（§五）。
- by_stage（机制节点数，node_id 前缀组）：

| stage | 件数 | stage | 件数 | stage | 件数 |
|---|---|---|---|---|---|
| E0 | 15 | E1F | 2 | E6 | 14 |
| E1 | 12 | E1G | 10 | E7 | 22 |
| E1A | 3 | E2 | 6 | E8 | 34 |
| E1B | 4 | E3 | 78 | E9 | 8 |
| E1C | 8 | E4 | 81 | MAP | 2 |
| E1D | 10 | E5 | 4 | 合计 | **323** |

  E4=81 = census 78 + stage 未定重判 3（§四）+ 闭卷闸附加件 1（§三）；序号按候选表行序组内递增。
- build_status 机生判定（真路径在盘=built，否则 pending；不做半态人工判读）：**built 308 / pending 14**。pending 14 全清单：MOD-BT-226/233/231/006/218/228/215/222/223/232、dir:_domain_ml_serve/deep_review_model_adapter、dir:_domain_ml_serve/codegen_model_adapter、dir:_domain_data_eng/quality_sla_breach_predictor、MOD-PA-002..024（区间成员注册不全）——均为 ownership 未登记或无实体可解析的诚实占位，F3/F4 批回填时顺手翻案。
- purpose_tag 分布：进货带出生证 55｜考试咽喉说了算 72｜外来经翻译成标准件 77｜病历有人翻 26｜上岗前先实习 14｜钱跟着确定性走 34｜在库按月体检 10｜重活夜里干 15｜不讲通不花钱 5｜加池子才准入 4｜赚亏拆开看 8｜图有人守 2（合计 323）。

## 二、主干未动声明 + 两锚修清单（唯一允许的主干改动）

**声明**：16 主干节点（stage/lane）与 purpose_legend 12 条零改动；git diff 全量核验=恰 2 行删除（下表两处 module_ref 旧值）+ 3758 行插入（mechanism 块），无第三处主干变异。

| # | 节点 | 旧值 | 新值 | 依据 |
|---|---|---|---|---|
| 1 | FAC-E4 | `MOD-BT-039` | `MOD-BT-027` | 039=C4 翻译共享引擎名实错位（F1 报告 §二-1）；改挂 E4 真身代表件=分层验证管道 `src/zephyr/backtest/services/layered_validation_pipeline.py`（ownership 已实现，verdict-1 E4 行） |
| 2 | FAC-E1A | `MOD-BT-035` | `scripts/backtest/strategy_intake_inventory.py` | 035=C2 粗筛灌表与车道A名实不符；爬取器考古=C1 人工版盘点归一（SOP-C Step C1，MATURITY production，597 条实战漏斗入口）；无独立编号（文件头仅域蓝图 MOD-BT-001），故按闭卷闸同款用真路径代码锚 |

**随锚修的机制层注记**：census 行 `MOD-BT-039（C4 翻译共享引擎，E4 挂点名实错位见报告）` 按 census 原样仍挂 E4（机生不改判）；其真家在 E3（翻译引擎，同族 MOD-BT-041..075 皆在 E3），**建议总筹下一批把该行 stage 重归 E3**，F2 不越权代判。

## 三、BT-201 定谳执行（任务单 4-b）

- census 行 `MOD-BT-201`（E7 前哨对账器，真身 `scripts/backtest/forward_post.py`）→ 机制节点 FAC-E7-M-002，挂 E7 保持 ✓。
- `src/zephyr/backtest/core/closed_book_gate.py` → **census 外唯一新增机制节点**，module_ref=真路径，name_zh=`闭卷读取闸（module_id 冲突待改号）`，挂 E4，考试咽喉说了算。af:closed_book_gate（ALGO_FLOW 外部真源行）另按 census 照挂 E4，两身份并存不混。

## 四、stage 未定 14 行处置（禁猜纪律）

- **3 行按 F1 报告 §四「基础设施数据库存储（E4 速度）」组判入 E4**：dir:_domain_data/data_compression_archiver（压缩归档）、MOD-INF-063（Redis 共享状态层）、dir:_domain_data_eng/cold_data_archive_manager（冷归档）。
- **11 行判不出单环节 → 呈总筹（未挂图，禁猜）**：MOD-INF-016（Shared+Core，F1 已注「横切无单环节归属」）、MOD-LLM_SECURITY（LSG，服务 E1B/E2/E3/E1G 四站）、MOD-INF-034（模型画像器，同横切）、MOD-INF-015（全系统遥测）、strategic_message_bus（战略消息总线）、MOD-INF-OPS-ALERT-FEED（运营告警）、research_asset_versioning、llm_agent_router、alt_source_health_manager、alt_data_catalog、spectral_guard。总筹参考口径：LLM 三件（LSG/agent_router/spectral_guard）可考虑与 model_profiler 一起归入一个「LLM 供力面」钉位（首触点 E1B 或算力面 E0），其余横切基建建议随 E0 或立「全图横切」挂载规约后批。

## 五、未上图反面摘要（116 行，全量见 census verdict=反面）

反面行 stage 字段在 census 中留空（未定），家族分布按 F1 报告 §五：全系统旁观基建（灾备/盘点/遥测/拓扑/日志）、执行与高频域（hot_plane/latency/shared_memory，图9 boundary 明排高频/做市）、币圈件（markets=[cn_a] 外）、TDM 编制件（decision_map/validation/trigger/结算）、AI 运营域（cross_layer 治理九件+orchestrator 四件+intelligence 记忆四件+feedback_loop 三件同名陷阱）、退归/placeholder（BT-026 退归实证、079/097-101/133/140/210/219/234 无实体）、产品非机制（087/093/095 联赛参赛策略）。置信分布 low77/medium23/high16。本批零消费、零改判。

## 六、病历挂载（fac9_01_report §六 15 本）

§六 15 本逐本挂到机制节点 casebooks（只挂册不挂个案）；机械匹配到 §六 组件的候选行 **26 行**全部贴「病历有人翻」（任务单手记 18 行为近似，机械匹配实数 26，逐行清单=机生台账 gen_report.json，差异请总筹复核）：

| 册 | 挂载节点（候选行） | 说明 |
|---|---|---|
| 1 因子研究案例库 | MOD-L02-027 | E4；「+E1C 挖掘前查库」未挂（E1C 组无查库行为行），总筹酌定 |
| 2 N试次账本 | MOD-BT-200 | E4 ✓ |
| 3 预审判定台账 | **回退挂 MOD-BT-091**（E2 预审门=台账写入者） | 设施行 BT-152/153=census 反面行（无实体），不上图 |
| 4 考试成绩+判定书台账 | MOD-BT-078 | 设施行 census 判在 E6（建议环节 E4，差异挂账总筹） |
| 5 衰减死因册 | MOD-BT-018 + signal_degradation_monitor + distribution_drift_monitor | E6 三钉 ✓ |
| 6 过拟合裁定档案 | overfitting_protection_gate | E4 ✓（adjudicator 本体无 census 行） |
| 7 回测run档案图书馆 | **回退挂 MOD-BT-022**（E4 报告聚合判定） | run_archive/verify_run_archive 均无 census 行 |
| 8 试验台账红证 | MOD-BT-228/032/033/034 | E4 四钉 ✓ |
| 9 进货台账 | MOD-BT-231 | E1 ✓ |
| 10 翻译件台账 | **回退挂 MOD-BT-190**（E3，translated_manifest 产出件） | manifest 非 module 无行 |
| 11 模拟盘病历族 | MOD-BT-223 + sim_platform_journal + MOD-BT-094(sim_governance) | E7 ✓（sim_deviation_report=MOD-BT-092 与 census「恐慌反弹策略深度化」撞号，未挂） |
| 12 联赛档案 | league 四件 | E7 四钉 ✓ |
| 13 模型版本注册表 | model_version_registry | E1E ✓ |
| 14 全域事实台账 | universal_fact_ledger | E1G ✓ |
| 15 复现演练档案 | replay_drill（E4）+ crisis_drill_monthly（E7） | ✓ |

15 本全部 ≥1 环节挂载，F4 覆盖账本三红之二预检应绿（终判归 F4）。

## 七、E1F 与 MAP 两处特殊挂载（任务单未细化，机械处置挂账）

- **E1F 2 行**（factory_grid_executor/lane_f_grid_adapter，F 车道）：FAC-E1F 节点未建（图头自注「2.4 接线跨线欠账」），挂所属 stage 主干 FAC-E1，node_id 保持 FAC-E1F-M-001/002 前缀。F 车道节点补挂后可改 parent。
- **MAP 2 行**（MOD-BT-080 校验器/MOD-BT-081 对抗测试）：图级设施无环节归属，挂 E0（工厂运维站），贴「图有人守」，node_id 前缀 FAC-MAP-M-001/002。总筹若立「全图横切」规约可迁。

## 八、校验器输出原文（写后实跑）

```
WARN: FAC-E9: 入库位待定（施工时定）: 待定（E9 施工时定）
WARN: FAC-E1: 数据源待定（未接/未入库）: 待定:c1_market.news_data
WARN: FAC-E1D: data_ref 非可校形态（非 c1_ 表且无路径分隔符）: ig_fact
PASS: 结构校验通过（nodes=339 edges=16）
EXIT=0
```
（三条 WARN 均为升版前既有待定注记，非本批新增。）对抗测试 `test_strategy_production_map_adversarial.py` **35/35 绿**（含本批第二刀脱钩修复，见 §九）。

## 九、随批发现与 ride-along（交总筹，未入本批提交面）

1. **对抗测试第二刀脱钩（已修复+staged，随总筹批落地）**：真图进 mechanism 层后，`_v02`/`_v03` 基底 deepcopy 真图会继承 323 机制节点，致 2 用例红（chief 第一刀只对图例升版脱钩）。修复=`_strip_mech()` 基底剥离机制节点，用例自控种群；35/35 复绿。文件 `tests/backtest/test_strategy_production_map_adversarial.py`，**不在本批 1 文件提交面内**，staged 待总筹。
2. **path_ownership_map 漂移两处**（不碰注册册，呈报）：①MOD-BT-001（域蓝图）被标为 run_archive/overfitting_adjudicator/strategy_intake_inventory/strategy_screen_c2/verify_run_archive 等 ≥7 无关路径 owner；②MOD-BT-092 同时被标 sim_deviation_report.py 与 census「恐慌反弹策略深度化」双源；③MOD-BT-231（进货台账对账器）实体在盘（scripts/backtest/intake_ledger_recon.py）而 ownership 未登记——本批 build_status 机械判 pending 的 14 件多源于此。
3. **token 登记顺序注记**：batch_creation_tokens 为前缀扫描式通道，物理顺序=本报告文件先落盘、token 随即登记（同工作树态，先于任何提交），与任务单「新建前登记」的字面序差异在此挂账。

## 十、幂等对拍结果

- 写入通道=`safe_write_text` CAS（expected_base_sha256=读时内容 hash，写后回读校验 written=True）。
- 首轮曾发生一次**坏块落盘即被进程外复核逮住**（name_zh 含 ASCII 冒号未加引号，YAML 解析崩）——按纪律从 HEAD 恢复单文件后修引号判据重写，坏块零残留（过程全录会话日志；CAS/写后复核两层防线实测有效）。
- 收敛后**重跑机生脚本=字节对拍一致，跳写**（IDEMPOTENT-SKIP），幂等铁律闭环；最终 diff=2 锚修行+3758 插入行，主干区段零变异。

## 十一、提交面

- 本批提交=**恰好 1 文件** `config/strategy_production_map.yaml`（git_commit.py --session st-map9-f2-20261003，提交后 git log -1 --name-only 核验）。
- staged 留待总筹批：本报告 + capability 册 map9_f2_writeback token + 对抗测试第二刀脱钩（§九-1）。
