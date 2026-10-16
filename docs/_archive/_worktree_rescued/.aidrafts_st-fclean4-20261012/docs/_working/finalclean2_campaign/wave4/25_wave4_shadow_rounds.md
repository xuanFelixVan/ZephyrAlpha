---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: 本班两批影子旁观轮读数入册且与波三 r1-r5 口径可对账；day2 首轮另册 26_
session: st-fclean4-20261012
lane: wave4-main
role: 影子旁观观测账（主责在周期班，本班只记录）
---

# 终清波四·影子旁观轮账（r6＝10-12 22:59 本地；day2 首轮另册 `26_`）

> 为什么另起本册而不就地改写 `23_` §4：`23_` 已随 q-0003 落地，同会话后袋对同件**只允许字节超集**
> （在册坑：同件复投非超集＝三方真冲突或静默吞前袋）。故本班把实跑数放在本册，`23_` §4 那行占位按原样留档。

## 1. r6 轮（day1 附加轮之一，另一为 r7，见 §4b）

| 字段 | 实测 |
|---|---|
| 本地时刻 / UTC | 2026-10-12 22:59:40 ／ 14:59:40Z |
| mode | `shadow` |
| scanned | **483**（波三 r1-r4＝466，r5＝475） |
| would_n（`len(actions)`） | **317**（r5＝296） |
| errors / suspected / merge_warned | 0 ／ 0 ／ 0 |
| skipped | 166 |
| 命中在飞 | **0**（would-set ∩ 在册分片 5 片 ＝ ∅） |
| 与 r5 差集 | new＝**21**，gone＝**0**（r5 ⊂ r6） |
| 进程退出码 | 4 ＝ 该件 `# [ERROR_CONTRACT]` 自述"有嫌疑/告警→exit 4；干净→exit 0" ⇒ **would 非空即为 4，不是失败** |
| 原始出件 | `.runtime/tmp/st-fclean4-20261012/out/shadow_day1_r6.json`（33,247 B） |

四件合格判据（`mode=shadow ∧ errors=0 ∧ suspected=0 ∧ 命中在飞=0`）**齐** ⇒ 记为 day1 的附加合格轮，
**不另计新日**（跨日才计 day2；10-12 已有 r1-r5，合格日仍＝1）。

## 2. new=21 的构成（sid 级，r5 之后新入点名集）

`AI-PROBE-001`、`st-cli-1`、`st-axisunify-flash-20261005`、`st-btfix-20261005`、`st-deadletter-cure-20261003`、
`st-fa-altint-20261005`、`st-fb-indeng-20261005`、`st-fc-census2-20261005`、`st-fd-srcline-20261005`、
`st-fg-srcline1-20261005`、`st-map9-f7-20261005`、`st-sA-surgery-20261003`、`st-sB-surgery-20261003`、
`st-sentinel-census-20261005`、`st-tclose-bmsurg-20261004`、`st-tclose-cardfix-20261004`、
`st-tclose-infracure2-20261005`、`st-tdm-mount-flash-20261003`、`st-vm12f1-20261003`、`st-vmount-sop-20261003`、`st-wm1-cutover-20261003`

- 全部是 **2026-10-03～10-05 的旧车道**＋两枚探针名（`AI-PROBE-001`、`st-cli-1`，实为 `.worktrees/st-maint2-20261011/.aidrafts/` 下的嵌套注册面）。
  ⇒ 增长机制＝**旧死车道陆续被枚举进来**（不是当日新增事故），与波三"四轮点名集全等"并不矛盾（那是同日窗口内幂等）。
- ⚑ **一枚在册脏件被点名**：would-set 里有字面为 `--help` 的条目。实物＝`.runtime/sessions/--help/`，
  **目录 ctime=2026-09-19 02:47**、其 `heartbeat.jsonl` 最后写于今日 15:45（均早于本班全部动作）
  ⇒ 有在册工具把 `--help` 当成 session_id 注册过并留下心跳面（波二"--help 即执行主逻辑"那族事故的化石）。
  **转正后归档器会把这枚 nonsense 条目列入处置对象** ⇒ 列交维护三班（`24_` 卡 A 追加项：枚举面缺 sid 字面校验）。
  本班 23:0x 曾自跑一次 `git_commit.py --help`（红线动作），其零副作用三点证明在 `99_` §四-6——该脏件不是本班所造。

## 3. 本班两条"不可用作交叉证"的申报（防后班误读）

1. **不能用本点名集给本班 M2 退场背书**：本班 10 个退场 sid 在 **r5 与 r6 两轮里都不存在**（r5⊂r6、gone=0）
   ⇒ 归档器枚举面与 `.aidrafts` 工作树面**覆盖面对不上**；两把尺不同面时不得互证。
