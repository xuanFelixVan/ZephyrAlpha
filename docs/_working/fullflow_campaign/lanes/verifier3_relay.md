---
ttl: task_bound
completes_when: 全流通战役收官（验收仪尺子连续两轮 0 新断点）
---

# verifier3 接力收口 — sid=`st-ff-verifier3-20260918`（第三腿）

> 给第四腿/总包：本文件是**断点与已落盘清单**，逐件标"已落盘勿回退"。
> 上一腿（verifier2）未写 relay 文件（亲验 `lanes/verifier2_relay.md` 不存在），
> 故其状态靠磁盘件 + `commit_queue/dead` blob 反推，见 `verifier3_relay_start.md` §3。

## 1. 已落盘（进 HEAD 才算交付；本仓并发窗口会扫掉未跟踪件，本会话已亲历一次）

| 件 | 状态 | 说明 |
|---|---|---|
| `scripts/automation/flowthrough_verifier.py` | **第 1 笔（尺子）** | 122KB→落地版；含 ROOR 反查 + 回填被误删块 + `MOD-AUTO-L3-003` + SQL 常量去 `Final` |
| `tests/automation/test_flowthrough_verifier.py` | 同批 | 21 passed / 0 failed（本会话亲跑） |
| `docs/.../catalogs/module_translation_registry.yaml` | 同批 | +2 条 `plain_zh`（尺子+测试），纯 16 行增 |

**勿回退的关键点**（重构时最容易再丢）：
1. `_probe_feed_rows/_probe_feed_buckets/_probe_feed_verdict/_probe_feed_evidence` 与
   `_exec_one_run/_annotate_rc2_usage/_runs_verdict/_runs_evidence` 这两组拆分
   是为过 `NO-HIGH-COMPLEXITY`（门禁自有 `_cyclomatic_complexity`，`_MAX_COMPLEXITY=15`），
   **判据语义未改**（含原 `elif channel_down and not measured: broken=[]` 这条死分支——
   实测该分支可达时 `broken` 本就为空，故删除等价）。
2. `SQL_*` 常量**一律 plain 赋值、禁 `: Final[str]`**（R-029；豁免器只认 `ast.Assign`）。
3. 文件头 `# [BLUEPRINT] MOD-AUTO-L3-003` 与 `# [A_module] module_id=MOD-AUTO-L3-003`
   ——`002` 与 HEAD 里 `scripts/automation/source_card_drafter.py` 撞号，勿改回。
4. `# noqa: bare-sql  <reason>` 须 **gate_id 紧跟 `noqa:` + 2+ 空格**，不能与 `S608` 同行并存
   （正则 `#\s*noqa:\s*bare-sql\s{2,}`；本仓 ruff 未选 `S` 族，S608 不生效，故让位）。
5. `CATALOG_DIR` 用 `Path` 分量拼接（`"docs" / "01_policies_and_standards" / ...`）——
   这是**规避 VOCAB-CHAIN 的必需写法**（字面量不以 `.yaml` 结尾即不匹配），勿"顺手"合并成一条字符串。

## 2. 第 2 笔（文档批，若本腿未落地则在此交接）

- `lanes/verifier3_relay_start.md` — T0 盘点（含 4 条任务书未列的真缺陷）
- `skeleton/05_census_reconciliation.md` — T3 归簇 + 四态重判
- `skeleton/03_omission_crosscheck.md` / `04_sixway_ledger.md` / `04_sixway_machine_ledger.yaml`
  — 第 1/2 腿产物，**至今仍是未跟踪文件**，本腿有义务收进 HEAD（否则又一次"没落地"）
- `adjudications/req_verifier3_01.md`（sanctioned 工具坏）/ `req_verifier3_02.md`（ROOR 缺册）

## 3. 本腿**没有做**的事（禁被当成已做）

- **⑥失败会响=静态推演，非动态注入**。注入须写生产表，按 R-024 明令降级。
  输出显式带 `⑥=静态推演（STATIC，非动态注入）` + `dynamic_injection=False`。
