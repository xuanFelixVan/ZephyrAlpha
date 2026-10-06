---
ttl: task_bound
title: 复盘台账·通宵尾件收口清扫班 st-sweep-tail-20260923
created: 2026-09-23
sid: st-sweep-tail-20260923
lane: sweep_tail
report_hour: 2026-09-23 17:55（白天班续，Max 五条裁定已收货执行）
---

# 清扫班台账（逐件：原死因 / 解锁动作 / 落地 hash / 证据等级）

证据等级：**A**=git HEAD·进程表等仓外权威面可独立复核；**B**=本班实测日志输出；**C**=本班探针脚本可复跑（脚本在 `.runtime/tmp/sweep_tail/`，TTL 区，须 promote 才长期存活）。

## 0. 时间线

| 时刻 | 事件 |
|---|---|
| 16:16 | 接令，先抢时间敏感件（重启窗 15:20-16:25 剩 9 分钟） |
| 16:21:18 | 调度器重启完成：旧 44624（滞后 dev 27h）→ 新 35080，**停机 18 秒** |
| 16:30:42 | tqcenter `kline_sector_880_incremental` 实跑成功 rows=14198（裁决点） |
| 16:32:08 | `kline_sector_880_resample` 与 09-22 同因失败（复现证据，已按 P1 登记） |
| 16:44-17:28 | 检出 st-stress 压测实跑 → 按家规让位，波次挂让位闸待发 |
| 17:28 | 连续三轮零进程，闸开放行，requeue 波次开火 |
| 17:39 | 主区 index 排弹完成（Max 批「7 add + 21 reset」）：回退炸弹 28→0，工作区字节零改动 |
| 17:40 | `session_worktree.py merge` 主区直连失败（他人 60+ 脏件挡道），改道队列正门 |
| 17:51 | 做T复活班 14 件代 merge 批入队 `q-20260923-st-sweep-tail-20260923-0001` |

## 1. 逐件三态

### 件1 BM-BUY-05 双变体去重 —— **已结案（Max 裁定号回话第 1 条收货）**

- 原死因：翻译册 `battle_map_steps` 段同 step_id 双登记 → 三向合并判身份不唯一 → 携该册的队列批结构性必死。
- 实况：**本班未动刀**。已由 `360468501e`(st-ailayer-p1) 摘 BM-BUY-05 短版、`66e6b31346`(st-regfix-lane0b) 摘同族 BM-BUY-14/BM-SIM-08。
- 本班复核（C，`verify_bmbuy05_v2.py`）：术前重复 3 对 → 术后 0 对（344→341 条）；HEAD 幸存条目==术前富版且含 AI-AUDIT21 补叙事。
- "富⊇穷"读数：字段集全等、穷版 108→富版 388 字符；字面非子串（穷版"锚点漂移"在富版改述为"语义混淆"）。**Max 判：结构口径成立即收货，不回滚。**

### 件2 requeue 波次 —— **已开火，6 封全部推到真门禁面**

波次前已做的排雷：落地环境 `auto_register_gates()` 主区实调不抛错；belt 起动（14:15:37）晚于名册修复（11:23）→ 常驻宿主已含修复；工作区 blob-vs-HEAD 三态探针逐件核。

| 原件 | 新件 | 结果 | 真堵点归类 |
|---|---|---|---|
| remedy-cf 0013 | 0023 | dead | **环境债**：`ruling_registry.yaml` HEAD 侧 `ruling_id=裁定#404` 同侧重复（新病，与 BM-BUY-05 同族） |
| emomine 0005 | 0006 | dead | 内容债：ruff / ruff-format / algo-flow-marker / any-abuse |
| combine 0017 | 0018 | dead | 内容债：CH-FINAL-GATE `allocation_inputs.py:405` FROM 缺 FINAL |
| tdm20 0026 | 0043 | dead | **快照过期**：09:04 整册快照自带 BM-BUY-05 重复，回灌即自毒 |
| xhs 0041 | 0052 | dead | **快照过期**：同上，`module_path=sim_daily_runner.py` 重复 |
| xhs 0042 | — | SKIP | 快照已全在 HEAD（按令"落地则跳过"） |
| xhs 0043 | 0053 | dead | 内容债：TRANSLATION-COVERAGE 缺 1 条 plain_zh |

