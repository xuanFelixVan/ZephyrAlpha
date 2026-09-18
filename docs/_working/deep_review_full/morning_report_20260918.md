---
ttl: task_bound
title: 全项目六轴深度审查战役晨报（v0.2 进行中快照）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 晨报：全项目六轴深度审查+施工战役（2026-09-18 通宵班）——进行中快照

> 状态会随波次推进更新，本文件是晨报底稿；终版以台账 `01_master_ledger.csv` 为准。

## 一、Owner 必读（P0 置顶）

1. **K08 先报告后交易闸从未武装**：`compliance_report_registry.py` 闸码完整、测试全绿，但 `report_gate=` 全仓零注入、broker_ack 0/6——监管红线 C-002 在任何生产装配中都未生效。武装前置=券商 ack 数据流（否则 0 ack 下武装=C-002 全拒单砖化交易）。需 Owner 裁定武装时点与 ack 数据源。
2. **K02 资金事故假处置**：`kill_switch_orchestrator.route_incident("funds")` 翻动的 trading 五级旗无任何下单路径消费（资金事故=假处置）；系统级 kill switch 纯内存，重启即丢。需接线裁定+持久化。
3. **X08 券商文件桥双键错配（已治本）**：原状=指令写 idempotency_key、本地/撤单/Fill 配对全用 order_id，OM 造单两键独立 → 实盘上线即状态推进/成交配对/撤单三链全断。已修复+三回归测试。**实盘首日请用真柜台 CSV 复核 EXEC v16.4 解析口径**。
4. **sim_paper_ledger 一红外移**：`test_replay_pipeline_consistent` events==2 断言与车道 D2 crisis 日拦截特性（e1a975b158，他会话落地）冲突——危机日不写事件属特性本意，测试断言需该车道作者更新。

## 一·五、补充裁定项（W/D 波新增，Owner 关注）

5. **W07 NaN 回撤判 NORMAL 满配（已治本）**：pf_alloc 回撤限额分配器对 NaN 回撤三重比较全 False→满配放行，回撤爆表策略被静默洗白——已治本（NaN 拒收 fail-closed）。同域横切：**pf_alloc 7 件仅 W03 真接线**，W01/W02 信号合成上半段整链缺位、W04/W07 名为 production 实为空转、W05 模式开关无效（risk_parity 与 inverse_var 逐位相同）——整域接线/退役裁决建议入挖矿。
6. **Regime 域"断供即满部署"三腿**（D01 HMM 异常→均匀分布 / D05 / D12 参数缺失→1.0）：数据事故日恰好叠加危机时全账户敞口放大——fallback 语义需统一裁定（hold-prev/防御上限/告警显化），未盲改。
7. **Wyckoff 证伪旁路**（D09/D11）：WYF-3 证伪置零只封引擎主出口，MVP 回退支在弱 guard 下静默接管可达 S2 门槛——旁路拆除需裁定。
8. **W05/W06 CVaR 双承载窗口漂移**（checklist#4 实锤）——合并施工挂起待裁定。

## 二、进度总览

