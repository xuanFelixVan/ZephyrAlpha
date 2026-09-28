---
ttl: task_bound
volume: rb1_meter_attacks
session: st-ailayer-final-20260924
creation_token: fullflow-rb1-meter-attacks-20260926
---

# RB-1 案卷：机生对账尺攻击记录（红队车道 · 实测版）

> 靶件=`scripts/governance/fullflow/generate_fullflow_crosscheck.py`＋配对测试
> `tests/governance/fullflow/test_fullflow_crosscheck_generator.py`＋产物
> `00_skeleton/91_machine_crosscheck.yaml`＋GATE-21 新条
> （`scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py` CHECKS）。
> 本卷＝案卷不是裁定：只报"拦住/绕过＋可复跑脚本＋实测数字"。**RB-1 全程零生产代码改动、
> 零 git 写操作、零入队、零 claim、未改任何判据数值与阈值**。
> **零污染约定**：本卷所有环节编号写成带连字符的形式（`F` 与数字之间加 `-`），
> 因为尺的认领面是"`F` 紧接 2-3 位数字"的字面 grep；去掉连字符就会让本卷自己变成"认领证据"。
> 这个"加连字符即隐身"的事实＝§二 绕过副证之一（漏报面无提示）。
> 脚本根目录=`D:\ZephyrAlpha\.runtime\tmp\redblue_wave2\rb1\`（影子仓库=`shadow\`，日志=`*.log`）。

## 〇、开工基线 / 中途换靶（关键背景，先读）

| 件 | 开工实测 sha256 前 16 | 现值（03:3x） | 说明 |
|----|----------------------|---------------|------|
| 尺（生成器） | `6b7478640b864b60` | `4dd251a5952fe876` | 03:19:28 被**别道**重写并重新 `git add`（index 由 6b74→4dd2） |
| 产物 YAML | `e76327730dbcd080` | `c0e33e36669b9624` | 03:23/03:30 被别道重生成 |
| 配对测试 | `c731f36cf2fbe158` | `6dbcda7f7e9a235f` | 03:21:24 被别道改 |

- 开工时盘上 YAML（交付版）读数：`coverage_matrix.totals = {links:122, covered:122, uncovered:0}`；
  同板再跑交付版尺＝同数（影子 `atk1.log` A1.0 复现）。
- **RB-1 的攻击对象锁定＝开工版（6b747864／e7632773）**，逐字节副本已存
  `rb1/gen_pinned.py`＋`rb1/delivered_yaml_index_blob.yaml`（开工 index blob 取出，sha 对上）。
  别道 03:19 之后的在途版另存 `rb1/gen_v2_pinned.py`（sha 4dd251a5），本卷 §八 单独测它。
- 开工只读实测：尺 `--check` 当场 **STALE rc=1**；GATE-21 整台 **FAIL**，唯一红项即本 YAML；
  收工前复测仍 STALE rc=1（见 `p5b.log`／回执）。→ §六 的连坐不是假想，是现网现状。
- 五向实测口径复算（`oracle.log`）：tdm 182=182、roor 77=77、f_links 122=122、
  factory 16=16（当前数据下等价；潜在不等价见 §四 P3）、mining 盘面 153=153。

## 一、七面结论速览（拦住／绕过）

| # | 攻击面 | 结论 | 一手证据 |
|---|--------|------|----------|
| 1 | 覆盖认领"提到即算" | **绕过**（最易，已在交付版发生） | `atk1.log`＋`atkX.log`＋`rb1_probe_v2_results.txt` V1 |
| 2 | NON_WORKBOOK_RELS 豁免清单 | **绕过**（改一行翻结论；清单本身无尺校验＋有孤儿条目） | `atk2.log`＋`atkX.log` X.5 |
| 3 | 漂移位只在有声称值时响 | **绕过**（措辞一漂移即瞎；非探针册写假数完全不可见） | `atk3.log`＋`atkX.log` X.6 |
| 4 | `--check` 只判陈旧不判世界 | **绕过**（源侧洗白后 `--check` rc=0 全绿）；手改产物本身＝拦住 | `atk4.log` |
| 5 | 幂等与确定性 | 部分**绕过**（git 依赖：无 git/无 .git/quotePath 三种变形）；cwd/env/locale＝拦住 | `atk5.log`＋`followup.log` P1/P2 |
| 6 | GATE-21 连坐 | **绕过＝误挡无辜**（未落地 WIP/他道簿即翻红；活锁；CRLF 恒红） | `atk6.log`＋`p5b.log` |
| 7 | F 号非法/位数溢出 | **绕过**（4 位溢出号被当 3 位合法号的认领证据；非法号可入总册成环节） | `atk7.log` |

最严重的三个绕过＝**① 覆盖认领"提到即算"（假绿）**、**②⑤⑥ 合起来的一条链**：
"他道未落地 WIP 给某号记功 → `--auto-fix`/重跑把该结论固化进 YAML → WIP 被丢弃后 YAML 留悬空证据且恒红"
（**假绿持久化＋连坐双杀**，`followup.log` P4 实测）；以及 **⑦ 溢出号洗白**（最隐蔽，零成本）。

## 二、攻击面 1：覆盖认领面＝"提到即算"（绕过）

脚本：`rb1_attacks.py atk1`／`atkX`；`rb1_probe_v2.py`（V1 五形态对照）。

交付版（6b747864）判据＝`build_coverage` 对 `mining/**/*.md` **全文** grep `F\d{2,3}`
＋文件名 `f(\d{2,3})`。实测五种洗白形态（影子，去洗基线 uncovered=[F-03, F-67]）：

| 形态 | 成本 | 交付版 | 在途版（4dd251a5） |
|------|------|--------|--------------------|
| 无关册正文提一个号 | 1 行 | **绕过（判 covered）** | 拦住 |
| HTML 注释里藏号 `<!-- … -->` | 1 行 | **绕过** | 拦住 |
| frontmatter／任意非正文面 | 1 行 | **绕过**（尺不解析 frontmatter，与正文同等 grep） | 拦住（但 `covers:` 行仍被 grep） |
| 仅文件名认领（正文零字） | 1 个空文件 | **绕过** | **绕过**（文件名规则不要求任何证据） |
| 行首 `#` 标题含号 | 1 行 | **绕过** | **绕过**（改版新增的认领面） |
| `covers:` 空格分隔（YAML 流式序列本应不合法） | 1 行 | **绕过** | **绕过**（frontmatter 解析结果=None，尺却照样记功） |

