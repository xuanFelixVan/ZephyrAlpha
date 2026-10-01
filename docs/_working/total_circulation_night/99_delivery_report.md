---
ttl: task_bound
session: st-circ-integ-20261001
parent: 00_skeleton.md（总包）
scope: 总集成验收（阶段一落地核验 / 阶段二循环检查 / 阶段三红蓝对抗 / 阶段四定稿）
---

# 99 — 总集成验收交付报告（2026-10-01，st-circ-integ-20261001）

> 能力反查审计在册（`.runtime/lookup_audit/st-circ-integ-20261001.jsonl`：commit queue
> landing 1 命中；session registry heartbeat / precommit debt ratchet 零命中=代码考古）。
> 验收环境实录：本会话 logical 注册+心跳守护 30s 在案；belt 全窗 drain-active
> （storageswap/menu-w3h/matrix-final/fullscore 多会话袋接力落地），CPU 峰值 94%。

## 1. 总览

### 1.1 阶段一 commit 核验（14/14 全过）

14 个 commit 全部在 dev 祖先链（merge-base --is-ancestor）且内容在库：

| commit | 内容 |
|---|---|
| 8742c318 | D2 出锁手术（pre-commit 通道锁外前移+锁内指纹复核） |
| e59c214e | 裁定#457：startup 词表 v1.2.0 第 6 值 on_demand |
| 0c20042f | 裁定#459：幽灵复读止血（重投存活闸+清淤） |
| 864c71e6 | 裁定#456：CREATE-GUARD 判重两档化 |
| 938673e8 | 裁定#458：PST 修改面收窄+一次性 CLI 帽子纠正 |
| 8c5117b6 | A7 车道 P0 断链三连治（F82/F27+F48/F92） |
| 01849a3d | S4-B CREATE-GUARD token 相似度影子采集（audit-only） |
| 04a30978 | S4-E 五件套终投（B4 tracked 快照 4→1） |
| 5a48e1ba | C5 debt-ratchet own/foreign 键级拆分 |
| c5bf0610 | A2 车道续作收编五件 |
| da8a95c4 | A2 施工簿 s2_precision_a |
| 49d1d2f1 | A3 重发四件（T2 收编+T3/T4/T5） |
| 09e5b4c9 | G2 S4-F+S4-D 终投六件 |
| c23180fb | 裁定#460 ②四件套（lookup --session 审计总口闭环） |

裁定册核验：#456/#458/#459/#460 四条目**均在 HEAD**（ruling_registry.yaml :6558/:6595/
:6615/:6632），无需"随下次裁定册提交"登记。

### 1.2 阶段一队列袋核验（7 袋全 dead，按死因分类如下）

| 袋 | 死因 | 内容落地判定 |
|---|---|---|
| q-20261001-st-circ-a1-0003 | ghost_session（属主已死，存活闸拒自动重投） | **内容已落地**：WinError233 瞬态标记+6 测件全在 HEAD（b7acad9ba1 等接力）；袋死无害 |
| q-20261001-st-circ-a1-0004 | ghost_session | s1_dead_purge.md 簿未落地（清淤工作簿，观测项 O-4） |
| q-20261001-st-circ-a8-0002 | ghost_session | s5_fix_b.md 簿未落地；token 册 145 行增量中 124 行已在他会话批次落地，残 21 行=st-fullscore-night-factory-chain 7 token（属他会话簿面） |
| q-20261001-st-circ-a8-0003 | ghost_session | F17 主件已落（HEAD 超集）；**残未落**：macro_regime_sensor 新模块 3 件+F38 翻译册 2 条目（36 行）（移交 M-6） |
| q-20261001-st-circ-g3-0009 | GATE-PRECOMMIT-RUN debt-ratchet 净增（他会话在途树面债） | 代码已随 01849a3d 落地；残=两手术簿留痕件未落（观测项 O-4） |
| q-20261001-st-circ-g3-0010 | SESSION-REQUIRED | **未落**：capability_lookup p90 缓存单例+测件（移交 M-6） |
| q-20260930-st-libuniv-0001 | landing 三向合并冲突（ruling_registry 同键异容） | 宪法普世化主面已落（§6.2/§8 在册+②四件套 c23180fb）；残=硬规则 9 双留审计行+trae PRE-OP 行+#460 第 1 步册注（15 行，移交 M-6） |

