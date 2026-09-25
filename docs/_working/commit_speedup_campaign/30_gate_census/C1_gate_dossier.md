---
ttl: task_bound
---

# 门禁证据卷宗（14 天窗，READ-ONLY 实测；结论级＝案卷，非裁定）

> 测量窗口实际长度 11 天（日志首条 09-13 → 09-24），未满 14 天——如实标注。
> 数据源：`.runtime/audit/{gate_execution_stats,commit_block_events,preflight_events,bottleneck_ledger}.jsonl`
> ＋ `git log --since=2026-09-10` ＋ `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`
> ＋ `gate_cache_preflight.py:43-64`（白名单）＋ `commit_gate_registry.py:108`（`ms>=1.0` 过滤）。
> 处置口径（Owner 明令，见 `90_verification/decisions_log.md`）：**只合并/降档/diff 化，夜间不执行退役**。

## 0. 底数
真实链 **1,330** 条（`n_specs≥80`；436 条 `G1/bad/COND` 为单测合成，已剔除）。
全部门禁 CPU **111,852 秒＝1,864 分**；其中现役 102 册名 **97,476 秒＝1,625 分＝73.3 秒/链**。
单链 mean 84.1s / p50 56.5s / p90 189.9s / max 521.9s。预跑 preflight 4,379 次 **681 分**。
被拦尝试烧掉 **2,386 分**（1,478 条带 `gate_chain_ms`）。
**固定地板回归**：`gate_chain_s ≈ 81.2 + 0.96 × files`（n=1,478）⇒ 单文件 mean 65.1s / p50 45.6s。
名册在窗内漂移：111→117 →（09-23 合并）99 → 102；24 个 legacy 名只有 09-23 前数据。

列义：`trig`=出现在链里且 ≥1ms 的链数(/1330)；`blk`=commit_blocked(gate_id) / 链内 failed；`min`=14d 总分钟；
`own`=`gate_registry.yaml.own_scope`；`wl`=缓存白名单；`pair`=tests/ 正反例（启发式，见 E3）。

## 1. 排名表（按分钟；全部为建议）

| gate | trig | blk | min | avg/p90 ms | own wl pair | 建议 | 证据等级 |
|---|---|---|---|---|---|---|---|
| CREATE-GUARD | 1330 | 98/110 | **221** | 9986/49125 | F – Y | **压缩**（见簇1；2.68MB 册 `yaml.safe_load` 实测 3.61/4.20s＝其耗时 36-42%；`create_guard.py:515` 逐类 git grep） | 实测 |
| CAPABILITY-OVERLAP | 1330 | 27/73 | 111 | 5003/15937 | T – Y | **diff 化＋并入簇3**（basename 碰撞面已被 CREATE-GUARD 内嵌） | 部分实测 |
| CH-VERSION-COL | 1124(+206 skip) | **0/0** | 86 | 4589/11110 | F – Y | **恒绿→先装表**（勿判死；files_trigger=schema/ddl） | 实测＋推断 |
| RECONCILER-HEALTH | 1137(+193) | **0/0** | 77 | 4065/8047 | F – Y | **降档异步**（读 `.runtime` 状态文件，非提交面判据） | 部分实测 |
| BLUEPRINT-HEADER | 276 | 5/10 | 77 | **16629**/25968 | F – Y | **降档异步**（union 台无条件跑双子判据） | 部分实测 |
| REGISTRY-MASS-DELETION | 1330 | 13/10 | 73 | 3314/14750 | T – Y | **保留**（Owner 门位 §5.2） | 实测 |
| GATE-ERRCODE-CONSISTENCY | 487(+240) | 23/9 | 72 | 8841/16781 | F – Y | **降档异步**（rglob＋importlib 动态载模块） | 实测 |
| CH-BATCH-SIZE | 1330 | 11/11 | 67 | 3004/9750 | F – Y | 保留（钱/数据完整面） | 实测 |
| GIT-CALL-BUDGET | 1330 | **0/0** | 65 | 2915/9704 | F – Y(warn) | **降档 post-commit**（warn-only 却做 8 处 subprocess AST 扫） | 实测 |
| BLUEPRINT-FORMAT | 1330 | 94/155 | 55 | 2462/8609 | F – Y | **并入簇2** | 实测 |
| MUTABLE-CONST-WITHOUT-FINAL | 1330 | 41/273 | 53 | 2386/7750 | F – Y | **diff 化**（41 拦里 38 条无可解析路径） | 部分实测 |
| NO-SECRET-HARDCODE | 1104(+226) | 0/9 | 52 | 2806/5532 | F – Y | **不可建议删**（见 §4） | 实测 |
| GATE-DOMAIN-FK / SSOT-REDEFINITION / TTL-METADATA / NO-HARDCODED-URL / CONSUMERS-ACCURACY | 1226/1330/1327/1330/1131 | 0/47/35/0/0 | 50/42/28/26/32 | — | F | 簇1·簇2 成员；后三台恒绿→先装表 | 实测 |
| PURE-SHIM | 1330 | **0/0** | 5.8 | 262/562 | F – **NO** | 零消费候选（**挂起不执行**） | 部分实测 |
| STASH-ACCUMULATION | 1329 | **0/0** | 1.1 | 49/78 | F – **NO**(0 文件引用) | 零消费候选（**挂起**） | 实测 |
| RECONCILER-FILE-OPS | 3(+193 skip) | 0/0 | ~0 | 16/16 | F – **NO**(0 引用) | 零触发候选（受 <1ms 盲区限制，**挂起**） | 实测 |
| META-TESTS-COVERAGE / FORGED-GW-MARKER | 0 可见 | 0/0 · **6/0** | ~0 | — | F | 前者不可判（trigger_skip=146）；后者**保留**（实测 6 拦＝非零触发） | 实测 |
| WORKTREE-REQUIRED / CLAIM-REQUIRED / HELD-OVERLAP / SESSION-REQUIRED / PROTECTED-PATHS | ≤47 各 | **80·57·60·16·12** | <1 | — | F | **零成本但高拦截→保留**；并说明"链内计时"系统性低估早退型台 | 实测 |