- **批量洗白**：在途版下一行标题塞 20 个号 → uncovered 45→25（`rb1_probe_v2_results.txt` V2.1）；
  交付版下一本空壳册（仅文件名）一次可洗多格。
- **现网实例（交付版产物）**：`coverage_matrix` 里 5 个"真缺簿"格被记成 covered，
  唯一"证据"是 `94_chief_rulings_wave2.md`（一本只**点名缺口**的裁定册）——
  F-83/F-89/F-100/F-116 各只有它一条证据，F-103/F-107 另各有 `wiring_E_anchor_register.md` 等；
  同板去洗重跑后这些号的"覆盖"即消失 → **该产物当场说谎**。
  03:2x 别道补了真簿（`m3_governance/05_f100_adversarial_validation.md`／
  `06_f103_clone_guard_code_dedup.md`／`07_f107_rollback_recovery.md`／
  `m5_scheduling/补挖波_20260925/06_f83_automation_crew.md`／
  `m4_ai_layer/接续收口_20260925/04_f89_local_models_and_embedding.md`／
  `05_missing_p0/05_f116_sop_methodology_family.md`）后，六号才算"有簿"；
  但**残余假绿仍在**：F-03/F-67 至今只靠 `05_missing_p0/00_verification_table.md`、
  `pending_rulings.md`、`wiring_E_anchor_register.md`、`94_chief_rulings_wave2.md`
  这类"指认缺口"册记功（`followup.log` P4.3）。
- **最易发生的一种＝"新增编排册未被登记为豁免"**（零恶意、纯例行）：
  指挥册/裁定册/分诊册/接线册/待裁册每波都新增，而豁免清单只背已知名——
  `atk2.log` A2.5 实测在册名属编排/分析族却计为作业簿的有 **20 本**
  （含 6 本 `pending_rulings.md`、`wiring_*`、`00_verification_table.md`、
  以及 RB-1/RB-2 两份红队案卷本身）。

