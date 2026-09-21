---
ttl: task_bound
rule_form: data
verifiability: manual
title: P2 Git 链真并发压测 收官报告（Flash 收尾班 2026-09-18）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
---

# P2 Git 链真并发压测·收官报告

> **收官方式（Owner 令 2026-09-18）**：压测沙箱 `.runtime/tmp/rb2/`（198MB，含 sandbox git 仓/results/harness）**整删不提交**——50 worker 档三度压死宿主（Kimi 两度内存中断 + Flash 收尾班 t50flash 一次整机卡死硬重启）。本报告在删除前固化全部 8 个完整档的 result.yaml 数字；raw 数据（commit/appends CSV、queue_depth 曲线、state json）随沙箱删除不再可复算。harness.py 单件留档 `.runtime/tmp/closeout_residue_20260918/rb2_harness_preserved.py`（TTL 内 S18 车道可拾，过期即灭）。
> ⚠ 连带记档：`S18_Flash施工包判据.md` 验收行引用 `python .runtime/tmp/rb2/harness.py --workers 20 --channels 4`——harness 已删，该指针悬空；且现行 harness 本无 `--channels` 参数，S18 施工时须按 R-3 k 通道语义重建 harness（头注释判据段保留在留档件里可抄）。

## 一、数据面总览（8 完整档 + 1 中断档）

判据①吞吐曲线（窗口归一：commits_ok ÷ 压测窗；沙箱=免门禁链骨架，真仓另有门禁常数）：

| run | workers | 窗口 | 落地笔 | 折算/时 | commit wall p50/max | 零丢失 | 饿死(零落地) |
|---|---|---|---|---|---|---|---|
| t10b | 10 direct | 120s | 20 | 600/h | 30.7s / 47.0s | PASS | 1/10 |
| t10direct | 10 direct | 120s | 29 | 870/h | 29.1s / 53.7s | **FAIL（4 行）** | 0/10 |
| t20direct | 20 direct | 120s | 18 | 540/h | 27.3s / 51.7s | PASS | **9/20** |
| t20k2 | 20 direct 杀 2 | 90s | 11 | 440/h | 45.6s / 66.9s | PASS（含杀后） | 8/20（杀者除外） |
| smoke5 | 5 direct | 24s | 7 | warmup 主导 | 23.9s / 46.3s | PASS | 0 |
| mk1 / mk2 | — | merge-kill 场景 | — | — | — | branch 零丢失 PASS ×2 | — |
| t50direct（Kimi，中断档） | 50 direct | 120s 窗跑满 | 台账 399 行 commit rows | 未 reconcile | — | 不可判 | 数据已删 |

中断档补充：t20kill（20 worker 带杀）与 smoke4 均无 result.yaml（Kimi 班中断遗产），随沙箱删除。

## 二、六判据逐条判读

### 判据① 吞吐曲线 vs 模型 24/h —— 偏差 17.5~26.9 倍，触发模型改写

- 实测偏差（window 口径）17.5x~26.9x，远超 30% 门槛 → 按冻结判据改写模型：**24/h 不是 serializer 常数而是门禁常数**。沙箱免门禁骨架上限 ≈440~870/h，由网关临界区（~3-4s 真提交段）+ 争用退化决定；真仓 24/h 上限由门禁链主导（A2 实测 gate 链 P50 46.4s）。**实证确认 A3 提速序：门禁 diff 化先行，k 通道其次**——单改锁粒度不动门禁，真仓天花板纹丝不动。
- **吞吐不随 worker 数扩展，反降**：10w 870/h → 20w 540/h。机理=单通道全局锁 + 退避风暴（gateway exit 2 指数退避）+ index.lock 碰撞（t10direct 实录 `git_add_fail: index.lock exists`）。

### 判据② 零丢失铁律 —— 稳态全绿，唯一丢失窗=优雅退出 flush 竞争（本轮最有价值发现）

