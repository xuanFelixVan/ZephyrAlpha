---
ttl: task_bound
completes_when: 主役放量袋落窗清账（每降一枚有 manifest 行＋证据 sha）＋八-10 未做面由下一班或维护线接走＋本班车道与壳收班即清
---
# 死信放量二班·收班册（sid=st-deadmass2-20261014，2026-10-14 02:2x → ）

令据＝统筹令 2026-10-14 晨（接 `deadmass_campaign/99_delivery.md` §七交接卡）；
全过程账＝同目录 `00_ledger.md` §八（本班班账，实测值全在那儿，本册只落终态与交接）。

## 一、终态（只认 dev 面与进程外读回）

| 项 | 终态 | 凭据 |
|---|------|------|
| 首件小步校准 | **复现**：正对照 MATCH／负对照 DIFF／与在册真门对表 agree=60 disagree=0 | `deadmass_c_measure.py --sample 60` 两轮 stdout（存 `.runtime/tmp/deadmass2_measure_log.txt`） |
| 判据表 | 重成 **1,639 枚**（前任 1,583→1,638→本班 1,639，含跨日新增）：C 1,404／A 76／B 114／D_MIXED 43／D_LOST 2 | `.runtime/tmp/deadmass_c_measure.jsonl`＋前任表已备份 `deadmass_c_measure_20261013T2317.jsonl.bak` |
| 独立尺互证 | 段二腿①自动分诊 10-14 面 C 1,400/A 75/B 118/D 43+2＝**同总数 1,638**（C↔B 差 3＝其间他班落地） | `.runtime/audit/dead_letter_triage_ledger.jsonl`（按 `triage_day` 分组，非 `ts`） |
| 墓园接力 | 新面 **85 枚／37.10 MiB** 入独立池；现表唯一面 **5,980/5,980＝100.0000%** 归宿；逐枚回读 mismatch=0 missing=0 | `E:/_tomb_quarantine/st-deadmass2-20261014/C_unique_20261014/`（MANIFEST 85 行）＋INDEX 本班 20 行 expires=2026-11-13 |
| B 面 115 枚处置 | **按属主活性分道**：活属主 18 枚留位（5 sid）／死属主 97 枚走内容级通道；render 袋按前任销账未 requeue | 归档器判定表 `B_LIVE_OWNER_LEAVE 17／B_DEAD_OWNER_TOMBSTORED 97`；判据源 `commit_queue.py:2129/2396`（死属主 requeue 必再死于 ghost_session） |
| blob_gc phase2 首轮 | **moved 4,710 枚／984.3 MiB，竞态 skip=0**；blobs/ 21,209→16,501，blobs_archive/ 10,883 | `blobs_archive/manifest.jsonl`（`--restore` 可逆）＋stdout `.runtime/tmp/deadmass2_blobgc_archive.json` |
| 前班车道退场 | 接线核查＝**已落** ⇒ 一条命令退场完成；四处读回全空；**执行窗内接管台账新增 0 行** | patch `.runtime/quarantine/st-deadmass-20261013-retire-20261013T185954Z.patch`（substantive=11，`+` 行 1,436）；`takeover_ledger.jsonl` 192→192 |
| 前任未落地交接面 | dev 缺的 §五–§七 **4,418 字节已正门补投**（袋 q-20261014-st-deadmass2-20261014-0001） | 搬入判据＝dev 字节是车道字节的严格前缀（`new[:len(old)]==old` True，纯追加零删改） |
| 会话壳 | **33 → 17**：13 壳 keepalive promote 入墓园后按在册谓词拆；3 壳取证改名件"已存证即放行"mv＋拆；3 壳真成果暂留（见 §三-2） | 墓园 `shell_keepalive_20261014/`（13 行）＋`shell_content_20261014/`（38 行＋mv 复记 3 行＝41 行）；墓园总回读 **139 行 mismatch=0**（六-2 实测读数） |
| 根层散件 | **平铺未跟踪=0**（正对照＝同尺全仓报 168 条 `??`／未跟踪 550，非零命中尺） | `git ls-files --others --exclude-standard` 按 `'/' not in` 分层 |
| gate_audit | 未删（删除属政策变更）；**一条前提被实测改判**：最大两段 120.3/65.3MB 是**已移位 .1 保留段**，同族 live 段实测仅 2.2/1.2MB | `.runtime/gate_audit/` 292 件／1,209.5 MB；维护七班 dev 面班账 `gate_audit` 零命中＝尚未定性 |
| 主役放量（C/D 归档） | **未落**：1,622 枚放行表已就绪、10 片逐片抓窗在跑；本班实测**无空窗可抓**（下表） | 判定表 stdout `.runtime/tmp/deadmass2_archive_log.txt`；`dead_archive_20261014/manifest.jsonl` 尚未生成 |

