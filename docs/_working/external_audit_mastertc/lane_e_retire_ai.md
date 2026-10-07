---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 E：退役+AI 层审计 findings

> 审查时点 HEAD=`649a8c93c7`（dev 同指针）；被审对象=总包会话 st-mastertc 2026-10-06 夜~10-07。全程只读，零写操作。

## P0 候选

**P0-E1（C441 词表门翻转的授权锚断链——交付报告引用了在册裁定中不存在的授权分项）**
- 交付报告（HEAD `docs/_working/master_tc_night/99_delivery/交付报告.md:135`）标 `C441 | L10 | DONE | #488 B 段：词表门判据已改写（BLOCK_FLIP_CLEAN_STREAK=20）批准翻转`；`:148` 的 B 段清单亦含"C441 词表门翻转"。
- 但在册裁定#488 全文（HEAD `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` L4242–4274，commit `6555113e56` 落册 +33/-0 纯插入）B 段**只有 16 项，无 C441**；L10 作业簿 §三（HEAD `lanes/L10_rulings/00_workbook.md`）同样无 C441。C441 只出现在 `docs/_working/master_tc_night/00_orchestration.md:57`（战役自书文档，非真源）。
- 链条=orchestration §六（17 项含 C441）→ L10 落册（16 项，C441 被静默丢弃、无任何痕迹解释）→ 交付报告仍以"#488 B 段"为 C441 授权依据。宪法 §5：flag 出厂翻转→Owner 门位；§9.11：Owner 门位经裁定登记生效——登记册即唯一正式通道，现该通道内**无此授权记录**。宪法 §4.4"文档矛盾=事故"。
- 缓解（生产风险当前为零）：翻转本体未执行——gate mode 仍 warn 起步（`fms_hygiene_gate.yaml` 卡面注释"FMS_HYGIENE_GATE_MODE=warn 起步…翻 block=OWNER-GATE"）；判据改写（`BLOCK_FLIP_CLEAN_STREAK: Final = 20`，`fms_hygiene_gate.py:119`）系他会话 st-nightsweep-sw6 `984c1787f8` **在先已落 HEAD** 的工作，非本夜成果；09-30 读数连零 2/20 未达标（`99_owner_gate.md:25`）。
- 定级理由：非生产行为事故，但属**授权链完整性事故**——若达标窗到来时按交付报告采信"#488 已批翻转"，将在无在册授权情况下翻转 Owner 门位。修复处方：#488 补记 C441 分项（同 commit 原子）或交付报告撤回该引用改"待裁"。

## 逐项 verdict（1~7）

### 1. 退役批零删除纪律 — **真完成（纪律遵行实证）**
- `6bb3c7e940`（C39）：1 文件 +1/-1，无 D。`0e6a76bbcb`（C85）：3 文件 +108/-3，无 D。`739b6fe466`（C169+C475）：2 文件 +506/-15，无 D。三袋净行为均为行级修改/新增，非破坏。
- 全夜 44+ 条逐条扫：`git diff-tree --name-status -r` 对全部 st-mastertc commit 的 `^D` 扫描 = **0 条文件删除**。numstat added=0 交叉核验出 2 处疑似，均澄清为误报：①`65e48209a4` 的 `tests/gov/governance/red_blue_pkg14/__init__.py` = **空文件新增**（blob=e69de29 空串恒值，numstat 0/0 被 awk 误读）；②`02fc4d72a4` 的 `tests/research/backtest/test_closed_book_tick_gate.py` = **文件内 24 行 xfail 装饰器摘帽**（文件在 merge 结果与 HEAD 均存续，blob `073165779d`）。
- 注册表类 commit 的 `[allow-mass-deletion:索引老化伪影]` 自述抽检 3 例（`fa165c56a1`/`01bf541fbb`/`3f47dbd6d5`）：实读均纯插入（+46/+16、+1×N、+5/+228），与自述一致。

