# 死信放量三班收班册（st-deadmass3-20261014，2026-10-14 12:45 → 14:3x）

> 令据＝`00_ledger.md` §九「统筹令·放量三班开工令」（chief-coordinator-st-20261014，12:5x 发令；
> 本班 13:07:12 轮询确认落地 dev，count=1 后进场）。本册只写本班实跑过的命令与读数；
> 每条读数注明来源时刻；未跑过的不写。

## 一、终态（只认进程外读回）

- **A 批实动盘 1,205 枚，dead 1,286 → 81**（14:16:29 执行窗，单片成，verify=off）。
- `dead_archive_20261014/manifest.jsonl` 总行 **1,657**＝二班 452＋本班 1,205（行差=实动数，逐枚对拍）。
- 终值闭合三等式：`dead_delta(1,205) == archived_total(1,205) == manifest_row_delta(1,205)`；
  `1,286 − 1,205 = 81 == dead 终值`（禁按条数估——qid 集合逐枚对拍全等，foreign 行=0）。
- 红线核账尺（`deadmass3_audit_manifest.py`，14:17:07）：**RED-LINES ALL-GREEN**（§五逐条）。

## 二、基线重测（全量现测，零沿用旧数）

| 量 | 读数 | 时点 | 来源 |
|---|---|---|---|
| dead 现值 | 1,273 | 13:14 | `ls dead/q-*.json \| wc -l` |
| dead 现值 | 1,277 | 13:22 | plan 相位 |
| dead 现值 | 1,286 | 14:14 | dryrun 扫描分母 |
| 四态（在册门分态） | A 57／B 118／C 1,055／D_MIXED 41／D_LOST 2（计 1,273） | 13:19 | `deadmass_c_measure.py --sample 60` 全表重建 |
| 尺校准 | 正对照 MATCH／负对照 DIFF(对)／对表 agree=60 disagree=0 | 13:19 | 同上 stdout（`deadmass3_measure_log.txt`） |
| unlanded（解析） | 全量 1,244／白名单面 1,184 | 13:22 | plan 相位（在册 landed checker 同源） |
| unlanded（权威） | **1,196**（全量缺省形态 dry-run，verify=on，would_archive=90） | 14:14:29 | `deadmass3_dryrun.json` |
| 与二班参照差 | unlanded 1,196−1,205＝−9（≪5%）；干跑将动盘 1,205 与呈批件数同值 | — | 对账 |

墓园面：两池 MANIFEST 5,898＋147 行、dst 在盘核验 5,898＋147，归宿并集 6,045（plan 相位逐池独立核验）。
门判定表 1,273 条（fresh measure＋墓园归宿集∪活属主集）：C_TOMBSTORED 1,046／D_MIXED_TOMBSTORED 41／
B_DEAD_OWNER_TOMBSTORED 99／A_LANDED 57／D_CONFIRMED_LOST 2／B_LIVE_OWNER_LEAVE 17／HOLD_UNIQUE_NOT_TOMBSTORED 11。

## 三、抢救名单保全（硬前置，双层剔除＋正向核验）

1. **双层剔除**：`st-bakdr-20261013`／`st-infoaxis-20261013` 在 13:22 实测均已处于
   `list_active_readonly()` 活性面（两班抢救复投已在册注册）⇒ 先被活属主过滤器自然剔除；
   本班驱动器再显式 `RESCUE_SIDS` 硬踢出 sessions 白名单（`deadmass3_plan.json`：
   `in_whitelist=false` 双确认）。
2. **名下袋普查**：bakdr 实测 7 袋（令面 5→7＝当日新增 2）、infoaxis 16 袋（与令面一致），13:22。
3. **正向核验（执行后）**：dead/ 残留 bakdr 8／infoaxis 23（含抢救期新增死信）；
   归档 manifest 中两 sid 名行数 **0／0**。零触碰成立。

## 四、A 批执行形态（令内三要素：白名单法＋已批开关＋chunk 200 等窗）

- 驱动器＝`.runtime/tmp/deadmass3_archive_driver.py`（本班一次性，TTL 头标注）：**import 二班门代码原样**
  （`tomb_home_set/build_verdicts/gate_factory`，零复制零改动），唯一增量＝统筹已批一次性开关
  `verify_landed=False`（映射在册 `dead_archive_letters` 形参，manifest 痕由在册通道自带 `verify="off"`，
  非本班手写）。三班未改任何门判据/阈值，未用 `--force` 任何形态。
