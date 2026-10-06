---
ttl: task_bound
title: "lane_e 车道补全报告（B方案）"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# lane_e 车道补全报告（B 方案，EXEC-D7）

Owner 裁定 lane_e 走 B 方案：补全落盘逻辑+挂上调度，把编制外半成品（MOD-BT-089/090 三模型分位数回归对比实验，只 print 不落盘、不在 _LANE_SPECS）转正为第七条进货车道。本报告留档补全内容、语义判定、挂槽位置与实测读数。

## 1. lane_e 语义判定

- **上游**：`scripts/backtest/lane_e_enhanced.py`（MOD-BT-089）——沪深300（000300）指数次日收益的三模型分位数区间预测对比实验：linear_qr（sklearn QuantileRegressor）/ gbr_quantile（GBR loss=quantile）/ lgbm_quantile（LightGBM objective=quantile），q05/q50/q95 三分位，特征全部 ≤T 收盘可知（滞后收益 1/5/10/20、滚动波动 5/20、涨跌宽度、动量比），滚动 500 日训练前推一日（PIT 无同窗泄漏），IS+OOS 双窗评估（覆盖率+区间均宽+pinball 双标准）。
- **输出**：原 CLI 只 print 对比矩阵到 stdout；转正后每模型产出一条**稳定假说候选**（内容寻址 id 只锚假说全文，实证读数随班进 mechanism_hint 不参与寻址——同假说跨班不换 id 不重复入账）。
- **基线身份**：图 FAC-E1E 明文"只当基线对台，不直接当交易信号"——候选文本自带该声明，运动员不兼任裁判，判定权在 E2 预审/E4 考试。

## 2. 补全内容（全部落既有模块，零新建 .py）

| 文件 | 补全 |
|------|------|
| `scripts/backtest/lane_e_enhanced_cli.py` | `run_intake()`（窗口实验→假说候选→内容寻址去重→出生证三件套→卸台账）+ `run_intake_sweep()`（never-raise 调度入口，同族 lane_g 范式：整体异常→ERROR 告警 ok=False；单窗口失败→failed_windows 留痕 WARN，成功窗口照常卸货）+ CLI `--intake/--dry-run` 旗标（原实验打印路径原样保留） |
| `scripts/backtest/factory_intake_pipeline.py` | `_LANE_SPECS` 追加 lane E 条目（lane="E"/name="e1e_quantile_forecast"/compute_class="local"/intake=lane_e_candidates.csv）；`run_pipeline` intake_sources["E"] 存在才消费（同车道 I 语义）；`cmd_race` 计分板补 E 台账读数 |
| `scripts/backtest/intake_ledger_recon.py` | `LEDGER_CHANNELS` 追加 `"lane_e_candidates.csv": "E"`（按其表头注释"新增车道改本表"；未入 CONTENT_ADDRESSED_PREFIX——E1E 前缀校验器未通用化，同 lane_g 先例） |
| `src/zephyr/data/config/schedule.yaml` | 新槽 `lane_e_intake_sweep`：cron `30 21 * * *` 每日，executor default，max_instances 1 |
| `src/zephyr/data/scheduler.py` | `_run_special_schedule` 追加 lane_e_intake_sweep 臂（总闸 `data/runtime/lane_e_intake_sweep.disabled`、alerter 注入、异常降级告警不反噬调度器，与 lane_g 臂逐字同构） |
| `scripts/governance/generators/generate_resource_profile_registry.py` | `SLOT_OVERRIDES` 追加 lane_e_intake_sweep（light/dmin 30/mem 2.0） |
| `config/resource_profile_registry.yaml` | 生成器 `--check --auto-regen` 再生（drift 1→0，total_entities 102→105） |
| `tests/backtest/test_lane_e_enhanced.py` | 新增 10 测：卸货 schema 对齐+幂等两跑零重复 / dry-run 零写 / 单窗口降级留痕 / 双窗口全炸零写盘 / sweep ERROR/WARN 降级 / 槽位分派+alerter 注入+非本槽穿透+总闸缺省 / E2 必需列断言 |
| `tests/backtest/test_factory_intake_pipeline.py` | 新增 `test_lane_e_registered_light`（lane=E + local 轻档 + intake 路径） |
| `data/strategy_intake/lane_e_candidates.csv` | 真实班产物：3 行（每模型一条），birth_channel=E |

- 台账 schema 与 B 车道候选模板逐列对齐（candidate_id/theme/hypothesis_zh/mechanism_hint/horizon/universe/birth_channel/birth_batch/birth_source），E2 `load_candidates` 必需列（candidate_id/hypothesis_zh/birth_channel/birth_batch）全携带；写盘必经 `intake_ledger_recon.append_ledger_rows` CAS 唯一写口（safe_write_text，禁裸 to_csv 追加）。
- 候选 id=CAND-md5_12("E1E:"+假说全文)，去重复用 `lane_b_idea_generator.load_existing_ids`（委托防双真源，同 lane_g 先例）。

## 3. 挂槽判定（tasks.yaml 不动的理由）

tasks.yaml 是 D_DATA 数据集成器任务清单（table/source/capability/provider 面，DATA-TASK-COMPLETENESS gate 管辖）；lane_e 是**计算时刻非数据源**的编排型调用——scheduler.py :590 既有明文先例："编排型调用走特殊槽（dloop_post 同款先例，不入 tasks.yaml——计算时刻非数据源）"，lane_g 2026-09-27 即按此挂 `lane_g_intake_sweep` 特殊槽。故 lane_e 照搬同构挂法：schedule.yaml 槽（21:30 每日）+ `_run_special_schedule` 硬编码白名单两侧同挂（防 R-021 假通道）+ 资源画像注册表 `data_slot_lane_e_intake_sweep` 实体。槽位选 21:30：日K 16:30/资金 18:00/事件 19:00/研报 20:00 之后、nightly_financial 22:00/lane_g 22:30/integrity_check 23:00 之前错峰空窗；与交易日历零耦合不进 TRADING_DAY_GUARDED_SCHEDULES（同 lane_g 全周先例，非交易日无新数据=内容寻址幂等 no-op 零写盘）。E0 问闸：compute_class=local（Owner B 方案裁定 heavy 档不适用；实验本体 sklearn/LightGBM CPU 轻；图 FAC-E1E 的 local_gpu 指 Kronos/KAN 深化族）。

