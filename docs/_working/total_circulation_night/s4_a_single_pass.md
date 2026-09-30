---
ttl: task_bound
session: st-circ-a6-20260930
batch: 第4批/A6 挖矿簿 1/6
---

# S4-A 手术单 — PRECOMMIT 通道单趟化（Phase-A/B 两段合并重设计）

> 立档：2026-09-30 ｜ 车道：A6（design-only，本簿不附代码，施工 lane 按本单写）
> 真源文件：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`
> 遥测真源：`.runtime/audit/precommit_channel_stats.jsonl`（264 行，本会话只读量取）、`.runtime/audit/commit_block_events.jsonl`

## 1. 现象量级（遥测实证）

- rc 分布（264 次通道运行）：`rc=1 ×259、rc=0 ×1、rc=143 ×4`。
- 时延：p50 **49.9s** / p90 **162.9s** / min 7.1s / max **1783.8s**（≈30 分钟，E4 双超时链形态）。
- Owner 立档口径（战役级窗口）：真阻断率 31.6%、p50 46.4s——与本窗口 p50 同量级，真阻断率随窗口漂移（本仓全量账本 `commit_block_events.jsonl`：precommit_channel_blocked ×140 / global_debt_warned ×230 / adopted ×9）。
- 关键差分：**rc=1 样本 fast_subset_ms/total_ms 中位 = 0.994**（Phase-A 快败短路主导，快段 p50 35.7s 即死）；唯一绿样本 total 25.7s = Phase-A 15.1s + Phase-B 增量 10.6s。即：**绿路径为 Phase-A 单独一次 pre_commit 框架调用多付约 6~15s**；阻断路径省的是慢尾（分钟级）。

## 2. 机理锚点（现行 Phase-A/B 结构）

| 位置 | 内容 |
|------|------|
| `git_commit_gateway.py:385-393` | D3 两段式设计注记：Phase-A=全通道减慢尾（SKIP 反选单次调用，首败短路）；慢尾清单 `_PRECOMMIT_SLOW_TAIL_HOOKS`（:394-417，19 台 T2/T3 档） |
| `:420-428` | `_precommit_fast_subset_enabled`：pytest 环境自动 OFF（50-commit 套件时长保护） |
| `:431-433` | `ZEPHYR_PRECOMMIT_PHASEB_FULL=1` 回退手柄 |
| `:3479-3540` | `_precommit_execute`（Phase-B）：`pre_commit run --files` 逐 chunk，timeout 900s（`:384 _PRECOMMIT_RUN_TIMEOUT_S`），mutation 侦测重跑 1 次（:3502-3539） |
| `:3772-3837` | `_precommit_run_scoped`：临时索引全生命周期（rev-parse HEAD→read-tree→构建 :3460-3477）；**Phase-A :3802-3820**（`_precommit_fast_subset` :3839-3877，timeout 300s，首败短路 ：3871-3872）；**Phase-B :3821-3831**（Rx-4 收窄：SKIP 反选快段，输出归因面合并 ：3830-3831）；finally 清临时索引 ：3832-3836 |
| `:2746-2754 / :3992-4004` | 锁外前移调用点 / 锁内指纹复核失败回退点（D2 出锁手术） |
| `:3727-3753` | E4：超时 fail-closed 拒袋（300s 快段超→900s 全量超→墙钟 1200s 的 73/552 病根处置） |
| `:3659-3663` | 归因语义：own 阻断 / foreign warn / mutation 重跑 / 超时拒袋 / 其余 infra 放行 |

**本质**：绿路径 = 两次完整 pre_commit 框架调用（快段一次 + 慢尾一次），快段在 Phase-B 已被 SKIP 反选（Rx-4），剩下的重复只有**框架自身开销**（python -m pre_commit 启动 + env 检查 + config 解析）；阻断路径 = Phase-A 短路救回慢尾分钟级。

## 3. 设计（意图，不附码）

**原则：单趟化的收益在绿路径框架开销，代价在阻断路径丢失短路——用遥测定决策，不拍脑袋。**

1. **方案①（推荐）单趟 + 快台前置排序**：`_precommit_run_scoped` 合并为一次 `pre_commit run`（全 hook 集、禁全局 fail_fast——:3806 既有论证成立，foreign 失败不得掩蔽 own 失败）；短路诉求下沉到 `.pre-commit-config.yaml` 的确定性快台 per-hook `fail_fast:true`（:391-393 Rx-3 已给 4 台配好）+ 配置序前置快台。一次调用天然保 own/foreign 全归因面。
2. **验收门槛（数据判据，施工前先量）**：借 `ZEPHYR_PRECOMMIT_PHASEB_FULL=1` 已有手柄 A/B 实测一次，若「绿路径框架开销节省」<「阻断率 × 慢尾平均时长」的 1/5，本单**降级为不做**（两段式更优）——按本窗遥测粗估：绿样本 n=1 不足以拍板，这正是先 A/B 的原因。
3. Phase-A/B 代码不删，改由单趟开关 `_precommit_single_pass_enabled()` 门住（出厂 OFF→Owner 窗口翻转），两段路径保留为回退（对齐 E4/两段式的既有回退手柄风格）。
4. **不动面**：临时索引机制、mutation 重跑、own/foreign 归因器 `_precommit_decide_failure`、超时数值、SKIP 清单、E4 fail-closed。

## 4. 红测两针（先证能红）

- **R-A1 调用次数断言**：monkeypatch `run_subprocess_hidden` 计数。开启单趟后，一次绿路径通道对 pre_commit 的 spawn 次数必须 =1——**现码（两段式）绿路径 =2，必红**。
- **R-A2 归因面全等断言**：注入「own 失败 + foreign 失败 + 快台失败」混合输出场景，单趟实现的 `_precommit_decide_failure` 输入归因面（own_failed/foreign_failed 集合）必须与两段式合并面（Phase-A 输出 + Phase-B 输出）逐段全等——**现码在「Phase-A 短路场景」跑同一断言必红**（短路时慢尾段缺失，归因面天然不全；此红证明单趟在归因完整性上的正向收益）。

## 5. 差分矩阵（两段式 vs 单趟，逐例终局判定全等）

1. 全绿；2. own 单失败；3. foreign 单失败（warn 放行）；4. own+foreign 混合；5. Phase-A 短路场景（快台失败——单趟终局判定须与现两段一致）；6. mutation 重跑消解（两次语义）；7. 快段 timeout（300s）；8. 全量 timeout（900s→E4 拒袋）；9. pre-commit 不可用（infra 放行）；10. 空 repo 无 HEAD（skipped 放行）；11. >200 文件分批；12. pytest 环境自动 OFF（单趟开关同款语义）；13. merge 跳过（:3682-3683）。

## 6. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | 阻断路径丢失慢尾短路→阻断批次从 ~36s 变全量分钟级 | §3.2 数据判据门槛；快台 per-hook fail_fast 保底（快台失败仍早死于该台之后） | 慢尾中的 foreign 债失败会拖满全量才 warn |
| 2 | 配置序重排影响他通道（裸 commit 面 hook 顺序） | 排序只动确定性快台相对位置，语义零变化；.pre-commit-config.yaml 变更走独立 commit 可单独 revert | 低 |
| 3 | 单趟开关与 pytest 自动 OFF 交互 | §4 矩阵例 12 显式覆盖 | 低 |

回滚：改动集中于 `_precommit_run_scoped` 函数族 + 配置排序，开关出厂 OFF，`env ZEPHYR_PRECOMMIT_SINGLE_PASS=0` 或单 commit revert 即净退。

## 7. 估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 1 | PHASEB_FULL A/B 实测取框架开销与慢尾分布 → 过 §3.2 门槛 | 0.5 h |
| 2 | 单趟开关 + R-A1/R-A2 红测先跑取红证 | 1.0 h |
| 3 | 配置快台前置 + 差分矩阵 13 例全绿 | 1.5 h |
| 4 | 真实提交灰度（10 次 commit 对照 total_ms 分布） | 1.0 h |
| 合计 | | **4.0 h** |

## 8. 执行留痕（施工车道 G1 · st-circ-g1-20260930 · 2026-10-01）

**状态：数据门槛实测未达标 → 按簿 §3.2 判两段式更优，登记不施工。**（簿内预设出口："若「绿路径框架开销节省」<「阻断率 × 慢尾平均时长」的 1/5，本单降级为不做"）

**门槛三项实测值（不拍脑袋，全量取证）**：

| 量 | 实测值 | 取证面 |
|---|--------|--------|
| 绿路径框架开销节省 S | **1.9s** | `pre_commit run --files AGENTS.md` 全 64 hook 全 SKIP 纯框架调用（零 hook 执行），best-of-3: 2416/1872/2361ms；两段式绿路径=2 次框架调用、单趟=1 次，节省=恰一次调用开销 |
| 阻断率 | **98.2%**（279/284） | `.runtime/audit/precommit_channel_stats.jsonl` 全窗 2026-09-24T14:26→2026-09-30T17:40 UTC，n=284：rc=1×279 / rc=0×1 / rc=143×4；rc=143（超时拒袋）单独计 |
| 慢尾平均时长 | **10.6s**（唯一直测下限） | 窗内唯一绿样本 fast=15140ms/total=25719ms → Phase-B 增量 10.6s；blocked 样本 fast/total 中位 0.994（279 例全在快段即死，慢尾零直测样本）；间接量级=E4 38 台扫测最长单台 13.5s×19 台慢尾≈数十秒~分钟级 |

**门槛判定**：最保守参数化（0.982×10.6）/5=**2.08s > S=1.9s**——即便把慢尾压到唯一直测下限、阻断率按窗口实证，S 已不达标；慢尾按 E4 实际量级（数十秒）则差距 5~30 倍。**结论：阻断路径丢失 Phase-A 快败短路的代价（98% 趟次分钟级慢尾白付）结构性压倒绿路径省一次框架调用（1.9s/趟）——两段式更优，不施工。** R-A1/R-A2 红测随之不落（无施工面）；`_PRECOMMIT_SLOW_TAIL_HOOKS`/Rx-3 快台 fail_fast/Rx-4 收窄维持现状。

**边界与让位登记**：①本会话同期在 `git_commit_gateway.py` 落地了 S4-E（tracked 快照 4→1，见 s4_e_b4_snapshot.md §8）——E 施工全程未触碰 Phase-A/B 结构（:385-433 常量族与 `_precommit_run_scoped` 两段编排零改动，E diff 面=守卫函数+编排点两处，可审计）；②A2 车道 debt 棘轮在飞内容随 E 投 adopt 收编（披露见 E 提交 message）；③本判定数据窗含 E4/E2 出锁前混合期，若后续通道形态再变（如 out-of-lock 全量化后阻断率显著回落），本单可按同门槛公式重测再议——登记于本节即重开依据。
