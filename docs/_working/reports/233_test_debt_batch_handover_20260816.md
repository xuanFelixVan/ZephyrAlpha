---
ttl: task_bound
title: 测试债 233 长尾清偿批次 · 立项交接书（六包派单规范）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-16
topic: handover_233_test_debt_batch
scope: 07_trading_decision_architecture
session: deep-investigation-0816
---

# 测试债 233 长尾清偿批次 · 立项交接书

> **致**：统筹会话（下一任 coord）
> **自**：AI-TDEBT 遗留裁定会话（经 Owner 2026-08-16 裁定授权）
> **日期**：2026-08-16
> **性质**：派单交接——统筹负责拆批派工；本交接书发出时主仓生命周期卫生执行同步进行（进程/目录级，零文件交集，可并发）

---

## 一、任务来源与基线

- 立项依据：裁定书 [2026-08-16-test-debt-leftover-adjudication.md](../audit/architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md) §关联项 E（六包方案）+ §四终态裁定补记。
- 基线链：全量 4.5 万项单进程可复现 **785 → 515 → 233 failed / 8 errors**（-70.3%，AI-TDEBT-001 三批清偿成果，2026-08-16 1h37m 实证）。
- 本批目标：233 failed 全量清偿（8 errors 不计入——见 §四已知排除项）。

## 二、施工范围：按域 6 包（风险加权排序，Two Sigma 原则：安全/资金路径优先）

| 包 | 域 | 规模 | 优先级理由 |
|---|---|---|---|
| ① | 安全与权限（escalation/rbac/agent_spec/skill） | ~30 项 | 安全路径最高敏 |
| ② | 交易与资金（trading/position/pf_core/rollback） | ~45 项 | 资金路径次高敏 |
| ③ | 治理与蓝图（blueprint/governance/orchestrator） | ~60 项 | 治理中枢 |
| ④ | 数据与基础设施（data/infrastructure/zephyr） | ~40 项 | 数据链路 |
| ⑤ | 自治与生命周期（autonomy/f_lifecycle/fix） | ~35 项 | 自治框架 |
| ⑥ | 工具与其他（utils/memory/skill/config 等） | ~23 项 | 工具层收尾 |

画像：130+ 文件 × 1-4 项，无 ≥5 大簇；失败形态与已清簇同族（API 演进/契约漂移——AttributeError/TypeError/文案漂移/namespace 迁移/dispatch 契约），**无真 bug 信号**。

## 三、施工规范（每包统一）

1. **独立 worktree**：`scripts/session_worktree.py create AI-TDEBT2-<包号> task-test-debt-pkg<包号>`，每包一个，互不复用。
2. **独立 commit**：每包完工即经 GitCommitGateway 落盘（先 claim 后编辑，或 commit 时 `--adopt-prior-work`——tracker #92 正确姿势）。
3. **验收标准**（同 AI-TDEBT-001 本批）：
   - 受影响测试 **2 轮全绿**（间隔重跑排除时序抖动）；
   - 假阳性必须转正（改测试跟进真演进），不得为压数字而 xfail；
   - 代码侧缺口（桩模块/设计契约分歧）→ `xfail(strict=False)` 留痕 + 登记 #ARCH-XXX（编号前先 grep 全文件最大号，撞号重编先例 #77-79/#85-92）。
4. **开工前查重**：目标测试文件先 grep 是否有在册议题/候选条目（D1 纪律）。
5. **merge 排期**：六包全部完工后由统筹统一走 #ARCH-70 通道 merge 回 dev（参照今日 11 路收口模式：派生文件取 theirs、关键文件并集取新、时序文件全保留）。

## 四、已知排除项与避让规则

- **8 errors = sqlite locked 环境抖动**：test_governance_db fixture 用 online backup 拷主仓生产 governance.db（锁竞争 + schema 漂移双耦合），已 xfail(strict=False) 留痕 + **#ARCH-099** 在册。治本 = 测试自建最小 schema fixture——可随包③治理域同批施工，亦可单列；不在 233 计数内。
- **派生活水避让**：施工期 worktree 内 blueprint/文档 AUTO 统计块数字 diff 一律丢弃不提交（tracker #85 SOP；提交必与并行会话刷新冲突，丢弃零损失）。
- **CRLF 陷阱**：热文件处置先查 blob/工作区行尾型再定回写姿势（tracker #85 处方）。
- **IDE 脏缓冲区**：关键文件改后须进程外 Select-String/git diff 核实（tracker #75 教训）。
- **ps1 纯 ASCII 铁律**：注释/日志串一律英文（INJ-007 硬拦）。

## 五、并发声明

本交接书发出时刻环境状态：全部 12 个施工 worktree 已退役、全部 ai/* 分支已 merged、主仓 dev = 0817f77e84（depgraph 收敛态）。主仓侧本会话仅余文档登记 commit（本交接书 + 裁定书补记 + tracker 台账）与进程/目录级卫生执行，**与六包施工零文件交集**。六包可按统筹节奏任意并发（参考前例 9-10 路并发上限）；包间无依赖，仅共享 GitCommitGateway 串行锁（设计内行为）。

## 六、验收回流

每包完工 → 统筹独立复跑核验 → tracker §四核验登记 + §七变更记录；六包全绿后全量复跑确认 233→0（8 xfail 留痕项除外），#63 遗留项闭环归档。