## 4. 治理副作用（登记不隐瞒）

- 资源画像注册表再生 diff 除本车道实体外，还带入两个**先存漂移**实体（`data_slot_nightly_news_score`/`sch_commit_perf_report`，2026-10-02 上次再生后他线新增槽）——生成器四源全量再生、条目禁手工增删，拆单反而要求手改生成册，故整批保留并在此留痕。
- 先存破损（他线资产，登记不代修）：`tests/scripts/test_generate_resource_profile_registry.py` 3 例计数断言滞后（槽位 26→34/ps1 实体 26→35/factory_lane_c cron 漂移）；`tests/infrastructure/test_resource_schedule_regen_check.py` 2 例因 `scripts/register_resource_regen_check_task.ps1` 已于 32047b6276（st-construct-20261002）纯删除但测试仍引用。本班改动前后失败集逐一比对无新增。

## 5. 测试与实跑读数

- 单测全绿：`tests/backtest/test_lane_e_enhanced.py`（12，含新 10 测）+ `test_factory_intake_pipeline.py`（15）+ `test_intake_ledger_recon.py`（18）= 45 passed；lane_g 接线/调度器/排班一致性/面板 cron 单源（再生后）/容量配额等周边套件全绿。
- **真实班 #1**（批 E1E-20261004-203744，IS 2020-01-01..2023-12-31 + OOS 2024-01-01..2026-10-03 滚动）：双窗口零失败，卸货 **3 行**（CAS after_sha256=df0d7a34…），台账 3 行 3 唯一 id；实证读数 IS n=408 覆盖率 94.85% 区间均宽 0.03902 pin50 0.007558 / OOS n=104 覆盖率 79.81% 区间均宽 0.03272 pin50 0.010306。
- 首班曾实证一处缺陷并当场治本：OOS 末端原写死 2026-06-30，数据增长后 dropna 后样本 546<550 触"样本不足"——OOS 末端改滚动 T-1（`_default_oos_end`），夜间车道窗口跟着日历滚。
- **真实班 #2（幂等验证）**：同日重跑 `--intake`（批 E1E-20261004-204343），generated=0 / skipped_dup=3 / 未写盘（written_to 缺席）/ 台账 sha256 不变（df0d7a34…与班1 CAS after_sha256 一致，零重复零追加）。

## 6. 遗留与移交

- **提交形态（共享工作区高峰实况）**：共享暂存区被他队 WIP 污染（scheduler.py 他队 98 行 staged 含悬空 import news_score_daily :432；IMPORT-INTEGRITY 对整面 staged 扫描阻断），直连多轮被不同门禁依次拦截后按宪法 §2.6"队列是正门"走 `--enqueue` 落 **q-20261004-st-datasop-20260930-0010（6 文件，快照入袋零丢失，position_ahead=12 排队自动落地）**：lane_e_enhanced_cli / factory_intake_pipeline / intake_ledger_recon / 双测试 / lane_e_candidates.csv。落地 hash 查 `python scripts/commit_queue.py status --session st-datasop-20260930` 的 landed_id。
- **留盘移交 5 件**（全部本会话实改、工作树完好、逐件受阻原因留痕）：
  1. `src/zephyr/data/config/schedule.yaml`（lane_e_intake_sweep 槽 21:30）+ `src/zephyr/data/scheduler.py`（_run_special_schedule 臂）——scheduler.py 他队 staged WIP 悬空 import 未落地前不可随批（HELD-OVERLAP 不硬闯）；槽先落会产生临时"槽无臂 no-op warn"窗口，臂随他队 settle 后即补齐。
  2. `scripts/governance/generators/generate_resource_profile_registry.py`（SLOT_OVERRIDES lane_e 行）+ `config/resource_profile_registry.yaml`（再生 drift 1→0，total_entities 105）——RESOURCE-SCHEDULE 闸检出 09:35 窗 2 条**先存**阻断冲突（sch_paper_session/sch_sim_bridge_execute/sch_decision_chain_sentinel 他会话新增实体，与 lane_e 21:30 槽无关），随冲突处置班一并落。
  3. 本报告件 `D7_lane_e_complete.md`——CREATE-GUARD token 需 capability_canonical_file_registry.yaml（render 投影册）在册；该册正被 st-gomap-chief-20261004 render 循环覆写（盘面相对 HEAD 缺条目，batch_creation_tokens fail-safe 拒写，意图 API/REG-CAPCAN-001 正道登记后随 render 落册），token=待补（capability=factory_backend, created_by=st-datasop-20260930, merge_evaluation 已拟）。
- CONTENT_ADDRESSED_PREFIX 未纳入 E（E1E 前缀 id 校验需 make_candidate_id 域前缀参数化，动 B 车道真源函数，超本工单半径；对账对该台账 integrity 校验跳过，dup/蒸发校验仍生效，同 G 现状）。
- IS 窗末端 2023-12-31 为固定历史锚（训练段语义，无陈旧性问题）；如需"滚动 IS"由后续工单裁定。
- 默认窗口/模型清单为模块常量，如需夜批参数化（如 --models 透传）留待后续。