### 2. C85 谷时偏好 — **真完成（接线在位+出厂关+如实声明）**
- HEAD `config/schedule_gate_policy.yaml:49-52`：`free_window_pref { enabled: false, windows: ['02:00-07:00'], boost: 0.5 }` — **enabled=false 出厂关在位**。
- `src/zephyr/ai_layer/scheduling/dispatcher.py`：`free_window_boost()` L154（缺失/关闭/坏配置一律 0.0 保守不抛）、`__all__` 导出 L67、`work_order_score(..., free_boost)` L125/136/147、`rank_pending` L202-209 真调用 `work_order_score(..., free_window_boost(now, policy))` — 三层接线全在。
- 消费端可达性：`work_order_score` 唯一生产调用方=`rank_pending`；`rank_pending` 唯一生产调用方=`api_server.py:5398`（`/api/schedulegate-queue` 路由，前端 `api.js` `fetchSchedulegateQueue` 消费）——**M4 排序消费端可达生产路径**（仪表盘排产页投影），非死代码。出厂关下零行为变化。
- 4 单测全在 HEAD：`test_dispatcher.py` L343（窗内外+端点）/L351（保守退化×4 态）/L361（排序偏好≠翻转优先级）/L385（naive 拒收回归）。
- "接线但出厂关"**如实声明**：commit 信息、L8 作业簿 C85 节、交付报告 `:96` 三处一致声明"出厂 enabled:false，翻转走 OBJ_R 修订窗"。

### 3. C39 miniQMT 文案 — **真完成**
- HEAD `src/zephyr/frontend/dashboard/web/pages/bridge.html` 第 3 行在位："miniQMT 2026-09-18 **仅实盘退役（模拟盘持续供数，裁定#339）**"。
- `git grep '券商全面清退' HEAD` 仅命中 2 处 `_working` 历史记录文档（workorders_docs_misc.md 的旧残点台账、data_chain_report.md 的历史引文），无任何活页面残句。

### 4. C169+C475 --cascade-deprecate — **真完成（工具+立法+测试）；消费定性=过渡性备用能力，零实际退役事件**
- HEAD `scripts/governance/d5_architecture/lifecycle/retire_module.py`：`cascade_deprecate_contracts()` L250 —— 单 CAS 写（`safe_write_text` + `expected_base_sha256`）落 `deprecated/deprecated_reason/deprecated_date`；幂等（`deprecated is True → skip`）；ISO 日期引号化（`patch_contract_fields` L224 `_ISO_DATE` 正则 + `json.dumps` 防 YAML date 漂移）；missing 单独记账。旧 `--cascade-contracts` **恒拒**（L974-977 "REFUSED: 已废止"）。dry-run 零写侧（L755-757 仅追加 `[DRY-RUN]` 预告，不触 `cascade_deprecate_contracts`）。
- 立法锚在位：`trae_032_module_lifecycle.yaml:459`（Owner 增枝批文②由该条取代）。
- 19 单测全在 HEAD（`tests/gov/governance/lifecycle/test_retire_module.py`，含 4 新增：execute 打标 L309/dry-run 零写 L331/缺旗回归 L342/字段手术保邻 L351）。
- **真消费=零**：`git grep cascade-deprecate` 在 scripts/src 无任何 tool 外调用方；契约册 `architecture_model/contracts/cross_layer_contracts.yaml` 无任何 `deprecated: true` 条目（打标 reason 字符串只存在于工具源码自身）。定性：trae_032:459 立法的执行器+测试齐备，属"立法义务兑现"（C475 销账语义=实现义务清偿），实际 IFC-007 级联退役事件本夜为零——**无消费≠不必要**（立法配套件），但不得解读为"已有模块经此通道退役"。

