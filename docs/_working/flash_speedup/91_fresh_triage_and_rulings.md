---
ttl: task_bound
completes_when: F91 新鲜分诊项与裁定已复核销项
rule_form: data
verifiability: manual
title: Flash 提速战役·Fresh 轮全量分诊与裁定交接（堵点本+新堵塞+遗留，逐条定 Simple/Max）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: triage_recorded_no_code_change_on_fresh
---

# Fresh 轮·全量分诊与裁定交接

> **本轮模式约束（Owner 令 2026-09-18）**：模型已切 **Fresh 型**。凡复杂/需判断问题**不直接修**，
> 只「记录+裁定」，留 Owner 切 **Max 型** 后修。简单机械问题可直修。
> **本文=Fresh 轮唯一交付物**：把 F6 堵点本全部病灶 + 本轮新查到的堵塞 + campaign 遗留 P-1~P-7
> 逐条分诊为 `Simple(已修/可修)` 或 `Complex→Max`，每条给足机理/文件:行/设计/风险，使 Max 可冷启动执行。
> **本轮零代码直修**——理由见 §0：全部命中「复杂」判据，且 §1 纠缠脏树使任何主区写都不安全。

## 0. 一句话结论 + 最高优先级警报

- **警报（P0，比任何堵点都优先）**：Owner 前提「其他会话任务都结束了」**与现实不符**——共享工作区
  泡着**多会话未提交的半成品**（含真实业务代码删除 + 46 个核心 src 改动 + 189 件评审 docs + 1 个 stash，
  详见 §1）。**在 §1 的「未提交半成品」被 Max/Owner 明确处置之前，任何主区提交（含本战役 7 件交付件落地）
  都不安全**（会误 sweep 毁活或误 commit 替别人落地半成品重构）。这正是本轮 7 件交付件仍卡住的根因。

## 1. 关键新发现 N-5：多会话纠缠未提交半成品（本轮查到的最大堵塞）

**现场实测（只读，未动）**：

| 面 | 数量 | 内容 | 严重度 |
|---|---|---|---|
| staged 删除（D） | 22 | `schemas/categories/{fundamental,macro,market}/*.py` 18 件 + `src/zephyr/data/implementations/irm_provider.py` + `scripts/ch/{apply_irm_extraction_ddl,irm_extract_batch}.py` + `tests/ex_core/adapters/test_pretrade_risk_gate_sim.py` | **极高**：真实业务代码 |
| 未跟踪新件（??） | 50 | `schemas/categories` 18 + `data/strategy_intake` 12 + `scripts/ch` 4 + src/tests 若干 | 高：疑为上述 D 的**重组新位置** |
| staged 修改（M/MM） | 420+137 | 含 `src/zephyr/{backtest/core,data,ex_core/adapters}` 46 件核心 | **极高**：横跨回测/数据/交易所核心 |
| staged docs | 212 | 其中 `deep_review_full` 189 件（一整个评审战役产出）+ 本战役 6 件 + tdchain 6 件等 | 中：产出未落地 |
| stash | 1 | `WIP on dev`（基线 `aa43e3b530`）——又一坨未提交活 | 中 |
| 进行中 merge/rebase | 0 | 无（可安全判定当前非合并原子中） | — |

**定性**：这是一次做了但**没提交完的「schema 目录重组 + irm 抽取管道重构」**（旧路径 staged 删、新路径 untracked、
src 消费方 staged 改），叠加一个 **deep_review_full 评审战役的 189 件产出未落地** 和 1 个 stash。
多个已关会话把各自的在途活**留成了共享区未提交状态**（HEAD 上虽有它们的收官提交，但这批改动在其之后、未提交）。

**处置分诊 = `Complex→Max + Owner 决策`**（Fresh 绝不擅动，理由：blast radius 覆盖全仓核心代码，误操作不可逆）：

- Max/Owner 须先回答三个问题，再决定动作：
  1. 这 22 删 + 18 新 + 46 src 改 = 一次**有意的重组**吗？若是→须按 rename 语义**整体恢复并原子提交**
     （用 `git add -A schemas/ src/zephyr/...` 让 git 识别 rename，或 `git diff --cached -M` 核对配对），**不可分批**；
  2. `deep_review_full` 189 件 + 那个 stash 是**待落地交付**还是**废弃探索**？
  3. 若均为**废弃**：确认后才可 `git restore --staged . && git clean -fd`（**破坏性，须 Owner 逐面签字**）；
     若**须保留**：分主题各自成批落地或转 worktree 继续。
