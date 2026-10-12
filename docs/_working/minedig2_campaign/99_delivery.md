---
ttl: task_bound
title: 挖矿二班收班交付（st-minedig2-20261012）——聚合 8 卡入池＋D 族资格四件全绿
created: '2026-10-13'
session: st-minedig2-20261012
order: 挖矿二班题库收尾令 2026-10-12
status: class_closed_pending_landing
---

# 99 收班交付

## 一、交付终态（两件按序）

| 令件 | 交付物 | 状态 |
|---|---|---|
| §二.1 聚合 8 条立卡 | 8 张卡入待考池（S2/calibration 40-47）＋断言轴集预登记册同批 | ✅ 已写盘并入队（q-20261013-st-minedig2-20261012-0001）；**8/8 如实 `blocked_on_impl`**，零张写 preregistered |
| §二.2 D 族资格验收 | 冻结稿 §5 四件跑完一轮＝**四件全绿**，D1 情绪六段资格成立；记录件＋两处纯追加回执 | ✅ 同上袋入队 |

⚠ 本件写作时队列 head 是**他班**袋（st-mineloop2-…-0014，已等 27 分钟），本班袋落地前 `git log -- <路径>`
仍是零命中 ⇒ 落地判定只认下面"复核命令"，不认本件自述。

## 二、三清单

### A. 新增（11 件，全部经 batch_creation_tokens 意图 API 登记，PG 账本 status=active）
- `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__40_agg_lu_count_level_fwd10.yaml`
  ～ `__47_agg_avg_abs_ret_z20_fwd10.yaml`（8 张，序号 40-47；37 号前班已 same_proposition_dedup 删除、38/39 在册，
  本班从 40 起接，`ls` 实测 40+ 原为空）
- `docs/_working/minedig2_campaign/00_agg8_axis_prereg.yaml`（断言轴集预登记，合法 YAML 可 safe_load）
- `docs/_working/minedig2_campaign/10_dfamily_qualification_acceptance.md`（验收记录本体）
- `docs/_working/minedig2_campaign/99_delivery.md`（本件）

### B. 追加（2 件，git diff numstat 实测 deleted=0）
- `docs/_working/2026-10-12-d-family-qualification-freeze-draft.md`：+25 行 −0 行，`## ` 节数 7→8（§8 验收回执，
  §1–§7 与 frontmatter `status: draft_for_ruling` **未动**——本班不自代 Owner 转态）
- `docs/_working/2026-10-12-exam-card-mining-meta-method-research.md`：+15 行 −0 行，节数 10→11
  （§9 表内":174 六段规则未冻结＝无考试资格"原行**保留不改**，另起 dated 节记反证指针）

### C. 未动（明确不碰，防连坐与归属篡改）
`capability_canonical_file_registry.yaml`（render 净增 75 行含他人登记，Owner 禁重打投影袋在册）、
`docs/_working/t0_matrix/six_phase_history_v1.*`（他班 st-t0-matrix 在飞面，本班物化产物全写
`.runtime/tmp/st-minedig2-20261012/replay/`）、`scripts/backtest/fexam/*`（矿考二班/考试班在飞）、
`TDM-E-L1__ablation__02`（他人卡面，禁改）、`scan_ledger_minedig_20261012_p*.jsonl`（前班账本 6 行字节未动，
本班另起新分册 `scan_ledger_minedig2_20261013.jsonl`）、`ruling_registry.yaml`（不代签）、生产表零写、
`n_trial_ledger` 零写。

## 三、复核命令（Owner/统筹逐条可自证，勿信本件转述）

