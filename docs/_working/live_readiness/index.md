---
ttl: task_bound
completes_when: 四件套经 Owner 点单处置后转 archived
session: st-live-readiness-20260922
date: '2026-09-22'
---

# live_readiness/ — 小资金实盘准入准备班交付索引（st-live-readiness-20260922）

> 通宵令目标=实盘准入四件套成稿。全程零实盘触碰：产出=文档+只读探针+检查器设计（探针窗口 2026-09-22 01:50–03:00）。

## 四件套

| 件 | 文件 | 一句话 |
|----|------|--------|
| 1 | [live_admission_checklist.md](live_admission_checklist.md) | 六面检查表（风控/仓位/监控/告警/密钥/合规），逐项判据+现状实测：**绿17/黄8/红7/白1** |
| 2 | [small_capital_live_sop_draft.md](small_capital_live_sop_draft.md) | 小资金 SOP 草案：pilot 档/300ETF 波段首选/风险预算仓位/五级熔断自动纪律/Owner 八个干预点；参数全 proposed 待 confirmed |
| 3 | [exception_handling_manual.md](exception_handling_manual.md) | 异常处置手册 E1–E8：断链/断供/模型异常/熔断后/误连实盘/告警故障/终端阻塞/撤单契约缺口；全部对照实测行为 |
| 4 | [admission_gate_design.md](admission_gate_design.md) | 准入门禁 G1–G12+只读检查器设计+**依赖项清单分列**（等 Owner 7/等指令A 1/等指令B 3/等考试链 1/等施工 3） |

## 七红速览（补齐前不得挂实盘旗）

熔断态无持久化（R3）｜仓位参数未 confirmed（P1）｜金字塔规则未接电（P2）｜交易心跳缺位（M4）｜交易级告警缺专条（A1）｜**密钥轮换未办（K1）**｜blocks_live_trading 零消费方（C2）。

## 依赖速览

- **等 Owner**：密钥轮换（第一依赖）/60% 硬顶 confirmed/资金规模与单笔止损/模拟盘 N 天=20 交易日建议/crisis θ 校准/换档签发/外部合规确认
- **等指令 A**（st-integrated-bt-20260922，在飞）：首跑报告+红蓝两轮 0（协议 v1 已冻结 01:05）
- **等指令 B**（st-sim-launch-20260922，实测进度 0）：模拟盘部署/30 笔纸面成交/熔断实弹演练
- **等考试链**：≥1 毕业包（GRADUATED_PACKAGES 首条）
- **本班禁施工项**（建议另立卡）：blocks_live_trading 接线/交易级告警 4 条/熔断态持久化