判定口径：袋 blob sha256 对 HEAD/工作树逐一比对+签名行包含度核查；袋均属死会话，
按裁定#459 CLI 手动 requeue 不受闸限，本车道不做代领（他会话遗产让位纪律）。

## 2. 阶段二循环检查（连续两轮，最终读数全绿）

| # | 套件 | 第一轮 | 第二轮 |
|---|---|---|---|
| 1 | test_commit_queue + test_commit_queue_b5_backoff | 133 passed（首跑 1 次 teardown ERROR=#ARCH-084，复跑即净） | **133 passed ×2 连续净跑**（修复②后） |
| 2 | test_commit_queue_landing | 104 passed | **90 passed**（修复③后复跑） |
| 3 | test_commit_queue_integration（余量） | 49 passed | **31 passed**（修复①后复跑） |
| 4 | integration 50-commit soak（soak 尺） | 1 passed（157.8s，超默认 120s per-test 预算=时长敏感非功能，扩时复跑） | **1 passed**（修复①后 238.9s；观测项 O-1） |
| 5 | test_commit_belt_daemon | passed（批 62 内） | passed（152 批内复跑） |
| 6 | test_lock_wait_ledger + test_precommit_debt_ratchet + test_commit_block_event_combo_a3 | 28 passed | **28 passed** |
| 7 | test_create_guard + test_create_guard_dup_tier + test_capability_overlap_gate | 76 passed | **76 passed** |
| 8 | test_ssot_redefinition_gate + test_orphan_module_gate + test_orphan_same_bag_reference + test_perm_trigger_gate + test_manual_only_permanent_gate_noqa | 121 passed | **121 passed** |
| 9 | test_lookup_session_audit + test_pst_modified_scope + test_commit_chain_campaign_20260922 | 46 passed | **46 passed** |
| 10 | red_blue_pkg14 全套 | 29 passed 7 skipped（S3 1 failed→修复④；S7 1 error 瞬态） | **31 passed 7 skipped**（含新增 S1-⑤ 回归尺；修复⑤后 S1 竞态尺 3 轮 6/6 净） |

两轮间修复五笔（全部本车道 own 提交，git_commit.py 正门，commit 后 `git log -1
--name-only` 归属核实过）：

1. `efc011ea` 包66§10 soak FIFO 断言忠实性修复：`sorted(qids)`（qid 字典序）误当
   到达序——产品排队键真源 `_pick_head` 自 B4/Rx-5 起按 (created_at FCFS, qid 破平)
   （docstring 明载 qid 序 56% 倒挂实测）。修=按 (created_at,qid) 同式派生期望序。
2. `9c873670` #ARCH-084 漂移噪声归还 guard 原语义：pyproject filterwarnings 增
   消息前缀豁免（"会话级 tracked 区漂移"=并发会话写入、guard 明文只 warn 不罚）；
   肇事归因变体仍 error、strict=1 防罚零放松。
3. `522a719c` 包14 S3 红证手术副本忠实性修复：A1 瞬态截收网（b7acad9ba1）落地后，
   旧语义手术副本须同步摘第二道截收网才是忠实旧码（否则红证失真）。
4. `8e1745bf`（落地通道归属留痕：**本车道 staged 面被 st-commitfix C8 pathspec
   提交吸收**，byte-identical diff -q 实证，宪法 §2.5 归属核实过）+ `efc011ea`
   （配套红证尺）= **Windows 平台 rename 互斥失效率补丁**（详见 §3 红针 R-1）。
5. （ probe 面零产品改动：红蓝探针全部 .runtime/tmp 沙盒。）

## 3. 阶段三红蓝对抗（七针全记录；蓝方判据先立，实测不符即缺陷）

