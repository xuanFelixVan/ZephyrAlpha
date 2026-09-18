---
ttl: task_bound
completes_when: F5 dc-preflight 设计已落地并复核
rule_form: data
verifiability: machine
title: F5 作业簿——DIRECTORY-CONTRACT 摩擦前置化（DC 入预检白名单+建议合规目录，语义零改）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: code_core_landed_workbook_deferred_on_token
---

# F5 作业簿 — DIRECTORY-CONTRACT 摩擦前置化（判据书 F5 / A2 堵点本 16 次阻断）

> **一句话结论**：把 `DIRECTORY-CONTRACT` 加入 `PREFLIGHT_GATES` 锁外快败白名单，并在
> `_ESCAPE_HINTS` 给「建议合规目录」指引——**门禁语义零改**（锁内 DC(priority=30) 仍
> fail-closed 权威执行，预检只把确定性违规从「烧完整门禁链 41.6s 后阻断」前移到「锁外
> 3-5s 快败+精确指引」）。实测主簇=**DCR-005 扩展名违规**（.py/.json 误放 `docs/_working/`，
> allowed=`.csv/.html/.md/.yaml`）：A2 堵点本 16 次 + 本账 58 次 DCR-005。9 测全绿。
> **`docs/_working/` allowed 净增 `.json`=Owner 门位，只出裁定书提案不自签**（见 §4）。

## 0. 病灶（第一性原理）

`DIRECTORY-CONTRACT`（DCR-001~007，真源 `directory_contract.yaml`，checker
`scripts/governance/d1_structure/check_directory_contract.py`，fail-closed，priority=30）
是提交链最基础的目录归属校验。病根：AI 把临时产物（.py 脚本、.json 证据/报告）误放进
`docs/_working/`（该目录 allowed 扩展名仅 `.csv/.html/.md/.yaml`），DCR-005 在**锁内门禁链**
阻断——此时已烧完 claim/锁等待/前序门禁（gate-chain P50 41.6s），AI 才拿到「扩展名不在
allowed 清单」的报错，且报错**不告诉它该放哪**，于是盲改一轮再烧一轮全链（重试环）。

F5 治本=**摩擦前置化**（不改判据、不改语义）：
1. DC 进 `PREFLIGHT_GATES`——锁外预检阶段（`run_preflight`，零锁、零写副作用）就跑 DC，
   违规 1 秒快败，不必进锁烧完整链。
2. `_ESCAPE_HINTS["DIRECTORY-CONTRACT"]` 给**建议合规目录**（.py→scripts/src、.json→转
   .yaml/.csv 或挪 .runtime/data、余查 directory_contract.yaml），把「报错」升级成「报错+怎么修」。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|---|---|---|
| ①上游 | 谁触发 DC 阻断 | `GitCommitGateway` 锁内门禁链 `check_all` 跑到 `DIRECTORY-CONTRACT`(30)；checker subprocess 调 `check_directory_contract.py` 读 `directory_contract.yaml` 真源，对本次 commit 的 files 清单校验 doc_type 归属(DCR-001)+扩展名白/黑名单(DCR-005/006)+根目录白名单(DCR-007) |
| ②下游 | 谁消费预检 | `scripts/git_commit.py` 直连路径在拿锁前调 `run_preflight`；违规→`CommitPreflightResult.blocking=True`+一过式 findings（含 escape_hint）→AI 锁外即见「哪违规+该放哪」，不进锁 |
| ③算法机制 | 白名单准入判据 | `PREFLIGHT_GATES` 准入=**gate 输入面仅 (files 清单 ∪ 磁盘内容 ∪ 会话态 ∪ 注册表)，禁依赖共享暂存区**（防外来 WIP 假阳性，MODIFY-GUARD 逐 gate 审计）。DC 输入面=files 清单 ∪ 各 file 磁盘 doc_type/扩展名；内联模式 ≤500 文件**只检本次 files**、零 `git diff --cached`；>500 退 `--all-files`=与锁内权威链同行为（非新增假阳性面）→ **PASS 准入** |
| ④后端 | 无 DB 写 | 预检零写副作用（审计 jsonl 除外）；DC checker 纯读 yaml+磁盘，零 DB |
| ⑤前端 | 无 | 纯提交链后端 |
| ⑥数据字段 | 计数口径 | DCR-005 detail=「扩展名 {ext} 不在 {path} 的 allowed 清单 {sorted(allowed)} 内」；`docs/_working/` allowed=`['.csv','.html','.md','.yaml']`（DCR-001 豁免区但 DCR-005 扩展名仍生效）；`_MAX_INLINE_FILES=500`（超则 `--all-files`，防 WinError 206） |