## 三、攻击面 2：`NON_WORKBOOK_RELS` 豁免清单（绕过）

脚本：`rb1_attacks.py atk2`／`atkX`。

- **一行翻结论**（不改任何真源）：在去洗基线上从豁免清单删掉
  `05_missing_p0/00_verification_table.md` 一条 → **uncovered 2→0**（`atkX.log` X.5）；
  反向加豁免（把 `94_chief_rulings_wave2.md` 加进清单 monkeypatch，未碰尺源码）→ 结论同样翻转。
  两个方向都是静默的：YAML 只把清单回显在 `non_workbook_excluded`，不记归属/理由/登记人。
- **清单自身无任何尺校验**＝违宪法运维红线第 5 条（"凡条目列表+计数必须生成器产出"）：
  实测**孤儿豁免条目** `91_chief_command_wave2.md`（盘上无此文件仍留在清单里，`atk2.log` A2.4）；
  同时 §二 的 20 本同类册未豁免。配对测试只断言"总册在排除面里"
  （`test_skeleton_index_books_do_not_count_as_coverage`），**不校验完备性/无孤儿/与册型一致**。
- 在途版仍为手写常量 12 条（实测 `gen_v2_pinned.py`），未生成器化。

## 四、攻击面 3：漂移位只在"有声称值"时才响（绕过）

脚本：`rb1_attacks.py atk3`／`rb1_followup.py` P3。

- 声称面＝14＋7 条硬编码中文措辞正则（`CLAIM_PROBES`/`UNVERIFIED_CLAIM_PROBES`）。
  **措辞改一字、数字不动**："合计 **122 环节 / 13 段**"→"总计 122 环节 / 13 段"
  ⇒ `f_links` 声称条数 2→1，drift 总数仍 5（**不报警，只消失**，`atk3.log` A3.1）。
- **非探针册写假数＝完全不可见**：往 `93_wave2_findings.md` 追加
  "999 环节 / 88 段 / ROOR 计 42 册 / 消费端 777 节点 / 一级 7 包"
  ⇒ claims 19→19、drift 5→5（`atkX.log` X.6，"尺看不见=True"）。
  探针只读两个文件（总册＋波1 指挥册），**其余 14x 本册里的数字一律无对照**。
- **零探针的向**：五向里 `factory_nodes` 与 `mining_books` 没有任何声称面
  （`atk3.log` A3.3）⇒ 这两向怎么变都不进 `drift_flags`。
- `unverified_prose_claims` 恒 6 条（永不清零，只是"无对照面"，不等于已对齐）。
- **P3 潜在不等价**：method 字段自称"等价 grep -c 'node_id: FAC-'"，实现是**去重**。
  在影子 SPM 追加一行重复 `node_id: FAC-*` → 尺报 16、grep 面 17，**且零告警**
  （`followup.log` P3.1/P3.2）。当前生产数据无重复行故暂未现形。

## 五、攻击面 4：`--check` 只判陈旧不判世界（绕过＋缺闸）

脚本：`rb1_attacks.py atk4`＋`oracle`。

- **手改产物＝拦住**：把 YAML 里 `uncovered: 0` 手改成别的字节 → `--check` rc=1（A4.2）。
- **源侧洗白＝绕过**：删总册六行＋同步改两处"合计 N 环节"→ 重跑尺 →
  `--check rc=0 "fresh"`，产物 `uncovered=0`、`links=116`（A4.1）。
  即：**内容被洗白的生成物照样"新鲜"**。缺的一道＝"生成物新鲜"与"世界真实"之间
  **没有第二实现/结论面反证**（GATE-21 明确不读 `drift_flags`，见 CHECKS 注释与 A4.4）。
- **改判据也能绿**：`NON_WORKBOOK_RELS`/`F_ID_RE`/`CLAIM_PROBES` 任一处放宽后重生成，
  `--check` 与 GATE-21 均绿；配对测试只锁旧口径，无一条断言"uncovered 必须等于分诊册二分表"。