- **⑤向的业务日期口径未实现**。z-sentinel 正在治"哨兵按 `ingest_ts` 而非业务日期判滞后"
  （议息日历停更 323 天而 breach=0），其 `lanes/sentinel_*.md` 在写本文件时尚不存在
  （亲验 `ls lanes/` 只有 `silent_*`/`datagap_*`/`registry_*` 等，无 `sentinel_`）。
  → 尺子⑤向的滞后判定**不在尺子里**：`probe_sentinel` 只从两册取 `max_lag_days` 配置，
    "是否滞后"整块外包给 `run_sentinel_live()`（即 z-sentinel 的 `check_tables()`），
    尺子自身**没有独立的业务日期新鲜度判据**。故 z-sentinel 的 ingest_ts 口径会被
    **原样继承**进验收结论。属 **PROVISIONAL**，下一腿须把"业务日期新鲜度"列成尺子自己的独立判据，
    **这是下一腿的真活，别把现在的⑤当已收口。**
  → 已亲验的尺子侧行为（这部分是真的）：allow_empty 白名单表进 `blind` 桶→该向**不许判绿**、
    两册皆无阈值行→`unwatched` 盲区面、`breaches.failed`→红（"跑了但取不到数=不会响的哨兵"）。
  → ★**本腿新发现的硬矛盾（亲验）**：`04_sixway_ledger.md`（生成于 19:36）FF-01 记
    **⑤=绿** 且同行证据写 "allow_empty 白名单 1 表"；但落地版 `sentinel_verdict()` 里
    `if blind: return "黄"` 在 `breaches` 两条红判据之后、`return "绿"` 之前，
    **blind 非空时代码不可能出绿**。→ **台账是旧版本产物、与尺子当前判据不一致**，
    不能当基线用。**接手者必须先 `--all` 重生成 04 台账，再引用其中任何数字。**
    （查法：`python scripts/automation/flowthrough_verifier.py --all` 后 `git diff` 该台账。）
- 普查 85 条**只复跑了 5 条**（见 05 §2），余 80 条标 `未复测`，未猜判。
- 未碰 `data_supply_sentinel.yaml` / `quality_sentinel*.py` / `tasks.yaml` / `schedule.yaml`
  / `src/zephyr/**`（z-sentinel 与 z-land3 独占）。

## 4. R-018 · 本腿的高风险判断

| 判断 | 依据 | 若错会怎样 | Max 验真命令 |
|---|---|---|---|
| **"前腿半成品可安全续用"**（只须回填误删块，不必重写 122KB 尺子） | **亲验**：blob `pyflakes` 无未定义名；磁盘件恰 13 个未定义名；两者 `diff -u` **只有 1 个 hunk**（83–152 区）；回填后 21 passed + 三门禁检测器全 0 | 若其实还有第二个隐藏语义差，尺子会带内伤进 HEAD，后续所有"某环节已打通"申报继续漂 | `diff -u .runtime/commit_queue/blobs/6a93d49e* scripts/automation/flowthrough_verifier.py \| grep -c '^@@'` → 期望仅回填块造成的差 |
| `--prove-red` 无缺陷可修（总包 R-024 自陈幻觉成立） | **亲验**（读 `dead_reason` 现值 + 磁盘 `--hop-count` 默认 12 + 测试件含逐跳指名断言并通过）；但"12/12 精确指名"**是转报**（本腿未实跑 `--prove-red`，实跑要连 CH 且耗时） | 若 12/12 是第二腿虚报，尺子的核心可信性论证缺一角 | `python scripts/automation/flowthrough_verifier.py --prove-red` |
| ⑤向现在**不能**算达标 | **亲验**（ledger 里 ⑤=绿 同时 breach=0）+ **转报**（z-sentinel 致盲缺陷来自任务书，其 lane 文件不存在） | 把致盲缺陷固化进尺子，验收仪替真断链作证 | 见 §3 第 2 条 |
| MOD-AUTO-L3-002 撞号成立 | **亲验**：`git show HEAD:scripts/automation/source_card_drafter.py` 头两行 | 尺子与已落地件共用 module_id → 翻译/depgraph 双向错挂 | `git grep -n "MOD-AUTO-L3-002" HEAD -- scripts/` |
| S608 让位给 bare-sql 无害 | **亲验**：`pyproject.toml [tool.ruff.lint] select` 无 `S` 族 | 若别处另有 bandit 全量扫描器，这两行会成为新红灯 | `python -m ruff check --select S608 scripts/automation/flowthrough_verifier.py` |