## 2. 治本设计（免签代码核，语义零改）

### 2.1 改动面（仅 `commit_preflight.py` 一个文件，三处）

| 处 | 改动 | 语义影响 |
|---|---|---|
| `PREFLIGHT_GATES` | 加入 `"DIRECTORY-CONTRACT"` + 输入面审计注释（PASS 判据） | 无——白名单只决定「预检阶段跑哪些 gate」，锁内权威链照跑全部 |
| `_ESCAPE_HINTS` | 加 `"DIRECTORY-CONTRACT"` → 建议合规目录三类指引 + Owner 门位注 | 无——escape_hint 是 finding 的附助提示，不改 gate passed/detail |
| 模块 docstring | 白名单准入判据段补「files 驱动 + 磁盘内容：DIRECTORY-CONTRACT」 | 无——文档 |

**关键不变量**：预检=提前失败不是豁免（INVARIANTS）。锁内 `DIRECTORY-CONTRACT`(30) 仍
fail-closed 权威执行；预检命中只是让 AI 早 38s 拿到同样的结论+更好的指引。预检 gate 抛异常
→ degraded 放行（fail-open 于设施故障），锁内链兜底。

### 2.2 判据对照

| 判据（Owner 夜令 F5） | 状态 | 证据 |
|---|---|---|
| 不改语义 | ✅ | 锁内 DC(30) fail-closed 权威不动；预检只前移快败；改动仅白名单+提示+docstring |
| 预检加 DC 扩展名白名单预判 | ✅ | `PREFLIGHT_GATES` 含 DIRECTORY-CONTRACT，`run_preflight` 跑同 spec.check |
| 违规输出建议合规目录 | ✅ | `_ESCAPE_HINTS["DIRECTORY-CONTRACT"]` 三类去向；随 `PreflightFinding.render()` 的「逃生通道」输出 |
| 预检提醒命中率 >90% | 🔶 待 24h 观测 | 主簇 DCR-005(.py/.json 误放 docs/_working/) 占 DC 阻断绝大多数（本账 58/总 DC 阻断），预检覆盖该全簇→命中率结构上 >90%；精确值需 preflight_events.jsonl 24h 聚合（挂 R 报告轮） |
| 正式 commit DC 拦截 24h<3 | 🔶 待 24h 观测 | 前置化后 AI 锁外即修，进锁的 DC 违规应趋零；需 commit_block_events.jsonl 24h 聚合验证（挂 R 报告轮） |
| 白名单净增=Owner 门位，不自签 | ✅ 遵守 | `docs/_working/` allowed 净增 `.json` 仅出 §4 裁定书提案，未改 directory_contract.yaml |

### 2.3 测试（9 测全绿，逐文件跑）

`tests/governance/rule_bridge/test_commit_preflight.py` 新增
`test_directory_contract_preflight_whitelisted_with_guidance`：
- (a) `"DIRECTORY-CONTRACT" in PREFLIGHT_GATES`
- (b) `_ESCAPE_HINTS["DIRECTORY-CONTRACT"]` 含 scripts/src、.yaml/.csv、directory_contract.yaml、Owner 门位注
- (c) DC `_FakeSpec(passed=False)` → `result.blocking` + finding 渲染含「scripts/」「逃生通道」

```
PYTHONPATH=src python -m pytest tests/governance/rule_bridge/test_commit_preflight.py -q
→ 9 passed in 0.97s（8 原有 + 1 新增 DC）
```

## 3. 挖后自审闸（三态裁定）

| 闸 | 三态 | 裁定 |
|---|---|---|
| 量尺=终局全貌？ | 施工/降级/否决 | **施工**——DC 是提交链最基础门禁，前置化直接砍重试环墙钟（58 次 DCR-005 × 每轮 ~41.6s 盲修=夜间并发放大） |
| 是否改门禁语义/判据？ | 是/否 | **否**——锁内 DC(30) fail-closed 权威不动；预检白名单+提示+docstring 三处均非语义面（夜令禁动门禁语义判据=遵守） |
| 是否触 Owner 门位？ | 是/否 | **是（部分）**——`docs/_working/` allowed 净增 `.json`=白名单净增=Owner 门位，**只出 §4 提案不自签**；免签代码核（前置化）已落地 |

