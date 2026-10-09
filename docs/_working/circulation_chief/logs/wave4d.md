---
ttl: task_bound
title: wave4-D 车道日志（V5 护栏+V4 僵尸清理+V1 metaq 定性）
session: st-ffchief-20261001
date: 2026-10-01
status: done
---

# wave4-D 车道日志（V5 register 频率护栏 + V4 僵尸守护清理 + V1 metaq ps1 定性）

> 会话=st-ffchief-20261001｜车道=wave4-D｜日期=2026-10-01
> 输入=skeleton/K_governance_gates/SEG_K.md §V + automation_panorama.md §3（V1/V2/V3/V5 同根收敛）
> 自裁授权=Owner 总包令（堵死→登记跳过，禁提问禁停）；主区直改经 `--allow-non-worktree --enqueue`

## 冷启动

- Python 3.12.8 PATH 修正 + usercustomize 在岗；`ZephyrAlpha_ProcessReaper` 在岗（scanned=25 killed=0）。
- 4 目标文件 lock_files.py claim 全成（session_concurrency.py / test_session_concurrency.py / register_metaq_audit_reconcile_task.ps1 / wave4d.md）。

## 任务1 V5 治本：register() 频率护栏（已落地）

**病灶**：`src/zephyr/security/access_control/session_concurrency.py` register() 无频率护栏——
keeper 循环无限重 register 刷新 last_activity，架空 #ARCH-HEARTBEAT-002 daemon idle 自退
（三类伪造同根）。

**设计**（先读 heartbeat_daemon + session_worktree 调用面后定）：
- 调用面实证：heartbeat_daemon 只调 `heartbeat()`（不 register）；register 面=session_worktree_start
  （src :2832 与 scripts :220，均 start 一次）、session_claim_start、reconcile_worker（sid 含 pid 唯一）。
- 窗值 `_REREGISTER_MIN_INTERVAL_SECONDS = _ACTIVITY_IDLE_TIMEOUT_SECONDS + 2*30s = 1860s`：
  daemon idle 检查 30s 粒度必然先于任何放行的重注册——守护在位时死条目通道结构性关闭，窗守得住。
- **降级执行语义**（红蓝修正：初版"拒绝+原样返回"打断了 test_session_worktree 共享 fixture 测试链
  与生产同 sid 部分失败重跑的状态重建依赖；HEAD 基线对照实证 5 败均由初版引入，降级模式后 89 全过）：
  状态字段（pid/held_files/task_files/breaking/deps/logical）按实参重建 + 四时间锚
  （start_time/last_heartbeat/last_activity/last_register_ts）全部冻结 + warning + JSONL 审计。
  keeper 得不到任何活性续期，窗自上次 FULL register 起算不被刷延长。
- 放行通道：①logical 豁免（请求参或既有条目任一）——总包/chief 周期 re-register 是 W-29 认可
  活性信号；既有条目 logical=True 重建时**继承**（防 mark_logical 随整体重建静默丢标——守护
  idle 豁免随之失效的隐性破坏）；②死条目放行=真实重启（守护不在位时 last_activity 无消费者）。
- 新字段 `SessionInfo.last_register_ts`（独立于 last_activity：claim/register_dependency 是合法
  治理操作不缩窄 register 窗；旧条目缺省 0.0=无锚放行）。审计=`.runtime/session_registry_audit/
  register_rate_guard.jsonl`（独立目录防分片 glob 误吞；IO 成本不高于原 register 分片双写）。

**测试**（tests/session/test_session_concurrency.py 增 8 例，`--basetemp=.runtime/tmp/wave4d/`）：
正常首注/超频降级四锚冻结+状态重建/审计留痕/logical 请求参豁免/既有条目豁免/窗满放行/死条目放行/
窗值对齐 idle 上限。结果：本文件 78 过；邻接套件 221 过（cross_commit/heartbeat_daemon×2/reconcile_async）、
session_worktree 89 过（基线对照）、cli/async/audit_wrapper 25 过。
m12b 跨进程 register 竞态测试子进程改 5-sid 轮转（护栏后同 sid 窗内重注册被降级，保留跨片竞态覆盖）。

## 任务2 V4 僵尸守护清理（已执行）

