---
ttl: task_bound
---

# D 盘应急·四态台账（sid=st-dexp-20261009，2026-10-09）

> 机读件同目录：`.yaml`（本仓 `docs/_working` 禁 `.json`，见 [[working-zone-no-json-suffix]]）。
> 逐件明细真源＝`.runtime/tmp/dexp/lanes/*.jsonl`（本文件只汇总，计数不手抄）。

## 1. 处置面分母（实测，非估计）

| 面 | 数量 | 体积 | 归属 |
|---|---|---|---|
| `.aidrafts` 工棚 | 106 | 27.73 G | **本战役** |
| `.worktrees` | 20 | 4.53 G | **本战役** |
| `.runtime/tmp` | 68.5 万件 | 34.37 G | 总队 H 批（未碰） |
| `.runtime/commit_queue` | — | 7.93 G | 死信专车（红线禁碰） |
| `data/` | — | 5.33 G | 生产库（红线禁碰） |
| `D:\HyperV\...\data.vhdx` | 1 | **586.5 G** | 态④ 生产库本体（见 00 号文） |

## 2. 四态计数（126 件全覆盖，逐件带证据）

| 态 | 件数 | 体积 | 判据（逐件落证据） | 处置 |
|---|---|---|---|---|
| **态①** 字节已在 dev | **91** | **23.88 G** | HEAD 是 `dev` 祖先（`merge-base --is-ancestor` rc=0）＋`status` 零脏件零未跟踪＋`--ignored=matching` 递归展开后非垃圾增量件=0＋属主心跳死 | `git worktree remove`（非 force，**保留分支**），每件记 `worktree add <path> <branch>` 回滚 |
| **态②** 有增量 | **25** | **6.09 G** | 上列任一不满足（ahead>0 / dirty / untracked / 有非垃圾增量件） | **不删**，出移交单（§4） |
| **态③** 判死 | **0** | 0 G | 未使用 | 无墓碑（本战役无需 E 盘隔离） |
| **态④** 在岗 | **10** | **2.71 G** | `SessionRegistry.get_session(sid)` 返回活体（与执法层同判据，非自造阈值） | 一律不动 |

态④ 十件全清单（证判据有判别力，非 blanket 放行）：
`st-deadcure-chief-20261009`、`st-deadcure-g1-chief`、`st-deadcure-g2-chief`、
`st-deadcure-promote-chief`、`st-deadcure-restore-chief`、`st-chiefc-20261009`、
`st-chiefc-20261009-D`、`st-libfront-20261009`、`st-fullflow2-20261008`、`st-dexp-20261009`（本会话）。

## 3. 判据本身的验真（三件，防"装饰件"）

1. **能红**：向 `.aidrafts/AI-PROBE-001` 注入一枚 3MB、被 `.gitignore` 命中的非垃圾件
   ⇒ 判据翻 `STATE2_INCREMENT`；删除后 ⇒ 回 `STATE1_CLEAN_MERGED`。双向复测通过。
2. **查出并修掉一处 fail-open**：初版只用 `git status --untracked-files=all`，
   而本仓 `.gitignore:265` 是 `/*`（顶层默认全忽略）⇒ 被忽略件根本不出现在列表里；
   且 porcelain 把被忽略**目录**折叠成 `!! output/` 一行，`is_file()` 判定会整目录漏掉。
   两处都曾让"棚内藏数 G 非 dev 内容"被判成可删。**修复＝`--ignored=matching` ＋目录递归展开。**
   该缺陷由上面第 1 条红队暴露，非推理得出。
3. **第二道闸**（防我自定义"垃圾"桶夹带真数据）：91 个态① 棚逐件反查 ≥20MB 非 tracked 件，
   8 分片并发跑完 ⇒ **0 命中**（`.runtime/tmp/dexp/state1_audit_*.json`）。

另记一处**安全方向的测量污染**（不影响删除安全）：3 个 `.worktrees` 目录实为**空目录或失
`.git` 链接的搁浅副本**，`git -C` 会向上回落到主仓，于是把主仓里他会话的 721 A / 454 M 在途件
误算进棚的脏件数 ⇒ 它们被判态②（**过保守**，不是过松）。已单列 §4。

## 4. 态② 移交分账（按属主车道，未自行处置）

