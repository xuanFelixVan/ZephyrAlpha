---
ttl: task_bound
completes_when: Owner 阅毕+晨间追认后随战役归档
---

# 模拟盘三步启动战役·终局班交付报告（st-sim-launch-20260923）

> 通宵/全日执行令 2026-09-23 点火｜前提=Owner 已登录终端（XtItClient 昨 20:50 起）+桥 connect=True（Max 已验）｜全程 env=sim，实盘四禁零触犯
> 前情=st-sim-launch-20260922 两批已落 HEAD（fb5a7821d7 白日修复全批+28b85901bf 委托裁定施工批）

## §0 一句话总结

模拟盘完成历史首次**计划→真桥→成交→结算全自动闭环**（10:42 防御姿态卖出 510300 1100 股成交@4.604，台账 bridge_fill_check=1.0），且**当日全天无人值守自动化全通**：09:35/13:05 计划任务双触发零误单→15:30 结算链日刊 fresh=1 degraded=0 首次全绿→晚间事件链（daily_kline SUCCESS）observe-chain 首跑自动落 43+E4 重放与 plan 全链→日刊终态 45 钱包 58.06M（三条观察档越界预警=哨兵正常）。09-22 断链结构性闭合；R-H5E-1 治本+裁定#339 两缺口 sim 实测收官；红蓝三轮 5121/5122/5128 绿。

## §1 考古增量与 09-22 断链处置

- **断链根因**：E4 重放/plan 桥/plan 执行/日报四步无任何调度挂接（前日只挂日刊一步）→ 09-22 台账零行+钱包塌回 4 空壳；幽灵钱包（STR-AUTO/MULTIFACTOR）在 FIX-2 卫兵上线前又开户 3 次。
- **回退残影**：sim_daily_runner+其测试被 02:29 活写手回退到裁定前版本（HEAD 15:48 已有 plan-execute；mtime 02:29>HEAD 落地 15:48 为铁证）——classify_workspace_wip 判 stale_rollback 族；本班 lock_files 持锁+审计后 `git restore --source=HEAD` 恢复裁定版。
- **09-22 回补实弹**：e4-replay 44/48 成功（4 例数据面缺口如实留错：68cc 基本面列/93aa 成分窗/8664+e2e7 NaN 尾行卫兵隔离）+plan-bridge（震荡→unexecutable 如实）+plan-execute+report；settle 全结算零 unresolvable；日刊 09-22 补定稿（47 钱包 44,490,280.84 fresh=1）。
- **FIX-2 卫兵自然实验 PASS（08:43）**：今晨自动开户仅注册策略 STR-E-TIMING-001，两幽灵被拒（run_id sim-open-20260923004323）——R5 孤儿钱包病灶闭合并经实弹验证。

## §2 批1 复活挂接（事件触发，宪法 §9.3 合规）

| 件 | 内容 |
|---|---|
| observe-chain 子命令 | sim_daily_runner 复合链：plan-bridge→plan-execute→e4-replay(全量)→report→settle(T+1 sweep)，单步失败不连坐全败才抛（A5 同款）；实弹重跑 09-22 幂等五步零失败 |
| 事件链挂接 | pipeline_events 新 kind=sim_observe_daily 挂 daily_kline SUCCESS 唤醒 FIFO 末位（账本→日刊→归因→观察面）；业务日=resolve_pf_alloc_trade_date 数据驱动禁墙钟；LIGHT_KINDS 轻消费；**时序要害=必须等 kline 落地（15:30 前跑会拿 T-1 旧价=09-22 断链的结构性闭合）** |
| 桥执行腿排班 | ZephyrAlpha_SimBridgeExecute 计划任务（09:35+13:05 双触发，LastTaskResult=0 实证）+wrapper：交易日历守卫+XtItClient 活性守卫（死桥不落单=隔夜缺口应用侧缓解）+cmd /c 原生重定向（FIX-3 v2 同款）；09:35 首火实弹过 |
| 09-22 断链预防 | tasks.yaml 为数据摄取清单（table/source/capability schema），sim 链硬塞=滥用；挂接真源=事件链+计划任务（PaperSession 先例） |

## §3 批2 接电：bridge-execute 桥真单腿（本班核心新件）

