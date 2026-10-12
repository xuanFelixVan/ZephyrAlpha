---
ttl: task_bound
title: 存证与再生（已落地册面怎么重跑、未入库件的 sha256、TTL 到期风险如实登记）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、为什么本件存在（在案教训点名）

在案两条同族事故：①"假留证"＝未入库源码归档过期＝等于没留；
②考试班被抢救的六件（现 `08_rescued_ttl_st_examrun/`）被已落 dev 的台账逐件点名，
但 dev 面与考试班车道面**双双查无**，只活在 `.runtime/tmp/` TTL 区。
本班不复犯：凡本班交付件里出现的"复核命令/可重跑证据"，本件给出处与再生命令；
凡本班**未入库**的一次性件，本件给 sha256 与重建要点，日后取回可验真伪。

# 二、已落地册面的再生命令（零 CH，任何接班可跑）

| 落地册 | 再生方式（在册尺，不依赖本班临时件） | 期望读数 |
|---|---|---|
| `03_binding_book_event20.yaml` | 逐格用运行器同款子串判据复验，命令见本表下方代码块（本班原样跑过，输出 `20 / 20`） | 20/20 命中 |
| `04_target_face_channel_census.yaml` | 对 `exam_cards` 全量跑在册 `classify_card` ＋按 `target.primary` 空白折叠归一 | universe 177／blocked 118／distinct 94／单例 91 |
| `05_recipe_book_grain_verdicts.yaml` | 对 11 张 A? 卡逐张取 `signal_derivation` 原文跑三条不同型判据 | 四表全"拒登本批"，fit=0 |
| `06_skeleton_card_verdicts.yaml` | 对 13 张 `no_data_binding_section` 卡跑两条机械判据 | 接线 4／新版本卡 2／拒考 7 |
| `18_handoff_matrix_177.yaml` | 对 177 张逐张跑 `classify_card`，reason 前缀归八类 | 求和自证 177=Σhistogram |
| 尺本身可用（正对照） | classify 喂在册已知 hint→应出 D；喂已登记表→应出 A；喂未登记表→复现 `table_not_in_recipe_book` 原文 | 三条全绿，否则"开考面 0"不可信 |

复验绑定册逐格判据（仓库根跑，零 CH；本班 02:5x 原样跑过＝`20 / 20`）：

```bash
PYTHONNOUSERSITE=1 python - <<'PY'
import sys, yaml
from pathlib import Path
sys.path.insert(0, "scripts/backtest"); sys.path.insert(0, "src")
from fexam.card_binding import CARDS_DIR, _card_text

idx = {}
for p in CARDS_DIR.rglob("*.yaml"):
    try:
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    if isinstance(c, dict) and c.get("card_id"):
        idx[str(c["card_id"])] = c

d = yaml.safe_load(Path("docs/_working/examunlock_campaign/03_binding_book_event20.yaml").read_text(encoding="utf-8"))
hits = sum(1 for e in d["entries"] if e["prose_quote"].replace(" ", "") in _card_text(idx[e["card_id"]]).replace(" ", ""))
print(hits, "/", len(d["entries"]))
PY
```

本班 03:0x 实测：上面三条正对照与两把尺独立性（跨 25 袋重跑 tally 全等）都已过一次；
接班只需照表重跑，不必复用本班临时件。

# 三、未入库件的 sha256（取回即可验真）

| 件 | 状态 | 字节 | sha256 前缀 |
|---|---|---|---|
| `scripts/audit/ti_daily_mean_materialize.py` | 待落地（R-1 归维护三班 C4 族） | 17,622 | `58ea5d8470d0e7d6838aa289` |
| `tests/gov/audit/test_ti_daily_mean_materialize.py` | 同上（配对测试 12 支） | 8,511 | `8053c8f20987876d689e1cee` |
| `.runtime/tmp/st-examunlock-20261013/gen_binding_book.py` | TTL，可弃 | 4,566 | `f3a1a6320c96a6d3` |
| `.runtime/tmp/st-examunlock-20261013/gen_recipe_verdicts.py` | TTL，可弃 | 7,743 | `80a9656bbd40087d` |
| `.runtime/tmp/st-examunlock-20261013/gen_skeleton_verdicts.py` | TTL，可弃 | 5,171 | `8a6031491e6f49ed` |
| `.runtime/tmp/st-examunlock-20261013/gen_status_flip.py` | TTL，**不可弃至 20 卡翻状态那班接手** | 6,608 | `a57035489b779d57` |
| `.runtime/tmp/st-examunlock-20261013/gen_target_face_census.py` | TTL，可弃 | 5,965 | `239bb6bba8304e60` |

