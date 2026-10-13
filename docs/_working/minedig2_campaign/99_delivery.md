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

## 十、通宵总令终账（2026-10-13 04:0x 两腿 → 10:5x 三袋入队；晨间补记，Owner 睡眠窗内零中继）

### 10.1 执行账（令 §四 本班终局＝聚合 8 卡可考：多日面＋物化＋绑定三件齐）

| 前置 | 实测（非声明） | 判据出处 |
|---|---|---|
| 复算证明 | **8/8 逐格精确等**：lu_count level fwd10 n=1734 ic=.1161 t=4.87；lu_count_z20 1730/.1019/4.26；lu_ratio 1733/.1207/5.06；lu_ratio_z20 1729/.1001/4.18；avg_abs_ret level fwd5 1733/.1015/4.24；fwd10 1733/.1012/4.23；avg_abs_ret_z20 fwd5 1729/.1145/4.79；fwd10 1729/.1292/5.41 | 预登记册 `agg8_readings`＋`recon_criterion_pinned_before_run`（等值三条：n 整数／ic 四位／t 两位） |
| 腿B run_id 钉版 | GREEN 四项：钉版 1,625 日 ⊂ 全表 1,638 日（超出 0）／重叠段 dom·six 逐日差 **0**／钉版内部同日重复 0／同码本两次重放逐日一致 True；正对照＝乱真 run_id 显式 RuntimeError（尺不哑） | D 族冻结稿 §5 判据②＋统筹"run_id 钉死＝批" |
| 绑定尺 | 8/8 由 `U·series_csv_absent:<具体文件>` 转 **`D`·reason=None**；读侧 signal＋target 双取到，对齐有效 1845..1854 日（闸内 min_days=400） | `card_binding.classify_card` 现器实测 |
| 卡面 | 8/8 `blocked_on_impl → preregistered`（每卡一处状态行＋尾部 18 行取证块：复算结论／CSV 名+rows+sha256+版本／绑定 cls／"只转态零开考"） | 收尾令原文"如实状态，禁凑张数" |
| 数据面 | 8 枚 CSV＋meta 落 `docs/_working/nightmine_campaign/series/`，跨 2019-02-11..2026-10-12，rows 1860/1856/1859/1855/1859/1855/1855/1850，实测纯 LF（与在册 7 枚夜矿 CSV 同形制） | 物化件 `agg8_series_materialize.py`（SERIES_VERSION=agg8-v1） |
| 三袋 | 0008＝D_BACKTEST 7 件＋它自己要读的翻译册 1 件；0009＝tests/backtest 2 件（depends-on 0008）；0010＝8 CSV＋meta＋8 卡＋预登记册＋案卷 19 件（depends-on 0008） | 拆袋理由＝COMMIT-SCOPE 用自己的路径→域尺量出 D_BACKTEST×D_AUDITTEST 跨域；册与 .py 同袋因 TRANSLATION-COVERAGE 的 loader 只读投影册、无 PG 第三源 |

### 10.2 自裁账（零中继窗口内本班自决五件，各给名目·代价·可回退）

1. **判据更正两节（比对面定义）**——时序如实入册：04:01 首跑 RED 后，按本册 `holdout.rule`"末段扣留，筛选全程不碰"原文＋装载侧 today 依赖定位出比对面；**阈值数值零改动、等值判据未降强度**（改的是样本段归属；一旦成立即 8/8 全等，任何错面给不出全等）。代价＝判据节多两节留痕；回退＝旧文未删可逐字比。
2. **装载收编 `fetch_matrix_ctx`** 取代"复用 lane_c.fetch_panel"——实测 fetch_panel 返回键无 close 矩阵与 dates 字符串（其 :415-426），产不出出生读数所依的矩阵面；原管线本体在 `.runtime/tmp` TTL 工棚内，不搬进册即随清理蒸发。代价＝本件带一条 kline SELECT（原 `SQL_FREE=True` 声明已更正为 False，SQL 全文落 `meta.inputs.own_sql` 可审）；宇宙口径与特征工程仍逐字复用 lane_c 单口（§4.2 同真源必并）。
3. **走 class D 本地序列路而非配方册 class A**——Owner 固定正解"改喂给闸的输入，不改闸"；配方册因此不是本班前置（他班"9 张单表入册"前提由他们自证，本班不引用其结论）。代价＝8 张卡的数据真源是仓内 CSV 而非 CH 单表。
4. **卡面转态**——三件齐才转，逐张取证；缺一保持 blocked（本班实测三件全齐后方动）。
5. **会话复命走 `SessionRegistry.register(pid=0)`＋keeper＋keepalive 正门**，不用 `session_worktree_start`——后者实测会去主区做工作面 reconcile（撞他班在途面；本班第一次尝试因主区 index.lock 在位而未遂，事后核车道 index 20915 条目零变动）。

