---
ttl: task_bound
completes_when: 全部波次施工终态达成且本册每包状态与 HEAD 实测一致（继任者可凭本册一条命令接手）
---

# 总包调度台账（95 册 · 机读友好 · 本役唯一派单真源）

> **本册是什么**：Owner 2026-09-26 20:1x 把"总筹/总包"职权交下后，本班（session `st-final-build-20260926`）
> 对全役的派单、验收、代裁与残余的**滚动台账**。它与 94 册（上一班归并台账）正交：94 册记"上一班留了什么"，
> 本册记"这一班正在做什么、做到哪、凭什么说做到了"。
> **判读铁律继承**：落地只认 `git show HEAD:<path>` 的字节；队列 done／回执／commit message 自述／子代理回报
> **都不算证据**。子代理回报一律按"案卷"采信，不按"裁定"采信（本仓在册纪律）。

## 一、本班会话坐标（继任者接手三行）

| 项 | 值 |
|---|---|
| 车道 | `D:\ZephyrAlpha\.aidrafts\st-final-build-20260926`（分支 `session/st-final-build-20260926`，247MB 全量 checkout） |
| 会话注册 | pid=0 + heartbeat_daemon（90s 判死），claim 走 `lock_files.py acquire-batch` |
| 接手命令 | `python scripts/commit_queue.py status --session st-final-build-20260926` ＋ 读本册 §三 表 |

## 二、★落地通道实测配方（本班逐 gate 试出来的，写成配方是给后面所有人省两小时）

**症状**：从车道提交时，`CLAIM-REQUIRED` 与 `WORKTREE-REQUIRED` 两门互相拉扯——
`lock_files.py` 把 claim 路径**一律归一到主区根**（即使传车道绝对路径也会剥掉车道前缀存成 `D:\ZephyrAlpha\...`），
而 `CLAIM-REQUIRED` 门用 `Path(f).resolve()` 按 **cwd** 解析文件清单；
`WORKTREE-REQUIRED` 门用 `gateway._get_worktree_manager().get_current_worktree()`，同样按 **cwd** 判定。

**正解（实测一笔袋 11 件零死）**：

```bash
cd /d/ZephyrAlpha                                  # ① cwd 必须是主区（让清单解析到主区绝对路径＝claim 记的法子）
export ZEPHYR_WORKTREE_ROOT=<不设在主区>            # ② 别设：设了会把内容门的扫描根搬到主区，读到别人在途版本
python scripts/git_commit.py \
  --session st-final-build-20260926 \
  --project-root "D:/ZephyrAlpha/.aidrafts/st-final-build-20260926" \   # ③ 字节从车道快照，不经主区共享 index
  --files "<车道绝对路径，逗号分隔>" \                                    # ④ 必须绝对车道路径：CLI 会把相对路径先转成
                                                                        #    主区绝对路径，_enqueue_mode 的 relative_to(车道)
                                                                        #    随即失败 → "文件不存在且未被 git 跟踪"
  --message-file <绝对路径> --enqueue --allow-multi-domain --allow-non-worktree
```

- ⑤ `--enqueue` 需要 flag `commit_queue_interactive`，**实测本窗=ON**（用 `flag_enabled('commit_queue_interactive')` 现读，勿背）。
- ⑥ `--allow-non-worktree` 的合法性来源＝旗标自述"2026-08-13 裁定 AI 可默认使用"＋**本批物理隔离在车道、字节不取自主区 index**，
  故该门警告的"搭便车带入他人 WIP"事实面不存在；用法是把理由写进 commit message 第四节公开披露（本班已如此做）。
- ⑦ `CLAIM-REQUIRED` 在 enqueue 模式被 `extra_skip` 跳过（落地侧按队列项 session 重新 claim），但 **claim 仍要先做**，
  否则落地侧白烧；`acquire-batch --files-from <相对清单>` 即可。
- ⑧ 内容门读 **index 暂存字节**，故入袋前必须 `git add -- <具名路径>`（禁 `git add .`）并自证
  `sha256(盘面)==sha256(git show :<path>)`（EOL 先归一再比）。
- ⑨ 一袋多域（scripts+tests+docs 同袋）在 `--enqueue` 模式下不存在"入袋前预跑 4 分钟"以外的代价，
  但**袋 ≤38 件**是硬约束；`git_commit.py` 无 `--base-head` 旗（要基底校验改走 `commit_queue.py enqueue --base-head`）。