- 干跑留存 JSON：`.runtime/tmp/deadmass3_plan.json`（13:22，解析面）＋
  `.runtime/tmp/deadmass3_dryrun.json`（14:14:29，权威双对照：缺省形态全量 verify=on＝unlanded 1,196；
  白名单+门+verify=off＝将动盘 1,205，kept content_held=4／other_session=77）。
- 干跑数与基线闭合核对：权威 1,205 vs plan 解析 1,187＝+18（1.5%≪5% 停手阈），
  逐项归因＝活属主集翻转（maint7 转死属主其 B/C 袋入白名单、袋面重新分桶），无判据改动。
- 执行：14:16:27 启动，白名单 144 sid 单片（≤200，令面 chunk 200），**首窗即中**（二班实测的
  空窗抓法原样：`_lease_snapshot` 轮询，attempts=240/sleep=20），`[片 1/1 成] archived=1,205
  kept={young:0, revival_in_flight:0, unlanded:0, other_session:77, content_held:4} corrupt=0 verify=off`。
- 执行日志：`.runtime/tmp/deadmass3_execute_log.txt`／`deadmass3_archive_log.json`。

## 五、验证红线逐条（统筹 §九-5，机械化零自拟）

| 红线 | 判据 | 实测（14:17:07 核账尺） |
|---|---|---|
| 每降一枚必有 manifest 行 | qid 集合逐枚对拍 | 1,205/1,205 全等；still_in_dead=0；not_in_bag_dir=0 |
| 双 sha 齐 | `bag_json_sha256`+`blob_set_sha256` 非空 | 缺行 **0** |
| 双 sha 真 | 逐行复算（袋字节 sha256／blob 集合摘要同式） | 失配 **0** |
| verify=off 痕全量 | 新行 verify 字段 | **off 1,205/1,205**（on=0） |
| 内容级证据 | `content_evidence` 真键形（二班 §六-补 键形警示已吸收） | 在 1,205/1,205 |
| n_no_home==0 | 全量断言 | 违例行 **0** |
| tampered==0 | 全量断言 | 违例行 **0** |
| blob 回读 ≥20 行 | 本班做**全量**：1,205 行全部 blob_ref 字节回读比对 | **99,664 文件，mismatch=0，missing=0** |
| 终值闭合 | 1,286−1,205=81 | `dead_now=81` 闭合；foreign 行=0 |

verdict 分布（新行）：C_TOMBSTORED 1,034／D_MIXED_TOMBSTORED 41／B_DEAD_OWNER_TOMBSTORED 99／
A_LANDED 29／D_CONFIRMED_LOST 2。

## 六、blob_gc 收尾（phase 2 --archive，只归档不删）

- 面（ls 口径）：blobs/ **15,685 → 5,824**；blobs_archive/ **11,824 → 21,685**（14:17:43 前／14:18:15 后）。
- run JSON：moved **9,861**／906,432,022 B（864.5 MiB），skipped_race_refs=0，skipped_dst_exists=0
  （承重墙"仍引用只数活引用面"正面读数延续，竞态复扫零跳过）。日志 `deadmass3_blobgc_log.txt`。
- 归档后 bucket 面：A 活引用 6／B 仅 dead 引用 97（回放面，禁碰）／C2 仅 done 引用 1,724（等 cleanup 消化）。
- 二班 §八-13 "pass3 被 1,236 枚引用卡住"的联动面已随本批归档释放（本 pass moved 9,861 即其增量）。

## 七、CREATE-GUARD 正门登记（本册新建）

- 本册经在册批量通道 `scripts/governance/d3_metadata/batch_creation_tokens.py`
  （意图 API 三步 register→publish_snapshot→render 内置，裁定#502 薄壳）从本班车道登记，
  `--prefix docs/_working/deadmass_campaign --created-by st-deadmass3-20261014 --capability deadmass`，
  先 `--dry-run` 预览后实跑；落位校验（账本 active 面）由工具内置 fail-closed 校验完成。
- 台账行（§十）为既存册追加，无需新 token。

## 八、本班自犯与坑（无一遮蔽）

1. **驱动器首版被 heredoc 截断**（bash 写文件 192 行腰斩，恰落语法合法处）——靠 tail 复核抓住，
   改 Write 工具整写后语法＋语义双核。教训：长文件禁 heredoc，写毕必 tail 对行数。