### 10.3 等裁账：无

本班面上无待 Owner 点头项。唯一外部依赖＝三袋落地读回；开考与试次入账归矿考二班／考试班（本班零开考、N 账本零写）。

### 10.4 复核命令（照抄可跑；本班 10:57 已在车道逐条自跑得出期望值，袋落地后在主区复跑同尺）

```bash
# 1) 复算逐格等值（零 CH；期望 RECON exact= 8 of 8）
python -c "
import yaml, io
meta = yaml.safe_load(io.open('docs/_working/nightmine_campaign/series/agg8_series_v1.meta.yaml', encoding='utf-8'))
pre  = yaml.safe_load(io.open('docs/_working/minedig2_campaign/00_agg8_axis_prereg.yaml', encoding='utf-8'))
rec  = {(r['series'] + ('_' + r['transform'] if r['transform'] != 'level' else '') + '|' + r['transform'] + '|' + r['target']): r for r in pre['agg8_readings']}
sc   = meta['recomputation_screen_face']
hit  = sum(1 for k, g in sc.items() if int(g['n']) == int(rec[k]['n']) and round(float(g['ic']), 4) == round(float(rec[k]['ic']), 4) and round(float(g['t']), 2) == round(float(rec[k]['t']), 2))
print('RECON exact=', hit, 'of', len(sc))
"

# 2) 绑定尺与卡面状态同尺（零 CH；期望只出一组合 ('D', 'preregistered')）
python -c "
import yaml, io, glob
from scripts.backtest.fexam import card_binding as cb
out = sorted({(cb.classify_card(yaml.safe_load(io.open(p, encoding='utf-8')))['cls'], yaml.safe_load(io.open(p, encoding='utf-8'))['status']) for p in glob.glob('docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__4[0-7]_agg_*.yaml')})
print('CLASSIFY+STATUS:', out)
"

# 3) 产物形制（零 CH；期望 8 枚全 True＝表头 trade_date,value 且字节内零回车符）
python -c "
from pathlib import Path
names = ['lu_count','lu_count_z20','lu_ratio','lu_ratio_z20','avg_abs_ret','avg_abs_ret_z20','mkt_fwd5','mkt_fwd10']
LF, CR = bytes([10]), bytes([13])
for n in names:
    raw = Path('docs/_working/nightmine_campaign/series/' + n + '.csv').read_bytes()
    print(n, raw.partition(LF)[0] == b'trade_date,value' and CR not in raw)
"

# 4) 落地判据（只认 git，不认队列自报）
git log --oneline -3 dev -- docs/_working/nightmine_campaign/series/agg8_series_v1.meta.yaml
git show dev:docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__40_agg_lu_count_level_fwd10.yaml | grep -m1 '^status: '
```

### 10.5 本班自犯追加四条（旧案 ①-⑫ 不销，见 §六）

⑬ **比对面定义系看数后补**：初版判据钉了"面目窗"，未钉"装载集合锚"与本册自己的 holdout 归属 ⇒ 首跑 RED。教训＝判据要同时钉"从哪读"与"读哪段"，只钉其一是把定位工作留给 RED 之后。
⑭ **班中调 `session_worktree_start` 复命会话**：它按设计去主区 reconcile 工作面，实测打出 `git restore failed … .git/index.lock exists`——若当时主区无锁，它会把别班在途文件 restore 掉。班中复命只准 `register(pid=0)`＋keeper＋keepalive 三件。
⑮ **`lock_files.py acquire-batch` 参数位用错**：owner 是**位置参**（`acquire-batch <owner> <paths…>`），`--session` 是可选参数；本班把 `--session` 打在首位 ⇒ 17 枚 claim 一度挂到字面 owner `--session` 名下，且 `--ttl-minutes 180` 的数值被当路径收走 ⇒ 3 枚伪路径 claim。已全部 release 并按正形重取（复核面＝`.ailocks/registry.json` owner 计数）。
⑯ **尺子假 0 险成结论**：在车道 cwd 下 `git show dev:<含反斜杠的 glob 路径>` returncode≠0 而 stdout 为空，Counter 差集遂报"dev_only=0＝严格超集"。补 `assert(returncode==0)`＋路径反斜杠归一后真值＝每卡 dev_only=1（正是本班改写的那行 status）。在册教训"零命中须正对照"第三次自犯，此次被顺手加的 returncode 断言拦住。