## 三、包状态表（每包一行；态＝⬜未开 / 🔨已做未落 / ✅已落 HEAD 实测 / 🌑门位 / ⚑待 Owner）

### 开工批（波 9.5 前置）
| 包 | 内容 | 态 | 证据 |
|---|---|---|---|
| 0-A | 终审交付 8 件入仓 + 28 条 token + 骨架族14 + 波次表补 9.5/10/11/12/W-180 | ✅ | 袋 `q-20260926-…-0001` → HEAD `3eeb935743`，11/11 文件命中，归属逐件核对仅本班 11 件 |
| 0-B | ⚑ 菜单补位 9+5 项（93 册「补位」节 + pending_owner_items.md） | 🔨 | 子代理已写盘；实测更正 5 处已回写族14 W-163 行（C5/C7 早在 ⚑-2、vhdx 已裁 #378/#380/#381/#398/#399、EV 出处非池⑧、emoreplay 属"声称已批册上查无"、245/678 未独立计数） |

### 波 1A 可信层
| 包 | 内容 | 态 | 实测要点 |
|---|---|---|---|
| 1A.1 | 建卡 20 张（1A×6＋1B×10＋波2×4），Owner 门位 4 张 `approval_required=True` | 🔨 | 21 字段校验 20/20 过；幂等复跑零新增 |
| 1A.2 | `VERIFIED` 判据（三条件）＋抽 20 张 COMPLETED 复算 | 🔨 | **20 张全部升不了 VERIFIED**（13 张无锚、7 张锚不在 HEAD）＝本役"自称完成"面被量化；canary 4 passed |
| 1A.3 | 触发面三列对账表生成器 | 🔨 | 红名单 3 台（NO-BARE-GETENV/NO-SECRET-HARDCODE/BARE-SUBPROCESS 的 `password`/`api_key` 子模式 HEAD 零命中）；**装载缺口 0**（103=99+4 复算成立） |
| 1A.4 | 规则↔执法面覆盖率尺 | 🔨 | **真执法面 37/86=43%**（与 10 册"80/86=93%"不符，已被实测下修）；被提及面 86/86；代码零匹配 49 条；trae_057 实测**有**代码引用（与 10 册"零匹配"矛盾，已上报） |
| 1A.5 | 死库死指针清理 | ⬜ | 子代理在跑（store_liveness_probe.py 已出普查，热册补丁待总包执行） |
| 1A.6 | 交接书退役（一条命令出跨会话视图） | 🔨 | `cross_session_view.py` |

### 波 1B 提交链解毒
| 包 | 内容 | 态 | 实测要点 |
|---|---|---|---|
| 1.1 | 四台 `enabled:false` 门归因（不翻旗标） | 🔨 | 归因"禁用原因"仅到 assumed；"禁用期间有无违规落地"**未取证**；恢复属 Owner |
| 1.3 | priority 撞号断言尺（禁改数值） | ⬜ | 子代理在跑（union_priority_ruler.py 已见雏形） |
| 1.5/1.6/1.7/1.7b/1.7c | CREATE-GUARD 触发面／flag 三态读／预检旁路封堵／失败摘除+后继重建／死信属主制 | ⬜ | 子代理在跑，已见 4 把 canary 测试落盘 |
| 1.8 | 从未入库件四态反查 | 🔨 | 79 簇/700 封；`test_redblue_governance.py`（blobs 4 袋 3 版）与 `test_redblue_robust.py`（波0 快照）**判"缺失"0 件**；`dead_triage*.yaml`/`deep_dive_r1.md` 三件实测**已在 HEAD**（骨架册 W-124 的"从未进任何分支"说法对这三件不成立）；捞回 4 份副本+sha 清单 |
| 复发 Top3 | 属主×签名（熔断判据≥3） | 🔨 | st-stress-20260923×NOTHING_TO_COMMIT 29／st-cmd-20260924×TTL-METADATA 21／st-sweep-tail-20260923×GATE-PRECOMMIT-RUN 16；R-3 有方 15 簇 356 封，**无处方 64 簇 344 封**（含 LandingEnvironmentError 38、TTL-METADATA 33 等新签名簇——R-3 表需扩） |

