---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
gate_selfdoc: GIT-DANGEROUS  # 本册引用在册函数/门禁原话（GATE-SELFDOC 豁免：违规行 1 处 ≤ 上限 10），非本班下达危险命令
completes_when: 波四各袋在 dev 复验落地＋统筹验收本册；day2-day7 影子由周期班续跑满 7 日零异常后转正
---
# 终清波四·收班册 99_delivery（sid=st-fclean4-20261012，2026-10-13 00:1x）

> 令卡＝Owner 2026-10-12 夜【终清波四 st-fclean4-20261012】大面处置执行令；批复＝统筹夜窗三裁（取证落点改 git 永久区／M5 撤 14 天提法＋加"先修清理器"硬前置／暂存面禁 blanket 复位）。
> 北极星承接＝波三把"附属物每面有主有据"推到 101/102 面；本班职责＝**把已批的大面真正处置掉**，并给下一班留下可对账的面。

## 一、五件目标终态（只认 HEAD，逐件给凭据）

| 目标 | 终态 | 凭据（落地面或实测面） |
|---|---|---|
| M2 工作树退场 | **达（按实测分母，非按菜单字母）**：可处置全集 17 棵（现面 18 减本班自身），其中**退场 10 棵**、6 棵判态④在飞、1 棵令卡排除（mineloop）。回收 **3,082,995,081 B＝2.87 GiB／203,440 件**；`git worktree list` 40→**30**，`.git/worktrees`→**29**（余 1 枚属存活单胞胎），`branch -d` 10/10 全过＝零真 ahead | `wave4/20_wave4_m2_dossier.md`（决策表）＋`wave4/21_wave4_m2_receipts.md`（回执＋副作用账）；5 枚 retire patch 在 `.runtime/quarantine/*-retire-20261012T14*.patch` |
| M2 闸① 不可再生字节 | **达＋1 件如实受阻**：318 件非缓存独有面逐件 sha 入册；本班退场 10 棵的 29 件副本**退场后复验 29/29 sha 全等、anomalies=0**；5 枚 patch 共 346 件全量对 dev 复查＝**仅 1 件 dev 查无**（`regsolo_campaign/99_delivery.md`，`ARCH-383` 号真悬空，波三判门拦得对本班复核同判；其字节现有**三处**：波三存证面／本班保护区副本／retire patch） | `wave4/evidence/aidrafts_fingerprint.yaml`（机生）＋`.runtime/quarantine/fclean4_safety/aidrafts_unique/MANIFEST.jsonl`（29 行） |
| M3-Q1 watchdog 保留窗 | **未落码（两条硬事实决定）**：①30 无任何配置面，属主通道＝模块自身面；②该文件此刻被维护三班暂存 +99/−6（内容是池面回退方向分量，与保留窗无关）＝HELD-OVERLAP；③⚑ **drift 文件真实寿命今天已是 7 天而非 30 天**（清理器声明制直通，实测 1,502 条），故清理器口径修落地前 Q1 是空转改子。本班产出＝即用预备改子＋分类输入册＋两条用例名 | `wave4/22_wave4_m3_dossier.md` §1-§2；分类册 `.runtime/quarantine/fclean4_dedup/class_summary.jsonl`（REDUNDANT 486 枚/13,588,772 B） |
| M3-Q2 内容寻址去重 | **达＝原型跑通并给出负结果**：原型 149 件/2,993,885 B 全等归档→放量 405 件/12,971,204 B→测得 135 枚空壳＋约 398 处悬空空子目录→修复 135→**整批回滚**；终态复验＝审计表 **8,072 行全部在位且 sha 全等（absent=0）**、空壳 0、悬空子目录回落到存量 2、回收站 0 件。硬算术：drift 目录 **89.3% 是单文件目录**（5,789/6,480）⇒"按文件抽取"结构上不成立，放量须按**整枚目录**且先修 tamper 清单缺陷 | `wave4/22_` §3-§4；`out/q2_prototype_report.json`／`q2_scale_report.json`／`q2_repair_report.json`／`q2_rollback_report.json`；索引 `.runtime/quarantine/fclean4_dedup/index.jsonl`（含 554 archived＋135 restored＋419 rolled_back 全留痕） |
| 已裁项核销 M1/M5/M12 | **达（M5 按批复改口径）**：M1＝22 枚复验 21 在盘（14 sha 全等）／1 枚自然释放（`backup.lock`，清理器 0 命中）＋⚑更正波三"无声吃掉"（`guard_remove` `ops_guard.py:812` 逐件落审计，真限制是审计面只留 4.33 天）＋查出**第 4 枚 TTL 暴露件** `takeover_ledger.jsonl.tmp.23876`（令卡与波三清单均未点名）；M5＝撤"≥14 天观测窗"（在册 0 命中，正对照有效），改报实测深度 4.22d／0.21d＋**两把上限闸**（`audit_jsonl_writer.py:57/:62` 与轮转段名 `.jsonl.N` 不被清理器豁免 ⇒ 深度硬顶 7 天以下）；M12＝**跨日实跑**：10-12 为 day1（波三 r1-r5＋本班 r6/r7），本班 10-13 **00:01:06** 跑 r8＝day2 首轮合格（scanned=481／would=320／errors=suspected=命中在飞=0）⇒ 合格日 2，最早转正仍 **2026-10-19**，计划任务实测仍未注册（合规）；⚑ 23:58 那轮（r7）本地未跨零点，**记 day1 不记 day2** | `wave4/23_wave4_status_checkoff_and_shadow.md`（核销正文）＋`25_wave4_shadow_rounds.md`（r6 旁观轮：would_n=317，new=21／gone=0，四件齐 PASS；exit 4 语义已读 `[ERROR_CONTRACT]` 定死） |

