---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: SOP-D 回测档案管理规范——run 目录·编号·结构·自动落盘·复现演练（图书馆规则）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-11
topic: backtest_system_sop
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-TRADING-DECISION-MAP-001"
---

# SOP-D 回测档案管理规范（图书馆规则）

> **定位**：回答"回测的文件夹建在哪、编号怎么编、里面放什么、谁负责放、放错了怎么办、怎么验证没放错"。目标是**任何 AI 在任何会话里产生的回测数据都自动按同一规范归位**——像图书馆：书在固定的架位、每本有唯一的索书号、书一旦上架只增不改。
> **裁定来源**：`docs/_working/2026-09-11-backtest-evidence-log-discussion.md` §八（Owner 2026-09-11：R1-R5 全认，R5 复现演练提前）。
> **总纲**：[README.md](README.md)。

## 1. 图书馆三原则（不可妥协）

1. **一书一位**：每类数据有且只有一个合法落点（§2 位置地图），落点之外一律违规；
2. **一书一号**：每个 run 有唯一 ID（§3 编号），台账行、run 目录、引擎产物三方靠 ID 互查；
3. **只增不改**：run 目录落成后禁修改历史文件——发现错误追加 `errata.md` 声明，禁止原地改写（与台账"只追加不删改"同构）。

## 2. 位置地图（全项目回测数据落点总表）

| 数据 | 唯一落点 | 入 git？ | 说明 |
|---|---|---|---|
| 引擎回测产物（净值/交易流水等） | `data/backtest_artifacts/bt-<variant>-<hash8>.json`（平铺，既有惯例） | ❌（2026-09-02 已裁定 gitignore，可重跑再生产物） | 引擎自动写，零迁移 |
| **run 过程档案（本规范主体）** | `data/backtest_artifacts/runs/<run_id>/` | ❌（同上区） | SOP-B 七步产物+判定书 |
| 回测对象注册表（验收阈值预注册） | `docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml` | ✅ **必须入库** | 预注册=可审计真源，放登记表区（与 validation_method_registry.yaml 同区），禁放 data/ |
| 节点验证台账（结论行） | ClickHouse `c1_backtest.node_verdict` | ❌（DB，已有备份体系） | DDL 真源 schemas/categories/backtest/backtest_node_verdict.py |
| 策略快筛台账 | ClickHouse `c1_backtest.strategy_screen`（待建，R3） | ❌（同上） | DDL-as-Code 同模式 |
| 策略级回测证据 | PG decisiongraph `decision_nodes` L5（evidence_hash） | ❌（DB） | MOD-BT-001 既有 |
| 数据本体（行情/财报等） | 各 DS 条目登记的落点（data_asset_registry） | — | **run 目录内禁存数据本体**（§9.1） |
| 一次性分析脚本与产物 | `tmp/`（退役区）/ `docs/_working/analysis/`（gitignore） | ❌ | 禁混入 run 目录 |

**入库边界的判断句**：**"改了会影响结论可信度的"进 git（登记表/阈值/方法学）；"重跑能再生的"不进 git（产物/档案）**——结论的可靠性由"台账行（DB）+ git 快照号（代码/参数/地图版本）+ data_manifest（数据指纹）"三者共同保证，不靠把档案塞进 git。

## 3. 编号规范（索书号）

| 对象 | 前缀 | 格式 | 例 |
|---|---|---|---|
| 回测对象（backlog 条目） | `BT-` | `BT-<批次>-<序号>` | BT-P0-001 |
| 节点验证 run | `VAL-` | `VAL-<batch>-<YYYYMMDD-HHMMSS>`，batch∈{L4,XFLOW,…} | VAL-XFLOW-20260911-180000 |
| 引擎回测 run | `bt-` | `bt-[<variant>-]<hash8>.json`，variant∈{tick,fw,scr,abl,…可扩展}，hash8=8 位十六进制（uuid4 截断）——**收编既有三种形态，不改历史** | bt-tick-8db0c7c6.json |
| 策略快筛 run | `SCR-` | `SCR-<YYYYMMDD-HHMMSS>` | SCR-20260912-090000 |
| 消融对照 run | `ABL-` | `ABL-<对象 id>-<序号>` | ABL-BT-P1-003-01 |

铁律：①全局唯一、只增不改；②run_id 一经落盘即冻结——目录名、台账 run_id 字段、meta.json 三处一致；③文件名 ASCII-only（中文进文件内容，不进文件名——跨工具兼容）。