### 波 2 存量成品抢救（时限风险最高）
| 包 | 实测（A4 清点，守卫已加） | 态 |
|---|---|---|
| 现场 | 真 worktree **12 条**（+campaign_hold 普通目录+主区点名 1 处＝14 现场） | ✅清点 |
| 三态 | 免投 30／热投要投 372／新建 206／删除态 0 | ✅清点 |
| 装袋 | **88 袋**，最大袋 38 件 | ⬜ 待投 |
| 冲突 | **11 组同名文件多版**（capability 册 5 版、commit_queue.py 6 版等）→ 真源未裁，已点名 | ⚑ 待裁 |
| 现读纠错 | st-mapbuild 脏项现读 319（C 册记 272，?? 34→81）；ailayer 2 件触 R5 数字尾须改名；t1_t2_handover index≠盘上字节；reland_final 16 新件疑为"路径迁移残壳"（投前待核） | 🔨 |

### 波 3–6 / 9–12
| 包 | 态 |
|---|---|
| 3.1/3.6/3.7（str>date 归一／三源收敛／miniQMT 口径+哨兵） | ⬜ 子代理在跑 |
| 3.2/3.3/W-102（假绿交叉尺／供数守恒／三把尺常设化） | ⬜ 子代理在跑 |
| 4.1/4.2/4.3/4.4（P-28 身份复验／P-27 只读位+一票否决／hardlinked 恒0／P-26 定性） | ⬜ 子代理在跑 |
| 3.0 W-180.3 空壳表 strict 复测、3.8 35 常红尺、5/6/9/10/11 | ⬜ 排队 |
| 12 统一跑批 | 🌑 **唯一合法停点**：五触发条件未全绿，禁自行点火 |

## 四、本班代裁清单（按 Owner 授权"遇到问题自己裁定"，逐条给依据）

| # | 事项 | 裁定 | 依据（第一性原理＋可核对证据） |
|---|---|---|---|
| Z-F1 | 桌面终审 8 件是否入仓 | 入仓，改名避非 ASCII，正文逐字节不改，每件留原件 sha256 | 真源单点灭失风险（桌面非受控、无备份实证）；改名+溯源行同时满足编码门与可核对性 |
| Z-F2 | 波 10 设计是否复制进 10 册 | 不复制，只登记排产位与出口判据 | 宪法 §4 内收律：同一内容两处写＝第二真源必漂（本役已因两图矛盾删过一次旧依赖图） |
| Z-F3 | `--allow-non-worktree` 可否用 | 可用，且必须在 message 里公开披露理由 | 旗标自述"2026-08-13 裁定 AI 可默认使用"＝既有裁定；本批物理隔离在车道、字节不取自主区 index，门警告的事实面不存在；不改门、不加豁免码 |
| Z-F4 | 车道内 `rescued/**` 是否随袋 2 入库 | 暂不入库（案卷与 sha 清单入，副本不入） | 副本缺 `[TTL]/[MODULE]` 头注，补头注＝改被抢救件原始字节，与"抢救留真"冲突；改在波 2 按真路径处理 |
| Z-F5 | 波 2 88 袋如何排 | 按"抢救价值÷袋成本"排序，先投六图役 30 件与 AI 层波2 高危面，其余袋序列入册供继任者机械执行 | 队列 p50≈4.4min（在册读数），88 袋≈6.5h 超出一夜窗口；而车道被外部重置的风险是即时的（本仓已发生多次） |
| Z-F6 | 覆盖尺读数 43% 与 10 册 93% 冲突 | 采 43%，并把它当**新缺口面积**披露，不改 10 册叙述 | 判矛盾先验量纲：10 册算"被提及"，A1 算"进程内可调其判据函数并改变结果"，两个不同对象；两数并存标注口径，禁混引 |

## 五、待 Owner（不自行推进，四类门位）

见 `pending_owner_items.md`（本班新建）与 `93_owner_menu.md`「⚑ 补位」节。本册只登记指针不复制内容（内收）。
最高时限项＝假日批（10-05 F 盘摘除窗口临近）；最高风险项＝波 12 统一点火批准卡（须五条件全绿后呈）。

## 六、双色总包并存事实与防撞（21:0x–23:0x 实测，后任必读）

**事实**：Owner 于 20:3x 另立 `st-zmaster2-20260926` 为**继任总筹**，其车道归属与热册唯一写手制真源＝
`docs/_working/three_piece_infra/00_plan_and_ownership.md`（已入 dev `32389d3123`）。该表把
**波 1A／波 1B（1.1–1.10）／W-180 划给本道**，本道据此不碰 `create_guard.py`、`governance/audit/`、
`library/`、`wiring_registry`、连接矩阵、`three_piece_infra/**`（那是它的乙丙丁戊己庚六道）。