- **语义**：日计划姿态→env=sim QMT 桥真单。决策矩阵与 plan-execute 同源（_plan_decision/不追高 1.5%/30% 额度，Owner 09-22 委托裁定参数）；**仓位真源=柜台 510300 实际持仓**（read_only broker 直读，与 SIM-PLAN-001 虚拟平面分离防双算）；**限价=下单时点桥盘口**（买=ask1/卖=bid1，quote mtime>900s 或 bid/ask=0=fail-visible 不下单，禁成本价旧价）；窗口闸 09:30-11:25/13:00-14:55；**幂等**=signal_batch=plan-bridge-<day>（trade_date 显式传 day）+orders_sim.csv idem 键预扫（跨进程重跑不二次下单）。
- **首笔实单全链（10:42）**：09:55 五态归类=防御→posture_check 结算 1.0→exit 卖 1100 股限价 4.603（bid1）→**柜台合同 4820 成交 1100@4.604（10:42:43）**→510300 持仓归零现金回笼→台账 sysid=4820/FILLED→结算 bridge_fill_check=1.0（委托 1100/成交 1100）。
- **失败可见三连实证（断供注入哨兵真响）**：05:31 盘外 quote 超龄→拒单；09:35 集合竞价零盘口→拒单；窗口外/未归类→honest why 行。恒落台账行（source=plan_execute_bridge）。

## §4 R-H5E-1 治本+裁定#339 缺口补测

**R-H5E-1（探针警告治本，裁定#338⑤）**：
- broker 加 `read_only` 参数（只读面显式声明：不触发未注入告警+submit 拒单兜底）；position_monitor/app_panel 两个只读构造点改 read_only（Assembly 走 configure_read_only 方法注入——__init__ 7 参顶满 NO-LONG-PARAM-LIST，configure_execution_report 先例）。
- smoke 工具显式注入 RiskValidationBridge(DefaultRiskValidator)+_CountingRiskBridge 计数器，新增 **TR 步=「pre-trade 校验触发证据 validate_order calls≥1」——裁定#338⑤ 接线验收口径达成**（09:45 实测 calls=1 PASS）。
- 顺手修 sysid 回填缺陷：OrderManager submit 预填 broker_order_id=本地 id 曾阻断柜台 sysid 回填（桥同步条件改 `in (None,'',order_id)`）——修复后合同 1573/1800/4820 均正常回填（T3 假 PASS 同步收紧=sysid≠本地 id 才算柜台 ack）。

**裁定#339 缺口补测（E8 授权，证据已回填 exception_handling_manual.md E8 条目 v2）**：
- **缺口②隔夜单=静默丢弃活体复现（未闭环呈 Owner）**：04:45 预市场落 600000@4.50→08:53 客户端重登后拾取→本地 #DONE+ack(SENT)→09:15 竞价+09:30 开盘后柜台零收录（09:17/09:31 双取证）——与 09-18 c3 一致。治理建议=客户端应拒单并 #FAIL 而非 #DONE 静默吞。
- **缺口①撤单契约=闭环（带两处修）**：柜台按原单 remark 配对撤单。09:40 v1 实测暴露 sysid 回填修复引入撤单回归（OrderManager 传 sysid→桥缓存 MISS→remark 退化）→**OrderManager.cancel_order 改传本地 order_id**；09:45 v2 全链 PASS（1800 已撤+Message 09:45:57 回报）。
- **新发现·客户端竞态重提交缺陷（呈 Owner）**：submit→cancel <5s 竞态触发未 #DONE 订单行反复重提交（同 remark 36 合同 1805..1954）+撤单重发；containment=客户端自身 #DONE 终态标注原子改写指令行（09:52 生效合同数冻结）；36 单全为深限价不可成交、当日有效 15:00 自动失效、冻结 16,203.40（0.16%）无害；计划腿无快速撤单节奏不暴露。
- 演练清单建议 v2：撤单用例 submit 后 ≥30s 再撤；禁预市场落单；监控=同 remark 合同数>1 告警。

## §5 结算语义修正+批3

- **settle plan_execute none/wait 假 0 分修正**：旧口径把无动作日映射"预期 cash"，持仓顺延日必炸（09-22 实证 65,055 股顺延+震荡→0 分）→新口径 `no_action_position_unchanged`=1.0（无动作=仓位不变即自洽）；09-22 已按 A6 复位法（重跑判定步再 settle）正名。
- **批3 日报**：[daily_report_20260922.md](daily_report_20260922.md) 已出（回补定稿日口径）；09-23 日报由收盘后 observe-chain 台账行渲染（链已自动化）。币圈 7×24 快线：数据腿复验在轨（max trade_date=09-22 UTC@09-23 00:43 ingest），昨日结论（数据通/回测通-负面证据/纸面不通）维持，等待 Owner 对币圈因子方向表态。

