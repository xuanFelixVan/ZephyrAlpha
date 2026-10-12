---
ttl: task_bound
completes_when: M1/M5/M12 三条已裁项的当窗读数入册，且 M5 的结构上限（7 天清理器×轮转命名）被写成可复算判据
session: st-fclean4-20261012
lane: wave4-main
role: 总包（已裁项状态核销＋影子旁观）
---

# 终清波四·已裁项核销与影子旁观账（M1／M5／M12）

> 令卡："已裁项状态核销：M1 散件不动、M5 观测窗计数（目标 ≥14 天）、M12 倒计时（满 7 天零异常呈'转正＋注册'一次批）"。
> 统筹批复（本班夜窗）另加两条：**M5 撤"14 天观测窗"提法**（它建立在错误模型上）＋**M12 影子 1 天照实计**。本案卷按批复口径核销，并把波三那两句需更正处**另起一节**写（旧案卷原文不动）。

## 1. M1 散件不动——22 枚当窗逐件复验（结论：仍 21 枚在盘，1 枚自然释放）

复验尺＝对波三冻结件 `p2_root_files_content_evidence.json` 的 22 条逐个查在位＋比 sha（存在性判据与内容判据分开给）：

| 读数 | 数 |
|---|---|
| 仍在盘 | **21**（其中 14 枚 sha 与冻结证据全等，7 枚被写者正当重写⇒字节推进非损失） |
| 已不在盘 | **1**＝`backup.lock`（49 B，原 mtime 10-12 01:06） |
| 新增 | 2＝`.probe_21144.tmp`、`session_registry.23800.tmp`（→ M10 那族 `.tmp` 崩溃残件仍在长） |

- `backup.lock` 的 TTL 本该到 10-19 才到期，而 `ops_guard_delete.jsonl` 对它 **0 命中** ⇒ **不是清理器吃的，是持锁进程自己释放的锁件**（正常生命周期，非事故）。本班不改判"消失即事故"。
- ⚑ **更正波三 M1 那句"将被无声吃掉"**（另起一节，`24_` 原文不动）：`GATE-RUNTIME-CLEANUP` 走 `ops_guard.guard_remove`，
  而 `guard_remove`（`scripts/ops_guard.py:812`）**逐件落审计** `gate_audit/ops_guard_delete.jsonl`（现册 49,386 条 GRC 记录）
  ⇒ 删除**不是无声**；真正的限制是**那条审计面本身只留 4.33 天**（见 §2），到期后"谁吃的"才变得不可追。
- 到窗清单（当窗实测＋按 7 天规则推算，动作窗口在本班之后）：
  `reconcile_launch.lock` 到期 **2026-10-13 02:39:38**（本班下笔时仍在盘，属下一个班的第一现场）；
  `takeover_ledger.jsonl.tmp.23876` **10-15 04:28:48**（⚑ 这是**第 4 枚** TTL 暴露件，**令卡/波三清单都没点它**）；
  `archive_watchlist.json` **10-15 06:15:57**；`task_board.db` 现算 **10-19 20:17**（活体 mtime 不断续命，不是固定到期日）。
- 本班动作＝**零删除**（照裁定"M1 散件不动"）。

## 2. M5 核销——撤销"≥14 天观测窗"提法，改报实测保留深度与两条结构上限

- **全集检索判"14 天窗"在册不存在**：HEAD 内 `取证窗/观测窗/gate_audit/ops_guard_delete/feature_flags` 组合检索 0 条"≥14 天"制式（正对照有效：同尺 grep `INV-RET` 命中 18、`backup_count` 命中在册定义）。
  即：**没有任何钟在数 14 天**，所以这条"计数"没有可计的对象——统筹批复据此撤提法，本班照办。
- **真实机制＝尺寸上限，不是时钟**：`src/zephyr/shared/io/audit_jsonl_writer.py:57` `DEFAULT_MAX_BYTES=50MB`、`:62` `DEFAULT_BACKUP_COUNT=3`（当前段＋3 历史段）。当窗实测深度：

| 取证面 | 现深度 | 段构成 |
|---|---|---|
| `gate_audit/ops_guard_delete` | **4.22 天** | 4 段 × 50 MB＝约 193 MiB |
| `gate_audit/feature_flags` | **0.21 天（4.96 小时）且在缩** | 密度高、50MB 封顶 ⇒ 深度随写速反向变动 |

  波三 M5 那句"现取证窗仅 3.7d/0.7d"方向正确，本班给的是同尺的当窗读数（3.7→4.22、0.7→0.21）。
- **⚑ 本班新查出的第二条上限（这条决定"14 天能不能长出来"）**：轮转段命名约定是 `<文件名>.jsonl.<N>`（`_rotate()` 自述，RotatingFileHandler 同型），
  而清理器保护规则只有 `filename.endswith(".jsonl")` ⇒ **`.jsonl.1/.2/.3` 全部不在豁免内**，
  实测 5 枚轮转段现龄 1.11–4.22 天、全部朝 7 天线走。
  ⇒ **只要清理器还吃轮转段，任何取证面的深度都被硬顶在 7 天以下**：把 `backup_count` 提到 13（≈14 天）**也长不出 14 天**，
  两把闸必须同时动：①轮转命名/豁免口径（让 `.jsonl.N` 也受保护，或改命名使末段为 `.jsonl`）；②`backup_count`／单段上限。
  二者皆属他班生产日志参数（写面）＋一条涉及"审计件保留"的判据改面 ⇒ **本班不自改**，呈批＋交属主车道。