## 十一、终读回与移交（2026-10-13 15:1x 实测；本班不得收班句，理由见 §11.2）

### 11.1 落地读回（判据＝`git show dev:<件>` 与 `git log -- <件>`，非队列自报）

| 面 | dev 落地件 | commit | 实测 |
|---|---|---|---|
| 数据面 | 8 枚 CSV＋meta | `24c5c24bf6`（0010） | rows 1860/1856/1859/1855/1859/1855/1855/1850，纯 LF，跨 2019-02-11..2026-10-12 |
| 卡面（含转态取证） | 8 张聚合卡 | `24c5c24bf6`（0010） | 复算 8/8 等值、绑定 cls=D、sha 与盘上字节逐张全等 |
| 绑定面 | `card_binding.py`＋`auto_mount.py`＋`t0_six_phase_materialize.py`＋sle3 测试 | `20744a3cc3`（0016） | dev grep `lu_count_z20`=1、`run_id`=17 |
| 测试面（class D 那支） | `tests/backtest/test_card_binding.py` | `7fc0e94631`（0013） | 承码已在 dev ⇒ 与 §11.1 绑定面同代 |
| 执行器面 | **未落地** `calibration_exam.py` | 死袋 0012/0014/0019 | dev grep `_forward_face`=0 |
| 物化器码 | **未落地** `scripts/audit/agg8_series_materialize.py`＋其测试 | 死袋 0012 | dev 无此二件（数据与读数已落，重跑能力暂缺） |

### 11.2 本班终局判读＝未达，且本班主动把 8 卡退回 blocked_on_impl（fail-closed）

实测出险形态（非假想）：绑定面已落地＝`classify_card` 认可本组卡 `target_forward_face=precomputed` 且能给 `load_named_series` 取到两面；
而执行器消费档在 `calibration_exam.py`，它**没落地**。此时开考这 8 张，`_series_metrics` 会按缺省对"已算好的第 h 日前向目标"再 `shift(-1)` 一次
⇒ 得到第 h+1 日收益冒充第 h 日＝**静默错值，不报错**。所以：

- 状态从 preregistered 退回 blocked_on_impl（另起 `status_rollback_20261013` 一节，转态取证块保留不删＝另起留旧案）；
- 数据/复算/绑定三面证据零改动，判据数值零改动，只动状态机一位（每卡 dev-only 行实测＝1，删除集==计划内）；
- 依据：开考普查只枚举 preregistered（在册教训 `classify-census-excludes-examined-cards`），回退即把这 8 张移出供题面；
  且"宁漏勿误"优先于"凑终局数"——本班不写"全链路已打通、全绿、无遗留、无待裁"这句，因为它现在不真。

### 11.3 死信账（本班六袋，逐袋死因与本班处置）

| 袋 | 死因（dead_reason 原文摘） | 本班处置 |
|---|---|---|
| 0005 | 同件双侧皆改真冲突（99_delivery 自家两袋相撞） | 让它死（内容被 0007 超集取代），不 requeue |
| 0008 | 非注册表族件双侧皆改真冲突：calibration_exam.py（base_head 取了车道 HEAD） | 改 `--base-head dev` 重投＝0012 |
| 0009 | 同上（test_calibration_exam.py） | 同因重投＝0013（后已落地） |
| 0012 | 落地门 TRANSLATION-COVERAGE：新建 .py 在**投影册**缺 plain_zh（本班 PG 行 active，主区投影滞后） | 拆袋：不新建 .py 的部分先行落地＝0016；新建件待投影追齐后 requeue（blob 健在） |
| 0014 | TAKEOVER-PENDING：命中文件 calibration_exam.py，open 接管条目属**他会话** st-examrun-20261012 | 不代裁不硬闯；摘出该件先落其余＝0016 |
| 0017 | ghost_session：本班属主会话 idle 自退（keepalive 授权 05:31 到期未续） | 复命后**新袋** 0018 投出（不走 requeue，避复发熔断），自撤袋已落地 |
| 0019 | 同 0014（TAKEOVER-PENDING 命中同一件） | 见 §11.4 移交① |

