---
ttl: task_bound
session: st-ec2-p0
completes_when: EC2 P0 断链车道收官归档
---

# ec2_p0_breaks_ledger — EC2 P0 断链处置台账（九项逐项）

> 任务：全流通骨架七断链（F26/F74/F34/F20/F62/F82/F04）+两条回灌边（FL1/FL2）现态复核+可修即修。
> 三态口径：已修（留证据）/本役修（qid+落地哈希）/登记跳过（原因）。复核日期=2026-09-27。
> 落地批：q-0001..q-0004（队列 qid 前缀 q-20260927-st-ec2-p0-000X，落地哈希见 91_progress.md 对应行）。

## 一、九项销账总表

| # | 项 | 三态 | 处置 | 证据锚 |
|---|-----|------|------|--------|
| 1 | F34 知识汇聚 | 本役落地（q-0001，遗产件吸收） | 死会话 st-chief4x-know-20260927 遗产 staged 三件（l9_readiness_aggregator 聚合器+DDL 部署器+16 测）经本会话核验测试全绿后正门落地；TDM L9-AGG module_ref null→实件锚同批 | 聚合器事件钩子挂 pipeline_events task_completed（daily_kline 系 SUCCESS+同日 60min 节流）；16 测绿；头注 token mod-data-l9agg；HEAD 已含翻译条 |
| 2 | F74 转正汇总器 | 本役修（q-0002；堵点3 Owner/堵点4 处女链自然时间除外） | ①combo gate 切 v2 frozen 尺 STD-SIM-ACCESS-002（裁定#337）：dsr_min 0→0.5+ρ̄≤0.7 腿+年化换手≤12× 腿+v1 suspect 注记（裁定#306）②combo 事件入口：run_promotion_advisory_due 执行体尾传动渲染一页报告（空目录静默跳过+失败不反噬） | test_promotion_combo_gate 11 绿（v2 钉值+DSR 边界）；test_promotion_advisory 17 绿 |
| 3 | F20 G 事件 | 本役修（q-0004；上游胃停摆另属 F96 域） | intel_harvester 落新班（hits>0）fire-and-forget 触发 lane_g_stomach_intake run——"新文件到达"=合法事件（宪法 §9.3 零 cron/Timer），Popen 即返回，触发失败不反噬搜索班 | test_intel_harvester 23 绿（零命中跳过/spawn 失败降级/命令断言）；inbox=1 件 seen=5 行与 09-25 持平 |
| 4 | F26 E7 前哨 | 他线已落地销账（88f62e893e，总筹通报在飞后当晚落地） | st-chief4x-promo2-20260927 落地 MOD-BT-225 paper_outpost.py（517 行：账实核对/判定书/run 落册）+277 测+strategy_production_map module_ref 回填；本会话在其在飞期间自建的重复件（MOD-BT-224）已按内收原则全撤净（py/test/config 删除+depgraph 节点移除+翻译/token 登记条精准摘除），防撞协议全程生效 | commit 88f62e893e=7 文件（含 F04 件）|
| 5 | F62 合规门 | 登记跳过（Owner 门位） | 6 处 OrderManager() 裸构造全在+broker_ack false×6/true×0+guard 零实例化——接线前置=Owner 人工报送程序化交易报告回填 broker_ack（B1 序列强约束） | 99_skipped_for_owner.md SKIP-1（修法处方+工程侧后续 1-2 天指向） |
| 6 | F82 order_daemon | 他线已接线落地（d0257693f1，09-27 深夜） | S0 判定"保持不存在"在本役复核时成立（EC3 row11 同判=零命中）；本役末段 st-chief4x-gut 系会话落地 order_daemon 接线（63 行改动+confirm_gate 1171 行随批）——按 journal 事件触发口径落地，判据演进为"接线存在且事件消费" | commit d0257693f1=6 文件；后续健康判据归 EC3 健康表行 11 维护 |
| 7 | F04 清洗接线 | 他线已落地销账（88f62e893e，总筹通报让位后当晚落地） | st-chief4x-promo2-20260927 落地 cross_source_validator 调度接线（schedule.yaml cross_validation 层+scheduler.py 接线+105 测）；本会话未动工仅保留只读复核结论（总筹通报让位），防撞协议生效 | 残项=cleaning 三引擎宿主托管（C1 处方在册）与 AI 判净站（Owner 花钱点）|
| 8 | FL1 E9→E2 | 本役修（q-0003） | 新增 MOD-BT-223 feedback_prior：E6 衰减台账 digest+E9 归因日账 digest→precheck_prior_note 先验注记；消费端接线=hypothesis_precheck（build_prompt 可选 prior_note 注入"只作背景不作判据"+判定行 notes 审计留痕），可选参数零破坏兼容 | test_feedback_prior 9 绿（fail-open/注入边界）+test_hypothesis_precheck 16 绿；CH 摘要走 ch_reader+FINAL（#ARCH-CH-007） |
| 9 | FL2 E6→E1 | 本役修（q-0003） | 同件 intake_direction：方向面读数（在考量/状态分布/存疑清单/归因净额）挂 factory_intake_pipeline 夜批报告 feedback_prior 段——只呈现不决策（编排层不评分铁律），失败 error 留痕不反噬进货 | test_factory_intake_pipeline 14 绿；写入端复测：strategy_decay_ledger.json 09-21 更新在案（MOD-SIG-150） |