- **全景 235 对象**（159 初册+76 TDM 对账补册）：P0 域 38、P1 域 137（含补册 76）、P2 域 45、TDM 对账 1。
- **已审 77 对象**：P0 域 38/38（含双角色单轮）；P1 域 B01-B09 回测内核 9、D01-D15 Regime 15、W01-W07 权重 7 全部审毕；在飞 S01-S12/F·M·G12/T·E13；T08 TDM 全图对账完成。
- **确认缺陷并已治本 15 项**（全部带回归测试+套件复检绿）：
  | # | 对象 | 缺陷 | 修法 |
  |---|---|---|---|
  | 1 | X08 | 双键错配 P0 | 双键配对视图+撤单 remark 解析+Fill 回解 |
  | 2 | V02 | 闸C 基线回退 0.5≠pooled（认证态可翻转，机验） | `__pooled__` 键恒同步真实池化基线 |
  | 3 | V03 | FDR canonical 对 NaN 零防御出"貌似合理错数" | NaN/Inf/越界 raise |
  | 4 | V04 | 台账缺读数 or-0 静默缩分母（DSR 放水方向） | 缺 n_trials raise（fail-closed） |
  | 5 | V05 | WFA 灾难否决缺 max_drawdown 静默旁路 | 缺字段窗口强制计未通过（测试契约同步收紧） |
  | 6 | V06 | `%.0%%` 非法格式串 | `%.0f%%` |
  | 7 | V01 | Wilson 越界 rate→复数 TypeError/NaN 静默 0 | [0,1] 校验 raise |
  | 8 | X01 | rebalance 不抵扣在途单（重复触发双下单） | 同侧在途抵扣+OM 异常降级留痕 |
  | 9 | K05 | VaR portfolio_value NaN 穿透 | isfinite raise |
  | 10 | B01 | **T+1 在 tick 级被绕过**（datetime 全等比较） | 日历日归一化比较 |
  | 11 | B06 | tick 合并排序并列不稳定 | kind=stable |
  | 12 | D03 | NaN 合成 VIX 静默判"平静" | 域检查+degraded 留痕+中性分 |
  | 13 | D04 | NaN 分布穿透 Fail-Closed（8 态全 NaN 畸形） | 校验补 NaN/Inf 拒绝 |
  | 14 | W07 | NaN 回撤判 NORMAL 满配（回撤爆表被洗白） | dd/base_weight 双 NaN 拒收 |
  | 15 | B11 | ADV 缺失→冲击腿 55× 虚高（生产 artifact 全量污染） | 分母退化到层代表 ADV（对拍 199.7→3.63bp） |
- **反驳者对拍结论**：8 个 P0 数学对象核心公式零"公式写错"级缺陷（Wilson/四闸/FDR/n_eff/决策闸/DSR/Kelly/VolTarget 全部独立复算一致）；7 个反例全在路径语义与边界，已修 5、挂 2（C04/C07 属 pf_alloc 孤儿域随合并裁定）。
- **挂起登记已落位**：#ARCH-338..#ARCH-356 共 19 条主题登记（safe_write CAS 原子批），覆盖：执行域孤儿族、风控孤儿闸族、K02/K08、对账链、pf_alloc 整域、Regime 断供三腿、Wyckoff 旁路、embargo 双承载、策略管线三洞、卖出族对账、信号域地雷、数据基建三洞、TF 退路与名义 DAG、告警无推送、F02/G01、预测域 NaN、X05 笼子、轴F 立卡 8 项——执行域孤儿族（Saga/ExecutionEngine/ex_sor/order_splitter/process_fill 零生产接线）、风控孤儿闸族（K03/K06/K09+复核链）、对账链双零接线（R03/R04）、pf_alloc 孤儿四件（C02/C04/C05/C07）、B05/B09 embargo 双承载、X04 参与率监管红线不强制、轴F 立卡（K02 系统级持久化/K05 min_history/B08 purge-embargo/metrics 频率感知年化）等。
- **测试纪律**：全部修复带回归；backtest 域 1792/1793、ex_core+risk+signal_ashare 广域回归全绿（唯一红=外来 crisis 级联已移交）。

## 三、提交落地

- 队列正门累计入队 19 笔；已落地：EXEMPT-ZONE-FM 合规四批（全部战役文档）、P0 域源码修复终批（八文件）、测试适配批；B 域修复批在消化。死信 4 笔均为路径/FM 门禁演进中被合规批取代的旧快照，无内容丢失。

## 四、剩余计划

1. 在飞：D01-D15、W01-W07 → 归队后收口。
2. 待派：B10-B17、F01-F05、S01-S12、M01-M04、T01-T07、G01-G03、E01-E06、P01-P76 补册域、P2 域 45 对象（按 Best-first 顺序波次推进）。
3. 收尾：挂起登记原子批→循环检查两轮 0→红蓝对抗→全量落地核实→本晨报终版。