**撞车实证（一次，且是唯一一次袋死）**：`q-20260926-st-final-build-20260926-0002` 死在 **LANDING 侧
TRANSLATION-COVERAGE**——6 条 `plain_zh` 在入袋字节里在册，落地后 `git show HEAD:` grep **0 命中**。
根因＝本道热册基线停在 `3eeb935743`，而同一窗口对方落了 `32389d3123` 并改过 capability 册
⇒ **陈旧热册快照压在新鲜 dev 之上＝别人条目被抹**（本仓在册病"热册蒸发"，这次差点由我制造）。

**防撞三行配方（此后每袋必做，已脚本化 `.runtime/tmp/<sid>/reregister.py`）**：
1. `git checkout <dev tip> -- <两本热册>`（取**更新的 dev 字节**为基，不是 `git checkout HEAD --`——后者是回退）；
2. 用官方 `batch_creation_tokens.py` / `add_module_translation.py` 在本批前缀**重放自家条目**；
3. 断言「条目数只增不减 + 顶格根键无重复 + `yaml.safe_load` 能过」，然后**立即入队**把竞态窗压到一袋内。
   禁止手写块合并：本班一次自造"块集合差插入"因缩进错位直接打坏 YAML（`- file:` 插到顶格）。

**给 Owner 的一句话**：两班各持一份热册写权 = 必然互相蒸发，除非要么"唯一写手＋队列串行"，要么每袋都做上面三步。
本道选了后者（自给自足，不依赖对方让路）。**这是结构性问题，值得一条常设尺**：入队前比较"袋内热册条目集合 ⊇
dev 热册条目集合"，不成立即拒投——登记为 W-190 候选（下一班可直接施工，半小时级）。

## 七、三总包并存事实与本道让路裁定（22:5x 实测，接班必读）

**事实（现测非转述）**：Owner 今晚先后任命了三条"总包/总筹"道——本道 `st-final-build-20260926`（20:1x）、
`st-zmaster2-20260926`（20:3x，`three_piece_infra/00_plan_and_ownership.md` 立热册唯一写手制）、
`st-chief3-20260926`（22:2x 就寝前，`wave13_chief3/LEDGER_chief3.md` 指挥台账＋12 道在途字节固化＋
byte_ledger 归账派工）。三条道都在写同一批热册与同一批波次面。

**由此产生的两条硬后果（本道实测）**：
1. **袋 `base_head` 落后 ⇒ 热册同段追加互相抹**。本道连死三袋（0002/0003/0004），死因都是
   LANDING 侧 `TRANSLATION-COVERAGE` 报"6 个新建 .py 无 plain_zh"，而**入袋字节里明明有**。
   真机制：袋 `base_head` 取的是**车道分支指针**（我道停在 `3eeb935743`），dev 已前进多个袋 ⇒
   合并器对 `entries:`/`creation_tokens:` **同段追加**做 3-way 合并时冲突 ⇒ 偏向 `ours=dev` ⇒
   自家条目被丢 ⇒ 落地侧门禁判缺。**处方（已实测生效于基线重放）：投袋前
   `git reset --soft <dev tip>` 把车道指针钉到 dev，再以 dev 字节为基重放本批登记，并断言
   `lane ⊇ dev`；本道已把该断言做成 `landbag.py` 的强制闸，不成立就**拒绝投袋**。
   ⚠ 早先只重放热册、不动分支指针＝无效（我踩了一次）。
2. **他道车道的在途字节不该由我落**。chief3 台账明文："未经字节归账不得逐道顺序落地（后落旧版＝
   静默回退弹）"，并已派 `byte_ledger` 对 12 道 69 件做归账。⇒ 本道**让路**：六图役 83 件搬运成果
   与 `d5_architecture` 五图生成器/挂线机生册**不由本道入队**，保留在本道已锁车道（`git worktree lock`
   已上 48 道）＋冷备镜像内，等归账定真源后由 chief3 或本道任一方单点落。

**本道裁定（Z-F7）**：只落**本道自己新写的面**——波 1A 可信层、波 1B 提交链解毒、波 3 数据链、
波 4 灾备、波 9/10 取证案卷与 ⚑ 菜单；救援面（波 2.1/2.2 从他道搬来的字节）**转交归账**。
理由：①避免"我落旧版把他道新成果弹回去"；②本道价值在波 1A/1B/3/4 的施工，不在抢救援落地；
③符合"两班自称总包之纠偏"（W-03）的在册要求。

## 八、本道欠自己的纪律项（已实测触发）

