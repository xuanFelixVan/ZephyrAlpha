---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
---

# 图书馆幽灵面与馆页漂移班 · 班账（st-libstale-20261013）

授权来源：Owner 2026-10-13 夜《通宵授权总纲》＋统筹 23:4x《图书馆令》（对本班四项裁定的执行令）。
本账=本班唯一过程真源；终报以本账为准，跨上下文压缩时接手先读此页。

## §1 门蓝图（LIBRARY-TRI-CONSISTENCY 的设计位）

- 对象：`src/zephyr/gov_enforcement/commit_gates/library/library_tri_consistency_gate.py`。
- 病根：`scripts/governance/generators/check_library_tri_consistency.py` 三层断言器（账↔视图↔盘）
  已在盘、已有 14 支测试，但**零执法面**——全仓仅 capability/module_translation 两册提到它，
  名册/门码/队列链无一消费 ⇒ 检查器是"只写报告没人看"的观察件。
- 本门=把它挂进 in-process 名册（收编既有检查器，不立第二真源），名义接替 2026-09-23 退役的
  LIBRARY-COVERAGE（退役理由=warn-only、0 拦截、0 消费方；本门补上的正是"消费方"这一环）。
- 形态：warn-only 影子，观察窗 2026-10-14→2026-10-21（7 天）。
- 零写承诺：门内**不调** `run_tri_check`（它会写 `docs/_working/ultimate_library/TRI_CONSISTENCY.md`），
  改为直取该模块 `_SQL_ALL`+`check_ledger_vs_view`+`check_view_vs_disk` 两个纯函数——
  常量与谓词零复制，落盘零新增。
- 分级判据（结构分级，不造数值阈值）：
  - `[账↔视图]` 族=**lag 级**（视图是上次再生产物，账在两次提交间继续长，结构上必非零）
    → 只进审计 jsonl 计数，不打 warn 行；
  - `[视图↔盘]`、`[regen]` 族=**warn 级**；
  - 附加只读面：`git status --porcelain -- docs/library` 非空 ⇒ "再生成面未随批落地"=warn 级。
  - own-scope：仅当本次袋触碰 `docs/library/` 时 warn 级才成行（宪法 §3.1/§3.4），
    外来脏面只计数入审计，不连坐。
- 回退判据（一行）：`in_process_gate_registry.yaml` 本条 `enabled: false`，或
  `python scripts/git_commit.py --session <sid> --files <两册> --message ...` 反悔袋；
  观察窗内若出现任一以 `LIBRARY-TRI-CONSISTENCY` 为 dead_reason 的失败袋 ⇒ 立即置 false 并留证。

## §2 本班自裁清单（简单面，逐条理由＋依据＋可逆锚点）

| # | 自裁事项 | 理由与依据 | 可逆锚点 |
|---|---|---|---|
| S1 | 读侧存在性判读只圈 `kind∈{file,doc,module}`，命名空间型/含冒号 home 恒不判 | 把"账本没这个概念"读成"资产已消失"比漏标更致命；判据不确定即不判 | revert 袋 q-20261014-st-libstale-20261013-0001 |
| S2 | 缺省只标注不剔除，剔除走 `--hide-missing` 旗 | 零行为变化起步，观察窗后再看是否改默认 | 同上 |
| S3 | `state` 源① 加尾标但 **has 语义不动** | 三源独立性属统筹令"方案③不落地"，本批不得顺手改判据 | 同上 |
| S4 | 门用结构分级（lag 级/warn 级）而非数值阈值 | 数值阈值＝判据数值变更＝复杂面留裁；结构分级可当场自裁且不含发明数字 | YAML `enabled: false` |
| S5 | 门不调 `run_tri_check`（避免写 _working 报告） | 提交链内写共享追加型文档=连坐与归属篡改风险 | 同上 |
| S6 | `generator_registry.library_index` 只补 `trigger_sources=[db:lib_assets]`，不翻 `regen.enabled` | 施工前实测：该字段唯一消费者=`reconcile_generators.reconcile(source)`（`scripts/governance/reconcile_generators.py:599`），全仓无一名调用方发该 id ⇒ 纯声明零行为变化；`_is_stale`（同文件 :693-711）只读 `input_sources` 的 `yaml:` 前缀，不受本字段影响 | 该两行 revert 即回旧态 |
| S7 | 机生投影两册（`capability_canonical_file_registry.yaml` 令牌面、`module_translation_registry.yaml`）本班**不入袋** | 实测 diff：前者 +73/−5 行、后者 +19 行，其中夹带 st-bakdr/st-condaxis/st-deadmass/st-goaldef 等他班物化行；袋=整档快照，随袋提交=归属篡改（在册铁律：需要该册变更的件另起袋）；本班令牌与翻译行已入 PG，落地门可读 | 不动盘即无锚；如需投影面单独成袋 |
| S9 | 袋②首投被 CREATE-GUARD MAP-MOUNTS 拦死后的对症两步：①`api.update` 只改**本班自己那条** token 条目（CAS v1→v2）补 `no_mount_reason`（先例=在册 56 条同字段，非节点图资产走逃生面留季度复核审计）；②在主区跑 `registry_projection_generator --registry-id REG-CAPCAN-001 --render` 把投影追齐 | 在册定案同型：CREATE-GUARD 的 token 存在性有 PG 第三源，但 **map_mounts/no_mount_reason 字段只从主区投影盘面读**（`create_guard.py:738-770` 锚 anchor_main_root，`:911-920` 按 file 建索引）——登记完即被"投影滞后假拦"，正解=render 追齐后原袋复投；本区写盘前已用 `--project-root` 探针目录先算差分=**+133 行/−0 行纯追加**（他班字节零丢失），并对 `docs/.../capability_canonical_file_registry.yaml` 做 HEAD 侧同尺复核亦 +133/−0；索引面（他会话 staged 字节）未被触碰（状态仍 MM） | 投影是 PG 纯函数，任何后续 render 归一；条目 revert=`api.update` 去掉该字段（v3） |
| S8 | 读侧判读白名单外一律不判（含 table/registry/task 等 6 kind） | 见 S1；另实测 active 行中 home 为盘符绝对路径者=0，故盘符分支今日无消费面，仍保留防仓外资产面复发 | 同 S1 |

