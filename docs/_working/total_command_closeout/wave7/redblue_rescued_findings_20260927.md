---
created: 2026-09-27
ttl: task_bound
completes_when: "本件 P-1 的静默放行面被补丁覆盖且两条红证在落地面转绿，或 Owner 明令保留现状并把该项登记为长期可观测风险"
authored_by: "st-final-build-20260926（总筹本班）"
measured_at: "2026-09-27 04:05-04:12（本地钟）"
---

# 波 7.3 · 红蓝补测首份真值——六图战役"抢救件"回正位后打出的一个 P0 静默放行

> 本件是 族 10 W-101 的第一份**能红的**红队证据。前一轮我把这两套件按"抢救副本"放在
> `docs/_working/…/wave1b/rescued/tests/` 下跑，得 6 failed + 4 errors，差点据此写成"六条防线失守"——
> 那是**路径伪影**，不是缺陷。回正位重跑后真值＝**一条**，且那条是真的。
> 结论顺序不能反：先消伪影，再报失守。

## §一 伪影消雷（这是本件的第二条产出，别跳过）

`test_redblue_governance.py` 第 64-65 行：

```
REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / "scripts" / "governance" / "git_hooks"
```

`parents[2]` 只对 `tests/governance/<file>` 成立。放在抢救位（`docs/_working/…/rescued/tests/governance/`）时
`parents[2]` 解析成 `docs/_working/…/rescued/`，于是钩子根本不存在：

| 现象 | 报错原文（节选） | 定性 |
|---|---|---|
| 6 FAILED | `rc=127 bash: …/rescued/scripts/governance/git_hooks/reference_transaction_guard.sh: No such file or directory` | 伪影 |
| 4 ERROR | `FileNotFoundError: …/rescued/scripts/governance/git_hooks/post_commit_guard.sh` | 伪影 |

真钩子在盘且三态同值：`scripts/governance/git_hooks/{reference_transaction_guard,post_commit_guard}.sh`
主区与我的车道 sha 同（`aa275177`，266 行），属主车道 `st-mapbuild-20260924` 是旧版（`63c95a33`，242 行）。

## §二 回正位实测（唯一真红）

把两份件复制到**真实位** `tests/governance/` 后跑（命令见 §五）：

| 套件 | 结果 | 用时 |
|---|---|---|
| `test_redblue_governance.py` | **22 passed / 1 failed** | 16.92s |
| `test_redblue_robust.py` | **18 passed / 0 failed** | 52.79s |

唯一红：`TestS4AForgedMarkersDirectRun::test_s4a3_impersonating_live_foreign_sid_exit1_or_audit`
断言原文＝**"冒充在活 sid 既未拦也未审计（静默放行）: rc=0"**。

## §三 P-1 · 提交正门的"冒充已注册他人 sid"零分支（真缺陷）

### 判据命题
`[GW:]` 尾注不可伪造是宪法级铁律（`[GW:]` 伪造会被 POST-COMMIT-GUARD reset 回滚）。
"不可伪造"的**执法对象**是"尾注里的 sid 是否等于真提交者"，不是"这个 sid 存不存在"。

### 实测定性（读钩子逻辑，非推断）
`reference_transaction_guard.sh` 对 sid 只有两条出路：

| 分支 | 行位 | 行为 |
|---|---|---|
| sid **不在** `.runtime/session_registry.json` 会话键内 | 241 | `伪造 GW 标记：sid=… 不在 SessionRegistry 会话键内` → 阻断 |
| sid 不在册**但**命中合法逃生通道（`ZEPHYR_COMMIT_GATEWAY` env / emergency） | 237-238 | `violation=unregistered_gw_sid`，`action=warn_only`，落审计放行 |
| sid **在册但不是本次提交者**（＝冒充在活他人会话） | **无此分支** | **exit 0，零审计** |

⇒ 现网防线是"存在性"门，不是"归属"门。任何知道他人活 sid 字符串的写入者，
用 `[GW:<他人活 sid>]` 提交即可**既不被拦也不留痕**。
`grep -l gw_sid_channel_unverifiable` 在 HEAD／主区／我的车道／属主车道 **四处零命中**
⇒ 测试里那句"本车道收窄后=warn_only 审计（violation=gw_sid_channel_unverifiable）"描述的是一条**从未存在过的实现**。
这是"判据先于产品"（红队件写的是应有防线），不是产品回退。