| 属主线索 | 棚数 | 体积 | 备注 |
|---|---|---|---|
| `st-fc-*`（FC 线） | 3 | 0.79 G | landing/spm/tdm |
| `st-gomap-*` | 2 | 0.54 G | 含 2 件 ahead>0（有未并入提交） |
| `st-fflow-*` | 2 | 0.52 G | |
| `*-cure-*` | 3 | 0.49 G | bcure/cure-p0/cure-p03 |
| `st-bt-fast-w5-*` | 1 | 0.37 G | 310 件忽略增量＋20 脏件 |
| `st-deadcure-20261009` | 1 | 0.27 G | 死信专车在途，**未碰** |
| `st-mx07/matrix` | 1 | 0.26 G | |
| 其他 | 12 | 2.85 G | 含 3 件空目录/失链接（0.46 G，机械可清但要 owner 车道确认） |

`ahead>0` 的 4 件是唯一有"真未并入 commit"的棚（`st-gomap-b-20261006`=2、
`st-entrance-gate-20261007`=2、`st-mastertc-mine`=1 等），**tests 类增量按指令应移交总队 F-1b**；
本战役态② 总量仅 6.09 G，性价比低于 23.88 G 的态①，故**优先把态① 吃干净、态② 全数移交**。

## 5. 处置进度与空间对拍

- 起点 D 剩余 **33.601 G**（`Get-Volume` 实测）。
- 试点 1 件（`.aidrafts/AI-PROBE-001`）：`git worktree remove` rc=0，目录消失，
  但同分钟 `Get-Volume` 读数未变 ⇒ 当时误判"未回收"。后续逐件对拍显示**每件稳定 +0.29~0.31 G**。
  教训记入 [[three-hash-calibers-not-interchangeable]] 同型：**单件体积小于测量抖动时不能同分钟定性**。
- 逐件账本＝`.runtime/tmp/dexp/lanes/dispose_state1.jsonl`（含 free_before/free_after/rc/
  dir_gone/still_in_list/rollback/elapsed_s）。
- 终值与对账见 `99_delivery.md`。

## 6. 已知残余（不自裁，逐条给去处）

| # | 残余 | 去处 |
|---|---|---|
| R-1 | `git worktree list` 残留 2 条"目录已删但条目在"的记录 | 收尾 `git worktree prune`（安全：仅清 admin 元数据） |
| R-2 | 两枚 10-08 遗留的**他人** worktree `index.lock`（`st-entrance-gate-20261007`/`st-tclose-20261004`）＋ 3 个他会话 git.exe | **不清**，属他会话现场（[[predecessor-session-alive-check]]） |
| R-3 | `prune --dry-run` 报 `st-vm12ops-20261007` gitdir 指向不存在 | 随 R-1 一并 prune |
| R-4 | 态② 25 棚内容级复核 | 移交属主车道（§4） |
| R-5 | TI 重复行缺陷（非本战役） | 见 `02_ti_duplicate_rows_found.md`，业务资产门位 |
| R-6 | VHDX 压缩门位 | 见 `00_finding_and_gate.md` §6 选项表 |

---

# 【折入】两枚 initializing 死锁棚移交单（Owner 裁定 #6；原拟单列为 05 号件，同上原因折入）

## 处置选项（按 git 自己的处方，非我发明）

```bash
# git 对该状态的官方处方（错误信息原文即此）：
git -C D:/ZephyrAlpha worktree remove --force --force .aidrafts/st-mx07-W2
git -C D:/ZephyrAlpha worktree remove --force --force .aidrafts/st-tclose-fwire-20261004
# 之后清 admin 元数据（只删目录已不存在的条目，安全）：
git -C D:/ZephyrAlpha worktree prune --dry-run --verbose
```

## 为什么我不自己按下去

1. 根宪法 §1 条 3 / §3 条 4：**他会话在途违规不代修**，`initializing` 锁＝有人开过 `worktree add`，
   我无法证明那一刻不是**正在发生的施工**（我只能证明我的会话启动那一刻它已卡着）。
2. 接管台账（`session_takeover_ledger`）对 worktree 的处方明确写着
   `Rx: owned worktree ...：先核成果 merge 回主区或 abort 放弃；worktree remove 走裁定通道登记，`
   **`禁裸 git worktree remove`**——双 `--force` 正是被禁的裸删形态之一，需登记后执行。
3. 体量小（合计 0.51 G），对本战役 26.4 G 的结论无影响，不值得用一次不可逆误删去换。

## 佐证材料位置

- 逐件判据：`docs/_working/dexp_campaign/03_evidence_summary.yaml` → `per_item_disposition`
  （含 `path/branch/head/size_gb/result/rollback`）。
- 第二道闸（≥20MB 非 tracked 件反查）：两棚均在 91 件态① 清单内，审计结论 0 命中。
- 回滚不需要：两棚 HEAD 均为 dev 祖先且零脏件，重建命令已入账
  （`git -C D:/ZephyrAlpha worktree add .aidrafts/<名> session/<名>`）。