- **CAPABILITY-LOOKUP-REQUIRED 被门拦下**：冷启动第 4 条（写第一行业务代码前调
  `capability_lookup.find(<kw>, session_id=<sid>)`）本班**漏做**，直到波 3 袋预检才暴露。
  ⇒ 已补调用；教训：**宪法冷启动序列的 4 不是可选步骤**，开工批就该做。
- 袋内新 .py 的 `# [TTL]` 值必须是**裸词**（`task_bound`/`permanent`），后跟 `:`/`（` 会被 TTL-METADATA 判非法；
  本道已在 bagprep 里统一清洗。
- `docs/_working/` **禁放 .py**（DIRECTORY-CONTRACT）；案卷型脚本一律 `scripts/governance/<wave>/`。
- CREATE-GUARD 要求新 .py 齐 15 字段头（只有 `[MODULE]/[TTL]/[STARTUP]/[CONSUMERS]` 四件不够）。

**路径改道记录（施工事实，须与案卷一致）**：施工方案 W-180.4 指定的标准探针路径 `scripts/data/ch_probe.py` 实测不可用——`.gitignore:603` 有 `scripts/data/*`，该目录仅 19 个历史件被跟踪，新件永远进不了 index（表现为 `git add` 静默不入册、袋内 sha 校验报 index 空）。本班把探针改道到 `scripts/governance/data_supply/ch_probe.py` 并在 token/翻译两册按新路径登记；对已入库且声明"正文逐字节未改"的 `final_review_chartlib/ext_01|03|04` **不改写**（改了就自毁溯源声明），改道事实只记在本册。

## 九、第二道 mandate：metaq 交接卡对账（09-27 01:3x–02:0x 实测）

Owner 中途把 `st-metaq-gc-20260924` 一系的"多会话交接汇总＋裁定执行"卡转下。基线与逐项核销结果：

| 项 | 判定 | 实测证据（命令→读数） |
|---|---|---|
| §三 基线 | **健康** | 188 passed in 9.81s ／ ruff "All checks passed!" ／ redblue `--scan` EXIT=0 且三态 151/46/86=283 掉桶=[] ／ 该会话队列 done=33 其余 0 |
| A 翻译册 3 条 `wo001_003` 净删 | **未办，且属门位** | `grep -c wo001_003 module_translation_registry.yaml` = **3**；未执行（注册表净删＝§5 high 门位，卡里只给答复口径未给答复） |
| B VM /root 两件残留 | **已办结（卡面前提过期）** | `ch_vm_ssh.py --cmd 'echo CHANNEL_OK; ls -d …'` → **CHANNEL_OK + BOTH_ABSENT**（通道活的，故"无输出"不是超时假象）⇒ 记核销，不再向 Owner 索取答复 |
| C `.runtime/tmp/st-metaq-gc-20260924/` | **未处置** | 目录在，**84 文件 / 12M**（卡写 76 文件，已漂）；删除动作等 Owner |
| D D 盘 | **比卡面更紧** | 卡：93%/56G；实测 **98% / 19G**，本会话内 41→35→22→19G 单调下降；已停发大批（25G 熔断线已破），清理策略属备份取舍＝门位 |
| E meta_question 三表入册 | **已办完** | 办前 `kind='table' AND home LIKE '%meta_question%'` = 0 → 办后 = **3**；`table` 总数 **361→364**（纯增量无净删）；经唯一写手 `Librarian.act()`；`generate_library_index.py` 重生 7 页（`docs/library/data.md` 291-293 行三卡） |
| §五 九项"已由前班办结" | **九项全部核销** | `wo009`=4 且双路径在册；`total_gates: 103`；`priority=130`；exam_loop 白名单 6 命中；ALGO_FLOW 出仓 **25** 件（≥10）；`meta_question_registry.py` 在且旧 `registry.py` 已出 HEAD |

### 本节挖出的四条新事实（都带证据，不写在别处会重演）
1. **`Librarian.act()` 与 `DatabaseService.get_depgraph_conn()` 不兼容**：`librarian.py:169` `cur.fetchone()[0]`
   对 `RealDictRow` 取 `[0]` ⇒ `KeyError: 0`，登记直接崩。正解＝`zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`
   （`lookup.py` 同源）。崩在同事务内，`lib_assets` 零残留（复查为空后重跑成功）⇒ 后续任何"经 Librarian 写图书馆"的道都会撞。
