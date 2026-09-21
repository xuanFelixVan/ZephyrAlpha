---
ttl: task_bound
title: ALGO top3 落地汇总（W2-T2，终极令 W2/BM-2；三卡三verdict）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: 完成（sid=st-final3-20260919）
parent_context: algo_mining_digest.md §6 + implementation_queue.csv id=1/2/3 + owner_package.md §4/§6
---

# algo_top3_summary.md — ALGO 实现队列 top3 正式考汇总

> 一句话：**三卡三 verdict = 1 PASS-待考（件②市场版开盘半小时动量）+ 8 RED + 3 RED（件③，预注册 fallback 规则）**；全波 12 主检验格 BH q=0.10 仅 1 格存活；假阳性数学与结果一致（12 格期望假阳 ≈0.012 个 @0.1% 门，观测显著格数 3=②H1/②H2 pooled/②H2 HIGH，其中仅 ① 格过全部门）。裁定#366 批准的有界矩阵第一波 top3 格全部闭合。

## 1. 三件 verdict 表（数字三口径见各报告与 csv）

| 件 | 卡 | 主检验 | verdict | 一句话死因/活因 |
|---|---|---|---|---|
| ① OFI 成交签名代理 | ofi_prereg_card.md | 当日累计 OFI→次日开收 IC（pooled+3 桶） | **RED**（LOW 桶 INSUFFICIENT） | 日内冲击存在（H1 β>0 复现 MIXED）但不延续到次日；n=415 日功效足 |
| ② 开盘半小时动量 | momentum_prereg_card.md | H1 市场版 Q5−Q1 尾盘价差 | **PASS-待考**（全门过：t=4.06≥3.29+OOS 同号+BH q=0.0006） | 活因=市场聚合层动量真存在；OOS 衰减 19.9→5.4bp（t=1.05）警告随身 |
| ② 同卡副检验 | 同上 | H2 个股版剩余段 Q5−Q1 | **RED** | 负号（日内反转迹象）IS/OOS 同向但 |t|=3.05<3.29；未预注册方向禁事后翻案 |
| ③ VWAP 偏离条件化做T | vwap_prereg_card.md | IS 选 k→OOS 净边际（3 标的） | **RED×3** | IS 三档 k 全负=无合法 k（卡 §3.2 预注册规则）；fallback k=1.5 OOS 净边际 −0.88~−6.59bp/日 全负 |

## 2. 全波多重检验账（frozen 族=12 格，BH q=0.10）

| # | 格 | t | p | BH q | 全门过 |
|---|---|---|---|---|---|
| 1 | ②H1 市场版 | +4.06 | 5.0e-5 | 0.0006 | ✓ PASS待考 |
| 2 | ②H2 pooled | −3.05 | 0.00228 | 0.0137 | ✗（t 门挂） |
| 3 | ②H2 HIGH | −2.59 | 0.00968 | 0.0387 | ✗（t 门挂） |
| 4-12 | 其余 9 格（①×4 / ②桶×2 / ③×3） | — | 0.105-0.855 | 0.32-0.88 | ✗ |

- 族构成 frozen 于三卡：①H2 4 格 + ②H1 1 格 + ②H2 4 格 + ③ 3 格 = 12。辅助检验（①H1 复现、②Spearman/sign、③27 格披露、req_cap 带）不进族、全量入册。
- 累计试验 N 账：本轮新增 12 主格（+辅助格不计 N），与 TICKM 累计 +54 格账并行披露（跨轮累计 N 纪律归口 matrix_necessity_verdict.md §3）。

## 3. 待考池增量（本轮唯一）

- **[NEW-待考] A股市场开盘半小时→尾盘动量（市场聚合层）**：全窗 spread +14.73bp/日（t=4.06），6/6 年同号；条件：市场级（等权聚合，对应 510300/等权篮子实现）、信号毛口径未过成本门、OOS 衰减至 +5.4bp（t=1.05）。升格前置=①成本后窄测（E4 口径）②滚动前向窗复核 ③与 auction_gap/隔夜情绪（ALT-B +0.262 线索）条件化交叉须新预注册卡。IS 冻结五分位边界与全部参数见 momentum_prereg_card.md。

## 4. RED 名单增量（如实入册）

1. ①OFI 日频 alpha：无预测力（t=−0.70）。
2. ②个股开盘动量：方向反（反转迹象，筛级线索 t=−3.05/HIGH 桶 −2.59）。
3. ③VWAP 条件化做T 三标的：缺正毛信号（IS 全负；OOS fallback 全负；forced 平仓占比 61-93%=日内均值回归不存在）——#304 四环证据链增补第五环（1min VWAP 级同样无信号）。

## 5. 纪律执行实录（诚实条款）

- 卡先 frozen 后取数：三卡 2026-09-19 落盘先于全部考试脚本执行；mtime 链可核。
- 参数零改动；三处实现勘误（①IS 边界误植修复、③σ 窗按卡修复、③req_cap 单位修复+卡预算行算术更正）全部在报告 §勘误 留痕，方向均不放松门。
- 数字三口径（成本/复权/窗）逐件注明；红蓝勘误下游 5 件修订在途未落地（mid_valley 等仍 15/17 旧计数）——与本车道无引用依赖，已核对（本车道引用源=digest §6+owner_package §4+etft0 csv 冻结值，不经 mid_valley 计数）。
- 数据缺口披露：绿区簇 ETF tick 仅 28 日（588200 5 日）不入正式考；2026-06 个股 tick 无空窗（tickm 卡空窗仅限其 ETF 标的）；tick=3s 切片非逐笔。
- 测试隔离：全部计算脚本与缓存在 `.runtime/tmp/bizmine/algo/`，生产表零写入、零 append。

## 6. 产物清单

| 件 | 路径 |
|---|---|
| 三张 frozen 卡 | docs/_working/bizmine_night/algo_mining/{ofi,momentum,vwap}_prereg_card.md |
| 三份考试报告 | docs/_working/bizmine_night/algo_mining/{ofi,momentum,vwap}_exam_report.md |
| 全量结果 csv | docs/_working/bizmine_night/algo_mining/algo_top3_results.csv（16 行） |
| 本汇总 | docs/_working/bizmine_night/algo_mining/algo_top3_summary.md |
| 引擎与缓存（TTL 件） | .runtime/tmp/bizmine/algo/{probe1,probe2,pull_data,exam_ofi,exam_momentum,exam_vwap,debug_vwap,assemble}.py + cache/ + results_*.json |