- **批复点名的硬前置（先修清理器吃保护面）现状**：主区工作区面 `src/zephyr/governance/audit/reconciliation_registry.py` 实测 **+33/−1**（未暂存），
  其内容已把 `PROTECTED_PREFIXES` 里属于 `.runtime` 的顶层名**从 os.walk 剪枝**并加 `_under_protected()` 逐件判＋`protected_skipped` 计数，
  注释自称"M3/M5 在册裁定"⇒ **同一道修已由他班在途实施**。本班曾独立写出等价改子（含两条测件，其中一条在旧码上验过红：
  `assert qf.exists()` 与 `protected_skipped=1` 双点），发现撞件后**撤回自家车道字节**（`git show HEAD:` 复位，车道 status 现不含该件），
  把改子转为"落地后复验清单"。**不双投、不抢投**（撞同一件必有一方整覆）。
- 缩容呈批的实质前置按批复改记为：①保留深度如实披露（本节表）＋②读者引用核（波三已做，本班复算 5 处行号 `:488/:493-494/:502/:749/:773` **全部仍精确**）＋③清理器口径修落地并复验。

## 3. M12 倒计时——影子 day1＝1 个合格日，最早转正日 2026-10-19

| 轮 | 时刻 | mode | scanned | would_n | errors | suspected | 命中在飞 |
|---|---|---|---|---|---|---|---|
| r1-r4 | 10-12 夜间四轮 | shadow | 466 | 288 | 0 | 0 | 0 |
| r5 | 10-12 16:4x | shadow | 475 | 296 | 0 | 0 | 0 |

- 合格自然日＝**1**（10-12）；r1-r4 的 sha 与波三 `27_` 记录逐条全等（本班复算），r5 起 would 面从 288→296（＋8）＝跨轮 `new/gone` 差集的第一手素材，**同日外不可用 `would_set_sha256` 全等判据**（波三 `29_` 已更正过该口径）。
- 10-12 20:0x 之后**无人续跑**（波三收班后无新轮；本班旁观轮见 §4）。计划任务实测**仍未注册**（54 支 `Zephyr*` 任务无一为 closeout）⇒ 与"影子期不注册、转正与注册同批"裁定一致。
- 满 7 个合格日的最早日期＝**2026-10-19**（day1=10-12 起算）。⇒ M12 的"一次批（转正＋注册）"最早 10-19 呈，**不得提前**。

## 4. 影子 day2 旁观轮（本班职责＝旁观记录，主责在周期班；跨轮口径＝would_n＋new/gone 差集）

| 轮 | 本地时刻 | scanned | would_n | errors | suspected | 与 r5 差集 new/gone | 命中在飞 | 判定 |
|---|---|---|---|---|---|---|---|---|
| （待 10-13 00:0x 跑轮后追加） | | | | | | | | | |

> 跑轮命令（在册件、只读 dry-run，禁加 `--execute`）：
> `python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json > .runtime/tmp/st-fclean4-20261012/out/shadow_day2_r6.json`
> 判活一律 `list_active_readonly()`；合格四件齐＝`mode=shadow ∧ errors=0 ∧ suspected=0 ∧ 命中在飞=0`，不齐即不计当日并暂停转正。

## 5. 复算命令

```bash
cd /d/ZephyrAlpha
python - <<'PY'
import json,pathlib,hashlib,time
R=pathlib.Path('D:/ZephyrAlpha/.runtime')
ev=json.loads((R/'tmp/st-fclean3-20261012/out/p2_root_files_content_evidence.json').read_text(encoding='utf-8'))
items=ev if isinstance(ev,list) else ev.get('items') or ev.get('files') or []
now=time.time(); present=0; same=0; gone=[]
for it in items:
    n=it.get('name') or it.get('file'); p=R/n
    if p.exists():
        present+=1
        sh=hashlib.sha256(p.read_bytes()).hexdigest()
        if sh==(it.get('sha256') or ''): same+=1
    else: gone.append(n)
print('frozen',len(items),'present',present,'sha_equal',same,'gone',gone)
for it in items:
    n=it.get('name') or it.get('file'); p=R/n
    if p.exists():
        d=(7*86400-(now-p.stat().st_mtime))/86400
        if d<2.5: print('  即将到期',n,'剩 %.2f 天'%d)
PY
ls .runtime/gate_audit/*.jsonl.[0-9] | wc -l         # 轮转段枚数（现 5）
python - <<'PY'
import json,pathlib
p=pathlib.Path('D:/ZephyrAlpha/.runtime/audit/worktree_drift_watchdog.jsonl')
rows=[json.loads(l) for l in p.read_text(encoding='utf-8',errors='replace').splitlines() if l.strip()]
from collections import Counter
print(Counter(str(r.get('verdict')) for r in rows).most_common(8))
PY
```