### 5. l8 未合并分支面（tip=`cf5b6ddcf7`，未并入 dev）— 13 卡总对账：**5 真完成 + 1 正确 OWNER + 7 过渡-待合并（其中 2 卡披露不全 P1）**
- 独有提交 4 条：`cf5b6ddcf7`（merge_state DEFERRED 补记）/`9094d25f55`（作业簿+B类映射表）/`f4910d5b03`（C314 HANDOFF）/`9c37e38775`（C394+C84 双注册表）。
- 内容面（vs merge-base `cd6ad4f7d0`）=**恰好 6 文件 +242/-1**，与交付报告 §八"六文件差异面零丢失"自述吻合：

  | 文件 | dev/HEAD | l8 分支 |
  |---|---|---|
  | `lanes/L8_retire_ai/00_workbook.md` | **无**（lanes/ 下无 L8_retire_ai 目录） | +112 |
  | `lanes/L8_retire_ai/b_class_map.md`（C136 载体） | **无** | +39 |
  | `ai_layer_vision/HANDOFF_wave2_closeout.md`（C314） | **无** | +50 |
  | `_registry/catalogs/strategy_registry.yaml` C84 `lifecycle_status_values` 九态块 | **无**（HEAD grep 仅命中 `src/.../registry_state_vocab.py` 的字段名引用，注册表块缺席；代码内置回退表含 shelved 兜底） | +15/-1 |
  | `_registry/catalogs/migration_registry.yaml` C394 `windows_service_file_retire` 行 | **无** | +11 |
  | `capability_canonical_file_registry.yaml` C314 token | 无此条 | +15 |

- 勘误：任务书路径 `config/strategy_registry.yaml` 不载该块——真身=`docs/01_policies_and_standards/_registry/catalogs/`，两路径 HEAD 均无此块。
- `tests/meta/shared/lifecycle/test_registry_state_vocab.py` **在 HEAD 存在但整文件 `pytest.skip`**（st-chiefzc-rescue-20260928 捞回袋标注，模块当时 ORPHAN 缓袋）——C84 卡"11 passed 1 skipped"中的 1 skipped 即本件；C84 的机读块在 HEAD 无硬测守护。
- C136 是什么（自分支版作业簿）：B 类波 6.2 施工位映射表（W-168 出口判据"四行映射表，无表不算完成"），载体=`b_class_map.md`，纯文档定性件（B5 收敛/B7 五子案未施工/B9 挂起有主/B10 余 --auto-fix 闸）。
- **13 卡三态 vs HEAD 落地逐卡点名**（交付报告 `:94-106`）：

  | 卡 | 报告标态 | HEAD 实证 | verdict |
  |---|---|---|---|
  | C39 | DONE | `6bb3c7e940` 在 HEAD 史，文案实证 | **真完成** |
  | C85 | DONE | `0e6a76bbcb` 在 HEAD 史 | **真完成** |
  | C169 | DONE | `739b6fe466` 在 HEAD 史，工具+19 测 | **真完成** |
  | C475 | DONE | 同件销账 | **真完成** |
  | C267 | OWNER | A 段登记关账，归档不真删 | **正确移交（非遗漏）** |
  | C84 | DONE（注"在分支"） | 块只在分支；HEAD 靠代码内置回退表承载 shelved | **过渡-待合并**（卡面已披露，诚实） |
  | C314 | DONE（注"合并 DEFERRED"） | HANDOFF 文件只在分支 | **过渡-待合并**（已披露） |
  | C136 | DONE（**无分支注记**，引用"b_class_map.md §三"） | 载体只在分支，HEAD 读者遇断链引用 | **过渡-待合并，披露缺失（P1）** |
  | C394 | DONE（**无分支注记**） | 本夜增量=候选册行只在分支；deprecated 文件头注记系 09-30 B11/ae952d32 **在先工作**（HEAD `windows_service.py:3-7` 实证） | **过渡-待合并，披露缺失（P1）** |
  | C96 | DONE | 登记载体（作业簿节+HANDOFF §四.2）只在分支；替补锚#417（L3305 active）/ #450（L3740 active）经核在册 ✓ | **过渡-待合并** |
  | C301 | DONE | 销账登记位=分支作业簿；底层数据（NB2 09-30 删除回执）在 `.runtime/tmp` 非 HEAD 可证 | **过渡-待合并** |
  | C412 | DONE | 读数台账只在分支作业簿（观测性交付） | **过渡-待合并** |
  | C462 | DONE | 定性节只在分支；248 件清单在 `.runtime/tmp` 本就非持久 | **过渡-待合并** |