## 二、⚑ 主役受阻的实测定性（不是"再等等"能解释的）

1. 0.2s × 898 样本连续 180s：**FREE 跨段=0**；`_lease_snapshot` 全程 `present&alive`，holder=常驻守护 pid。
2. 带量吞吐：done 838→845、pending 27→25 ⇒ **约 8–9 min/枚**，25 枚积压需 ~3.5h 才可能出真空窗。
3. 这是闸的本义而非尺的缺陷：`commit_queue.py:1394-1420`＝活体持有者超 TTL 判"慢项在途**绝不可抢**"
   （2026-09-17 十一条 pathspec 死信病根：抢＝两 drain 并发同 serializer worktree，
   `reset` 快进加 `clean` 毁未 commit 新文件）；`dead_archive_letters:3855`＝官方通道**自身**以
   "租约存活"整体拒绝并行维护操作。⇒ 归档的前置条件是**队列空闲**，不是"租约抖一下"。
4. 本班据此**未越闸、未停带、未改判据**（统筹令红线原样执行），把该片实测作为呈批依据交下（§四-1）。

## 三、净零申报

零新门、零新注册册、零新 git 面代码件。全部落在既有驱动器上改**输入指向**：
measure/preserve/archive 三件在册 TTL 驱动器（前任所造）加 `--pool/--skip-pool/--sid/--owner-sid`
与 B 面活性分道判据；新增一次性件仅 `.runtime/tmp/`（不入库）两件——保活腿与壳提升驱动器。
新建 git 面＝本册（1 件，CREATE-GUARD 正门登记 token）＋前任收班册补面 4,418 字节（非新件）。

## 四、⚑ 本班自犯与更正（无一遮蔽）

1. **Edit 追加写坏他班一行**：给 `data/runtime/process_reaper_keep.txt` 追加本班两行时，锚段里
   备份线夜班的计划任务名被误打（丢了 `Alpha-` 段），**当轮即 grep 自纠复原**＋行数对拍
   385→387＝恰本班两行。教训＝追加型热件的锚段必须逐字复制，改后以"行数差＝计划差"自证，
   不能只确认"我的东西进去了"。
2. **长跑日志被判"没跑"**：保活腿与归档腿都插了 `| tail -N`，块缓冲使输出到进程结束才可见 ⇒
   一度误判双腿未起；改文件重定向并以进程表证实两腿一直在跑（在册"空日志≠没跑"复犯一次）。
3. **`clone_guard_audit.py` 无 argparse**：取用法时 `--help` 被当位置参数，直接跑了一轮 L2 全量
   .py 审计（findings=0／健康 A，产物落 `.runtime/clone_guard_audit/audit_20261014T031448.json`）。
   副作用登记在此；该尺只覆 .py，对本班 .md promote 无判别力。
4. **首版墓园尺 KeyError**：把两族 MANIFEST（`blob_sha256` 与 `sha256`）当同一 schema 逐枚回读，
   中途崩 ⇒ 改按 schema 分支后全量 136 行回读跑通。
5. **`--mv` 首版漏 `--execute` 闸**：work 模式 mv 臂若不显式要求 execute 也会 unlink 源件——
   干跑会真删。落盘前自查发现，补 `and args.execute` 并以干跑证明"源件仍在盘＋INDEX 行数不动"。

## 五、交接卡（下一班按此接手，命令已按当下 HEAD 实测可跑）

1. **主役放量＝等队列空闲，勿改判据**。归档器（10 片×195 死属主 sid）在跑时不要并发第二个；
   若本班进程已停，续跑命令＝
   `python -u .runtime/tmp/deadmass_c_archive.py --execute --chunk 20 --attempts 1200 --sleep 15 --owner-sid <你的sid>`
   跑前先 `python -c "import json;d=json.load(open('.runtime/tmp/deadmass_c_archive_log.json',encoding='utf-8'));print(d['ts'],d['archived_qids'][:3])"`
   读回上一轮死因（该文件仅全程跑完才写＝缺文件即"未跑完"，不等于"没跑"）。
   ⚑ 呈批件（前任 §四-1 已预告此分支）＝Owner 令"暂停 belt N 分钟做大批清账"；本班未自拍。