## 二、超计划修复（复核中发现，批 1 随批）

**sim_observe_daily 接线回归**：09-24 st-ailayer-final 批的观察面日件契约在 tests 钉死
（SIM_DAILY_KINDS 四元组+run_sim_observe_daily+marker 语义），执行体接线在 09-26/27 快照
回退事故中丢失→5 测长期红（HEAD 即红，非本役引入）。批 1 按 HEAD 测试契约补落：
SIM_DAILY_KINDS 尾部追加+四平面串行执行体+消费成功才落 marker。连带修复：F34 唤醒钩子
在 wire 测试打真 CH socket（ResourceWarning 升级 ERROR+全文件 70s）——autouse 隔离补
L9 钩子（沿 _isolate_phase2a_judgment_hooks 既有范式），修复后 test_pipeline_events 38 绿/6.7s。

## 三、复核命令实录（关键三条）

```bash
# F34 现态（修复前）：module_ref=null → 落地后=实件锚
grep -n "module_ref" config/trading_decision_map.yaml | grep -n "L9AGG" || true
# F62 现态（跳过依据）
grep -c "broker_ack: false" docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml   # =6
# F82 判据（EC3 同款复测）
grep -rn "OrderDaemon(" src/ --include="*.py" | grep -v test | wc -l   # =0 → 判据成立
```

## 四、移交与遗留

1. **F26/F04**：均已由 st-chief4x-promo2-20260927 落地（88f62e893e，2026-09-27）——七断链
   现状：F34/F74/F20/F26/F04 本役或他线翻绿，F62=Owner 门位（SKIP-1），F82=设计态销账；
   回灌边 FL1/FL2 消费端已建（MOD-BT-223）。F04 残项=cleaning 三引擎宿主托管（C1 处方
   在 m1_data/02_cleaning.md，cross_source_validator 接线≠C1 全量）与 AI 判净站（Owner 花钱点）。
3. **F74 残项**：堵点3 通知通道=Owner 裁定（99_skipped SKIP-2）；堵点4 处女链 e2e 彩排
   随首个自然治理班次（sim 满 2 月≈11 月中）；⑤首例真实 ADV 包=转 built 判定日。
4. **F62**：Owner 报送后工程接线（99_skipped SKIP-1）。
5. **sim 观察面**：首班真实运行证据待下一 daily_kline 交易日（09-28）自然唤醒产生。