## 2. 三个可立即执行的簇

**簇1 共册解析**：CREATE-GUARD, SSOT-REDEFINITION, NO-SECRET-HARDCODE, REGISTRY-YAML-PARSE,
DERIVATION-ANNOTATION, DERIVED-FILE-DELETION-PROTECTION（六台同读 2.68MB canonical 册）；
另有 9 台同读 `in_process_gate_registry.yaml`、6 台同读 `noqa_exempt_registry.yaml`。
共同真源＝**册字节**。合并形态＝"一次解析＋多条判据数据"，判据零变化 ⇒ **可直接套"重放最近 100 笔逐笔一致"**。
内收判据：同真源可派生→必并。

**簇2 文档头/放置**：BLUEPRINT-FORMAT, BLUEPRINT-HEADER, MODULE-ID-CONSISTENCY, TTL-METADATA,
FILE-PLACEMENT-TTL, EXEMPT-ZONE-FM, DOC-REF-BROKEN（合计 ≈8.6 秒/链 ≈191 分）。
真源＝frontmatter/头部字段＋`directory_zones`/trae_028。判据对象**不同**（ttl ↔ 头格式 ↔ 链接实存）
⇒ 只能收敛为"一台门＋7 条判据数据"，**7 条判据一条都不可退役**。
自证：union 已有 `[源台名]` 前缀先例；重放须逐台比对 detail 文本等价，不能只比 passed。

**簇3 复杂度/克隆**：COMPLEXITY-GUARD（＝NO-HIGH-COMPLEXITY＋NO-GOD-CLASS＋NO-LONG-PARAM-LIST 的 union）
＋ FILE-COPY ＋ FUNCTION-DUP ＋ PURE-SHIM ＋ CAPABILITY-OVERLAP ＋ CREATE-GUARD 内嵌 `check_capability_duplicates`。
实测病灶：union 台**丢掉了子台的 files_trigger** ⇒ post-merge 无条件全跑。
零判据变化动作＝**给 union 补回按文件面短路**。（合并前后耗时不可直接比，见 §6-E2。）

## 3. 回收测算（含算式与"必须先装表"项）

`73.3 秒/链 − 10.0（簇1 共册一次解析） − 6.8（内容扫描类恢复条件触发） − 15.0（四台降档异步：
RECONCILER-HEALTH 3.47 ＋ BLUEPRINT-HEADER 3.45 ＋ GATE-ERRCODE 3.24 ＋ GIT-CALL-BUDGET 2.92 秒/链）
≈ **41 秒/链（−44%）**`
⇒ 固定地板 81.2 → ≈48 秒；单文件 p50 45.6 → ≈25 秒。

内容扫描类现况实测：白名单 14 台 ran 6,408 次 / cache_hit 557 ＝ **命中率 8.0%**；
该 14 台总盘只占全部门禁分钟 **6.1%**（6,789/111,852 秒）⇒ 缓存类优化天花板很低。

**达不到"秒级"**：要进个位数必须动 **always-run 的 43 台（44.1 秒/链＝977 分＝60%）**，
本轮证据不足以支撑该结论。**链外另计**：`slow_item` 均值 755.4 秒（n=173）属衍生再生扇出，删门碰不到它。

**必须先装表才能确认的四项**：① `<1ms` 盲区＝33.7% spec 不可见（`commit_gate_registry.py:108` 的 `ms>=1.0` 过滤）；
② `commit_slow.gate_chain_ms` 恒 0（A1 已在修）；③ 链记录无 session_id/qid 关联键（无法做归因与重放对表）；
④ 链内无文件面指纹（"是否因 own-scope 而省"不可测）。