### 与在册旧账的关系（不重复立项）
- `greatwall-eight-package-night-20260916` 记"HMAC 取证为最高优先移交项"——同一病根（提交无凭据载体）。
- 93 册菜单甲案要求 EV-02 红证复现（`WorktreePunchThrough`）：实测 `tests/` 全域零命中，仍是欠账，
  与本条同属"归属级"族，但攻击面不同（本条＝冒充 sid；EV-02＝成果被卸走）。

## 四 · 总筹裁定 Z-F8（自裁部分与不自裁部分分开写）

**自裁（不需要 Owner，且今晚就做）**
1. 本缺陷**今晚不改钩子**。理由＝`reference_transaction_guard.sh` 是所有会话提交的必经面，
   8 路并发在飞时改它＝最高爆炸半径；而"归属级"修法要么加凭据载体（新面），要么把 warn_only 升 block
   （＝门禁强度翻转），两者都撞 Owner 门位。
2. 这两份红队件**今晚不入袋**。本仓规矩"门禁本体＋自家测试同批"，产品未改而先落测试＝
   给全仓所有会话的回归里塞一条恒红件，属连坐；用 xfail/skip 压掉＝违"禁改断言/skip/xfail"红线。
   ⇒ 与 §三 的补丁**同袋**投，一次落。

**不裁（呈 Owner，一句话就能点）**
- 甲（推荐）＝加"可观测腿"，不改行为：sid 在册且≠本次提交者时落 `action=warn_only` 审计
  （新 violation 名建议 `gw_sid_registered_but_unverified`），先让这条洞可被计数，HMAC 载体另行立项。
  代价＝`.runtime/reconcile_reports/` 增速上升；且**代投场景会留痕**（本班代他人投字节是常态，会被记为可疑）。
- 乙＝直接升硬拦（在册 sid 不等于提交声明者即 exit 1）。代价＝代投/接力/队列 finalize 全链路会被打断，
  现有多会话正门纪律依赖代投，乙案＝要求先有"代投申报"通道。
- 丙＝只登记为长期风险，不动代码。代价＝洞持续静默，且"红队件已写"会变成第二例"判据在册产品缺位"。

## 五 · 复跑命令（可整块复制）

```bash
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"          # 必须落在 .aidrafts 内
cp docs/_working/total_command_closeout/wave1b/rescued/tests/governance/test_redblue_governance.py tests/governance/
cp docs/_working/total_command_closeout/wave1b/rescued/tests/governance/test_redblue_robust.py tests/governance/
python -m pytest tests/governance/test_redblue_governance.py tests/governance/test_redblue_robust.py \
  --no-header -q --tb=line --basetemp=D:/ZephyrAlpha/.runtime/tmp/bt_rb_real
rm tests/governance/test_redblue_governance.py tests/governance/test_redblue_robust.py   # 探针件用完即清
```

判据行（供 92 册回流）：**抢救副本必须回正位再判红**——凡"件里用 `__file__` 反推仓库根"的测试，
放到任何非原始深度都会产生整批伪红；伪影定性法＝读报错里的路径是否含 `rescued/` 或非预期前缀。

## 六 · 交班位

| 序 | 事项 | 前置 | 说明 |
|---|---|---|---|
| R-7a | 钩子加"可观测腿"补丁 + 两份红队件回正位同袋投 | Owner 点甲/乙/丙 | 见 §四 |
| R-7b | 六图包（5 图 yaml + 6 生成器 + 5 校验器 + 12 测试 + 49 文档＝79 件）落地 | 无（本班可做，排在 B2/B3 之后） | 字节与属主车道逐件同值，代投时在 message 记名，不占他人归属 |
| R-7c | 6 台图门（`src/.../commit_gates/*_map_gate.py`）接线 | 主区 `git_commit_gateway.py` 现被他会话在途改（`MM`） | 未接线即落地＝6 台装饰门，本仓已有"装饰件无调用者"缺陷族，禁止制造第二例 |