**杀前核证**（psutil 扫 + 逐个读 session_registry 分片）：
- 实杀 6 守护（任务书 st-menu-w3h "×3" 实为 ×2 在跑）：5724/28240=st-menu-w3h-20260930
  （idle 5.99h，**仍持 27 个 held_files** 含 module_translation_registry.yaml——阻塞实证）、
  32752=st-circ-g2-20260930（idle 9.23h）、37440=st-menu-w3harvest-20260930（idle 10.51h）、
  21316(nohup wrapper)/23344=st-circ-integ-20261001（idle 3.66h）。
- **偏差自裁**：四 lane 注册表 `logical=True`（任务书预期"非 logical"）——核证其为残留伪造标：
  四 lane worktree 分支已不在 git 分支表（lane 完结清理），idle 3.7~10.5h，W-29 豁免被完结 lane
  遗留 flag 架空=本战役打击的伪造族。总包令点名杀之，据实执行并留痕。杀后心跳 90s 内过期，
  条目自死、held_files 自动释放（st-menu-w3h 27 件 claim 随之解除）。
- **保护区零接触**：17396=st-chief7-20260928、21520=st-ffchief-20261001 杀前杀后均 alive；
  st-fullscore-20260930 无在跑守护（其 pid 文件本就是死 pid，按"只删死 pid"规则清除）。
- 扫描中 3 个 sid=None 守护（15:17 创建）=本车道 pytest 派生的测试残留，已在扫描间隔自退
  （锚点丢失自退生效），无需处理。

**pid 文件清扫**（.runtime/locks/heartbeat_*.pid，只删 pid 已死）：删 129 个死 pid 文件，
保留 8 个活 pid（st-c9-f115/finalz/tzday、st-chief7、st-chiefzc-docs、st-finaldel-final2、
st-p2-cens、st-p9-fixchart）。报告=.runtime/tmp/wave4d/v4_report.json。

## 任务3 V1 裁定落地：metaq ps1 定性=读侧审计扫描（已修正+豁免登记）

**定性证据**：check_meta_question_audit_reconcile.py [INVARIANTS] "全程零写（PG read_only 连接 +
JSONL 只读流式解析）"，差集仅报告不回写——**非 §9.3 reconciler 语义**（reconciler=自动修复写回）。
任务书两分支取"读侧审计扫描"支：修正自相矛盾注释 + 豁免登记留痕，**不停用计划任务**。

**修正内容**（register_metaq_audit_reconcile_task.ps1，纯 ASCII 复核 0 非 ASCII 字节）：
- :27 "reconciler is read-only" → "audit scan is read-only"（词错事实对——wave4-D 修正记录在头注）；
- :79 任务描述 "audit dual-track reconcile" → "dual-track audit scan ... NOT a reconciler, 9.3 N/A"；
- 新增"Exemption registration"头注块：零写证据（read_only=True + JSONL 只读流）+ §9.3 适用边界 +
  先例（register_gate_fulltree_audit_task.ps1:17 同款豁免语）——本头注即常设豁免登记
  （resource_profile_registry.yaml 由 ps1 族生成，禁手编，豁免随生成链传导）。
- 幂等重注册同步在跑任务描述（Set-ScheduledTask in-place）：state=Ready，next=10/02 03:50。
- 保留面：脚本文件名/任务名/报告日志名含 "reconcile" 为表标识符不改动（改名破坏在注册任务与生成册映射）。

## 遗留与移交

- register 降级路径的审计 JSONL 无消费方告警接线（审计留痕面已足，告警面归 keeper 治理后续件）。
- `logical` flag 的授予面（mark_logical 无门槛）是 W-29 遗留扩权面：本次四僵尸 lane 的残留
  logical=True 即其代价实证；建议后续件给 mark_logical 加总包/chief 形态核验（未动，超车道边界）。
- test_session_worktree_cli 在脏工作区偶发 conftest tracked-write guard teardown 报警（他测写
  热册 capability_canonical_file_registry.yaml / rule_catalog_registry.yaml——非本车道改动，
  594 主区漂移下他车道并发写入所致，未处置）。
- 提交：git_commit.py --enqueue 队列落地（qid 见提交回执）。
