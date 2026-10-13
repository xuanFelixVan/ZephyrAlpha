---
ttl: task_bound
session: st-ffchief-20261002
date: 2026-10-02
title: T1 接管显化基建施工册
completes_when: 台账脚本+L3 门禁+判死钩子三件套落地，测试绿，词条/token/注册面全登记
resources:
  ledger_script: scripts/governance/session_takeover_ledger.py
  gate: src/zephyr/gov_enforcement/commit_gates/takeover_pending_gate.py
  salvage_hook: src/zephyr/security/access_control/session_concurrency.py (list_active 判死处)
  ledger_runtime: .runtime/takeover_ledger.jsonl
  resolved_dir: .runtime/takeover/resolved/
---

# T1 接管显化基建 施工册（st-ffchief-20261002）

任务书：`00_orchestration.md` §2.2（Owner 核心构想：接管台账 Takeover Ledger + 三层显化）。
本册是 T1 车道施工记录（设计/接口/接线点/测试证据），机生补充禁手改。

## 1. 病根与治本

**病根**：AI 施工队会话中途死亡 → 暂存区/worktree/claim/在途袋/心跳全成无主黑箱；下一个 AI 要重新考古，考古不出来就永久堆积（死袋无主/暂存区孤儿/claim 泄漏/ghost 心跳十五类病灶的公共根因）。

**治本 = 三层显化**（本车道全部落地）：

| 层 | 件 | 职责 |
|----|----|------|
| L1 资源清单 | `scripts/governance/session_takeover_ledger.py` `scan_dead_sessions` | 读 session registry（S4-D 分片+旧表聚合），对判死会话（`last_activity>7200s` 且非 `logical`）收集五类资源 |
| L2 死亡显化 | 同件 `write_takeover_entry` + `session_concurrency._salvage_takeover_ledger` 钩子 | 判死处自动生成/刷新接管条目 → `.runtime/takeover_ledger.jsonl`；幂等+600s 节流 |
| L3 门禁显化 | `src/zephyr/gov_enforcement/commit_gates/takeover_pending_gate.py`（TAKEOVER-PENDING, priority=160） | commit 文件命中 open 条目命中面 → 硬阻断并打印死亡证据+接管处方+`--resolve` 指引 |

## 2. 接口（真源=代码 docstring，此处只列签名）

```python
# scripts/governance/session_takeover_ledger.py
scan_dead_sessions(root, *, now=None) -> list[dict]        # 判死扫描（只读）
collect_resources(root, sid, entry, *, now=None) -> dict   # 五类资源：held_files/worktrees/staging/bags/heartbeat_files
write_takeover_entry(root, sid, *, resources=None, death_evidence=None,
                     registry_entry=None, now=None) -> dict  # 幂等生成/刷新 open 条目（600s 节流窗内原样返回）
load_open_entries(root) -> list[dict]                      # L3 门禁消费面
entry_match_surface(entry) -> set[str]                     # 命中面=held_files∪worktree dirty∪staging files（repo-relative posix）
# 命中面剔除（统筹 2026-10-13 批①）：_worktree_dirty 把"盘字节已等于落地面 _LANDING_REF(=dev)"的
# 跟踪件移出 dirty_files，另记 excluded_dev_identical=n 与 excluded_dev_identical_files 留痕；
# 病根=status 报的是对自家 HEAD 之差，车道指针落后 dev 时同字节件也报 M ⇒ 隔空挡死无辜袋
# （实证 .runtime/tmp/mineloop2/evidence/takeover_hit_face_proof_20261013.txt：card_binding.py
#  磁盘 sha==dev sha 仍被算作他人成果，挡死两枚码面袋）。比对不可用/未跟踪件一律保留＝只缩不扩。
resolve_entry(root, sid, by, note="") -> dict              # 终态迁移 .runtime/takeover/resolved/<sid>-<ts>.json

# CLI
python scripts/governance/session_takeover_ledger.py --scan                     # 扫死亡生成/更新 open 条目
python scripts/governance/session_takeover_ledger.py --list                     # 列 open 条目+处方
python scripts/governance/session_takeover_ledger.py --resolve <sid> --by <接管者> [--note ...]
```

条目字段：`ts/ts_epoch/sid/death_evidence{last_activity_age_seconds,last_heartbeat_age_seconds,pid,pid_alive,logical,threshold_seconds,reason}/resources{held_files,worktrees,staging,bags,heartbeat_files}/impacted_modules/prescription/status`（+`refresh_count`）。

## 3. 接线点

1. **判死钩子**（L2）：`session_concurrency.py` `SessionRegistry.list_active` 的 `expired` 集合处（reap 前）调 `_salvage_takeover_ledger(project_root, data, expired, now)`——函数内延迟 import `scripts.governance.session_takeover_ledger`（防循环；sys.path 兜底）；异常只 warning 永不阻断判死/收割主流程。
2. **门禁注册**：`in_process_gate_registry.yaml` 追加 `TAKEOVER-PENDING`（module_path/factory_function/enabled，priority=160）+ `commit_gates/__init__.py` ORPHAN-MODULE 静态引用区追加一行（#ARCH-GATE-REGISTRY-AUTO-001 已知限制）+ `gate_registry.yaml` 经 `generate_gate_registry.py` 机生刷新（182 条）。
3. **登记面**：`module_translation_registry.yaml` 两词条（大白话禁模板）+ `capability_canonical_file_registry.yaml` creation_tokens 两条（capability=`session_takeover_ledger`/`takeover_pending_gate`）+ depgraph 设计节点 16062834（gate）/16062835（ledger）。

## 4. 设计决策（红蓝要点）

