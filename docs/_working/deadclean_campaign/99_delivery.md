---
ttl: task_bound
completes_when: 本班四裁体＋落地面复验＋ghost 四袋判定行在册；放量与死锁立法已交维护六班/新死信班
---
# 死信清零战役·收班册 99_delivery（sid=st-deadclean-20261013，2026-10-13 夜）

令据＝Owner 2026-10-13 派工令 v2＋四道裁（50 袋先行／maint4-5 交我判／段三立法先落袋／九面基线三处纠偏采信）；
追加＝统筹 21:3x 裁定（先复验 0010/0011→跑自家 ghost 四袋判定行→干净收班；放量与死锁立法不归本班）。

## 一、终态（只认 dev 面与进程外读回）

| 项 | 终态 | 凭据 |
|---|---|---|
| 段三立法 | **全落** | 文档袋 q-…-0005→`81d5a0c6f1`（AGENTS.md＋政策册＋00_ledger）；码腿袋 q-…-0008→`561a8b08af`（commit_queue＋session_worktree）；phase2 两件→`b18b416c0c`／`5b47263d9b` |
| dev 面六判据复验 | 达 | `_RECURRENCE_DECAY_DAYS=5`／`content_gate=10`／`--content-level=3`／`_archive_ledger_evidence=2`／`_prune_session_shell=2` 且 teardown 挂接=1／`--phase` 在位且缺省=1 时候选只含 Z（archive_only 5066 不入候选＝旧行为逐字不变） |
| 配对测试 | dev 面复跑 **6 passed**（`--basetemp` 仓外）；反向自证＝主区旧面喂 phase=2 直接 TypeError | tests/meta/scripts/test_blob_gc_phase2.py |
| 存量（唯一真清掉的一面） | dead 1599→1550（A 类 49 袋 mv 进 dead_archive_20261013，manifest 逐袋 verdict=A_LANDED＋袋体 sha＋49/49 归档位重算 sha256 全等） | `dead_archive_20261013/manifest.jsonl` |
| 裁②「8 件救」 | 达＝10 行 MANIFEST 全 verified，INDEX 两条含 rollback_cmd＋expires_at=2026-11-12 | `E:\_tomb_quarantine\st-deadclean-20261013\` |
| 自家 ghost 四袋判定行 | 机生落 `.runtime/quarantine/st-deadclean-20261013_ghost_triage/disposition.jsonl`（尺＝本班新立的 dev 面内容级门）；可归档者走正门写进 manifest | 同上＋archive_run.json |
| 两棵 maint4/maint5 车道 | **未退场**（OPS-GUARD 正当阻断，见 §三-2）；字节已由墓园＋retire patch 双兜底 | `.runtime/quarantine/st-maint4-20261013-retire-20261013T125505Z.patch`（substantive=15） |

## 二、净零申报

零新门、零新脚本、零新注册册。新建 git 面＝2 件：本战役案卷 `00_ledger.md`（已落）＋本册；新测试一件（`test_blob_gc_phase2.py`，tests/ 免 CREATE-GUARD）——它是补一条**在册虚标**：`blob_gc.py` 头册 [TESTS] 声明的 `tests/governance/test_blob_gc.py` 实测全仓零命中＝该在册工具长期无配对测试。

## 三、⚑ 本班自犯与三处已采信更正（无一遮蔽）

1. **ghost 四枚是我自己造的**：心跳守护 idle>1800s 自退 ⇒ 注册表判死 ⇒ 我首投的 0001/0002/0003/0004 被存活闸收。长班开局只开守护没开保活授权＝在册"保活正门"是给长班准备的，我漏了一道。复命四步（register pid=0＋守护 DEVNULL 不挂管道＋grant＋mark_logical）后才稳。
2. **A/B 换面备份顺序做反**：为做反向自证把主区字节盖进车道，先存的却是主区那份 ⇒ 车道立法被覆，当窗按原文重放＋复跑 13 passed 才算数。处方＝换面必先存 edited 再装 pristine，两份 sha 都打输出。
3. 更正①"0008 会先磨先死"——**错**：两袋同字节，先磨者落地、后一袋按内容寻址判 noop。统筹此前回复中"确认不干预、记账第 5 枚死信"一句随之作废。
4. 更正②"拆壳器未落"——**错**：盘码面 grep=0 是"运行面落后 HEAD"旧病，dev 面命中 2。
5. 更正③"修宪必须两袋时序"——被自然实验否证（文档袋走活跃裁定#414 的 Layer1 通道真落地），该规则不入法；议题册 0007 的 noop 不追 PG（marker 已不需要）。
6. 尺的第一版是坏的：`ls-tree` 解析把 `blob ` 前缀混进 sha 列 ⇒ "内容已在 dev"零命中假红；加正/负双对照后才可用。
7. 车道内跑 pytest 会把产物写进主区 `.runtime/tmp`（`_strip_lane_prefix` 对显式 tmp 路径同样生效）⇒ 14 支既有测试在车道集体假红。我造的两枚 `pytest_<pid>` 已 mv 进存证区未裸删；正解（仓外 `--basetemp`）已写进 §9 第 6 条。
8. 能力反查留了审计但晚于首行代码；且本域四次反查全零命中——正对照（历史 12,809 行审计中 2,833 行非零）证明尺能响 ⇒ 结论＝能力卡面对治理/队列/worktree 域失明，属观测性缺口，不在本战役自修。
9. TaskUpdate #8 报 EPERM（重命名被拒）＝**立法主体实际已落、台账未闭合**，下班销此条。

## 四、四条交接卡（下一班按此接手即可）

1. **放量 B/C/D**（新死信班）：B 类 91 袋／C 类 1,455 袋（先做 5,881 枚 1.10GB 唯一内容存证再入墓园 30 天窗）／D 类 2＋45 袋显式记"确认已失"。通道＝`dead-archive --content-level --days 0 --session <sid>`（租约闸不越，抓空窗）。render 袋 `q-20261013-st-maint5-20261013-0010`：与维护六班重渲染线协调，重渲染先落地销账则更优，requeue 非必选。
2. **车道归档↔`docs/_working/` 保护区死锁**＝统筹已定正解归维护六班第 8 条：给 OPS-GUARD 加"墓园存证已核验"查证钩子（archive 携带 MANIFEST 引用，guard 按 sha 覆盖核验后放行；禁 env 绕过、禁弱化判据、净零＝扩既有通道不立新门）。卡死面＝maint4/maint5 两棵；`session_takeover_ledger`/`reconciliation_registry` 的 merge-or-abort 也归维护六班。
3. **附属面未动**：工棚 164 车道（前五棵占 44.7 GiB=84%）／会话壳 497（108 空＋382 纯机制件可拆，拆壳器已在 dev；存量未跑）／quarantine 非 drift 65 项 3,740 件 103 MB／根散件 23 枚＋嵌套 `.runtime/.runtime` 3 件／gate_audit 1.79 GiB 轮转是否在转未核／worktree `.git/worktrees` 41 管理项 vs 磁盘 30 棵＝11 枚悬空。
4. **段二常态化未落码**：当日分诊的**自动触发腿**（事件驱动，禁 cron/Timer）＋主区暂存区无主 staged 巡检器；blob_gc phase2 旗已落但**存量未跑**（Z 6,150／D 5,066，`--phase 2 --archive` 一次即清，仍只归档不删）。