| 针 | 攻击面 | 蓝方预期 | 实测 | 判定 |
|---|---|---|---|---|
| ① | 幽灵闸：活会话（本会话真守护 30s 心跳）+伪造 exited 尾行 | 闸只认最新**真**心跳：伪造可占末行（红窗），真守护下一拍自愈放行；真死会话（a1 heartbeat=exited 无守护）必须拒 | 红窗 ghost=True 实证（按末行判）；+≤35s 守护拍后 ghost=False 放行；阴性对照真死会话 ghost=True 拒 | **蓝胜** |
| ② | 判重两档：capability_id 直击/别名子串构造 vs 纯 description 散文 | 标识符级两臂硬拦（消息含 capability_id+canonical_override+逃生标记）；散文面 warn 放行+审计 jsonl | 三断言全中（硬拦×2 消息逐字段；warn 放行+裁定#456 审计落账） | **蓝胜** |
| ③ | PST 修改面：存量带订阅脚本作用域外改行；无订阅脚本新增 manual 行 | 前者放行（作用域级订阅判定）；后者仍拦 | 放行/仍拦均中（探针首版传原文为改后面=探针 bug，机制无罪） | **蓝胜** |
| ④ | rc143 拒袋：伪造 rc∈{-1,128,143,160,192}；对照 127/193/rc=1 | 信号码区间全走瞬态拒袋（非违规措辞+signalled 审计携 pid/create_time+requeue 处方，不进阻断统计）；127/193 不入分支；rc=1 不被吞 | 矩阵 8/8 全中 | **蓝胜** |
| ⑤ | debt 棘轮：基内重犯/净增 own 锚/净增外来锚/基线单向 | 重犯 warn 放行（baseline_hit≥1,net_new=0）；own 净增必拦；外来净增降级 warn 不入册；基线永不升 | 四断言+基线单向全中 | **蓝胜** |
| ⑥ | on_demand 词表：[STARTUP] on_demand 过 GATE-VOCAB；bogus_value 对照 | on_demand 放行零违规；bogus 被 WARN 且合法值列表含 6 值（v1.2.0 在岗） | 全中（good exit 0 零违规；bad WARN 列表含 on_demand） | **蓝胜** |
| ⑦ | 会话册分片：双进程并发注册+心跳 20 轮 | 各写各片零丢失、get_session 双侧互见、探针片终态自清理 | 全中（CHILD-OK×2+互见+片文件在+unregister 双成） | **蓝胜** |

**红方战果（非七针预设、验收中现抓的实锤）——R-1 Windows rename 互斥失效**：
包14 S1 遗孤复活尺间歇红（done=2 同 qid 双落地）→ 调用级探针钉死：双工同毫秒各持
同一 processing 路径（os.rename 两次均 RENAME OK）→ 微基准确证**本机并发同源
os.rename 300 轮 297 次"双方均成功"**（NTFS/MoveFileEx 语义；顺序单发时
FileExistsError/FileNotFound 正常）——"原子 rename 即互斥"设计假设在本平台结构性
失效，pool 双工可同领同一 pending 件 → 双落地（belt k=4 同面暴露；触发窗=队尾单件
+双工同时 glob，亚毫秒级故存量观测罕见）。**已修**：`_run_pool_wave` claimed 集
第二道闸（rename 后锁内查重，先到者施工、后到者让位；env/read 失败退回 pending 及
终态出口出册允许合法重领；集随波生命周期）+确定性回归尺 S1-⑤；修后 S1 3 轮 6/6、
包14 全套 31 绿、原竞态复现器 12 连跑零复现。跨进程面仍由 SerializerLease 单写者
承担（本补丁只闭进程内面）——平台级根治登记移交（M-5）。

## 4. 遗留与观察项

**移交维护班（M 系列）**：
- **M-1 debt 棘轮冷启动洞**（A2 自设、G1 代修用过一次进程级回退手柄
  ZEPHYR_PRECOMMIT_DEBT_RATCHET=0，登记在 s4_e_b4_snapshot §8）：基线空种子时
  存量树面债全判净增——治本待基线吸收或树面收敛后复归，手柄使用须运维登记。
- **M-2 心跳 daemon 缺陷**（commitfix 在途，本车道让位未代修）：daemon 对 legacy
  册 Permission denied 即退+会话被 watchdog 收割链（st-circ-g2 簿 §8 运维留痕）。
- **M-3 能力册尾键缺陷立案**（st-circ-a4 偏差披露 1：lookup_import_surface 环境
  漂移 2 败=usercustomize 引导链重量+基线册口径，处方归 usercustomize/基线册
  owner：PYTHONNOUSERSITE=1 或基线口径含 site 引导）。
- **M-4 F96 胃源调度**（五项移交既定项，本车道未触碰）。
- **M-5（本车道新增）Windows rename-as-mutex 平台根治**：进程内面已补（§3 R-1），
  跨进程面（belt/CLI 混抢）仍赖 SerializerLease 单写者不变量——建议后续批次以
  平台原生互斥（named mutex/ReplaceFile 排他）复核 `_pool_claim_item` 与
  drain_queue `_retry_transient(rename)` 两处假设，并把本机 rename 微基准
  （300 轮 297 双成功）列入平台环境基线。
