---
ttl: task_bound
completes_when: F2 血肉批完成（blood_stage=f2_done+validator errors=0/warns=0+覆盖账本三红对账报告落盘）后本件退役为施工留档
title: 图12 F2 血肉批施工模板（chief 手术批下发；前置闸文件——本文件存在即手术完成信号）
owner: st-vm12surg-20261003（手术批）→ st-vm12f2-20261003（执行批）
date: "2026-10-03"
status_note: 本模板由中段手术批（schema 0.3+gate 补件+挂轴）下发；F2 批按此逐节执行，勿自行发挥字段形态
---

# F2 血肉批施工模板（图12 四字段填充+翻闸+对账）

## §0 前置检查（缺一即停）

1. `config/data_supply_chain_map.yaml` 图头 `schema_version: '0.3'` 且 `blood_stage: f1_pending`（手术批已落）。
2. `python scripts/governance/d5_architecture/validators/validate_data_supply_chain_map.py` → exit 0（errors=0；warns=200 属预期=43 节点血肉未满）。
3. **Owner 终审回执**：§1 图例标签 9 条已经 Owner 批准冻结（未批=只填 casebooks/trigger_facts/consumers 三字段，purpose_tag 与翻闸等 Owner 批后做）。

## §1 图例标签冻结入图头（Owner 终审后第一步）

图头 `purpose_tags` 列表（现空 `[]`）写入以下 9 条（**逐字使用，禁增删改名**——SOP §2 冻结流程；每条三键 `id/label/plain_zh`，`pre_mount/confidence` 是候选表过程字段不进图头）：

```yaml
purpose_tags:
- id: fresh_check
  label: 数据还新鲜吗
  plain_zh: 每张业务表都有"最后一天"——这族机制天天核对它停没停在昨天，停了就报警。
- id: break_detect
  label: 坏了谁发现
  plain_zh: 数据断了、缺了、烂了，得有东西第一时间喊出来，不能等下游用的时候才炸。
- id: break_repair
  label: 坏了谁修回
  plain_zh: 发现问题只是第一步——这族机制负责把缺的补回来、把坏的修回去。
- id: can_rollback
  label: 坏了能不能回滚
  plain_zh: 删错表、写坏库的时候，冷库和备份是唯一能让你说"还好有备份"的东西。
- id: schedule_complete
  label: 该来的数据来了没
  plain_zh: 每天该跑的任务都跑了吗——拿"应跑清单"对"打卡记录"，漏一个都能数出来。
- id: lineage
  label: 东西从哪来的
  plain_zh: 每行数据都能说清来自哪家源、走哪条通道——源出问题知道找谁。
- id: source_fallback
  label: 源不可靠怎么办
  plain_zh: 外部源说断就断——备胎源、熔断器、先落盘再入库，都是为了断供当天数据不断。
- id: no_double_write
  label: 别把同一行写两遍
  plain_zh: 重跑不可怕，可怕的是重跑把数据翻倍——幂等加判重，保证跑十遍还是一份。
- id: ledger_readable
  label: 账本要能翻
  plain_zh: 每笔采集、每次失败都留底账——出了事能翻账，没出事能对账。
```

（候选表 `f1d_purpose_tags.yaml` 第 10 条 schema_shape 已随 E-5 裁定出域——DDL 族判架构域不设格，标签无落点退出候选。）

## §2 节点四字段形态（43 节点逐个填，语义层 existing-wins 手改）

每节点在 `config/data_supply_chain_map.yaml` 语义层加四字段（改前 `lock_files.py acquire`，改后生成器重跑校验保真）。**gap 节点（15 个）四字段合法且 module_id 保持 null**；**非 gap 节点（28 个）purpose_tag 必填**；production 节点（10 个）trigger_facts 必非空。形态：