- **AI 侧安全边界（Max 也须守）**：本发现下任何清理都是 `RULE-GIT-SAFE` 危险操作；每面处置前
  `git diff --cached` 留档到 `.runtime/tmp/`（免疫 clean -fd），保留 24h 可回溯。

### 1.1 N-6：热文件潜伏克隆债（Max 落地 §2.1 时撞出，2026-09-18）

- **现象**：`session_worktree.py` 内 `_session_active_lockfile` / `_heartbeat_pid_file` /
  `_commit_persisted_marker_path`（均路径 getter 一行）与 `_get_manager` / `_get_registry`（均
  lazy-singleton getter）互相似 100%（extract 级 structural）。这些函数自 `c8b9c1ca5a`（P0/P1 治本批）
  即存在于 HEAD，**只因自严格 extract 级 gate 后无人再提交过该文件而从未暴露**。
- **触发**：本战役 §2.1 修复（在 `_wt_block_gate_id` 加 8 行归因分支，未碰上述函数）一旦提交，
  CloneGuard 全文件函数重扫即判 extract 级克隆 → `CAPABILITY-OVERLAP 阻断`（queue drain q-…-0010 死信实证）。
- **定性**：`Complex→Max + 需 Owner 授权`（合理重复走 `resolve_finding` 标 acknowledged，或对 3 对函数做
  合并重构）。**非本战役 §2.1 引入**，是「改任一潜伏债热文件即被连坐」的观测面——与 N-1/N-2 同属
  「共享区无主面治理」病灶族，是**任何**对核心治理文件的提交前置税。
- **落地闸堆（Max 实测，一笔 2 行观察性修复的拦路石全谱）**：
  1. 直连 → BLUEPRINT-FORMAT 对 foreign staged 坏文件 `scripts/backtest/crisis_drill_monthly.py`（own_scope=false）连坐 = **N-1 铁证**；
  2. 队列 → SESSION-REQUIRED（st-flashspeed 心跳过期）+ WORKTREE-REQUIRED（`st-datapack/st-nightcoord/st-deeprev` stale pid=0 逻辑会话）= **N-4 铁证**；
  3. 队列（加两逃生旗后真 drain）→ CAPABILITY-OVERLAP/CloneGuard 对本文件既有克隆 = **N-6**。
- **§2.1 修复就绪态**：代码+测试正确、`test_session_worktree_audit_wrapper 13 全绿 + test_session_worktree 89 全绿零回归`；
  在途编辑已备份 `.runtime/tmp/flash_speedup_workbook_backup/§2.1_gateid_base_conflict.patch`（64 行）；死信原件 q-…-0010 按令留存取证。
- **解闸次序建议**：先 N-5 定性恢复/废弃（清 foreign 317+注册表 MM+stash）→ 令 stale 会话心跳过期或
  `session_worktree_start` 重注册本会话消 N-4 假阳 → 经 Owner 授权 `resolve_finding` ack N-6 三对合理重复 →
  §2.1 走 `--allow-overlap --allow-non-worktree --enqueue` 一次落地。**三步任一缺失，最正确的 2 行修复也落不了地**——
  这正是「24/h 门禁常数」病灶对施工者的真实税单。

## 2. F6 堵点本全量分诊（逐条）

> 判据口径：F6 已定四态归属零无主（3572 行）。下表对**需要动代码的病灶**逐条定 `Simple/Complex`。
> 绝大多数为 Complex（触碰门禁语义/热保护文件/并发时序/Owner 门位），Fresh 轮只记录。