- **进展判定**：环境级 `GateAutoRegistrationError` 已从所有新件消失——堵点从"结构性不可行"降为"逐件可修的真门禁"，这是本波的实际产出。
- **内容债三件不代修**（宪法 §3.4 owner 责任制）：combine / emomine / xhs 各自的 ruff、CH-FINAL、翻译条目归其作者车道；本班只出坐标。
- **两条通用判据（值得进册）**：① 携带**热册整文件**的死信，其快照若早于该册最近一次去重手术，`--from-bag` 回灌必自毒——须改"取本道 delta 重放到现 HEAD"；② 新出现的 `ruling_registry.yaml` 同侧重复（裁定#404）是 BM-BUY-05 同族病，会挡住一切携裁定册的批，建议列为下一台手术。

### 件3 ulib3b 0062（37 件）—— **状态改判：不投，交后继车道**

- 原死因 NEW-FILE-DEPGRAPH（3 个门 .py 无节点）实测已愈（三门 `build_status=stable`，节点 14984637/14984638/14984640）。
- 但 **st-ulib3c-20260923 车道正在同一写域在途**（其 0001-0003 件在 dead/pending 间往返，含 `logs_collector.py` ORPHAN-MODULE、REGISTRY-MASS-DELETION），与 0062 的 25 件真需落地内容高度重叠。
- 判定：按"同 payload 双投会产生完全重复项"与"他在途不代修"，本班**不投 0062**，转 ulib3c owner。0062 剩余真需落地件=25/37（12 件已在 HEAD）。

### 件4 修宪 0047 —— **按选项 a 执行中**

- 袋内 AGENTS.md 与主区工作区**逐字节同**（sha 5198a4bbda3d），改动=两行原地替换（+2 -2，宪法现 140 行 ≤300 上限不破）。
- **本班偏离一处并留痕**：原批第二件 `rules_integrity_db.json` 是 02:16 快照，HEAD 已被此后 post-commit 自动 fold 反超（实测 袋!=HEAD）→ 随批回灌=把他人已入库基线折回旧态（回退）。基线重置的设计内通道就是 gateway 自动 fold（先例 `84ef69262f`），手动 `--fold` 被 `ZEPHYR_RECONCILER_MODE` 明文禁。故**只投 AGENTS.md**，db 交自动通道。
- 落地方式：独立 scratch worktree 装快照字节 + `ZEPHYR_PROTECTED_PATHS_BYPASS=1` 随带 env 入队并自举排空（等价"到队首带 env drain 一次"）。

### 件5 两笔 merge —— **改道队列正门**

`session_worktree.py merge` 的实测行为=**在主区跑 `git merge`**，本机主区此刻 276 条他会话在途暂存 + 数十脏件，17:40 直连被 git 拒（`Your local changes ... would be overwritten by merge`，ort 失败，无 MERGE_HEAD 残留）。即使放行，gateway 遇 MERGE_HEAD 强制全量提交会把他人半成品吸收进我的提交=连坐。

- 排弹先行：`INDEX<HEAD` 28 条→0（7 条工作区已==HEAD 做 add、21 条做 mixed reset，工作区字节复核 0 改动；快照 `index_snapshot_20260923_173851.json` 可逐条复原）。
- **t0-revival（3 笔）已改道**：`git merge-tree` 内存算得无冲突合并树 `1d0a781e17`，scratch worktree 树==合并树逐位一致后按 14 件入队；热册增量经文本级逐字对 HEAD 判 0 撞键（纯插入）；2 个新脚本 depgraph 设计节点本班补登记（`14998198/14998199`，blueprint 用文件自带 `SH-SCRIPT-001` 锚，先误用 `[MODULE]` 名被三轨制格式闸拒，报错可复现）。
- **secbuild（2 笔）受阻待裁**：19 件与 HEAD 全异，其中 3 个新 .py 的 creation_token **在 HEAD 实测为 0**——该车道晨报 §七.3 自报"翻译/token 已被 oddjobs 批（5b6ee808a6）吸收落地"，与 HEAD 实盘不符（A 级证据：`git show HEAD:<capability 册> | grep -c sector_state_pipeline` = 0）。故其"注册表先行、不随批"的前提不成立，须补 11-14 条 token + 3 条翻译。**本班未补**，两条理由：① 代他人写 capability/merge_evaluation 语义字段属作者判断；② token 批登记工具 `batch_creation_tokens.py` 的锚点插入缺陷今日刚由 `b66dd183eb` 立为施工项、修复正被 st-stress 压测中，此刻批量注册=拿在测工具造热册数据伤。**请 Max 定点**：等工具修复落地后用工具补，或授权本班 CAS 手写补登。