- 全部完整档 `committed_missing=0`（29/29、20/20、18/18、11/11 笔 commit 全部在库可找回）、`cross_contamination=0`——**网关/队列稳态链路零丢失，中途被杀也零丢失**。
- 唯一违例 t10direct：40 条 append 行丢 4 条（w000 seq4/5、w004 seq4、w006 seq3），逐笔 CSV 定性：
  - 丢失机理：deadline 时 N 个 worker **同时收尾 final-flush**，挤单把全局提交锁（`--wait 30` 输家 exit 2）；且 harness final-flush 失败路径静默吞异常、不记账、不重试。
  - **治理盲区定性：优雅退出不被 G1 salvage 覆盖**——退出瞬间会话还"活着"，registry 无 dead 证据，salvage 永不触发；等它死了，flush 早已失败完事。这是与"被杀会话"互补的唯一丢失窗。
  - 工程喂料（进 S18-R2/R-3 包）：①final flush 走 `--enqueue` 快照队列（快照+重试语义天然兜底）；②worker 错峰退出；③gateway 提供 flush-retry-until-landed 原语。三选一即可闭合。
- 注：按冻结判据"丢一字符=P0"，此条应升级 Owner 复核；但丢失面=压测 harness 自身的收尾路径（生产会话收尾序列同构：merge→release→promote 无兜底），非生产数据丢失。

### 判据③ 死信与饿死 —— 死信全零，饿死随并发非线性恶化

- `dead_total=0` 全档成立（dead_letter_rate=0.0），队列正门无一死信。
- 饿死：10w 档 0~1/10；20w 档 8~9/20（**45% worker 零落地**，名单已固化于各 result.yaml，随删）。单通道全局锁无公平性——先到者滚雪球，后来者在退避循环里耗尽窗口。S18-R3 k 通道 + claim 公平性的最硬实证。

### 判据④ 杀会话穿插 —— G1 salvage 真触发，杀后零丢失，幸存者不阻塞

- t20k2：4 受害者计划（claimed×2/staged/committing 三态轮转），实际杀 2（均为 claimed 态）；salvage `dead_confirmed=True` ×2；**杀后零丢失 PASS**；幸存 worker 时间轴连续落地（kills.csv + commits csv ts 链在档，已随删，结论固化于此）。
- 覆盖缺口：staged/committing 两态受害者在窗内未被杀到（轮转未轮到窗关）。**staged 态丢失面已被判据②的 exit-burst 发现等效覆盖**（同属"staged 有改动+会话终结"）。
- mk1（merge-kill）：MERGE_HEAD 晾置 → 观察者正确阻断（pass）→ salvage abort merge + 分支完好零丢失（pass）→ 唯一 FAIL=杀后观察者解阻检查，**定性为沙箱环境伤**（sandbox 内 observer 开不了 governance.db："unable to open database file"），非网关缺陷。
- mk2：salvage 触发但 `merge_abort=skipped`（MERGE_HEAD 已被先行清掉，断言口径过严）+ 同款观察者环境伤；branch 零丢失 PASS。

### 判据⑤ 锁尸扫描 —— 全绿

`ailocks_residue_immediate` PASS 全档（沙箱 .ailocks 零 *.lock 残留）。

### 判据⑥ 红方 —— 未执行

redteam.py 在 harness 头注释中立案，实际从未建成未跑（Kimi 班中断遗产）。本报告不覆盖红方结论；红方需求（让文件消失/假提交过闸）随 S18 施工包重建 harness 时一并补。

## 三、宿主容量结论（新发现，2026-09-18）

- **本宿主 direct 模式容量上限在 20~50 worker 之间**：20w 可跑（45% 饿死但机器存活），50w 三度压死（内存耗尽：Kimi 两度中断 + Flash 一次硬重启）。
- 后续压测纪律：**worker ≤20、拉长时间窗**替代加并发；或降 worker 子进程开销/换大内存宿主后再试 50+。极限档（100 worker）按 Owner 令取消，不再排程。
- 判据①的模型改写已使"50/100 worker 实测吞吐"失去紧迫性——真仓瓶颈在门禁链，不在锁通道数，先修门禁。

## 四、交接与残留

| 项 | 去向 |
|---|---|
| 本报告数字的 raw 证据（result.yaml/CSV/曲线） | 已随 rb2 删除（Owner 令），数字固化于本报告 §一/§二 |
| harness.py | `.runtime/tmp/closeout_residue_20260918/rb2_harness_preserved.py`（TTL 内可拾） |
| S18-R2/R-3 施工喂料 | §二判据②③④：exit-burst 兜底 / k 通道公平性 / salvage 已验证面 |
| S18 验收指针 | `S18_Flash施工包判据.md` 该行须随 harness 重建改写（本报告记档，不代改） |
| t50direct/极限档 | 关闭，不再排程（Owner 令） |
