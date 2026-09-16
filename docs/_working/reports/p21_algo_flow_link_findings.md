---
ttl: task_bound
date: 2026-09-17
---

# P2-1 ALGO_FLOW 出仓战役 — 环境与治理面发现登记（不改判，只留账）

<!-- creation_token: algo-flow-externalize-p21-algo-flow-link-findings-2026-09-17 -->

> 口径：本文件登记**出仓链路之外**在战役执行期实测到的环境/门禁/工具缺陷。凡"改一行就能让
> 本战役变绿"的处置一律不做——弱化门禁换绿灯是把病藏进墙里（AGENTS.md §4 第 2 条 退役审计靠触发率，
> §3 第 3 条新 gate 必 own-scope 是同一价值观）。每条给：实测证据 / 影响面 / 建议处置 / 归属。

## 0. 战役本体状态（对照用，非本文件主题）

- `src/zephyr/**` 死块（module docstring 之外机器块）实测 **0 处**；判据与 ALGO-FLOW-LINK
  门禁第 3 判据同源函数 `algo_flow_dead_block_spans`，不是另起一套口径。
- 尾池 143 件（69 件作者欠账除外）全量落地：t00 `af2f1ebbd3` / t01 `d99c7068c2` /
  t02 `76e376b3e3` / t03 `aabbde6575` / t04 `3c4e3cb2d0` / t05 `984728c6a3`，
  逐批 landed_id 反查 `git log -1 --name-only` 得 in_commit=expected、extra=0、missing=0。

## 1. 提交序列化 worktree 的双写者不变量无强制（P1，#ARCH-317）

- 实测：`scripts/governance/commit_queue_landing.py` 每次消费条目起手
  `_sync_worktree()` = `git reset --hard refs/heads/dev` + `git clean -fd`。两个进程同时排空队列时，
  后者起手即把前者"已 apply 未 commit"的新文件连抹——本战役 3 个批次（t00/t01/t02 + cga）
  整批报 `ALGO-FLOW-LINK：12 处 yaml 不可读（已删除?）` 与 `no changes added to commit`。
- 监视器取证（`.runtime/tmp/bt_wt_watch.py`，2s 采样）：02:27 那次快照 24/24 在场且 staged 全程未掉，
  下一帧归零——排除"快照写坏"与"门禁误判"两条假设。
- 对照实验（决定性）：同批内容原封 `requeue`、只让常驻 `commit_belt_daemon` 消费 → `af2f1ebbd3` 24/24
  干净落地。**凶手是自家脚本补的那次 drain**，不是环境。
- 根因结构：`SerializerLease` 用 O_EXCL + TTL=300s，`acquired_at` 只写一次、**不续约**；
  超 TTL 后任何进程都可合法接管，而单批 gate 链实测 3–7 分钟，与 TTL 同量级 → 长批必被抢。
- 建议：lease 心跳续约（消费循环内每 60s touch `acquired_at`）+ 接管前强制读 processing/ 判活；
  或把"新文件快照 apply→commit"做成同进程内不可打断的临界区。
- 归属：队列落地器（非出仓器）。我方已自改规避（`bt_land_queue._wait` 只在守护 PID 判死时才 drain）。

## 2. 全索引扫描型门禁连坐无辜提交人（P1，#ARCH-318）

- 实测：`NO-LONG-PARAM-LIST` 等 `own_scope: false` 门禁扫的是**整个 git index**，
  他会话在途 staged 的 `src/zephyr/strategy_pipeline/fw_backtest.py` 违规，把我这批
  一个字节都没碰它的提交拦死；红蓝探针 R2/R4/R5 三轮 verdict=wrong_gate 皆因此。
- 与裁定#279/#ARCH-316 同族，但那批只治了 4 个**内容扫描**门（HEAD 基线差分），
  结构扫描面（跨文件参数/行长统计类）未覆盖。
- 建议：按 #ARCH-316 同一配方补 HEAD 基线差分（NOW−BASE 只阻断本次新增，NOW∩BASE 存量降级
  warn 并归属责任人），或强制走队列（serializer worktree 净暂存区结构性免疫）。