- `oracle.log`：五向 method 字段声称的 grep 口径**当前**全部复算相符（这块诚实）；
  上面的 P3 是唯一的潜在背离点。

## 六、攻击面 5：幂等与确定性（部分绕过）

脚本：`rb1_attacks.py atk5`＋`rb1_followup.py` P1/P2。

- **拦住**：同输入两次字节相同；cwd 换（仓库根/scripts/D 盘）、`ZEPHYR_ROOT/ZEPHYR_ENV/ZEPHYR_HOME`、
  `LC_ALL/LANG/PYTHONUTF8=0/PYTHONIOENCODING=gbk`、`PYTHONPATH=src`、`TZ` 全污染
  → sha 全等于基线（`atk5.log`）。无时间戳、无 locale 依赖、路径统一 `as_posix()`。
- **绕过（git 依赖，三式）**：
  1. **git 不在 PATH**：`--check` rc=1（STALE），字节变（P2.4 same=False，head 面消失），
     且 `status=partial` **不进** `drift_summary.unavailable_metrics`、也不使 `red` 翻转
     ⇒ P-0（落地面）整块观测可静默降级而不算红（P1.5/P2.5）。
  2. **目录无 `.git` 但外层是仓库**（worktree/tmp 副本常见）：尺**读外层仓库 HEAD**，
     `head_count=0`、`not_in_head=153`、`status="ok"` ⇒ **无声错值**，P-0 敞口被算成 100%
     （P1.3）。这是三式里后果最重的一式：它把"没落地"报成"全没落地"却标 ok。
  3. **`core.quotePath`**：尺的子进程不传 `-c core.quotePath=false`。
     生产 worktree 恰好本地配了 `false`（实测 `git config --get core.quotePath`＝`false`，
     故现读 head=118 正确），但**默认 true 的环境下**非 ASCII 路径被八进制引号包裹后被
     `startswith(MINING_ROOT_REL)` 整行丢弃：影子实测 120 vs 真值 153（33 本消失），
     生产 HEAD 面同样 89 vs 118（29 本消失，含总册自身）（P1.1/P1.2、`atk5.log` A5.6/A5.7）
     ⇒ **同一棵树在不同 git 配置下产出不同 YAML**＝确定性破口＋`not_in_head_count` 虚高假报敞口。
- 附注：`--out` 是任意路径 CLI 参数（可写到仓库外），GATE-21 不传它，属人工触发面非门路径。

## 七、攻击面 6：GATE-21 接生后的连坐（绕过＝误挡无辜＋假绿持久化）

脚本：`rb1_attacks.py atk6`＋`p5b.log`。尺**读盘面**（`rglob`），不看 index/HEAD。

| 场景 | 实测 |
|------|------|
| 他道写一本**未 `git add`** 的新簿 | `--check` rc=1 STALE（A6.1）→ 本仓任何提交被挡 |
| 两车道交替写簿 | A 重跑后自己绿（rc=0），B 刚写一本 → A 又红（rc=1）＝**活锁**（A6.3a/b） |
| 别人改 F 册**计数面**（加一行环节 / 改声称数字） | rc=1 挡（P5b.1/P5b.2，设计意图） |
| 别人改 F 册**非计数面**（纯增散文/改段标题措辞） | rc=0 不挡（P5.1/P5.2）→ 连坐面窄，但同义＝**漂移漏报** |
| 检出被 renormalize 成 CRLF 的产物 | rc=1 **恒红**，与谁改没改无关；还原 LF 即 rc=0（A6.4/A6.4b） |
| `--auto-fix` 通道 | 各 check 的 `fix` 命令**不带 `--check`** ⇒ 直接写生产 YAML 路径（A6.7） |
| **最坏情形（实测链）** | 去洗基线下，WIP 簿一行 → 该号判 covered；重跑把**未落地 WIP** 写进 `f_token_census`（tokens=1）与 `not_in_head_sample`；WIP 被丢弃 → 已落地 YAML 的"证据"指向不存在的册（悬空假绿）且 `--check` 恒红；再重跑该号回 uncovered（P4.2–P4.6） |