2. **3 壳真成果仓库侧 promote 前置未清**（勿盲投，拥堵队列里新增死信即反向）：
   复测证伪交接卡两处计数——gpuux3v 实质面 **17 枚非 3 枚**、maint3 是 **两个 plan 批共 17 枚**；
   且 `v5_section_13_O.md` 签名行实测已在 dev 的 `gpufeed_campaign/03_gpux_final_report.md` ⇒
   先清 CLONEGUARD 前置（acknowledged 对或散文去重），再 promote，**提升之后**才拆这 3 壳。
   实质面已双证（壳在盘＋墓园 `shell_content_20261014/` 逐枚 sha），不促拆。
   注：宪法引用的写前预查 API `check_before_write`/`resolve_finding` 全仓查无（在册案卷
   `fullflow_mining/m3_governance/06_f103_clone_guard_code_dedup.md` 已挂治理裁定），
   故 promote 前无法预查，只能在 commit 面吃事后 staged 复检。
3. **maint3 的 `orig/` 面不进仓库**（85KB/51KB 级已跟踪件前像副本＝第二真源，且 .py 克隆尺不覆 .yaml）
   ——按本班八-8 只走墓园，墓园行含 rollback_cmd；如维护线要入库须先过 SSOT 方向判。
4. **blob_gc phase2 第二 pass**：本班 C/D 归档落地后再跑一次同一命令
   （`python scripts/governance/blob_gc.py --phase 2 --archive --json`），此时新归档袋的 blob 才转
   archive-only；仍只归档不删。
5. **gate_audit 等维护线定性**，本班已改判一条前提（§一末行）：两段"超标"是已移位保留段，
   live 面 2.2/1.2MB；请维护线据此重找"仍在涨的不过闸写侧"，别按原叙述删存量。
6. **保活与活性面**：本班 grant/守护/心跳腿三件齐（`heartbeat.jsonl` 30s 一跳）；
   下一班若接手同一池子请另起 sid，勿复用 `st-deadmass2-20261014` 的 grant。

## 六、复核命令（正文抽出原样跑，期望值即本册所记）

```bash
# 1) 校准尺仍在（期望：正对照 MATCH／负对照 DIFF(对)／对表 agree=60 disagree=0）
#    ⚠ 该命令以 "w" 重写 .runtime/tmp/deadmass_c_measure.jsonl 与 _uniq.json——
#      只在**无归档器在飞**时跑，否则会把在跑那轮的判据表换成新表（本班两轮实测读数已存
#      `.runtime/tmp/deadmass2_measure_log.txt`，可直接读回核期望值而不必重写表）。
python -u .runtime/tmp/deadmass_c_measure.py --sample 60 | tail -6
# 2) 墓园全面回读（期望：行=139 mismatch=0 missing=0）
python -c "
import hashlib,json
from pathlib import Path
B=Path('E:/_tomb_quarantine/st-deadmass2-20261014'); tot=bad=miss=0
for m in sorted(B.rglob('MANIFEST.jsonl')):
    rows=[json.loads(l) for l in m.read_text(encoding='utf-8').splitlines() if l.strip()]
    k='blob_sha256' if 'blob_sha256' in rows[0] else 'sha256'
    for r in rows:
        f=m.parent/r['dst']
        if not f.exists(): miss+=1
        elif hashlib.sha256(f.read_bytes()).hexdigest()!=r[k]: bad+=1
    tot+=len(rows)
print('行=',tot,'mismatch=',bad,'missing=',miss)"
# 3) 主役进度（期望：dead 每降一枚 ⇒ manifest 行数同增，缺一即回态④存疑）
ls .runtime/commit_queue/dead/q-*.json | wc -l
wc -l .runtime/commit_queue/dead_archive_20261014/manifest.jsonl 2>/dev/null || echo "尚无＝未落窗"
# 4) 租约空窗实测（期望：pending 非空期 FREE=0；本册二-1 的读数复现）
python -c "
import sys,time;sys.path.insert(0,'.');sys.path.insert(0,'src')
from scripts.commit_queue import _lease_snapshot
from pathlib import Path
Q=Path('D:/ZephyrAlpha/.runtime/commit_queue');free=0
for _ in range(150):
    s=_lease_snapshot(Q)
    if not (s.get('present') and s.get('alive')): free+=1
    time.sleep(0.2)
print('samples=150 FREE=',free)"
```

本班自证口径＝六-2/六-3/六-4 三条已在当轮**原样抽出跑到本册所写值**（139 行零失配／
"尚无＝未落窗"＋dead 1,642／samples=150 FREE=0）；六-1 的读数取自本班当轮两次真跑
（02:2x 与 02:5x 均 agree=60 disagree=0，stdout 留存 `.runtime/tmp/deadmass2_measure_log.txt`），
**末稿时未再跑一次**——因它会重写判据表而彼时归档器正在飞（故该条上方加了禁并发注）。
凡未跑过的不写进本册；写进本册的每条都注明了读数来源。
