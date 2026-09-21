---
ttl: task_bound
title: 深度审查报告——结算对账链（R04）
owner: st-deeprev-20260918
created: 2026-09-18
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline_commit: 2fa92002c3
---

# 深度审查报告：结算对账链（R04）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/post_settlement_pipeline.py:101` + `settlement_reconciliation.py:174` + `recon_runner.py:392`
- 生产调用方（实核）: run_post_settlement_pipeline ← scripts/run_post_settlement.py:481（**手动脚本**，脚本自打"手动触发未挂调度"）；SettlementReconciler ← 同脚本:274 + recon_runner:430；recon_runner.run_daily_reconciliation ← **零生产调用方**（57号文 SOP 人工触发，头部自认 recon_runner.py:5,26）；build_post_settlement_jobs ← **零调用方**（15:30 cron 规格从未注册进任何调度器）
- 测试文件: tests/trading/test_post_settlement_pipeline.py（9）/ test_settlement_reconciliation.py（501 行）/ test_recon_runner.py（10）——全绿（2026-09-18 实录，94+10 passed）
- 备注: "盘后 15:30 硬时点"现状=纸面承诺

## 1 对象快照

- **范围**：三件套全链——①post_settlement_pipeline（15:30 编排入口，对账→审计串联）；②settlement_reconciliation（SettlementReconciler 交易级逐笔对账+报告哈希）；③recon_runner（回测 vs 模拟盘三层 diff：L1 交易级/L2 持仓级/L3 PnL 级→归因 ABC→落库）。辅助实核 broker_settlement_adapter（配对键真源）与 daily_auditor 接缝。
- **排除项**：DailyAuditor 五件套内核（MOD-RK-20，独立大件，本簿只审其在 pipeline 中的调用契约）；miniqmt_broker（见 R01/R02 簿 B 轴）。
- **测试覆盖概况**：三套全绿；覆盖洞见缺陷 1/3。
- **材料包缺项声明**：同 R01（无运行时证据包）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | pipeline 对 reconcile_fn 返回值只 getattr("matched")，无类型校验：返回 dict/None/缺属性对象 → matched=None → 走 else 分支标 **OK** 不告警 | post_settlement_pipeline.py:141-148 | **P1**（假阳性过关） | 注入 `lambda d: {"matched": False}` → 状态 OK |
| A | recon_runner L3 现金流公式**忽略买卖方向**：`trade_cash=sum(filled_quantity×fill_price)` 把卖出也当现金流出；Fill 契约无 side 字段（适配器头注自认） | recon_runner.py:297-303 + backtest_fills_adapter.py:32 + shared/contracts/fill.py:52-59 | **P1**（数学错误） | 买 10 万@10 再卖 11 万@11：sim_pnl=0−210000=−21 万 vs 真实 ≈+1 万 |
| A | settlement_reconciliation 配对索引**静默覆盖**：`system_by_id[key]=fill` 无重复检测——partial fills 回退 order_id 配对时键碰撞丢笔（对比 three_way 同场景 Fail-Closed） | settlement_reconciliation.py:226-229,232-243 | P2 | 两笔同 order_id 的 fill 跑 reconcile，total_system_trades=1 |
| A | L1 `_compare_fields` 只比 price/qty/commission，**不比方向**；业务键=标的+时间序（组内 seq），两侧笔序错位+方向不同可判 MATCH | settlement_reconciliation.py:370-419 + broker_settlement_adapter.py:67-79,101-106 | P2 | 回测买/实盘卖同价同量 → L1 matched |
| A | 结算日期不符的券商记录仅 warning 不剔除，照常进当日对账口径 | settlement_reconciliation.py:234-243 | P2 | 喂昨日记录观察混入 totals |
| A | recon_runner 归因映射完备（5 类 drift 全覆盖，else 兜底 C 类） | recon_runner.py:218-282 | （正面） | 跑测试 |
| A | L3 隐含假设链已文档化（期初空仓/fresh 开仓/滚动持仓降参考层）——**但"无卖出日"假设未文档化**（与缺陷方向项同根） | recon_runner.py:52-58 头注 | P3 | 读头注 |
| B | pipeline audit_fn 返回值完全不检查（audit_status 只看抛不抛异常）——审计报告内部"部分失败"不影响状态 | post_settlement_pipeline.py:156-159 | P2 | mock audit_fn 返回含 failed 项的报告 → 状态 OK |
| B | fill.commission 契约="券商回报原值"（fill.py:56 区段），回测侧 commission 语义=FeeConfig 全费用还是纯佣金未文档化 → L1 COMMISSION_MISMATCH 参考列语义模糊（好在 C9 明确"仅参考不归类"兜底） | backtest_fills_adapter.py:94 + recon_runner.py:333 | P3 | — |
| C | recon_runner append-only INSERT **无幂等键**：同 trade_date 重跑行数翻倍；pipeline 头注宣称"同 trade_date 重跑由下游幂等保证"（post_settlement_pipeline.py:8）**不成立** | recon_runner.py:115-121,381-389 | P2 | 同参数跑两次断言 rows 翻倍且无去重 |
| C | reconciliation_differences 消费方（谁读这张表做闭环）grep 无读取方——只写不读=差异登记后无人消费 | recon_runner.py:59-61 头注 + grep `reconciliation_differences` | P2 | grep 实录 |
| C | C 类"当日即告警"实为**返回值里带出**（c_class_items），recon_runner 无 alert_sink——人工 SOP 消费，自动化告警链不存在 | recon_runner.py:444,456-467 | P2 | grep 结果消费方 |
| D | build_post_settlement_jobs 两个 job 同 cron 同 entrypoint（reconcile job 与 audit job 都指向 run_post_settlement_pipeline）——若真挂调度=同一时刻双跑全流水线；且当前零调用方，15:30 硬时点未注册 | post_settlement_pipeline.py:83-98 | P2 | grep `build_post_settlement_jobs(` 零命中 |
| D | 裸 sqlite3.connect 写 governance.db（SQL 常量+参数化，合规 NO-BARE-SQL 门禁口径）但绕过 DatabaseService——与宪法 §9.1"唯一真源"存在张力（governance.db 是否 sqlite 专属未见裁定） | recon_runner.py:115-121,383-389 | P3 | 查 NO-BARE-SQL gate 白名单 |
| E | **QMT 降级=SKIPPED=exit 0**：reconcile_fn=None（QMT 不在线/xtquant 缺失）→ 状态 SKIPPED → exit_code 0，无"连续 N 日 SKIPPED"看门狗——券商通道死了每天绿灯（checklist #6 直接命中：数据源静默死亡） | scripts/run_post_settlement.py:38,53,407-413 | **P1**（断了没人知道） | 断网跑脚本 exit 0；连续 7 日 SKIPPED 无任何告警产生 |
| E | 结算单迟到/乱序：跨日记录混入当日口径（A 轴已记）；broker 侧"空结算单日"无 sanity 信号区分"真无成交"与"断供" | settlement_reconciliation.py:234-243,274-285 | P2 | 空 records+有 fills → MISSING_IN_BROKER 响（此向正确）；空+空 → 全绿（无人知道今天该有对账） |
| E | reconcile/report 生成幂等性：reconcile 纯读可重放（正面）；report_id=uuid4 非确定但 report_hash 排除 id，同内容同 hash 可去重 | settlement_reconciliation.py:287-296,335-346 | （正面） | 同输入两次 hash 相同 |
| F | 逐笔配对+容差+例外台账=对账引擎业界标准形（Trintech multi-way matching；Juspay 2025）；混合制（实时+批量兜底）见 R01/R03 簇报告 | settlement_reconciliation.py 全文 | （对等已有） | — |