2. **`pytest -p no:cacheprovider` 在本仓必炸**（`pytest.ini` 设 `cache_dir`）⇒ `INTERNALERROR … Unknown config option`
   ＋ `no tests ran`，极易被读成"没测出问题"。**施工册 §7.1 那条配方写法是错的**，应只带 `--basetemp=<私有目录>`。
3. **`python -m zephyr.library.lookup --kind table | wc -l` = 7，真值 361**：lookup CLI 有默认 limit，`--limit 3000` 亦被截。
   判"有没有"可查，判"多少张"必须回 SQL `count(*) GROUP BY`。（差点据此把卡面"361 件"写成不实——计数口径两坑再证一次。）
4. **HEAD 上一把常红尺已修**（不在卡上的分内活）：`tests/data/test_internal_compute_provider_cohort_daily.py`
   仍断言 `columns==INSERT_COLUMNS` 旧契约，而 `a9818b2e`（09-23 cohort 闸合拢）故意令 `columns/rows=[]`
   防框架二次插行 ⇒ 按新契约重写并**加严**一条（未提交日必须 fail-visible 且不中断后续交易日），
   现 3 passed，`tests/data` 由 1 failed → 0 failed / 588 passed。

## 十、第二班续（02:0x–02:5x 实测）：落地通道真因、三件翻案、一处自修

**A. 我自己的"CLAIM-REQUIRED 根因"假设被取证班证伪（记档，防后人再照我错的抄）**
- 我原判："CLAIM 门按 cwd 解析、车道 claim 一律归主区根 ⇒ worktree 袋必死"。**错**：
  落地侧 `commit_queue_landing.py:2297/2301` 传的是**绝对 worktree 路径**，held 与 target 同根（红证脚本四道 worktree 全 True）。
- 真机制两条：① `session_concurrency.py:571-591` 判死即把 `held_files=[]` 重建，`_save` 整表无跨进程锁；
  ② `lock_files.py:1143-1155` salvage 会批量 unregister（**我自己在 01:3x 跑 `lock_files.py cleanup` 时把在途袋的 claim 清了**）。
- ⇒ **本班新纪律（可抄）**：同一会话**一次只留一袋在途**；袋在途期间禁跑 `lock_files.py cleanup`、禁 `--release-only`；
  心跳 keeper 间隔从 40s 压到 10s（`pid=0` 会话只靠 90s 心跳判活，40s 在满载机器上会偶发越界）。
  实证：单袋在途的 `0017`（图书馆索引袋）02:06 落地 done；同期四袋重叠的 `0014/0015` 全死。

**B. 三件取证/翻案（子代理交付，证据已入各自案卷；未复跑项标 E2）**
- 空壳表复测（strict，`tcp:9000` 可达，读失败 0 张）：在册 14 张候选 ⇒ **翻案 1 张**（`c1_market.suspend` 实 36 行，
  病因是旧快照过期而非 `count()` fail-silent）、**仍空 13 张**、读失败 0。⇒ 交接册里"空壳可能是假空壳"这一假设
  **在本表集合上不成立**，但"三套旧数并存（9/10/11/8）"被证实是分母各取子集，**唯一口径＝13/14**。
  `known_data_gaps.yaml` 63→**74**（纯追加 11 条，`deletion_set=[]`、`mutated_existing=[]`、diff 167 insertions/0 deletions，二次复跑幂等 0 增）。
- W-178 板块宇宙（strict 双探测 57/57 一致）：旧数 467/89,586/128/375/32,659/729/5,217 **全部复现**，
  但两处**语义错**：①729 不是"880 日K全覆盖"，而是 880 前缀 601 ＋ 881 前缀 128；
  ②gap 真值 **134＝601−467**，册面 262 系**混族**（把 881 段 128 只算进概念 gap，虚高 128）；
  ③`sector_list`(5,217) 实为 A 股池清单（`sector_name` 恒'沪深A股'），不是板块名册。
  两套口径集合差：板块码/名 **0 重合**（467 vs 375 互独），股票级交集 4,864、880 段独有 1,315；
  合成引擎两套都不读（走 `index_constituent`＋`sws2021_l1`）⇒ **W-178 的靶子由"补 262"改判为"补 134 或降级观察轴"**。
- 探针自身缺陷（我的件）：`ch_probe` 对 Date/Decimal 列 `json.dumps` 崩 ⇒ 整批探针废掉。
  已修为 `_jsonable`（鸭子类型 isoformat / numbers.Number 定点字符串），并锁 `tests/governance/test_ch_probe_json_serialization_canary.py`
  三例（含"拿掉 default 必抛"的能红证）。**修的过程本身又踩一次**：`from datetime import datetime` 遮蔽模块名，
  写 `datetime.date` 直接 AttributeError ⇒ 助手刻意不依赖模块属性名（该坑已写进测试 docstring）。

