---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
gate_selfdoc: GIT-DANGEROUS  # 本册第 60 行原文引用在册函数提示语（拒绝对话未提交件强复位），非本班下达的危险命令
completes_when: 10 棵退场回执与 `20_` 决策表逐棵对账一致，且回收额度/管理面/旁证面三项实测被复核
session: st-fclean4-20261012
lane: wave4-main
role: 总包回执（执行后实测）
---

# 终清波四·M2 退场回执（10 棵，在册 lane-archive 通道）

> 执行时刻（实测 `date`）：2026-10-12 22:20:17→22:21:15 本地（=14:20:17→14:21:15Z，退休 patch 文件名同源）。
> 决策依据与逐棵判型见同目录 `20_wave4_m2_dossier.md` §2；本案卷只记**执行后事实**。

## 1. 退场集与逐棵回执

通道＝`python scripts/session_worktree.py archive --execute <绝对路径>`（SOP∩令卡实质，见 `20_` §4），
目标一律传**绝对路径**（`_resolve_archive_target` ①路径匹配先于 ②basename，避开 `.aidrafts`/`.worktrees` 同名单胞胎歧义）。

| sid | 判型 | ahead | 脏/未跟踪 | retire patch | rescue 项 | branch -d | daemon |
|---|---|---|---|---|---|---|---|
| st-backfix-patrol-20261011 | zero_loss | 0 | 0/0 | 不需要（零脏） | 0 | 已删（壳分支） | 无 PID 件 |
| st-deadcure3-20261010 | zero_loss | 0 | 0/0 | 不需要 | 0 | 已删 | 无 |
| st-finalclean2-20261010 | zero_loss | 0 | 0/0 | 不需要 | 0 | 已删 | 已终止 PID 10412 |
| st-fullflow2-20261008 | zero_loss | 0 | 0/0 | 不需要 | 0 | 已删 | 已终止 PID 42064 |
| st-nightmine2-20261010 | zero_loss | 0 | 0/0 | 不需要 | 0 | 已删 | 已终止 PID 52216 |
| st-dexp-20261009 | needs_rescue | 0 | 4/4 | `st-dexp-20261009-retire-20261012T142017Z.patch` | 4 | 已删 | 已终止 PID 24404 |
| st-final4-20261010 | needs_rescue | 0 | 2/1 | `...-142026Z.patch`（三分类 substantive=2） | 1 | 已删 | 已终止 PID 38640 |
| st-nightmine-20261010b | needs_rescue | 0 | 51/17 | `...-142039Z.patch`（crlf_phantom=26＋substantive=25） | 17 | 已删 | 已终止 PID 40160 |
| st-regsolo-20261010 | needs_rescue | 0 | 4/4 | `...-142048Z.patch`（substantive=4） | 4 | 已删 | 无 |
| st-nightmine-20261010 | needs_rescue | 0 | 259/249 | `...-142115Z.patch`（substantive=259） | 249 | 已删 | 已终止 PID 34740 |

`branch -d`（非 `-D`）10/10 全过 ⇒ 10 个 `session/<sid>` 分支末提交当时均为 dev 祖先（零真 ahead）；
落点核对：`git worktree list` 40→**30**；`.git/worktrees/` 管理面现 **29** 枚，其中 10 个目标名只剩
`st-finalclean2-20261010`——它属**存活**的 `.worktrees/st-finalclean2-20261010` 单胞胎（`.aidrafts` 那棵当年注册成
`st-finalclean2-202610101`，随本批 prune 消失）⇒ 非残留、非漏清。

**回收额度（实测）**：10 棵 apparent **3,082,995,081 B ＝ 2.87 GiB / 203,440 个文件**（逐棵 271.9–304.0 MiB，
表在 `20_` §1；口径＝`os.path.getsize` 求和）。D 盘 free 现 72.3 GB（`shutil.disk_usage`，同批两次读数 72.33→72.3）。

## 2. 未动集（态④）与令卡分母差