## §3 跳过留裁清单（复杂面，逐条建议＋代价面）

| # | 跳过点 | 建议 | 代价面 |
|---|---|---|---|
| K1 | `regen.enabled=true` 与 `trigger_sources` 是否升 enforce | 观察窗后按 lag 族分布再裁 | 现在翻=每天多一批脏馆页待人工提交，且生成器会写 lib_assets 行 |
| K2 | 5,086 条幽灵行撤账（真撤账＝账本注销） | 见 §4 只读定性后按族分批改判 | 不撤则读侧永远背着 11.7% 的假在编 |
| K3 | LIBRARY-COVERAGE 复活 enforce | 本门稳定 7 天后合并为同一 enforcement 面 | 名册净增 1 条（本门）＋退役条目仍占行＝名义净零需 Owner 认 |
| K4 | `state` 三源独立性（数值判据） | 方案③已出，待裁后再动码 | 现尺在噪声串上给 rc=0，负存在断言仍不可作准 |
| K5 | CLI 4.1s 性能（进程内仅 0.78s，大头在 CLI 启动路径） | 另批 profiling | 慢是"没人用单口"的主因之一 |
| K6 | Qoder 侧挂钩（`.zcode/config.json` 的进门闸在 Qoder 不生效） | 若要让进门闸真拦 Qoder 会话＝权限档变更，属 Owner | 现状=宪法 §0 第 6 步仅文字义务 |
| K7 | CAPABILITY-LOOKUP 判据（"有记录即放行"） | 若要限定"必须命中图书馆"＝判据变更 | 现状=21 次 CLI vs 5,373 次嵌入式探针 |
| K8 | **机生统一册不可复现**：`generate_gate_registry.py` 重跑即净删 2 台门行（POOL-REGRESSION-DIRECTION、STRATEGY-CARD-LIFECYCLE-MAP） | 根因实测=`extract_commit_gates` 用 `_RE_GATE_ID.search(text)` 每台模块只取**第一个** `gate_id="..."`（`scripts/governance/generators/generate_gate_registry.py:112,152`），而本仓有 8 个"一文件双工厂"门先例 ⇒ 姊妹门行每次重生必消失。修法=改 `.finditer` 逐工厂出行（读侧扩展非判据变更，但会**净增**多台门行进统一册，且 total_gates 计数随之变）| 本班因此**未提交**重生后的 gate_registry.yaml（已还原 HEAD 字节）。夹钳：GATE-21 触发面含 `commit_gates/*.py` 与 `_registry/catalogs/*.yaml` ⇒ 新门不重生被拦、重生则净删他班门行撞 REGISTRY-MASS-DELETION——两头都需 Owner 定性 |
| K9 | **采集链复活已注销行的 SQL 仍在岗**：`ledger_schema.py:127` `status = EXCLUDED.status` 无 COALESCE（同句其余字段全有 COALESCE 保护） | 一字段改动即治本；但属写侧口径变更＝复杂面留裁。实测受害：46 行有 delete 事件而 status 仍 active；115 幽灵行 `built_at>10-09`；4,119/4,783 幽灵 `generation≥10` | 一行 revert |
| K10 | **`--feeds` 供数反查面是死面**：`potential_consumers` 非空行数=0（全表，非仅 active），故门面 FRONT_DOOR 第 5 行"数据表真源/裁定#410 增枝"永返空 | 供数轴重建＝写侧采集器改造（另役）；本班只在报告标注"该单口不可作准" | 不改码无锚 |
| K11 | `tests/` 幽灵撤账（4,783 条，97.5% 属"删过/搬走过而账未撤"） | 见 §4；真撤账须 authority+Owner 裁定在册（`retire_module.py:379-393` 要求裁定 status=active）且无自动 reconciler ⇒ 属治理面 | 未动一行账 |

