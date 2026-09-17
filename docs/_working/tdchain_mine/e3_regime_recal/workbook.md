---
ttl: task_bound
title: E3 regime r4/r10 重校准合并复核作业簿——方向语义退役落 dev
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E3 regime r4/r10 重校准合并复核作业簿

## 六向台账

- **目标**：交接令任务 2（r4/r10 方向失真 walk-forward 重校准，失真不改则降权/下线+登记裁定）。侦察结论：**重校准已由 st-regcal-20260917 班按预注册协议执行完毕**（协议先 commit 后跑数，纪律合规），成果在 session/st-regcal-20260917 分支待合并。本环节=合并+复核裁定链完整+落档。
- **证据**：
  - 起点：裁定#304 实证 r4/r10"看空态"前向 20 日收益 +0.26%/+0.92%（方向失真，切换器系统性卖低）。
  - 协议预注册：26ac558beb（docs/_working/regime_recal/regime_recal_protocol_2026_09_17.md，跑数前 commit——考试纪律合规先例）。
  - 执行落地：a2ab567992 "裁定#304 r4/r10 方向失真重校准——HMM 组件锚定+态层方向语义退役"——src/zephyr/regime/core/regime_detector.py+tests/regime/test_regime_detector.py+config/trading_decision_map.yaml+结果报告 regime_recal_results_2026_09_17.md+ruling_registry+蓝图。
  - **方向定案=态层方向语义退役**（比"降权"更彻底：r4/r10 不再携带方向语义，只作状态输入），与本环节目标"失真不改则降权或下线"一致且更优。
- **块**：B1 合并（E0 的 M1 步）；B2 复核：分支带来的裁定条目编号不撞 dev、结果报告数字与 #304 实证自洽、测试随合并全绿；B3 本簿回写+e0 台账联动。
- **依赖**：E0-M1；无其他。
- **三态**：挖干（合并即收口）。
- **下一步**：合并后跑 tests/regime 冒烟+读结果报告核对结论段，回写本簿。

## 复核记录（合并后回写）

（待 M1 完成）

## 长尾登记

- regime/kline 表 FINAL 查询触发 ClickHouse Code 181 服务端崩溃（s-owner002 交接包实测，复现路径=c1_backtest.regime_snapshot_history 带 FINAL 多列查询）——全仓 FINAL 查询排查属维护班，本环节只在 e8 红蓝中加一条探针。
