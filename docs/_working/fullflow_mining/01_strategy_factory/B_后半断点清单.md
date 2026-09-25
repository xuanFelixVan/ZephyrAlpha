---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: SF-B 后半断点清单——E2→E3→E4 幂等接线断点 + E7/E8/E9 三缺位件施工前置
date: 2026-09-25
status: mined
---

# SF-B 后半断点清单（F23-F29 挖矿附带产出）

> 组 SF·策略工厂供给链 B 后半（分工册 §二 组 SF）。与 SF-A 的 00_overview.md 不冲突：本册只收 B 后半（E4-E9+台账出生证）视角的断点与施工前置，总链断点以两组合并口径为准。
> 每条断点：位置/现象/证据/影响/修法草案（+工作量+是否本车道可修）。证据日期=2026-09-25。

## A. E2→E3→E4 幂等接线断点清单（重点①）

> 链路应然：E2 过审（c1_backtest.hypothesis_precheck 幂等按 candidate_id）→ E3 构造（auto_construct 幂等按 constructed_manifest；假说轨走 MOD-BT-190 翻译专项）→ E4 考试（c4_batch_due 重事件→c4_batch_screen --auto-only；落账发 c4_batch_completed 轻事件→E5/E6）。

| # | 断点 | 现象与证据 | 影响 | 修法草案 |
|---|------|-----------|------|---------|
| BP-1 | **E2→E3 假说轨无自动接续** | auto_construct 硬编码只认公式轨 `("C","C2")`（factory_intake_pipeline.py:168 `_CONSTRUCT_LANES`）；D/B 假说轨过审后靠 MOD-BT-190 hypothesis_translator **专项手动**跑（translated_manifest 全链仅 5 行 vs lane_b 4 行+候选存量） | 三高/AI 生成假说过审即滞留，E3 产能瓶颈在人工班期 | construct 子命令扩假说轨分支调 hypothesis_translator（或发 transcribe_due 轻 kind）；工作量 M；可修 |
| BP-2 | **E2 过审集读取 fail-silent** | `_e2_passed_by_channel()` CH 不可达时 `except: return set()`（factory_intake_pipeline.py:267-268）——构造静默零产出，报告只显示 constructed=0，无告警无留痕 | 台账故障日=构造无声空转，违反"静默失败"防线（M5 册同类病灶） | 空集分支加 alerter 告警+报告内 fail_closed 字段；工作量 S；可修 |
| BP-3 | **E3→E4 重事件滞留（本清单最硬断点）** | pending_events.jsonl 滞留 2 条 c4_batch_due（2026-09-16，85 件+1 件，attempts=0，**9 天未 drain**）；HEAVY kind 设计上只经显式 drain（pipeline_events.py:143），但无任何授权班次/人执行过 | 考卷件积压 9 天进不了考试；E2→E3 自动链"产了货没人考" | Owner 派工一次 `python -m zephyr.strategy_pipeline.pipeline_events drain --allow-heavy`（handler 本身 --auto-only 幂等增量，实考≈未考件数）；此后把 heavy drain 纳入月度审计班或晨报授权清单；操作分钟级；可修（运行操作非代码） |
| BP-4 | **F06 车道判定书不进统一台账** | f06_e4_wfa_exam 判定写 f06_survivors.csv+E4 档案，**不落 c1_backtest.strategy_screen**；E5 消费面（screen_source bothwin）只认 strategy_screen → F06 幸存者配方永不进 C6 及格集 | 车道 F 成了"平行判定权"（同 run_strategy_validation 引擎、不同台账出口），赛马不可比 | F06 判定行追加落 strategy_screen（verdict=f06_wfa，附 exam_archive 指针），或 screen_source 扩第二表联查；工作量 M；可修；**与 F06 网格图节点补挂欠账（骨架 2.4 跨线项）同班处理** |
| BP-5 | **E4→E5/E6 轻事件无生产消费** | c4_batch_completed 轻事件→run_intake_auto 是 E5/E6 唯一入口，但 6/6 份 intake 报告全是 pytest 泄漏件、注册表 0 条 STR-AUTO——生产链零运转；bothwin 16 及格在账无消费 | 及格集堆积，E5/E6 built 能力闲置 | 先清泄漏报告+修 REPORT_DIR 注入（F25 册堵点 2）→手动触发一次 drain 验证首条自动入库→此后随 c4 落账自动走；工作量 S-M；可修 |
| BP-6 | **幂等键三处三口径（潜在重考/漏考）** | ①auto_construct 幂等键=candidate_id（manifest）；②c4_batch_screen 幂等键=(batch,sid,verdict,source_file) 四键；③c4_batch_due handler 忽略 payload.files 全量 `--auto-only` 重发现（pipeline_events.py:379-382） | 三键各自正确，但同件在"已构造未落账"窗口期重放会重复占 manifest 行→四键判重兜底不重考（安全），而滞留事件 drain 时 payload 85 件清单失真（以发现为准） | 统一文档口径即可（不修代码）：payload.files 仅作告警参考，权威=台账差集；工作量 S |
| BP-7 | **双窗窗口漂移无机检** | OOS 批默认窗终点=动态"上个周六"（c4_batch_screen.py:218-223），IS 冻结批靠 `_BATCH` 常量；screen_source 两职 parity 有测试钉，但 OOS 终点前移无人审计 | OOS 窗随时间自然延长属设计内，但"考卷变了"无台账留痕（知识漂移哨兵只管件不管窗） | OOS 批 run 档案 summary 已记 window（在案），补一条月度窗口漂移播报即可；工作量 S；可修 |

