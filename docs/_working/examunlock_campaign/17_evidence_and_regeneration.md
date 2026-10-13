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
| `scripts/audit/ti_daily_mean_materialize.py` | 未落地（R-1 归维护三班 C4 族）⇒ **字节全文内嵌本件 §六** | 19,054 | `c8cada6e44669cdb9977ebcf`（04:5x 刷新：口径注记入 generator＋`ruff format` 后） |
| `tests/gov/audit/test_ti_daily_mean_materialize.py` | 同上（配对测试 **15** 支，本班 04:5x 复跑全绿）⇒ 字节全文内嵌 §六 | 10,274 | `4d05469242c771aa1ab2cb34` |
| `.runtime/tmp/st-examunlock-20261013/gen_binding_book.py` | TTL，可弃 | 4,566 | `f3a1a6320c96a6d3` |
| `.runtime/tmp/st-examunlock-20261013/gen_recipe_verdicts.py` | TTL，可弃 | 7,743 | `80a9656bbd40087d` |
| `.runtime/tmp/st-examunlock-20261013/gen_skeleton_verdicts.py` | TTL，可弃 | 5,171 | `8a6031491e6f49ed` |
| `.runtime/tmp/st-examunlock-20261013/gen_status_flip.py` | TTL 收班即清 ⇒ **字节全文内嵌本件 §六**（本班 04:4x 实测复原＝6,608B／sha 前缀与旧行 `a57035489b779d57` 全等） | 6,608 | `a57035489b779d57` |
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

# 六、未入库件字节存证（全文内嵌，逐字符可复原）

本班 04:5x 把三件字节原样搬进本节（不是摘录、不是改写、不省略）。**Why**：三件都从未入库，
只活在车道工作树／TTL 区；而本班 03:1x 已实测过一次"自动重基把自己未落地编辑拍回旧面"的同型事故
（内层 worktree 已被拍平，外层侥幸）。落在册面上才是交付，TTL 区里的源码等于没写。
**How to apply**：①两件 .py 在 R-1（翻译册投影滞后，维护三班 C4 族）解掉后取出写成同名文件即可入袋；
②`gen_status_flip.py` 收班即随 TTL 消失，接班按 §四 第 3 条的四条前置复原它再干跑。

取用约定：块内正文＝源文件去掉末尾换行后的全部内容；复原时补一个 `
`（校验式已补）。
本班 04:4x 首版校验式有两处自家错（正则里写字面 fence→把式子自己当代码块；内嵌掉末换行→少 1 字节），
都是跑自己写的式子时看到的红；改后实测＝原样绿、末位改 1 字符红、少 1 换行红。
04:5x 二次刷新：物化件改了口径注记并过 `ruff format`（18,765→19,054B），本节字节随之重生——
在案教训"改完 .py 必重跑归档件再入袋"，本班按此重跑，故本节的 sha 与车道盘面逐字节一致（下方校验式实测三行全 `OK`）。

登记面：

| 件 | 磁盘字节 | 复原字节 | sha256 |
|---|---|---|---|
| `scripts/audit/ti_daily_mean_materialize.py` | 19054 | 19054 | `c8cada6e44669cdb9977ebcf241cb7ae4b7ca9da185a0dad473672bd38792e24` |
| `tests/gov/audit/test_ti_daily_mean_materialize.py` | 10274 | 10274 | `4d05469242c771aa1ab2cb34c15d71e847e37780ec96694fa468afb56f6269fd` |
| `.runtime/tmp/st-examunlock-20261013/gen_status_flip.py` | 6608 | 6608 | `a57035489b779d5718cdd8d158ca3af7bf3bb937fa29f33bbba7a98c15fb1c22` |

复原校验式（仓库根跑，零 CH）：

```bash
PYTHONNOUSERSITE=1 python - <<'PY2'
import hashlib, re, pathlib
F = chr(96) * 4
doc = pathlib.Path('docs/_working/examunlock_campaign/17_evidence_and_regeneration.md').read_text(encoding='utf-8')
want = [
    ('scripts/audit/ti_daily_mean_materialize.py', 19054, 'c8cada6e44669cdb9977ebcf'),
    ('tests/gov/audit/test_ti_daily_mean_materialize.py', 10274, '4d05469242c771aa1ab2cb34'),
    ('.runtime/tmp/st-examunlock-20261013/gen_status_flip.py', 6608, 'a57035489b779d5718cdd8d1'),
]
for name, size, sha in want:
    seg = doc.split('### `' + name + '`', 1)[1]
    blk = re.search(F + 'python
(.*?)
' + F, seg, re.S).group(1) + '
'
    b = blk.replace('
', '
').encode('utf-8')
    ok = (len(b) == size and hashlib.sha256(b).hexdigest().startswith(sha))
    print('OK ' if ok else 'RED', name, len(b), hashlib.sha256(b).hexdigest()[:24])
PY2
```

期望＝三行都以 `OK ` 开头。

### `scripts/audit/ti_daily_mean_materialize.py`

磁盘字节 19054 ／ 复原字节（块体+末换行）19054 ／ sha256=`c8cada6e44669cdb9977ebcf241cb7ae4b7ca9da185a0dad473672bd38792e24`

