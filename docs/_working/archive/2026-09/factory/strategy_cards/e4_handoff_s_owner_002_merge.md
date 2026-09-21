---
ttl: task_bound
completes_when: S-OWNER-002 分支成果被合并（cherry-pick 指定 commit 集）或 Owner 明示放弃；本交接包随之归档。
---

# 交接包 — S-OWNER-002「regime→策略包切换器」分支合并指引（2026-09-17）

- 会话: st-sowner002-20260916 ｜ 分支: `ai/st-sowner002-20260916/s-owner-002-regime-switcher`
  ｜ worktree: `D:\ZephyrAlpha\.worktrees\st-sowner002-20260916`
- 结论速览: 框架验证完成，**verdict=FAIL（H 不成立：OOS Sharpe 差 CI 含零；增量来自降敞口非择时）**，
  机制验证通过；裁定#304 已原子登记。卡归档留案底，生产流转不做（Owner 门位另行裁定）。

## 1. 待合并 commit 集（**禁整支 merge，必须 cherry-pick**）

分支基点=dev@`655a921eec`，但分支上先落了两枚**他车道探针 commit**（队列串行化落偏所致，
标注"预期死信勿落地"）——整支 merge 会把它们带进 dev。请按序 cherry-pick：

1. `4376f35627` — E4 冻结文档预注册（验收线先于跑数的顺序留痕，裁定#304 证据链起点）
2. `fa5c8febaf` — 出证报告+裁定#304 原子登记（含 registry 同步至当时 dev 版+本条目追加）
3. `89dd33dd8a` — 切换器模块 7 件+CLI+24 用例测试+登记面派生件+考试产物归档+报告产物路径修订
4. 本 handoff commit（最后一批：合并指引+两枚生成器派生件）

冲突预案：`fa5c8febaf` 中的 ruling_registry.yaml 以"当时 dev 版+#304"为基座，若合并时
dev registry 又前进，按"保持 dev 已有条目+仅追加 #304"机械重放（CAS 语义，无内容歧义）。

## 2. 遗留事项（维护班口径，施工 AI 不修复）

1. worktree 队列项 `q-20260917-st-sowner002-20260916-0001`（冻结文档自动入队副本）因
   OPS-GUARD 阻断 worktree 内 pending→processing 迁移而无法 drain（工具层缺陷）——
   该项内容已经直连通道落地（`4376f35627`），**作废勿重放**，建议直接清理。
2. 分支上两枚探针 commit（`e10ac5acc4`/`2924601305`）属他车道产出，本会话不代删；
   cherry-pick 路线天然绕开。
3. regime/kline 表 `FINAL` 查询触发 ClickHouse Code 181 服务端崩溃（2026-09-17 实测，
   复现路径=对 c1_backtest.regime_snapshot_history 带 FINAL 的任意多列查询）——
   全仓扫描其它带 FINAL 的查询是否踩同一坑，建议列入维护班清单。

## 3. 会话收尾状态

- 测试: 24 用例两轮 0 失败（红蓝四场景含在内）。
- claim: 本会话全部文件 claim 已释放（`git_commit.py --release-only`）。
- 临时面: `.runtime/tmp` 会话脚本/日志/缓存已清；worktree 与分支按 001 先例保留待合并。