**链级结论**：E2→E3→E4 的**幂等原语三处全对**（candidate_id/manifest 四键/drain 出队），不存在重复考试或成绩覆盖风险；断的是**事件流的手动关口**（BP-3）与**两轨分流**（BP-1/BP-4）。修复顺序建议：BP-3（分钟级解锁积压）→ BP-5（解锁 16 及格消费）→ BP-1/BP-4（M 级接线）→ BP-2/BP-6/BP-7（S 级加固）。

## B. E7/E8/E9 三缺位件施工前置清单（重点②：每件"要建成需要什么"逐条）

### B-E7 模拟盘前哨（missing→可施工的最小件序列）

现状一句话：sim_* 家族 8 件+FSM sim 态+两表 DDL 全在，缺"registry sim 名单驱动的考核闭环"。要建成需要：

1. **考核对象清单器**：registry lifecycle_status=sim 名单读取面（现池=1 件 lane_e_quantile_baseline；若池空心可先以 bothwin 16 及格经 BP-5 自动流转补池）。需要什么=一个 `list_sim_strategies()` 纯函数+注册表只读；工作量 S。
2. **逐日执行挂点**：SIM_DAILY_KINDS FIFO 追加 `e7_daily` kind（deps=sim 账本当日行，照抄 attribution_daily 接线范式——超时/幂等/marker 三件套照抄 run_sim_ledger_daily）。需要什么=pipeline_events 追加 kind+执行体子进程；工作量 S-M。
3. **逐日对账器**：预测 vs 实际偏差日账（复用 sim_deviation_report 口径升频到日，输出=对账行落 c1_backtest.sim_daily_report 或新表）。需要什么=每策略可执行的预测产物（考卷件 build() 权重 or 分位数预测）+当日实际行情——两者 sim 平面已有；工作量 M。
4. **滑点/容量实测档**：图上 E7 硬要求。需要什么=e4-replay（收盘价口径）之上开真单腿档（bridge-execute 已有 QMT 桥真单范式：限价=盘口 ask1/bid1+柜台持仓真源+R-H5E-1 风控闸），或五档滑点扫描桥接（exam_cost_gate 复用）；两案二选一须裁定；工作量 M-L。
5. **考核期状态机**：入期日+N 周+期末判定→FSM sim→shelved（合法边已在）或回 E6 标 decayed。需要什么=E7 考核参数档（N 周/容差/判退线，建议落 config 冻结档仿 exam_scale_cost_gate.yaml 先例）+判定器（{ok,reason,source} 三件套范式照抄 promotion_advisory）；工作量 M。
6. **产出落点裁定**：store_refs"待定（E7 施工时定）"→建议复用 c1_backtest.sim_daily_report（判定台账已在 DDL+在用）+run 档案指针，不建新表；裁定级。
7. **事件接线**：期末判定事件 kind 注册+emitter+drain 面（照抄 c4_batch_completed 轻事件范式）；工作量 S。
8. **与 PR 组 F72 边界协定**：E7=考核期（本清单），F72=转正汇总器（promotion_advisory/promotion_combo_gate 已 built）——共用 sim_pocket 账本，以"期末判定行"为交接物；一行裁定防两组建两套判定。

**净零声明**：八项中 3/5 复用既有件、6 复用既有表，净新增=清单器+日账执行体+参数档。

### B-E8 组装与资金分配（partial→闭环的最短路径）

现状一句话：装配体 MOD-PA-030+事件链已投产（09-15..09-23 七业务日成功 marker），3 枚毒丸已修待重放。要闭环需要：

1. **毒丸重放**：3 条 PIPE-20260923-*（根因 tuple.get() 已于 09-24 治本，allocation_inputs.py:715-719 注释在码）→`pipeline_events drain` 一次+核对 alloc 三表当日行；分钟级；Owner 派工（与 BP-3 同班）。
2. **09-24/25 分配日成验证**：治本后尚无成功 marker 在案，需一次日链自然唤醒验证；零代码。
3. **钱包额度接线**：MOD-PA-030 自述 sim_paper_ledger 接线 diff 待主会话落地——预算产出≠钱包拿额。需要什么=落地该接线 diff（分配→钱包开户额度字段对齐）；工作量 S-M。
4. **策略池来源**：StrategyBook 读 registry/账本——池空心问题同 E7 前置 1（两件共享同一清单器）。
5. **IC_IR 加权口径裁定**：图上法注无实件；最接近=risk_budget_allocator sharpe_weight 模式。需要什么=一行裁定"IC_IR 加权=sharpe_weight 实现"或降级为演进方向；裁定级。
6. **资金渐进爬坡件**：capital_ramp（drawdown 控制爬坡）无独立实件。需要什么=爬坡参数档+回撤→额度系数函数（可挂 maxdd_limit_allocator MOD-PA-013 旁）；工作量 M；可缓（lump 口径先跑通）。
7. **sleeve 落库语义**：alloc_budget_daily 现按 strategy 粒度；sleeve（regime 组）层是否落表待裁（建议=regime 列已隐含，免新表）；裁定级。
8. **TDM 组合流对接**：alloc_budget_daily 的 TDM 侧消费者登记（F48，归 TD 组对账）；跨组欠账登记即可。