**C. 未落地清单的现状**：待落 100 件已按"一袋一投"排队（REG 册先行袋 → C1 代码袋 → C2/C3 案卷袋）；
救援面（六图役 83 件＋`d5_architecture`＋五张图 config 册＋挂线门）仍按 §七 Z-F7 让路给 byte_ledger 归账，未入队。

## 十一、metaq 卡 A 项的决定性事实（替 Owner 把"删了会不会丢东西"先查清）

Owner 要答的"1 批删 / 1 不删"，实测三件齐：
1. **旧路径条目 3 条仍在册**：`module_translation_registry.yaml:60894/60902/60910`
   = `…/wo001_003/{generate_source_line_register,intake_batch,replay_audit_to_jsonl}.py`；
2. **新路径同名 3 条已在册**（同一文件基名一一对应）：`:60403/60411/60419` = `…/wo_intake_reconcile/{同名三件}`；
3. **旧目录既不在盘上也不在 HEAD**：`ls scripts/governance/meta_question/wo001_003` → 不存在；`git cat-file -e HEAD:…wo001_003` → 无；
   而 `git ls-tree HEAD …/wo_intake_reconcile/` 列出实际文件（含 `patches/0001-wo001-registry-degraded-stub-to-real-check.pending_patch.yaml`）。

⇒ **结论**：删这 3 条**零信息损失**（新路径条目 1:1 覆盖，旧路径指向的对象已不存在），属"账实不符"清理而非知识删除；
但它仍是**注册表净删**（条目数减少），按根宪法 §5 属 Owner 门位 ⇒ 本班**不执行**，只把上面三条证据摆出来供一次勾选。

## 十二、第三班续（03:4x-04:4x 实测）：两袋死因、四处自犯、六条下修

> 证据等级同前：【HEAD实测】= `git show HEAD:` 字节；【车道实测】= 本车道盘面；【声明未验】= 在册但没在落地面验。

### 12.1 落地通道又补两条硬事实（改写了本班的投袋顺序）
1. **B2 首投死因 NO-BARE-SQL**，唯一点名 `ch_probe.py:109` 的 f-string SQL。修法＝改调
   `ch_reader._SQL_COUNT`（内收：探针复述实际执行口径，禁另立模板）。自证＝用门禁自家判定器
   `find_bare_sql_violations()` 对"新增行"复算：修前 1 处／修后 0 处。【车道实测】
2. **0019 死因 TRANSLATION-COVERAGE，根因是"袋内自带册行不能自证"**：
   `grep -c ch_read_shape_ruler` 主区册＝**0**、车道册＝2（有行）；同袋另 24 件全过，
   因为它们早在 dev（0018 落的）。⇒ 落地面读的是 **dev/主区字节**，不是袋里的册快照。
   - 对本班既有纪律的范围修正：记忆与 92 册写的"册与件必须同袋"**只是必要条件，不是充分条件**；
     对新建件必须**册先行独立袋先落 dev，件袋后投**。本班已按此改流程（`regbag.py`）。
   - 早先"0018→0017 证明同袋可行"是**误读**——那两袋的成功来自册行已在 dev，不来自同袋本身。

3. **`batch_creation_tokens.py --prefix <目录>` 会跳过「已被 git add 但尚未提交」的文件**（它按未跟踪面找活），于是三本册（95/96/pending_owner_items）在 04:1x 被 landbag `git add` 之后再也登记不上，验证面反复报缺（我连撞两次 regbag rc=7）。正解＝**用文件级前缀**（`--prefix docs/.../96_final_delivery.md` 一条插一条，实测 3 条全成功），或先登记再 `git add`。⇒ 建议入 92 册尺：**在册登记必须先于任何 `git add`**；否则"已登记"这件事本身不可复现。