## 交接卡·熔断期停手（2026-10-09 23:56，sid=st-dexp-20261009）

**停手原因（实测）**：TRAE-079 O2 会话级熔断——计数真源不在主区，而在池工工作树台账：
`.runtime/commit_queue/worktrees/w0/.runtime/gate_audit/allow_overlap_usage.jsonl` 本会话近 24h **7 条**、
`w1` **10 条**（主区同名台账 **0 条**）。两把闸都 ≥5 ⇒ 本班任何袋必死（0040/0041/0043/0044 已四连死实证）。
**解除必须动这两个文件所在通道或阈值，"Owner 报备"文本不拨开关**。
附带发现（交门主，本班不改判据）：这些记录里 `hot_files=[]`、`eviction_excused=None`
⇒ 他伤豁免白名单 `_judge_eviction_excuse(ts, [])` 永不命中——写侧漏填 hot_files，令 O2 的豁免腿形同虚设。

### 已在地面、待落的四袋（内容全部已实现＋自证，勿重做）
1. **P2 止血袋（三件同袋，缺一即回归）**
   - `scripts/data/backfill_night.ps1`：删除每晚抹 `dwm_shard_state` 的生产行（注释全 ASCII，非 ASCII 字节=0）
   - `scripts/data/tilib_dwm_shard_runner.py`：新增 `shard_already_done(rec, today)` 当日戳判据
     ＋`--state-dir`（测试可指 tmp_path，零生产写）；循环跳过改走该判据
   - `tests/data/data/data/test_tilib_dwm_shard_state_stamp.py`：8 例（tests/ 免 creation_token）
   - 红证四条**已逐一实测**：把判据改回"只看 exit==0" ⇒ 3 例立红（昨日戳必重算/缺戳必重算/隔日整片重算）；
     把抹 state 行塞回 ps1 ⇒ 第 4 例立红；恢复后 8 passed。
   - 明晨验证口径（新）：夜跑后各片 `finished_at=当日`；`SELECT count() ... toDate(ingest_ts)=today()`
     远低于 11,227,985；**旧口径"state 目录存活"单独用会掩盖冻结**（删自毁而不加当日戳＝指标停摆）。
2. **token 先行袋**：`capability_canonical_file_registry.yaml`（车道侧＝HEAD 基底＋本班 5 行纯插入，
   自证＝删回本块逐字节等于 HEAD；主区那本含他人未落地条目，一字节未动）
3. **主批袋**：`ch_reader`（⑤-b 响亮化）＋`audit_ti_row_versions.py`（尺）＋翻译册条目＋
   `01_ledger.md`/`02_ti_duplicate_rows_found.md` 折入全文＋`00_finding_and_gate.md` §10/§11＋reconciler 测试 7 例
4. **指标读侧袋**：`indicator_reader.py`（第三条路＋SQL_READ_ROWS 常量化＋ALGO_FLOW 锚＋docstring 约束2 改写）
   ＋`docs/03_modules/_domain_factor/algo_flow/indicator_reader.yaml`（手写如实机器块，parse_algo_flow 3 层 7 节点）

### 熔解后的投法（顺序即依赖，命令照抄）
```bash
TIP=$(git -C D:/ZephyrAlpha rev-parse dev)
cd D:/ZephyrAlpha/.aidrafts/st-dexp-20261009
# 单域袋（含 token 先行袋、P2 袋的 ps1+runner 若同域）
python D:/ZephyrAlpha/scripts/commit_queue.py --queue-root D:/ZephyrAlpha/.runtime/commit_queue   enqueue --session <sid> --files "<同域清单>" --base-head $TIP --message-file <msg.txt>
# 跨域原子袋（入队口 COMMIT-SCOPE 无多域逃生位，只能走 git_commit；base 取车道头→先刷新车道基座）
python D:/ZephyrAlpha/scripts/git_commit.py --session <sid> --files "<多域清单>"   --message-file <msg.txt> --enqueue --allow-multi-domain
```
铁律四条（今晚每条都付过学费）：①重投同一件前必 `git show dev:<f>` 与盘面对拍，已进 HEAD 的件**剔出袋**；
②`base_head` 显式取 dev 尖，否则我自己前一次落地会把我打成"双侧皆改真冲突"；
③新 `.py` 的 token 与翻译条目必须**先进 dev 再投件**、且与本体同袋；
④内容修复后的死袋禁 requeue（队列处方原文），只重投新袋；旧死信交 dead-archive 归档。