## 3 SOTA 对照

- 逐笔交易对账+归因：对等已有——Trintech Adra Matcher《Automating 3-Way Transaction Matching》（trintech.com，2024-2025）multi-way matching+例外管理；Juspay（juspay.io/blog，2025）逐笔证明式对账。本链 L1/L2/L3 分层与归因 ABC 分类不落后。
- 差异登记闭环：缺陷「只写不读」对应的业界形态=exception management 工作台（同 Trintech/Juspay 文）。**立卡候选**：给 reconciliation_differences 配最小读取方（晨报/看板），否则落库无意义。
- 断供看门狗：R03 簿同款立卡——"对账该跑没跑"本身必须是告警事件（Oceanobe，oceanobe.com，2025 前后）。

## 4 缺陷清单

1. **P1 QMT 断供降级绿灯（SKIPPED=exit 0 且无看门狗）**
   现状→QMT 不在线/xtquant 不可用 ⇒ reconcile_fn=None ⇒ SKIPPED ⇒ exit 0；文档口径明示"0=OK/SKIPPED（含 QMT 降级）"；无任何机制发现"连续 N 日没跑成对账"。
   证据→scripts/run_post_settlement.py:38（降级设计）、53（exit 矩阵注释）、407-413（_exit_code_of）；全仓 grep 无 SKIPPED 连续计数/watchdog。
   影响与爆炸半径→券商通道静默死亡 ⇒ 结算对账无限期停摆而运维面全绿。这是"对账断了没人知道"的最坏形态——差异抓不到 + 没人知道抓不到。全账户级。
   建议修法→①SKIPPED 状态至少告警（alert_sink 事件"对账未执行"）；②加状态落盘（JsonStateStore 记 last_successful_recon_date），晨判/看门狗消费 staleness；③exit code 区分 SKIPPED（如 exit 2）供调度层重试。
   验证法→模拟 broker.connect 抛错跑脚本：断言 exit≠0 或告警通道收到事件；连续两日跑后 staleness 记录可查。