| # | 病灶（行数） | 涉及文件:锚点 | 拟定修复设计 | 风险/门位 | 分诊 |
|---|---|---|---|---|---|
| 2.1 | (b) gate_id 归因缺口 UNKNOWN ×26 | `git_commit_gateway.py` `_audit_commit_block_event` L1638-1641（`_STATUS_GATE_ID` 映射 + `门禁 ([A-Z\-]+) 阻断` 正则） | 扩展 gate_id 判定链覆盖 worktree/landing 路径：新增正则 `pre-commit gate 阻断（worktree 路径）: ([A-Z\-]+):` + `（([A-Z_]+_VIOLATION)）` 映射 + landing 冲突归伪门禁 `WORKTREE-BASE-CONFLICT`；**audit-only 零行为变更** | 触碰热保护文件（§13 safe_write_text）；altdata 并发已撤但 §1 脏树未清；低价值 | **Complex→Max**（且建议纳入 S18-R1 同批，见堵点本 §7#4） |
| 2.2 | R-06 告警自激 ×1095（全场 31% 噪声） | 堵点本记录器 `_check_ledger_backlog`（bottleneck_ledger 写入侧） | 状态跃迁才落盘 + 同状态 30min 冷却窗；消除每 tick 重写 | **Owner 门位**：告警阈值/冷却=噪声降级清单 S18-R1 | **Complex→Max + Owner 签 S18-R1** |
| 2.3 | R-04 claim 生命周期 ×227 + R-02 LOCK_TIMEOUT ×70 | claim 释放路径 / serializer 通道数 | claim 移到提交成功后释放 + TTL 300s；k=4 按域分区通道（F2 前置件已交付） | **Owner 门位**：通道数=Owner 定值（S18-R3）；禁 AI 动 serializer 通道数 | **Complex→Max + Owner 签 S18-R3** |
| 2.4 | R-03 commit_slow ×192（门禁链长尾墙钟=真天花板） | 113 门禁/笔；gate-chain P50 41.6s→近段 29.0s | ①进程级内容哈希 YAML 解析缓存（1.67MB 注册表被 7+ 门禁重复解析）；②门禁退役/降级（§4.2 触发率审计） | **Owner 门位**：门禁退役 AI 禁用；解析缓存挂 harness 门 | **Complex→Max + Owner 签 S18-R3/§4.2** |
| 2.5 | R-12 存量悬空引用 ×62 | 旧宪法 §6.1 换版尾债；全仓 grep 旧章节号 | 存量主动清（门禁已拦新增）；换版改写进同一 commit | 需逐处判断引用是否真悬空=**语义判断** | **Complex→Max**（堵点本 §7#5 标「免签可自裁定」但实为全仓引用改写，Fresh 不碰） |
| 2.6 | R-08 DEPGRAPH 预登记 ×42 + freshness（F4 已治部分） | `apply_depgraph` 登记与 commit 原子化 | 消除「先施工后补登记」窗口：登记入 commit 前置原子步 | 触碰 depgraph 门禁链 | **Complex→Max** |
| 2.7 | R-09 REGISTRY-YAML-PARSE 连锁 ×5 | 共享注册表解析失败隔离 | 解析失败隔离到所属门禁不连坐 + 写后 1min 解析复查 | 触碰多门禁共用解析路径 | **Complex→Max** |
| 2.8 | (c) 使用摩擦 1433 行 → F5 前置化 | `commit_preflight.py` PREFLIGHT_GATES / `_ESCAPE_HINTS` | DC×62 + FOLDER-CAPACITY×45 + WORKTREE×55=162 行前置提醒（F5 已落 1fb04f6e 部分）；余 1271 行治本在报错文案精确化 + 队列同 qid 同原因合并死信 | **禁动门禁语义判据**（指令）；报错文案=判断 | **Complex→Max**（F5 已落代码核，残余文案精修留 Max） |
| 2.9 | (d) 死信残留 ×77 | `.runtime/commit_queue/dead/` | 专人专事：高模型维护班清账（**施工 AI 勿修**，protocol 明文） | 协议明示 Max/维护班 | **Complex→Max** |
| 2.10 | **N-1** BLUEPRINT-FORMAT own_scope=false 外来连坐 | `gate_registry.yaml` BLUEPRINT-FORMAT `own_scope` 字段 vs 宪法 §3.1 | own-scope 化（一个外来占位 .py 不该挡全场直连提交）或登记「全仓扫描」理由（§3.3） | **禁动门禁语义**（AI 未自修，留 Owner/Max） | **Complex→Max + Owner 门位** |
| 2.11 | **N-2** 共享 index 无已落地路径保护 | POST-COMMIT 守护 / bulk-add 前置校验 | 防①刚落地内容被陈旧 bulk-add 回退 ②落地新文件被 staged 成 D（本轮 §1 即其**放大实证**） | 新增守护=门禁/flag 门位（超出战役授权） | **Complex→Max + Owner 门位**（本轮 §1 提供强力证据） |
| 2.12 | **N-3** 预检逃生旗映射漏配 | `scripts/git_commit.py` `_preflight_skip_set` | 加 `allow_overlap → SESSION-REQUIRED` 映射 | 免签（修映射一致性非动语义） | **✅ 已治本 `be934b079d`**（4 测全绿） |
| 2.13 | **N-4** pid=0 心跳 90s 窗口竞态 | SessionRegistry 心跳/预检时序 | 心跳窗口参数化 / 预检前自动续心跳 | 触碰 SessionRegistry 语义（AI 禁自裁）；N-3 已用 allow_overlap 逃生遮蔽 | **Complex→Max** |