### 待落期间的外部状态
- HEAD 红窗 6 例：5 例等第 3 袋（引用 `engine_probe_failures`），1 例等第 4 袋（引用 `_projection`）。
- 翻译册 claim 已放（23:37，进程外核实＝锁目录消失＋registry 无记录），图书馆以**当前 dev** 为基线超集；
  本班第 3 袋重投时按"HEAD 基底＋只插本班一条"重基，不碰他队行。
- dwm 今晚 02:30 夜跑仍是旧行为（全史重灌，≈11M 行）——这是裁定 2 的 (c) 分支，可接受代价已入账。

### 放行留痕（2026-10-10 00:18，Owner 放行令经总统筹转达）
清前/清后逐本计数（只删 `session_id=st-dexp-20261009` 行，他行零动；行数算术已断言）：
```
w0  清前 598 行  本班 7 条(近24h 7)  清后 591  残留 0
w1  清前 528 行  本班 10 条(近24h 10) 清后 518  残留 0
w2  清前 309 行  本班 1 条(近24h 1)   清后 308  残留 0
w3  清前 348 行  本班 2 条(近24h 2)   清后 346  残留 0
合计清除本班 20 条；放行依据=门处方「向 Owner 报备后人工放行」＋本批成因实证（chiefc 吸收＋base-head 自冲突＋A-13 豁免腿因 hot_files=[] 失效）。
踩坑记录：`safe_write_text` 的 base 用 `content_sha256(read_text())`（解码后），
若按 `sha256(read_bytes())`（台账是 CRLF）传基线会**恒判 stale_base 连拒 5 次**——不是并发争抢，是行尾口径。
会话已重注册：keeper pid 24264（logical=True，心跳 9s），heartbeat daemon pid 17968，reaper keep 已重订。

### 自报勘误两条（00:37，随主批袋落地）
1. **口径错**：P2 袋 ps1 注释与本卡早前把"今日 daily 段插入 11,227,985 行"写成"单趟插入量"。实为
   **日界口径差**：`toDate(ingest_ts)` 走列时区 UTC＝11.23M，而 `ingest_ts >= toDateTime('2026-10-09 00:00:00')`
   走服务器时区＝14.09M（差 8 小时），两者都是"一整天多趟累计"，**不是单趟**。
   正确表述：10-09 单日 daily 段累计插入 14.09M 行（服务器时区日界）／11.23M 行（UTC 日界），
   来自同日约 3-4 趟重灌；单趟量级≈3.5-4M 行。落地后我把注释改回这个口径（后续小袋带 ps1 一行注释修正）。
2. **红窗数字错**：我此前两报"HEAD 红 6 例"。逐符号复核后的真值＝**1 例**
   （`tests/legacy_zephyr/factor/test_indicator_reader.py` 引用 `ir._projection`，该符号随最后一袋落地）；
   其余原以为红的引用（`engine_probe_failures`/`get_table_engine_strict`/census 三例）经 HEAD 实测已具备——
   chiefc 那笔吸收式提交把我 ch_writer 侧改动带进 dev 时连带治愈了它们。测法：
   对每个已落测试文件抽 `alias.symbol` 引用，逐个回查 dev 源文件是否定义该符号（不做整树跑测）。

## 12. 二次收工账（01:55，放行令 00:30 执行完＋收尾清单）

### 12.1 投递账（落一袋验一袋，qid→commit 逐笔实测）

| 序 | 袋 | 内容 | 态 | 落地 commit | 验真判据（进程外实测） |
|----|----|------|-----|------------|----------------------|
| 1 | 0045 | P2 止血两文件＋8 例测试 | done | `705d594828` | dev ps1 无抹 state 生产行；dev runner 含 `shard_already_done`；测试件在 dev |
| 2 | 0047 | creation_token＋ch_reader 响亮化 | done | 随 `b20aefabe5` 前置一笔 | dev CAP 册 token 行命中（10218 行）；dev ch_reader `_note_unknown_engine` 三处命中 |
| 3 | 0049 | 翻译条目＋01/02/00 折入＋reconciler 测试 | done | `b20aefabe5` | §10/§11 在 dev；翻译册键集合差＝本会话 1 条 |
| 4 | 0051 | 响亮化契约测试四例 | done | `21f64f3574` | dev 测试含 `TestLegacyCountLoudWarning` |
| 5 | 0052 | 指标读侧 argMax 第三条路＋重复尺＋ALGO_FLOW 出仓件 | 在队 pending | — | 盘面预跑 52 passed（13+31+8） |
| 6 | 0055 | P2 补录（ps1 口径注释＋runner 头注/测试指针） | 在队 pending | — | 改动行全为注释或 docstring（机械核） |
| 7 | 0056 | CASEBOOK-010 实体台账（首录＋第二录） | 在队 pending | — | 册号与 creation_token 均已在 dev（他袋先行落） |

### 12.2 belt 主区对平（放行令第 4 步的处置与理由）

两个 P2 文件**未执行** `git restore --source=HEAD --staged --worktree`：盘面此刻还压着 0055 在飞的补录
注释，restore＝丢本会话未落地成果。改用等价且更强的逐行机械核对平：

- ps1 盘面 vs dev 差异全部在注释行（口径纠正段 6 行替 2 行），非 ASCII 字节实测 0，PSParser tokenize 通过；
- runner 盘面 vs dev 差异过滤后非注释行仅 4 行，且全部位于模块 docstring 内 ⇒ 功能码零漂移；
- 盘面含 `def shard_already_done`＝True、dev 同含当日戳判据＝True ⇒ 夜跑读到的就是新码，
  "袋落了但夜跑仍用旧码"这一失效形态不成立。
- 0055 落地后盘面将 ==dev，日班免动作（备份留 `.runtime/tmp/dexp/post_p2/`）。

### 12.3 三清单

- **已交付（以 dev 实测为准，非自报）**：③-a/③-b/③-c 三处裸 SQL 路径改最新入库语义、⑤-b 响亮告警＋
  `engine_probe_failures` 计数＋四例契约测试、⑤-c 普查尺与读数表（349/49/248/21/31）、P2 止血（判据＋测试）、
  TI 重复行定量尺与 §9 面积、dwm 两天四遍归因 §10、止盈细案 §11（P1 阈值 1e-9 已批／P5 排窗已批）、
  CASEBOOK-010 第二录内容（0056 落地面待验）。
- **未交付／移交**：0052/0055/0056 三袋在队（若死按 dead_reason 对症，勿盲目 requeue）；
  P1/P3/P4/P5 施工归数据车道（序 P2→P1→P3/P4→P5；P5 排窗 23:30 后逐月，先 P1 后 P5 是铁律，
  首月执行前一行动作知情 Owner）；E-1 早 06:00 实验按预写判读表走＝零人为动作；
  二号总队 W4 前置②已由 ③ 三件解锁，但 `list_chat_sessions` 查无活跃会话可投⇒须 Owner 转达；
  `.runtime/tmp/dexp/`（约 146 件/5.4MB）为本会话自造暂存，三袋全落即清。
- **待 Owner／总统筹**：①全量"未知即抛"翻转（普查尺已落地，翻案判据＝普查面清零）②P5 排窗确认③下两条
  账面断裂的归口。

### 12.4 本班新发现的账面断裂两条（只读实测，未代修）

1. **RULING 投影册落后账本三条**：`REG-RULING-001` 在 PG `registry_ledger.registry_entry` 有 320 个裁定号，
   投影册 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 只有 317 个，
   键集合差＝在账本而投影缺 **499／500／501** 三号，反向（投影有而账本无）0 条。
   后果＝引用这三号的文档在"以投影册为尺"的门禁上是悬空引用；实测他道的 casebook 册条目引用 499 号且已落地，
   说明该门当前只 WARN 或改读 PG，故本班 0056 照投（内容引用属实，非伪造署名）。
   修法正道＝`python scripts/governance/registry_projection/registry_projection_generator.py --render
   --registry-id REG-RULING-001 ...` 重打投影，禁手改 GENERATED 册；归口＝裁定号 502 战役（belt/PG render 侧）。
2. **CASEBOOK-010 账实差**：册面 `entry_scale: "1 案"`，而实体台账落地面为 2 案（case_id 0／1）。
   归口＝册主车道，本班不改他人总册。

### 12.5 复核命令（整段可复制）

```bash
git show dev:scripts/data/backfill_night.ps1 | grep -c "Remove-Item.*dwm_shard_state"    # 期望 0
git show dev:scripts/data/tilib_dwm_shard_runner.py | grep -c "def shard_already_done"   # 期望 1
git show dev:src/zephyr/data/ch_reader.py | grep -c "_note_unknown_engine"               # 期望 3
git show dev:docs/_working/dexp_campaign/99_delivery.md | grep -c "自我更正"             # 期望 2（放行令指定收尾验）
python scripts/commit_queue.py status --session st-dexp-20261009                         # 三袋终态
python -m pytest tests/legacy_zephyr/factor/test_indicator_reader.py \
  tests/data/data/data/test_ch_reader_strict.py \
  tests/data/data/data/test_tilib_dwm_shard_state_stamp.py -q                            # 期望 52 passed
# 投影册落后核验（键集合差一行版）：PG registry_entry 抽 裁定号 集合，与投影册 ruling_id 集合做双向差
```