```yaml
  purpose_tag: fresh_check            # 单值，必在图头 purpose_tags 枚举内；一岗多流程同机制多挂时贴主导目的
  casebooks:                           # 列表，册籍标识符（有登记身份的病历本；个案不挂——SOP §3 规3）
  - data/failures 案卷库               # 命名段待上户口批授 CASEBOOK-* 册号后改挂册号
  - integrator_progress.db task_runs
  trigger_facts:                       # dict：L1 汇总位三必键（as_of/evidence/期望与计数）；明细归 L2 freshness_evidence 禁重复
    as_of: '2026-10-03'
    evidence: 'machine.tasks_yaml 271 任务执行留痕；F1 表C 双时点口径'
    expected_runs_window: 7            # 节拍归一（SOP v1.1.0 补丁1）：观测窗内期望次数=窗长÷节拍，禁只报裸计数
    observed_runs: 6
    zero_trigger_verdict: alive        # alive/dead/insufficient_window——期望≤1 且计数缺席=insufficient_window 禁判死
  consumers:                           # 列表，引用面（F1 表C 174 点/40 表归节点版）
  - zephyr.data.scheduler
  - 因子族（经 DSC-HA 出图）
```

数据源三表（`docs/_working/vmap12_flesh/`）：表A `f1a_mechanism_mounts.yaml`（32 挂载候选+18 节点判定+7 不挂清单）→ purpose_tag/casebooks 落格；表B `f1b_casebooks.yaml`（11 本判定：合格 4 挂/停更 3 标 orphan/不合格 4 不挂）→ casebooks；表C `f1c_facts.yaml`（43 节点双时点口径）→ trigger_facts/consumers。

## §3 翻闸与全链验证（填完后）

1. 图头 `blood_stage: f1_pending` → `f2_done`（唯一一次翻转；此后 validator 对缺键转 error 硬拦）。
2. `python scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py --as-of <当日>` 重跑（语义层四字段 existing-wins 保留；counts 四覆盖键应=非 gap 节点数）。
3. validator 全绿：`errors=0` 且 `warns=0`（f2_done 后 warn 项已转 error 或消除；残余 warn=血肉漏填，回去补）。
4. 对抗测试重跑：`python -m pytest tests/governance/commit_gates/test_data_supply_chain_map_gate.py -q` 全绿。
5. gate 实弹：构造触及 `config/data_supply_chain_map.yaml` 的提交走正门，确认 DATA-SUPPLY-CHAIN-MAP 子检查在 MAP-ALIGNMENT 里转绿放行。

## §4 覆盖账本三红对账（SOP §5 步6，机生报告）

产出 `docs/_working/vmap12_flesh/f2z_coverage_report.yaml`，三红口径：

| 红 | 判据 | 数据源 |
|---|---|---|
| 孤儿 | 该挂没挂：表A 32 候选中高置信者未出现在任何节点挂载面 | 表A × 图 yaml |
| 抄写 | 复制非引用：节点四字段里出现真源条目正文（非标识符/指针） | 图 yaml 语义层 |
| 未挂病历 | 表B 合格 4 本未挂 ≥1 环节；停更 3 本须以 orphan 注记挂载 | 表B × casebooks |

报告尾附：四字段覆盖计数（须=counts 四键值）+production 节点 trigger_facts 零缺口声明+三红计数（目标 0/0/0；非 0 逐条列处置）。

## §5 提交

`python scripts/git_commit.py --session st-vm12f2-20261003 --files <图yaml+报告+escalations> --enqueue`；commit 后 `git log -1 --name-only` 核实归属；escalations（需裁定/需 Owner 的发现）写 `f2z_escalations.md` 留 chief。

## §6 红线

- 只动图 yaml 语义层+自家 vmap12_flesh/ 目录；机生层（machine/counts）禁手改（重跑生成器刷新）。
- E-3（sla_tracker 死环二选一）/E-6（data/failures 上户口）/E-8（断供台账三选一）呈 Owner 未决前：casebooks 挂现状描述性标识（如 `data/sla（停更38天，E-3 呈批中）`），禁自行退役/建册/删册。
- tasks.yaml 重复 id（E-4）域内未修前，trigger_facts 计数照机生层 271/270 口径转录并注明 duplicate 口径。