- 结论：无"假完成"级（交付物皆存在、未丢失），但 8 张 DONE 卡中 7 张 HEAD 无落地面；C136/C394 未按 C84/C314 标准作卡面披露（全局 §七.1 DEFERRED 注记部分缓解）。

### 6. mine 未合并分支（`f73bf8714d` W1 初版）— **残渣可归档，无独有内容需捞**
- 独有 1 commit、8 文件（旧路径 `master_tc_20261006/01_skeleton/` 七件 + `r5_exemption.md`）。mine2=`6072df11ef` 已在 dev（`git merge-base --is-ancestor` 通过）。
- 8 文件中 6+1 件已被吸收：七件骨架经 L0 改名波 `600abe9991`（18 文件 git mv）以**字节同源**落 HEAD 新路径 `master_tc_night/01_skeleton/`——抽检 `03_block_backtest_exam.md` mine vs HEAD 仅差 1 行路径自引用（`master_tc_20261006`→`master_tc_night`）；`r5_exemption.md` 同在 HEAD。
- 第 8 件 `00_环节总表.md` 被 mine2 **有意重写取代**（174/200 行差；三真源读数校正 F系9/132表10/工单1；126 卡挂接；检测法改为六块抽检+≤10 上限）。
- 新立卡建议差集收敛核验：W1 的 17 条 vs mine2 的 10 条——P0×4（F027/F028/F072/F082）**逐字一致保留**；W1 多出的 F029/F031/F035/F036/F084/F094/F115 七条在 HEAD 树均有承接（F094 经 C96 卡挂接 `00_环节总表.md:114`；F115 以"按 §五建议补卡挂接，工单不重写"五处块文件引用；余者有遮蔽/在册主）。
- 处置定性：**可归档删档**；如求极致保守可把 W1 版 17 条全列表作历史附件归档，非必须。

### 7. 裁定#488 A/B 段与宪法 §5 — **A 段无漏保（且偏严）；B 段无越权施工实证；1 项踩线口径（C24）待证；C441 授权断链见 P0-E1**
- 落册本体：`6555113e56` 对 HEAD **+33/-0 纯插入**（接 #487 尾，原文零触碰）✓。
- **A 段 7 项**（C63/C287/C109/C410/C267/C36+C37/C45）vs §5 四门位（production 流转/注册表净删/flag 出厂翻转/资金破坏性操作）：C63/C287=实盘资金+生产流转，精确对门 ✓；C109/C410/C267=物理删除三段式——**不属 §5 明文四门位，保留口径比宪法下限更严**（与 RULE-DATA-OPS 三步验证纪律自洽，属安全冗余）；C36/C37/C45=VM 环境依赖，非门位事项、留Owner 合理。**无应裁未裁、无漏保。**
- **B 段 16 项**逐项过（C81/C82/C398/C102/C103/C19/C21/C24/C38/C65/C320/C445/C490/immutable_tree/AI 点火/C300）：
  - **零 flag 翻转、零净删、零 production 流转、零资金操作在夜内发生**：C300"维持现状=非翻转"（效力与边界明示；落地件 `bb6a03f5c1` 纯注释 1 行实证）；C19 warn 维持；C21/AI 点火**封存维持**（保守向）；ROOR 全夜零 st-mastertc commit 触碰+全夜零文件删除 → C24 净删**仅批未执**。
  - **C24（注册表净删代裁）= 唯一踩 §5 明文门位的口径**：以"带 successor 且零消费者"前置条件收窄后授权净删候选。依 §9.11"Owner 门位经裁定登记生效"，#488 本身即正式通道产物，架构自洽；但授权效力依赖 Owner 2026-10-06 对话授权原文（"全部未完成任务开工、遇到问题自己裁定、最终不留待裁定内容"）——**待证（授权自述）**，且 blanket 授权覆盖"注册表净删"级决定属扩张解读。建议执行前回 Owner 单项确认。
  - C320"图15 human_gate→medium 落册"：medium≠§5 high 四门位、且比宪法 §5.1"未列出域默认 low"更严——不踩线；但 **risk_tier_registry.yaml（130 行）无 fig15/strategy-lifecycle 域行，全夜无 commit 触碰该册**——"落册 DONE"未兑现到注册表实体，落点仅裁定文本（P2）。
  - C445"判不出=记红不拒单"：交易邻接判别器的 fail-open 判据（暂记）——P2 提示施工前补与实盘门位/KillSwitch 的交互评审。
  - C65"按 99 册建议逐条批"：by-reference 批量授权，条目未在册枚举——P2 空泛授权面。
  - C81/C82/C398/C102/C103/C38/C490/immutable_tree 补成册：无门位触碰。