2. `dead_owner_sids & RESCUE_SIDS` list/set TypeError 一发，改 `set()` 交集即修（plan 相位首跑即拦，未涉盘面）。
3. **活属主集翻转（活性族新读数，呈维护线）**：condaxis 在 13:22（live）→14:13（不在）→14:16（又 live）
   三读间翻转，其名下 45 袋随之在"入白名单/留位"间摆动；本班最终窗以其 live 态收束＝45 袋全数留位。
   建议与二班 §五-9 "exited 却在册活"形态并账。
4. plan(1,187)→dryrun(1,205) +18 与门表分桶 ±1 归因均逐枚对账闭合（maint7 活→死 +8 B_DEAD、
   HOLD 先于 B 分支吃掉 1 枚 B 袋等），无未解释残差。

## 九、复核命令（原样抽出即跑）

```bash
# 1) 终值与台账（期望：dead=81 上下（belt 在产会涨）；manifest 总行=1657；行差 1205=本班批）
ls D:/ZephyrAlpha/.runtime/commit_queue/dead/q-*.json | wc -l
wc -l D:/ZephyrAlpha/.runtime/commit_queue/dead_archive_20261014/manifest.jsonl
# 2) 红线核账尺（期望：RED-LINES ALL-GREEN）
python -u D:/ZephyrAlpha/.runtime/tmp/deadmass3_audit_manifest.py | tail -1
# 3) 抢救零触碰（期望：两值 0）
python -c "
import json
from pathlib import Path
mf=Path('D:/ZephyrAlpha/.runtime/commit_queue/dead_archive_20261014/manifest.jsonl')
rows=[json.loads(l) for l in mf.read_text(encoding='utf-8').splitlines() if l.strip()]
print(sum(1 for r in rows if (r.get('content_evidence') or {}).get('session_id')=='st-bakdr-20261013'),
      sum(1 for r in rows if (r.get('content_evidence') or {}).get('session_id')=='st-infoaxis-20261013'))"
# 4) 残留 81 枚构成（期望：condaxis/infoaxis/bakdr/maint7/datalane2/datalane3，全为留位面）
python -c "
import json
from pathlib import Path
from collections import Counter
Q=Path('D:/ZephyrAlpha/.runtime/commit_queue/dead')
t=Counter(json.loads(p.read_text(encoding='utf-8')).get('session_id') for p in Q.glob('q-*.json'))
print(dict(t))"
# 5) blob_gc 逆向通道在册（期望：manifest 行数>0，只归档不删的 restore 口）
wc -l D:/ZephyrAlpha/.runtime/commit_queue/blobs_archive/manifest.jsonl
```

## 十、交接卡（下一班/维护线按此接手）

1. **残留 81 枚构成（14:26 实测）**：condaxis 45（活属主，28 A＋13 B＋4 未测）／infoaxis 23
   （抢救面：11 C＋5 B＋7 未测）／bakdr 8（抢救面：7 C＋1 未测）／maint7 3（HOLD 未存证）／
   datalane2 1（HOLD 未存证）／datalane3 1（未测）。77 枚系活属主/未测留位（other_session），
   4 枚系 HOLD_UNIQUE_NOT_TOMBSTORED（唯一面未入墓园，fail-closed 留位）。
2. **下一批前置＝补一轮存证**：HOLD 11 枚（全表面）＋13 枚未测新死信的唯一面未入墓园
   （二班墓园批次止于其收班时刻）⇒ 复用二班存证流程（独立池＋逐枚 sha）后才可归档；
   本班未越（令内无存证授权，fail-closed 留位）。
3. **unlanded 参照**：1,196（14:14 全量缺省形态）；belt 在产死信持续缓涨，下一班以当刻重测为准（禁沿用本数）。
4. blob 面：B 类 97 枚（仅 dead 引用）是回放面禁碰；C2 1,724 等 done TTL cleanup 消化后可再跑 phase2。
5. 保活与收尾：本班 grant/心跳腿三件齐（session_worktree_start ok=True，heartbeat_daemon pid 39612
   30s 一跳）；reaper keep 行（`deadmass3`，381→383 登记差=2）收班即撤；车道 `archive --execute`
   执行前同分钟复测全部活会话心跳龄（二班 §五-9 变异式坑继续有效，只动自家车道）。