## 4. 明确不建议删除的门（AI 无裁撤权；证据指向"拦截有效"）

- **密钥/泄密面**：NO-SECRET-HARDCODE, NO-BARE-GETENV, SECRET-REGISTRY-CONSISTENCY,
  ZEPHYR-ENV-DIRECT-ACCESS, REAL-KEY-REFERENCE-SCAN, MSG-EXPOSURE。
- **机制红线**：FORGED-GW-MARKER（实测 6 拦）、PROTECTED-PATHS（12）、GIT-DANGEROUS、SESSION-HEARTBEAT。
- **并发毁伤面**：WORKTREE-REQUIRED(80)、CLAIM-REQUIRED(57)、HELD-OVERLAP(60)、
  FOREIGN-CHANGE-DETECTION(37)、HOT-FILE-BASE-FRESHNESS(33，6h 修复率 **100%**)、COMMIT-SCOPE(35)、SESSION-REQUIRED(16)。
- **钱/数据面**：CH-BATCH-SIZE、CH-FINAL-GATE、CH-VERSION-COL。
- **Owner 门位/真源治理**：REGISTRY-MASS-DELETION（§5.2）、CREATE-GUARD（第二真源）、RULE-EXECUTION-PAIRING（28 触发/0 拦＝观察）。

理由一句话：**"零阻断≠无用"** 在本卷宗里同时出现两种零差值形态——HOT-FILE-BASE-FRESHNESS 33 拦全部真修，
与 STASH-ACCUMULATION 0/0，数值同为"零"而意义相反。恒绿且无配对测试者应判"疑似判据失效"，不得判"可删"。

## 5. 处置结论（本役采纳范围）

采纳：簇1／簇2／簇3（合并与补短路）、四台降档异步、MUTABLE-CONST 与 CAPABILITY-OVERLAP 的 diff 化。
**挂起不执行**：PURE-SHIM / STASH-ACCUMULATION / RECONCILER-FILE-OPS 三个退役候选——
理由＝§6-E1 与 §3 的 `<1ms` 盲区使"零触发零消费"在现测下不可证。挂起项已进待 Owner 裁定清单。

## 6. 诚实清单（测不出或不可信，逐条给因）

- **E1 真修复率不可测**：1,531 次拦截仅 **596（38.9%）** 的 detail 含可解析路径（截断或无文件面，
  如 WORKTREE-REQUIRED、GATE-PRECOMMIT-RUN 100% 不可测）；路径落地对热文件（registry/depgraph）有系统性假阳性
  ⇒ 6h 76.5%、ever 91.3% 只能作**上界**；会话侧证（`[sid]`↔commit）166/259=64.1%，口径不同**不可与前者合并**。
  RENAME-DEPGRAPH-SYNC 0%、TRANSLATION-COVERAGE 4% 极可能是改名后面包屑失配，而非"拦了没人修"。
- **E2 合并前后不可比**：09-23 名册 114→99 切窗（前 1,050 链／后 280 链）；同窗对照门均值 **+139%**
  （CREATE-GUARD 6.81→21.91 秒/链，且它不是被合并台），files_count 反而 16.6→7.8；逐日 mean 42s→423s 抖动 10 倍
  ⇒ **任何"合并提速/劣化"结论都必须受控重放后才可写进交付**（判据＝重放 100 笔逐笔一致，本仓 F3 判据②的历史欠账）。
- **E3 配对测试列是启发式**（正则扫 `tests/**/test_*.py` 断言）：9 台判"单边"，复核后 MSG-STYLE／UNSAFE-DICT-SPREAD／
  CH-FINAL-GUARD 实为双边（`assert passed`／`violations==[]` 变体）；仅 3 台（PURE-SHIM／STASH-ACCUMULATION／
  RECONCILER-FILE-OPS）tests 目录 0 引用属硬事实。
- **E4 I/O 类分钟占比为源码静态签名推断**（全仓 312 分／衍生进程 252／内容扫描 273／其余 788／DB·网络 0），
  无运行时打点 ⇒ 等级"推断"。
- **E5 名册不同步**：`commit_gates/*.py` 119 个模块 vs 在册 102 vs `gate_registry.yaml` 113 条 commit-gate
  vs 链内出现 124 个计时名；REAL-KEY-REFERENCE-SCAN／GATE-VOCAB／CONSTITUTION-LINE-LIMIT／TASK-ORDER-DOCS-LOCK
  的 `own_scope` 为 None。
- **E6** 所有"零触发/零消费"退役结论一律**待装表**后复判（E1＋§3 之 ①③ 决定其当前不可证）。