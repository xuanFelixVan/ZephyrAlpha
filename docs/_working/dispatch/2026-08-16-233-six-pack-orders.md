---
doc_type: dispatch_order
ttl: task_bound
status: active
date: 2026-08-16
---

# 233 测试债下批·6 包开工指令（2026-08-16 用户裁定 6 路全并发）

> 发包人：第五统筹 coord-0815-gov3 ｜ 依据：TDEBT-001 裁定书 §关联项 E（docs/_working/audit/architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md）
> 基线：dev HEAD fcf3e21e89（11 路 merge 已收口，worktree 均从此点切出）

## 六包总表

| 包 | 会话 ID | worktree | 域 | 预估 |
|---|---|---|---|---|
| ① | AI-TD2-SEC-001 | .worktrees/AI-TD2-SEC-001 | 安全与权限（escalation/rbac/agent_spec/skill） | ~30 项 |
| ② | AI-TD2-TRD-001 | .worktrees/AI-TD2-TRD-001 | 交易与资金（trading/position/pf_core/rollback） | ~45 项 |
| ③ | AI-TD2-GOV-001 | .worktrees/AI-TD2-GOV-001 | 治理与蓝图（blueprint/governance/orchestrator）**+搭车 #ARCH-099**（gov_db 8 xfail 治本=自建最小 schema fixture，不再拷贝生产库） | ~60 项 |
| ④ | AI-TD2-DATA-001 | .worktrees/AI-TD2-DATA-001 | 数据与基础设施（data/infrastructure/zephyr） | ~40 项 |
| ⑤ | AI-TD2-AUTO-001 | .worktrees/AI-TD2-AUTO-001 | 自治与生命周期（autonomy/f_lifecycle/fix） | ~35 项 |
| ⑥ | AI-TD2-UTIL-001 | .worktrees/AI-TD2-UTIL-001 | 工具与其他（utils/memory/skill/config）**+全量复跑验证职责** | ~23 项 |

## 基线获取（各会话开工第一步）

```powershell
# 在各自 worktree 内执行，跑出全域失败清单作为本包基线
python -m pytest tests/ -x --co -q 2>$null | Out-Null  # 可先 collect 探 collection error
python -m pytest tests/<本包域目录>/ -p no:xdist -q 2>&1 | Select-String "FAILED|ERROR"
```

- 画像：130+ 文件 × 1-4 项，无 ≥5 大簇；形态与上批已清簇同族（API 演进/契约漂移），**无真 bug 信号**——若发现疑似真 bug，不硬修，登记反馈统筹裁定。
- 域界定模糊项（跨目录）：按测试文件 import 的生产模块归属定域；拿不准的登记反馈，不越域硬收。

## 验收标准（与上批同规）

1. 本包域失败项 **2 轮全绿**（间隔复跑，排除抖动）
2. 假阳性必须转正（改测试跟进 API 现状），**禁止 delete  failing test 充数**
3. 确需留置的：xfail(strict=False) + 编号登记（ARCH-1xx 系列，向统筹申请号段，防撞号）
4. 长清单 Step 1 + Step 6（14 节）双 PASS
5. 全部经 GitCommitGateway 提交（[GW:会话ID] 标记），**0 裸 commit / 0 --no-verify**

## 铁律（并发防护）

- **只动本包域的测试文件+被测生产文件**；发现跨域依赖问题登记不代修
- 注册表（architecture_issue_registry 等）写入前必须先读 dev 最新版取号，merge 时撞号按"保留信息全者+重编"处理
- 临时脚本用后全清；IDE 脏缓冲区陷阱处方：落盘后进程外 Select-String 核实
- 完工反馈格式参照上批（六要素：commit hash/Step1/Step6/测试轮次/改动清单/遗留项）

## 特别职责

- **包③**：#ARCH-099 治本——gov_db 测试自建最小 schema fixture（替代 online backup 拷生产库），8 项 xfail 转正
- **包⑥**：本包清偿后执行**全量复跑**（python -m pytest tests/ -p no:xdist -q），输出 233→? 基线对比报统筹；若剩余失败含他包域项，原样记录不代收
