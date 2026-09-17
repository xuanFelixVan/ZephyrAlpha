---
ttl: task_bound
title: 交易决策链总包战役终局交付报告——五任务收口+ETF 五表修复+合并链 M1-M5（诚实条款版）
session: st-tdchain-20260917
date: 2026-09-18
completes_when: Owner 阅毕
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# 终局交付报告（st-tdchain-20260917，2026-09-18 07:3x）

> 口径遵裁定#325：禁"全仓全绿"表述；以下逐项如实，绿有证据、黄有原因、红无隐瞒。

## 一、交接令五任务终态

| 任务 | 终态 | 证据 |
|---|---|---|
| Task 0 合并收口 | ✅ 五路归 dev：M1 regcal=0060289c66 / M2 p2b=259b15c612 / M3 orchp3=2fa92002 / M4 sowner001 整支 merge / M5 sowner002 按交接包 cherry-pick（cp1=08d3fa97+cp2 落地；cp3/cp4 队列在飞） | dev 祖先核查 ✓；835→1766 tests 三轮全绿 |
| Task 1 做T v2 | ✅ 按 #304 新口径封存（窄考试 RED 在案）；**数据面超额交付**：ETF 五表 4.12 亿 UTC 误标行全修复（remaining_utc=0），备份五表在库可逆 | e1 簿终态+etf_tzfix_exec*.log 九轮留痕 |
| Task 2 regime r4/r10 | ✅ st-regcal 前班已按预注册协议做完，本班合并复核：R3 方向语义退役（比"降权/下线"更彻底），锚定后 r3 季符号一致率 0.385→0.80 | e3 簿复核记录+regime_recal_results 报告 |
| Task 3 WYF-3 | ✅ 前班已终态（#264→#271→#285 证伪加厚，v2 重跑 0/204 维持置零），本班封矿核实 | e4 簿 |
| Task 4 G07 关联核查 | ✅ 有条件赞成 evidence 附注接线、禁入主判链（值域互斥 fail-closed）；挂起真因=定位器回放锁死；裁定 COMBINATION_INVALID 不禁打标用途 | e5 簿（file:line 全带） |
| Task 5 准入判据 | ✅ STD-SIM-ACCESS-002 转 frozen（裁定#337）：81 全量覆盖/55 翻转零不可解释/v1拒v2放=0 件；STD-SWITCH-001 维持 draft（#305 自留门）；机读证据归档 exp_evidence/ | q-0005+standards.yaml |
| 骨架挖矿（Owner 追加令） | ✅ docs/_working/tdchain_mine/：总谱 a0+九环节作业簿（三轴对账防遗漏），已落 dev=e7a17a9012 | 本文件夹 |

## 二、端到端与红蓝

- **QMT 100 股模拟单**：✅ 本夜已完成——03:08 自动化战役第三棒实弹（600000.SH 100 股 BUY LIMIT 8.10→SUBMITTED 全链打穿→撤单受理），官方入账 60747a8a47+证据 qmt-bridge-smoke-20260918-c3.yaml。本班防重复下单（同一模拟账户二次下单=污染证据链），broker 侧对账补强因 XtMiniQmt 进程白班前不在线而留晨间（e7 簿登记，零新下单只读核验）。
- **红蓝+循环检查**：R1/R2 连续两轮 1766 tests 全绿+六注册表 YAML 全过+四关键文件编译全过——达标线（连续两次 0 问题）闭环。红蓝抓出 1 真红=抽查器自身时区 bug（已修，4/4 随机行深比对全等）；数据面幂等/可逆性抽查全过。

## 三、诚实条款（黄/红项如实列）

1. **队列 4 件待 serializer 落地**（q-0004 cp3 切换器模块 17 件 / q-0005 E6 批 6 件 / q-0006 cp4 交接包 / q-0007 修复工具+四簿终态）：快照入袋零丢失；积压原因=多车道 24 件排队+serializer lease 被僵尸 status 进程反复持有（已清两只自家/他车僵尸，详见 e8 簿）。落地侧门禁我方文件已全部预过（M11 注记/复杂度重构 16→6、22→8 等价对拍 152 组/depgraph 9 节点/token 12 枚）。
2. **板块分钟 15/30/60m 三天合成=裁定跳过**：无独立消费方+1m 原料系合成近似+无现成工具且存量 15m 桶时间戳发散存疑（三问停止判据），缺口登记不造管线。
3. **120min 表=豁免**：tasks.yaml:2027"60min 两根聚合"先例，查询期聚合即可，不建表。
4. **kline_index_intraday 新表**：需 apply_market_tables_ddl.py（residual C1 独占）→挂单；现用 510300 代理。
5. **depgraph 全量重扫**：reconciler post-flush 例行职责（我方新文件 9 节点已预登记过 NEW-FILE-DEPGRAPH 闸），多车道在飞期手动 --force 会与其扫描冲突，未手动执行。
6. **stash 6 笔**（pre-merge 净窗扫描快照+他会话 WIP）：保留未 pop——两会话已重提交各自内容，221 件暂存区现状下 pop=高冲突破坏行为；留作恢复档案，列表见 stash list（tdchain-* 前缀）。
7. **裁定#304 三方撞号**（regcal/做T砍/切换器 verdict）：存量 tombstone 现象，引用须带 title 消歧，编号唯一性治理属维护班（V-06/#316 已立法）。

## 四、裁定登记

- **裁定#337**（本班唯一新裁定）：STD-SIM-ACCESS-002 转正 frozen+#306 红队三条款处置（③回写/②#315 追认/①治理层挂单）+SWITCH-001 维持 draft 备案。

## 五、防复发资产

- 修复工具 scripts/ch/repair_etf_minute_tz_split.py（冻结台三代流，M11 一次性脚本豁免注记）随 q-0007 收编。
- 挖矿总谱+九作业簿=本战役全知识底稿（含三轴战役对账、合并预案、复活路径、G07 接线建议）。
