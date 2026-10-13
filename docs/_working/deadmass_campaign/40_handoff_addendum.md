---
ttl: task_bound
completes_when: 本册三条裁定处置与两项新证被下一班并入 99_delivery.md（或独立执行完毕）后作废
---
# 死信放量班·裁定补册 40_handoff_addendum（sid=st-deadmass-20261013，2026-10-14 00:5x）

> 为什么另开一册：`docs/_working/deadmass_campaign/99_delivery.md` 已由袋 q-…-0003 落地（00:36:57 `63a1b437ab`），
> 而本班车道的 HEAD 仍停在 `215e2da12b`（该路径在车道基底里不存在）。此时把追加段直接投进袋里，
> 落地仲裁会按"非注册表族件双侧皆改＝整文件三方真冲突"处理并把袋打死——实测两次（q-…-0005 即死于此处）。
> 在册处方是"基底＝dev 现值"，但本班车道基底追不上 dev（215e2da→dev 已 62 个文件前进，
> 且 `tests/gov/governance/rule_bridge/test_commit_belt_daemon.py` 也被他班动过，`merge --ff-only` 两次 abort）。
> ⇒ 改用**纯新增件**承载（新路径两边都不存在＝无三方面），下一班在新鲜车道里把本册三段并回 99_delivery 即可。
> 本册内容全部来自统筹裁定（00:5x）与本班实测，非新规则载体。

## 一、裁定三项处置落卡（0003 版 99_delivery §四 里没有的三条）

1. **转维护七班｜gate_audit 绕闸写侧定位**：存量两段超 `DEFAULT_MAX_BYTES=50MB`（实测 120.3MB／65.3MB）。
   要办的不是删存量，而是**定位没走 `rotate_if_oversized` 入口闸的写入者**——
   总 1,214MB／293 件，>3 天未动的 182 件仅 26MB，大头全在"有写侧不过闸"的热文件里。
   尺入口：`src/zephyr/shared/io/audit_jsonl_writer.py`（`rotate_if_oversized`，其 [CONSUMERS] 行已列五处自带 append 的写侧）。
   存量处置属政策面，不急；本班只报不删。
2. **转下一班｜四件真成果按墓碑制提升，提升之后才拆那 4 个壳**（去处已点名）：
   - `st-gpuux3v-20261013`：`staging/v3_section_03_note11C.md`／`staging/v3_section_13.md`／`staging/handoff_st-gpuux3v-20261013.md`
     → `docs/_working/gpufeed_campaign/`；
   - `st-maint3-20261011`：`archive/plan_20261011T151409Z/`（`plan.yaml`＋`manifest.json`＋`report.json`）→ `docs/_working/`；
   - `st-nightmine2-20261010`：`t1_quarantine_hash_index.json` → 其 campaign 目录；
   - `st-datasop-20260930`／`st-gomap-b-20261006`／`st-mastertc-l5`：`heartbeat.jsonl.takenover-by-*`／`heartbeat.jsonl.resolved-by-p12a`
     三枚取证改名件 → `.runtime/quarantine/` 案卷区。
   其余 11 个留存壳只剩 `keepalive.jsonl`（保活授权审计），可按前任先例 promote 入墓园后直接拆。
   ⚑ 红线：未提升就拆壳＝把第六态藏起来（在册"被清除面≠净收官"）。
3. **转维护七班｜locked 池位**：`git worktree list` 52 条中仅 1 条目录已消失但仍 `locked`
   （`.aidrafts_pool/pool-20260919202729-c433`）。本班不自解他人 locked 池位，交接管/检疫通道查。

## 二、新证一条：投影分叉的**反向**形态（统筹已转维护七班做双向巡检）

`REGISTRY-YAML-PARSE` 判据＝capability 册 `file|token` 复合键集合差（`_head_token_lag_issue`）。
本班两袋（0001/0002）因随陈旧投影被拦——拦得对；但深挖出更深一层：23:5x 时 HEAD 有
`docs/_working/tdm_goal_structure_research_2026_10_13.md|token=…-20261013` 一行，
而**从 PG 重打的投影里没有它** ⇒ 任何诚实 render 都相对当时的 HEAD"少 1 条"、必被该门拦。
即"YAML 有行而 PG 无行"的反向分叉（与"PG 有 YAML 无"的滞后假拦同族互补）。
00:1x 他班一笔 render 落地时把该行从 dev 抹平，并顺带把本班三处登记物化进 dev。
**处方复证＝内容袋不要随投影册**（PG 为真源，投影由登记/落地侧各自追齐）——
本班代码袋 q-…-0006 起零注册表文件即过门。

## 三、跨日首轮自动分诊账（腿①自证"当日不隔夜"已自动化）

00:29 `dead_triage_probe` 跨日首轮：`scanned=1604 triaged=1604`，10-14 分态＝
**C_UNIQUE_WOULD_REGRESS 1,391／A_LANDED 67／B_UNIQUE_REQUEUEABLE 101／D_EVIDENCE_MIXED 43／D_EVIDENCE_LOST 2**；
账本 `.runtime/audit/dead_letter_triage_ledger.jsonl` 累计 3,191 行（10-13＝1,587／10-14＝1,604）。
对照 23:10 独立尺：dead 1,583→1,604＝**＋21 枚新死，gone=0**（两把尺互证）。
⇒ 下一班只消费判定表；放量命令口径见 99_delivery §七。

## 四、本班袋终态（截至 01:0x）

| 袋 | 内容 | 态 |
|---|---|---|
| q-20261013-…-0001 | 代投遗件 4 件（随陈旧投影） | dead，让死（0002 严格超集） |
| q-20261013-…-0002 | 两腿＋代投 7 件（随投影） | dead，让死（0004/0006 超集） |
| q-20261014-…-0003 | 案卷两册 | **done** `63a1b437ab`（00:36:57，`git ls-tree dev` 两件皆在） |
| q-20261014-…-0004 | 代码五件（裸 subprocess） | dead，死于 BARE-SUBPROCESS（门判对） |
| q-20261014-…-0005 | 案卷终版两件 | dead，死于整文件三方冲突（本册即其解法） |
| q-20261014-…-0006 | 代码五件（process_pool 正门版，50 passed＋ruff 净＋裸调用自扫零命中） | 在途 |
| q-20261014-…-0007 | 本册（纯新增件，无三方面） | 本袋 |