## 二、袋账（只认 `git show dev:`／`git log -- <path>`，不认工棚自证）

| 袋 | 内容 | 终态 |
|---|---|---|
| q-…-0001 | `20_` 施工前案卷＋账册波四节（纯追加） | **done**，landed_id=`80fbf64916d6`；落地后 `git show --name-only` 复验＝袋内 2 件、dev 账册 637 行/19 节，**波三第十四节与本班第十五节同时在场**（主区那枚"删第十四节"的暂存回退弹未被本班吸收） |
| q-…-0002 | `21_` 退场回执＋`evidence/aidrafts_fingerprint.yaml` | **dead**：死因＝`GATE-PRECOMMIT-RUN` → hook `gate-detect-git-dangerous` 在 `21_:60` 扫到字面 `git reset --hard`（那是**原文引用在册函数提示语**，非本班下达命令）。处置＝按根宪法 GATE-SELFDOC 给该册加 frontmatter `gate_selfdoc: GIT-DANGEROUS`（违规行 1 ≤ 上限 10），**证据正文一字未改**；两件随 q-0004 重投 |
| q-…-0003 | `22_` M3＋`23_` 核销＋`24_` 交接＋5 份车道案卷入册（8 件） | **done**，landed_id=`a9e2a0d6a6ff`；dev 面 `git ls-tree` 复验 8 件全在（含 `wave4/lanes/` 5 份 1,039 行） |
| q-…-0004 | 同上五件（`21_` 已加 GATE-SELFDOC 豁免标记重投） | **dead**：同一钩子这次指到 `99_:25` 的另一处引用原话（`git reset --hard`）——
  证明"改一处不等于改一类"；处置＝给 `99_` 也加 frontmatter 豁免标记（违规行 1≤10），并按"重投三步"在**投前用真钩子跑一遍暂存面**证明能绿：
  `python -m pre_commit run gate-detect-git-dangerous --files <五件>` → `检测危险 git 命令 ... Passed`（本班 00:0x 实跑） |
| q-…-0005 | 同五件（`99_` 亦带豁免标记）＋`25_` 补 day2 轮实跑数 | 待落地后由 §七末笔以 `git show dev:<path>` 复验回填 |