### 12.2 本班自犯四处（逐条具名，不遮掩）
| # | 自犯 | 后果 | 处方（已入册/已改码） |
|---|---|---|---|
| S-1 | `landbag.py` 用 `path in registry_text` **子串**判"是否已登记" | 2 件册行漏登记却自判通过，白烧一袋（0019） | 改按 YAML 解析 `module_path` 键集合差＋门禁谓词复算；建议入尺 **G-78** |
| S-2 | 自家跑批器 `wave7.py` 把"该面不存在"记 `rc=0` | **14 目录里 9 个假绿**，"两轮全绿"根本不成立 | 改 `rc=1/n_fail=1`；建议入尺 **G-77**（临时删一个目录名再跑，看 n_fail 是否 +1） |
| S-3 | 第二次使用 `-p no:cacheprovider` | pytest INTERNALERROR＋"no tests ran"，极易读成全绿 | 跑批命令行**永久禁该旗**；已在 f10 册 §1.3 写明 |
| S-4 | 抢救副本位（`docs/_working/…/rescued/tests/`）直接判红 | 差点上报"六条防线失守"，实为 `parents[2]` 路径伪影 | 判据＝报错路径是否含非预期前缀；回正位后真值＝**1 条**且为真 |

### 12.3 六条下修／新事实（对外可直接引用）
1. **W-100 从未达成**：真跑目录仅 5/14，且 `tests/infrastructure` 1500s 未收敛（04:3x 复跑亦 Timeout）。两轮＝0/2。
2. **六图包是无主面**：属主车道 `st-mapbuild-20260924` 实测 locked＋脏 319＋自有 commit **0**＋队列零袋携带；
   5 张图 yaml 与 5 份红队件 **HEAD 全缺**。抽 7 件字节与属主车道 **same=True** ⇒ 代投无归属冲突（代投须在 message 记名）。
3. **6 台图门是装饰件**：`in_process_gate_registry.yaml`（HEAD/主区/车道三态均 103 条）里 6 个 gate_id **零命中**
   ⇒ 落地即"声明在册、无人装载"第二例。裁定 Z-F10：不随批投。
4. **RULING-REFERENCE 同一形态**：`gate_registry.yaml:1684` 写 `status: active / entry: in-process`，
   但不在 103 条自动装载名册 ⇒ "悬空裁定引用"目前**无执法**。
5. **红队真值**：`test_redblue_robust.py` 18 绿；`test_redblue_governance.py` 22 绿 1 真红＝
   冒充在活他人 sid 的伪造 `[GW:]` 尾注**零分支、零审计**（读 `reference_transaction_guard.sh` 213-241 行
   ＋四表面 `grep gw_sid_channel_unverifiable` 全零）。裁定 Z-F8（见 f10/wave7 案卷）。
6. **f05 复算推翻本班两个旧数**：①"ROOR 散文写死计数 53 处"未复现（f05 给 76/55 判据面与 26/24 精核面，
   两套并列不合并，且判据未钉真源＝新增未决 Q-52d）；②W-59 前提错——`10_d_data.md` 是被
   `.gitignore:541` 有意排除的派生域文档，不是"未跟踪散件待归属"。**两处 96 册已就地改口，不另造 v2 平行册。**
   另实测两处宪法漂移：数据集成器 **8** 子命令（`AGENTS.md` 写 7）、提交队列 **6** 子命令（只列 4 名）；
   本班不自改 `AGENTS.md`（PROTECTED-PATHS＋金哈希 post-commit 自动重基线，改了也测不出），补丁进 f05 patch 呈批。

### 12.4 清洁面（f09 册回流后本班复核通过）
- worktree **120** 树／锁 **50**→**51**（本班为 `st-ailayer-sx-20260927` 加保护锁：6 个未合 commit 且未锁）；
  ahead-of-dev **8** 道，除该道外全锁。
- 主区 index 358 条为多会话混合池；早先担心的 **135 件 staged 删除＝index-only 伪影**
  （100% blob 在 HEAD ＋ 100% 仍在盘）⇒ **W-93 可判结**，无数据丢失、无需代修。
- 盘 **18G/98%**，仍低于"25G 禁大批"线 ⇒ 本班不新增大数据面，只投文本袋并逐袋串行。

### 12.5 盘实测（本班自己就是那个吃盘的人）
`df` 从 04:36 的 **18G** 掉到 05:23 的 **12G**（99%），跨了"25G 禁大批"线 twice。归因不是他人：
05:27 用 `shutil.rmtree` 清掉本班自己的 **19 个 pytest basetemp 目录＝回收 8.06 GB**，回到 **20G**。
⇒ 处方（已入本班操作纪律，建议入 92 册）：**每轮回归跑完立刻删当轮 `--basetemp` 目录**；
跑批脚本默认把 basetemp 放 `.runtime/tmp/bt_<轮名>`，收尾即删；`du` 全树扫在 700G 盘上会超时，
判占用要用定向 glob 而不是全仓 `du -sh .runtime`。