### 件5b 二次调度器重启 —— **待 secbuild 落地**

Max 令：今晚 secbuild merge 落地后立即执行，硬约束明早 09:15 前，18 秒停机无需等窗。判据=新进程 `sector_state` 槽位数>0（本次重启实测=0，因分支未合）。

### 件6 时点任务 —— 两件全执行（A+B 级）

- 重启：守护 29112 保锁，子进程 44624→35080，停机 18s，272 任务/27 档全载，窗内完成。无优雅重载入口（无控制文件/无 CLI flag，Windows 跨控制台 SIGTERM=硬杀），故按守护"杀子→15s 轮询→重启"的既定设计走。
- 16:30 裁决点：`tqcenter 健康检查=healthy → rows=14198 last_key=2026-09-23`（昨日 14197 行同量级）→ **日K腿成功，切源可行性升级**；分钟腿仍未证（晨报 §七.2 的 1m 握手失败未被推翻），故 req_sentinel_02 的裁据应写成"日K通、分钟未证"。
- resample 缺陷：已按 P1 登记进 `src/zephyr/data/config/known_data_gaps.yaml`（新增条目 `kline_sector_880_resample_false_success`，含两日复现证据指针与"0 行+通道错=必记 FAILED"处方，修复归明晚 E2E 班）。登记面安全已核：`backfill_checker` 只分派 `date_range`/`empty_table`，`pipeline_idempotency` 不触发任何生产写。

### 件7 台账 —— 本文件；随班会话件与 P1 登记同批提交

## 2. 呈报清单（要人看的四条）

1. **secbuild 晨报的"token 已被吸收"自报与 HEAD 不符**（A 级）——弱模型车道的自报交付声明需按证据等级复核，勿据其解锁后继动作。
2. **`ruling_registry.yaml` 出现 BM-BUY-05 同族新病**（HEAD 侧 `裁定#404` 重复）——它正挡住一切携裁定册的批，建议列为下一台去重手术。
3. **主区暂存区是常驻雷区**：本轮实测 282 条中 28 条 INDEX<HEAD。任何走主区 `git merge` 的通道都会引爆；`session_worktree.py merge` 的主区语义与多车道现实冲突，建议改造为"scratch worktree 算合并树 → 队列正门投递"。
4. **热册整文件快照的重放纪律**：凡快照早于该册最近去重手术的批次，禁 `--from-bag` 整册回灌，改 delta 重放。

## 3. 复核命令

```bash
# 件1 术前/术后重复对照
python .runtime/tmp/sweep_tail/verify_bmbuy05_v2.py
# 件2 落地环境健康 + 死信件三态
PYTHONPATH=src python -c "import pathlib;from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates as a;from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry as R;a(R(),pathlib.Path('.').resolve());print('landing env OK')"
python .runtime/tmp/sweep_tail/probe_dead_item.py .runtime/commit_queue/dead/<qid>.json
# 件5 排弹三态（应全 0）
python .runtime/tmp/sweep_tail/triage_stale_index.py
# 件5 合并树一致性
git merge-tree --write-tree dev session/st-t0-revival-20260922   # 期望 1d0a781e17...
# 件6 重启与实跑证据
grep -nE "2026-09-23 16:(2[1-9]|3[0-9])" tmp/scheduler_run.log | grep -E "已加载调度计划|kline_sector_880"
```