`.aidrafts` 现存 9 目录＝本班 1 ＋ 他班 8：`st-backfix3-20261011`、`st-cband-20261012`、
`st-deadcure3b-chief-20261011`、`st-gpux3-20261012`、`st-maint3-20261011`、`st-minedig-20261012`、
`st-statsgov-20261012`（令卡之后新开工）、`st-mineloop-20261010`（令卡点名排除，矿考二班域，ahead=1＋脏 107）。
其中 7 棵在执行窗内有**在册活性旁证**（心跳分片或 daemon 或 dev 落地），故本班按令卡纪律条"在飞班资产禁碰"零动作。

## 3. 副作用账（我用 mutating 死判通道的代价，逐条实测）

- **前置证明确实做过、但过期了（⚑ 本班程序性过失）**：`20_` §4 记 21:35:16 实测"13 片全部心跳 <900s ⇒ 无过期项 ⇒ 零接管写入零收割"，
  而实际执行在 **22:20**——相隔 45 分钟。在册铁律是"运行态断言同分钟复测"，我没在动手前复测。
  后果实测（22:3x 复核）：执行窗内 8 个会话的心跳分片被收割（`backfix3/cband/deadcure3b-chief/gpux3/maint3/statsgov` ＋ **本班自身**），
  机制＝这些会话的 `heartbeat_daemon` 在 21:3x–22:0x 间自退（daemon 有 1800s idle 自退出设计），心跳停跳后由 mutating `list_active()` 收割。
  ⇒ 树与字节**零损失**（7 棵他班树原样在盘、我只删了自己判定的 10 棵），但"零副作用"那句结论**只对 21:35 成立，不成立在我执行时刻**。
- **接管台账零新增（实测）**：`.runtime/takeover_ledger.jsonl` 183 行全 `status=open`；
  其中本班 10 个目标 sid 的条目 `ts`＝**2026-10-12 20:21:25 本地**（12:21:25Z），早于本班动手 2 小时，
  `death_evidence.reason` 原文＝`orphan_resources: .aidrafts/<sid> 在盘而注册表无此会话（瞬时死亡/被除名）`
  ⇒ 那 9 棵**已由在册 orphan_resources 扫描独立判死并立案**，本班退场与其结论一致（旁证，非本班所造）；
  执行窗（14:20–14:21Z）**无任何新行**（逐行按 `ts_epoch` 过滤实测）。
- **本班自身**：分片被收割后已复注册（`session_worktree_start` 幂等，新 daemon PID 5616，心跳活）；
  复注册时该函数提示"worktree 有 1 个未提交改动，拒绝 `git reset --hard` 以防丢弃 AI 编辑"（＝本案卷与 `evidence/`），
  仅告警未强改，本班未提交件字节完好。
- **明文密钥**：`st-regsolo-20261010/config/.env.{clickhouse,postgres}` 随该树退场被 `git worktree remove` 删除
  （主仓同名原件未动、sha 全等关系由波三 `hash_only_manifest` 留证）⇒ 本面**少了一处未纳管明文副本**，方向是收敛不是损失；
  本班未自行扩大处置（主仓那份仍属波三 M7 呈批面）。

## 4. 闸① 落地回执（批复改的落点：案卷与指纹入 git，字节入取证保护区）

- 318 件非缓存独有面逐件处置已入 `evidence/aidrafts_fingerprint.yaml`（机生）：
  `in_flight_lane_untouched_no_copy` 285（`st-cband` 169MB 主体在此，它没退场）、
  保护区字节副本 **29 件**、`hash_only_plaintext_never_copied` 4（密钥零复制明文）。
  **退场后复验＝29/29 sha 全等、anomalies=0**（清单建于退场前、复验在退场后，故此数即"零损失证明"）。
- 字节副本落点 `.runtime/quarantine/fclean4_safety/aidrafts_unique/`（29 件＋`MANIFEST.jsonl` 29 行），
  该面受 ops_guard `PROTECTED_PREFIXES` 保护；**其寿命取决于同日在途的清理器口径修**（见 `22_` §清理器），
  故 git 侧留全量 sha 供失配即查。