## §4 只定性结论（不撤账）

分母：`status='active'` 且 kind∈{file,doc,module} 共 43,367 行，其中 home 盘上与 git HEAD 均无=
**5,085～5,086 行（11.7%，两次独立测量差 1 行，活跃工作区下的正常抖动）**；`tests/` 下=**4,783（94%）**，
tests/ 外仅 ~302 条（0.7%）。

| 族 | n | 占比 | 定罪证据 |
|---|---|---|---|
| (a) 曾在 git、后被删 | 4,088 | 85.5% | 删除集中 **10-05=2,679 / 10-06=1,359**（我本人 `git log --all --no-renames --diff-filter=D -- tests/` 复核，与探查班同口径），10-09 当日=0 |
| (b) git 从未有过 | 119 | 2.5% | 注册 09-22→10-13 仍在新增；采集自盘上瞬态 |
| (c) 搬走后的旧路径 | 576 | 12.0% | 同名对偶件在跟踪面存在（如 `tests/intelligence/test_news_score_daily.py`→`tests/ai/intelligence/…`） |

**结论一（改判我班前判）**：10-09 tests 树事件**不是**主因——主因是 `st-tests-chief-20261004`
的"旧路径删除"波次（10-05/10-06）删了树但**从未撤账**，(a)+(c)=4,664=**97.5%**。
**结论二**：4,571/4,783（95.6%）幽灵在跟踪面有同名对偶 ⇒ 机判可配 `successor_of` 的面积很大。
**结论三（撤账可行性）**：可行但须分族——(c) 576 条可按同名对偶自动挂后继注销；(a) 4,088 条
须"删除证明+无后继"批量注销且要 authority 在册；(b) 119 条先查队列 blob（实测 112/119 有活体
blob，(c) 560/576 有，(a) 仅 420 有活体但内容在 git 史）再判复活或注销。
**结论四（机制缺位）**：唯一合法注销口=`Librarian.act("delete")`→`librarian.py:197` 执行
`_SQL_MARK_DECEASED`（`ledger_schema.py:150-151` 写 deceased+disposition_authority+successor_of），
authority 由 `validate_action`（`ledger_schema.py:221`）强制"delete 时必填"；
**无任何 reconciler 自动化注销**（`library_regen_reconciler.py:122-140` 只 collect+upsert）。
active 行里 `successor_of` 非空=**0/43,919**，tests/ 已注销=4 条。
**结论五（复活链仍在岗）**：`ledger_schema.py:127` `status = EXCLUDED.status` 无 COALESCE
（同语句其余字段全有保护）⇒ 采集器省略 status 即把 deceased 洗回 active；见 K9。

## §5 交付与自测

**读侧 recall 定性（本班新尺，E1）**：同一 `lookup_assets` 总口——
token 形态查询（`batch_creation_tokens/process_pool/session_worktree/git_commit/kill_switch`）**5/5 命中**；
散文形态（`暂存区 无主 staged 巡检` 等 5 条 + 两个中文单词）**7/7 全 0**。
⇒ 嵌入式探针 96.2% 零命中的主因不是索引缺件，而是**查询形态错配**：agent 用散文提问，
账本按路径 token 匹配。修法属另一条线（词表归一轴 G15-① 只覆盖登记过的术语）。

**性能定性（E1，进程内 vs CLI）**：`import zephyr.library.lookup` self≈0.01s、
`lookup_assets()` 0.78s、而 CLI 单次 **≈4.1s** ⇒ 大头在 CLI 启动/引导路径而非查询本身（K5）。

**自测清单**：
- 目标两支册：`test_lookup_on_disk_marker.py` 12 支 + `test_library_tri_consistency_gate.py` 13 支 = 25 passed。
- 馆内全套：`tests/ai/library/` + 门册 = **258 passed, 4 skipped, 1 failed**；
  唯一失败=`test_importtime_cumulative_significantly_dropped`（import 预算 467/295ms > 235ms），
  **已 A/B 证伪与本班无关**：未改动的主区面同尺复现红（两次 295.4/259.3ms），非我引入。
- 判别力自证（每把尺都见到红形态）：读侧 M1（判读面扩 table）/M2（白名单旁路）/M3（相对路径恒 present，
  7 支红）；门侧 block 模式必判红 + "未知族不得归 lag" 反向用例。
- 名册实装：`auto_register_gates` loaded=**100**，本门在列，priority=142 无撞号（`[measured]`）。
- 首袋死信对症：GATE-PRECOMMIT-RUN 抓到我自己 3 处裸 Any（`check_any_abuse.py` 复跑=clean），
  按"修码不弱闸"处置，未加 noqa 豁免、未改判据。

**结构自证**：`99_delivery.md` 更正行 +10/−0、标题数 9→9、旧案卷 L44 原样在位（追加不改写）。

**袋况（02:4x 实测，`ls .runtime/commit_queue/{pending,processing,dead}` + `git show dev:` 双尺）**：