> **堵点本分诊结论**：13 条需动代码的病灶，**12 条 Complex→Max、1 条（N-3）本轮已直修**（be934b079d，
> 系免签映射一致性修复，早于本 Fresh 轮完成）。**Fresh 轮无新增可直修简单项**——因每条要么触门禁语义/
> 热保护文件/并发时序，要么属 Owner 门位，全部命中「复杂」判据。

## 3. campaign 遗留 P-1~P-7 现状（总簿 §5，均 Owner 门位/复杂，只重申不擅推）

| # | 事项 | 门位 | 现状 |
|---|---|---|---|
| P-1 | F2 serializer k=4 通道数 | Owner 签 S18-R3 | 前置件全绿（lease 续租/双通道压测/热文件闸/exit-burst），**「k=4 就绪待签」** |
| P-2 | F5 DC 白名单净增 `.json` | Owner 门位 | AI 建议**不净增**（治本在指引非放宽 allowed），待裁 |
| P-3 | S18-R1~R4 四张裁定书 | Owner 签 | 均 status=待 Owner 签，未自签 |
| P-4 | 门禁退役 + 进程级 YAML 解析缓存 | Owner §4.2 | CREATE-GUARD P50 40-41s TOP 阻断候选；提案不自签 |
| P-5 | =N-1 | Owner | 见 §2.10 |
| P-6 | =N-2 | Owner | 见 §2.11（§1 提供放大实证） |
| P-7 | =N-4 | Owner | 见 §2.13 |

## 4. 本会话 7 件交付件落地障碍（含 Owner 必交件②③）

- 在盘未跟踪 + 已备份：`F3/F5/F6/F9/F2_prereq/DESIGN.md` + `90_report.md` + `lane_reports/F6_堵点总账.md`
- **落地障碍**：需 `capability_canonical_file_registry.yaml` 补 7 条 creation_token，但该注册表**当前 MM**
  （外来会话 staged 删了 `altdata-night-01-morning-report` token + worktree 第三变体）→ 覆写毁别人活、
  跟随=搭便车 → **须待 §1 脏树处置后、注册表干净时再落**（队列正门，F9 已修新文件死信，untracked 走队列安全）。
- **交付件本体零损失**：全部在磁盘 + `.runtime/tmp/flash_speedup_workbook_backup/`（9 件，免疫 clean -fd）。
  本分诊文档写完后同样备份到该目录。

## 5. Fresh 轮处置说明（为何零代码直修）

1. 堵点本 13 条 = 12 Complex→Max + 1 已直修（N-3，本轮前完成）——**全部复杂项按令只记录**。
2. §1 纠缠脏树 = 新查到的最大堵塞，破坏性清理须 Owner 逐面签字 → 记录为 N-5 待 Max/Owner。
3. §4 交付件落地因注册表 MM 纠缠而失去「简单」属性 → 记录，不冒险动热文件。
4. 结论：Fresh 轮**正确交付=本分诊文档**，代码直修数=0（唯一 N-3 早已完成），符合「稍微复杂就别直接修」。

## 6. Max/Owner 建议开工次序（切回 Max 后）

1. **先处置 §1（N-5）**：三问回答 → 恢复/落地/废弃决策（含注册表 MM 与那个 stash）→ 清出干净共享区。
2. **再落 §4 本战役 7 件交付件**（注册表干净后，队列正门，补 7 token）。
3. **后推堵点本 Complex 批**：优先级 真 100/h 杠杆 = §2.4 门禁退役/解析缓存 > §2.2 R-06 噪声 >
   §2.10/2.11 N-1/N-2 外来连坐（本轮 §1 强证 N-2 值得做）> §2.1 gate_id > 余下。
4. 每批守：改前 claim、毕后 release；热文件 safe_write_text；门禁语义判据除非 Owner 明确放行不动；
   压测 worker ≤20。
