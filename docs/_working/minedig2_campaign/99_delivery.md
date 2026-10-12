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
## 八、裁定投递核对（2026-10-13 01:12 事件，本班零动作）

01:12 本班收到一条抬头为「统筹裁定 · 矿考二班」的批复，正文＝路径 1 批（给 production 风控件加
`graduation_face='absent'` 显式档，署名批准＋Owner 否决窗，今夜备好补丁明晨投）＋路径 2 留档＋路径 3 永不特批
＋04:00 后 07 重读照计划自走＋"解析器盘点 518→12→8、三处消费者改法＝验收"。

**本班判定＝投递对象错，未据此执行任何动作**，依据三条实测：
①正文所指对象（`src/zephyr/risk/core` 生产风控件、`graduation_face`、07 五态锚定卡、解析器盘点、"甲案申报文字"）
在本班全部案卷（预登记册／验收记录／本件／8 张卡）**零命中**——本班尺正对照在岗：同尺能命中本班真读数
（8/8 classify 结果、四件读数、`agg8_readings` 八格）；
②本班从未跑过所述"日频面 step 不动 vs 笔级数据晋升"对照实验，也未做过 518→12→8 的解析器盘点；
③本班 00:57 呈上的菜单是另一套五项（①立项多日目标面 ②先钉 run_id ③A×5 签署归属 ④按下不表 ⑤先看数字），
编号与正文内容不同型——巧合在"路径 1/2/3"这层编号，不在内容。
⇒ 已向统筹确认，回复＝**误投，应转矿考二班，本班待命**。

纪律落点（为什么不"照着做一件相近的"）：`src/zephyr/risk/core` 是他班属主的实盘风控件，
按根宪法 §5/§9.11 与在册禁忌（他人在飞件与属主面不代改、指令真源须经认证通道），
猜测式执行会把别人班的生产改动算进本班 commit＝归属篡改；本班不越此线，亦不拆他班自己钉的禁令。
本班仍待命的两件真缺口不变：多日目标前向面（决定 8 张卡能否开考）与六段 run_id 钉版（决定幂等是否钉死）。

本袋态存证（写作时实测）：q-20261013-st-minedig2-20261012-0001 仍 pending，队列 12 袋在途本班居末，
`git log -- 卡40 路径`＝空（未落 dev 如实）；心跳 daemon 已于 00:57 复岗（pid 27292，前一双拍 00:08 因
idle>1800s 自退）；01:00-04:00 让路窗内本班零 CH 零开考。
## 九、统筹三裁执行账（2026-10-13 本班 01:12 呈报后接令（令面无时戳，锚点实测），本班按序办）

| 裁 | 本班动作 | 实测读数 | 落地态 |
|---|---|---|---|
| ①多日面＝立项批（归本班） | 纯追加可选档：`calibration_exam._forward_face`＋`card_binding._declared_forward_face`；缺省路径逐字不变，申报且自洽才免二次位移 | 三套测试合跑 **111 passed**（零 CH，合成注入；含本班新增 19 支红绿双向）；8 张卡复测 cls 由 C 转 **A? table_not_in_recipe_book**（目标面开、数据面照拦）；正对照＝删两键即回 C，既有 178 张 preregistered 卡零影响 | **今夜只备好不入队**（令文"明晨 Owner 无否决即投"）；共触三枚多班在飞件，投前先复测在途袋 |
| ②run_id 钉死＝批 | `_snapshot_rows(start, end, run_id=None)` 等值谓词＋形态闸（^[A-Za-z0-9._-]{1,64}$）；`load_phase_panel`/物化件 `--run-id` 同形追加；钉版轮才落 meta `pinned_run_id` | 缺省 SQL 与改前**逐字同形**（测试断言整串相等）；钉版 SQL 含 `AND run_id = 'VAL-P0-20260916-230726'`；注入面 5 形态全拒且零查询下发；缺省转调仍两位置参（不破既有 stub 签名） | 同①袋待投；真 CH 复跑（钉版重放 vs 全表重放逐日对拍）按让路窗推迟到 04:00 后 |
| ③A×5＝统筹补签、本班走正门 | 取号器 `--claim` 占 509-513（O_EXCL，无撞号）→ PG 账本 `api.register` 五条全 OK → 册字节纯追加 → 裁定袋单独入队 | 册 `git diff --numstat`＝**+100/−0**、entries 复解析 330 条、ruling_id 键集合差新增 5 消失 0；PROTECTED-PATHS 的裁定通道在 worktree 面失配（命中面是车道绝对路径 vs approved_paths 相对 posix，HEAD 面本班数得 12 条 active 覆盖该册）⇒ 按正门标记载体 [ARCH-APPROVAL:#ARCH-381] 走，未用环境变量拆闸 | 已入队 q-20261013-st-minedig2-20261012-0006。**落地态如实：本班写本行时（实测 01:55:01）dev 面按 `ruling_id` 主键逐号（509／510／511／512／513）grep＝0 命中 ⇒ 仍在队列在途，未落地**；判定只认 `git log --oneline -1 -- <册路径>` 与该逐号 grep 复测（非本行转述） |

卡面同步追加（零门柱改动）：8 张卡各加两枚机读申报位 `target_forward_face=precomputed`／`target_horizon_days={5|10}`
（插在 signal_kind 之后），②状态的可复核口径以**尾追加键 `status_update_20261013`** 承载；
卡面原文 `status_reason` 与 `impl_gap` 一字未动——首版就地改写被落地仲裁点名（"dev 在你基底之后新落的 2 行
不在这份字节里"，本袋自有实核：dev_only 行改写前=8 件×2、改后＝**0**），故改形制不改内容。
判据位数值、窗口、分桶、牛熊段零改动（逐张打印比对）；变换以幂等脚本
`.runtime/tmp/st-minedig2-20261012/amend_cards_tail.py` 承载，二跑 0 rewrite＝源面与盘面同形（防"假留证"）。
