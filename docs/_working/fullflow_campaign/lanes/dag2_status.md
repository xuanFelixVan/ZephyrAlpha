---
ttl: task_bound
completes_when: BRK-050 剩余无依赖任务的机械原因分解被总包接受，且推导器在版本保护内可重跑再生
---

# BRK-050 · 任务依赖推导车道状态（st-ff-dag2-20260918，2026-09-18 22:0x 实测）

> 本文件只记**本轮实跑**数字（R-019：交工数不跨腿继承）。产物真源=
> `docs/_working/fullflow_campaign/lanes/dag_dependency_proposals.md`（由推导器生成，禁手改）。

## 1. 本批落地面（真源义务）

| 件 | 作用 |
|---|---|
| `scripts/derive_task_dependencies.py` | BRK-050 推导器进版本保护（此前不在 HEAD/不在盘/不在历史任何一笔，只存活于队列 blob）——落地前它是"手工维护 28 条边"的唯一风险源（宪法 §9.5） |
| `src/zephyr/data/config/tasks.yaml` | 推导器 `--apply` 产物：+20 条高置信边 / 16 任务被改写，对 HEAD **零删除边**（单调 insert，见 §3 证据） |
| `docs/_working/fullflow_campaign/lanes/dag_dependency_proposals.md` | 按 HEAD 基线重生成，替换 19:31 那份按**死信快照**生成的失真记载 |
| 两份注册表 | 新 .py 的大白话翻译 + 新 .md 的 creation_token（判据：token 须对 serializer 干净工作树可见=在 HEAD 或随本批入面） |

## 2. 真实剩余数与机械分解（本轮实测，非普查快照）

- 本批前：`236 无依赖 / 264 任务 = 89.4%`（普查记的 262/235=89.7% 是 13:59 基线，其后
  `85ef0962d0` 净增 2 任务，其中 1 个自带手写前置 → 89.4% 才是本批起点）。
- 本批后：**`225 无依赖 / 264 任务 = 85.2%`**（−11 任务，+20 边，+9 任务由他道手写前置）。
- 剩余 225 的构成（逐条从产物三节反查，不重复计数）：

| 桶 | 数量 | 机械原因（为何推不动） |
|---|---|---|
| A 完全无表级血缘证据 | **217** | 推导器的边只存在于"**某任务实现码读到的表 ↔ 另一个任务的 `table` 字段（写入表）**"。这些采集任务写的表在 tasks.yaml **册内无任何消费方**（读方住在 strategy_pipeline/backtest，不是调度任务），故册内既无 producer 也无 prose 点名 → 无证据可推，不是工具偷懒 |
| B 仅 medium 建议（未落地） | **8** | ①**多生产者歧义**：同一张表被 ≥2 个任务的 `table` 字段声明写入 → `_resolve_edges` 判 medium（宁缺毋假）；本轮 §2 表级行 45 条全为 medium。②**跨文件一跳**：读表发生在实现函数 import 的模块里（`impl_module` 24 条），一跳之外还有几跳不做（放大即错） |
| C 超扇入预算被真丢弃 | **112 条边** | `MAX_NEW_DEPS_PER_TASK=4`：TaskQueue 语义是"任一前置 FAILED → 当前 BLOCKED"，扇入过宽=故障耦合放大。超预算同族边只登记（§2.1） |
| D 跨日界（边**保留**，只标注） | **81 条** | 生产者档期晚于消费者（如 `daily_kline` 16:30 → `intraday_sector` 09:05），运行时按"前一交易日已满足"处理，声明价值在 catchup 拓扑重放 |
| E 成环被弃 | **2 条** | `pattern_event_incremental ↔ pattern_evidence_certify`、`pattern_win_rate_materialize ← pattern_evidence_certify`：表级互读形成 2-环/3-环，`_prune_to_acyclic` 逐边试加即弃 |

- **结论（表述按 #325）**：本轮"该工具检出 21 个任务的 high 建议、实际写入 16 任务/20 边，且已证明二次 `--apply` 零写入"；
  **不得表述为"依赖已补齐"**——225 个无依赖任务里 217 个是**册内无对端**，靠这台推导器永远推不出来。
  要把 A 桶压下去，缺的是"消费方任务在册"这一前置条件（例：把 strategy 层读数改成在册任务，或给表加在册 reader），属**排班编制问题非脚本问题**，交总包编制。

## 3. 本轮证据链（可重跑）

```bash
python scripts/derive_task_dependencies.py --dry-run     # 264/225 快照，只写产物文档
python scripts/derive_task_dependencies.py --apply       # 第一次：tasks_touched 16
python scripts/derive_task_dependencies.py --apply       # 第二次：tasks_touched 0（幂等复证）
git diff HEAD --numstat -- src/zephyr/data/config/tasks.yaml   # 16 16（全是 dependencies 行内改写）
```
单调性判据（本车道实测，非 numstat 肉眼）：任务集与 HEAD 全等、`被删边总数=0`、
"改动行中非 dependencies 行数=0"、每条被改任务的旧 deps 是新 deps 的子集、
旧行内 `# DAG: …` 手写注释由 `DERIVED_TAG` 之后的 tail 保留。

## 4. 生成器自身的两处账实不符（本轮实跑复现，未擅自改语义）

