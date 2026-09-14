---
ttl: task_bound
---

# 全自动化夜班总方案（Full Automation Night Mandate Plan）

> 2026-09-15 夜班 ｜ Owner 令：全模块自动化零人工、先方案后施工、循环检查两次零失败+红蓝对抗、收尾三件套。
> 方法=挖矿 SOP（外部实践调研→本项目对照→四闸自查）+ 施工 SOP 15 步（每模块 lookup/depgraph/claim/测试/gateway）。
> 自裁预案：可裁自裁（第一性原理+量化社区实践），不可裁登记跳过，堵塞才停。

## 0. 调研结论（挖矿 SOP，两轮外部实践+本项目对照）

| 实践 | 社区/机构做法 | 本项目裁定 |
|---|---|---|
| 券商终端登录 | 量化社区普遍做法=watchdog 保活+自动重拉（会话内免登录），密码自动填充仅 miniQMT 部分版本可行，滑块验证码是硬边界；密码明文落盘违反安全惯例 | **保活自动化做到头**（存活探针+自动重拉+告警），最后一公里（真过期登录）若无法免验码则登记——人工从"每日"降为"偶发" |
| 定时批任务 | cron 固定时间批任务 vs 事件触发 reconciler 是两类物 | 结算=固定时间批任务，走既有 DataScheduler tasks.yaml（ house style），**不违 §9.3**（红线只管 reconciler） |
| DDL 执行 | DDL-as-Code + admin 通道预建是本仓既有先例（apply_rbac.py） | Owner 全自动指令=窗口放行，admin 通道执行+system.columns 探针验证 |
| 基本面 PIT | announce_date 生效制（价值可用日=公告日）是 PIT 标准做法 | financial_indicator 按 announce_date ffill 构造日频截面 |
| 假 done/落地竞态 | 队列 landing 记录必须在 commit 创建事务内取返回值，不得事后读 HEAD | 修 commit_queue landed_id 记录时序 |

## 1. 施工编排（对 Owner 17 项清单的映射）

| 批 | 内容 | 产出 |
|---|---|---|
| N1 | 引擎基本面门扩展（MOD-BT-096 INVARIANTS 修订+gate/secondary-sort 参数+测试） | _valuation_engine v2 |
| N2 | B 档 12 只翻译（逐只读原文定 gate/sort 矩阵）+IS/OOS 双窗 | 12 翻译件+台账 24 行 |
| N3 | C5 聚类复检（63+ scored 行重聚类，出簇首/redundant 标记） | 聚类刷新报告 |
| N4 | 模拟盘批 3：月度偏离报告生成器（信号一致率/成交价偏差/漏单率/收益归因） | 生成器+run 档案 |
| N5 | 模拟盘批 4：decay_watch（0.5 存疑线扫描→lifecycle 流转建议） | 扫描器+建议文件 |
| N6 | Owner 窗口自动化：B2 DDL 执行+B5 结算挂 tasks.yaml+B1 QMT 保活/自动登录探针 | DDL 落库+调度接线+保活件 |
| N7 | 队列假 done 根因修复+堵点 TOP 治理+battle_map/ROOR 核实 | 修复+核销/登记 |
| N8 | EXP-02 现状核实；#10 C-1/#11 分钟表 评估→自裁或登记 | 核实记录+裁定 |
| N9 | 循环检查（连续两轮 0 失败）+红蓝对抗+修复 | 检查报告 |
| N10 | 收尾：gateway 全落地+临时文件清+零遗留总汇报 | 本文件销项+汇报 |

## 2. B 档 12 只 gate/sort 矩阵（施工时逐只读原文终定）

数据源：stock_indicator（pe/pb/ps/pcf/dividend_yield/total_mv/circ_mv）+ c3_fundamental.financial_indicator
（roe/roa/net_profit_yoy/revenue_yoy/ebit/debt_ratio/ocfps 等，announce_date PIT）。

## 3. 防噪音四闸自查（每新节点过三条件）+ Owner 窗口项自裁记录

- B2 DDL：Owner"全自动化零人工"指令=窗口放行，admin 通道+探针，登记于本文件。
- B5 调度：tasks.yaml 日批档位，事件依赖保持，非 reconciler 不触 §9.3。
- B1 QMT：保活/重拉=全自动；密码自动填充先探针（控件可寻址+无滑块才做），滑块=登记。
- C-1/分钟表：评估后按价值/可行性自裁（预期：登记跳过，理由随 N8 记录）。

## 4. 验收线

- 循环检查连续两轮全绿（回测烟测+触及域测试）；红蓝对抗一轮（对新增件做对抗性审查）；
- 全部落 gateway（队列落地必 git log 内容级核验）；临时文件零残留；台账/run 档案零游结论。