````python
# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/examunlock_campaign/02_ti_series_spec.md | §三 物化口径
# [MODULE] ti_daily_mean_materialize（scripts 技术指标族日频基序列物化件，非 src 包模块）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; yaml; 标准库 argparse/csv/re/sys/pathlib;
#   scripts/backtest/fexam/ch_data.ch_query_df（考试域 CH 只读单口，经 TableRegistry 表名真源）;
#   scripts/backtest/fexam/card_binding（SERIES_DIR/CARDS_DIR 路径真源，只导入禁复制）;
#   schemas/categories/market/market_technical_indicator.py（INSERT_COLUMNS 列白名单真源）
# [CONSUMERS] scripts/backtest/fexam/card_binding.py --mode run --binding-book
#   docs/_working/examunlock_campaign/03_binding_book_event20.yaml（op_event_flag_rolling_pctile 的 base_csv 底座）;
#   考试卡族 origin=reverse_triage_batch3_20261012（20 张卡面 impl_gap 验证项①）
# [STARTUP] manual（python scripts/audit/ti_daily_mean_materialize.py --mode materialize）
# [MATURITY] production
# [INVARIANTS] 列集与窗**从卡面派生**（data_binding.baseline_birth 的表.列引用原文＋window 键），
#   禁手抄清单——手抄必漂移；列须同时命中 schema INSERT_COLUMNS 白名单，未命中即抛（禁拼未证列）；
#   查库只读零状态变更；表名经 TableRegistry 品类派生，禁字面量（TABLE-NAME-REGISTRY）；
#   同键多版表面按 (symbol, 日) anyLast 去重后再跨票等权均值（禁把多版本原始行当唯一行）；
#   缺格=自然缺格，禁前向填充冒充；逐日截面票数只入 meta 不进 value 列、不设筛阈（零自创判据）；
#   末日不得越过在册闭卷切点 2025-09-09；产物文件名带 PHASE 版本，映射变更升版禁原地改；
#   本件零 wall-clock（数据面不写 datetime.now()，生成时刻一律由数据末日 as_of 表达）
# [MODIFY-GUARD] 改动=20 张反向卡基序列口径变更，须先改卡面并作废重开（G4-5 冻结纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达=CHAccessError 上抛（fail-closed，禁静默空产物）；
#   面板出现重复 trade_date=SystemExit（双写致下游按日计数翻倍）；
#   窗内零行=SystemExit（禁出空件冒充物化完成）；列名不在白名单=ValueError
# [TESTS] tests/gov/audit/test_ti_daily_mean_materialize.py（列派生零手抄断言＋白名单拒判＋逐日唯一＋输出契约）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  人工 CLI 物化件（考试前接线，按需触发），非常驻自动系统
# create-guard-not-dup: 本件是"技术指标族逐日全市场等权均值基序列"的物化面；命中项均为
#   日频指标**计算/扫描**件（indicator builder、audit_technical_indicator_columns 列覆盖率审计）
#   或既有 7 枚广度序列的一次性临时件（.runtime/tmp/st-nightmine-20261010，本件按根宪法 §4.1
#   收编其输出契约并替代之），零功能交集于"卡面派生列集→持久化基序列→供 event flag 底座"这条链。
"""ti_daily_mean_materialize — 技术指标族日频基序列物化件（考试解锁②）。

20 张 `origin=reverse_triage_batch3_20261012` 反向卡卡面 `impl_gap` 自书开考前须验
"①物化序列逐日可复算"，而 `SERIES_DIR` 实测技术指标族 0 枚（规格与实测出处=
`docs/_working/examunlock_campaign/02_ti_series_spec.md` §二）。本件补该面：

  materialize  按卡面派生列集，逐列取 CH 日频全市场等权均值，写 `ti_ew_<col>_v1.csv`
               （表头 trade_date,value，与现有 7 枚同契约）＋同名 `.meta.yaml` provenance。
  verify       不写盘：重查同一 SQL 与盘面 CSV 逐日逐值对拍，证"可复算"（幂等重跑无漂移）。
  census       不写盘零 CH：只打印卡面派生到的 (card_id, column) 集合与窗，供投前校准。

用法：python scripts/audit/ti_daily_mean_materialize.py --mode materialize
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

RUN_ROOT = Path(__file__).resolve().parents[2]
for _p in (RUN_ROOT / "scripts" / "backtest", str(RUN_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, str(_p))

from fexam.card_binding import CARDS_DIR, SERIES_DIR  # 路径真源只导入禁复制  # noqa: E402

CATEGORY_ID = "market_technical_indicator"  # 表名唯一真源=TableRegistry 品类 id
PERIOD = "daily"  # 在册默认档：scripts/audit_technical_indicator_columns.py:69-72,119
PHASE_VERSION = "ti-ew-v1"  # 口径版本；映射变更升版禁原地改
CLOSED_BOOK_CUTOFF = "2025-09-09"  # 在册闭卷切点（t0_six_phase_materialize.py:52 同式）
FAMILY_ORIGIN = "reverse_triage_batch3_20261012"  # 卡面冻结族标（非本件自拟）
_CARD_COL_RX = None  # 惰性构造：卡面"表.列"引用正则的表名段取自 TableRegistry 派生值，禁落字面量


def _card_column_pattern() -> re.Pattern[str]:
    """从品类真源拼卡面列引用式（表名字面量不落本件，TABLE-NAME-REGISTRY 门约束）。"""
    global _CARD_COL_RX
    if _CARD_COL_RX is None:
        from zephyr.data.table_registry import get_registry

        tbl = get_registry().table(CATEGORY_ID)
        _CARD_COL_RX = re.compile(rf"{re.escape(tbl)}\.([a-z][a-z0-9_]*)")
    return _CARD_COL_RX


#: 去重口径＝argMax(col, ingest_ts) 而非 anyLast：本班 04:05 实测该表同键多版共存
#: （DDL `ReplacingMergeTree` 未带版本参数、ORDER BY (symbol,period,trade_time)，`ingest_ts` 是列但没进版本位），
#: anyLast 在 merge 前后与并发重算期间跨执行不确定 ⇒ 复算证明腿（verify）判红。
#: 在册不变量原文＝"聚合去重口径 anyLast(argMax 同义) per day"，故 argMax(值, ingest_ts) 是**同口径的确定性写法**。
#: §5.160.2 SQL 集中化面：模板常量收本块，表名/列名经派生注入，函数体零裸 SQL
#: SETTINGS 帽子是本仓在案的共享内存墙对策（172.24.30.100:8123 总上限 7.14 GiB，
#: 10-13 凌晨矿考二班开考实测：并发面板装载撞穿＝HTTP 500 / system.errors code=241），
#: 本班 20 次逐列聚合属同型装载，故单查询自限 3 GiB 并让 GROUP BY 外排磁盘，
#: 宁可自己慢/自己红，不把他班查询洗成墙外人质。
SQL_TI_DAILY_EQUAL_WEIGHT = (
    "SELECT d, avg(v) AS m, toUInt64(count()) AS n FROM ("
    "SELECT symbol, toDate(trade_date) AS d, argMax({col}, ingest_ts) AS v FROM {tbl} "
    "WHERE period = '{period}' AND trade_date >= '{start}' AND trade_date <= '{end}' AND {col} IS NOT NULL "
    "GROUP BY symbol, d) GROUP BY d ORDER BY d "
    "SETTINGS max_memory_usage = 3221225472, max_bytes_before_external_group_by = 1610612736"
)


def _schema_columns() -> set[str]:
    """列白名单真源=schema 的 INSERT_COLUMNS（动态取，静态清单禁手工维护，根宪法 §9.5）。"""
    path = RUN_ROOT / "schemas" / "categories" / "market" / "market_technical_indicator.py"
    spec = importlib.util.spec_from_file_location("_mti_schema", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return set(re.findall(r"[a-z][a-z0-9_]*", str(mod.INSERT_COLUMNS)))


def derive_card_columns(cards_dir: Path = CARDS_DIR, origin: str = FAMILY_ORIGIN) -> list[dict]:
    """从卡面派生 (card_id, column, 窗)——列名不手抄，只认卡内 `表.列` 引用原文。

    一卡多列或零列即抛：卡面 `piece_1_signal_face` 是单列声明面，多列=该卡需重冻而非本件硬凑。"""
    out: list[dict] = []
    for p in sorted(Path(cards_dir).rglob("*.yaml")):
        try:
            card = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — 非卡件（册/不可解析）跳过
            continue
        if not isinstance(card, dict) or card.get("origin") != origin:
            continue
        binding = card.get("data_binding") or {}
        prose = yaml.safe_dump(binding, allow_unicode=True)
        cols = sorted(set(_card_column_pattern().findall(prose)))
        if len(cols) != 1:
            raise ValueError(f"card_column_not_single:{card.get('card_id')}:{cols}")
        win = card.get("window") or {}
        ins, oos = win.get("in_sample") or [], card.get("oos_window_ref") or []
        if len(ins) != 2 or len(oos) != 2:
            raise ValueError(f"card_window_not_frozen:{card.get('card_id')}:{ins}:{oos}")
        out.append(
            {
                "card_id": str(card.get("card_id")),
                "path": str(p),
                "column": cols[0],
                "in_sample_start": str(ins[0]),
                "oos_end": str(oos[1]),
                "status": str(card.get("status")),
            }
        )
    if not out:
        raise ValueError(f"family_origin_not_found:{origin}")
    return out


def series_name(column: str) -> str:
    """文件名带口径版本号（卡面 piece_1_signal_face 的 PHASE 版本化纪律：升版禁原地改）。"""
    return f"ti_ew_{column}_v{PHASE_VERSION.rsplit('-v', 1)[-1]}.csv"


def fetch_daily_mean(column: str, start: str, end: str, *, timeout: int) -> pd.DataFrame:
    """取一列的逐日全市场等权均值（含逐日截面票数 n_symbols；只记账不设筛阈）。"""
    from fexam.ch_data import ch_query_df

    allowed = _schema_columns()
    if column not in allowed:
        raise ValueError(f"column_not_in_schema_whitelist:{column}")
    from zephyr.data.table_registry import get_registry

    sql = SQL_TI_DAILY_EQUAL_WEIGHT.format(
        col=column, tbl=get_registry().table(CATEGORY_ID), period=PERIOD, start=start, end=end
    )
    df = ch_query_df(sql, timeout=timeout)
    if df.empty:
        raise SystemExit(f"FAIL: {column} 窗内零行——禁出空件冒充物化完成")
    out = pd.DataFrame(
        {
            "trade_date": pd.to_datetime(df.iloc[:, 0]),
            "value": pd.to_numeric(df.iloc[:, 1], errors="coerce"),
            "n_symbols": pd.to_numeric(df.iloc[:, 2], errors="coerce"),
        }
    ).set_index("trade_date")
    out = out.dropna(subset=["value"])
    if out.index.duplicated().any():
        raise SystemExit(f"FAIL: {column} 面板含重复 trade_date——双写会使按日计数翻倍，禁出件")
    return out.sort_index()


def repro_check(disk_path: Path, frame: pd.DataFrame) -> dict:
    """复算判据＝与写盘同一格式**逐字符**相等（不自拍容差）：CSV 落的是 %.10g，
    用浮点差判"等不等"会把书写精度当成数据漂移（04:09 实测 adosc 差 0.048 / 量级 1e8）。"""
    if not disk_path.exists():
        return {"column": disk_path.stem, "drift": "absent_on_disk", "reproducible": False}
    disk_raw = pd.read_csv(disk_path, dtype=str, keep_default_na=False)
    disk_days = list(disk_raw["trade_date"])
    live_days = [d.strftime("%Y-%m-%d") for d in frame.index]
    live_txt = [f"{v:.10g}" for v in frame["value"].to_numpy()]
    mism = [(a, b, c) for a, b, c in zip(disk_days, list(disk_raw["value"]), live_txt, strict=False) if b != c]
    return {
        "rows_disk": len(disk_days),
        "rows_live": len(live_days),
        "index_identical": disk_days == live_days,
        "text_mismatch_days": len(mism),
        "first_mismatches": [f"{a}:disk={b}!={c}" for a, b, c in mism[:3]],
        "reproducible": bool(disk_days == live_days and not mism and len(disk_days) == len(live_days)),
    }


def _rows_from_frame(frame: pd.DataFrame) -> list[dict]:
    return [
        {"trade_date": idx.strftime("%Y-%m-%d"), "value": f"{val:.10g}"}
        for idx, val in zip(frame.index, frame["value"], strict=True)
    ]


def build_meta(column: str, frame: pd.DataFrame, card_ids: list[str], start: str, end: str) -> dict:
    n = frame["n_symbols"]
    return {
        "schema_version": "ti-ew-meta/v1",
        "column": column,
        "phase_version": PHASE_VERSION,
        "series_file": series_name(column),
        "as_of": frame.index.max().strftime("%Y-%m-%d"),  # 数据末日，非 wall-clock
        "date_span": [frame.index.min().strftime("%Y-%m-%d"), frame.index.max().strftime("%Y-%m-%d")],
        "requested_window": [start, end],
        "rows": int(len(frame)),
        "closed_book_ok": int(frame.index.max().strftime("%Y-%m-%d") <= CLOSED_BOOK_CUTOFF),
        "cards_bound": sorted(card_ids),
        "caliber": {
            "table_category_id": CATEGORY_ID,
            "period_filter": PERIOD,
            "definition": "逐日全市场等权均值（非缺格截面）",
            "dedup": (
                "先 (symbol, 日) 取单版再跨票 avg；口径原文=anyLast，实现取确定性写法 "
                "argMax(col, ingest_ts)（该表 ReplacingMergeTree 无版本参数，anyLast 跨执行不确定；"
                '二者同为"任取一版"口径非新造——见 14 号件 FIX-1）'
            ),
            "null_policy": "IS NOT NULL 且禁前向填充",
            "source_card_face": "data_binding.baseline_birth.piece_1_signal_face / piece_2_universe",
        },
        "universe_disclosure": {
            "n_symbols_min": int(n.min()),
            "n_symbols_median": float(n.median()),
            "n_symbols_max": int(n.max()),
            "n_symbols_first_day": int(n.iloc[0]),
            "n_symbols_last_day": int(n.iloc[-1]),
            "statement": "逐日截面票数只此记账，不进 value 列、不设筛阈（本班零自创判据）；"
            "截面塌缩若影响卡面判据，由开考读数与分数册承担，不由本件代裁",
        },
        "discipline": {
            "ch_writes": 0,
            "cards_modified": 0,
            "thresholds_written": 0,
            "hand_copied_column_lists": 0,
            "replaces": ".runtime/tmp/st-nightmine-20261010/derive_breadth_series.py（一次性件输出契约收编，根宪法 §4.1）",
        },
    }


def _write_series(out_dir: Path, column: str, frame: pd.DataFrame, meta: dict) -> Path:
    csv_path = out_dir / series_name(column)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["trade_date", "value"], lineterminator=chr(10))
        w.writeheader()
        w.writerows(_rows_from_frame(frame))
    # 逐列 provenance 不落盘：其内容全部可派生自汇总册 ti_ew_series_v1.meta.yaml
    # （根宪法 §4.2 内收判据"同真源可派生→必并"；04:2x 实测逐列 meta 与汇总册字段同集）
    return csv_path


def main() -> int:
    ap = argparse.ArgumentParser(description="技术指标族日频基序列物化（考试解锁②）")
    ap.add_argument("--mode", choices=("materialize", "verify", "census"), default="census")
    ap.add_argument("--origin", default=FAMILY_ORIGIN, help="卡面冻结族标（列集与窗从该族卡面派生）")
    ap.add_argument("--cards-dir", default=str(CARDS_DIR))
    ap.add_argument(
        "--out-dir", default=str(SERIES_DIR), help="默认=在册 SERIES_DIR（card_binding._load_csv_series 读取位）"
    )
    ap.add_argument("--start", default="", help="窗下界，缺省取卡面 in_sample[0]")
    ap.add_argument("--end", default=CLOSED_BOOK_CUTOFF, help=f"窗上界，硬上限=闭卷切点 {CLOSED_BOOK_CUTOFF}")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--meta-out", default="", help="汇总 meta 路径（缺省写 out-dir/ti_ew_series_v1.meta.yaml）")
    args = ap.parse_args()

    derived = derive_card_columns(Path(args.cards_dir), args.origin)
    by_col: dict[str, list[dict]] = {}
    for d in derived:
        by_col.setdefault(d["column"], []).append(d)
    start = args.start or min(d["in_sample_start"] for d in derived)
    end = min(args.end, CLOSED_BOOK_CUTOFF)
    if start > end:
        raise SystemExit(f"FAIL: 窗倒置 {start}>{end}")

    if args.mode == "census":
        print(
            yaml.safe_dump(
                {
                    "origin": args.origin,
                    "cards": len(derived),
                    "columns": len(by_col),
                    "window": [start, end],
                    "statuses": sorted({d["status"] for d in derived}),
                    "pairs": [{"card_id": d["card_id"], "column": d["column"]} for d in derived],
                },
                allow_unicode=True,
                sort_keys=False,
            )
        )
        return 0

    out_dir = Path(args.out_dir)
    if args.mode == "materialize":
        out_dir.mkdir(parents=True, exist_ok=True)
    metas: list[dict] = []
    drift: list[dict] = []
    for column, cards in sorted(by_col.items()):
        frame = fetch_daily_mean(column, start, end, timeout=args.timeout)
        meta = build_meta(column, frame, [c["card_id"] for c in cards], start, end)
        if args.mode == "materialize":
            path = _write_series(out_dir, column, frame, meta)
            metas.append(meta)
            print(f"wrote {path} rows={meta['rows']} span={meta['date_span']}", flush=True)
        else:
            fname = series_name(column)
            disk_path = out_dir / fname
            if not disk_path.exists():
                drift.append({"column": column, "drift": "absent_on_disk"})
                continue
            chk = repro_check(disk_path, frame)
            chk["column"] = column
            drift.append(chk)
    if args.mode == "verify":
        bad = [d for d in drift if not d.get("reproducible")]
        print(
            yaml.safe_dump(
                {"columns": len(drift), "not_reproducible": bad, "detail": drift}, allow_unicode=True, sort_keys=False
            )
        )
        return 1 if bad else 0
    summary = {
        "schema_version": "ti-ew-batch-meta/v1",
        "phase_version": PHASE_VERSION,
        "origin": args.origin,
        "window": [start, end],
        "columns_materialized": len(metas),
        "cards_covered": len(derived),
        "caliber_shared_by_all_columns": (metas[0]["caliber"] if metas else {}),
        "per_column_meta_materialized_separately": 0,
        "series": [
            {
                "column": m["column"],
                "rows": m["rows"],
                "date_span": m["date_span"],
                "closed_book_ok": m["closed_book_ok"],
                "universe": m["universe_disclosure"],
                "cards_bound": m["cards_bound"],
            }
            for m in metas
        ],
    }
    meta_out = Path(args.meta_out) if args.meta_out else out_dir / "ti_ew_series_v1.meta.yaml"
    with meta_out.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(summary, fh, allow_unicode=True, sort_keys=False, width=140)
    print(f"wrote {meta_out} columns={len(metas)} cards={len(derived)}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工 CLI 物化驱动器，非常驻自动系统
    sys.exit(main())
````

### `tests/gov/audit/test_ti_daily_mean_materialize.py`

磁盘字节 10274 ／ 复原字节（块体+末换行）10274 ／ sha256=`4d05469242c771aa1ab2cb34c15d71e847e37780ec96694fa468afb56f6269fd`

````python
# [MODULE] tests/gov/audit/test_ti_daily_mean_materialize.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/ti_daily_mean_materialize.py; pandas; yaml; pytest
# [CONSUMERS] pre-commit 自家测试批（与本件同袋的物化件 ti_daily_mean_materialize 的配对测试）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 零 CH 零网络（全部合成卡面/monkeypatch）；每条断言须能红；禁写生产路径（输出一律 tmp_path）
# [MODIFY-GUARD] 禁为过测试而在物化件内自定阈值或放宽列白名单
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红，禁 skip
# [TESTS] 本件即测试
# [TTL] task_bound
"""技术指标族日频基序列物化件契约测试：列从卡面派生 + 白名单拒判 + 双写拒判 + 输出契约 + 闭卷钳制。"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "audit"))
sys.path.insert(0, str(REPO / "scripts" / "backtest"))