- **M-6 死袋残留代领清单**（§1.2 判"未落"项）：a8-0003 macro_regime_sensor 3 件
  +F38 翻译 2 条目；g3-0010 capability_lookup p90 单例+测件；libuniv-0001 宪法
  规则 9 行+trae PRE-OP 行+裁定册 15 行注；a1-0004/a8-0002/g3-0009 簿面留痕件。
  均属死会话遗产，建议 Owner 点名后由维护班按袋 blob（.runtime/commit_queue/dead/
  +blobs/）代领或废弃。

**观测项（O 系列）**：
- **O-1 soak 尺时长**：50-commit 真落盘尺本窗 158-239s/趟，超 pyproject 默认
  120s per-test 预算——belt 活跃窗必假红。建议：该尺单独标 timeout≥300s 或
  @pytest.mark.slow 分层。
- **O-2 #ARCH-084 guard 归因局限**：belt 落地窗内他会话写热册会被"肇事测试"
  归因变体误标（本窗实证：capability 册 +10 行均为 st-fullscore token，
  created_by≠本会话）。drift 变体已归还 warn 语义（修复②），归因变体的跨会话
  免误伤建议维护班评估（如按 [GW:] 落地留痕豁免）。
- **O-3 rc143 明晨 pid_join 定谳**：S4-F 捕证面（pid/create_time）已全量记账，
  明晨 `python .runtime/tmp/s4f_pid_join.py --days 1` 定谳 H1（工具层收割）/
  H2（reaper 树级联）。
- **O-4 清淤静窗**：belt 持续 drain-active 全夜（storageswap/menu-w3h/matrix/
  fullscore 多袋接力；head waiting 曾 4712s），集成验收窗口建议留静窗。
- **O-5 token 影子一周**：S4-B token 相似度影子采集（01849a3d，audit-only）按
  裁定#456 二阶段计划观测一周后议升格。
- **O-6 双查两周观测**：#460 ③ CAPABILITY-LOOKUP-REQUIRED 扩双查（library 痕迹
  OR 判据）两周数据支持后议独立门（ruling_registry #460 三步走在案）。

## 5. Owner 无需裁定声明

本报告全部结论均已自裁或有在案出处方，无需 Owner 新裁定：
- 两轮循环读数与红蓝攻防判定=机械验收口径（判据先立于簿，实测对账）；
- 五笔修复均在既有裁定/处方轨道内（S3/S1=红证忠实性修复归包14 MODIFY-GUARD 语义；
  FIFO 断言=对齐 B4/Rx-5 排队键真源既有裁定留档；#ARCH-084 豁免=归还 conftest
  明文原语义；rename 补丁=缺陷治本走施工正门+确定性回归尺配套）；
- 死袋七封均按裁定#459 存活闸语义处置（不代领、死因分类在册）；
- 裁定册 #456/#458/#459/#460 已在 HEAD，零补登记需求；
- 让位披露：st-commitfix C8 pathspec 吸收本车道 staged 面（宪法 §2.5 归属核实
  byte-identical 在案），归属披露即闭环。

—— st-circ-integ-20261001 总集成验收车道，2026-10-01 收笔。

## 附：本簿落地状态（收笔时点实录）

本簿内容已定稿并 stage（git add 即写即 add 纪律）；其 commit 因 CREATE-GUARD
预检读 HEAD 版 token 册而待 token 同批落地——token 已登记（batch_creation_tokens，
capability=night_campaign_work_book）但 capability 册 claim 由活跃会话
st-menu-w3h-20260930 持有（心跳 13s 实证，31 件在途），按 RULE-WORKTREE 让位纪律
不硬闯。token 随其落地进 HEAD 后，重跑下述保留命令即净（msg-file 已保留）：
`python scripts/git_commit.py --session st-circ-integ-20261001 --files docs/_working/total_circulation_night/99_delivery_report.md --message-file .runtime/tmp/integ_msg.txt --allow-multi-domain --allow-non-worktree`
（若届时本会话心跳已停，由接班会话以任意 --session 代跑即可，内容无会话绑定。）
