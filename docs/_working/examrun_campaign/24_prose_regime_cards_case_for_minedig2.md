---
ttl: task_bound
title: 卡面 window.regimes 写成散文串＝判官出分前崩（案卷，路由挖矿二班）
created: "2026-10-13"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 一、一句话与路由

dev 卡册 526 张里有 **22 张把 `window.regimes` 写成散文串**，判官代码对它调 `.items()` ⇒
**出分前 `AttributeError`**（不是"判 fail"，是"根本出不了分"）。
路由：**挖矿二班**＝这 22 张卡的属主（统筹 02:0x 裁）；
"判官侧把崩溃变成明确报错、禁静默把散文当字典吞"＝另随**判官域下一袋**，本班不代改。

# 二、形态普查（本班自己的尺，零 CH）

尺＝`git show dev:` 取卡面字节后 `yaml.safe_load`，只看 `window.regimes` 的 Python 类型：

| 形态 | 张数 |
|---|---|
| dict/list（在册可读形） | 318 |
| 无该字段 | 186 |
| **str（散文串）** | **22** |

- **22 张全部是今日新增**（其余 504 张零命中）：`TDM-E-L1-S2/calibration/17..36_ind_*_high_event` 20 张
  ＋ `…/38_agg_limit_days_monthly`、`…/39_intraday_tpl_blocked` 2 张。
- 典型样例（可 grep）：`window.regimes: 'bull: 2019-01-04..2021-06-30（流动性牛）；bear: 2021-07-01..2024-01-31（贴现率熊+微盘熊）——逐字继承 16 卡先例窗'`。
- 复算尺（零 CH，可一行验）：
  `git ls-tree -r --name-only dev docs/03_modules/_domain_backtest/exam_cards` 取全集，
  逐件 `git show dev:<path>` 后 `yaml.safe_load`，判 `window.regimes` 的 Python 类型即可
  （今日新增面用 `git log --since=2026-10-12 04:00 --diff-filter=A --name-only dev -- <该目录>` 取）。
  本班一次性产物：`.runtime/tmp/st-examrun-20261012/devface_regress_census_0148.yaml`
  （注意 `.runtime/tmp` 是 24h TTL 暂存面，长命真源是本件表格与上列命令，不是那个文件）。

# 三、代码位（静态读，未运行任何测试）

`scripts/backtest/fexam/calibration_exam.py`（dev 面）四处直接把该字段当映射用：

```
179:    regimes = card.get("window", {}).get("regimes", {})
181:    for name, span in regimes.items():          # str.items() → AttributeError
215/217: 同上（面板路）
404:    for seg_name, span in (card.get("window", {}).get("regimes") or {}).items():
762:    for name, span in (w.get("regimes") or {}).items():
```

⇒ 散文串不是"读数变差"，是**考尺在出分前抛异常**；若届时有人为了跑通而"顺手放宽/跳过 regime 柱"，
就变成放水——所以转换必须只改**数据形状**，见第五节两条防线。

# 四、转换配方：本班不代证

统筹转述：**考试解锁班已交"散文 regime → 在册结构"的转换配方＋"转换后判 fail 非 pass"的反凑通证据**。
本班按"引用必先 grep 到命中"的规矩核过：该原文**目前在 dev 面 grep 不到**
（`docs/_working/mineloop2_campaign/00_morning_pack.md` 内仅 1 处 `regimes`，且是另一议题
`_span_dates` 只取串内前两日期、多段危机窗被静默弃——那条与本件无关，别混引）。
⇒ 故本班**不抄写、不代其举证**；挖矿二班实施时请直接引用解锁班落地件的**路径＋节号**，
并在其落地后由本班把指针补进本件（现在留空是诚实，不是遗漏）。

# 五、转换时的两条防线（防"改形状"顺带"改判据"）

1. **只改形状不改语义**：regime 名与窗起止须与卡面散文**逐字对应**（`bull 2019-01-04..2021-06-30`、
   `bear 2021-07-01..2024-01-31` 等），禁借转换挪窗、改名、增删段；转换后 diff 只应出现"结构与缩进"变化。
2. **转换后判 fail 就是 fail**：不得因"刚转换"给豁免、不得把 regime 柱列入 `not_judged_pillars` 蒙过；
   本班 §9.3/§廿二 那两根 ICIR 钉同理适用——不可判必须显形为"未判面"，不能消失。
3. 开跑前做**零 CH 全链预演**（在册新成例）：卡面装载 → 判官分派 → 出分不落库，先把这类
   `AttributeError` 在非生产路径上暴露，而不是等真开考时才发现。

# 六、本班边界（申明）

不改他班卡面一个字节、不动任何判据阈值或窗口、不代解锁班出配方；本件只交
"哪些卡／什么形态／什么后果／怎么复算／转换时的两条防线"。
出处：班账 `docs/_working/examrun_campaign/00_ledger.md` §廿三（供题 22 张落地面）／§25.8（转正卡分类）；
普查件 `.runtime/tmp/st-examrun-20261012/devface_regress_census_0148.yaml`。
