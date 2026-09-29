---
ttl: task_bound
title: F74 转正建议书汇总器（全链唯一人工门）——L08 复飞矿道案卷
session: zc-l08-20260927
updated: 2026-09-29
---

# F74 · 转正建议书汇总器

> 总册行：H 段 F74，状态 missing（汇总器缺位=全流通最大单点），P0。
> 本卷=09-27 复飞复测。基册=03_promotion_ab/03_promotion_gate.md（PR-B 09-25 挖干，已判总册 missing 过时→partial）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | 四路证据（SCR-SIMGOV 治理档案/SCR-DEV 月度偏离/fw-auto latest.json/sim_memo 月档）+PA-1 三实据（双窗/FDR/衰减台账）——PR-B §6.1 逐条核收表维持 |
| 下游消费 | pipeline_events OPTIONAL_DUE_KINDS（pipeline_events.py:173-175）；combo gate；api_server GET /api/promotion-advisories(:4329)+POST /api/promotion-decide(:4375)；前端 #promotion 页；拍板后 FSM sim→production→daily_decision_orchestrator S4 已毕业包集 |
| 自动化触发 | **09-27 实测：`.runtime/strategy_pipeline/pending_events.jsonl` 中 promotion_advisory_due 计数=0（维持）**——发射方 sim_governance 仅在有 promote/demote 建议时 emit，两 sim 策略月判 null=零事件；combo gate CLI manual 无事件入口 |
| 真源与注册表 | strategy_registry.yaml（163 条，schema:58 八态词表，sim 态 2 条）；standards.yaml（002 v2 frozen 裁定#337）；campaign 簿 mining/08（8.5 转正门"挖干封矿"在案）；裁定#305/#306/#315/#337/#365 |
| 门禁与质量尺 | PA-1 fail-closed 三条件逐条落台账；token 三态校验 fail-closed（:576）；KillSwitch 探针（:594）；注册表 CAS+术后复核（:531/:549）；建议≠决定双保险；v1 尺 suspect（#306） |
| 当前运行状态 | **黄（件绿链未转，维持）**：09-27 ls 实测 data/strategy_intake/promotion_advisories/ **仍不存在**（零建议包）；四件代码+测试在（PR-B 实证）；处女链自 09-15 建成零实弹 |

## 二、子模块三级枚举（PR-B 四件+两端点+一页，维持）

1. **建议包生成器** promotion_advisory.py（四路证据读取 :116/:129/:152/:177；兜底判定 :378；build_advisories :415，hold 不产包 :428）。
2. **事件入口** OPTIONAL_DUE_KINDS→run_promotion_advisory_due（:445）；发射方 sim_governance.py:133-144（仅 actionable recs）。
3. **组合门+一页报告** promotion_combo_gate.py（THRESHOLDS 硬编码 :56-61 四条 v1；score_candidate :139；render_report :178；OUT_DIR=promotion-reports/）。
4. **Owner 拍板执行器** _token_check :576/_kill_switch_clear :594/_transition_lifecycle :614/CAS :549/台账 :723/回执 :733；api_server.py:4329/:4375；web/features/promotion/promotion.js。
5. **人工门交互面**：#promotion 页（建）+token 键 ZEPHYR_OWNER_APPROVAL_TOKEN（**生产 secrets 是否已配=未验，PR-B §6.3-3 前置核点维持**）+**触达通道=唯一缺口（飞书裁撤后仅前端横幅+落文件）**。

## 三、接线四态独立复核

- **骨架勘误（维持 PR-B 判定）**：总册 F74 `missing（全流通最大单点）` **过时**——四件齐链通，实态=**partial（处女链+v1 尺+无事件入口+无带外触达）**；今日清单 §1.4 missing 6 仍列 F74——两处应改 partial；"全流通最大单点"降格为"唯一人工门触达缺铃铛+处女链未转"。
- **事件面复核**：pending_events.jsonl promotion_advisory_due=0（09-27 实测）与"发射方条件 emit+观察期不足"自洽，非断链。