**为何 §二 说"不必复用临时件"而本表仍登记 sha**：册面必须能由在册尺独立再生（否则是第二真源），
但两件事性质不同——再生的是**结论**（可由尺重跑），而 `gen_status_flip.py` 装的是**动作配方**
（逐卡两行、判据面 sha 前后断言、缺底座即拒翻），这个配方不在任何尺里，随 TTL 消失就真没了。
⇒ 本班把它的关键判据抄进 §四 第 3 条，并登记 sha 供日后核对；
矿考二班接手 20 卡修法（总令 §四"散文 22 卡修法接手"）时按 §四 第 3 条自证即可，不需找本班要文件。

# 四、三条必须随件存活的动作配方（抄在这里，TTL 死了也不丢）

1. **绑定册格的合法性判据**（运行器同款，`run_binding_book` 内部同一式）：
   `entry.prose_quote.replace(" ","")` 必须是 `_card_text(card).replace(" ","")` 的子串，
   其中 `_card_text` ＝ `data_binding` 的 `signal_table/signal_column/signal_derivation/target_source` 四键拼接
   （`card_binding.py:234-239`）；不命中即 `prose_quote_not_found_on_card`，拒绑不出假分。
2. **事件底座二选一硬规**：`_event_base_series`（`:720-726`）要求 `base_op` 与 `base_csv` 恰选其一，
   同给或同缺即 `ValueError`；`base_csv` 缺失/空文件→`base_csv_absent_or_empty`（本班 03:0x 红队实测该路径为红）。
3. **20 卡状态翻转的前置与断言**（矿考二班/挖矿二班接手用）：
   ① 逐列 CSV 必须已存在（缺任一即整批拒翻，禁半翻）；
   ② 只允许改两处顶层键 `status:` 与 `status_reason:`，逐卡 `^status:` 行数必须=1，否则拒；
   ③ 翻转前后对 `JUDGMENT_KEYS`（`card_id/node_id/family/signal_kind/window/buckets/pillars/
      pillars_numeric/target/oos_window_ref/hypothesis`）做 yaml 规范化后 sha256 比对，
      **不等即中止**（这条是反挪门柱自闸的同式，本班 03:0x 实测 20/20 前后 sha 全等、改动行数=2）；
   ④ 先决条件：`window.regimes` 表示层定夺（本班 13 号件）未落地前翻状态只会让 run 面
      从"出分前 AttributeError"变成"逐卡 error 行"，无增益——**故本班不翻**。

# 五、车道同步事实（接班别拿旧基算新账）

- 本班车道 `st-examunlock-20261013` 建基于 `91644e826f`（00:11），
  02:4x 发现 `dev` 已前进 25 袋（56 A／20 M，两本热册未被碰）⇒ **`git merge --ff-only dev` 同步至 `9fabb46a73`**；
  同步前把与 dev 全等的 12 件按 `git show --name-only 7ea68bc19f` 备份到
  `.runtime/tmp/st-examunlock-20261013/pre_sync_backup_<HHMM>/`（backed_up=12），未删任何他班件。
- 同步前后各跑一次在册尺：tally 与宇宙集合**完全一致**（177／A0 A?11 B17 C121 D0 U28，集合差 0）
  ⇒ 本班 04/05/06 三册的读数至今有效，无需回写。
- 踩坑如实报：`git show --name-only ... | tee /dev/stdout | wc -l` 在 Git Bash 下把同一流计两遍，
  本班一度误判"落地 24 件≠袋内 12 件"疑为归属篡改，实为自家管道伪影；改为直接列表后=12 件、热册 0 携带。