## 4. Owner 裁定项（裁定书提案，勿自签）

### 提案 S18-F5-①：`docs/_working/` allowed 扩展名净增 `.json`

- **病灶**：`docs/_working/` 是 DCR-001 豁免区（自由工作区），但 DCR-005 扩展名白名单仅
  `.csv/.html/.md/.yaml`。AI 产出的**机器证据/报告**（如 `qmt-smoke-result.json`、
  `pipeline-research/reports/intake-*.json`）天然是 `.json`，误放 `docs/_working/` 即 DCR-005
  阻断（本账 46+ 次 .json 类）。
- **两难**：
  - 净增 `.json` 到 `docs/_working/` allowed → 消除该簇摩擦，但 `.json` 是结构化数据格式，
    放工作区易与「第二配置真源」混淆（CREATE-GUARD .yaml token 扩展的同源顾虑）。
  - 不净增 → AI 须把 .json 证据转 `.yaml`/`.csv` 或挪 `.runtime/`、`data/`（预检 escape_hint
    已给此指引，摩擦由「盲改重试环」降为「一次明确改向」）。
- **AI 建议（供 Owner 裁，不自签）**：**倾向不净增**，理由——`.json` 证据/报告的合规归宿是
  `.runtime/`（临时）或 `data/`（持久），`docs/_working/` 应只放人读文档（.md/.html）与
  表格（.csv/.yaml）；F5 预检 escape_hint 已把「.json→转 .yaml/.csv 或挪 .runtime/data」
  前置提醒，摩擦已从「烧全链盲修」降到「锁外一次改向」，**无需动白名单即达 F5 判据**。
  若 Owner 认为 .json 工作区证据是高频刚需，再净增（属 `directory_contract.yaml` 真源改动，
  须走 RULE-SSOT YAML→DB 同步 + RULING 登记）。
- **门位依据**：夜令「白名单净增=Owner 门位，只出裁定书提案不自签」；AGENTS §5 high 域门位。

### 裁定登记待办（Owner 签后）

若 Owner 裁定净增：① 改 `directory_contract.yaml` 的 `docs/_working/` allowed 加 `.json`；
② `ruling_registry.yaml` 登记裁定#NNN（同 commit 原子，RULE-RULING）；③ YAML→DB 同步
（RULE-SSOT）；④ 回填本簿 §2.2 判据表 + master ledger B-F5。**AI 未签，等 Owner。**

## 5. 施工日志

| 批次 | 日期 | 动作 | commit | 备注 |
|---|---|---|---|---|
| F5-1 | 2026-09-18 | 挖矿：`f5_dc.py` 聚合 DC 阻断本，定位主簇 DCR-005(.py/.json 误放 docs/_working/) | —（挖矿） | A2 16 次 + 本账 58 次 DCR-005 |
| F5-2 | 2026-09-18 | 免签代码核：DC 入 `PREFLIGHT_GATES` + `_ESCAPE_HINTS` 建议合规目录 + docstring；新增 DC 预检测；9 测全绿 | （代码笔待回填） | 语义零改；claim st-flashspeed-20260918 |
| F5-3 | 2026-09-18 | 工作簿（本件）+ Owner 裁定书提案 S18-F5-①（不自签） | —（新件待 token） | 热注册表 token 外来 st-cohort-ledger 在途，待清后补登记 creation_token 再提交本 .md |

## 6. 残余与交接

- **工作簿提交延后**：本 `DESIGN.md` 是新 .md 件，CREATE-GUARD 需 `creation_token`
  （对照 F1/F4 工作簿已在 registry L32398-32409 登记）。当前 `capability_canonical_file_registry.yaml`
  工作树有**外来在途 token**（st-cohort-ledger 的 `cohort_daily_ledger.py`，未提交），
  此时改注册表会夹带外来 WIP / CAS 冲突。**遵守 §3.1 不代修他会话在途**，本簿写盘留存，
  待外来 staged 清后补登记 F3/F5/F6 三簿 token 一并提交（同 F9 DESIGN.md 延后模式）。
- **代码核已可独立提交**：`commit_preflight.py`（existing 改动，无需 token）+
  `test_commit_preflight.py`（tests/ 豁免）+ `00_master_ledger.md`（existing，已有 token）
  = 本批 F5 代码笔，与工作簿提交解耦。
- **判据 24h 观测**（命中率>90% / 拦截<3）挂 R 最终报告轮聚合 preflight_events.jsonl +
  commit_block_events.jsonl。