### B-E9 实盘归因（partial→闭环的最短路径）

现状一句话：引擎 MOD-PF-007 built+sim 级归因日账已日更（09-24 marker）；缺的三件全卡在实盘数据面与接线。要闭环需要：

1. **IS 分解前置字段**：execution_report DDL 无决策时间戳（FIELD-GAP 实证）。需要什么=schema 增列（架构数据走 apply_*.py 直写 DB 侧）+M7 产出侧回填规则；工作量 M；产出侧在 ex_core/M7 域。
2. **影子组合工作流最小件**：实盘 NAV 旁跑信号复刻对照。需要什么=实盘在跑（**M7 合规门 Owner 报送门位，绝对前置，禁自动施工**）+C4 引擎复刻脚本+对照报告落点（复用 sim_attribution 表构）；工作量 M；Owner 门位后开工。
3. **E9 归因报告落点裁定**：store_refs"待定"→建议=c1_backtest.sim_attribution_daily 表构推广实盘级（attribution_live_daily 或同表加 mode 列）；裁定级。
4. **回灌 E2 接线**：attribution/衰减结论→假说库先验（feedback_loops 两行均无实件）。需要什么=decay_cause 枚举回写 E6 衰减台账+假说库先验标签字段；建议与 E6 反馈环（F25 册堵点 3）同案立项；工作量 S-M。
5. **消费端激活核对**：MOD-PF-007 CONSUMERS 声明 PC-01/D_REPORTING 消费——实件激活度未核（归 TD/FR 组对账面）；登记即可。
6. **风险贡献升级**：占位 1/N→波动贡献（挂 M-11）；登记不施工。

## C. B 后半七册三态汇总（供总筹回写总册）

| 册 | 环节 | 三态 | 一行结论 |
|----|------|------|---------|
| b2_f23 | F23 E4 考试 | 挖干可施工 | built 属实；双器两口径+重事件滞留 9 天=断点 BP-3/BP-4 |
| b2_f24 | F24 E5 去重 | 挖干（含 2 待裁） | 聚类准入 built；双实现待并；对称正交化/IC_IR=图上法注未建 |
| b2_f25 | F25 E6 入库监控 | 挖干可施工 | 引擎全 built 但自动链生产零运转（6/6 报告=pytest 泄漏）；16 及格在账待消费 |
| b2_f26 | F26 E7 前哨 | 挖干（missing 定性） | 缺位属实：考核器/判定器/落点三缺；八项前置齐（§B-E7） |
| b2_f27 | F27 E8 组装 | 挖干可施工 | 装配体已投产 7 日+毒丸 3 枚已修待重放；差 IC_IR/爬坡两法注件（待裁） |
| b2_f28 | F28 E9 归因 | 挖干 | 引擎+sim 日账 built；IS 分解 FIELD-GAP/影子组合/回灌环三缺=前置清单 §B-E9 |
| b2_f29 | F29 台账出生证 | 挖干可施工 | 台账族 13+全活；断链两处：constructed_manifest 缺 5 行+车道 G 零货（归 SF-A） |

**待裁五案**（随册呈总筹，总筹裁不了留 Owner 晨报）：①E5 簇首准则与双实现归并；②对称正交化/IC_IR 法注降级或立项；③E4a/E4b 拆分（开放决策点 7 原样）；④constructed_manifest 补登 5 行豁免与否；⑤E7 滑点实测档两案（真单腿 vs 五档扫描）+产出落点。

## D. 复核命令（10 分钟核对全清单）

```bash
export PATH="/c/Users/$USER/AppData/Local/Programs/Python/Python312:$PATH"
tail -c 2500 .runtime/strategy_pipeline/pending_events.jsonl                        # BP-3 滞留+毒丸
python scripts/backtest/strategy_screen_query.py bothwin                            # 16 及格在账
grep -L "pytest_" docs/_working/pipeline-research/reports/intake-*.md               # BP-5 泄漏=0 生产报告
cat .runtime/strategy_pipeline/last_audit.json | tr ',' '\n' | grep -c "pf_alloc_daily:2026"  # E8 投产日数
ls scripts/backtest/translated/c4_fact_*.py | wc -l; wc -l data/strategy_intake/constructed_manifest.csv  # 6 vs 2(含表头)
grep -n "module_ref: null" config/strategy_production_map.yaml                      # E7 missing 图证
```
