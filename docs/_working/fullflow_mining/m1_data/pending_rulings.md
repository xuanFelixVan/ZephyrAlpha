---
ttl: task_bound
---

# M1 数据链 · 待裁清单（一行一案）

- **R-M1-01 CH 影子表/隔离表退役**：现象=kline_daily_hfq_{legacy_20260924,preversion_20260925,quarantine_20260925}、index_valuation_daily_quar_20260920、weekly/monthly_hfq_legacy、index_valuation_daily_v2 等 8+ 张留观表占用 c1_market（WO-004 复权重算与 C-36 遗留）；已试路径=无退役通道，留观无 TTL；选项=①archiver 正门 export→verify→drop 进冷库后净删（Owner 门）②原地 RENAME 归 _retired 库；建议=①+7 天留观计时器。工作量 0.5 天/表。
- **R-M1-02 daily_valuation 幽灵行+零值行清理**：现象=77,668/259,238 FINAL 行落 14 个周末幽灵日（C-36 实测）+close/amount/turnover 全 0 行（supply_sentinel 实测）；已试路径=四路哨兵已捕获，清理被 Owner 门挡住；选项=①按 trade_calendar NOT IN 谓词出 dry_run 清单→Owner 批→mutations 删②只拦增量不清理存量；建议=①（写侧日历闸 C-34/C-35 同批立项）。
- **R-M1-03 rate_decision_calendar 435 行 epoch 残留清理**：现象=decision_date<1990-01-01 占全表 14%（quality_sentinel 表册实测注）；建议=随 R-M1-02 同批出 dry_run 清单。
- **R-M1-04 l2_tick 空表（0 行）退役评审**：现象=表在库无行，tick_depth_5 才是五档落点；选项=①waste_table_scanner 跑分+退役②保留待用；建议=先跑 scanner 出证据再裁。
- **R-M1-05 宪法/骨架册"16 表交叉轴"口径修正**：现象=AGENTS.md §8 与 00_skeleton D11 写"16 表"，代码真源 _XREF_SPECS=13 轴；已试路径=无；选项=①宪法等长替换改"13 轴"②加基准日期注；建议=①（#ARCH-351"哨兵 16 表"旧口径另立注防混淆）。
- **R-M1-06 清洗三引擎接线立项（WO-④-03/04 承接）**：现象=cleaning_rule_engine/cleaning_anomaly_engine/data_anomaly_alerter 建成零调用、DSL 无 YAML 承载（2026-09-24 grep 复核仍零调用）；建议=挂 supply_sentinel 同款宿主托管+config/ 规则 YAML，先 flag 后 block 两档灰度。本车道可施工，报总筹排期即可，非真裁定。
- **R-M1-07 TradingWatchdog/RestartMiniQmt 计划任务正式退役或换道**：现象=两任务 Disabled 长期挂册（schtasks 实测），miniQMT 已清退；建议=走 D2 退役登记；若 tick 桥模式需看门狗则立桥版新件。
- **R-M1-08 #ARCH-351 退役映射表落地优先序**：现象=miniQMT 清退 24 任务无退路（open P1，裁定#376 已授权设计）；建议=TF02 16 全裸任务最险优先，走 01 册 B1 修法。

## 三态汇总（2026-09-25 快照）

- **挖干可施工**：D1/D2/D3/D4/D5/D6/D7/D10/D11/D12 十环节（D8/D9 随 04 册主张收编同挖干）。
- **待挖**：无（各册六向均有实证；D12 图谱内容质量归 M8 专项，本车道不重复）。
- **待裁**：R-M1-01~05、07、08 八案已按一行一案登记；R-M1-06 为排期申报非裁定。