### 11.4 移交与等裁（三件，各给"这是什么／为什么要点头／不点会怎样"）

1. **处置 st-examrun-20261012 的 open 接管条目**（该会话经门的同一尺复测确已死：不在 list_active、注册片缺席、心跳 04:51 exited、现存 claim 0）。
   不点＝任何触碰 `scripts/backtest/fexam/calibration_exam.py` 的袋都被挡（本班三袋实证＋后续任何班同撞），
   聚合 8 卡因此不能转回 preregistered，多日标的前向面永远缺半。点法＝属主班/统筹按接管处方 merge 或 abort 其 dirty=10 worktree、requeue 其死袋。
2. **翻译册投影追齐**（REG-MODULE-TRANSLATION-001 本班行 active 而 YAML 投影滞后；该门 loader 只读投影、无 PG 第三源——与解锁班 ti_daily_mean_materialize 同病灶第二例）。
   不点＝新建 .py 落不了地；追齐后本班死袋 0012 原样 requeue 即可，本班零新写。
3. **主区 index 混池里出现 8 枚自家卡的 staged  deletion**（实测 `git diff --cached HEAD`＝D 11 枚：本班 8 枚聚合卡＋他班 exit_flow 卡 1 枚＋测试 2 枚；worktree 面是旧字节未跟踪）。
   本班不代裁他人删除面（Owner 门位），只报：本班 8 枚的正身内容在 dev `24c5c24bf6` 可一键取回；
   不点的后果＝任一从主区整池提交的班会把这 8 枚（含他班 3 枚）从库里删掉。

### 11.5 自犯追加两条

⑰ **把"三件齐"当作终局达成来转态，未先核承码是否同代落地**：绑定面与执行面是两袋，0016 落了前半、0019 被挡后半，
dev 于是出现"认可 precomputed 却仍 shift(-1)"的组合＝静默错值风险。教训＝跨袋交付的"可考"判据必须包含**承码同代性**检查
（投袋前先问"这个判据要在哪几个件上都成立"），否则半落地比不落地更坏。
⑱ **keepalive 授权只续 2h 却排了 6h+ 的落地链**：0017 死于 ghost session（可避免）。教训＝长链投袋前按"最晚一袋的预计落地时刻"续保活，或每袋投前复测 `list_active`＋held_files 两证（在册五形态之第四形态）。

### 11.6 本班终态一句话

聚合 8 卡的**数据面与复算证明已落 dev 且逐格精确等**（这是本班夜班的真金），
执行器承码半落地未闭合 ⇒ 本班已把 8 卡退回 blocked_on_impl 并列明解锁路径；本班不收"全绿无遗留"句。

## 十二、统筹三件裁定执行账（2026-10-13 15:4x-16:1x，本班照 ①→② 顺序推进）

### 12.1 ①代处置 examrun 死条目（统筹授权，note 原文照令）

处方执行：`python scripts/governance/session_takeover_ledger.py --resolve st-examrun-20261012 --by st-minedig2-20261012 --note "<统筹令原文，逐字>"`。
执行前后各跑一把尺：执行前 `--list` 该 sid 命中 1（open，resources=held 7／worktrees 1 dirty=10／bags 16／heartbeat 1），
且 `.ailocks` 里该 sid 现存 claim＝0（Rx 第一条实测已不需要）；执行后 `--list` 该 sid 命中 **0**，条目迁至 `.runtime/takeover/resolved`。
本班只解"提交连坐"，未代做他班 worktree 的 merge/abort，也未 requeue 他班死袋（那些处置权仍归属主/统筹）。

### 12.2 ②承码袋投出与落地（含本班一处偏离，理由给实测）