⚑ 投袋工法留痕（后班直接用）：车道内投主区队列必须 `cd 车道 && python scripts/commit_queue.py --queue-root <主区队列> enqueue --worktree-root <车道>`——
不带 `--queue-root` 会落进车道影子根（在册坑，本班按 `--help` 递送的指路现场复验）；`git_commit.py` 在车道内直跑会因 `wt=project_root` 判 SESSION-REQUIRED 未注册。
新 `.md`/`.yaml` 一律先 `batch_creation_tokens.py`（本班 v431/v432/v433 三批 11 条），跑完必把车道被打脏的投影册按 `git show dev:` 字节复位且**不入任何袋**。

## 三、净零申报

- **新建 git 永久面＝0**：未新建门禁／规则／注册表／第二套判据；波四册全部进 `finalclean2_campaign/wave4/`（沿用波三 `waveN/`＋`waveN/lanes/` 惯例），账册进既有 `00_ledger.md`（纯追加，删除行=0 已证）。
- **新建运行态面＝2 枚（如实报，均有具名消费者）**：
  ① `.runtime/quarantine/fclean4_safety/aidrafts_unique/`（29 件＋MANIFEST）——消费者＝闸① 存证与后班失配核查；
  ② `.runtime/quarantine/fclean4_dedup/`（`index.jsonl` 去重全留痕＋`class_summary.jsonl` REDUNDANT 分类册）——消费者＝Q1 属主车道的分类输入（`24_` 卡 A1）。
  二者都在 ops_guard 声明的取证保护区内、都走 `.jsonl` 命名（清理器豁免）。
- **判据与阈值零改动**：本班未动任何保留天数、未动任何门、未动 `backup_count`/`max_bytes`、未动 watchdog 常量（撞件即撤，`22_` §1-②）。
- 悬挂账（不自销）：①`reconciliation_registry.py` 与 `worktree_drift_watchdog.py` 两处他班在途面，本班只出复验清单与预备改子；
  ②5 棵 needs_rescue 车道的缓存类未跟踪件只活在 `.runtime/tmp/rescue/`（24h TTL），本班判其可再生故不永久留存——若后班判反，须在窗内搬家（`24_` 卡 A4）。

## 四、⚑ 本班自犯七起（全留案，无一遮蔽）

1. **前置证明与动手隔 45 分钟未复测**：21:35 实测"13 片全未过 TTL ⇒ mutating 死判零接管零收割"，执行在 22:20；
   执行窗内 8 会话分片被设计内 GC 收割（含本班自身）。后果实测＝树与字节零损失、接管台账执行窗 0 新增行（本班 10 目标的立案行由在册 `orphan_resources` 扫描在 2 小时前独立开出，`death_evidence.reason` 原文可查）；
   违反的是在册"运行态断言同分钟复测"，不是判据本身。（`21_` §3）
2. **放量批用 8 分钟前的字节快照算配额** ⇒ "每目录至少留 1 文件"被架空，产出 135 枚无文件空壳。（`22_` §6-1）
3. **自检尺是坏的**：`len(list(dir.rglob('*')))==0` 判空壳把**空子目录**也计入 ⇒ 报出"0 空壳"假绿；按文件口径复测＝135。（`22_` §6-2）
4. **guard_recycle 未带会话署名** ⇒ 149 条归档审计行 `session_id="ops-guard-unknown"`。（`22_` §6-3、§4-2）
5. **曾把 5 枚车道运行态件双写进 `docs/_working`**（该面在册 DCR 禁 `.json`，且运行态件不该由本班定真源）→ 当窗自纠撤回为"指纹入 git＋字节入保护区"。（`21_` §4）
6. **误跑在册工具 `--help` 一次**（红线明文禁止的形态，本班在 `20_` §0 自己写过这条红线）。零副作用三点证明（非空口）：
   ①`git_commit.py` `--session` 为 `required=True`，`--help` 在 `parse_args()` 内 SystemExit，其后才是 preflight/锁/暂存；
   ②`.runtime/gate_audit/*.jsonl` 在误跑后 3 分钟内 0 写入；
   ③旁观轮里那个 `--help` 脏条目的实物 `.runtime/sessions/--help/` **ctime=2026-09-19 02:47**（早于本班 23 天），其 heartbeat 最后写于今日 15:45（早于本班误跑 7 小时）⇒ 该脏件不是本班所造，但它是**另一条在册缺陷**（有工具把 `--help` 当 session_id 注册并留心跳，转正后会被归档器点名）。