## 四、缺口清单（PR-B 五堵点维持+施工序）

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | combo gate 未切 v2 frozen 尺（硬编码 v1 suspect）**〔09-27 v9 收敛批已闭合，见刷新批注〕** | 切 standards.yaml 动态取尺+judge_std_id 跟升+测试钉值（与 F73 堵点 5 同批） | **P0** |
| 2 | combo 无事件入口（建议包→一页报告中间断链）**〔09-27 v9 收敛批已闭合，见刷新批注〕** | 挂 promotion_advisory_due 执行体尾或新 optional kind（禁 cron） | **P0** |
| 3 | 唯一人工门无带外通知（Owner 不开屏=建议无限滞留）**〔09-28 晨报承接落地（载体在途），见刷新批注〕** | Owner 裁定触达（晨报消费/邮件/死件开关三选一）；裁定前 F74 不得宣 built | **P0**（Owner 门位） |
| 4 | 处女链零实弹（生产路径未经流量检验） | tmp 目录 e2e 彩排（不污染生产） | P1 |
| 5 | token 键生产配置未验（未配=拍板面永远 reject） | 彩排时一并核 secrets | P1 |
| 6 | 上游带伤：fw-auto 停 09-16/sim_memo stats.error=CH TCP | 归 M2/XC（PR-B 登记归属维持） | P2 |
| STALE 13/假绿 5 | **不属 F74**（归 F77 §四） | — | — |

## 五、自审闸三态

**部分挖干（复核维持）**：PR-B 六向+五堵点全证引用；本卷补当日事件计数/advisories 目录双活探。未挖面（fw 停更根因/S4 消费细节/league 维度）归属有主不在本卷下钻。三态=**partial（missing 勘误成立）**。**〔过时标记 2026-09-29：三条 P0 堵点已两闭一半落，刷新见卷末批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28`（含 09-27 当日卷写作后落地件）复核＋码面现读。

- **翻面 commit（两件）**：
  - `a46e1fbc3f7`（09-27 10:19，F74 双实现收敛·v9 增量并入已落地版）——**堵点1 闭合**：`promotion_combo_gate.py` 切 v2 frozen 尺（`THRESHOLD_SOURCE=config/standards.yaml#STD-SIM-ACCESS-002（v2 frozen 2026-09-18，裁定#337）` :62 实锚；v1 suspect 注记保留防口径误读；dsr_min≥0.5+combo_corr_max≤0.7 新腿）；**堵点2 闭合**：combo 事件入口挂 `run_promotion_advisory_due` 执行体尾（`promotion_advisory.py:508-510` 实锚，`run_promotion_combo_gate()`，传动故障不反噬建议产出）——即卷内处方"挂执行体尾"选项，满足禁 cron 约束；**未走新 optional kind**（OPTIONAL_DUE_KINDS 现四席无 combo 席，:186-200 现读）。
  - `d988f1e6d0`（09-28 19:12，F74 堵点3·通知通道落地）——**堵点3 裁定面落地**：晨报承接路线选定（转正建议待办摘要面 `data/reports/morning_digest.md`，Owner 晨读唯一入口），随批 CCR +10/MTR +9 登记在册。**半落余量**：通道实体件 `algo_flow/morning_digest.yaml` 在会话分支 `c4c1eeda67`（通道件，"内容由队列袋投递落地 dev 为准"），dev HEAD 上 `data/reports/morning_digest.md` 实体与晨报生产面未见——载体在途。
- **缺口状态修订**：堵点1 P0→**闭合**｜堵点2 P0→**闭合**｜堵点3 P0（Owner 门位）→裁定已选+登记在册、载体在途（半落）｜堵点4（处女链零实弹）/堵点5（token 生产配置未验）/堵点6（fw-auto 带伤）维持。
- **自审闸三态（刷新后）**：**partial（维持；构成变化：三条 P0 堵点两闭一半落，"全流通最大单点"进一步降格为"晨报载体收尾+处女链未转"）**——堵点1/2 处方对施工面失效；"裁定前 F74 不得宣 built"前置条件中触达裁定已落，宣 built 仍受堵点4/5 与载体收尾约束。
- **复跑**：`git show a46e1fbc3f7 --stat`｜`sed -n '62p' scripts/backtest/promotion_combo_gate.py`（v2 尺源）｜`sed -n '508,510p' src/zephyr/strategy_pipeline/promotion_advisory.py`（combo 执行体尾）｜`git log --all --oneline --grep morning_digest`（两件在案）。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
ls data/strategy_intake/promotion_advisories 2>&1                                   # 不存在=零包
grep -c promotion_advisory_due .runtime/strategy_pipeline/pending_events.jsonl      # 0
grep -n "THRESHOLDS" -A 6 scripts/backtest/promotion_combo_gate.py                  # v1 四条
grep -n "STD-SIM-ACCESS-002" config/standards.yaml | head -2                        # v2 frozen 在
sed -n '4329p;4375p' src/zephyr/frontend/dashboard/api_server.py                    # 两端点
```