| 袋 | 内容 | 态 | 死因/说明 |
|---|---|---|---|
| -0001 | ①读侧（2 件） | **dead** | GATE-PRECOMMIT-RUN→`gate-any-abuse`：我自己 3 处裸 Any（`check_any_abuse.py` 复跑已 clean）。修码非弱闸，未加 noqa |
| -0002 | ②影子门（6 件） | **dead** | CREATE-GUARD MAP-MOUNTS：新 .py 的 token 条目缺挂图申报；且 map_mounts/no_mount_reason **只从主区投影盘面读**（PG 第三源只证 token 存在性）——在册"投影滞后假拦"同族。对症见 S9 |
| -0003 | ①+②+文档合一（10 件，严格超集） | pending | 修好 MAP-MOUNTS 后原袋可直接落 |
| -0004 | ①独立袋（2 件） | pending | 拆袋防②连坐① |
| -0005 | 标签纠偏（3 件） | pending | `[视图↔盘]` 真标签 19 处 |

**刻意未做的两件事（有理由，非遗漏）**：① 未提交机生统一册 `gate_registry.yaml`——重跑生成器会净删两台
双工厂门行（K8，根因 `generate_gate_registry.py:152` 用 `.search()` 每台只取首个 gate_id），已还原 HEAD 字节；
② 未 `session_worktree.py archive` 收车道——三袋仍在飞，"袋在飞禁放锁"，落地后由下一班或本班续班清。


## §6 下一班最值钱的一刀（本班实测定位，未施工）

**病灶**：图书馆"查不到中文/散文"的根因不是词表小，而是**两半没接起来**——

| 半边 | 在册量 | 实测形态 |
|---|---|---|
| 资产总账 `lib_assets`（借阅轴） | active 43,919 行 | `title` 全填充，但填的是**文件名 basename**（实样：`home=src/zephyr/governance/audit/cross_layer_contract_signature_reconciler.py` → `title='cross_layer_contract_signature_reconciler.py'`）；`one_liner` 几乎全空（file 43/33,340、module 605/3,879、doc/registry/task/table=0） |
| 翻译册 `module_translation_registry.yaml`（血肉轴） | `entries` 8,118 行 | **8,116 条有 name_zh、8,118 条有 plain_zh**（BLOOD-FLESH/TRANSLATION-COVERAGE 两道门逼出来的散文，就躺在这里没人查） |

**实测后果（E1）**：抽 5 条在册 name_zh 去总口查——`H1 Redis 热缓存/跨层契约/能力Heatmap/运行时Planes` 四条 **0 命中**，只有英数混排的 `Invariants` 命中（因为它是路径子串）。
与 §5 的形态二分互证：token 形态查询 5/5 命中、散文形态 7/7 全 0；探针月内 5,481 次里 96.2% 返回 0。

**一刀**：采集器把 `module_path → name_zh/plain_zh` join 进 `lib_assets.title/one_liner`（供数轴已具备
`Librarian.act('update')` 回读原字段的用法先例=ulib3c 班"误签 59 条回写"同法）。收益面≈3,879 个 module
行 + 潜在 8,118 条散文；不动判据、不动门禁、可整批 revert。**代价与前置**：①必须同批改 `ingest_with_shrink_guard`
的供数轴口径，否则 title 变长会让"账面收敛"再次被采集器复活（§4 结论五同族，`ledger_schema.py:127`）；
②`generate_library_index.py` 馆页会因 title 改变而重排，馆页数字/顺序变化=预期行为，须随批再生成提交。

**判据红线**：本条属"读侧供数"，不改任何阈值与执法面；但若施工时想顺手把 `--feeds`
（K10：`potential_consumers` 全表 0 行非空=死面）一起救活，那要单独呈批——它是写侧采集器改造。



## §7 复核命令（**须在主区跑**：车道 HEAD 落后 dev，行号与读侧面均以落地面为准）