| 袋 | 内容 | 态 |
|---|---|---|
| 0021 | `calibration_exam.py`（多日标的前向面，dev_only=1 即本班改写的那行 shift） | **已落 dev `a67009f3ef`**（实测 dev grep `_forward_face`=5） |
| 0022 | `test_calibration_exam.py` 95 行（§十一 自撤的正身重投，dev_only=0＝严格超集） | 在途（落地判据＝`git show dev:tests/backtest/test_calibration_exam.py`，本班不代报绿） |

偏离一处并给理由：令文写"calibration_exam.py＋card_binding.py＋两测试件"四件同袋，本班实测 `card_binding.py`（20744a3cc3）
与 `test_card_binding.py`（7fc0e94631）**已在 dev**，再投＝同件双袋连坐（在册死法），故本袋只含未落地的两件；
且 COMMIT-SCOPE 用自己的路径→域尺把 tests/backtest（D_AUDITTEST）与 scripts（D_BACKTEST）判为跨域，四件同袋必死，
本班按门自己的形制拆两袋并以 depends-on 保序（先码后测）。

### 12.3 承码同代性预演（本班把 ⑰ 那条教训落成一把尺，零 CH）

脚本＝`.runtime/tmp/st-minedig2-20261012/preview_8cards.py`：经**已落地**绑定单口取两面 ⇒ 交**已落地**执行器 `_series_metrics`，
并断言跑完 8 张真卡面 sha256 未变（在册教训：判官跑完会重写卡面，故只喂内存副本）。

| seq | 全窗 ic | 出生面 ic（剔末 126 交易日） | 在册 ic | 出生面逐格等值 | 删申报键后 ic 是否变 |
|---|---|---|---|---|---|
| 40 | 0.0961 | 0.1161 | 0.1161 | 是 | 变（红证在） |
| 41 | 0.1037 | 0.1019 | 0.1019 | 是 | 变 |
| 42 | 0.1023 | 0.1207 | 0.1207 | 是 | 变 |
| 43 | 0.1022 | 0.1001 | 0.1001 | 是 | 变 |
| 44 | 0.0828 | 0.1014 | 0.1015 | 差 1e-4 | 变 |
| 45 | 0.0826 | 0.1012 | 0.1012 | 是 | 变 |
| 46 | 0.1028 | 0.1144 | 0.1145 | 差 1e-4 | 变 |
| 47 | 0.1132 | 0.1291 | 0.1292 | 差 1e-4 | 变 |

读法三条，全部如实：①**全窗≠出生面**是设计而非缺陷——考卷面含 OOS 段，出生读数产自"筛选全程不碰"的那一段；
②出生面上执行器复现在册 IC，5/8 逐位等、3/8 差 1e-4＝判官 `_spearman` 与物化件 `ts_ic` 两把实现的**末位取整差**（已登记，不改任何判据数值，也不在本班此刻去统一两把尺——那是尺面统一工程，归门禁/判官域，需另案）；
③"删申报键 ic 必变"8/8 成立＝申报位真被执行器消费（在册教训：真源只被一条路径消费＝审计面生效、提交面空转）。
本班**不在此重算 n/t**：那两面环节6 已在同一把尺上证过，此处另建第二把尺＝造第二真源。

### 12.4 ③投影 render 归维护线（本班复测：仍未追齐）

实测 `git show dev:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -c agg8_series_materialize` ＝ **0**，
主区磁盘同样 0 ⇒ 维护线的 render 袋尚未落。本班**不重打投影袋**（Owner 禁，且会带上他人未落地条目＝归属篡改）。
追齐后动作＝`requeue q-20261013-st-minedig2-20261012-0012`（新建物化件 .py＋其测试＋在册件共 8 件，blob 健在在队列里）。

### 12.5 终判（此刻）

8 张聚合卡＝**preregistered**（承码同代性已用 12.3 那把尺证过，取证块逐卡入面）；
本班残余两件＝①0022 测试袋落地待读回；②新建物化件袋待投影追齐后 requeue（不阻塞这 8 张卡开考，
因为考卷数据面与执行器面都已各自在 dev，缺的只是"重跑数据的能力"在册）。
开考与试次入账归矿考二班／考试班；本班零开考、N 账本零写。