1. **"已写入"是文件级 substring 判据**：`render_markdown` 用
   `landed = DERIVED_TAG in tasks_yaml.read_text()` 决定文档写"本次 --apply 已写入 tasks.yaml"——
   只要文件里**曾经**有 tag，哪怕本轮 `tasks_touched=0` 也照样宣称"已写入"。
   本车道**现场复现**：在一份含 tag 的输入上跑 `--apply` → 输出 `tasks_touched: 0`，
   文档仍写"（本次 --apply 已写入 tasks.yaml）"，且逐字节重出 19:31 那份（sha `fb8990d1…`）。
2. **"22/21 条"口径是任务数不是边数**：`len(applied)` 数的是"含 ≥1 条 high 证据的任务"，
   本轮 = 21 任务，实写 = 16 任务 / 20 条边。
   ⇒ 这就是 R-026 第 9 型（标题与代码不符）在本役的实体来源。修法见 `adjudications/req_dag2_01.md` ②（需总包签字，车道不单方面改产数面措辞）。

## 5. 并发危害事件（并入 R-042 未结案卷，本车道只记观测不归因）

- 观测：本会话 21:4x 在 HEAD 基线跑 `--dry-run` 时 tasks.yaml 仍是 264/236 且与 HEAD 全等；
  数分钟后同一路径 `git status` 变 ` M`，工作区字节 = 死信队列快照
  `.runtime/commit_queue/blobs/a11bc4fc…`（`--apply` 于 19:30 的产物，266 任务 / 16 行 DERIVED / 缺 HEAD 的 2 个任务）。
- 危害方向与 R-038/R-042 相反但同源：**未查明主体把过期快照推进了主工作区的 tracked 热配置**。
  若车道当时直接 `git add` 提交，会**净删 HEAD 的 2 个在册任务 + 塞进 4 个外来未落地任务**。
- 本车道处置（全程未用被禁的破坏性 git）：①`cp` 双份归档（`a11bc4fc` 原文 + 现态）；
  ②`git checkout HEAD -- <该单一 tracked 路径>` 复原（手册 §4 热文件配方）；③用推导器在真基线上重放增量。
  可逆性：注入内容仍存于不可变 blob + `.runtime/tmp/st-ff-dag2-20260918/backup/`。
- **未落地的外来任务块不属本车道判断面**：`cftc_positioning_refresh`、`gold_etf_holdings_refresh`、
  `cohort_ledger_daily`、`kline_index_intraday_incremental` 四块只存在于该过期快照内（各 owner 车道自有工作树），
  本批按 HEAD 基线落地 ⇒ 它们**未被删除、也未被本批代表**。

## 5b. 二次同签名事件（本车道落地后 4 分钟内，实测于 commit `7894946ae0` 之后）

- 观测：`scripts/derive_task_dependencies.py` 已在 HEAD（磁盘==HEAD，sha256 `e8f287e9…`），
  但**索引面被写入一笔 `D`（对该文件的暂存删除）**，同时 `dag_dependency_proposals.md` 的索引面被退回
  我提交前的旧内容（`--cached` 面 = +11/−23 对我已落地版）。签名与 R-038 的"tracked/staged 件被无声改写"同类。
- 若不拦：任何后续按现暂存面落地的提交会**把刚进版本保护的推导器再删一次**（回到"生成器不在版本保护"的原点）。
- 处置：`git restore --staged -- <自家 2 路径>`（只动 index，不带 `--source`、不带 `--worktree`，手册 §8 许可形态）
  → 复测五路径三态全等（HEAD==index==worktree）。
- 同窗口内**他人** staged 删除 2 件未触碰、只登记：`tests/backtest/test_rb_stats_validator_teeth.py`、
  `tests/zephyr/data/test_silent_latch_before_delivery.py`（owner 责任制，宪法 §3.4 不代修）。

## 6. 未达成 / 欠账（如实）

1. `schedule.yaml` / `known_data_gaps.yaml` / `data_supply_sentinel.yaml` 在死信快照 q-0001/q-0002 里的
   在途改动**仍未落地**——`schedule.yaml` 本单明令禁写，故只登记（申请书 ①）。
2. depgraph 遗留 `scripts/data/derive_task_dependencies.py`（node 14830699）与
   `scripts/derive_task_dependencies.py`（node 14830701）两枚 `planned` 节点并存；旧路径件已不存在。
   节点注销属注册表净删面（Owner 门位），本车道**未动**。
3. 文件头注 `[M11]` 豁免条款引用的家族先例 `scripts/onboard_source.py` **实测不在 HEAD**
   （`git cat-file -e HEAD:scripts/onboard_source.py` 失败）；另一先例 `batch_creation_tokens.py` 在 HEAD。
   豁免条款成立性不受影响（`m11-perm-manual-legitimate` 只看注释），但引用面需修正。
4. 本推导器**无 pytest 测试件**（自测面=CLI `--dry-run`/`--apply` 幂等 + `TaskQueue.load_yaml` 无环校验）。
   立测试件需另批（`tests/` 双豁免 CREATE-GUARD，但要写断言面），本轮未做。
5. B 桶 8 个"仅 medium"任务未逐条人工判读（45 条 medium 边的取舍交总包/后续波次）。