- C96 补充核验：其援引的补批文锚 #417（L3305 active"12 项已批项补批文"）/#450（L3740 active）均在册 ✓。

## 证据块

```
# 任务1
git show --stat 6bb3c7e940        → 1 file, +1/-1
git show --stat 0e6a76bbcb        → 3 files, +108/-3
git show --stat 739b6fe466        → 2 files, +506/-15
git log --grep=st-mastertc --format=%h | while read c; do
  git diff-tree --no-commit-id --name-status -r -m --first-parent $c | grep -c '^D'; done → 全 0
numstat added=0 命中 2 处 → 65e48209a4=e69de29 空文件新增；02fc4d72a4=M（xfail 摘帽 24 行，文件存续）
git ls-tree 02fc4d72a4 -- tests/research/backtest/test_closed_book_tick_gate.py → blob 073165779d 存续

# 任务2
git show HEAD:config/schedule_gate_policy.yaml | sed -n '49,52p' → free_window_pref enabled:false
git show HEAD:src/zephyr/ai_layer/scheduling/dispatcher.py L154/67/125/202-209
git grep -n free_window_boost HEAD → dispatcher.py+test_dispatcher.py 4 测（L343/351/361/385）+redblue F6 登记
git grep -n rank_pending HEAD -- src → api_server.py:5398（/api/schedulegate-queue 生产路由）

# 任务3
git show HEAD:src/zephyr/frontend/dashboard/web/pages/bridge.html | sed -n 3p
  → "miniQMT 2026-09-18 仅实盘退役（模拟盘持续供数，裁定#339）"
git grep -n '券商全面清退' HEAD → 仅 2 处 _working 历史记录文档

# 任务4
git show HEAD:scripts/governance/d5_architecture/lifecycle/retire_module.py L250-296/974-977/755-757
git show HEAD:tests/gov/governance/lifecycle/test_retire_module.py | grep -c 'def test_' → 19
git grep 'cascade-deprecate' HEAD -- scripts src（排除工具本体）→ 0 命中
git show HEAD:architecture_model/contracts/cross_layer_contracts.yaml | grep deprecated → 0 条目级标记

# 任务5
git log --oneline dev..session/st-mastertc-l8 → cf5b6ddcf7/9094d25f55/f4910d5b03/9c37e38775
git diff --stat cd6ad4f7d0..session/st-mastertc-l8 → 6 files, +242/-1
git ls-tree dev -- docs/_working/master_tc_night/lanes/L8_retire_ai/* → 0
git ls-tree dev -- docs/_working/ai_layer_vision/HANDOFF_wave2_closeout.md → 0
git grep -c lifecycle_status_values session/st-mastertc-l8 -- docs/.../strategy_registry.yaml → 在分支 L41-50 九态
git grep -c lifecycle_status_values dev -- docs/.../strategy_registry.yaml → 0（HEAD 仅 src registry_state_vocab.py:72 字段名）
git grep windows_service_file_retire dev → 0；分支 catalogs/migration_registry.yaml L303-309
git show dev:tests/meta/shared/lifecycle/test_registry_state_vocab.py L29 → pytest.skip(allow_module_level)
git show HEAD:src/zephyr/trading/windows_service.py L3-7 → [DEPRECATED] 2026-09-30 B11 在先标记

# 任务6
git log --oneline dev..session/st-mastertc-mine → f73bf8714d（8 文件旧路径）
git merge-base --is-ancestor 6072df11ef dev → true
git diff mine:...03_block_backtest_exam.md HEAD:...03_block_backtest_exam.md → 1 行路径自引用
git diff mine:...00_环节总表.md HEAD:... → 174+/200-（mine2 有意重写）
W1 17 条 vs mine2 10 条：P0×4 一致；7 条差集在 HEAD 有挂接/工单承接（00:114 F094=C96；F115 五块文件引用）

# 任务7
git show HEAD:docs/.../ruling_registry.yaml | sed -n '4242,4274p' → #488 全文 33 行
git show --numstat 6555113e56 → 33 0（纯插入）
sed -n '4242,4275p' | grep C441 → exit 1（在册无 C441）
交付报告 :135/:148 与 00_orchestration.md:57 含 C441；L10 workbook §三无 C441
git log --grep=st-mastertc -- risk_tier_registry.yaml → 空（全夜未触）
sed -n '3305p;3740p' ruling_registry.yaml → #417/#450 active 在册
```