```
# 1) 8 张卡是否真在 dev（落地判据只认这条）
git log --oneline -1 -- docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__40_agg_lu_count_level_fwd10.yaml
git show dev:docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__47_agg_avg_abs_ret_z20_fwd10.yaml | head -5

# 2) 卡面读数=筛级真源？（期望 8 行全 True；纯子串判据，免正则折叠陷阱）
python - <<'EOF'
import json
from pathlib import Path
src = Path(r"D:/ZephyrAlpha/.runtime/nightmine_exploration/agg_series_minedig_20261012.json")
rows = json.loads(src.read_text(encoding="utf-8"))["daily_pass"]
cards = sorted(Path("docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1")
               .glob("*__calibration__4*_agg_*.yaml"))
print("cards", len(cards), "readings", len(rows))
for r in rows:
    hit = [c for c in cards if f"_{r['series']}_{r['transform']}_{r['target']}.yaml" in c.name]
    if not hit:
        print(r["series"], r["transform"], r["target"], "match= NO CARD FILE")
        continue
    flat = " ".join(hit[0].read_text(encoding="utf-8").split())
    print(r["series"], r["transform"], r["target"], "match=",
          f"IC={r['ic']}" in flat and f"t={r['t']}" in flat and f"n={r['n']}" in flat)
EOF

# 3) 预登记闸未被看数后改（应 True）
python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path(r'D:/ZephyrAlpha/.runtime/nightmine_exploration/prereg_minedig_20261012.yaml').read_bytes()).hexdigest().startswith('89652c3b'))"

# 4) 绑定尺对 8 张卡的自判（应 8/8 cls=C reason=target_face_not_index_next_day；零 CH）
cd scripts/backtest/fexam && python -c "import sys,glob,yaml,io; sys.path.insert(0,'.'); sys.path.insert(0,'..'); import card_binding as cb; [print(cb.classify_card(yaml.safe_load(io.open(f,encoding='utf-8').read()))['reason']) for f in sorted(glob.glob('../../../docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/*__calibration__4*_agg_*.yaml'))]"

# 5) D 族资格四件（重放幂等：两次独立重建逐字节相同）
python scripts/audit/t0_six_phase_materialize.py --out-dir .runtime/tmp/<你的目录>/r1
python scripts/audit/t0_six_phase_materialize.py --out-dir .runtime/tmp/<你的目录>/r2
diff -q <r1>/six_phase_history_v1.csv <r2>/six_phase_history_v1.csv   # 应无输出
# 前缀截断（PIT）：load_phase_panel(start,end) 三个 cut 与全窗重叠段 dominant/six 标签差应为 0

# 6) 追加件是否纯追加（deleted 必须=0，节数 7→8 与 10→11）
git diff --numstat HEAD -- docs/_working/2026-10-12-d-family-qualification-freeze-draft.md
```

## 四、证据分级（自跑／读码／转述，禁混级）

| 结论 | 等级 |
|---|---|
| 8 张卡 cls=C 目标面拒绑 | **自跑真门**（classify_card 逐张执行） |
| 卡面 n/ic/t 与筛级全等 | **自跑**（脚本对拍 8/8，一次因本班正则漏缩进假报 8 红，修尺后全绿） |
| 重放幂等、跨时对照、正对照、码本普查、前缀截断 | **自跑**（3 次物化通道＋4 次面板重建＋4 条只读 SQL） |
| `_REGISTERED_TABLES` 3 表、`_series_metrics` shift(-1)、`ic_ir=None`、`_unjudged_pillars` | **自读 HEAD 源码行**（card_binding.py:259-277/316-325/338-355；calibration_exam.py:154-156/184/296-298） |
| 卡 38/02/17 形制、母卡门柱值 | **自读在册卡面** |
| 漂移守卫 12 passed | **自跑 pytest**（零 CH） |
| 前班"63 读数""7 序列" | **实测否证**（产物实数 45 日频＋1 月度＝46；docstring 与实载不符已留案） |
| "五未冻点 A×5 已入册" | **实测查无**（ruling_registry 内 2026-10-12 零命中，正对照五条在册裁定各命中 1）——令卡所载，本班不代签，归统筹/册主 |

## 五、待呈菜单（要 Owner/统筹点头的，按"这是什么／为何要点／不点会怎样"）

1. **执行器多日标的前向面是否立项**（新发现，最治本）。
   是什么：考卷执行器只会算"次日"目标（`_series_metrics` 硬编码 `shift(-1)`），绑定尺也把非"指数次日收益"
   一律拒绑（cls C）。本班 8 张卡判的是 5 日/10 日面。
   为何要点：挖矿班批的"聚合 8 条"是真金（8 条全过预登记日频闸，t 4.18-5.41），但**结构上考不了**。
   不点会怎样：这 8 张与任何未来 5/10 日卡永远 `blocked_on_impl`，供题再多开考数仍为 0；
   与前班 20 张反向卡不同解——那 20 张只差"物化＋入配方册"，本批做尽那两件仍堵在这面。
   代价：动 `card_binding.py`/`calibration_exam.py` 两个多班共触件（矿考二班/考试班在飞），须按 §一 排队隔窗。
   可回退：改动可 revert，且不回改任何已出分卡。
2. **六段 run_id 钉版是否补做**。是什么：现在"同码本"靠全表 dominant 零分歧＋分歧即报错两防线，
   装载口不钉 run_id（函数自述原文）。为何要点：一旦新 run 与旧 run 同日分歧，重建会整体罢工。
   不点：资格今天绿，但绿在一块没钉死的底板上。代价：改 `auto_mount.load_phase_panel`（做 T 链与 5 条考卷共读）。
3. **落台件安置**（根宪法 §9.4）。`docs/_working/` 里的逐日六段件被 5 条 production 考卷当真源读；
   工作区件按纪律要 promote 才算交付。不点：production 消费面继续指向 task_bound 区。
4. **裁定 A×5 入册**（§四 末行）。令卡说入了，册上查无；本班按草案默认 A×5 跑，判据文字未改。
   不点：D 族资格"成立"这一条在裁定面上仍无署名依据。