```bash
cd /d/ZephyrAlpha
# ① 读侧存在性标注：反（幽灵必标）/正（存在件不误杀）/剔除
python -m zephyr.library.lookup "test_stage3_vault_mtime_and_verdict" --no-alias
python -m zephyr.library.lookup "card_binding" --no-alias            # 两支均无尾标
python -m zephyr.library.lookup "test_stage3_vault_mtime_and_verdict" --no-alias --hide-missing
# ② 影子门分级（[账↔视图]→lag 只审计，其余→warn）
python -c "from zephyr.gov_enforcement.commit_gates.library.library_tri_consistency_gate import _split_pillars as s;print(s(['[账↔视图] x','[视图↔盘] y']))"
# ② 名册实装数
python -c "from pathlib import Path;from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry as R;from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import auto_register_gates as a;x=R();a(x,Path.cwd());print(len(x.list_gate_ids()),'LIBRARY-TRI-CONSISTENCY' in x.list_gate_ids())"
# ④ 幽灵分族分母（只读 SQL；主区实测 43367/5084/4783，活跃工作区下 ±2 属正常抖动）
python - <<'PY'
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g, release_depgraph_pg_connection as r
import os
c = g()
try:
    with c.cursor() as cur:
        cur.execute("select home from public.lib_assets where status='active' and kind in ('file','doc','module')")
        rows = [x[0] for x in cur.fetchall()]
    miss = [h for h in rows if h and ':' not in h and not os.path.exists(h)]
    print("RESULT total=%d miss=%d tests_miss=%d" % (len(rows), len(miss), sum(1 for h in miss if h.startswith('tests/'))))
finally:
    r(c)
PY
# K9 复活链是否仍在岗（应见 status = EXCLUDED.status 且无 COALESCE）
grep -n "status = EXCLUDED" src/zephyr/library/ledger_schema.py
# K10 供数反查死面（应见 0）
python -c "from zephyr.governance.depgraph_schema import get_depgraph_pg_connection as g;import os;c=g();cur=c.cursor();cur.execute(\"select count(*) from public.lib_assets where coalesce(array_length(potential_consumers,1),0)>0\");print('nonempty potential_consumers =',cur.fetchone()[0])"
```

## §8 K8/K9 治本交付与一条系统性拆袋律（统筹裁定②③，10-14 01:3x→01:5x）

### 8.1 K8 统一册重生不再净删他门（裁定②，前提半证伪已如实改报）

- 修法按令执行：`generate_gate_registry.py` 弃"每台模块只取首个 gate_id"，改**两遍**——
  第一遍与旧尺逐字节同（122 台主台行零改写），第二遍只登第一遍未认领 id，gate_id 两种写法
  （字面 / 常量绑定 `gate_id=_X_GATE_ID`）全收。实测在册：多 id 模块 10 台。
- **裁定②"净增 2 行"被实测改判为 1+1**：两台里只有 POOL-REGRESSION-DIRECTION 是真门
  （in_process 名册 enabled:true，`auto_register_gates` 装载面实见 priority=161）；
  STRATEGY-CARD-LIFECYCLE-MAP **无源**——同名模块在 commit_gates/ 下于 HEAD 树与全史
  `git ls-tree -r`／`git log --all --diff-filter=D` 双向零命中（从未实现，非删除遗留），
  其同名测试采集期即 ImportError；该行入库笔=d314bb0d980（2026-10-05）。
  ⇒ 处置=按在册"缺源禁装/0 占位禁"判据转 **MANUAL_GATES 墓碑条目**（status: active→deprecated，
  行不删、id 保留、redirect_to 指本账；复活=实现落位后删墓碑行、由第二遍自动出行）。
  本笔属如实记账而非新政策，但状态字段变更仍请 Owner 追认（不追认=一行 revert）。
- 判别力自证：三突变全见红（删第二遍→POOL 缺行红；去"已认领守卫"→重复行＋归属改写红；
  墓碑改名→状态断言红）；另加幂等自证（连跑两次 generate() 逐字节同）与"只增不改"契约测试
  （既有行任一字段被姊妹台改写即红，MAP-ALIGNMENT 跨三模块点名锁定）。
  测试并入既有 `tests/gov/governance/generators/test_generate_gate_registry.py`（净零：未新建测试件）=28 passed。
- 顺带查实并在册的新事实：**GATE-21 的 `--check` 只比 `total_gates` 一个数**（不比行内容），
  且 HEAD 现面即红——`generate_gate_registry.py --check` rc=1"磁盘 191 ≠ 生成 189"
  （已避开"管道 $? 量的是 tail"的假绿坑，重定向后直取 rc）。K8 落地后该计数归位 191=191
  ⇒ 今晚"谁装新门谁死"的锁有一半由本袋解开。

### 8.2 K9 处置态保护（裁定③，"补 COALESCE"字面为恒真式，已按同构先例改为裸参数重传）

- 字面 `status = COALESCE(EXCLUDED.status, lib_assets.status)` 是**空操作**：VALUES 侧已写
  `COALESCE(%s,'active')`，EXCLUDED.status 恒非 NULL。真修法照抄同句在册先例
  （potential_consumers 裸参数重传，裁-07）：`status = COALESCE(%s, lib_assets.status)`，
  参数 15→16 位且按 SET 子句文字序 status 在 consumers 之前，`act`/`register_batch` 两处元组同步扩列
  （在册事故形态=扩列不同步元组必炸）。
- 语义 A/B（同一 pg_temp shadow 表、各自事务回滚、零生产写）：省略 status 的全量入账——
  旧面 `deceased → active`（generation 5→6 证明确实触达）；新面 `deceased` 保留且 generation 照递增
  （指纹刷新语义不变）；`archived` 同样受保护；显式申报 status 的调用面照写不变。
- 判别力自证：SQL revert 回 EXCLUDED 形态 ⇒ 4 支测试红（新 3 支＋在册 1 支
  `test_conflict_branch_references_raw_param_not_excluded`）；restore ⇒ 23 passed；馆内全套 249 passed/4 skipped。
