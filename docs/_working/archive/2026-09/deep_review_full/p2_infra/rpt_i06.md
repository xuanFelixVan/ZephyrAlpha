---
ttl: task_bound
title: 深度审查报告——I06 QMT 桥采集 Provider
object: I06 QMT桥采集Provider
target: src/zephyr/data/implementations/qmt_bridge_provider.py:156（QmtBridgeIngestProvider + _call_derive_auction/_call_synth）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；tasks.yaml 属他会话在途改动，按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I06 QMT 桥采集 Provider（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：桥 Provider 全文（探活三通道/capability 路由/tick no-op 防双写/分钟K合成/竞价族派生）。实时 tick 真身=BridgeTickSource（归 I07）。
- 断桥前科核实：#BRIDGE-WRONG-FILE（2026-09-08，v18 遗留 ticks.csv 静默尾读灌 166 万行错日数据）记录于 tick_subscriber.py:1471-1475；本模块 ENV_CONFIG 已与 v19 ticks3.csv 同源对齐（qmt_bridge_provider.py:59-64）。
- 测试：头注自述仅手动冒烟，tests/ 无专文件——**缺口**。
- 变更热力：3 commits（新件，2026-09-17 最后）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P2 分钟K合成路径 rows_fetched 缺失→游标冻结**：_call_synth 分支的 FetchResult 未传 rows_fetched，rows=[] → __post_init__ 补 0 → 调度器 `rows_fetched>0 才推进 last_key` 永不满足：last_key 冻在首跑日，合成窗口 [last_key,today] 逐日变长（重算成本线性增长），且交易日 0 行告警每槽必响。竞价族路径已修（红队 P1：L326-334 显式传 rows_fetched=n），K 线族漏修——同型补丁只打了一半 | qmt_bridge_provider.py:379-384（对照 326-334）+ scheduler.py:2032 | P2 | grep tasks.yaml source=qmt_bridge 的 kline_*min 任务；跑一次看 last_key 是否推进 |
| A | 竞价派生 rows_fetched=n 语义仍是"末日表内行数"非本批拉取行数——指标/看门铃口径失真（假完成态风险，checklist #12 邻接） | qmt_bridge_provider.py:322-334 + backfill 验证逻辑 | P3 | 对比 task_runs.rows 与表增量 |
| B | E:\qmt_bridge[_sim] 硬编码 Windows 绝对路径+TICK_BRIDGE_ENV 默认 sim——环境假设文档化充分（93 备忘），但 real 误配（env 变量打错）无 fail-fast，靠路径不存在才炸 | qmt_bridge_provider.py:61-73,247-252 | P3 | TICK_BRIDGE_ENV=real 于 sim 机器跑 connect 看报错可读性 |
| E | tick_data no-op 防双写设计正确（实时真身在 tick_subscriber，scheduler 侧零行成功防误配双写）——双写风险闭环 | qmt_bridge_provider.py:355-367 | 已查无 | 跑 tick_data 任务查表行数不增 |
| E | 历史日防覆盖闸 fail-closed（get_client None 即抛，防静默跳闸后原产日被派生近似覆盖——Replacing 后写胜出）：红队二轮加固已到位 | qmt_bridge_provider.py:111-153 | 已查无 | 断 CH 跑派生看抛错 |
| A | _probe_http 读到响应头即停，body 在后继分包时 alive 误判 False（假阴性探活） | qmt_bridge_provider.py:286-303 | P3 | 分包 mock 单测 |
| C | 派生/合成直写 CH 绕过 BufferedWriter+quality_gate（走 ch_writer 内部通道）——与 I08 质量门禁旁路同族（该发现主锚在 I08，此处登记旁路入口之一） | qmt_bridge_provider.py:81-89,111-153 | P3 | 见 rpt_i08 |
| D | capability 注册集（tick/kline 5 档/auction 2 档）与路由实现一致；quote 族显式 NotImplemented 错误契约正确 | qmt_bridge_provider.py:172-197,396-414 | 已查无 | 对表 |

## 3 SOTA 对照
- "CH 内自拼（tick→1min→高周期二次合成）"与量化界通行的 bar 工厂（tick→bar 聚合）做法对等；幂等用 Replacing+防覆盖闸属合理工程化。**对等已有**。来源：市场数据工程通识（未单独检索 URL=受阻如实记）。

## 4 缺陷清单
1. P2 kline 合成游标冻结+窗口膨胀+0 行告警噪声（若 tasks.yaml 已有该源任务则为 P1 级运行事故；当前 grep 显示 qmt_bridge 源任务在 tasks.yaml 中处于切换窗口，实际影响待收口方确认）。修法=合成分支补 rows_fetched=n（与竞价族同款一行）。
2. P3 组：rows_fetched 语义失真、real/sim 误配可读性、_probe_http 假阴性、质量门禁旁路登记。
3. 测试缺口：建议把竞价防覆盖闸+游标推进补成 pytest（本模块是红队密集修复区，无回归网）。

## 5 挂起疑问
- tasks.yaml（他会话在途）qmt_bridge 任务当前真实挂载数待收口方定格后复核 P2 影响面。

## 6 完备性自评
六轴全查。长尾：ch_tick_kline/ch_auction_derive 被委托模块未深审（懒导入边界只验证了异常转发）；sim 环境实跑冒烟未执行（无沙箱权限=受阻如实记）。
