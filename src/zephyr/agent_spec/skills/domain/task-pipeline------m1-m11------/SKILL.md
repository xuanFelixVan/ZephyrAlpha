---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "Task Pipeline 蓝图 — M1-M11 双管线路由"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Task Pipeline 蓝图 — M1-M11 双管线路由

## CRITICAL Rules

### Core Operations
## 54. 第三十四轮审计——Windows操作系统特异性与施工完备性治理（第21维度：Windows OS-Specific Resilience & Construction Completeness）

> **审计主题**：前二十维度让Pipeline在逻辑层面上无死角——但一个尚未被任何审计师考虑过的底层问题终于浮出水面：**「Pipeline跑在一台Windows 11笔记本上——不是跑在Google SRE管理的Borg集群里。Windows有自己的规则：MAX_PATH 260字符限制、Defender实时扫描会block HTTP、Windows Update会毫无预警地强制重启、文件句柄比Linux严格得多、Python multiprocessing的spawn vs fork行为完全不同、NTFS和WSL的交互有坑——Pipeline对这一切完全没有感知。」** 与此同时，蓝图自身的施工完备性也在本轮被审视——**construction_phase表格遗漏了v0.33.0所有条目。**

**范式第二十一次切换**：前二十维度的586项盲点中——B592处理了OS休眠、B597处理了网络灰度降级、B307处理了网络分区——但**Windows桌面操作系统的特异性**（与Linux/云环境的系统性差异）作为一个维度从未被独立审视。585项盲点覆盖了代码→市场→硬件→网络→账户→监管→人→钱→税→团队→自治理→事件→韧性→数据→通信→实验→时间→可移植→FinOps→Runtime Integrity——但**"这是个Windows笔记本"**这个事实从未被当作独立的风险维度来审计。

> **「Pipeline并非运行在Azure/AWS/GCP上由SRE团队维护的Linux容器集群中——它运行在一台Owner随身携带的Windows 11笔记本电脑上，一个Windows Update可以在一分钟内把20个in-flight dispatch全部杀死——而Pipeline对此一无所知。」**

本轮以 **Windows Update API（wuapi/GetUpdateInfo→pending_reboot_detection + Pre-Reboot State Snapshot）** + **Windows MAX_PATH Registry（LongPathsEnabled + `\\?\` prefix + 路径长度预检）** + **Windows Defender Exclusions（Add-MpPreference→ExclusionPath→Pipeline感知Defender是否在干扰）** + **Process Group Management（CreateJobObject / subprocess.run(start_new_session) → 全子进程级联清理）** + **`atexit` + `SIGBREAK`（Windows信号处理→cleanup handlers注册+注册失败告警）** + **psutil.Process.num_handles()（文件句柄泄漏检测→阈值告警→forced GC+fclose）** + **Model Quality Collapse Detection（给定模型黄金测试集→每次session跑→对比基线→如果P95/StdDev突变→Quality Cliff Alert）** + **Python `gc` module（gc.get_stats()→GC pause监控→>1s pause告警）** + **Network Interface Change Detection（GetAdaptersAddresses→adapter list change→通知等待network settle）** + **Blueprint Documentation Linter（检测缺失§编号+重复标题+Construction Phase遗漏）** 为方法论，开启Pipeline Windows操作系统特异性与施工完备性治理的第二十一个维度。

### Unique Constraints
### 2.5 Affinity / Anti-Affinity 约束矩阵（对标 K8s podAffinity/podAntiAffinity + Inter-Pod Affinity）

> **B93 第七轮审计**——双盲审查的独立性要求 M3(生成) 和 M7(审查) 必须用不同模型，否则双盲退化到单盲。

| 约束类型 | 约束项 | 节点A | 节点B | 权重 | 说明 |
|:---:|------|:---:|:---:|:---:|------|
| **mandatoryAntiAffinity** | model | M3 | M7 | hard | 双盲审查必须用不同模型——M3 deepseek ↔ M7 glm，禁止同模 |
| **preferredAntiAffinity** | model | M8 | M9 | soft | 建议合规检查 + 风险评估用不同模型，交叉覆盖不同类型漏洞 |
| **mandatoryAffinity** | sandbox | M1~M4 | — | hard | A 区生产模块必须在 full/standard sandbox，不可降级到 restricted |
| **mandatoryAffinity** | pipeline | A 区全部 | — | hard | A 区产出物必须经 M5 打包→M6 边界标记（AP2），不可跨区直通 |
| **preferredAffinity** | model | M8~M11 | — | soft | B 区后半段（report+gating）优先用 deepseek，降低审查成本 |

**M3↔M7 antiAffinity 硬约束影响**：如果 deepseek 不可用 → M3 降级到 glm → 此时 M7 被迫改用 claude（因为不能和 M3 同模）→ claude 成本上升但保证双盲独立性。这是双盲审计体系的安全底线。

---

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md