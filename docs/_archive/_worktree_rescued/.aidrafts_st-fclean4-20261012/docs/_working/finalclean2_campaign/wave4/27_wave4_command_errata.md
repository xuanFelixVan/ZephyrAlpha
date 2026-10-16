---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
completes_when: 后班按本册修正命令复算 M1 到期面，并知悉 `21_/23_` 三处时间点位读数与一条坏命令
session: st-fclean4-20261012
lane: wave4-main
role: 勘误与实况追加册（已落地各册正文一字不改）
---

# 终清波四·交付复核命令自跑结果与勘误（2026-10-13 01:0x）

> 动因＝在册教训"交付件里的复核命令必须从正文抽出**原样跑到期望值**"。本班把 `20_-26_/99_` 里所有 ```bash 围栏块
> 整块抽出实跑（脚本 `.runtime/tmp/st-fclean4-20261012/tools/m2_verify_delivery_commands.py`；
> 含动面 token 的块整块跳过不半跑）。结果三条：一条命令本身有缺陷、两处读数已随面移动、一条结论被实况**加强**。

## 1. ⚑ 坏命令勘误（`23_` §5 第一条）

发布的片段只按"mtime＋7 天"算到期，**没有套清理器自己的豁免规则**，于是把 `.jsonl` 与 `.gitkeep` 这类
**永久免疫件**也打成"即将到期"（实跑输出里出现 `algoflow_progress.jsonl 剩 -35.77 天` 这种荒谬行：它已 42 天，仍活得好好的）。

修正版（按 `reconciliation_registry.py:7749-7753` 三条件判：`>7 天 ∧ 非 .gitkeep ∧ 非 endswith('.jsonl')`）：

```bash
cd /d/ZephyrAlpha
python - <<'PY'
import json,hashlib,pathlib,time
R=pathlib.Path('D:/ZephyrAlpha/.runtime'); now=time.time()
ev=json.loads((R/'tmp/st-fclean3-20261012/out/p2_root_files_content_evidence.json').read_text(encoding='utf-8'))
items=ev['files'] if isinstance(ev,dict) and 'files' in ev else ev
present=sha_same=gone=0; at_risk=[]
for it in items:
    n=it.get('name') or it.get('file'); p=R/n
    if not p.exists(): gone+=1; continue
    present+=1
    b=p.read_bytes()
    if hashlib.sha256(b).hexdigest()==(it.get('sha256') or ''): sha_same+=1
    if n=='.gitkeep' or n.endswith('.jsonl'): continue          # 清理器豁免，永不到期
    ttl=(7*86400-(now-p.stat().st_mtime))/86400
    if ttl<3: at_risk.append((n, round(ttl,3)))
print('frozen',len(items),'present',present,'sha_equal',sha_same,'absent',gone)
print('真正暴露在 7 天刀口下的（<3 天）：', at_risk)
PY
```

01:0x 实跑输出＝`frozen 22 present 22 sha_equal 11 absent 0`，暴露清单＝
`reconcile_launch.lock 剩 0.07 天`（≈02:39 到期，与 `23_` §1 预告一致）、
`takeover_ledger.jsonl.tmp.23876 剩 2.14 天`、`archive_watchlist.json 剩 2.22 天`（其余 5 枚为 `.jsonl`＝免疫）。

## 2. 两处"时间点位读数"更新（不是错，是面在动；后班别拿它当定值）

- `21_` §6 期望值 `worktree 30 / .aidrafts 9 / .git/worktrees 29 / retire patch 5`：01:0x 复跑＝
  **32 / 9 / 31 / 5** ⇒ 增量 2 棵来自本班退场**之后**新开工的他班车道（`st-minedig2`、`st-examrun` 等），
  本班退场净效果仍是 **−10 棵**（40→30 的那一刻已复验）。
- `23_` §1 "1 枚不在盘（`backup.lock`）"：01:0x **它又回来了**（`present 22`），
  且清理器审计对它 **0 命中**（前后都 0）⇒ 这正是 §1 已经下的结论：**持锁进程自己释放、锁件随下一轮备份再建**，
  不是删除事故。也就是说 §1 的"消失"是瞬时态，**判读（自释放非他杀）被实况加强**。

## 3. 未被推翻的关键结论（复跑再证一次）

- Q2 副作用归因：`quarantine_tamper` 现 **244 条**（本班两批开跑前 234），
  按 drift 目录名匹配：本班触过的 427 枚目录在 **14:39Z 之后新增的 10 条里 0 命中**；
  全期交集 2 枚（`drift_20261012T105633`／`T110950`），其行时戳 **11:07Z／11:13Z＝早于本班两批 3.5 小时**，
  成因是 `known_quarantine` 登记的是**文件路径**而判据问 `is_dir()`（`:1153` 自 fires）＝`22_` §4-1 那条缺陷本身。
- 闸① 存证面复验：`.runtime/quarantine/fclean4_safety/aidrafts_unique` **29/29 sha 全等**；
  波三存证面 **23/23 在位且 sha 全等**；drift 面 **0 枚无文件目录**（本班搬走又全部放回的后验）。
- 落地面：dev 上 `wave4/` 现有 **14 件**（含 `evidence/` 与 `lanes/` 5 份），逐件与车道字节 **EOL 归一后全等**。

## 4. 本册之后的两袋状态（写本册时）

| 袋 | 内容 | 状态（01:0x） |
|---|---|---|
| q-…-0006 | `26_` 影子轮次编号更正册 | pending（队首拥堵，本班不催不抢） |
| q-…-0007 | 本册 `27_` | 本册随投 |

> 收班口径与波三一致：**袋入队＝快照入袋**，但**只有 `git show dev:<path>` 读回才算落地**；
> 本班在 `99_` §二/§七里对未复验的袋一律不称完成。复验入口：
> `git ls-tree -r --name-only dev | grep finalclean2_campaign/wave4`（终态期望 16 件＝原 14 ＋ `26_` ＋ `27_`）。