1. **注册面修正**：任务书原文"注册进 .pre-commit-config.yaml"，实勘该文件是 pre-commit framework 面（裸 git commit 用，本仓禁裸 commit）；GateSpec 工厂形态的权威注册面=`in_process_gate_registry.yaml`（gate_auto_registrar fail-closed 装载，landing 侧"门禁一套不裁"天然继承）。已照后者接线，功能等价且覆盖队列落地通道。
2. **命中面=具体文件集合**（非 impacted_modules 目录前缀）：目录级会误伤同域无关文件；具体文件重叠才是真冲突信号。
3. **fail-open 边界**：台账缺失/损坏行/模块 import 失败=显化设施失效 → 放行+warning（同 ast 类 gate 契约）；命中即 fail-closed。
4. **600s refresh 节流**：判死钩子在 `list_active` 热路径，宽限窗（15min）内每次调用都命中 expired——无节流会反复 git status/staging rglob 重 IO；窗内原样返回，台账粒度 10min 对接管语义足够。
5. **辅助证据降级**：pid 存活/心跳年龄取不到=null 不阻断；worktree 非 git 目录 dirty=-1 记 `git_status_unavailable`。
6. **净零声明**：新建能力（capability_lookup 'takeover' 零命中在案），无替代/合并旧条目；豁免通道无。

## 5. 测试证据

`tests/governance/test_session_takeover_ledger.py`（tmp_path 假 root，零真库；PID/git 判定 monkeypatch 确定性化）：

```
10 passed in 0.79s  （--basetemp=.runtime/tmp/t1/）
  态1 scan：判死命中/活会话跳过/logical 豁免；幂等（同 sid 单行，窗内节流原样返回，超窗 refresh_count+1 资源刷新）
  态2 字段：七字段齐+resources 五键+held 绝对→相对归一+ghost 心跳注记+处方五类覆盖+影响域推断精确
  态3 resolve：status=resolved+resolved_by+迁 resolved/ 恰一件+open 表清空+重复 resolve 抛 LookupError
  态4 gate：held 命中阻断（detail 含 sid/处方/--resolve）/未命中放行/空台账放行/tests/ 豁免/损坏台账 fail-open
  钩子集成：真 SessionRegistry.list_active 判死路径 → 台账条目生成（判死主流程不受影响）
  CLI 冒烟：--scan/--list/--resolve 全链
```

邻接回归：`test_gov_session_concurrency.py`+`test_generate_gate_registry.py`+`test_commit_gate_registry.py` = **70 passed**。
实仓 L1 冒烟：`--scan` 真册（7 会话全活跃/logical）→ `no dead sessions`（零误报）。
门禁装载冒烟：`auto_register_gates` 实载 TAKEOVER-PENDING priority=160。

## 6. 处方速查（下一个 AI 接管动线）

```
python scripts/governance/session_takeover_ledger.py --list     # 看谁死了、留下什么、怎么处理
# 按条目 prescription 处置（release_files / merge|abort worktree / promote staging / requeue 死袋 / 清 ghost 心跳）
python scripts/governance/session_takeover_ledger.py --resolve <sid> --by <你的sid> --note <结论>
# 若 commit 被 TAKEOVER-PENDING 拦截：错误消息里就是处方，处置+resolve 后自动放行
```

## 7. 存量条目刷新出口（维护七班 P2，2026-10-14 追加）

**病根（实测，非推断）**：`--scan` 的候选集只有两个来源——注册表判死会话（`scan_dead_sessions`）
与在盘孤儿资源（`_scan_orphan_resources`）。一条 open 条目一旦走到"会话已从注册表除名 **且**
资源面已被清完"，就再不进任何候选集，于是**永久带着立案当天的旧资源数挂着 open**。
现场＝`st-deadclean-20261013`：处方三项（claim 3 件／车道 1 棵／心跳 1 件）23:4x 复核均已归零，
条目仍报 `held=3 worktrees=1 heartbeat=1`，L3 门禁按 `entry_match_surface` 逐件挡道，
把维护六班的存证钩子袋（q-…-0011）挡成死信；当时只能人工 `--resolve` 绕行。

**出口（本文件 §7 与代码 docstring 同源）**：`--refresh [SID] [--execute]`
1. 逐条（或指定一条）用 L1 同一把尺 `collect_resources` 重取五类资源面并写回；
   写回带 `force=True` 越 600s 节流窗——那是判死钩子热路径的 IO 防护，不是给人工刷新设的闸；
   `death_evidence` 沿用立案原文（开账条目必须自带"当时三证读数"，刷新不许改写历史证据）；
2. **只有五类全零**（held／worktrees／staging／bags／heartbeat）才走 `resolve_entry`
   同一通道收口，注记固定为"刷新出口复测：五类资源面全零，无待接管项"；
   有任何残留（**含死袋**——死袋要四态分诊不许静默消失）一律留 open，只把数字缩到实测面；
3. 默认 **dry-run 只报数不动盘**（与 blob_gc `--archive`、`--sweep-absorbed` 同哲学），
   `--execute` 才写。

**判别力（在册测试，两条突变实测各红）**：
`tests/gov/governance/test_session_takeover_ledger.py` 新增 6 支（dry-run 零动盘／
归零支非 execute 不收口／残留即不收口／**窗内刷新必须缩数**／单条 SID／未知 SID 显式 LookupError）。
- 突变 1（写账去掉 `force=True`）→ `test_refresh_bypasses_throttle_window_...` 红，
  读数 `{'held': 1, 'worktrees': 1, 'staging': 2, 'bags': 1, 'heartbeat': 2}` ＝旧数没缩掉＝挡道面还在；
- 突变 2（`all(v==0)` 改成 `any(v==0)`）→ 残留支被误收口，红于 `refreshed != resolved_all_clear`；
- 复原后 6 passed（sha `fbc5fbb8d54b7adecba8f5d5` 逐次核回）。