- 归属：gate_engine。我方规避=战役后续全部改走提交队列（AGENTS.md §2 第 6 条）。

## 3. 未提交工作在共享主区可被整片吞掉（P1，#ARCH-319）

- 实测：2026-09-17 02:59:14 主工作区 **214 个在途脏文件同一分钟被改写**（mtime 聚类），
  其中本会话 4 个未提交工具件被还原到 HEAD，丢失 +290/−13；`externalize_algo_flow.py`
  于 02:59:14 落盘为 HEAD 内容，03:06 的队列快照因此抓到的就是 HEAD → 队列项 `q-…-0049`
  落 `noop@2436f92c`（in_commit=0 missing=4）。
- 排除项：`.runtime/workspace_alerts/stash_notice.json` 当夜只有 1 个文件、属
  `st-skeletonaudit-20260916` 的 pre_merge_clean，非本事件通道；无文件锁在场（`lock_files.py status`
  = CLEAN）；本会话未跑过任何 mutating git 命令。
- 恢复：23 条编辑从会话记录（sidechain `agent-ageneral-purpose-e1464ec45783daa2.jsonl`，
  01:10–01:24）逐条重放，`old_string` 全部唯一命中、零模糊匹配，自 pristine HEAD blob 二次重放
  得同 sha256；重发批 `tl1b` → `2bdc9f074a` 4/4 干净落地。
- 建议：①"每轮修改即 git add"（RULE-GIT-SAFE 第 12 条）在直改主区模式下必须真执行——staged
  内容不会被 `reset --hard` 之外的批量改写吞（对象库有 blob）；②长战役工具链改完即出小批落地，
  不攒到收尾；③批量改写类工具（blueprint 归一化/生成器全库刷）应限定自身产出面，
  不做 `git checkout`/整片回写。
- 归属：共享主工作区并发模型（结构性，非单一会话过失）。

## 4. `apply_depgraph.py --add-design-node` 对 MOD-* 蓝图恒发假告警（P3，#ARCH-320）

- 实测：`scripts/governance/apply_depgraph.py:1097` 按 `docs/03_modules/{blueprint_id}/blueprint.md`
  推路径判存在，而 DB 触发器 `check_blueprint_id_three_track()`（裁定#208 三轨制）只接受
  `MOD-*/D-*/SH-*/SYS-*/PLACEHOLDER*`——两个口径不可能同时满足：MOD-* 必然"文件不存在"，
  填目录名（如 `_cross_layer/gov_scripts`）则被触发器拒绝（本轮两次调用分别撞中，第二次
  `add_design_node失败: nodes.blueprint_id format violation`）。
- 影响：设计态登记要么带假告警、要么直接失败；`blueprint_path` 机械推导对 MOD-* 也是错的
  （写成 `docs/03_modules/MOD-GOV_ALGO_EXTRACTOR/`）。
- 建议：路径推导改查真源（module→blueprint 映射注册表），别拿 id 当目录名。
- 归属：apply_depgraph（登记侧）。本轮结果：node_id=14462964 以 `MOD-GOV_ALGO_EXTRACTOR`
  注册成功、带 missing 标记（既有先例同形态，非新造偏差）。

## 5. ALGO-FLOW-LINK 读暂存区的方式恒失败 + scope 外存量（P2，#ARCH-321）

- `src/zephyr/gov_enforcement/commit_gates/algo_flow_link_gate.py::_read_staged` 调
  `gateway.read_staged_file`——**该方法不存在**，异常后回退 `(root/rel).read_text()` 读磁盘。
  后果：门禁判的是工作区内容而非 staged blob，与 #ARCH-316 治的"观测面错位"同一病（staged≠磁盘
  时会误判/漏判）。修法=改用 `git show :<path>` 或补 gateway 该方法（**不能反过来放宽门禁**）。