import ti_daily_mean_materialize as ti  # noqa: E402


def _card(
    tmp_path: Path, card_id: str, column: str, *, origin=ti.FAMILY_ORIGIN, window=("2019-01-04", "2023-12-31")
) -> Path:
    p = tmp_path / f"{card_id}.yaml"
    p.write_text(
        yaml.safe_dump(
            {
                "card_id": card_id,
                "origin": origin,
                "status": "blocked_on_impl",
                "window": {"in_sample": list(window)},
                "oos_window_ref": ["2024-01-01", ti.CLOSED_BOOK_CUTOFF],
                "data_binding": {
                    "baseline_birth": {
                        "piece_1_signal_face": f"真源=c1_market.technical_indicator.{column}（符号引用禁抄值）"
                    }
                },
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return p


def test_columns_are_derived_from_card_face_not_from_a_list(tmp_path):
    """列集只能来自卡面引用原文：卡面写什么就物化什么（未在册的列由白名单腿拒，不是这里拒）。"""
    _card(tmp_path, "C1", "adosc")
    _card(tmp_path, "C2", "parkinson_20")
    derived = ti.derive_card_columns(tmp_path, ti.FAMILY_ORIGIN)
    assert sorted((d["card_id"], d["column"]) for d in derived) == [("C1", "adosc"), ("C2", "parkinson_20")]
    assert derived[0]["in_sample_start"] == "2019-01-04" and derived[0]["oos_end"] == ti.CLOSED_BOOK_CUTOFF


def test_other_origin_cards_are_not_swept_in(tmp_path):
    _card(tmp_path, "C1", "adosc")
    _card(tmp_path, "C9", "tsi", origin="some_other_batch")
    derived = ti.derive_card_columns(tmp_path, ti.FAMILY_ORIGIN)
    assert [d["card_id"] for d in derived] == ["C1"]


def test_multi_column_card_is_refused(tmp_path):
    p = _card(tmp_path, "C1", "adosc")
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    doc["data_binding"]["baseline_birth"]["piece_4_r_face_source"] = "另一列引用 c1_market.technical_indicator.tsi"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match="card_column_not_single"):
        ti.derive_card_columns(tmp_path, ti.FAMILY_ORIGIN)


def test_unfrozen_window_is_refused(tmp_path):
    _card(tmp_path, "C1", "adosc", window=("2019-01-04",))
    with pytest.raises(ValueError, match="card_window_not_frozen"):
        ti.derive_card_columns(tmp_path, ti.FAMILY_ORIGIN)


def test_empty_family_is_refused(tmp_path):
    with pytest.raises(ValueError, match="family_origin_not_found"):
        ti.derive_card_columns(tmp_path, ti.FAMILY_ORIGIN)


def test_series_name_carries_phase_version_and_bumps_with_it(monkeypatch):
    assert ti.series_name("adosc") == "ti_ew_adosc_v1.csv"
    monkeypatch.setattr(ti, "PHASE_VERSION", "ti-ew-v2")
    assert ti.series_name("adosc") == "ti_ew_adosc_v2.csv"  # 升版换名，禁原地改


def test_column_outside_schema_whitelist_never_reaches_ch(monkeypatch):
    """未证列必须在拼 SQL 之前被拒，且零查询外发（防"猜列名打库"）。"""
    calls = []
    monkeypatch.setattr(ti, "_schema_columns", lambda: {"ma_5", "adosc"})
    monkeypatch.setattr("fexam.ch_data.ch_query_df", lambda sql, **kw: calls.append(sql) or pd.DataFrame())
    with pytest.raises(ValueError, match="column_not_in_schema_whitelist"):
        ti.fetch_daily_mean("not_a_real_column", "2019-01-04", "2025-09-09", timeout=1)
    assert calls == []


def test_sql_carries_period_filter_and_no_literal_table_name(monkeypatch):
    captured = {}

    def fake(sql, **kw):
        captured["sql"] = sql
        return pd.DataFrame(
            {
                "c1": ["2024-01-02", "2024-01-03"],
                "c2": ["1.5", "2.5"],
                "c3": ["5100", "5101"],
            }
        )

    monkeypatch.setattr(ti, "_schema_columns", lambda: {"adosc"})
    monkeypatch.setattr("fexam.ch_data.ch_query_df", fake)
    frame = ti.fetch_daily_mean("adosc", "2024-01-02", "2024-01-03", timeout=1)
    sql = captured["sql"]
    from zephyr.data.table_registry import get_registry

    fqn = get_registry().table(ti.CATEGORY_ID)
    assert "period = 'daily'" in sql and "IS NOT NULL" in sql
    # 钉死去重口径：必须是按入库时刻取最新的确定性写法，不得回退 anyLast（跨执行不确定，04:05 复算实测判红）
    assert "argMax(adosc, ingest_ts)" in sql
    assert "anyLast(" not in sql
    assert f"FROM {fqn} " in sql  # 表名段只能由品类派生注入（本件源码零表名字面量，见下条断言）
    assert fqn not in (REPO / "scripts" / "audit" / "ti_daily_mean_materialize.py").read_text(encoding="utf-8")
    assert list(frame.columns) == ["value", "n_symbols"]
    assert frame.index[0] == pd.Timestamp("2024-01-02") and float(frame["value"].iloc[1]) == 2.5


def test_duplicate_trade_date_is_refused(monkeypatch):
    """双写面板若放行，下游按日计数翻倍——在册 30 倍放大事故同型，必拒。"""
    monkeypatch.setattr(ti, "_schema_columns", lambda: {"adosc"})
    monkeypatch.setattr(
        "fexam.ch_data.ch_query_df",
        lambda sql, **kw: pd.DataFrame({"c1": ["2024-01-02", "2024-01-02"], "c2": ["1.5", "1.6"], "c3": ["1", "1"]}),
    )
    with pytest.raises(SystemExit, match="重复 trade_date"):
        ti.fetch_daily_mean("adosc", "2024-01-02", "2024-01-02", timeout=1)


def test_empty_window_is_refused_not_silently_empty(monkeypatch):
    monkeypatch.setattr(ti, "_schema_columns", lambda: {"adosc"})
    monkeypatch.setattr("fexam.ch_data.ch_query_df", lambda sql, **kw: pd.DataFrame())
    with pytest.raises(SystemExit, match="零行"):
        ti.fetch_daily_mean("adosc", "2024-01-02", "2024-01-02", timeout=1)


def test_written_series_matches_the_seven_existing_csv_contract(tmp_path, monkeypatch):
    """输出契约与在册 7 枚序列逐字同形（trade_date,value／ISO 日），否则 _load_csv_series 读不进。"""
    frame = pd.DataFrame(
        {"value": [1.25, 2.0], "n_symbols": [5100, 5101]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    meta = ti.build_meta("adosc", frame, ["C1"], "2019-01-04", ti.CLOSED_BOOK_CUTOFF)
    path = ti._write_series(tmp_path, "adosc", frame, meta)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "trade_date,value"
    assert lines[1].split(",")[0] == "2024-01-02"
    assert all("," in ln and len(ln.split(",")) == 2 for ln in lines)
    loaded = pd.read_csv(path, index_col=0, parse_dates=True)
    assert list(loaded.columns) == ["value"] and float(loaded["value"].iloc[1]) == 2.0
    # n_symbols 只入 meta，绝不进 value 面
    assert "n_symbols" not in lines[0] and meta["universe_disclosure"]["n_symbols_min"] == 5100
    assert meta["closed_book_ok"] == 1 and meta["as_of"] == "2024-01-03"


def test_window_end_is_clamped_to_closed_book_cutoff(tmp_path, monkeypatch):
    """越过闭卷切点的窗必须被钳回——切点后数据不得参与判据面。"""
    _card(tmp_path, "C1", "adosc")
    seen = {}

    def fake_fetch(column, start, end, *, timeout):
        seen["window"] = (start, end)
        raise SystemExit("stop-after-window-check")

    monkeypatch.setattr(ti, "fetch_daily_mean", fake_fetch)
    sys.argv = [
        "x",
        "--mode",
        "materialize",
        "--cards-dir",
        str(tmp_path),
        "--out-dir",
        str(tmp_path),
        "--end",
        "2026-12-31",
    ]
    with pytest.raises(SystemExit, match="stop-after-window-check"):
        ti.main()
    assert seen["window"] == ("2019-01-04", ti.CLOSED_BOOK_CUTOFF)


def _frame(vals, days=None):
    idx = pd.to_datetime(days or ["2024-01-%02d" % (i + 1) for i in range(len(vals))])
    return pd.DataFrame({"value": list(vals), "n_symbols": [10] * len(vals)}, index=idx)


def _write(tmp_path, frame, column="x"):
    """用生产写手落盘，测试里不手写换行（工具层会折义字面量换行）。"""
    meta = {"column": column, "rows": len(frame)}
    return ti._write_series(tmp_path, column, frame, meta)


def test_repro_check_passes_on_exact_roundtrip(tmp_path):
    f = _frame([1.0 / 3, 2.0 / 3, 1e8 + 0.0482])
    path = _write(tmp_path, f)
    chk = ti.repro_check(path, f)
    assert chk["reproducible"] is True and chk["text_mismatch_days"] == 0


def test_repro_check_turns_red_when_underlying_data_moves(tmp_path):
    f = _frame([1.23456789012, 2.0])
    path = _write(tmp_path, f)
    assert ti.repro_check(path, f)["reproducible"] is True
    moved = _frame([1.23456789012 * (1 + 1e-6), 2.0])  # 表被外部重算，值动到第 10 位有效数字
    chk = ti.repro_check(path, moved)
    assert chk["reproducible"] is False and chk["text_mismatch_days"] == 1


def test_repro_check_turns_red_on_date_shift_and_missing_file(tmp_path):
    f = _frame([1.0, 2.0], days=["2024-01-01", "2024-01-02"])
    path = _write(tmp_path, f)
    shifted = _frame([1.0, 2.0], days=["2024-01-02", "2024-01-03"])
    chk = ti.repro_check(path, shifted)
    assert chk["reproducible"] is False and chk["index_identical"] is False
    assert ti.repro_check(tmp_path / "absent.csv", f)["reproducible"] is False
````

### `.runtime/tmp/st-examunlock-20261013/gen_status_flip.py`

磁盘字节 6608 ／ 复原字节（块体+末换行）6608 ／ sha256=`a57035489b779d5718cdd8d158ca3af7bf3bb937fa29f33bbba7a98c15fb1c22`

````python
"""一次性接线件（TTL）：20 张反向卡的 status 翻转＋开考点名清单产出。

卡面自书授权：`status_reason` "…物化接线跑通即转 preregistered 开考，禁改卡面"；
`impl_gap` "任一不通保持 blocked_on_impl，禁改卡面凑通"。
⇒ 本件只在**底座 CSV 已物化且 verify 通过**后运行，且只动两行：
   顶层 `status:` 与顶层 `status_reason:`；判据面（JUDGMENT_KEYS：window/buckets/pillars/
   pillars_numeric/target/oos_window_ref/hypothesis/card_id/node_id/family/signal_kind）
   逐字节不变，由本件断言自证（前后 sha 比较，除被允许的两行外零差异）。

用法：
  python gen_status_flip.py            # 干跑：打印每卡将改的两行与不变断言结果，零写入
  python gen_status_flip.py --apply    # 实改（须 --series-ok 传 verify 的通过凭据文件路径）
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

RUN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RUN / "scripts" / "backtest"))
sys.path.insert(0, str(RUN / "src"))
from fexam.card_binding import CARDS_DIR, JUDGMENT_KEYS  # noqa: E402

ORIGIN = "reverse_triage_batch3_20261012"
BOOK = RUN / "docs" / "_working" / "examunlock_campaign" / "03_binding_book_event20.yaml"
APPROVE = RUN / ".runtime" / "tmp" / "st-examunlock-20261013" / "approve_list_20.txt"
TOP_STATUS = re.compile(r"^status:\s*\S+\s*$", re.M)
TOP_REASON = re.compile(r"^status_reason:\s.*?$", re.M)

NEW_REASON = (
    "物化接线已跑通（{as_of}）：底座=scripts/audit/ti_daily_mean_materialize.py 产 "
    "docs/_working/nightmine_campaign/series/ti_ew_<col>_v1.csv，verify 面见 {verify}；"
    "绑定=docs/_working/examunlock_campaign/03_binding_book_event20.yaml 本格；"
    "卡面判据面（window/buckets/pillars/pillars_numeric/target）逐字节未改（G4-5）。"
)


def cards_of_family() -> list[Path]:
    out = []
    for p in sorted(CARDS_DIR.rglob("*.yaml")):
        try:
            c = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(c, dict) and c.get("origin") == ORIGIN:
            out.append(p)
    return out


def judgment_sha(card: dict) -> str:
    return hashlib.sha256(
        yaml.safe_dump({k: card.get(k) for k in JUDGMENT_KEYS}, allow_unicode=True, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verify", default="", help="verify 模式通过的凭据文件名（实改必填）")
    args = ap.parse_args()
    if args.apply and not args.verify:
        raise SystemExit("FAIL: 实改必须带 --verify <凭据件名>（卡面 impl_gap 要求先证①可复算）")

    book = yaml.safe_load(BOOK.read_text(encoding="utf-8"))
    bound = {e["card_id"] for e in book["entries"] if e.get("status") == "approved"}
    files = cards_of_family()
    missing_csv = []
    report = []
    for p in files:
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        cid = str(c["card_id"])
        blob = yaml.safe_dump(c.get("data_binding"), allow_unicode=True)
        col = re.findall(r"c1_market\.technical_indicator\.([a-z][a-z0-9_]*)", blob)
        fname = f"ti_ew_{sorted(set(col))[0]}_v1.csv" if col else ""
        csv_ok = bool(fname) and (RUN / "docs/_working/nightmine_campaign/series" / fname).exists()
        if not csv_ok:
            missing_csv.append((cid, fname))
        if cid not in bound:
            raise SystemExit(f"FAIL: 卡不在本班绑定册 approved 格：{cid}")
        before = judgment_sha(c)
        text = p.read_text(encoding="utf-8")
        n_status = len(TOP_STATUS.findall(text))
        n_reason = len(TOP_REASON.findall(text))
        if n_status != 1:
            raise SystemExit(f"FAIL: 顶层 status 行数非 1（{n_status}）：{cid}")
        new_reason = NEW_REASON.format(as_of="2026-10-13", verify=args.verify or "待跑")
        out_text = TOP_STATUS.sub(lambda _m: "status: preregistered", text, count=1)
        if n_reason == 1:
            out_text = TOP_REASON.sub(lambda _m: "status_reason: " + new_reason, out_text, count=1)
        after = judgment_sha(yaml.safe_load(out_text))
        report.append(
            {
                "card_id": cid,
                "base_csv": fname,
                "series_present": csv_ok,
                "status_line_count": n_status,
                "status_reason_line_count": n_reason,
                "judgment_sha_before": before,
                "judgment_sha_after": after,
                "judgment_face_unchanged": before == after,
                "changed_line_count": sum(
                    1 for a, b in zip(text.splitlines(), out_text.splitlines(), strict=False) if a != b
                )
                + abs(len(text.splitlines()) - len(out_text.splitlines())),
            }
        )

    bad = [r for r in report if not r["judgment_face_unchanged"] or r["changed_line_count"] > 2]
    print(yaml.safe_dump({"cards": len(report), "series_missing": len(missing_csv),
                          "judgment_violations": bad[:3],
                          "sample": report[:2]}, allow_unicode=True, sort_keys=False).strip()[-1200:])
    if missing_csv:
        print(f"FAIL: {len(missing_csv)} 张卡的底座 CSV 尚未物化，禁翻状态（卡面 impl_gap）")
        return 2
    if bad:
        print(f"FAIL: {len(bad)} 张卡判据面/行数断言不过")
        return 3
    if args.apply:
        for p in files:
            c = yaml.safe_load(p.read_text(encoding="utf-8"))
            text = p.read_text(encoding="utf-8")
            new_reason = NEW_REASON.format(as_of="2026-10-13", verify=args.verify)
            out_text = TOP_STATUS.sub(lambda _m: "status: preregistered", text, count=1)
            if len(TOP_REASON.findall(text)) == 1:
                out_text = TOP_REASON.sub(lambda _m: "status_reason: " + new_reason, out_text, count=1)
            assert judgment_sha(yaml.safe_load(out_text)) == judgment_sha(c), p
            p.write_text(out_text, encoding="utf-8", newline="\n")
        print(f"applied: {len(report)} cards flipped to preregistered")
    APPROVE.parent.mkdir(parents=True, exist_ok=True)
    APPROVE.write_text("\n".join(r["card_id"] for r in report) + "\n", encoding="utf-8", newline="\n")
    print(f"approve list → {APPROVE} n={len(report)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````
