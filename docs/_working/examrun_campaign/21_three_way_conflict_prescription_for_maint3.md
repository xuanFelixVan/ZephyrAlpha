---
ttl: task_bound
title: 落地仲裁把"同作者顺序追加"判成真冲突——处方件（提维护三班）
created: "2026-10-12"
sid: st-examrun-20261012
family_id: EXAMRUN-CAMPAIGN-20261012
---

# 一、一句话

`commit_queue_landing.py` 的整文件三方仲裁只看"两侧都相对基底改过"，不看"改的方式是否互不重叠"，
于是**同一个会话在同一文件上先后投两袋**（班账/追加型台账的日常形态）必然后袋死信——
本晚实测死 32 支，其中 26 支（81%）撞的就是 `docs/_working/*/**.md` 这类**只有追加**的件。

# 二、代码位与判据原文（可直接 grep）

- 文件：`scripts/governance/commit_queue_landing.py`，非注册表 catalog 族分支，约 2428–2446 行：

```python
_base = base_text if base_text is not None else ""
if theirs_text == _base:        # 袋侧没改 → whole-file noop
    ...
    return None
if ours_text == _base:          # dev 侧没改 → 取袋侧
    return theirs_text.encode("utf-8")
raise RuntimeError(f"[landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: {rel}")
```

- 语义缺口：`ours` 与 `theirs` **都**不等于 `base` 就判冲突。追加型单作者件的真实关系是
  `ours ⊆ theirs`（dev 已吸收较早的一袋，后袋是它的严格超集），信息零丢失，却被当成分叉。
- 触发条件（本晚实测形态，可复现）：袋 A 与袋 B 同会话同件、A 的基底＝B 的基底＝入队时刻 dev sha，
  A 先落地推进该件 ⇒ B 落地时 `ours`（含 A）≠base 且 `theirs`（含 A＋B）≠base ⇒ 死信。
  本班 0021 即此例（A＝0019 于 21:47 落 `00_ledger.md`，B 的基底是 21:28 的 dev sha）。

# 三、证据（尺＝死信档案全量扫描，零抽样）

| 口径 | 袋数 | 会话数 | 备注 |
|---|---|---|---|
| 全池 `dead/` 累计含"双侧皆改真冲突" | **239** | **33** | dead/ 永不清理 ⇒ 这是历史累计 |
| 本晚（`q-20261012-*`） | **32** | **9** | maint3 8／gpuwo 8／gpux2 5／mineloop2 3／backfix3 2／deadcure3b 2／fclean3 2／examrun 1／gpux3 1 |
| 本晚按撞件类型 | 追加型台账 **26**／代码件 5／yaml 1 | — | 累计口径为 70/140/29 |

- 取数法（接班可复算）：遍历 `.runtime/commit_queue/dead/*.json`，
  `dead_reason` 含子串 `双侧皆改真冲突`，会话取文件名 `q-<日期>-<sid>-<NNNN>` 段，撞件取死因尾串。
- 我先前向统筹报的"跨班 5 袋"是**本晚本班＋矿考二班的子集且口径写错**，本件以全量扫描数取代（旧话留档不删）。

# 四、三条候选处方（含代价与是否弱化闸）

1. **甲（推荐）＝仲裁前加"多重集包含"前置判据**：在 `raise` 之前比 `ours`/`theirs` 的行多重集，
   若 `ours ⊆ theirs` 取 `theirs`（袋侧为严格超集），若 `theirs ⊆ ours` 走既有 noop 吸收，
   **两者都不成立才死信**；并在 `meta.noop_audit` 记一行包含判据与两侧行数。
   - 代价：一处函数改动＋三态测试；不放松任何真分叉（交叉改动仍死）。
   - 覆盖面：本晚 32 支里的追加型 26 支；累计 239 支里的 70 支。
2. **乙（推荐与甲并施）＝死信文案给可执行出口**：`dead_reason` 附带重基配方
   （`git show HEAD:<rel>` 为基＋本袋差集只追加，附两侧 sha256），使人工/自动重投一次即成，
   不必再反推基底。代价：仅文案与元数据，零语义变更。
3. **丙（不建议）＝入队侧给同会话同件的后袋改基底**（后袋 base 取前袋落地后的该件 sha）。
   代价：与在册"基底＝入队时刻 dev sha"口径冲突（`backfill-base-head` 工具与既有史证语义都要改），
   且只治同会话、不治跨会话同件——症状层，非根因层。

**建议＝甲＋乙并施，丙不做。** 甲减少无谓死信，乙保证真分叉仍走人工但不再盲猜；
两者都不触碰"双侧交叉改动仍判死"的原有防线（不属弱化闸／不属白名单／不属新豁免）。

# 五、验收法（维护三班可直接套）

1. 三态单测：`ours⊆theirs`→取袋、`theirs⊆ours`→noop 吸收、交叉→照旧 `RuntimeError`；
2. 自然实验：同会话同件（班账类）连投两袋，第二袋应落 `superset absorb` 而非死信；
3. 反向自证：故意让两袋各删不同段（真分叉）⇒ 仍须死信，证明甲没把闸放软；
4. 落地读回：`git show HEAD:<rel>` 与袋侧字节 sha256 逐字相等（追认三步之步四）。

# 六、本班侧已生效规避（不等他班修）

- 同一件多轮内容**并成一袋**投；投前确认无"同会话同件"的在途袋（本件即按此规则单独成袋，
  与在飞的班账袋不撞件）。
- 必须分投时：隔 C1 合批窗，且在前袋落地后以**新 dev sha** 为基底。
- 出处：本班班账 `docs/_working/examrun_campaign/00_ledger.md` §25.11／§25.7／§廿六。