2. **不能用 r5→r6 的 would_n 增长反推"退场无效"**：本班退场发生在 22:20-22:21，r6 在 22:59，
   而 would-set 不含这些 sid（见上条），增长 21 项全是 10-03～10-05 旧车道，与本班处置面无交集。

## 4b. r7/r8 两轮（跨日界实录：r7 仍属 day1，r8 才是 day2 首轮）

| 轮 | 本地时刻 | UTC | scanned | would_n | errors | suspected | skipped | 与上轮差集 | 命中在飞 | 计日 |
|---|---|---|---|---|---|---|---|---|---|---|
| r7 | 10-12 **23:58:13** | 15:58:13Z | 481 | 320 | 0 | 0 | 161 | new=4／gone=1（vs r6） | 0 | **day1**（未跨本地零点） |
| r8 | 10-13 **00:01:06** | 16:01:08Z | 481 | 320 | 0 | 0 | 161 | new=0／gone=0（vs r7） | 0 | **day2 首轮＝合格** |

- ⚑ **为什么必须记这条**：本班起手按"10-13 跑 day2"计划，23:58 那轮看似"新一轮"其实仍在 day1（本地钟与 UTC 钟差 8 小时，
  在册教训"心跳/时间门前先 `date` 实测"再次适用）。若把 r7 记作 day2，合格日就会**提前一天**虚增——转正日也会被推错。
- r8 四件判据齐（`mode=shadow ∧ errors=0 ∧ suspected=0 ∧ 命中在飞=0`）⇒ **day2 合格**，
  合格日累计＝**2**（10-12、10-13）；按"满 7 个自然日零异常"推算最早呈"转正＋注册"一次批的日期仍为 **2026-10-19**。
- r7 的 `gone=1`（vs r6）＝点名集自身在收敛，非本班动作所致：r6→r7 隔 59 分钟，其间他班有 4 笔落地；
  本班退场的 10 个 sid 全程不在点名集（见 §3-1），故不能用这两轮给 M2 背书。
- 原始出件：`shadow_day2_r7.json`／`shadow_day2_r8.json`（两份均在 `.runtime/tmp/st-fclean4-20261012/out/`）。
- 复命时在册活性面（00:01 实测分片 9 片）：`st-deadcure3b-chief-20261011`、`st-examrun-20261012`、`st-fclean4-20261012`（本班）、
  `st-gpux2-20261011`、`st-gpux3-20261012`、`st-maint3-20261011`、`st-minedig2-20261012`、`st-mineloop2-20261012`、`st-statsgov-20261012`
  ⇒ 其中 `deadcure3b-chief`/`gpux3`/`maint3`/`statsgov` 的分片在 22:20 那批之后曾消失（mutating 死判收割，`21_` §3 已自报），
  此刻又各自动了新分片＝**它们的主人在 00:01 仍在施工**，本班"态④不动"的判断继续成立。



## 5. 复算（只读）

```bash
cd /d/ZephyrAlpha
python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json > /tmp/r.json   # 禁加 --execute
python - <<'PY'
import json,pathlib
r6=json.loads(pathlib.Path('D:/ZephyrAlpha/.runtime/tmp/st-fclean4-20261012/out/shadow_day1_r6.json').read_text(encoding='utf-8'))
r5=json.loads(pathlib.Path('D:/ZephyrAlpha/.runtime/quarantine/fclean3_safety/shadow_rounds/shadow_round5.json').read_text(encoding='utf-8'))
a=set(r6['actions']); b=set(r5['actions'])
print('scanned',r6['scanned'],'would',len(a),'errors',len(r6['errors']),'suspected',len(r6['suspected']))
print('new',len(a-b),'gone',len(b-a))
print('sessions dirs residue of my retired lanes:',[p.name for p in pathlib.Path('D:/ZephyrAlpha/.runtime/sessions').iterdir() if p.is_dir() and any(s in p.name for s in ('nightmine','regsolo','dexp','final4','fullflow2','finalclean2','deadcure3-','backfix-patrol'))])
PY
```

> 附注：本班退场的 10 棵在 `.runtime/sessions/` 各留 1 枚目录（9 枚已被 `cleanup_heartbeat_file` 清空、
> 1 枚仍含 `heartbeat.jsonl` 20,813 B）⇒ 归档通道 teardown **只删心跳件不删目录**；该面共 489 枚目录，
> 即 `scanned` 的枚举源。列维护三班簿记项（`24_` 卡 A）。