## 4. run 目录结构（书架格局）

```
data/backtest_artifacts/runs/<run_id>/
├── meta.json                # 必选·全部 kind——run 元数据（§5.1）
├── 01_survey.md             # VAL/BACKTEST 必选——SOP-B①候选算法清单（≥3 候选+出处）
├── 02_data_gap.yaml         # VAL/BACKTEST 必选——SOP-B②DATA-GAP 清单
├── 03_data_manifest.yaml    # 必选·全部 kind——实际取数清单（§5.2）
├── 04_wide/                 # 宽回测产物（大文件子目录：原始指标 csv 等）
├── 05_prune_log.yaml        # VAL/BACKTEST 必选——剪枝记录（剪了什么/为什么/剪后表现）
├── 06_narrow/               # 窄回测产物（WFA/OOS 结果、净值序列）
├── 07_iteration_log.yaml    # 有迭代必选——每轮参数 diff+理由+结果（多重检验计数器）
├── 08_replay.md             # 复现演练报告（§8，做了才写）
├── verdict.md               # 必选·终态——归档判定书（§5.4）
├── errata.md                # 只增不改的修正声明（有错才写）
└── assets/                  # 图表（<步骤号>_<名称>.png/html）
```

**kind × 文件矩阵**（未列=不适用可缺省）：

| kind | 01 | 02 | 04 | 05 | 06 | 07 | 说明 |
|---|---|---|---|---|---|---|---|
| VAL（节点验证） | ✅ | ✅ | 可选 | ✅ | ✅ | 有迭代必选 | SOP-B 全流程 |
| BACKTEST（策略回测） | ✅ | ✅ | 可选 | 可选 | ✅ | 有迭代必选 | 单策略深度回测 |
| SCREEN（快筛批测） | — | — | ✅（scoreboard 全量） | — | — | — | SOP-C C4，结果主要进 strategy_screen 表，目录存批配置与汇总 |
| ABLATION（消融对照） | — | — | ✅ | — | — | — | PB-11 反事实对照 |

**极简豁免**：运行中 dry_run / 探索性试跑（未写台账、未出结论）可不建目录；**一旦写台账或出结论，目录必须齐备**——"结论必须能翻到过程"是本规范的底线。

## 5. 文件内容模板

### 5.1 meta.json（书名页）

```json
{
  "run_id": "VAL-XFLOW-20260911-180000",
  "object_id": "BT-P0-002",
  "kind": "VAL",
  "created_at": "2026-09-11T18:00:00+08:00",
  "created_by": "ai-session:sess-45504",
  "snapshot_commit": "9e6fbe9f",
  "map_effective_from": "2026-09-08",
  "window": {"start": "2019-01-01", "end": "2025-09-10"},
  "holdout": {"mode": "anchor", "cutoff": "2026-09-09"},
  "cost_mode": "rough",
  "attempts": 3,
  "steps": {"01": "done", "02": "done", "03": "done", "04": "done",
             "05": "done", "06": "done", "07": "done", "verdict": "done"},
  "verdict_ref": {"table": "c1_backtest.node_verdict", "run_id": "同 run_id"},
  "linked_artifacts": ["../bt-8607ffc2.json"]
}
```

字段铁律：`snapshot_commit` 必填（PB-06）；`attempts` 与 07 文件轮数一致（喂 Deflated Sharpe）；`linked_artifacts` 指向引擎产物（相对路径）。

### 5.2 03_data_manifest.yaml（借书卡——PB-15 砍哈希后的替代）

```yaml
- name: A股日线行情
  source: westock-data kline
  table_or_file: DS-XXX（data_asset_registry 条目 id）
  window: {start: 2019-01-01, end: 2025-09-10}
  pit_note: "全部字段带 valid_since；未使用未来函数"
  proxy: false            # true 时必须降级标注并写明替代关系
- name: 账户费率配置
  source: config/xxx.yaml # 引用不复制（敏感信息禁入 run）
```

### 5.3 07_iteration_log.yaml（调参审判记录）

```yaml
- round: 1
  changed: "MA 窗口 20→30"
  why: "宽测显示 20 日窗口在吸筹段信号过密"
  result: "OOS IC 由 0.03 升 0.05"
  kept: true
```

### 5.4 verdict.md（判定书，固定六段）

