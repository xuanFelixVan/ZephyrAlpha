---
ttl: task_bound
---

# auto_mount 自动挂图器施工交底（2026-09-15 班，MOD-BT-171）

> 立项真源：[2026-09-14-auto-mount-research.md](2026-09-14-auto-mount-research.md) §4（五步管线+验收五条+治理边界）。
> 本文档=施工交底与验收证据归档。

## 模块

- `scripts/backtest/auto_mount.py`（MOD-BT-171，241→260 行）：五步管线——①SOP-C §6.2 类别→节点映射表 ②分状态回测判 activation_state ③PP-001 等权起步档 ④文本级手术写入+语义级 only-add 断言+38 规则校验 ⑤报告（挂了哪/为什么/证据指针）。
- `tests/backtest/test_auto_mount.py`：20 用例（手术幂等/红蓝六姿势/等权缩水/映射表契约/常量冻结）。

## 核心设计裁定

1. **r→六段映射**（管线②的规则真源，逐段 Sharpe 校准 2026-09-15）：
   r10 CRISIS→capitulation；r4 熊市阴跌/r11 RECOVERY→accumulation；r3 牛市趋势→expansion；r12 BREAKOUT→ignition；r1 低波/r2 中波→保守不路由。语义前置=CLASS_CANDIDATE_STATES（数据只在类别候选态内裁决，防 IS 过拟合）。
2. **only-add 语义门**：挂载/格子/证据只增不减不改；sleeve 只增不减、老 sleeve 仅允许全局等比缩水（立项 §4③ 设计行为）、新 sleeve 必 0.05。红蓝六姿势测试（伪造删挂载/删格子/改 evidence/缩格子挂载/非等比改权重/新 sleeve 违规档位）全部必拒。
3. **evidence 防注入**：手术生成的 evidence 字符串剥离单引号（YAML 单引号标量安全）；段证据格式 `state=+Sharpe(天数)`。
4. **`--apply` 强制显式 `--strategy`**：挂谁=C6 入库线决策，工具只负责怎么挂（治理边界：全自动 only-add ≠ 自动选人）。
5. **判定缓存**：`.runtime/tmp/auto_mount_judge_cache.json`（sid+code mtime+窗口+映射版本键控），避免重放全量回测。

## 验收五条对账

| # | 立项条款 | 结果 |
|---|---|---|
| ① | 6 条已挂策略重放复现（幂等） | ✅ `--replay` 已挂 28 条 STR-* 零 diff（REPLAY OK） |
| ② | 分状态判定与人工一致率 ≥5/6 | ✅ 5/6 校准（VREV-025/026/MOMTREND/TSMALL/VAL 命中；DABAN-023 expansion 漏挂=宁漏勿误方向，其人工依据为 OOS+做T 实操非 IS 分段——已知边界，月度审计兜底） |
| ③ | only-add 断言红蓝测试 | ✅ 语义级门+6 红队姿势全拒（真实地图多行折行格子事故已由门禁拦截并修复） |
| ④ | 38 规则校验全绿 | ✅ 端到端沙箱演练 fails=0（warns=117 与生产基线一致）；生产地图 audit ok |
| ⑤ | Owner 视觉复核 | ⏳ 待 Owner 看本报告+报告样例 |

## 端到端沙箱演练（tmp 隔离）

真地图+真注册表副本注入假想条目 STR-DRILL-001 → ops=4（节点挂载+capitulation 格子+sleeve 0.05+老 sleeve 等比缩水）→ only_add 通过 → 38 规则 0 fails → 二次计划零 ops（幂等）。报告样例含 judge_shape（activated 态列表）。

## 已知边界与欠账

1. judge 分状态回测当前=回测件 Sharpe 全量串行（缓存后可接受）；后续可换量并向量化。
2. STR-E-TIMING-001（sim）code_path 非 C4 翻译件（无 build 契约）被管线跳过——其底层=恐慌反弹（STR-VREV-025 已挂）；若需独立挂载，先补 build 契约。
3. `rescale` 与 `sleeve` op 的证据行均落报告 stdout；报告文件输出待 Owner 定稿格式（本班不拍板）。
4. 架构评审（Step 1.8）按"纯内容新增、不改接口契约"豁免申报；Owner 复核时可一并追认。

## 提交

队列提交：session=st-automount-20260914；files=scripts/backtest/auto_mount.py, tests/backtest/test_auto_mount.py, docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml, 本文档；commit 后 `git log -1 --name-only` 核实归属。