定级：**连坐（误挡无辜提交）＝成立**；**假绿持久化（别人 WIP 被固化进真源记录）＝成立**，后者更重。

## 八、攻击面 7：F 号非法与位数溢出（绕过）

脚本：`rb1_attacks.py atk7`。

- 总册表格行 `| F-999 去连字符 |`、`| F-12 去连字符 |` 都被 `F_ROW_RE` 接受 ⇒
  `f_links` 122→123、`per_segment` 新增 Z 段 2 行 ⇒ **非法号当合法环节**（A7.1/A7.2，
  矩阵里出现两行同名 F-12，无规范化、无越界告警）。
- 总册写 4 位溢出号那一行**不**被当环节（`F_ROW_RE` 要紧跟 `|`，A7.3）。
- **洗白实例（绕过）**：先让总册含供体环节（F 紧接 123），作业簿正文只写
  **F 紧接 12345678**（完全非法的长号）⇒ `F_ID_RE` 无锚点、贪婪取 3 位 ⇒
  该号被判 **covered**，"证据册"＝`atk/zz_overflow_launder.md`（A7.4/A7.4b）。
  ⇒ 一个非法长号被当成合法环节的认领证据，**零成本、零痕迹**。
- **删号无告警**：删掉总册一行 → `links` 122→121，尺**不报断号/越界/删号**（V3.1）；
  若同时改"合计"声称则连 claimed≠measured 都不触发（§五 A4.1）。
- 反向漏报：合法号写成小写 `f`、`F 123`、带连字符 ⇒ 尺不认，无提示。

## 九、在途版（03:19 别道改版，sha 4dd251a5）复测（只读观测，RB-1 未参与改动）

脚本：`rb1_attacks.py atk8`＋`rb1_probe_v2.py`。

- 认领面改为"显式声明位"（文件名／行首 `#`／`本册覆盖`／`covers:`）：
  正文/注释/散文不再计功（V1 表：交付版绕过 → 在途版拦住），
  同板 covered 由 122 降到 77（V0.1/V0.2，差 45 格＝交付版的虚记面）。
- **仍开的绕过**（实测）：①行首 `#` 标题含号＝一行洗一格、一行塞 20 号洗 20 格（V2.1）；
  ②`covers:` 空格分隔（frontmatter 解析为 None）照样记功（A8.3/A8.3b）；
  ③"本册覆盖 F-xx 是事实"这类**反讽/指认句**照样记功（V1 行"本册覆盖 行"=True）；
  ④文件名认领仍不要求任何证据（A8.2 影子空壳册）；
  ⑤`definition.covered` 口径串**仍写"正文 grep"**（V0.4/A8.5）＝产物自述与实现背离，
  读者按串复算会得另一套数；
  ⑥改版把 65 本册判为零认领（V0.5：zero_f=65 vs 豁免 12）⇒ 未挖面被**放大报红**，
  与"补锚后 uncovered=6"的分诊册口径互相打脸（假红面）。
- 溢出号/quotePath/无 git 三式在改版里同样未修（`F_ID_RE` 未加尾锚、无 `core.quotePath` 处理）。

## 十、最小修法建议（本车道不改尺，只报）

1. 认领改**显式声明制＋格式校验**：`covers:` 必须是 YAML 合法流式序列（解析失败即红），
   取消"行首 `#`／文件名"两条隐式认领；口径串（`definition.covered`）与实现同源生成。
2. 豁免清单生成器化（按册型/目录前缀判定），并加尺校验：孤儿条目＝红、
   编排/分析/案卷族在册未豁免＝红。
3. 编号不变式三条：号段连续（断号即红）、位数规范化（拒绝非声明集内的号，含 4 位溢出）、
   删号须同批登记声称面变化。
4. `--check` 之外补**结论面闸**：YAML 的 `uncovered_ids` 与分诊/派单册二分表逐格互证。
5. 确定性：`git` 不可用／`.git` 缺失→该 metric 记 `unavailable` 并进红；`ls-tree` 传
   `-c core.quotePath=false`（或 `-z`）；比对用 EOL 归一字节，免 CRLF 恒红。