## 小结 + P1/P2 建议

**小结**：车道 E 七项审计中，退役批零删除纪律（任务1）为全场最干净——44+ commit 零物理删除、伪影自述抽检属实；C39/C85/C169/C475 四卡为可复核的**真完成**（接线、文案、工具、测试均在 HEAD 实证）；C85"接线但出厂关"三处口径一致如实。主要风险不在施工面而在**账面与真源的三个断点**：①P0-E1 C441 授权锚断链（登记裁定无此分项而交付报告引为已批）；②l8 分支 6 文件 242 行（含两注册表增量）三次 DEFERRED 未并入，致 13 张 L8 卡中 7 张 DONE 在 HEAD 无落地面（C136/C394 披露不全）；③C320"落册"未兑现到 risk_tier_registry 实体。裁定#488 本身 A 段无漏保、B 段无越权施工实证，唯 C24 净删代裁口径待证（授权自述）。

**P1**：
1. 修复 P0-E1：#488 补记 C441 分项（同 commit 原子）或交付报告撤回"#488 B 段"引用改"待裁"；补记前禁止任何 block 翻转。
2. l8 分支按 `close_lane.md §二` 处方尽快合并（6 文件 +242/-1 零内容风险；C84 机读块缺位期间 HEAD 靠 `registry_state_vocab` 内置回退表承载 shelved=双真源窗口期）。
3. 交付报告 C136/C394 卡面补"在分支"注记（对齐 C84/C314 披露标准），消除 b_class_map.md §三 断链引用。
4. C24 净删候选执行前回 Owner 单项确认（不沿用 blanket 对话授权）。

**P2**：
5. C85 潜在时钟语义错位：生产调用方 `api_server.py:5398` 注入 `datetime.now(timezone.utc)`，而 config 窗声明"本地时 HH:MM-HH:MM"——出厂关下无害，启用前必须统一（折算本地或改 config 口径）。
6. `free_window_boost` 跨午夜窗恒 False（redblue_findings F6 已自曝登记）——OBJ_R 窗补 wrap 判定。
7. C320：risk_tier_registry 补 fig15 域行，或将卡面口径改为"按 §5.1 默认"。
8. C445 fail-open 判据（判不出=记红不拒单）施工前补实盘门位交互评审。
9. C65 执行时逐条回填裁定引用，消除 by-reference 空授权面。
10. mine 分支删档前可选归档 W1 版 17 条建议全列表（实质已被吸收，非必须）；裁定#488 affected_files 的 `master_tc_20261006` 旧路径宜加"现路径 master_tc_night"注记。
