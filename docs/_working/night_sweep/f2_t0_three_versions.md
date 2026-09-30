---
asset_id: "DOC:docs/_working/night_sweep/f2_t0_three_versions.md"
ttl: "task_bound"
title: "F2 · t0 甲位三版本对比表+五要素裁定+施工留痕（Z-C1 收口）"
session: st-menu-t1f2-20260930
completes_when: "裁定施工落地入 HEAD 且 ruling#455 登记，本册随夜战归档"
---

# F2 · t0 甲位三版本对比表 + 五要素裁定 + 施工

> Owner 本夜批复（原文留痕）："t0 三版本打架：对比表出来你自己裁定，然后直接施工执行"
> ——授权总筹体系按五要素自裁并直接施工。本册=该授权下车道 T1-F2 的对比表、裁定与施工台账。
> 前案卷：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/ADJ_t0_jiawei_versions.md`（2026-09-25 实测）+ Z-C1（ADJ_rulings.md：甲位=放行 V2 写回，附两条硬前置）。
> 纪律：本项涉交易执行面——只动版本管理/指向/标记，未改任何实盘行为逻辑（实盘暴露论证见 §3.2）。

## 1. 三版本对比表（本班 2026-09-30 盘面实测，全部可复算）

| 维度 | V1（主区=HEAD 现状） | V2（worktree 治本件） | V3（0033 在册 blob） |
|---|---|---|---|
| 代码位置 | `scripts/backtest/auto_mount.py`（git clean） | `.worktrees/st-t0-matrix-20260924/scripts/backtest/auto_mount.py`；逐字节同副本 `.runtime/tmp/st_t0_monitor/fixed/auto_mount.py`（双盘互证） | `.runtime/commit_queue/blobs/f436d2b981b4…`（0033 袋 JSON 已不存在，blob 仍在） |
| 盘上字节 / 归一 sha256[:12] | 61,143 B / `7316d34b0bd7`（本班复测=ADJ 同值） | 64,573 B（CRLF）/ **LF 归一 63,374 B / `e4dc2de62355`**（=t0_matrix LEDGER D-51 自报治本件 sha，逐字吻合） | 64,581 B（CRLF）/ LF 归一 63,381 B / `07cb0777c8e7`（与 V2 归一恰差 7B=一处长串折行） |
| 功能面 | 判定窗解冻+亢奋/派发两态+BHY-FDR（09-16 三连批态）；`load_phase_panel(end=None)`；无快照表去重；裸 SQL 内联 | V1 全部 + ①`_SQL_SNAPSHOT_DOMINANT` 常量提取（治 NO-BARE-SQL）②`load_phase_panel(end=None, start=IS_WIN_START)` ③**同日双写去重+dominant 分歧 fail-closed**（1,624/1,631 双写日治本）④zip strict/noqa 位置加固 | V2 的同内容+7B 折行差异；`ruff format --check` **FAIL** |
| 成熟度 | ruff format FAIL / ruff check FAIL（ADJ 实测）；在库但被本班实测 3 红测证伪（§2） | **ruff format PASS / ruff check PASS（本班复测）**；有 3 条专属回归测试在 HEAD（TestAutoMountDedupeRegression） | ruff format FAIL / check PASS → 落地必再修格式=落回 V2，且重新制造 7B 分叉 |
| 消费方 | HEAD 全部现役消费（R2SIX 同表镜像×3、SIX_STATES 词表、dsr 挂载门注释引用——均为表级镜像+漂移守卫，无函数签名耦合） | `scripts/audit/t0_six_phase_materialize.py:56` **硬依赖** `load_phase_panel(start=)`（已落 HEAD）；`six_phase_history_v1.csv` meta.truth_source 明文指向本版行为 | 无新增消费方（0033 袋死，拆批已改道） |
| 风险 | 双写不去重→面板行/日计数虚高（研究段脏数）；物化链 TypeError（§2 断②） | 口径切换需下游重算标注（Z-C1 前置②）；无其他 | 落地=格式回归+口径再分叉（走不通） |

V1→V2 归一 diff 本班复测：71 hunk = 45 纯格式 + 26 语义 hunk；语义 hunk 全部收敛于上表 V2 功能面①②③④，无删除/改名任何既有公开函数——对 V1 调用方向后兼容。

## 2. 案卷（09-25）之后盘面变化（本班挖矿增量，裁定的事实基座）

1. **0033 死袋 JSON 已不存在**（dead/ 查无；剩 0001/0007/0008 均为 09-24 更旧快照，blob sha 非三版本任一）——被"拆批 A-D"系列取代：拆批A `50a453fd17`（token 先行）→ 拆批D `1b46889a9f`（09-28，32 件交付）。
2. **依赖侧已落 HEAD 而真源未落**——拆批D 落地了 `docs/_working/t0_matrix/six_phase_history_v1.csv`（1,816 行全史）、`scripts/audit/t0_six_phase_materialize.py`、`tests/audit/test_t0_six_phase_materialize.py`、`scripts/audit/t0_gpu_condition_pack.py` 新版；但 `auto_mount.py` 仍=V1。由此 HEAD 当下三处实证断裂（本班逐一实测）：
   - **断①**：`pytest tests/audit/test_t0_six_phase_materialize.py` = **3 failed**（TestAutoMountDedupeRegression 三条：`KeyError: 'start'` 签名断言红 + 去重收拢/尾日剔除两条真调用红）——在库判据以 V2 行为为断言，代码缺位。
   - **断②**：物化件 `:56 am.load_phase_panel(start=start)` 对 V1 签名 `load_phase_panel(end=None)` 直跑必 TypeError——六段全史重生成通道断。
   - **断③**：全史 CSV 在库，其 `six_phase_history_v1.meta.yaml` 的 `truth_source.mapping` 指向 auto_mount（R2SIX+overlay+resolve）且 `duplication_guard` 自述即 V2 行为——**派生产物与其生成代码版本在库内不齐**，违派生数据可重生成纪律（ADJ §4：FDA 21 CFR Part 11 / EMA Annex 11 / GAMP5、DVC/lakeFS 版本绑定论证，检索日 2026-09-25）。
3. 死会话确认：`st-t0-matrix-20260924` 不在 SessionRegistry 活跃 6 会话中（本班实测）——worktree 残留为死车道遗物，V2 用作只读源无让路问题；worktree 本体归档走 `session_worktree.py archive`（不属本车道，尾注 §6）。
4. Z-C1 前置①（echo-guard 两条 acknowledged）至今未登记（echo-guard.yml 查无 t0_gpu_condition_pack 条目）——本班随裁定施工补齐。

## 3. 五要素裁定（Owner 授权自裁，2026-09-30）

### 3.1 事实
三版本如 §1 对比表；案卷后变化如 §2——**问题已从"要不要写回"变为"HEAD 已落地 V2 的判据与消费端，唯一缺位的是 V2 本体"**。

### 3.2 影响（含实盘暴露论证）
- 不写回：断①红测续红（提交链上任何触碰该测试文件的批都会撞红）+断②物化断链+断③版本漂移持续；选"适配 V1 改判据"=篡改在库冻结判据且双写脏数续行（见 3.4-C）。
- 写回 V2：一键治愈三断；口径变化（去重后日计数）须下游重算标注→登记排期（§5），不静默。
- **实盘暴露=0**：`GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()`（`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:121`，本班复测仍空）→结构性不产实盘单（裁定#305 安全态）；本车道未触碰任何执行面逻辑，仅版本管理/指向/标记。

### 3.3 规则依据
①宪法 RULE-SSOT（机械判定禁止凭记忆）+§9.4 派生真源一致性；②在库判据先行原则（判据已落、代码补位，方向唯一）；③派生数据可重生成外部论证（ADJ §4）；④Z-C1 前排推荐+Owner 本夜"对比表出来你自己裁定，然后直接施工执行"批文；⑤夜战铁律 8（五要素自裁留痕）。

### 3.4 选项
- **A = V2 写回定版**：治三断，代价=口径重算标注（排期项）。✅
- B = V3 写回：ruff format FAIL 须同批格式修复→落回 V2；+7B 重造分叉。走不通。❌
- C = 不写回、适配 V1：须改红三条在库判据=判据篡改；双写脏数续行→30 日样本地板虚假满足是唯一带资金尾部形态（ADJ §5）。❌

### 3.5 结论（裁定）
**定版本：V2（LF 归一字节 `e4dc2de62355`/63,374 B）= `scripts/backtest/auto_mount.py` 唯一真源版本。**
V1=deprecated（被 V2 替代，git 历史 `105b0d02d7d` 起可追溯）；V3=deprecated+successor 注记指向 V2（唯一差异=ruff format 缺陷折行，blob 不投递、随 commit_queue blob 清理通道退役）。本裁定=**裁定#460**（ruling_registry 已登记；取号时点实测 max=459，遇并行会话取号竞态从预案 #455 顺延，Owner 授权自裁留痕），收口 Z-C1。

## 4. 施工记录（本班执行，定版本=真源标注+其余退役标记+闸指向统一+测试）

| 步骤 | 内容 | 证据 |
|---|---|---|
| 1 | V2 LF 归一写回主区 auto_mount.py（63,374 B，写后进程外 sha 复核=e4dc2de62355） | 本批 commit hash 见 git log |
| 2 | echo-guard.yml acknowledged 登记存量克隆对 2 条（`t0_gpu_condition_pack.py:_reg ↔ build_closure_ledger.py:_connect`、`↔ wo008/generate_product_synonym_register.py:_pg`；存量对非本批引入，ADJ §2.4 实测口径）——Z-C1 前置①补齐，safe_write_text CAS | echo-guard.yml diff |
| 3 | 红转绿：tests/audit/test_t0_six_phase_materialize.py 3 failed→14 passed | pytest 输出 |
| 4 | 基线保持：tests/backtest/test_auto_mount.py + test_auto_mount_sle3.py + tests/governance/test_mount_route_consistency.py = 81 passed（施工前后各跑一遍） | pytest 输出 |
| 5 | ruff format --check + ruff check 对写回件 PASS | ruff 输出 |
| 6 | 裁定#460 登记 ruling_registry.yaml（取号=max+1，实测遇竞态 #455-459 已被他会话占用→顺延 #460） | ruling_registry.yaml diff |

## 5. 尾项转排期（非本车道施工面）

- **脏口径下游点名+重算**（Z-C1 前置②）：哪些下游已按未去重口径出过结论（P1 条件表 v1 469 板块版/做T 相位匹配矩阵/六段锚定表）——落 pending_owner 排期册，随补-1/补-2 同册管理。
- `.worktrees/st-t0-matrix-20260924` 死车道归档（V2 已定版入 HEAD，worktree 完成历史使命）——建议总筹 Wave 3 清理段统一 `session_worktree.py archive`。

## 6. 复算指引

```bash
# 三版本指纹
python -c "import hashlib;print(hashlib.sha256(open('scripts/backtest/auto_mount.py','rb').read().replace(b'\r\n',b'\n')).hexdigest()[:12])"
# 红蓝
python -m pytest tests/audit/test_t0_six_phase_materialize.py tests/backtest/test_auto_mount.py -q
```