- 46 枚被洗回 active 的受害行一次性处置方案（裁定③要求随袋附呈）：
  谓词=`status='active' AND EXISTS (SELECT 1 FROM lib_events e WHERE e.asset_id=a.asset_id AND e.action='delete')`
  （实测 46 行）；处置=按 §4 族分三批走 `Librarian.act('delete', authority=…)`——同名对偶 4,571 条可挂
  `successor_of`，其余须死亡证明。本班**未动一行账**（撤账=Owner 终裁治理面，K11 在册）。

### 8.3 系统性拆袋律（今晚用 5 只死袋换来的操作结论）

落地链把 `zephyr` 包预绑到主区：GATE-TEST 钩子的 rootdir 是 serializer worktree，import 却解析到
`D:\ZephyrAlpha\src\zephyr`（两次复现：bag -0004 ImportError；`PYTHONPATH=主区 python -m pytest <新测试>`
同形复算）。TEST-SOURCE-CONSISTENCY 又按同一主区源码面判"测试 import 的符号不存在"（bag -0005 死因）。
⇒ **"代码＋钉新行为的测试"同袋必死**（宪法 §2.4 允许的 gate+自家测试同批，在当前 import 绑定下
   与之冲突）。本班统一改走：**代码袋先投、测试袋后投**——代码袋不含任何引用未落地符号的测试文件，
   可同时绕过 GATE-TEST 与 TEST-SOURCE-CONSISTENCY。在册旁路（测试顶部
   `pytest.skip(allow_module_level=True)`）不采：那会产出永不执行的测试件。

## §9 拆袋律的正解＝落地钩子 import 绑定一处可修（裁定②"先治本后立法"，交维护线）

根因实测（非推演）：`scripts/setup_dev_env.py` 安装的 usercustomize
（`%APPDATA%\Roaming\Python\Python312\site-packages\usercustomize.py:26-34`）把
`<repo_root>/src` 插到 sys.path[0]，而 `_repo_root` **默认硬编码 `D:\ZephyrAlpha`**，
仅当环境变量 `ZEPHYR_ALPHA_ROOT` 存在时才改指。⇒ serializer worktree 的 rootdir 是 worktree，
`import zephyr` 却绑到主区 ⇒ 同袋新符号不可见（GATE-TEST ImportError 与
TEST-SOURCE-CONSISTENCY"模块不存在"两门同源于此）。

**修法=一行环境注入，不改 usercustomize、不改宪法 §2.4**：序列化落地链
（git_commit_gateway / commit_queue 起 pytest 处）导出
`ZEPHYR_ALPHA_ROOT=<当次 worktree 根>`。

A/B 实证（用那条能杀死 -0004 的测试，车道内**不带** PYTHONPATH 跑）：

| 环境 | 结果 |
|---|---|
| `ZEPHYR_ALPHA_ROOT=主区` | `ERROR collecting tests/ai/library/test_lookup_on_disk_marker.py / Interrupted: 1 error during collection`（=死袋形态复现） |
| `ZEPHYR_ALPHA_ROOT=车道` | **12 passed** |
| `import zephyr` 落点 | 主区 `D:\ZephyrAlpha\src\zephyr\__init__.py` ↔ 车道 `D:\ZephyrAlpha\.worktrees\<sid>\src\zephyr\__init__.py` |

⇒ 拆袋是**绕开缺陷的临时工作法**，不是该入法的规则；§8.3 的结论以本节改判为准。
旁证：生成器测试自带 `sys.path.insert(0, 项目根)` 且导 `scripts.*`（未被预绑）⇒
"代码+自家测试"同袋可过——`ZEPHYR_ALPHA_ROOT=主区` 下仍 28 passed，说明缺陷面只在 zephyr 包。

## §10 ③④ 散文轴 join 交付（裁定③④，净零=join 既有翻译册，不立第二真源）

- 支点依据（实测）：借阅谓词三列 `asset_id ILIKE OR home ILIKE OR title ILIKE`
  （`ledger_schema.py:172/183`）与缓存侧 `_NEEDLE_COLUMNS=("asset_id","home","title")`
  （`ledger_cache.py:81-82`）**同轴含 title**，而 title 至今只装文件名 basename ⇒
  散文/中文查询结构性 0 命中。把 name_zh 灌进 title＝单点生效、SQL 与缓存两路同治。
- 面积实测：翻译册 PG 账本 8,889 条带 name_zh，可 join 到 active 资产
  **module 4,004＋file 3,994＋doc 88＋registry 4 = 8,190 行**；键=`home ↔ payload->>'module_path'`。
- 落点=`Librarian.register_batch`（采集器全量入账唯一咽喉）；SQL 提为模块级常量
  `_SQL_TRANSLATION_PROSE` + `TRANSLATION_REGISTRY_ID`（NO-BARE-SQL 合规）；散文优先、
  无在册散文时沿用采集器文件名（不造标题、不置空）；账本不可达 fail-soft **且必记
  logger.warning**（GATE-SILENT-DEGRADATION：降级不得伪装成正常，已入测试断言）。