2. **P1 pipeline 返回类型不校验 → 假阳性 OK**
   现状→`matched=getattr(result,"matched",None)`，`if matched is False` 才 DRIFT；返回 dict/None/异构对象时静默 OK。
   证据→post_settlement_pipeline.py:141-148。
   影响与爆炸半径→reconcile_fn 实现重构（如改返回 dict）后整条对账链无声失效——类型漂移=绿灯漂移。测试无此类负例（覆盖洞实证：9 用例无缺属性场景）。
   建议修法→matched is not True ⇒ ERROR+告警（fail-closed）；或 isinstance 校验 ReconciliationResult。
   验证法→注入返回 dict 的 reconcile_fn，断言状态 ERROR。
3. **P1 L3 PnL 代理公式忽略方向（含卖出日必错）**
   现状→`trade_cash=sum(filled_quantity×fill_price)`（299）把买卖全部当现金流出；Fill 契约无 side（适配器头注自认 backtest_fills_adapter.py:32）⇒ 任何含卖出的交易日 sim_pnl 低估 2×卖出额。
   证据→recon_runner.py:297-303；contracts/fill.py:52-59（无 side 字段）。
   影响与爆炸半径→L3 是参考层（C8 人工复核链），但结果=含卖出日恒 MISMATCH：要么人工复核疲劳致真差异被淹没，要么 L3 被默认无视——归因第三层形同虚设。回测-vs-模拟盘日频对账有效性。
   建议修法→①短期：broker_fills 为空或含卖出时 L3 显式 SKIPPED+头注声明"仅买单日有效"；②治本：给对账数据链补 side（query_trades_today 已有方向信息，miniqmt_broker.py:599 注释确认丢弃了它——Fill 加 side 或改传 signed quantity）。
   验证法→构造买 10 万+卖 11 万当日：断言当前实现 MISMATCH（复现噪音）；修后断言 gap≈费用。
4. **P2 配对索引静默覆盖丢笔**
   现状→system/broker 两侧索引 `dict[key]=record` 无重复检测；broker_fill_id 缺失回退 order_id 时，同 order 多笔 partial fill 互相覆盖。
   证据→settlement_reconciliation.py:226-229,232-243；对照 three_way_reconciliation.py:210-212 同场景 Fail-Closed 抛错。
   影响与爆炸半径→total_system_trades 偏小、被覆盖笔逃逸逐笔核对——恰在"部分成交"这一最需要逐笔对账的场景失明。
   建议修法→对齐 three_way 口径：重复键抛 InvalidSettlementInputError；或键升级为 (key, fill_id) 二级。
   验证法→两笔同 order_id fill 断言抛错。
5. **P2 差异落库只写不读+不幂等**
   现状→append-only INSERT 无 (trade_date,trade_id,drift_type) 幂等键，重跑翻倍；全仓无读取方消费该表。
   证据→recon_runner.py:116-121,381-389 + 头注 59-61；grep 无 SELECT 方。
   影响与爆炸半径→"重跑由下游幂等保证"承诺失真；登记表无人消费=闭环断裂（56号文 C10 首查项落空）。
   建议修法→幂等键 UNIQUE 约束或 INSERT 前查重；配最小读取方（晨报）。
   验证法→同参重跑断言行数不翻倍；晨报含当日行数。
6. **P2 15:30 硬时点未注册+双 job 同入口**
   现状→build_post_settlement_jobs 零调用方（纸面规格）；且两 job 同 entrypoint——真挂上会 15:30 双跑并发。
   证据→post_settlement_pipeline.py:83-98 + grep 零命中。
   建议修法→挂调度时合并为单 job（流水线本身已串联对账+审计）。
   验证法→调度注册表出现单条 post_settlement 任务。
7. **P3 杂项**：跨日结算记录仅 warning 混入（settlement_reconciliation.py:234-243）；audit_fn 返回值不检查（post_settlement_pipeline.py:156-159）；裸 sqlite3 与 DatabaseService 张力（recon_runner.py:383，门禁口径内，建议裁定登记）。

## 5 挂起疑问

- recon_runner L1 的语义是"回测 vs 实盘"而非"系统 vs 券商结算单"——真正的券商结算单通道（fetch_broker_settlement_records）只有 run_post_settlement.py 手动脚本在用。三层对账（54号 §3.3）中"结算单腿"是否只有手动保障？请收口方核对调度规划。
- governance.db 裸 sqlite3 是否有既存豁免裁定（未检索裁定册全文，grep #ARCH 未命中相关号）。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；正面项 3 条（归因映射完备、reconcile 纯读幂等、report_hash 防篡改设计）。
- 长尾清单：①DailyAuditor.audit 内核不在本簿（调用契约已审，报告内部失败语义挂 P2 待其专属簿）；②miniqmt_broker.query_trades_today 的交易日过滤边界（时区=QMT 本地 Windows）未实测；③运行时证据包未取——SKIPPED 是否已实际连续发生无法从代码判定。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
