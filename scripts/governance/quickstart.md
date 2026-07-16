---
blueprint_id: MOD-INF-005
ttl: task_bound
doc_type: index
---

# 脚本系统 Zero-Memory Quickstart Card

> **用途**：新 AI session / 新人类维护者 冷启动时第一份必读材料。
> **Token 预算**：≤ 500 tokens。读完 < 30 秒。

---

## 一句话

**脚本系统是 ZephyrAlpha 的自动化治理基础设施**——一键运行 `python scripts/governance/run_all.py` 检查全项目健康。

## 3 条命令就够了

```bash
# 1. 看有哪些脚本
python scripts/governance/run_all.py --list

# 2. 全维度审计扫描
python scripts/governance/run_all.py

# 3. 只扫变更相关维度（快）
python scripts/governance/run_all.py --diff-ref HEAD~1
```

## 架构地图（10 秒看懂）

```
12 维度审计 → C1扫描→C2分类→C3报告→C4跟踪→C5沉淀
               ↑ 73+ 脚本自动编排 ↑
             run_all.py 统一入口
```

## 关键文件速查

| 看什么 | 去哪里 |
|--------|--------|
| 蓝图全文 | `docs/03_modules/infrastructure/script_system/blueprint.md` |
| 脚本注册表 | `scripts/governance/script_manifest.yaml` |
| 质量铁律 | `scripts/governance/quality_standard.md` |
| 所有阈值 | `scripts/governance/_shared/thresholds.yaml` |
| Kill Switch | `scripts/governance/meta/kill_switch_state.yaml` |
| 健康自检 | `python scripts/governance/meta/validate_script_system_health.py` |

## 门槛规则

- 新脚本必须走**三件套入库**：落位 → manifest注册 → 运行验证
- 脚本退出码：**0**=通过 / **1**=警告 / **2**=阻断 / **3**=崩溃
- pre_commit 门禁：V1违规硬阻断、V2违规警告
- 假阳性率 > 5% → Error Budget 消耗 → 可能触发 Feature Freeze

## 1 人+AI 维护备忘

- 每次 AI session 结束时检查 `kill_switch_state.yaml` 是否有意外禁用
- 每月跑一次 `validate_script_system_health.py --json` 看系统是否退化
- 关键阈值在 `thresholds.yaml`——改了会有审计日志
- 6 个月后回来：先读这份卡片，再读 blueprint.md