7. **重投时只修被点名的那一册、没扫全袋** ⇒ q-0004 第二次死在同一类问题上（`99_:25` 另一处引用原话）。
   正解补记（在册"重投三步脚本化"）：投前先对**整批文件**跑真钩子 `python -m pre_commit run gate-detect-git-dangerous --files ...`，
   绿了再走正门；本班 q-0005 已照此跑过（Passed）。教训形态＝"改一处"不等于"改一类"，与 §四-3 的坏尺同族。

## 五、移交与承接（详单在 `24_`）

- **→ 维护三班**（卡 A1-A6）：Q1 即用预备改子＋分类输入册；清理器吃保护面那版（主区工作区面 +33/−1）请**尽快落袋**，本班已备好两条红证用例待其落地复跑；tamper 清单与自家 sweep 不同步（234 条假警）；rescue 面 24h TTL；guard_recycle 署名回落。
- **→ 周期班／影子续跑班**（卡 B）：day1＝1 合格日，最早转正 2026-10-19；跨轮口径固定 `would_n＋new/gone`；r6 已入册，day2 首轮见 `23_` §4b。
- **→ Owner／统筹**（卡 C1-C4）：`99_delivery.md` 落册三选一授权；取证窗要动哪把闸（只提 `backup_count` 长不出 14 天）；波三 Owner 面维持；Q2 负结果与"按整枚目录去重"的后续路线。

## 六、复算入口（全部只读；本班逐条自跑过）

```bash
git -C /d/ZephyrAlpha worktree list | wc -l                         # 期望 30
ls /d/ZephyrAlpha/.aidrafts | grep -c '^st-'                         # 期望 9
git -C /d/ZephyrAlpha log --oneline -- docs/_working/finalclean2_campaign/wave4/
git -C /d/ZephyrAlpha show dev:docs/_working/finalclean2_campaign/00_ledger.md | wc -l   # 637＋后续追加
ls /d/ZephyrAlpha/.runtime/quarantine/*-retire-20261012T14*.patch | wc -l                 # 5
python - <<'PY'
import json,hashlib,pathlib
M=pathlib.Path('D:/ZephyrAlpha/.runtime/quarantine/fclean4_safety/aidrafts_unique')
rows=[json.loads(l) for l in (M/'MANIFEST.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
ok=sum(1 for r in rows if (M.parent/'aidrafts_unique'/r['sid']/r['rel']).exists() and hashlib.sha256((M.parent/'aidrafts_unique'/r['sid']/r['rel']).read_bytes()).hexdigest()==r['sha256'])
print('闸① 保护区存证',len(rows),'sha 复验通过',ok)
PY
python - <<'PY'
import json,pathlib
p=pathlib.Path('D:/ZephyrAlpha/.runtime/audit/worktree_drift_watchdog.jsonl')
rows=[json.loads(l) for l in p.read_text(encoding='utf-8',errors='replace').splitlines() if l.strip()]
from collections import Counter
print(Counter(str(r.get('verdict')) for r in rows).most_common(7))
PY
```

## 七、末笔回填（收班时写，落地后只认 HEAD）

- 影子 day2 首轮＝已跑并回填 `25_wave4_shadow_rounds.md` §4b（r7 本地 23:58＝day1、r8 本地 00:01＝day2 合格轮）；周期班后续轮次接续 r9 起编号。
- 各袋终态＝q-0001/0003 已 `git show dev:` 复验（见 §二）；其余袋**未复验不称完成**，复验入口：`git ls-tree -r --name-only dev | grep wave4`（期望含 20/21/22/23/24/25/30/99 与 evidence/、lanes/）。
- 本班 claim 释放与车道归档＝末笔执行（`git_commit.py --release-only` 后按 `session_worktree.py archive --execute` 自归档；
  ⚑ 归档只清 `.aidrafts` 一面，`session/<sid>` 壳分支与 `.runtime/sessions/<sid>` 目录需按波三 `30_` 那条口径手工复核）。