- 自测：馆内全套＋影子门 **266 passed / 4 skipped**；突变自证=摘掉散文优先后
  `test_register_batch_prefers_prose_title` 判红（1 failed / 21 passed），恢复即全绿；
  净零自证=新 SQL 只读 registry_ledger、串内不含 `lib_assets`（不改总账列面）。
- **时序硬约束（勿犯）**：本班**未跑任何全量入账**。K9 未落地＝部署面仍是
  `status = EXCLUDED.status`，此时 ingest 会把 deceased/archived 洗回 active（§8.2 A/B 已证）。
  join 生效须由 K9 落地后的自然 post-commit 入账链带动；④ 的销账（family a/c 4,664＋b 119）
  同理**必须排在 K9 落地之后**，否则 tombstone 被自己人洗掉——这条是本账对裁定④的唯一附加条件。
- 留裁 K12：写侧灌 title 之后，馆页四列（asset_id/kind/status/home）**不展示 title** ⇒
  人类读者看不到散文、只有查询命中可见。是否把 title 加进展页/输出列＝视图口径变更，留裁。

## §11 交接清点（统筹 02:2x 裁定②：停在这里，序交下一班；读回义务随本节省交）

### 11.1 在队五袋（`ls .runtime/commit_queue/pending/` 02:2x 实点，FIFO 即序）

| qid 尾号 | 内容 | 落地后自愈什么 | 风险 |
|---|---|---|---|
| -0008 | `src/zephyr/library/lookup.py`（读侧存在性标注，代码件） | ① 读侧防幻觉上线 | 低（无测试件＝不触 GATE-TEST 陷阱） |
| -0009 | 生成器补丁＋其测试 | K8：POOL 行可导出、GATE-21 计数 191=191 归位 | 该测试导 `scripts.*`（未被预绑），同袋或可过；若死于 TEST-SOURCE-CONSISTENCY 则拆两袋重投 |
| -0010 | `ledger_schema.py`＋`librarian.py`（K9 码） | 处置态不再被采集链洗回 | 低 |
| -0011 | 本账（§1–§8 版） | 班账上 dev | 低 |
| -0012 | `ledger_schema.py`＋`librarian.py`（join 码，严格超集） | ③④ 散文轴可供数 | 低；**生效须等 K9 落地后的入账**（勿手动跑 ingest） |

### 11.2 只在车道、不在任何活袋的工件（-0007 死后失载，务必按此重建）

`src/zephyr/gov_enforcement/commit_gates/library/library_tri_consistency_gate.py`（新门本体）、
`src/zephyr/gov_enforcement/commit_gates/__init__.py`（静态接线边，缺它 ORPHAN-MODULE 必拦）、
`docs/.../in_process_gate_registry.yaml`（107→108 行）、`docs/.../generator_registry.yaml`
（`trigger_sources=[db:lib_assets]`）、`tests/gov/gov_enforcement/test_library_tri_consistency_gate.py`、
`docs/_working/libghost_campaign/01_state_independence_design.md`、`docs/_working/examcard_campaign/99_delivery.md`（更正行）。

重建法（K8 落地后）：在**干净 dev 面**跑 `generate_gate_registry.py`（无 `--check`）重生总册
⇒ 191→192（含新门行、POOL 回归在册、ghost 走 MANUAL_GATES 墓碑），与"新门＋`__init__`＋两册＋总册"
同袋投＝② 代码袋；随后单独投 ② 测试袋。**总册不要在落后车道里重生**（=假重基净删他人门行）。

### 11.3 本班留下的两处"脏面"，下一班请勿随袋带走

1. `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` 与
   `module_translation_registry.yaml`：车道盘面上含本班令牌/翻译行**外加他班物化行**
   （主区盘面已按 S9/S7 用探针先算 +133/−0、+37/−0 纯追加后 render，索引面未触碰）。
   两册一律**不入袋**（S7 在册判据：袋=整档快照＝归属篡改）。
2. `docs/02_enterprise_architecture/04_architecture_principles_decisions/`（README＋project_handbook/01..07，
   共 7 支生成文档）＝本班一次 `apply_depgraph.py --add-design-node` 尝试的**副产物**
   （该命令在参数报错下仍起了后台重生，与在册"apply_depgraph --dry-run 也写 PG 并起后台重生"同族）。
   本班未据以改动任何真源，处置=在干净面重跑生成器覆盖或直接丢弃，**勿并入任何袋**。

### 11.4 会话态与移交义务

- 车道 `st-libstale-20261013` 与全部 claims **保留不放**（五袋在飞，"袋在飞禁放锁"）；
  心跳保活授到 ~03:5x，若续做需再 grant。
- 读回义务（随 1→6 序移交）：每袋落地后 `git show dev:<file>` 逐字读回＋
  `git log -1 --name-only` 核归属；① 的验收判据＝`git show dev:src/zephyr/library/lookup.py | grep -c missing-on-disk` ≥1。
