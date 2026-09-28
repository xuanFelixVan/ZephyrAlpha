---
asset_id: "DOC:docs/_working/fullflow_chief_closeout/s52_dynamic_lanes_v1.md"
ttl: "task_bound"
title: "S5② 动态车道 v1：路径租约模型与影子期方案"
session: st-s52-20260928
completes_when: "影子期 3 天复盘完成且 v2 硬阻断提案（或降级处方）经 Owner 裁定后归档"
---

# S5② 动态车道 v1 — 路径租约模型与影子期方案

> 状态：v1 影子模式落地（WARN-only）｜落地件：`scripts/governance/lane_leases.py`（MOD-INF-093）+ `scripts/governance/lane_leases_gate.py`（MOD-INF-094）+ `tests/governance/test_lane_leases.py`（22 用例）｜落袋会话：st-s52-20260928（2026-09-28 夜）

## 1. 病根与目标

工作区分治的最终形态：**每个施工队持有一张动态租借的冲突域**（一组路径前缀），而不是静态分工或口头约定。此前已落地的前置：四工池（belt w0-w3）、FCFS 提交队列、不可变树门（ed935c29af）、分叉基底拒绝（§6.4）。缺的最后两块=**租约分配器** + **写属主核验**——本批补上（v1 影子形态）。

动态车道同时消灭两类慢性病：

- **多 chief 病**：多个会话/队各自为政改同一域，靠人眼发现冲突、靠事后对账收拾。租约模型下，同一前缀同一时刻至多一张活租约——第二支队伍 claim 即被拒绝并拿到不相交拆分建议，冲突在**开工前**显性化。
- **双写病**：两个活租约覆盖同一路径、或文件落在租约域之外——影子门每次落盘自检即产出 `cross-lease-overlap` / `outside-lease` / `no-lease` 三类审计信号，病发即留痕，不再静默。

## 2. 租约模型（design）

- **登记**：`.runtime/lane_leases.json`（根级 runtime 协调文件，先例=session_registry.json / archive_watchlist.json）。条目 `{sid, prefixes[], acquired_at, heartbeat_at, expires_at}`，心跳 TTL 缺省 600s，过期即死（懒清除）。
- **冲突判定**：段边界感知的前缀包含（`src/zephyr` 与 `src/zephyr2` 不相交；`src/zephyr` 与 `src/zephyr/data` 相交）。同 sid 再 claim=覆盖式合并；他 sid 活租约相交=拒绝（fail 消息含相交对象+suggest 拆分指引）。
- **分配器 `suggest`**：读文件清单（csv 串或清单文件），按目录族分域——`src/zephyr/<pkg>/`、`tests/<dir>/`、`docs/_working/<campaign>/`、`scripts/<dir>/`、含 `_registry` 段=hot-register 类（聚合一队，前缀=各具体 _registry 根）；N 队贪心 FCFS（域按首文件出现序入列，分给域数最少的队，平票取小号），类间构造性不相交；跨队残余相交=输出 advisory（不拒，影子纪律）。
- **并发安全**：O_EXCL 锁文件（best-effort，超限放行——影子期可用性>强一致）+ `safe_write_text` CAS 写册（热文件纪律）。时间一律 `now_utc()`。

## 3. 影子期方案（WARN-only，run 3 天）

- `lane_leases_gate.py` 独立运行：`python scripts/governance/lane_leases_gate.py --session X --files a,b,c`，退出码 0=干净 / 2=有告警。**不注册进 gate_registry、不挂 commit 链**（入链须走 gate registry 净零流程；本批零门禁面变更）。
- 影子期动作：各施工队开工前 `claim` 自己的前缀域、长任务中途 `heartbeat`、收工 `release`；落盘自检跑 gate。告警进入审计日志，人工复盘。
- **v1→v2 毕业判据**（三条同时满足才提案硬阻断）：
  1. **数据量**：影子连续运行 ≥3 天，覆盖 ≥4 支并行队伍的日常落盘自检；
  2. **误报率**：`outside-lease`/`cross-lease-overlap` 告警中误报占比 <10%（误报=告警所涉文件实际属主清晰无争议）；
  3. **纪律面**：claim 覆盖率（落盘文件落在某活租约内的比例）≥90%，且 claim 冲突拒绝零硬闯申诉。
- 达标后 v2 提案：gate 入册（走净零流程：声明替代/合并条目）+ own-diff 作用域接线 commit 链，`cross-lease-overlap` 升 hard-block；`no-lease` 维持 warn（新人/临时脚本不强收敛）。
- 不达标处置：误报高→修 classify_domain 分组语义（数据驱动）；覆盖率低→先做 suggest 进交接包模板，不强行硬阻断。

## 4. 落地与运维

```bash
# 开工：登记租约（冲突即拒绝+拆分建议）
python scripts/governance/lane_leases.py claim st-xxx src/zephyr/governance tests/governance
# 长任务：续期
python scripts/governance/lane_leases.py heartbeat st-xxx
# 落盘自检（影子，永不阻断）
python scripts/governance/lane_leases_gate.py --session st-xxx --files a.py,b.py
# 分队建议：给 N 支队伍拆不相交域
python scripts/governance/lane_leases.py suggest --teams 4 --files changed.csv
# 收工
python scripts/governance/lane_leases.py release st-xxx
python scripts/governance/lane_leases.py status
```

测试：`python -m pytest tests/governance/test_lane_leases.py`（22 用例，全 tmp_path 假册，零生产路径写入）。