- scope：门禁只覆盖 `src/zephyr`，`scripts/`+`tests/` 实测 **28 处死块 / 24 件**在覆盖外。
  其中 ≥9 处是**自指夹具**（`code_algorithm_extractor.py` 2、`check_algo_flow.py` 1、
  `test_algo_flow_link_gate.py` 2、`test_code_algorithm_extractor.py` 3 等——解析器/门禁的测试
  数据本就必须内联，出仓它反而毁测试），其余 19 件（regime/backtest/data 测试与两个 resource
  生成器）属真存量。**结论不是"清仓"而是"分家"**：自指夹具要显式豁免口径，真存量要逐件判
  该搬该删——两条都需要算法作者语义输入，工具无权代判（伪造边=错图冒充已验证）。
- 归属：gate 实现 + 门禁 scope 定义。

## 6. `safe_write_text` 残留 `.tmp.<pid>.<ms>`（P3）

- 实测：`scripts/**` 下 9 个 `.tmp.<pid>.<ms>` 残留，owner PID 35264（Qoder CN）/31816（ZCode）
  **均存活**——即宿主工具进程的中断写入残片，不是本会话可判死的孤儿。按"存活进程的文件不动"
  处置：本轮不清理，只登记（清理需其属主会话或 Owner 判定）。
- 建议：`safe_write_text` 在 rename 失败的 finally 里自清 `tmp`；或写入端加启动期清扫（属主 PID
  判死才清）。

## 7. #ARCH-319 通道二次发作：CAS 写成功的热文件仍能被整片盖回（P1 复现，同 #ARCH-317 家族）

- 实测：04:0x 本会话以 `safe_write_text(expected_base_sha256=…)` 对 `ruling_registry.yaml` 完成
  CAS 写入并**工作区读回核过**（entries=110，尾条 `裁定#292`）；04:4x 复核时工作区该文件已回到
  `HEAD + 1` 形态——尾条是他会话的 `裁定#291`，`#292` 整条消失（非本会话所为：本会话期间对该文件
  只有那一次写入）。即"以陈旧内存副本整文件改写"能盖掉别人的**已落盘**内容，CAS 只保证写入瞬间
  的基线，不保证事后不被回退。
- 与 §3 同一通道，但本次目标物是热注册表，危害更高：注册表条目是裁定/门禁/令牌的唯一真源。
- 本轮处置（不改判、不追归属，AGENTS.md §3 第 4 条）：重贴 `#292`（号位钉死，因
  `#ARCH-317..321` 的 `related_adjudication` 已反向引用 292）+ **当分钟即出小批**落地，
  把"未提交窗口"从小时级压到分钟级；建议治本同上：热文件写入后应立刻 staged（对象库留 blob），
  或由注册表写入器统一"写→add"闭环。
- 归属：共享主工作区并发模型（同 #ARCH-319）。

## 8. 端到端核销器判据分家：硬缺陷 vs 半径外吸收（不需白名单）

- 旧判据在"AST 指纹变了但字节码流也变了"时一律记 `ast_semantic_drift`（硬缺陷），
  round4 因此留下 2 件需人查；人查结论=他会话在途代码被整文件快照带进本批（`retain_ratio`
  字段+`__post_init__`、`slippage_bps` 三元式），非出仓器所为。
- 新判据（`.runtime/tmp/bt_diff_radius.py`，收口后随临时件一并删除，机制侧候选转正见 §5 归属）：
  出仓器对 `.py` 的**全部**编辑半径被几何限定=机器块跨度 + 裸字符串语句内散文 + 一行 external
  锚 + 注释空行；差异里出现"半径外的可执行语句增删"即不可能由出仓器产生 → 记
  `info_foreign_absorbed_code` 并附证据行；半径内仍变指令流才是工具缺陷，保持硬判据不放宽。
- round5 结果（58 批 / 2342 个 .py / 2339 有锚 / 2177 图对比）：硬缺陷 **0**，
  `info_foreign_absorbed_code` 2 件（即上述两件，证据行现为纯指令行，散文噪声已剔除）。
- 台账侧同步收口：`docs/_working/reports/algo_flow_author_debt.md` 由已落地生成器
  （`29e7dafce0`）现扫产出，恒等式 47+17+5（作者欠账 69）+ 可机械 5 + 其他 0 = 池 74 自证成立。