- ④ 销账闸门：**只在 K9 落地后开**（§10 时序硬约束，A/B 已在 pg_temp shadow 表证死）；
  谓词/分族/回退面见 §4 与 §8.2。
- ③ 维护线一行 env（`ZEPHYR_ALPHA_ROOT=<worktree>`）落地后，全队回到"码＋测同批"，§8.3 拆袋工作法作废。

## §12 待投补丁：序列化落地链的 scoped-env 钮（统筹 02:5x 定版「先写待投、排空即投」）

**归属三依据已核**：钮位文件 `scripts/governance/commit_queue_landing.py` **不在任何在飞袋**
（`git status --porcelain` 该文件净；pending/processing 里无它）；动因=本班报的落地面；
习语=该文件自身已有的 try/finally 环境对（不必借 belt）。`session_worktree.py` 归 B，本班不碰。

### 12.1 精确改点（唯一一处，六行；两枚 commit 调用共用同一 env  scope）

现形（`scripts/governance/commit_queue_landing.py`）：`_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"` 在 **:236**；
设置对在 **3444-3445**；复原对在 **3524-3527**（同一 `finally`）；第二枚 `gateway.commit(` 在 **:3501**，
落在同一 try 内 ⇒ **一个 scope 覆盖两条落盘路径**（legacy 与重试/池路径）。

```python
# :236 后追加一行常量
_ALPHA_ROOT_ENV = "ZEPHYR_ALPHA_ROOT"   # 子解释器 usercustomize 的仓根指向（缺省硬编码主区）

# 3445 之后同一位置追加（与 _GATEWAY_ENV 同设同复）
prev_root = os.environ.get(_ALPHA_ROOT_ENV)
os.environ[_ALPHA_ROOT_ENV] = str(self.worktree_path)

# 3524-3527 的 finally 里按同款 prev/None 复原
if prev_root is None:
    os.environ.pop(_ALPHA_ROOT_ENV, None)
else:
    os.environ[_ALPHA_ROOT_ENV] = prev_root
```

### 12.2 这枚钮治什么、不治什么（别当成全治）

| 失败门 | 执行体 | 本钮 | 依据 |
|---|---|---|---|
| GATE-PRECOMMIT-RUN / GATE-TEST | pre-commit **子进程**里再 spawn 的 pytest（新解释器，启动时读 usercustomize） | **治** | -0004 现场 rootdir=serializer worktree 而 `zephyr` 绑主区 |
| TEST-SOURCE-CONSISTENCY | serializer **进程内** in-process gate（`zephyr` 已预绑，中途设 env 不改已导入包） | **不治** | -0005/-0007 判"模块不存在"，而模块当时就在袋内/在 worktree 盘上 |

⇒ 第二半（另批，需先测后写）二选一：①drain worker 起程即带 `ZEPHYR_ALPHA_ROOT=<worktree>`
（但工棚同进程还要读主区名册，`anchor_main_root` 一族判定输入会被牵动，须先量）；
②改 TEST-SOURCE-CONSISTENCY 的源面解析=按 `gateway.project_root` 走路径查存在性，不靠 import 绑定
（与 `create_guard._load_capability_registry` 的 anchor_main_root 反向，属门禁判据面＝留 Owner）。
**在第二半落地前，"码＋钉新行为测试"仍须分袋投**（§8.3 工作法继续有效，§9 只算半治）。

### 12.3 取证脚本（纯只读，零落地链动作；两跑对照即证钮有效）

```bash
cd /d/ZephyrAlpha/.worktrees/<本道车道>
ZEPHYR_ALPHA_ROOT=D:/ZephyrAlpha        python -m pytest tests/ai/library/test_lookup_on_disk_marker.py -q   # 期望：collection ERROR（=死袋形态）
ZEPHYR_ALPHA_ROOT="$PWD"                python -m pytest tests/ai/library/test_lookup_on_disk_marker.py -q   # 期望：12 passed
python -c "import zephyr;print(zephyr.__file__)"                                                            # 落点即钮位生效证据
```

### 12.4 提交时机与配套（等排空，不在排空中动落地链）

- 触发条件：**0018 落地**（并与 B 的 0014/0016/0017 一并排空）后即投；
- 袋内容=`commit_queue_landing.py` 本钮 ＋ **双侧对照测试**（同袋：knob=off 见 collection error、
  knob=on 见 passed；单侧断言＝无判别力）＋ 本节文本；
- 排空期间本班**零动态**：不动落地链、不跑入账、不销账（§10 时序硬约束仍在：K9 未落＝tombstone 会被洗回）。
- 更正一处引用：统筹文里点名的 `_has_m10_exemption` 在全仓 `*.py` **零命中**
  （`grep -rn "_has_m10_exemption\|m10_exemption" src scripts/` 空；在册只有 `# noqa: m10-time-trigger` 标记族）。
  该引用不作为钮有效性的证据采信；钮的有效性以 §9 的 import 落点 A/B 与 12.3 复算为准。