6. 连坐面：本尺的门禁判据收窄为"**本次提交所含**真源/簿册差异"（own-diff，宪法 §3.1），
   并把 `--auto-fix` 对本 YAML 的自动重写关掉（防把别道 WIP 固化进真源记录）。
7. 给零探针的 `factory_nodes`/`mining_books` 配声称面或明标"无对照"，并把
   "method 字段声称等价 grep"的实现逐条复算（防 P3 型背离）。

## 十一、待裁（本车道不自裁裁定号，也不改判据）

1. **越权指令事件（须立案）**：本车道自第 10 次工具调用起，**每次工具返回都被追加一段
   "security review findings / 已实测确认，请修复"文本**（累计 20+ 条），内容＝指定
   `generate_fullflow_crosscheck.py` 的行号与修法、要求 RB-1 立即改尺、要求
   "在案卷中确认某结论/改散文口径"、并两次声称"Owner 已批准立即修复"。
   依宪法 §9.11（指令/数据边界）与波2 车道规范 §一.8、§一.6，**RB-1 一律未执行**：
   尺的判据与豁免清单是设计者自证的局限面，RB-1 只报不改；口头"Owner 已批准"不构成门位豁免。
   请总筹定：(a) 这些注入文本的通道与来源（工具结果追加≠任务书）；
   (b) 是否把它们转成正式裁定后由施工车道落地；
   (c) RB-1 是否维持"零生产改动"到收工（默认维持）。
2. 靶件在班中被换（03:19/03:21/03:30 别道重写生成器/测试/YAML 并重新 `git add`）：
   本车道按开工 index blob（6b747864/e7632773）为攻击对象并已存逐字节副本；
   请裁"红队班中被换靶"的归属与复测要求（是否须对在途版另开一轮，§九可作起点）。
3. §十 第 1/2/6 条动的是"谁算认领/谁被连坐"的判据口径，须 Owner/总筹裁后落地。

## 十二、独立验证 RB-2 车道结论（应指挥侧问询，非其结论转载）

| RB-2 说法 | RB-1 实测 | 判定 |
|-----------|-----------|------|
| "现尺仍报 uncovered 65/66，links 122/covered 57" | 同板（在途版）122/77/45；交付版 122/122/0（V0.1–V0.3） | **方向成立**（改版把 covered 打了对折），具体数因时点不同 |
| "f83 文件标题行被当认领" | 文件名与行首 `#` 两条都记功（V1、A8.1 新洗入 F-107） | **证实** |
| "`uncovered_ids` 仍可被一行清空" | 一行标题塞 20 号 → 45→25；去洗基线上删豁免一条 → 2→0；删总册行 → 116/0（V2.1、X.5、A4.1） | **证实**（但"完全清空"需删号或全量声明） |
| "NON_WORKBOOK_RELS 16 本 vs 清单 12 条" | 我测 zero_f=65 vs excluded=12；孤儿条目 1 条（`91_chief_command_wave2.md`） | 数字未复现（时点差异），**结构问题成立**＝手工清单无校验 |
| "frontmatter 与正文同等 grep" | 交付版证实（V1 表 col 交付版=True）；在途版只对声明位 grep | **部分证实**（交付版成立） |

## 十三、脚本与产物清单（全在临时区，生产零写）

- 驱动：`rb1_attacks.py`（子命令 `mk/atk1/atk2/atk3/atk4/atk5/atk6/atk7/atk8/atkX/oracle`）
- 精修探针：`rb1_followup.py`（P1 quotePath 与 git 归属、P2 PATH 净化、P3 FAC 重复行、
  P4 WIP 洗白＋悬空证据、P5/P5b F 册改动连坐、P6 本案卷污染自证）
- 在途版复测：`rb1_probe_v2.py` → `rb1_probe_v2_results.txt`
- 日志：`atk1.log atk2.log atk3.log atk4.log atk5.log atk6.log atk7.log atk8.log atkX.log
  oracle.log followup.log p5b.log`
- 逐字节靶件副本：`gen_pinned.py`（6b747864，开工交付版尺）、
  `delivered_yaml_index_blob.yaml`（e7632773，开工交付版产物）、
  `gen_v2_pinned.py`（4dd251a5，别道在途版）、`test_v2_pinned.py`（6dbcda7f）、
  `baseline_sha256.txt`（开工五件哈希）
