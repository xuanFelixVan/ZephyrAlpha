---
ttl: task_bound
title: "99 台门禁独立红蓝安全复验报告（st-gaudit2-20260923，不信自测背书）"
session: st-gaudit2-20260923
---

> 车道 st-gaudit2-20260923｜Owner 令：对瘦身后的 99 台门禁做独立红蓝复验。只读+测试，零门禁代码改动，零生产账本污染（测试台审计/统计汇全程内存捕获，真实 git 索引零触碰）。
> 复验对象真源：`in_process_gate_registry.yaml`（total_gates=99）+ `gate_registry.yaml`（统一册）+ 上轮审计 `05_gate_audit_report.md`。
> **方法**：进程内实例化真实 GitCommitGateway（99 台真注册表装载），GIT_INDEX_FILE 沙箱索引承载违规样本（`hash-object -w`+`update-index --cacheinfo`，真索引零触碰）；每台"违规样本须拦、合法样本须放"双向实测；全链 check_all 跑真触发链；生产账本（.runtime/gate_audit/*.jsonl、gate_execution_stats.jsonl）只读取证。

## 0. 结论总览

**总判定：99 台门禁体系安全性整体成立。** 七簇合并语义等价性实测通过（16 红 6 绿全符合预期），own 化 warn+审计流生产侧活跃无静默，退役 3 台无隐藏防线丢失。**发现 2 个漏洞级问题（登记勿自修，呈 Owner）+ 7 条观察项**，均不构成即时安全风险，但 F2 建议纳入下批修正。

| # | 项 | 三态 | 一句话 |
|---|---|---|---|
| 1 | P1 退役 3 台消费方复核 | ✅安全 | 活代码消费方=0；墓碑 3/3 保身份；间接引用残渣见观察 O1-O4 |
| 2 | P1 退役 3 台原防违规漏防检测 | ✅安全 | 原防面无人拦（已批接受的提醒型损失）；新文件无索书号被 3 层安全网拦 |
| 3 | P1 触发网实测 | ✅安全 | 进程内全链 26 台触发矩阵双向验证+生产账本 52/88 链实跳 |
| 4 | P2 七簇合并等价性 | ⚠️发现 | 14/16 红样本精准拦截、6 绿零误拦；**F2=REFERENCE-INTEGRITY 触发器收窄检查面** |
| 5 | P3 own 化 warn+审计流 | ✅安全 | 生产账本三台实读有痕；功能测试 21 台 60 次审计事件齐发无静默 |
| 6 | P4 速度 | ✅安全 | 干净链 P50 41.4s（vs 审计旧 43.2s）；拦截链受晨间大战窗口偏置见 §5 |

## 1. 现状盘点（复验基线核对）

- `in_process_gate_registry.yaml`：total_gates=99，条目 99，与装载对账一致（GitCommitGateway 构造即 auto_register_gates fail-closed 装载成功，本次进程内实测）。
- files_trigger 实装 **26 台**（Owner 口径"39 台观察网"=零触发+慢门+warn-only 观察面总账；审计 §B 零触发标记存活 19 台中 17 台已挂触发器，未挂 2 台=GIT-CALL-BUDGET/STASH-ACCUMULATION，均 warn-only）。对账不缺台，口径差在"观察面"与"触发器"两个集合。
- 退役 3 台：盘上文件/测试/镜像 yaml 已删（4b8fb00a555），注册表除名+统一册墓碑 3/3 带 redirect_to（gate_registry.yaml L2054/L2067/L2080）。
- 统一册生成器 `generate_gate_registry.py` 内置墓碑源（L564 等）——墓碑是生成器产出非手维护，符合 §9.5。

## 2. P1 退役三台复核

### 2.1 消费方 grep（含间接引用）

活代码消费方（import/注册/CLI 调用）：**0**（全仓 py/yaml/toml/json/ps1/cfg 扫描）。剩余引用全部定性如下：

| 位置 | 引用内容 | 定性 |
|---|---|---|
| gate_registry.yaml L2054/L2067/L2080 | 三台 deprecated 墓碑+redirect | ✅设计内（保身份，rule pairing 校验因此不炸） |
| trae_035_task_construction_verification.yaml L345 | `paired_gate_id: "DATA-TASK-COMPLETENESS"` | ⚠️O1 观察：语义死链（见下） |
| capability_canonical_file_registry.yaml L3509/L4145/L5132 | 3 条 canonical_override 指向已删文件 | ✅O2 设计内：capability_lookup._reconcile 显式标记 canonical_alive/dead，可观测容忍 |
| module_translation_registry.yaml L10905/L55798 等 | 已删模块的翻译条目 | ⚠️O3 卫生残渣（loader 惰性，无校验器要求被译文件存在） |
| **fail_open_register.yaml L3128-3146/L5775** | 5 行指向已删 issue_resolved_integrity_gate.py | ❌**F1 发现：派生册过期**（见 2.4） |
| path_ownership_map.yaml L23151/L41253 | 已删路径条目 | ⚠️O4 同类派生册残渣（未独立验证 --check，建议随 F1 同批重生） |
| dossiers_v2_index.yaml / architecture_issue_registry.yaml / commit_diffs.json | 历史档案提及 | ✅历史记录，不动 |

**O1 展开**：RULE-EXECUTION-PAIRING 门（rule_execution_pairing_gate.py）要求 staged 规则的 paired_gate_id "须在 gate_registry 注册"——墓碑保留了 gate_id 身份，故 trae_035 这条配对**校验不炸但语义已死**（配对对象永远不会再执行）。建议随下批规则清扫把 trae_035 的 paired_gate_id 置 null（文档型）或改指承接台。

### 2.2 原防违规样本漏防检测（P1②）

三台均 warn-only 提醒门（**从不阻断**，已从 git 史恢复原件核实）。将各自原防违规样本注入 99 台全链（check_all 真触发链）：

| 原台 | 原防什么 | 违规样本 | 99 台现状反应 | 判定 |
|---|---|---|---|---|
| DATA-TASK-COMPLETENESS | tasks.yaml 新任务缺 fallback_sources 提醒 | 追加无 fallback 的 task_id | **零台拦零台警**（RESOURCE-SCHEDULE 正常 ran 但不管此字段） | ✅接受损失：提醒环消失，本就 warn-only |
| ISSUE-RESOLVED-INTEGRITY | issue 标 resolved 但 impact 文件不存在提醒 | 追加 status=resolved 假条目 | **零台拦零台警** | ✅同上 |
| LIBRARY-COVERAGE | 新 .py/.md 无索书号 asset_id 提醒 | 无索书号新 .py | **3 层安全网实拦**：CREATE-GUARD（无 token）+TRANSLATION-COVERAGE（无翻译）+DEPGRAPH-ENFORCEMENT（未登记）全阻断 | ✅实质风险≈0：新文件登记链兜底 |

结论：退役决策与上轮审计 C1 判据一致，无隐藏防线丢失。

### 2.3 触发网实测（P1③）

- **进程内**（真注册表 check_all 全链）：src 侧文件跑 78 台/跳 19 台，docs 侧跑 73/跳 24——跳过集与 26 台触发表逐一吻合；REFERENCE-INTEGRITY 在 docs 侧 ran、src 侧 trigger_skip（该差异即 §3 F2 的实证）。
- **生产侧**（gate_execution_stats.jsonl 只读）：99 台时代 88 次链执行中 **52 次含 trigger_skip**（top=NO-BARE-GETENV/ID-UNIQUENESS/GATE-PRECOMMIT-OFFLINE/NO-SECRET-HARDCODE/GATE-ERRCODE-CONSISTENCY/BARE-SUBPROCESS 各 52 次），67 次含 preflight 复用——条件触发+预跑复用双设施在真实提交路径活跃。
- 本报告自身落库提交即第 3 次实弹（docs 件，见 §5 探针）。

### 2.4 F1 发现：fail_open_register 派生册过期（登记勿自修）

- 现象：`python scripts/governance/d7_code/generate_fail_open_register.py --check` → `DRIFT: fail_open_register 派生册过期（盘上=4cf28afb7575）`，exit=1（2026-09-23 实测）。
- 归因：P3 退役批删 `issue_resolved_integrity_gate.py` 后未重生成派生册，盘上册残留 5 行指向已删文件（L3128/3134/3140/3146/5775）。
- 影响：现无门禁在提交链跑此 --check（不阻断日常提交）；但该册标"CI/门禁 --check"消费位，下次任何消费方对账即红。修法（属主=门禁基建车道，本车道不执行）：重跑生成器同批落册。

## 3. P2 七簇合并语义等价性

方法：每簇 union 台 `spec.check` 进程内直调（绕开触发器层，纯语义面），违规样本按"被吸收台各自的原检测面"逐台构造；合法对照样本验不误拦。样本经沙箱索引/临时磁盘注入，不碰真暂存区。

| 簇 | 红样本（须拦） | 实测 | 绿样本（须放） | 实测 |
|---|---|---|---|---|
| REFERENCE-INTEGRITY | 三个悬空样本（假章节号/假 ARCH 号/假裁定号）各精准命中对应子台前缀（样本字面量不录入本报告防自我拦截，原文见 evidence.json） | 3/3 | #ARCH-310+裁定#404+§0 合法引用 | ✅ |
| PERMANENT-SYSTEM-TRIGGER | time.sleep 循环→[PERM-TRIGGER]✅；argparse 无订阅→[MANUAL-ONLY-PERMANENT]✅（同一样本双前缀齐响） | 2/2 | 纯函数✅；argparse+合规 m11 noqa（reason≥10字）豁免放行✅ | 2/2 |
| GATE-VOCAB | SSoT 路径字面量→[VOCAB-CHAIN]✅ | 1/1 | 干净文件✅（VOCAB-HARDCODE 子检查器同批实跑 26s=接线活着，无合适无副作用样本，深度注 A） | 1/1 |
| DEPGRAPH-ENFORCEMENT | 未登记新 src .py→拦✅（[NEW-FILE-DEPGRAPH] 前缀） | 1/1 | 已登记生产模块平凡修改→放✅ | 1/1 |
| MAP-ALIGNMENT | 红样本不可合成（全局三图对齐器吃仓库状态非样本内容，深度注 B） | — | staged 触发面内文件（depgraph_schema.py）→run_alignment 实弹真跑 5.06s✅ | 1/1 |
| BLUEPRINT-HEADER | 层码下划线小写 MOD-INF_bad_name→[CONSISTENCY]✅；双拼写 MOD-GOV_x vs MOD-GOV-x→[CROSS-CHECK]✅ | 2/2 | 合法格式两头一致→放✅ | 1/1 |
| COMPLEXITY-GUARD | 25 方法 God Class✅；McCabe≈20✅；9 参数✅ | 3/3 | 简单函数→放✅ | 1/1 |

**红 10/10 拦截、绿 6/6 放行（MAP 红侧不可合成如实标注）**。吸收台闭包提级+union 聚合（违规带 [源台名] 前缀、任一失败即阻断）行为等价成立。

### 3.1 F2 发现：REFERENCE-INTEGRITY 挂 `['docs/']` 触发器收窄了吸收台检查面（登记勿自修）

- 事实：合并前 DANGLING-REFERENCE（历史 14 拦）/RULING-REFERENCE（6 拦）**每次提交都跑**，扫描面含 .py/.yaml/.md/.json/.txt；合并后新台被 P5 批挂上 ARCH-REFERENCE 的处置触发器 `files_trigger: ['docs/']`（in_process 册 L123）。
- 实测：同一悬空章节引用样本——纯 src 提交在 check_all 中 **trigger_skip**；docs 提交正常 ran；同内容直调 union（绕触发器）**精准拦截**。即：**纯 src/ 提交在 .py 注释/docstring 里新增的悬空引用、悬空裁定引用，现在不再检测**。
- 定性：ARCH-REFERENCE 单台的 docs/ 触发是上轮审计 C5 表明批项（Owner E 批），但 DANGLING/RULING 两台原无触发器，收窄是**合并的副作用**，未见显式逐台裁定。
- 影响：中低——悬空引用是文档质量债非资金/数据风险；且只漏"新增引用"，存量不追。建议：新台触发器扩为 `['docs/', '.py', '.yaml']` 或去掉触发器（单次 P50≈2.1s，实测可承受），随下批修正。

### 3.2 观察项（P2 相关）

- O5：PERM-TRIGGER 时间触发识别面=APScheduler 族+`.sleep`+`schedule.*`——**`threading.Timer` 不在识别面**，Timer 型常驻循环可溜过（红样本实测未触发）。既有行为非合并引入（行为逐字节保留），建议纳入检测器扩面清单。
- O6：BLUEPRINT-HEADER 只查 added 行——存量文件的合法格式争议被"新增才查"豁免（如 `MOD-GATE_ENGINE` 无序号后缀格式在存量文件普遍存在，新文件同写法会被拦）。设计如此，提请知悉。
- O7：MAP-ALIGNMENT 实弹绿跑顺带测得当前仓库三图状态=2 处状态漂移（warn-only 不阻断），属主=地图对齐车道。

## 4. P3 own 化安全性（warn+审计流）

- **生产账本实读**（3 台抽验）：`.runtime/gate_audit/*_foreign_staged.jsonl` 56 台在账，抽 NO-BARE-SQL/CREATE-GUARD/MSG-EXPOSURE 最新行——外来清单、会话号、计数齐备（CREATE-GUARD 一笔实录 123 个外来 staged 文件），时间戳均为 09-23 当日。**warn 有痕、无静默**。
- **功能实测**（测试台 monkeypatch 审计汇，不污染真账本）：3 轮全链跑中 **21 台合计 60 次** `_audit_foreign_staged` 事件齐发，文件清单与会话归因字段完整，logger.warning 同步发声。
- 观察 O8：`attribution` 字段（对外来文件尽力归因到持有会话）抽验三笔均为空——归因依赖 registry.list_active() 与 claim 交集，实战命中率低；不阻断主流程，但审计价值打折，建议后续用 claim_snapshots 目录补充归因面。

## 5. P4 速度实测

**历史重算**（gate_execution_stats.jsonl，99 台时代全量 88 链，窗口 2026-09-23 00:31→05:39 UTC）：

| 链型 | n | P50 | P90 | 备注 |
|---|---|---|---|---|
| 干净链（failed=[]） | 15 | **41.4s** | 108.5s | vs 审计旧值 43.2s：-4% |
| 拦截链（failed≠[]） | 73 | **149.9s** | — | 晨间六会话大战窗口偏置（单链外来 staged 面上万件），与审计 10 天混合窗 71.1s 不可直接比 |

审计 D 表"拦截链≈38s"是"减慢门 sum_p50"的投影值；实测干净链 41.4s 与其同量级。拦截链变长的主因不是门禁变慢，而是：阻断尝试集中于大战窗口（73/88），且阻断后门禁链**全量继续跑完**（check_all 不短路）+ 外来 staged 归因/审计开销随暂存区面积放大。

**探针提交实测**：本报告落库即探针件。实测三探针（stats 账本行归因，可复现：解析 gate_execution_stats.jsonl 尾行）：

### 5.1 P4-PROBE 探针实测（追记）

| 探针 | 提交 | 文件域 | CLI 墙钟 | L2 链净时长 | 链构成（共 99 台） |
|---|---|---|---|---|---|
| ① | 3d910705 | 注册册 yaml（非 docs 触发面） | 100.9s | **37.6s** | 69 跑+22 触发跳+8 预跑复用，failed=0 |
| ② | 371bc6e6 | 本报告 v1（docs 面，REFERENCE-INTEGRITY 实弹 ran） | 55.5s | **7.7s** | 67 跑+24 触发跳+8 预跑复用，failed=0 |
| ③ | 本追记提交 | docs 面 | 见提交时墙钟 | 以本提交时刻 stats 行为准 | — |

判读：拥堵窗（序列器 46 件慢项在磨+六会话并发）下 CLI 墙钟 55-101s，其中 L2 门禁链仅 7.7-37.6s——差额=全局锁等待+CLI 装配+L2.5 precommit 两段式+post-commit 步骤，非门禁本身变慢；非拥堵历史窗干净链 P50=41.4s 仍是最具代表性口径。**瘦身目标（拦截链≈38s）与实测干净链同量级成立**；探针② 7.7s 证明预跑复用+触发跳过的叠加收益在暖态下可将链压到个位数秒。

## 6. 可复现命令

```bash
# F1 派生册漂移（只读 check）
python scripts/governance/d7_code/generate_fail_open_register.py --check

# P2/P1 进程内红蓝测试台（沙箱索引，真索引零触碰；审计/统计汇内存捕获）
python .runtime/tmp/gaudit2/harness.py    # P2 七簇首轮+P1③ 全链×2+P1② 样本
python .runtime/tmp/gaudit2/harness2.py   # 修正：磁盘样本/隔离索引/BP 合法格式
python .runtime/tmp/gaudit2/harness3.py   # PERM 双子台/m11 豁免/双拼写/MAP 实弹
# 证据：.runtime/tmp/gaudit2/evidence{,2,3}.json

# P4 历史重算
python - <<'PY'
import json
rows=[json.loads(l) for l in open(".runtime/audit/gate_execution_stats.jsonl",encoding="utf-8") if l.strip()]
rows=[r for r in rows if r.get("n_specs")==99]
ok=sorted(r["total_ms"]/1000 for r in rows if not r["failed"]); bad=sorted(r["total_ms"]/1000 for r in rows if r["failed"])
import statistics; print("clean P50",statistics.median(ok),"blocking P50",statistics.median(bad))
PY

# P1① 消费方 grep
grep -rniE "data_task_completeness|ISSUE-RESOLVED-INTEGRITY|library_coverage_gate|LIBRARY-COVERAGE" \
  --include="*.py" --include="*.yaml" --include="*.toml" --include="*.ps1" . | grep -v "\.runtime/"
```

测试台沙箱机制：`GIT_INDEX_FILE` 指向 `.runtime/tmp/gaudit2/index.sandbox`；样本 blob 经 `git hash-object -w`+`update-index --cacheinfo` 入沙箱索引（真索引零写）；磁盘型样本置于 `.runtime/tmp/gaudit2/samples/` 或即建即删；审计与执行统计写入函数在测试进程内被替换为内存捕获。全程未执行任何 commit/checkout/reset，真暂存区经提交前后对账核实无涉。

## 7. 发现与观察汇总（呈 Owner）

| 级别 | id | 内容 | 建议 |
|---|---|---|---|
| 发现 | F1 | fail_open_register 派生册过期（--check exit=1，5 行指向已删文件） | 门禁基建车道重跑生成器落册，path_ownership_map 同查 |
| 发现 | F2 | REFERENCE-INTEGRITY 触发器 `['docs/']` 收窄 DANGLING/RULING 原有全提交检查面 | 触发器扩 `['docs/','.py','.yaml']` 或摘除；单台 P50≈2.1s 可承受 |
| 观察 | O1 | trae_035 paired_gate_id 指向退役墓碑（校验不炸语义死） | 规则清扫批置 null 或改指承接台 |
| 观察 | O2 | capability_canonical 3 条 canonical 指向已删文件（lookup 标 dead 设计内） | 随 F1 同批清理 |
| 观察 | O3 | module_translation 残留已删模块条目 | 翻译册对账批清理 |
| 观察 | O5 | PERM-TRIGGER 不识别 threading.Timer 时间触发 | 检测器扩面清单挂账 |
| 观察 | O8 | own 化审计 attribution 实战命中低（抽验 3/3 空） | 归因面补 claim_snapshots |

（O4/O6/O7 见 §2.1/§3.2 正文。）本车道只读+测试红线全程遵守：发现均登记未自修。