5. **本班 8 张卡是否需要"降级为次日面重考"**（备选，本班不建议）：把 fwd5/fwd10 换成次日面即可今天开考，
   但那是改命题迁就执行器＝自拟判据，本班不做。

## 六、事故与本班自犯（全留案，不销账）

1. 尺误报①：判"聚合读数分母"先写了 63（照抄管道 docstring 的"7 序列"），实测产物＝5 序列 45 读数 ⇒ 更正并在
   预登记册登记 docstring 与实载不符（不改他人件）。
2. 尺误报②：`ruling_registry` 我第一版正则尾部多写引号 ⇒ 5 条在册裁定全报 0（假红）；
   改用 `ruling_id: 裁定#(229|304|325|501|502)\b` 后各命中 1。
3. 尺误报③：自写对拍脚本漏 YAML 折叠换行的缩进 ⇒ 8/8 假报 mismatch；加 `\s*` 后 8/8 全等。
4. 尺误报④（对下游危害最大的一次）：验 CREATE-GUARD 的 PG 正证时把卡路径拼错（漏 `agg_` 段）⇒
   差点得出"8 卡未正证"的错结论；改用真实文件名重测＝10/10 正证、未登记负对照正确不认。
5. 自误读：见 run_id 普查最大 2026-10-12 与面板末日 2026-10-09 曾写"矛盾"，实为 PIT 切尾一行，已当场更正入案。
6. 袋型死信 1 次：`git_commit` 消息引用了 `tests/...test_auto_mount_sle3.py` 路径而袋内无代码件 ⇒
   MESSAGE-CLAIMS-CODE-BAG-EMPTY 拒；按处方补 `[docs-only]` 显式申报后过（未删引用、未加塞代码件）。
7. 入队死信 2 次：从主区跑 `commit_queue.py enqueue` 被 WORKTREE-REQUIRED 拦（处方给的旗 enqueue 不认）⇒
   改在车道内跑（队列根 `_strip_lane_prefix` 车道感知，仍归主队列），两次入队合成一袋 12 件。
8. 账本未取证项：本班 CH 查询**条数**未取证（`system.query_log` 在 00:00-00:25 窗内 count()=0，
   含无过滤总数 ⇒ 日志面不可用，不能据此判"零查询"也不能反报一个数）。已在本班分册登记为
   `ch_proof_status` 未取证，只登记可数的执行次数（3 次物化通道＋4 次面板重建）。

9. 登记通道异常 1 次：本件（99_delivery）走 `batch_creation_tokens.py` 时 register 成功而
   `publish_snapshot` 在 `src/zephyr/governance/registry_ledger/baseline.py:814` 抛异常（首跑可见 traceback，
   重跑报"无待登记文件（全部已登记）"）。判定面复确认＝直接调门自己的 PG 第三源
   `create_guard._pg_confirmed_token_files`，本件与另两件 campaign 文件三条全认 active，未登记探针路径正确不认。
   ⇒ 本班不据此判"已登记"为假，但**快照发布面是否完整**归册主车道复看（非本班能自解，亦不拆旗绕过）。

10. 交付件内命令失真 4 处，全部当场"自抽自跑"抓到并修好（本件的复核命令按可跑形态留档）：
    ①47 号卡文件名在命令里漏写 `abs_` 段 ⇒ 路径不可 grep 即失真；
    ②对拍块里我写的反斜杠 b 经多层转义在文件里变成**退格控制符**（肉眼与 grep 均不可见），
      正则静默失效报 8/8 False，且该转义位在中文标点前语义不稳 ⇒ 整块改为**纯子串判据**，
      并跑"从本文件抽出该块再执行"至 8/8 True 才留稿；
    ③命令 #2/#3 原用相对路径读 `.runtime/nightmine_exploration/…`，而该真源只在**主区** .runtime（车道内无此件）
      ⇒ 改绝对路径后 eval 实跑＝True；
    ④命令 #4 的 glob 相对深度多写一层（fexam→仓根实为三层，我写四层）⇒ 空集会假绿，修正后实跑 8/8
      reason=target_face_not_index_next_day。
    ⚑计数自证：本件 §六 共 10 条（其中 10 含四个子项），袋文"自犯九条"系写作时旧计数，以本件为准。

## 七、残余（本班未闭合的，如实）

- 8 张卡开考数＝0（缺口在 §五.1 那面），待考池只完成"供题到位"。
- D 族资格"成立"仍是**本班执行记录**，裁定署名与 A×5 入册归统筹/册主。
- 队列在途：本班袋 q-...-0001 落地与否须自证（§三.1）；若死信则按 dead_reason 对症另投，不盲重投。
- 车道：`ai/st-minedig2-20261012/task-minedig2-closeout` 上有两笔车道提交
  （8454f66de5 卡袋／6a37fcd38c 验收袋），落 dev 走队列正门，**未在脏主区做 merge**（在册禁忌）。