## §6 回执六要素

1. **改动文件**（14+2）：scripts/backtest/sim_daily_runner.py（observe-chain/bridge-execute/结算修正/quote 最新行）｜src/zephyr/strategy_pipeline/pipeline_events.py（sim_observe_daily 挂链）｜src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py（read_only+sysid 回填修）｜…/qmt_file_bridge_integration.py（configure_read_only）｜src/zephyr/ex_core/order_manager.py（cancel 传本地 id 修）｜src/zephyr/frontend/dashboard/app_panel.py+components/position_monitor.py（只读构造点）｜scripts/construction/qmt_bridge_regression_smoke.py（R-H5E-1 注入+TR 步+T3 判据收紧；**09-18 st-commitchain 未提交遗留收编**）｜新增 scripts/run_sim_bridge_execute_daily.ps1+register_sim_bridge_execute_task.ps1｜tests/backtest/test_sim_daily_runner.py+tests/strategy_pipeline/test_pipeline_events.py｜docs：campaign_ledger/delivery_report/daily_report_20260922/exception_handling_manual E8 v2｜注册表：capability_canonical_file_registry（+4 token）+module_translation_registry（+3 条）——**同批声明：两册 staged 含他会话在途条目随批吸收=被吸收型勿重放（q-0007 先例）**。
2. **红证双向**：断供注入=quote 超龄/零盘口/盘外三连拒单真响+XtItClient 守卫；订单链注入=隔夜单（缺口②复现）+窗口撤单（缺口①修复后 PASS）；负面注入=sysid 回填回归在 v1 实测暴露并于 v2 修复重验；结算假 0 分在 09-22 实证后修正。
3. **验收命令与实测数字**：`sim_daily_runner bridge-execute --day 2026-09-23`（sysid=4820 FILLED 1100@4.604）｜`settle --day 2026-09-24`（bridge_fill_check=1.0）｜`qmt_bridge_regression_smoke --cancel`（TR calls=1+T5 CANCELLED）｜三轮电池 5121/5122/5128 绿（唯一同款红=tests/risk/core/test_alert_generator 去重窗负载 flake，隔离重跑恒过、文件零改动非本班引入）｜runner+pipeline 套件 28+38 绿。
4. **门位/停手**：无 Owner 门位触发（未动注册表净删/未翻转 flag/未接实盘——env=sim 全程，real 实例显式不注入校验器维持现状=裁定#338⑤）；幽灵钱包存量处置+客户端竞态缺陷呈 Owner 两项。
5. **证据等级**：本报告全部数字 [亲验]（柜台 CSV/CH 实查/命令实跑）；09-18 缺口史实=[转报]（E7 工作簿+手册在案锚点）。
6. **未完成部分**：无停摆项。移交项：①客户端 submit→cancel 竞态重提交缺陷（呈 Owner，桥客户端侧治理）②缺口②隔夜单静默丢弃未闭环（治理建议已附）③T6b 撤单终态不产 execution_report 行（producer 语义待勘，非本班引入）④币圈快线待 Owner 方向表态。

## §7 收盘后增补（17:31 定案）

- **晚间事件链首跑成功**：kline 09-23 落地→sim_observe_daily 自动执行 observe-chain（e4_replay 43 行+plan 全链落台账）——观察面日链从本日起零人工。
- **FIFO 序修正**：首跑实证日刊先于重放跑=钱包计数少 43 观察钱包→SIM_DAILY_KINDS 改 账本→观察面→日刊→归因（日刊见终态）；今日日刊已幂等刷新（45 钱包 58,063,421.64 fresh=1，3 条越界持仓预警=CAND-5301/6a6e/9987 观察档市值超 110 万预警线，哨兵正常工作）。
- **13:05 二次触发实证零误单**：posture=flat+空仓→action=none 诚实行（幂等+矩阵双保险生效）。
- **移交观察项**：09-22 竞态重复单 36 合同冻结 16,203.40 待晚间清算自动释放（A 股当日有效已过期）。