```markdown
# 判定书：<run_id>
对象/节点：BT-P0-002 / TDM-E-L3-07-1 ｜ kind=VAL ｜ 窗口=… ｜ 成本口径=…
结论：verdict=<valid|noise|pending> significance=<…> verdict_reason=<枚举>
判定链：代码规则（引 runner 土规/方法学条目，禁手写理由）
关键数字：触发 N 次 / 命中率 X / 分状态表现（六段各一行）
遗留问题：…
台账回执：已写 c1_backtest.node_verdict run_id=<…>
```

## 6. 自动落盘与巡检（让图书馆员是代码，不是自觉）

- **落盘必须是代码**：`src/zephyr/backtest/run_archive.py`（新模块，按 trae_056 建模块流程施工）提供 `create_run() / write_step() / finalize_run() / load_meta()`——AI/runner 只调 API，**禁手 mkdir/手写路径**；目录与文件名由 API 按本规范拼装，从根上杜绝乱放。
- **巡检脚本**：`scripts/backtest/verify_run_archive.py`（治理脚本，可入 batch）检查四类违规：①台账有 run_id 无目录（缺档案）②目录无 meta.json（无主档案）③文件名含非 ASCII（命名违规）④单文件 >50MB 无压缩（超大）——输出清单，不自动修复。
- **登记闭环**：`runs/` 目录按 P0-1 惯例登 data_asset_registry 新 DS 条目；backlog YAML 按 CREATE-GUARD 流程登记。

## 7. 保留、备份、容量

- 只增不删（个人量化容量可控）；无归档压缩策略（后置）；
- 单文件 >50MB：优先只存摘要+全量指针（指向引擎产物或 DB），确需存全量则 gzip；
- 备份依赖既有 MOD-INF-043 restic/CH 备份体系，run 档案不靠 git；
- 敏感信息禁入：凭据永不入（.gitignore 已兜底 config/.env.*，runs 同规）；费率等账户配置**引用不复制**。

## 8. 复现演练（R5 提前执行）

- **触发**：每个批次决策点，从本批 verdict≠pending 的 run 中抽 1 条（Owner 可点名加抽）；
- **步骤**：锁 meta（commit+manifest+参数）→ 干净环境重跑 → diff 四件套（净值序列逐点/交易笔数/核心指标/首尾 5 笔交易）→ 结果写 `08_replay.md`；
- **判定**：一致=演练通过；不一致=立调查（数据回填漂移/代码漂移/隐藏随机性），errata 声明并暂挂该对象结论；
- **频率上限**：每批 1 条起步，成本可控后加密（模拟盘上线前对 P0 对象全量演练一次）。

## 9. 数据落点补遗清单（"还有什么需要规范"——乱放防患）

1. **run 内禁存数据本体**（图书馆最关键一条）：行情/财报等数据在 DS 登记的落点，run 只存清单+口径——否则同一数据被复制 N 份，回填修正后各 run 各说各话；
2. **数据落点总规则**：原始数据→data_asset_registry 登记落点；运行中间缓存→`data/cache/`（gitignore）；一次性脚本与产物→`tmp/` 或 `docs/_working/analysis/`；回测产物→本规范位置地图；
3. **图表命名**：`assets/<步骤号>_<slug>.png`，中文标题进图内不进文件名；
4. **跨 run 引用**：一律相对路径+run_id 双写，禁绝对盘符路径（换机/备份还原即断链）；
5. **时区**：沿用 RULE-SCHEMA-TZ——系统时间戳 UTC，业务窗口 Asia/Shanghai；
6. **并发**：同一 object_id 禁止两个 run 并行写（复用 session 文件锁；HELD-OVERLAP 同语义）；
7. **空跑留痕**：dry_run/失败 run 允许无目录，但失败原因若影响后续判断 → 台账 pending 行 notes 披露（不造假原则延续）。

## 10. 验收清单（AI 每次收尾自检）

- [ ] run 目录在唯一落点，命名符合 §3，文件名全 ASCII；
- [ ] meta.json 七步状态与实际产物一一对应；
- [ ] data_manifest 每项有 DS id/PIT 声明/proxy 标记；
- [ ] verdict.md 六段齐全，verdict_reason 为代码生成枚举；
- [ ] 未存数据本体、未复制费率配置、无绝对路径引用；
- [ ] 台账行/引擎产物/meta.json 三方 run_id 一致；
- [ ] 修正是 errata 追加，未改任何历史文件。