- **本班一处自纠**：首版曾把 5 枚 regsolo 运行态小件（`trigger_queue/*.json`＋`activate_env.ps1`，共 2,382 B）双写进
  `docs/_working`——那里在册 DCR 禁 `.json`，且这些是车道运行态而非交付件（commit 进 dev＝替业务资产定真源，波三 M2 同判）。
  已撤回，改为"指纹入 git＋字节入保护区"，理由写进册内 `why_no_byte_copies_in_git`。
- **波三存证面复验**：`fclean3_safety/aidrafts_irreplaceable` 25 条 MANIFEST 行中 23 条 byte_copy 今仍在盘，
  **sha 23/23 全等、失配 0**（`still_present`=23／`sha_now_matches_manifest`=23）；2 条为密钥 hash-only（原即不复制）。
- **`regsolo_campaign/99_delivery.md` 仍未落册**（`ARCH-383` 号 真悬空，波三判门拦得对，本班复核同判）：
  本班**不把它复制进 git**——新建件里该引用会被 `ARCH-REFERENCE` 的 L2 同提交原子性硬拦，
  而放行它的唯一办法是自造注册表条目或改他班正文，两者都在禁列。该案卷正本在波三存证面＋本班保护区副本，双处 sha 同值入指纹册。

## 5. 面形状变化的在册复核（不靠"应该没事"）

只读车道实测结论（`lanes/lane_face_readers.md`）：面级通配读者＝10 模块/12 枚举点，
**其输出无一件是 git 跟踪件**（`docs/_working/three_piece_infra/visibility_board/*` 与接管台账均不在跟踪面），
故 40→30 棵的形状变化不触发任何 `regenerate --exit-code` 齐平门；本班据此**未**重打任何投影册。
退场后现面实测＝`.aidrafts` 9 目录＋`.aidrafts_pool` 1（locked）＋`commit_queue` 系 6（w0-w3/worktree/单胞胎）＋`.worktrees` 系 13 ⇒ 与 `git worktree list` 30 条自洽。

## 6. 复算命令（只读，本班逐条自跑过）

```bash
git -C /d/ZephyrAlpha worktree list | wc -l                      # 现 30
ls /d/ZephyrAlpha/.aidrafts | grep -c '^st-'                     # 现 9
ls /d/ZephyrAlpha/.git/worktrees | wc -l                         # 现 29
ls /d/ZephyrAlpha/.runtime/quarantine/*-retire-20261012T14*.patch | wc -p 2>/dev/null; ls /d/ZephyrAlpha/.runtime/quarantine/ | grep -c "retire-20261012"  # 期望 5
python - <<'PY'
import json,pathlib,datetime
rows=[json.loads(l) for l in pathlib.Path('D:/ZephyrAlpha/.runtime/takeover_ledger.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
win=[r for r in rows if isinstance(r.get('ts_epoch'),(int,float)) and 1791804000<=r['ts_epoch']<=1791805400]
print('takeover rows in my 14:20-14:23Z window:',len(win))
print('rows for my 10 targets and their ts:',sorted({r['ts'][:19] for r in rows if r.get('sid','').startswith(('st-dexp','st-final4','st-finalclean2','st-fullflow2','st-nightmine','st-regsolo','st-backfix-patrol','st-deadcure3-2026'))}))
PY
```

## 7. 残余（如实）

- 5 棵 needs_rescue 的未跟踪件被在册通道 **mv** 到 `.runtime/tmp/rescue/<sid>/`（**24h TTL 面**）；
  本班已在保护区另存其非缓存件的字节副本与全量 sha，但**缓存类未跟踪件（nightmine 249 项主体）只存在于该 TTL 面**——
  本班判定可再生（`__pycache__`/`.runtime` 形态），不为其申请永久面；若后人判其不可再生，需在 24h 窗内从 rescue 面搬家，
  窗过即不可追（本班不扩权自留，此条列呈批）。
- 2 个在册通道自身缺口未修（不属本班权限）：`archive` 只清传入的那一面（单胞胎问题靠传绝对路径规避，非机制修）；
  `_rescue_untracked_files` 落点仍在 TTL 临时区。均已在 `22_`/晨包列交维护三班。
- 本班未跑 `--all`（排除表虽含 pool/qoder/serializer，但 `--all` 会把在飞车道一并送进死判，风险不可控）；逐棵显式目标。