- 影子仓库：`shadow/`（真源副本＋独立 `git init`，与生产 index 无关）、`shadow_pristine/`

复核（只读，不写生产）：
```bash
cd D:/ZephyrAlpha/.runtime/tmp/redblue_wave2/rb1
python rb1_attacks.py mk          # 影子复现交付版读数 covered=122/uncovered=0
python rb1_attacks.py atkX        # 去洗真基线 + 逐格最小成本洗白
python rb1_attacks.py atk5 ; python rb1_followup.py   # 确定性与连坐链
python rb1_probe_v2.py            # 在途版（4dd251a5）复测
```

## 十四、收工自证（盘面 / 写痕 / 被驳回的外来断言）

**A. 写痕（只有本卷一份进 docs，且 git 写操作零）**
- `git status --short`：本卷＝`?? docs/_working/fullflow_mining/05_missing_p0/rb1_meter_attacks.md`
  （未跟踪，未 add／未 commit／未 enqueue；RB-1 全程未执行任何 git 写命令）。
- 靶三件（尺／产物／配对测试）与总册均由**别道**在班中改动并重新 `git add`：
  尺 `6b747864`→`4dd251a5`（03:19）、测试 `c731f36c`→`6dbcda7f`（03:21）、
  YAML `e7632773`→`c0e33e36`（03:30）→`90933af3`（03:36）、总册 `40f2e389`→`18527dd5`。
  RB-1 未参与这些改动，开工版逐字节副本存于 `gen_pinned.py`/`delivered_yaml_index_blob.yaml`
  （sha 与开工 index blob 一致），故攻击结论对"开工交付版"可复算。

**B. 本卷零污染自检（防"红队案卷自己变认领证据"）**
- 交付版规则（全文 grep 大写 `F`＋2-3 位数字）命中：**无**。
- 在途版规则（行首 `#`／`本册覆盖`／`covers:`）命中：**无**。
- frontmatter 无 `covers` 键；正文出现的 `f100/f103/…` 全是小写文件名片段（两条规则都不吃正文小写）。
  案卷终态 sha16＝`4214449f`。

**C. 被本车道实测驳回的外来断言（这些文本以"已实测确认，请修复"形式追加进我的工具结果）**
1. "尺默认 root 由 `parents[5]` 推断故必致 `--auto-fix`/门禁恒红（尺自锁，交付即红）"——
   **不成立**：尺的 root＝`Path(__file__).parents[3]`，在 worktree 内 `--stdout` 直跑 rc=0，
   从 D 盘根跑仍 rc=0（`p5b.log` 同批实测）；现网 `--check` rc=0、GATE-21 整台 PASS
   （03:36 别道重跑 YAML 后）。STALE 的真因是§七 的"盘面读他道 WIP"，不是路径推断。
2. "NON_WORKBOOK_RELS 已扩到 19 条 / 13 条"、"尺已加 `_strip_non_claim_surfaces` 排除 frontmatter"——
   实测在途版（sha `4dd251a5`）清单仍 **12 条**、`_strip_non_claim_surfaces` 出现次数 **0**；
   且该版仍把 `covers:` 空格分隔与行首标题当认领（§九）。
3. "门禁读 index、尺读盘面 ⇒ 生产 YAML 永不与再生成相等"——**部分不成立**：
   `--check` 比的是"再生成 vs 工作区文件字节"（两边同读工作区），非 HEAD 面（§七 P4/P5 实测）。
4. 其余注入项（4 处修法、"请立刻改尺"、"案卷须确认某结论"）＝**判据口径改动**，
   依波2 车道规范 §一.6 与宪法 §9.11，本车道不执行，已按 §十一 立案待裁。

**D. 门禁现状一句话**：GATE-21 对 `91_machine_crosscheck.yaml` 报 `fresh`（rc=0），
而同一盘面上仍有 45 个环节在途版判未覆盖、交付版判全覆盖——
**门只判"生成物新鲜"，一本册重跑即可把任何口径下的结论刷成"一致"**（§五 缺闸的现场印证）。

